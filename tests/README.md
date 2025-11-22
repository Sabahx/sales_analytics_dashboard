# Test Suite

Comprehensive test suite for the Sales Analytics Dashboard.

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures and test configuration
├── test_config.py             # Configuration module tests
├── test_database.py           # Database connection tests
├── test_etl_extract.py        # ETL extract module tests
├── test_etl_transform.py      # ETL transform module tests
├── test_etl_load.py           # ETL load module tests
└── test_integration_etl.py    # End-to-end ETL pipeline tests
```

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run with Coverage Report
```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/ -m unit -v

# Integration tests only
pytest tests/ -m integration -v

# ETL tests only
pytest tests/ -m etl -v

# Database tests only
pytest tests/ -m database -v
```

### Run Specific Test Files
```bash
pytest tests/test_etl_extract.py -v
pytest tests/test_etl_transform.py -v
pytest tests/test_etl_load.py -v
```

### Using the Test Runner Script
```bash
# Run all tests with coverage
python scripts/run_tests.py

# Run specific test types
python scripts/run_tests.py unit
python scripts/run_tests.py integration
```

## Test Coverage

Current coverage targets:
- **ETL Modules**: 100% coverage
- **Configuration**: 90%+ coverage
- **Overall Target**: 80%+ coverage

View detailed coverage report:
```bash
# Generate HTML report
pytest tests/ --cov=src --cov-report=html

# Open in browser
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac
xdg-open htmlcov/index.html  # Linux
```

## Test Fixtures

### Data Fixtures
- `sample_raw_data`: Raw sales data for testing
- `sample_clean_data`: Cleaned sales data for testing
- `temp_csv_file`: Temporary CSV file for file I/O tests

### Mock Fixtures
- `mock_db_connection`: Mocked database connection
- `mock_env_vars`: Test environment variables

### Analytics Fixtures
- `sample_kpi_data`: KPI test data
- `sample_revenue_trend`: Revenue trend test data
- `sample_product_data`: Product performance test data
- `sample_country_data`: Country performance test data

## Writing New Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Test Markers
Use markers to categorize tests:
```python
@pytest.mark.unit
@pytest.mark.etl
def test_my_function():
    pass
```

Available markers:
- `unit`: Unit tests
- `integration`: Integration tests
- `etl`: ETL pipeline tests
- `analytics`: Analytics module tests
- `database`: Database-related tests
- `slow`: Tests that take significant time

### Example Test
```python
import pytest
from src.etl.extract import extract_csv

@pytest.mark.unit
@pytest.mark.etl
class TestExtractCSV:
    def test_extract_success(self, temp_csv_file):
        """Test successful CSV extraction."""
        df = extract_csv(temp_csv_file)
        assert len(df) > 0
```

## Continuous Integration

Tests are automatically run on:
- Every commit
- Pull requests
- Before deployment

## Troubleshooting

### Import Errors
Ensure project root is in Python path:
```python
import sys
import os
sys.path.insert(0, os.path.abspath('..'))
```

### Database Tests
Database tests use mocked connections by default. No real database required.

### Coverage Reports
If coverage reports are not generated, ensure pytest-cov is installed:
```bash
pip install pytest-cov
```
