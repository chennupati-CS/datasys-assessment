"""
Unit tests for consumer identity resolution matching functions.
"""

import unittest
from consumer_resolution.utils.name_utils import (
    normalize_name,
    get_name_variations,
    calculate_name_similarity,
    parse_full_name,
    are_names_match
)
from consumer_resolution.utils.address_utils import (
    normalize_address,
    parse_address,
    calculate_address_similarity,
    are_addresses_match
)
from consumer_resolution.utils.contact_utils import (
    normalize_email,
    normalize_phone,
    calculate_email_similarity,
    calculate_phone_similarity,
    are_emails_match,
    are_phones_match
)
from consumer_resolution.config.settings import (
    NAME_MATCH_THRESHOLD,
    ADDRESS_MATCH_THRESHOLD,
    EMAIL_MATCH_THRESHOLD,
    PHONE_MATCH_THRESHOLD
)

class TestNameMatching(unittest.TestCase):
    """Test cases for name matching functionality."""
    
    def test_normalize_name(self):
        """Test name normalization."""
        self.assertEqual(normalize_name("John Doe"), "john doe")
        self.assertEqual(normalize_name("John-Doe"), "john doe")
        self.assertEqual(normalize_name("John  Doe"), "john doe")
        self.assertEqual(normalize_name(""), "")
        self.assertEqual(normalize_name(None), "")
    
    def test_get_name_variations(self):
        """Test getting name variations including nicknames."""
        variations = get_name_variations("Bob")
        self.assertIn("bob", variations)
        self.assertIn("robert", variations)
        
        variations = get_name_variations("Robert")
        self.assertIn("bob", variations)
        self.assertIn("robert", variations)
    
    def test_calculate_name_similarity(self):
        """Test name similarity calculation."""
        self.assertEqual(calculate_name_similarity("John", "John"), 1.0)
        self.assertEqual(calculate_name_similarity("John", "Jane"), 0.0)
        self.assertGreater(calculate_name_similarity("Bob", "Robert"), 0.8)
    
    def test_parse_full_name(self):
        """Test parsing full names."""
        first, last = parse_full_name("John Doe")
        self.assertEqual(first, "John")
        self.assertEqual(last, "Doe")
        
        first, last = parse_full_name("John")
        self.assertEqual(first, "John")
        self.assertEqual(last, "")
        
        first, last = parse_full_name("John James Doe")
        self.assertEqual(first, "John")
        self.assertEqual(last, "Doe")
    
    def test_are_names_match(self):
        """Test name matching with threshold."""
        self.assertTrue(are_names_match("John", "John"))
        self.assertFalse(are_names_match("John", "Jane"))
        self.assertTrue(are_names_match("Bob", "Robert"))
        
        # Test custom threshold
        self.assertTrue(are_names_match("John", "Jon", threshold=0.8))
        self.assertFalse(are_names_match("John", "Jon", threshold=0.95))

class TestAddressMatching(unittest.TestCase):
    """Test cases for address matching functionality."""
    
    def test_normalize_address(self):
        """Test address normalization."""
        self.assertEqual(normalize_address("123 Main St"), "123 main st")
        self.assertEqual(normalize_address("123 Main Street"), "123 main street")
        self.assertEqual(normalize_address("123 Main-St"), "123 main st")
        self.assertEqual(normalize_address(""), "")
        self.assertEqual(normalize_address(None), "")
    
    def test_parse_address(self):
        """Test parsing addresses."""
        street, city, state = parse_address("123 Main St, New York, NY")
        self.assertEqual(street, "123 Main St")
        self.assertEqual(city, "New York")
        self.assertEqual(state, "NY")
        
        street, city, state = parse_address("123 Main St")
        self.assertEqual(street, "123 Main St")
        self.assertEqual(city, "")
        self.assertEqual(state, "")
    
    def test_calculate_address_similarity(self):
        """Test address similarity calculation."""
        self.assertEqual(calculate_address_similarity("123 Main St", "123 Main St"), 1.0)
        self.assertEqual(calculate_address_similarity("123 Main St", "456 Oak Ave"), 0.0)
        self.assertGreater(calculate_address_similarity("123 Main St", "123 Main Street"), 0.8)
    
    def test_are_addresses_match(self):
        """Test address matching with threshold."""
        self.assertTrue(are_addresses_match("123 Main St", "123 Main St"))
        self.assertFalse(are_addresses_match("123 Main St", "456 Oak Ave"))
        self.assertTrue(are_addresses_match("123 Main St", "123 Main Street"))
        
        # Test custom threshold
        self.assertTrue(are_addresses_match("123 Main St", "123 Main Street", threshold=0.8))
        self.assertFalse(are_addresses_match("123 Main St", "123 Main Street", threshold=0.95))

class TestContactMatching(unittest.TestCase):
    """Test cases for contact information matching functionality."""
    
    def test_normalize_email(self):
        """Test email normalization."""
        self.assertEqual(normalize_email("test@example.com"), "test@example.com")
        self.assertEqual(normalize_email("TEST@EXAMPLE.COM"), "test@example.com")
        self.assertEqual(normalize_email(" test@example.com "), "test@example.com")
        self.assertEqual(normalize_email(""), "")
        self.assertEqual(normalize_email(None), "")
        self.assertEqual(normalize_email("invalid-email"), "")
    
    def test_normalize_phone(self):
        """Test phone number normalization."""
        self.assertEqual(normalize_phone("123-456-7890"), "1234567890")
        self.assertEqual(normalize_phone("(123) 456-7890"), "1234567890")
        self.assertEqual(normalize_phone("+1 123-456-7890"), "1234567890")
        self.assertEqual(normalize_phone(""), "")
        self.assertEqual(normalize_phone(None), "")
    
    def test_calculate_email_similarity(self):
        """Test email similarity calculation."""
        self.assertEqual(calculate_email_similarity("test@example.com", "test@example.com"), 1.0)
        self.assertEqual(calculate_email_similarity("test@example.com", "other@example.com"), 0.0)
        self.assertGreater(calculate_email_similarity("test@example.com", "test@example.co"), 0.3)
    
    def test_calculate_phone_similarity(self):
        """Test phone number similarity calculation."""
        self.assertEqual(calculate_phone_similarity("1234567890", "1234567890"), 1.0)
        self.assertEqual(calculate_phone_similarity("1234567890", "9876543210"), 0.0)
        self.assertGreater(calculate_phone_similarity("1234567890", "1234567891"), 0.9)
    
    def test_are_emails_match(self):
        """Test email matching with threshold."""
        self.assertTrue(are_emails_match("test@example.com", "test@example.com"))
        self.assertFalse(are_emails_match("test@example.com", "other@example.com"))
        self.assertTrue(are_emails_match("test@example.com", "test@example.co"))
        
        # Test custom threshold
        self.assertTrue(are_emails_match("test@example.com", "test@example.co", threshold=0.8))
        self.assertFalse(are_emails_match("test@example.com", "test@example.co", threshold=0.95))
    
    def test_are_phones_match(self):
        """Test phone number matching with threshold."""
        self.assertTrue(are_phones_match("1234567890", "1234567890"))
        self.assertFalse(are_phones_match("1234567890", "9876543210"))
        self.assertTrue(are_phones_match("1234567890", "1234567891"))
        
        # Test custom threshold
        self.assertTrue(are_phones_match("1234567890", "1234567891", threshold=0.8))
        self.assertFalse(are_phones_match("1234567890", "1234567891", threshold=0.95))

if __name__ == '__main__':
    unittest.main() 