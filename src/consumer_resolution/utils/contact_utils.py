"""
Utilities for contact information matching and standardization.
"""

import re
from typing import Tuple
from thefuzz import fuzz
from consumer_resolution.config.settings import (
    EMAIL_MATCH_THRESHOLD,
    PHONE_MATCH_THRESHOLD
)

def normalize_email(email: str) -> str:
    """
    Normalize an email address by converting to lowercase and removing whitespace.
    
    Args:
        email: The email address to normalize
        
    Returns:
        Normalized email string
    """
    if not email or not isinstance(email, str):
        return ""
    
    # Convert to lowercase and remove whitespace
    email = email.lower().strip()
    
    # Basic email validation
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return ""
    
    return email

def normalize_phone(phone: str) -> str:
    """
    Normalize a phone number by removing non-digit characters.
    
    Args:
        phone: The phone number to normalize
        
    Returns:
        Normalized phone string (digits only)
    """
    if not phone or not isinstance(phone, str):
        return ""
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Handle common formats
    if len(digits) == 10:  # Standard US format
        return digits
    elif len(digits) == 11 and digits.startswith('1'):  # US format with country code
        return digits[1:]
    elif len(digits) > 10:  # International format
        return digits[-10:]  # Take last 10 digits
    
    return digits

def calculate_email_similarity(email1: str, email2: str) -> float:
    """
    Calculate similarity between two email addresses.
    
    Args:
        email1: First email
        email2: Second email
        
    Returns:
        Similarity score between 0 and 1
    """
    email1 = normalize_email(email1)
    email2 = normalize_email(email2)
    
    if not email1 or not email2:
        return 0.0
    
    if email1 == email2:
        return 1.0
    
    # Split into local part and domain
    local1, domain1 = email1.split('@')
    local2, domain2 = email2.split('@')
    
    # Calculate component-wise similarities
    local_similarity = fuzz.ratio(local1, local2) / 100.0
    domain_similarity = 1.0 if domain1 == domain2 else 0.0
    
    # Weight the components (domain match is more important)
    return 0.3 * local_similarity + 0.7 * domain_similarity

def calculate_phone_similarity(phone1: str, phone2: str) -> float:
    """
    Calculate similarity between two phone numbers.
    
    Args:
        phone1: First phone number
        phone2: Second phone number
        
    Returns:
        Similarity score between 0 and 1
    """
    phone1 = normalize_phone(phone1)
    phone2 = normalize_phone(phone2)
    
    if not phone1 or not phone2:
        return 0.0
    
    if phone1 == phone2:
        return 1.0
    
    # Calculate similarity based on longest common subsequence
    return fuzz.ratio(phone1, phone2) / 100.0

def are_emails_match(email1: str, email2: str, threshold: float = None) -> bool:
    """
    Determine if two email addresses match based on similarity threshold.
    
    Args:
        email1: First email
        email2: Second email
        threshold: Similarity threshold (default: from config)
        
    Returns:
        True if emails match, False otherwise
    """
    if threshold is None:
        threshold = EMAIL_MATCH_THRESHOLD
    
    similarity = calculate_email_similarity(email1, email2)
    return similarity >= threshold

def are_phones_match(phone1: str, phone2: str, threshold: float = None) -> bool:
    """
    Determine if two phone numbers match based on similarity threshold.
    
    Args:
        phone1: First phone number
        phone2: Second phone number
        threshold: Similarity threshold (default: from config)
        
    Returns:
        True if phone numbers match, False otherwise
    """
    if threshold is None:
        threshold = PHONE_MATCH_THRESHOLD
    
    similarity = calculate_phone_similarity(phone1, phone2)
    return similarity >= threshold 