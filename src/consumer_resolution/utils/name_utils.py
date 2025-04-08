"""
Utilities for name matching and standardization.
"""

import re
from typing import Tuple, List, Set
from thefuzz import fuzz
from consumer_resolution.config.settings import NICKNAME_MAPPINGS, NAME_MATCH_THRESHOLD

def normalize_name(name: str) -> str:
    """
    Normalize a name by removing special characters and converting to lowercase.
    
    Args:
        name: The name to normalize
        
    Returns:
        Normalized name string
    """
    if not name or not isinstance(name, str):
        return ""
    
    # Remove special characters and extra spaces
    name = re.sub(r'[^\w\s]', '', name)
    name = ' '.join(name.split())
    return name.lower()

def get_name_variations(name: str) -> List[str]:
    """
    Get all possible variations of a name including nicknames and spelling variations.
    
    Args:
        name: The name to get variations for
        
    Returns:
        List of name variations
    """
    name = normalize_name(name)
    variations = {name}
    
    # Check if the name is a nickname
    for nickname, full_names in NICKNAME_MAPPINGS.items():
        if name == nickname:
            variations.update(full_names)
        elif name in full_names:
            variations.add(nickname)
            variations.update(full_names)
    
    # Add spelling variations
    spelling_variations = get_spelling_variations(name)
    variations.update(spelling_variations)
    
    return list(variations)

def get_spelling_variations(name: str) -> Set[str]:
    """
    Generate spelling variations of a name using fuzzy matching.
    
    Args:
        name: The name to get spelling variations for
        
    Returns:
        Set of spelling variations
    """
    variations = set()
    
    # Common spelling mistakes and variations
    common_variations = {
        'a': ['e', 'i', 'o', 'u'],
        'e': ['a', 'i', 'o', 'u'],
        'i': ['a', 'e', 'o', 'u', 'y'],
        'o': ['a', 'e', 'i', 'u'],
        'u': ['a', 'e', 'i', 'o'],
        'y': ['i'],
        'ie': ['ei', 'y'],
        'ei': ['ie', 'y'],
        'ou': ['u'],
        'oo': ['u'],
        'ee': ['ea', 'ie'],
        'ea': ['ee', 'ie'],
        'ph': ['f'],
        'f': ['ph'],
        'k': ['c'],
        'c': ['k'],
        's': ['c', 'z'],
        'z': ['s'],
        'x': ['ks'],
        'ks': ['x']
    }
    
    # Generate variations by replacing characters
    for i, char in enumerate(name):
        if char in common_variations:
            for replacement in common_variations[char]:
                variation = name[:i] + replacement + name[i+1:]
                variations.add(variation)
        
        # Check for common two-character combinations
        if i < len(name) - 1:
            two_chars = name[i:i+2]
            if two_chars in common_variations:
                for replacement in common_variations[two_chars]:
                    variation = name[:i] + replacement + name[i+2:]
                    variations.add(variation)
    
    # Add common misspellings
    common_misspellings = {
        'michael': ['micheal', 'michal', 'michail'],
        'jennifer': ['jenifer', 'jenniffer', 'jeniffer'],
        'christopher': ['cristopher', 'chrisopher', 'christofer'],
        'stephanie': ['stephany', 'stefanie', 'stefani'],
        'nicholas': ['nickolas', 'nicolas', 'nick'],
        'katherine': ['catherine', 'kathryn', 'cathryn'],
        'andrew': ['andrew', 'andre', 'andru'],
        'jessica': ['jesica', 'jessika', 'jesika'],
        'daniel': ['danial', 'danielle', 'dani'],
        'sarah': ['sara', 'sarra', 'sara']
    }
    
    name_lower = name.lower()
    if name_lower in common_misspellings:
        variations.update(common_misspellings[name_lower])
    
    return variations

def calculate_name_similarity(name1: str, name2: str) -> float:
    """
    Calculate similarity between two names considering nicknames.
    
    Args:
        name1: First name
        name2: Second name
        
    Returns:
        Similarity score between 0 and 1
    """
    name1 = normalize_name(name1)
    name2 = normalize_name(name2)
    
    if name1 == name2:
        return 1.0
    
    # Get all variations of both names
    variations1 = get_name_variations(name1)
    variations2 = get_name_variations(name2)
    
    # Calculate maximum similarity between any variation
    max_similarity = 0.0
    for var1 in variations1:
        for var2 in variations2:
            # Use token sort ratio to handle word order differences
            similarity = fuzz.token_sort_ratio(var1, var2) / 100.0
            max_similarity = max(max_similarity, similarity)
    
    return max_similarity

def parse_full_name(full_name: str) -> Tuple[str, str]:
    """
    Parse a full name into first and last name components.
    
    Args:
        full_name: The full name to parse
        
    Returns:
        Tuple of (first_name, last_name)
    """
    if not full_name:
        return "", ""
    
    parts = full_name.strip().split()
    if len(parts) == 1:
        return parts[0], ""
    elif len(parts) == 2:
        return parts[0], parts[1]
    else:
        # Assume first part is first name and last part is last name
        return parts[0], parts[-1]

def are_names_match(name1: str, name2: str, threshold: float = None) -> float:
    """
    Check if two names match using fuzzy matching and variations.
    
    Args:
        name1: First name to compare
        name2: Second name to compare
        threshold: Minimum similarity score to consider a match
        
    Returns:
        Similarity score between 0 and 1
    """
    if threshold is None:
        threshold = NAME_MATCH_THRESHOLD
    
    # Get all variations of both names
    variations1 = get_name_variations(name1)
    variations2 = get_name_variations(name2)
    
    # Calculate maximum similarity between any variation
    max_similarity = 0.0
    for var1 in variations1:
        for var2 in variations2:
            # Use token sort ratio for better matching of name parts
            similarity = fuzz.token_sort_ratio(var1, var2) / 100.0
            max_similarity = max(max_similarity, similarity)
    
    return max_similarity 