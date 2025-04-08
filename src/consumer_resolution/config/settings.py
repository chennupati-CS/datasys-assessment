"""
Configuration settings for consumer identity resolution.
"""

import os
from pathlib import Path

# Get the project root directory (two levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"

# File paths
INPUT_FILE_A = INPUT_DIR / "file_a_with_nicknames.csv"
INPUT_FILE_B = INPUT_DIR / "file_b_with_nicknames.csv"
OUTPUT_FILE = OUTPUT_DIR / "resolved_records.csv"
AUDIT_LOG_FILE = OUTPUT_DIR / "audit_log.csv"

# Matching thresholds
NAME_MATCH_THRESHOLD = 0.85
ADDRESS_MATCH_THRESHOLD = 0.80
EMAIL_MATCH_THRESHOLD = 0.90
PHONE_MATCH_THRESHOLD = 0.95

# Field weights for scoring
FIELD_WEIGHTS = {
    'name': 0.3,
    'address': 0.3,
    'email': 0.2,
    'phone': 0.2
}

# Common nickname mappings
NICKNAME_MAPPINGS = {
    'bob': ['robert'],
    'rob': ['robert'],
    'bobby': ['robert'],
    'jim': ['james'],
    'jimmy': ['james'],
    'joe': ['joseph'],
    'joey': ['joseph'],
    'mike': ['michael'],
    'mikey': ['michael'],
    'tom': ['thomas'],
    'tommy': ['thomas'],
    'dick': ['richard'],
    'rick': ['richard'],
    'rich': ['richard'],
    'bill': ['william'],
    'billy': ['william'],
    'will': ['william'],
    'charlie': ['charles'],
    'chuck': ['charles'],
    'charlie': ['charles'],
    'ed': ['edward'],
    'eddie': ['edward'],
    'ted': ['edward'],
    'fred': ['frederick'],
    'freddie': ['frederick'],
    'george': ['george'],
    'georgie': ['george'],
    'harry': ['harry'],
    'henry': ['henry'],
    'hank': ['henry'],
    'jack': ['john'],
    'johnny': ['john'],
    'larry': ['lawrence'],
    'larry': ['larry'],
    'leo': ['leonard'],
    'len': ['leonard'],
    'lenny': ['leonard'],
    'matt': ['matthew'],
    'matty': ['matthew'],
    'nick': ['nicholas'],
    'nick': ['nick'],
    'nick': ['nick'],
    'paul': ['paul'],
    'pete': ['peter'],
    'pete': ['peter'],
    'pete': ['peter'],
    'sam': ['samuel'],
    'sammy': ['samuel'],
    'steve': ['steven'],
    'steve': ['stephen'],
    'steve': ['steve'],
    'tony': ['anthony'],
    'tony': ['anthony'],
    'tony': ['anthony'],
    'vince': ['vincent'],
    'vince': ['vincent'],
    'vince': ['vincent'],
    'walt': ['walter'],
    'walt': ['walter'],
    'walt': ['walter'],
    'zack': ['zachary'],
    'zack': ['zachary'],
    'zack': ['zachary'],
}

# Address standardization rules
STATE_MAPPINGS = {
    'al': 'AL', 'alabama': 'AL',
    'ak': 'AK', 'alaska': 'AK',
    'az': 'AZ', 'arizona': 'AZ',
    'ar': 'AR', 'arkansas': 'AR',
    'ca': 'CA', 'california': 'CA',
    'co': 'CO', 'colorado': 'CO',
    'ct': 'CT', 'connecticut': 'CT',
    'de': 'DE', 'delaware': 'DE',
    'fl': 'FL', 'florida': 'FL',
    'ga': 'GA', 'georgia': 'GA',
    'hi': 'HI', 'hawaii': 'HI',
    'id': 'ID', 'idaho': 'ID',
    'il': 'IL', 'illinois': 'IL',
    'in': 'IN', 'indiana': 'IN',
    'ia': 'IA', 'iowa': 'IA',
    'ks': 'KS', 'kansas': 'KS',
    'ky': 'KY', 'kentucky': 'KY',
    'la': 'LA', 'louisiana': 'LA',
    'me': 'ME', 'maine': 'ME',
    'md': 'MD', 'maryland': 'MD',
    'ma': 'MA', 'massachusetts': 'MA',
    'mi': 'MI', 'michigan': 'MI',
    'mn': 'MN', 'minnesota': 'MN',
    'ms': 'MS', 'mississippi': 'MS',
    'mo': 'MO', 'missouri': 'MO',
    'mt': 'MT', 'montana': 'MT',
    'ne': 'NE', 'nebraska': 'NE',
    'nv': 'NV', 'nevada': 'NV',
    'nh': 'NH', 'new hampshire': 'NH',
    'nj': 'NJ', 'new jersey': 'NJ',
    'nm': 'NM', 'new mexico': 'NM',
    'ny': 'NY', 'new york': 'NY',
    'nc': 'NC', 'north carolina': 'NC',
    'nd': 'ND', 'north dakota': 'ND',
    'oh': 'OH', 'ohio': 'OH',
    'ok': 'OK', 'oklahoma': 'OK',
    'or': 'OR', 'oregon': 'OR',
    'pa': 'PA', 'pennsylvania': 'PA',
    'ri': 'RI', 'rhode island': 'RI',
    'sc': 'SC', 'south carolina': 'SC',
    'sd': 'SD', 'south dakota': 'SD',
    'tn': 'TN', 'tennessee': 'TN',
    'tx': 'TX', 'texas': 'TX',
    'ut': 'UT', 'utah': 'UT',
    'vt': 'VT', 'vermont': 'VT',
    'va': 'VA', 'virginia': 'VA',
    'wa': 'WA', 'washington': 'WA',
    'wv': 'WV', 'west virginia': 'WV',
    'wi': 'WI', 'wisconsin': 'WI',
    'wy': 'WY', 'wyoming': 'WY',
    'dc': 'DC', 'district of columbia': 'DC',
}

STREET_SUFFIXES = {
    'avenue': 'ave',
    'ave': 'ave',
    'street': 'st',
    'st': 'st',
    'boulevard': 'blvd',
    'blvd': 'blvd',
    'drive': 'dr',
    'dr': 'dr',
    'lane': 'ln',
    'ln': 'ln',
    'road': 'rd',
    'rd': 'rd',
    'court': 'ct',
    'ct': 'ct',
    'circle': 'cir',
    'cir': 'cir',
    'place': 'pl',
    'pl': 'pl',
    'parkway': 'pkwy',
    'pkwy': 'pkwy',
    'square': 'sq',
    'sq': 'sq',
    'terrace': 'ter',
    'ter': 'ter',
}

# Logging configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO' 