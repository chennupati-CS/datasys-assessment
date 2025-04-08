# Consumer Identity Resolution

A Python package for resolving consumer identities across datasets that lack a shared unique identifier. This package provides a robust solution for identifying and merging duplicate consumer records using fuzzy matching and rule-based logic.

## Features

- Fuzzy string matching for names, addresses, and contact information
- Rule-based matching with configurable thresholds
- Support for nickname variations and address standardization
- ZIP code blocking for performance optimization
- Detailed audit logging of matching decisions
- Confidence scoring for match quality
- Comprehensive test coverage
- **Model explainability** with detailed match reasoning
- **Robust error handling** and input validation
- **Edge case handling** for name/address inconsistencies

## Project Structure

```
consumer_identity_resolution/
├── src/
│   └── consumer_resolution/
│       ├── __init__.py
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── name_utils.py
│       │   ├── address_utils.py
│       │   └── contact_utils.py
│       └── resolver.py
├── tests/
│   └── test_matching.py
├── data/
│   ├── input/
│   └── output/
├── setup.py
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.8 or higher
- pandas
- numpy
- thefuzz

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/consumer_identity_resolution.git
cd consumer_identity_resolution
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package:
```bash
pip install -e .
```

## Usage

1. Place your input CSV files in the `data/input` directory:
   - Dataset A: `data/input/dataset_a.csv`
   - Dataset B: `data/input/dataset_b.csv`

2. Run the resolution process:
```python
from consumer_resolution.resolver import ConsumerResolver

resolver = ConsumerResolver()
resolver.load_data()
resolver.resolve_identities()
resolver.save_results()
```

3. Find the results in the `data/output` directory:
   - Resolved records: `data/output/resolved_records.csv`
   - Audit log: `data/output/audit_log.csv`

## Configuration

The package's behavior can be customized by modifying `src/consumer_resolution/config/settings.py`:

- Matching thresholds for names, addresses, emails, and phone numbers
- Field weights for scoring matches
- Common nickname mappings
- Address standardization rules
- File paths and logging configuration

## Matching Strategy

The resolution process uses a hybrid approach combining fuzzy string matching and rule-based logic:

1. **Preprocessing**:
   - Normalize names, addresses, and contact information
   - Standardize address formats and street suffixes
   - Handle common variations in names (nicknames)

2. **Blocking**:
   - Group records by ZIP code to reduce comparison space
   - Only compare records within the same ZIP code

3. **Matching**:
   - Calculate similarity scores for each field
   - Apply field-specific thresholds
   - Weight matches based on field reliability
   - Combine scores into a final match score

4. **Resolution**:
   - Merge matching records
   - Preserve non-empty values from either record
   - Calculate confidence scores
   - Log matching decisions for audit

## Model Explainability

The system is designed with transparency in mind:

- **Confidence Scores**: Each match is assigned a confidence score (0.0-1.0) based on weighted field comparisons
- **Match Details**: The audit log captures the individual scores for each field (name, address, email, phone)
- **Match Ranking**: When multiple matches are found, they are ranked by confidence score
- **Source Tracking**: Each record maintains information about its source dataset and original record IDs

## Threshold Tuning

The matching process uses configurable thresholds that can be adjusted based on your specific needs:

- **Name Matching**: Default threshold of 0.8 (80% similarity required)
- **Address Matching**: Default threshold of 0.7 (70% similarity required)
- **Email Matching**: Default threshold of 0.9 (90% similarity required)
- **Phone Matching**: Default threshold of 0.9 (90% similarity required)
- **Overall Match**: Weighted combination of all fields with configurable weights

These thresholds can be adjusted in the `settings.py` file to make the matching more or less strict.

## Input Validation and Error Handling

The system includes robust error handling:

- **Data Validation**: Checks for required fields and data types
- **Missing Value Handling**: Gracefully handles missing or null values in any field
- **Logging**: Comprehensive logging of all operations and errors
- **Exception Handling**: Graceful recovery from errors during processing

## Edge Case Handling

The system is designed to handle various edge cases:

- **Name Variations**: Handles nicknames, middle names, and name order differences
- **Address Inconsistencies**: Normalizes addresses with different formats, abbreviations, and spellings
- **Phone Format Variations**: Recognizes the same phone number in different formats
- **Email Variations**: Handles email addresses with different capitalization or formatting
- **Multiple Matches**: When a record matches with multiple others, all matches are preserved with confidence scores

## Testing

Run the test suite:
```bash
python -m unittest discover tests
```

## Performance Considerations

- The package uses ZIP code blocking to reduce the number of comparisons
- Fuzzy matching is optimized using the thefuzz library
- Efficient data structures are used for lookups
- Batch processing for large datasets

## Limitations

- Assumes US address formats
- Limited to English name variations
- May miss matches if data quality is poor
- Performance degrades with very large datasets

## Future Improvements

- Support for international address formats
- Machine learning-based matching
- Parallel processing for large datasets
- Additional field types (e.g., SSN, DOB)
- Web interface for configuration
- Real-time matching API

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 