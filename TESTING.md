# Testing Guide for Coding-LLM-Monitor

## Testing Strategy

This application should be tested using a combination of:
1. **Unit Tests** - For pure functions and logic
2. **Integration Tests** - For async functions with mocked HTTP requests
3. **End-to-End Tests** - Optional, for full workflow validation

## Test Structure

```
tests/
├── __init__.py
├── test_status_parsing.py      # Status emoji/style functions
├── test_config_validation.py   # Configuration validation
├── test_parsers.py             # JSON/HTML parsing functions
├── test_fetch_status.py        # HTTP fetching with mocks
├── test_table_generation.py    # UI table generation
└── fixtures/                    # Test data fixtures
    ├── github_status.json
    ├── statuspage_status.json
    └── gcp_status.html
```

## Testing Framework

We use **pytest** with the following plugins:
- `pytest-asyncio` - For async test support
- `pytest-mock` - For mocking
- `aioresponses` - For mocking aiohttp requests

## Running Tests

```bash
# 1. Create/activate virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install test dependencies (includes runtime dependencies)
pip install -r requirements-test.txt

# 3. Run all tests
pytest

# Run with coverage
pytest --cov=status --cov-report=html

# Run specific test file
pytest tests/test_status_parsing.py

# Run with verbose output
pytest -v
```

## Test Categories

### 1. Unit Tests (Pure Functions)

These test functions that don't require external dependencies:

- `get_status_emoji()` - Test all status indicators
- `get_status_style()` - Test style mapping
- `_is_operational_status()` - Test status detection
- `_is_degraded_status()` - Test status detection
- `_is_outage_status()` - Test status detection
- `validate_service_config()` - Test configuration validation
- `generate_table()` - Test table generation (with mocked Rich)

### 2. Integration Tests (With Mocks)

These test functions that interact with external services:

- `_parse_statuspage_json()` - Test JSON parsing
- `_parse_github_json()` - Test GitHub-specific parsing
- `_parse_gcp_html()` - Test HTML parsing
- `fetch_status()` - Test HTTP fetching with mocked responses

### 3. Error Handling Tests

Test error scenarios:
- Network timeouts
- Connection errors
- Invalid JSON responses
- Missing HTML elements
- Invalid service configurations
- HTTP error status codes

### 4. Edge Cases

- Empty service lists
- Missing component names
- Case-insensitive matching
- Partial component name matches
- Unknown status indicators

## Mocking Strategy

### HTTP Requests

Use `aioresponses` to mock aiohttp requests:

```python
import aioresponses

@aioresponses()
async def test_fetch_status_success(m):
    m.get('https://status.example.com/api/v2/status.json',
          payload={'status': {'indicator': 'operational'}})
    # ... test code
```

### HTML Content

Use fixtures for HTML responses:

```python
@pytest.fixture
def gcp_html_fixture():
    with open('tests/fixtures/gcp_status.html') as f:
        return f.read()
```

## Coverage Goals

- **Target**: 80%+ code coverage
- **Critical paths**: 100% coverage
  - Status parsing logic
  - Error handling
  - Configuration validation

## Continuous Integration

Tests should run on:
- Python 3.8+
- Before each commit (pre-commit hook)
- In CI/CD pipeline

## Writing New Tests

1. Follow the existing test structure
2. Use descriptive test names: `test_function_name_scenario()`
3. Test both success and failure cases
4. Use fixtures for reusable test data
5. Mock external dependencies
6. Keep tests fast and isolated

