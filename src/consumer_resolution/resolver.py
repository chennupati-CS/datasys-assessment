"""
Consumer Identity Resolution System

This module implements a robust consumer identity resolution system that:
1. Matches records across datasets using fuzzy matching
2. Handles spelling variations and nicknames
3. Generates persistent consumer IDs
4. Merges matching records into a single deduplicated record
"""

import logging
import pandas as pd
import hashlib
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from datetime import datetime

from .utils.name_utils import are_names_match
from .utils.address_utils import are_addresses_match
from .utils.contact_utils import are_emails_match, are_phones_match
from .config.settings import (
    INPUT_FILE_A, INPUT_FILE_B, OUTPUT_FILE, AUDIT_LOG_FILE,
    NAME_MATCH_THRESHOLD, ADDRESS_MATCH_THRESHOLD,
    EMAIL_MATCH_THRESHOLD, PHONE_MATCH_THRESHOLD,
    FIELD_WEIGHTS, LOG_FORMAT, LOG_LEVEL
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)

class ConsumerResolver:
    """
    Main class for resolving consumer identities across datasets.
    
    This class handles the entire process of:
    1. Loading data from input files
    2. Finding matches between records
    3. Merging matching records
    4. Generating persistent consumer IDs
    5. Saving results to output files
    """
    
    def __init__(self):
        """Initialize the resolver with empty datasets and tracking variables."""
        self.dataset_a = None
        self.dataset_b = None
        self.matches = []
        self.audit_log = []
        self.resolved_records = []
        self.consumer_id_map = {}  # Map to store persistent IDs
        self.stats = {
            'total_records_a': 0,
            'total_records_b': 0,
            'matches_found': 0,
            'unmatched_a': 0,
            'unmatched_b': 0,
            'merged_records': 0
        }
    
    def _generate_consumer_id(self, record: pd.Series) -> str:
        """
        Generate a unique, persistent ID for a consumer based on their key attributes.
        
        The ID is deterministic - the same person will always get the same ID
        regardless of which dataset they come from or how many times the process runs.
        
        Args:
            record: Consumer record with attributes to hash
            
        Returns:
            Unique 12-character consumer ID
        """
        # Create a string of key attributes, converting all values to strings
        key_attributes = [
            str(record['first_name']).lower(),
            str(record['last_name']).lower(),
            str(record['street']).lower(),
            str(record['city']).lower(),
            str(record['state']).lower(),
            str(record['zip']),
            str(record['email']).lower() if pd.notna(record['email']) else '',
            str(record['phone']) if pd.notna(record['phone']) else ''
        ]
        
        # Join attributes with a delimiter and generate hash
        key_string = '|'.join(key_attributes)
        return hashlib.sha256(key_string.encode()).hexdigest()[:12]
    
    def _get_or_create_consumer_id(self, record: pd.Series) -> str:
        """
        Get existing consumer ID or create a new one.
        
        This ensures that the same person gets the same ID even if
        they appear in different datasets or multiple times.
        
        Args:
            record: Consumer record
            
        Returns:
            Consumer ID (either existing or newly generated)
        """
        record_id = record['record_id']
        
        if record_id in self.consumer_id_map:
            return self.consumer_id_map[record_id]
        
        consumer_id = self._generate_consumer_id(record)
        self.consumer_id_map[record_id] = consumer_id
        return consumer_id
    
    def load_data(self, file_a: Optional[str] = None, file_b: Optional[str] = None) -> None:
        """
        Load datasets from CSV files and prepare them for processing.
        
        Args:
            file_a: Path to first dataset (optional)
            file_b: Path to second dataset (optional)
            
        Raises:
            Exception: If there's an error loading the data
        """
        try:
            logger.info(f"Loading dataset A from {file_a or INPUT_FILE_A}")
            self.dataset_a = pd.read_csv(file_a or INPUT_FILE_A)
            self.stats['total_records_a'] = len(self.dataset_a)
            
            logger.info(f"Loading dataset B from {file_b or INPUT_FILE_B}")
            self.dataset_b = pd.read_csv(file_b or INPUT_FILE_B)
            self.stats['total_records_b'] = len(self.dataset_b)
            
            # Add index as record_id if not present
            if 'record_id' not in self.dataset_a.columns:
                logger.debug("Adding record_id column to dataset A")
                self.dataset_a['record_id'] = self.dataset_a.index.astype(str)
            if 'record_id' not in self.dataset_b.columns:
                logger.debug("Adding record_id column to dataset B")
                self.dataset_b['record_id'] = self.dataset_b.index.astype(str)
            
            # Add source column to identify origin
            self.dataset_a['source'] = 'A'
            self.dataset_b['source'] = 'B'
            
            logger.info(f"Loaded {self.stats['total_records_a']} records from dataset A")
            logger.info(f"Loaded {self.stats['total_records_b']} records from dataset B")
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def find_matches(self) -> List[Dict]:
        """
        Find matching records between datasets using fuzzy matching.
        
        This method:
        1. Groups records by ZIP code for efficient matching
        2. Calculates match scores for name, address, email, and phone
        3. Determines matches based on weighted total score
        4. Allows multiple records from dataset B to match with a single record from dataset A
        5. Logs all match attempts for auditing
        
        Returns:
            List of dictionaries containing matched records and confidence scores
        """
        logger.info("Starting match finding process")
        matches = []
        
        # Create dictionaries to store potential matches for each record
        potential_matches_a = {}  # record_a_id -> [(record_b_id, score), ...]
        
        # Group records by ZIP code for efficient matching
        zip_groups_a = self.dataset_a.groupby('zip')
        zip_groups_b = self.dataset_b.groupby('zip')
        
        total_comparisons = 0
        potential_matches = 0  # Track records that almost matched
        
        for zip_code, group_a in zip_groups_a:
            if zip_code in zip_groups_b.groups:
                group_b = zip_groups_b.get_group(zip_code)
                
                for _, record_a in group_a.iterrows():
                    record_a_id = record_a['record_id']
                    potential_matches_a[record_a_id] = []
                    
                    for _, record_b in group_b.iterrows():
                        total_comparisons += 1
                        
                        # Calculate match scores
                        name_score = self._calculate_name_score(record_a, record_b)
                        address_score = self._calculate_address_score(record_a, record_b)
                        email_score = self._calculate_email_score(record_a, record_b)
                        phone_score = self._calculate_phone_score(record_a, record_b)
                        
                        # Calculate weighted total score
                        total_score = (
                            name_score * FIELD_WEIGHTS['name'] +
                            address_score * FIELD_WEIGHTS['address'] +
                            email_score * FIELD_WEIGHTS['email'] +
                            phone_score * FIELD_WEIGHTS['phone']
                        )
                        
                        # Track potential matches (score > 0.5)
                        if total_score > 0.5:
                            potential_matches += 1
                        
                        # Log match attempt with more details
                        self._log_match_attempt(record_a, record_b, {
                            'name_score': name_score,
                            'address_score': address_score,
                            'email_score': email_score,
                            'phone_score': phone_score,
                            'total_score': total_score,
                            'matched': total_score >= 0.7,  # Add match status
                            'zip_code': zip_code
                        })
                        
                        # If total score exceeds threshold, add to potential matches
                        if total_score >= 0.7:  # Configurable threshold
                            potential_matches_a[record_a_id].append({
                                'record_b_id': record_b['record_id'],
                                'confidence_score': total_score,
                                'match_details': {
                                    'name_score': name_score,
                                    'address_score': address_score,
                                    'email_score': email_score,
                                    'phone_score': phone_score,
                                    'zip_code': zip_code
                                }
                            })
        
        # Process potential matches to find all matches for each record
        matched_record_ids_b = set()
        
        # For each record in dataset A, find all matches
        for record_a_id, matches_list in potential_matches_a.items():
            if not matches_list:
                continue
            
            # Sort by confidence score (descending)
            matches_list.sort(key=lambda x: x['confidence_score'], reverse=True)
            
            # Add all matches that exceed the threshold
            for match in matches_list:
                record_b_id = match['record_b_id']
                
                # Add to matched records set
                matched_record_ids_b.add(record_b_id)
                
                # Add to matches list
                matches.append({
                    'record_a_id': record_a_id,
                    'record_b_id': record_b_id,
                    'confidence_score': match['confidence_score'],
                    'match_count': len(matches_list),
                    'match_rank': matches_list.index(match) + 1,  # 1 = best match
                    'match_details': match['match_details']
                })
        
        self.matches = matches
        self.stats.update({
            'matches_found': len(matches),
            'total_comparisons': total_comparisons,
            'potential_matches': potential_matches,
            'match_rate': len(matches) / total_comparisons if total_comparisons > 0 else 0,
            'multiple_matches': sum(1 for m in matches if m['match_count'] > 1)
        })
        
        # Log essential statistics
        logger.info(f"Found {len(matches)} matches after {total_comparisons} comparisons")
        logger.info(f"Match rate: {self.stats['match_rate']:.2%}")
        logger.info(f"Records with multiple matches: {self.stats['multiple_matches']}")
        
        return matches
    
    def merge_records(self) -> pd.DataFrame:
        """
        Merge matching records into a single deduplicated record.
        
        This method:
        1. Processes all matches to create merged records
        2. Handles multiple records from dataset B matching with a single record from dataset A
        3. Adds unmatched records from both datasets
        4. Assigns persistent consumer IDs to all records
        5. Excludes the record_id column from the output
        
        Returns:
            DataFrame containing all resolved records (merged and unmatched)
        """
        logger.info("Starting record merging process")
        
        # Create sets of all record IDs from each dataset
        all_record_ids_a = set(self.dataset_a['record_id'].unique())
        all_record_ids_b = set(self.dataset_b['record_id'].unique())
        
        # Create a dictionary to store merged records
        merged_records = {}
        
        # Track matched record IDs
        matched_record_ids_a = set()
        matched_record_ids_b = set()
        
        # Group matches by record_a_id to handle multiple matches
        matches_by_a = {}
        for match in self.matches:
            record_a_id = match['record_a_id']
            if record_a_id not in matches_by_a:
                matches_by_a[record_a_id] = []
            matches_by_a[record_a_id].append(match)
        
        # Process matches
        for record_a_id, matches_list in matches_by_a.items():
            # Add to matched records sets
            matched_record_ids_a.add(record_a_id)
            
            # Get the record from dataset A
            record_a = self.dataset_a[self.dataset_a['record_id'] == record_a_id].iloc[0]
            
            # Get all matching records from dataset B
            records_b = []
            for match in matches_list:
                record_b_id = match['record_b_id']
                matched_record_ids_b.add(record_b_id)
                record_b = self.dataset_b[self.dataset_b['record_id'] == record_b_id].iloc[0]
                records_b.append((record_b, match['confidence_score']))
            
            # Create a merged record with all matching records
            merged_record = self._merge_multiple_records(record_a, records_b)
            
            # Use a unique key for merged records
            record_b_ids = '_'.join([r[0]['record_id'] for r in records_b])
            merged_key = f"merged_{record_a_id}_{record_b_ids}"
            merged_records[merged_key] = merged_record
        
        # Calculate unmatched records
        unmatched_record_ids_a = all_record_ids_a - matched_record_ids_a
        unmatched_record_ids_b = all_record_ids_b - matched_record_ids_b
        
        # Add unmatched records from dataset A
        for record_id in unmatched_record_ids_a:
            record = self.dataset_a[self.dataset_a['record_id'] == record_id].iloc[0]
            # Use a unique key for unmatched records from A
            merged_key = f"unmatched_a_{record_id}"
            merged_records[merged_key] = self._create_record_from_single(record)
        
        # Add unmatched records from dataset B
        for record_id in unmatched_record_ids_b:
            record = self.dataset_b[self.dataset_b['record_id'] == record_id].iloc[0]
            # Use a unique key for unmatched records from B
            merged_key = f"unmatched_b_{record_id}"
            merged_records[merged_key] = self._create_record_from_single(record)
        
        # Update stats
        self.stats['unmatched_a'] = len(unmatched_record_ids_a)
        self.stats['unmatched_b'] = len(unmatched_record_ids_b)
        self.stats['merged_records'] = len(merged_records)
        
        # Convert to DataFrame
        resolved_df = pd.DataFrame(list(merged_records.values()))
        
        # Save to instance variable
        self.resolved_records = resolved_df
        
        # Log final counts
        logger.info(f"Final counts:")
        logger.info(f"  Total records in A: {len(all_record_ids_a)}")
        logger.info(f"  Total records in B: {len(all_record_ids_b)}")
        logger.info(f"  Matches found: {len(self.matches)}")
        logger.info(f"  Unmatched from A: {len(unmatched_record_ids_a)}")
        logger.info(f"  Unmatched from B: {len(unmatched_record_ids_b)}")
        logger.info(f"  Total resolved records: {len(resolved_df)}")
        
        # Verify counts
        expected_total = len(all_record_ids_a) + len(all_record_ids_b) - len(matched_record_ids_b)
        logger.info(f"Expected total records: {expected_total}")
        logger.info(f"Actual total records: {len(resolved_df)}")
        
        return resolved_df
    
    def _merge_multiple_records(self, record_a: pd.Series, records_b: List[Tuple[pd.Series, float]]) -> Dict:
        """
        Merge multiple records into a single record with the best available data.
        
        Args:
            record_a: First record from dataset A
            records_b: List of tuples containing records from dataset B and their confidence scores
            
        Returns:
            Merged record as a dictionary
        """
        # Get or create consumer ID
        consumer_id = self._get_or_create_consumer_id(record_a)
        
        # Initialize merged record with record_a data
        merged = {
            'consumer_id': consumer_id,  # Add persistent consumer ID
            'first_name': record_a['first_name'],
            'last_name': record_a['last_name'],
            'street': record_a['street'],
            'city': record_a['city'],
            'state': record_a['state'],
            'zip': record_a['zip'],
            'email': record_a['email'],
            'phone': record_a['phone'],
            'confidence_score': max(r[1] for r in records_b),  # Use highest confidence score
            'source': 'MERGED',
            'original_ids': record_a['record_id']
        }
        
        # Map all records to the same consumer ID
        self.consumer_id_map[record_a['record_id']] = consumer_id
        
        # Add all record_b IDs to original_ids
        record_b_ids = [r[0]['record_id'] for r in records_b]
        # Sort the IDs to ensure consistent ordering
        record_b_ids.sort()
        # Join all IDs with underscores
        all_ids = [record_a['record_id']] + record_b_ids
        merged['original_ids'] = '_'.join(all_ids)
        
        # Map all record_b IDs to the same consumer ID
        for record_b, _ in records_b:
            self.consumer_id_map[record_b['record_id']] = consumer_id
        
        # Update merged record with non-empty values from record_b records
        for record_b, _ in records_b:
            for field in ['first_name', 'last_name', 'street', 'city', 'state', 'zip', 'email', 'phone']:
                if pd.isna(merged[field]) or merged[field] == '':
                    if not pd.isna(record_b[field]) and record_b[field] != '':
                        merged[field] = record_b[field]
        
        return merged
    
    def _create_record_from_single(self, record: pd.Series) -> Dict:
        """
        Create a record from a single unmatched record.
        
        Args:
            record: Single record
            
        Returns:
            Record as a dictionary with appropriate fields
        """
        # Generate consumer ID for single record
        consumer_id = self._get_or_create_consumer_id(record)
        
        # Create record dictionary without record_id
        return {
            'consumer_id': consumer_id,  # Add persistent consumer ID
            'first_name': record['first_name'],
            'last_name': record['last_name'],
            'street': record['street'],
            'city': record['city'],
            'state': record['state'],
            'zip': record['zip'],
            'email': record['email'],
            'phone': record['phone'],
            'confidence_score': 1.0,  # Single records have 100% confidence
            'source': 'SINGLE',
            'original_ids': record['record_id']  # Keep original_id for reference
        }
    
    def _calculate_name_score(self, record_a: pd.Series, record_b: pd.Series) -> float:
        """
        Calculate name match score using fuzzy matching.
        
        Args:
            record_a: First record
            record_b: Second record
            
        Returns:
            Name similarity score between 0 and 1
        """
        return are_names_match(
            f"{record_a['first_name']} {record_a['last_name']}",
            f"{record_b['first_name']} {record_b['last_name']}",
            threshold=NAME_MATCH_THRESHOLD
        )
    
    def _calculate_address_score(self, record_a: pd.Series, record_b: pd.Series) -> float:
        """
        Calculate address match score using fuzzy matching.
        
        Args:
            record_a: First record
            record_b: Second record
            
        Returns:
            Address similarity score between 0 and 1
        """
        return are_addresses_match(
            f"{record_a['street']}, {record_a['city']}, {record_a['state']} {record_a['zip']}",
            f"{record_b['street']}, {record_b['city']}, {record_b['state']} {record_b['zip']}",
            threshold=ADDRESS_MATCH_THRESHOLD
        )
    
    def _calculate_email_score(self, record_a: pd.Series, record_b: pd.Series) -> float:
        """
        Calculate email match score using fuzzy matching.
        
        Args:
            record_a: First record
            record_b: Second record
            
        Returns:
            Email similarity score between 0 and 1
        """
        # Handle empty email fields
        if pd.isna(record_a['email']) or pd.isna(record_b['email']):
            return 0.0
        return are_emails_match(
            record_a['email'],
            record_b['email'],
            threshold=EMAIL_MATCH_THRESHOLD
        )
    
    def _calculate_phone_score(self, record_a: pd.Series, record_b: pd.Series) -> float:
        """
        Calculate phone match score using fuzzy matching.
        
        Args:
            record_a: First record
            record_b: Second record
            
        Returns:
            Phone similarity score between 0 and 1
        """
        # Handle empty phone fields
        if pd.isna(record_a['phone']) or pd.isna(record_b['phone']):
            return 0.0
        return are_phones_match(
            record_a['phone'],
            record_b['phone'],
            threshold=PHONE_MATCH_THRESHOLD
        )
    
    def _log_match_attempt(self, record_a: pd.Series, record_b: pd.Series, scores: Dict) -> None:
        """
        Log match attempt details for auditing.
        
        Args:
            record_a: First record
            record_b: Second record
            scores: Dictionary of match scores and metadata
        """
        self.audit_log.append({
            'record_a_id': record_a['record_id'],
            'record_b_id': record_b['record_id'],
            'name_score': scores['name_score'],
            'address_score': scores['address_score'],
            'email_score': scores['email_score'],
            'phone_score': scores['phone_score'],
            'total_score': scores['total_score'],
            'matched': scores.get('matched', False),
            'timestamp': pd.Timestamp.now()
        })
    
    def save_results(self, output_file: Optional[str] = None, audit_file: Optional[str] = None) -> None:
        """
        Save matching results and audit log to CSV files.
        
        Args:
            output_file: Path to save matches (optional)
            audit_file: Path to save audit log (optional)
            
        Raises:
            Exception: If there's an error saving the results
        """
        try:
            # Save resolved records
            if self.resolved_records is not None and not self.resolved_records.empty:
                output_path = output_file or OUTPUT_FILE
                self.resolved_records.to_csv(output_path, index=False)
                logger.info(f"Saved {len(self.resolved_records)} resolved records to {output_path}")
                
                # Log summary statistics
                logger.info("Summary statistics:")
                logger.info(f"  Total records from A: {self.stats['total_records_a']}")
                logger.info(f"  Total records from B: {self.stats['total_records_b']}")
                logger.info(f"  Matches found: {self.stats['matches_found']}")
                logger.info(f"  Unmatched from A: {self.stats['unmatched_a']}")
                logger.info(f"  Unmatched from B: {self.stats['unmatched_b']}")
                logger.info(f"  Total resolved records: {self.stats['merged_records']}")
            
            # Save audit log
            audit_path = audit_file or AUDIT_LOG_FILE
            audit_df = pd.DataFrame(self.audit_log)
            audit_df.to_csv(audit_path, index=False)
            logger.info(f"Saved audit log with {len(audit_df)} entries to {audit_path}")
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
            raise

def main():
    """
    Main function to run the consumer resolution process.
    
    This function:
    1. Creates a ConsumerResolver instance
    2. Loads data from input files
    3. Finds matches between records
    4. Merges matching records
    5. Saves results to output files
    """
    start_time = datetime.now()
    logger.info(f"Starting consumer resolution process at {start_time}")
    
    try:
        resolver = ConsumerResolver()
        resolver.load_data()
        resolver.find_matches()
        resolver.merge_records()
        resolver.save_results()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Consumer resolution process completed successfully in {duration:.2f} seconds")
    except Exception as e:
        logger.error(f"Error in consumer resolution process: {str(e)}")
        raise

if __name__ == "__main__":
    main() 