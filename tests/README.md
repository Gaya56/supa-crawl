# Test Structure Documentation

## Overview
This test suite follows Python testing best practices and official documentation from:
- **Crawl4AI**: https://docs.crawl4ai.com/
- **Supabase**: https://supabase.com/docs/
- **Python Testing**: https://docs.python.org/3/library/unittest.html
- **pytest**: https://docs.pytest.org/

## Directory Structure

```
tests/
├── __init__.py                           # Package initialization
├── crawl4ai/                            # Crawl4AI specific tests
│   ├── __init__.py
│   └── test_basic_crawling.py           # Basic AsyncWebCrawler functionality
├── supabase/                            # Supabase specific tests  
│   ├── __init__.py
│   └── test_database_operations.py      # Database CRUD operations
└── integration/                         # Integration tests
    ├── __init__.py
    └── test_crawl4ai_supabase.py        # Combined workflow tests
```

## Test Categories

### Unit Tests (`tests/crawl4ai/`, `tests/supabase/`)
- **Purpose**: Test individual components in isolation
- **Scope**: Single functionality, mocked dependencies where needed
- **Examples**: 
  - AsyncWebCrawler configuration validation
  - Browser settings verification
  - Database connection testing
  - CRUD operations

### Integration Tests (`tests/integration/`)
- **Purpose**: Test complete workflows combining multiple components
- **Scope**: Real external dependencies, end-to-end scenarios
- **Examples**:
  - Crawl web content → Store in database → Retrieve and validate
  - Multi-URL streaming crawl with real-time storage
  - Error handling across component boundaries

## Running Tests

### Method 1: Test Runner Script (Recommended)
```bash
# Run all tests
python run_tests.py

# Run specific test categories
python run_tests.py --crawl4ai        # Only Crawl4AI tests
python run_tests.py --supabase        # Only Supabase tests  
python run_tests.py --integration     # Only integration tests
python run_tests.py --async           # Only async tests
python run_tests.py --sync            # Only sync tests
```

### Method 2: Direct Execution
```bash
# Run individual test files
python tests/crawl4ai/test_basic_crawling.py
python tests/supabase/test_database_operations.py
python tests/integration/test_crawl4ai_supabase.py
```

### Method 3: pytest (if installed)
```bash
# Install pytest
pip install pytest pytest-asyncio

# Run with pytest
python run_tests.py --pytest
pytest tests/                          # All tests
pytest tests/crawl4ai/                 # Crawl4AI tests only
pytest tests/integration/              # Integration tests only
pytest -m "crawl4ai"                   # By marker
```

## Test Configuration

### Environment Variables Required
```bash
# For Supabase tests
export SUPABASE_URL="your-supabase-url"
export SUPABASE_ANON_KEY="your-supabase-anon-key"
```

### pytest Configuration (`pytest.ini`)
- Test discovery patterns
- Async test support 
- Output formatting
- Test markers for categorization
- Warning filters

## Test Implementation Details

### Crawl4AI Tests (`test_basic_crawling.py`)
- **AsyncWebCrawler API**: Tests based on official documentation
- **Browser Configuration**: Headless mode, verbose settings
- **Multi-URL Crawling**: `arun_many()` method testing
- **Streaming Mode**: Real-time processing with async iteration
- **Error Handling**: Graceful failure handling
- **Configuration Validation**: Browser and crawler config validation

### Supabase Tests (`test_database_operations.py`)
- **Database Operations**: INSERT, SELECT, UPDATE, DELETE
- **Filtering**: URL pattern matching with LIKE operator
- **Batch Operations**: Multiple record insertion
- **Connection Testing**: Client initialization validation
- **Cleanup**: Automatic test data removal

### Integration Tests (`test_crawl4ai_supabase.py`)
- **Complete Workflow**: Crawl → Store → Retrieve → Validate
- **Batch Processing**: Multiple URL crawling with batch storage
- **Streaming + Storage**: Real-time crawl results storage
- **Data Validation**: Content integrity verification
- **Timestamp Validation**: Created_at field verification
- **Error Scenarios**: Invalid URL handling

## Best Practices Followed

### Code Organization
- ✅ Separate test categories in dedicated directories
- ✅ Proper Python package structure with `__init__.py`
- ✅ Descriptive test file and function names
- ✅ Clear documentation and comments

### Test Design
- ✅ Independent test cases (no dependencies between tests)
- ✅ Proper setup and teardown methods
- ✅ Comprehensive assertions
- ✅ Error case testing
- ✅ Data cleanup after tests

### Documentation Standards
- ✅ Official documentation references in docstrings
- ✅ Clear test purpose and scope descriptions
- ✅ Usage examples in comments
- ✅ Configuration requirements documented

### Async Testing
- ✅ Proper async/await syntax
- ✅ Context managers for resource cleanup
- ✅ Async test runners
- ✅ Exception handling in async contexts

## Dependencies

### Required Packages
```bash
pip install crawl4ai supabase
```

### Optional Testing Packages
```bash
pip install pytest pytest-asyncio  # For pytest runner
```

### System Requirements
- Python 3.8+
- Network access for web crawling tests
- Supabase project with configured credentials

## Troubleshooting

### Common Issues
1. **ImportError**: Ensure all dependencies are installed in virtual environment
2. **Supabase Connection**: Verify environment variables are set correctly
3. **Network Timeouts**: Check internet connection for crawling tests
4. **Permission Errors**: Ensure Supabase RLS policies allow test operations

### Debug Mode
Add verbose output to troubleshoot issues:
```bash
python run_tests.py --verbose
```

### Individual Test Debugging
Run specific test methods for isolated debugging:
```python
# In Python REPL
import asyncio
from tests.crawl4ai.test_basic_crawling import TestAsyncWebCrawlerBasic

test = TestAsyncWebCrawlerBasic()
test.setUp()
asyncio.run(test.test_single_url_crawling())
```

## Test Maintenance

### Adding New Tests
1. Identify appropriate test category (unit vs integration)
2. Place in correct directory structure
3. Follow naming conventions (`test_*.py`)
4. Include proper docstrings with official doc references
5. Add cleanup methods for data persistence tests

### Updating Tests
1. Keep tests synchronized with API changes
2. Update official documentation references
3. Maintain backward compatibility where possible
4. Update pytest markers if categorization changes

### Performance Considerations
- Tests use cache bypass mode for consistent results
- Content truncation in tests to avoid large data storage
- Timeout settings appropriate for network conditions
- Cleanup operations to prevent test data accumulation