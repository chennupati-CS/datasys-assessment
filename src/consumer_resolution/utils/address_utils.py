"""
Utilities for address matching and standardization.
"""

import re
from typing import Tuple
from thefuzz import fuzz
from consumer_resolution.config.settings import (
    STATE_MAPPINGS,
    STREET_SUFFIXES,
    ADDRESS_MATCH_THRESHOLD
)

def normalize_address(address: str) -> str:
    """
    Normalize an address by standardizing street suffixes and removing special characters.
    
    Args:
        address: The address to normalize
        
    Returns:
        Normalized address string
    """
    if not address or not isinstance(address, str):
        return ""
    
    # Convert to lowercase and remove extra spaces
    address = ' '.join(address.lower().split())
    
    # Standardize street suffixes
    for suffix, replacement in STREET_SUFFIXES.items():
        # Match whole words only
        pattern = r'\b' + re.escape(suffix) + r'\b'
        address = re.sub(pattern, replacement, address)
    
    # Remove special characters except for numbers and spaces
    address = re.sub(r'[^\w\s]', '', address)
    
    return address

def parse_address(address: str) -> Tuple[str, str, str]:
    """
    Parse an address into street, city, and state components.
    
    Args:
        address: The address to parse
        
    Returns:
        Tuple of (street, city, state)
    """
    if not address:
        return "", "", ""
    
    # Split address into components
    parts = address.split(',')
    if len(parts) < 2:
        return address.strip(), "", ""
    
    street = parts[0].strip()
    city_state = parts[1].strip().split()
    
    if len(city_state) < 2:
        return street, city_state[0] if city_state else "", ""
    
    state = city_state[-1]
    city = ' '.join(city_state[:-1])
    
    # Standardize state abbreviations
    state = STATE_MAPPINGS.get(state.lower(), state)
    
    return street, city, state

def calculate_address_similarity(addr1: str, addr2: str) -> float:
    """
    Calculate similarity between two addresses.
    
    Args:
        addr1: First address
        addr2: Second address
        
    Returns:
        Similarity score between 0 and 1
    """
    addr1 = normalize_address(addr1)
    addr2 = normalize_address(addr2)
    
    if addr1 == addr2:
        return 1.0
    
    # Parse addresses into components
    street1, city1, state1 = parse_address(addr1)
    street2, city2, state2 = parse_address(addr2)
    
    # Calculate component-wise similarities
    street_similarity = fuzz.ratio(street1, street2) / 100.0
    city_similarity = fuzz.ratio(city1, city2) / 100.0
    state_similarity = 1.0 if state1 == state2 else 0.0
    
    # Weight the components (street is most important)
    weights = [0.6, 0.3, 0.1]
    similarities = [street_similarity, city_similarity, state_similarity]
    
    return sum(w * s for w, s in zip(weights, similarities))

def are_addresses_match(addr1: str, addr2: str, threshold: float = None) -> bool:
    """
    Determine if two addresses match based on similarity threshold.
    
    Args:
        addr1: First address
        addr2: Second address
        threshold: Similarity threshold (default: from config)
        
    Returns:
        True if addresses match, False otherwise
    """
    if threshold is None:
        threshold = ADDRESS_MATCH_THRESHOLD
    
    similarity = calculate_address_similarity(addr1, addr2)
    return similarity >= threshold 