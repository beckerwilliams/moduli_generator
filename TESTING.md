# Testing Framework Documentation

This document describes the pytest testing framework that has been set up for the Moduli Generator project.

## Overview

The project now uses pytest as the primary testing framework, providing comprehensive test coverage for:

- Parameter validation and security
- CLI argument parsing
- Database configuration parsing
- Integration testing
- Security-focused testing

## Test Structure

```
test/
├── conftest.py                      # Shared fixtures and configuration
├── test_parameter_validation.py     # Parameter validation tests
├── test_cli_argument_parsing.py     # CLI argument parsing tests
├── test_mariadb_cnf_parser.py      # MariaDB configuration parsing tests
└── test_moduli_generator_show_stats.py  # Database statistics tests
```

## Running Tests

### Prerequisites

Install the required testing dependencies:

```bash
pip install pytest pytest-cov pytest-mock pytest-asyncio
```

### Basic Test Commands

#### Run All Tests

```bash
pytest
```

#### Run Tests with Verbose Output

```bash
pytest -v
```

#### Run Tests by Category

**Unit Tests Only:**

```bash
pytest -m unit
```

**Integration Tests Only:**

```bash
pytest -m integration
```

**Security Tests Only:**

```bash
pytest -m security
```

**Fast Tests (excluding slow ones):**

```bash
pytest -m "not slow"
```

#### Run Specific Test Files

```bash
pytest test/test_parameter_validation.py
pytest test/test_cli_argument_parsing.py
```

#### Run Specific Test Classes or Methods

```bash
pytest test/test_parameter_validation.py::TestValidateIntegerParameters
pytest test/test_parameter_validation.py::TestValidateIntegerParameters::test_valid_parameters
```

### Coverage Reporting

#### Generate Coverage Report

```bash
pytest --cov=moduli_generator --cov=db --cov=config
```

#### Generate HTML Coverage Report

```bash
pytest --cov=moduli_generator --cov=db --cov=config --cov-report=html
```

The HTML report will be generated in the `htmlcov/` directory. Open `htmlcov/index.html` in a browser to view detailed
coverage information.

#### Generate XML Coverage Report (for CI)

```bash
pytest --cov=moduli_generator --cov=db --cov=config --cov-report=xml
```

### Using Poetry Scripts (if available)

If you're using Poetry, you can use the predefined test scripts:

```bash
poetry run test                 # Run all tests
poetry run test-unit           # Run unit tests only
poetry run test-integration    # Run integration tests only
poetry run test-security       # Run security tests only
poetry run test-coverage       # Run tests with coverage
poetry run test-fast           # Run fast tests only
```

## Test Configuration

The pytest configuration is defined in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["test"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--verbose",
    "--cov=moduli_generator",
    "--cov=db",
    "--cov=config",
    "--cov-report=term-missing",
    "--cov-report=html:htmlcov",
    "--cov-report=xml",
]
```

## Test Markers

The following markers are available to categorize tests:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (may be slower)
- `@pytest.mark.security` - Security-focused tests
- `@pytest.mark.slow` - Tests that take longer to run

### Using Markers

```python
@pytest.mark.unit
@pytest.mark.security
def test_parameter_validation():
    # Test implementation
    pass
```

## Fixtures

Common fixtures are available in `conftest.py`:

- `temp_file` - Creates a temporary file for testing
- `temp_dir` - Creates a temporary directory
- `sample_config_content` - Sample MariaDB configuration content
- `sample_config_dict` - Parsed configuration dictionary
- `mock_db_connector` - Mock database connector
- `valid_cli_args` - Valid CLI arguments for testing
- `mock_subprocess` - Mock subprocess for command testing

### Using Fixtures

```python
def test_config_parsing(temp_file, sample_config_content):
    with open(temp_file, 'w') as f:
        f.write(sample_config_content)
    
    # Test implementation using temp_file
    pass
```

## Test Examples

### Parameter Validation Test

```python
@pytest.mark.unit
@pytest.mark.security
def test_key_length_validation():
    # Test valid key length
    key_length, nice_value = validate_integer_parameters(4096, 10)
    assert key_length == 4096
    
    # Test invalid key length
    with pytest.raises(ValueError, match="key_length .* is too small"):
        validate_integer_parameters(256, 10)
```

### CLI Argument Test

```python
@pytest.mark.unit
@pytest.mark.parametrize("key_length", [3072, 4096, 8192])
def test_valid_key_lengths(key_length):
    args = {'key_length': key_length, 'nice_value': 10}
    assert 3072 <= args['key_length'] <= 8192
    assert args['key_length'] % 8 == 0
```

### Integration Test

```python
@pytest.mark.integration
def test_config_file_integration(temp_file, sample_config_content):
    # Write config to file
    with open(temp_file, 'w') as f:
        f.write(sample_config_content)
    
    # Parse and validate
    config = parse_mysql_config(temp_file)
    assert 'client' in config
    assert config['client']['user'] == 'testuser'
```

## Best Practices

### Test Organization

- Group related tests in classes
- Use descriptive test names
- Add docstrings to explain test purpose
- Use appropriate markers

### Test Data

- Use fixtures for common test data
- Avoid hardcoded values when possible
- Use parametrized tests for multiple inputs

### Security Testing

- Test input validation thoroughly
- Test for command injection attempts
- Test boundary conditions
- Test type confusion scenarios

### Assertions

- Use specific assertions (`assert x == y` vs `assert x`)
- Use pytest.raises for exception testing
- Include meaningful error messages

## Continuous Integration

For CI/CD pipelines, use:

```bash
# Run all tests with coverage
pytest --cov=moduli_generator --cov=db --cov=config --cov-report=xml --junitxml=test-results.xml

# Run only fast tests for quick feedback
pytest -m "not slow" --cov=moduli_generator --cov=db --cov=config
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the project modules are in the Python path
2. **Missing Dependencies**: Install test dependencies with `pip install pytest pytest-cov pytest-mock pytest-asyncio`
3. **MariaDB Import Errors**: Some tests may require MariaDB dependencies or mocking

### Debug Mode

Run tests with more verbose output:

```bash
pytest -vvv --tb=long
```

### Running Single Test with Debug

```bash
pytest -vvv --tb=long test/test_parameter_validation.py::TestValidateIntegerParameters::test_valid_parameters
```

## Contributing

When adding new tests:

1. Follow the existing naming conventions
2. Add appropriate markers
3. Include docstrings
4. Use existing fixtures when possible
5. Add new fixtures to `conftest.py` if they're reusable
6. Ensure tests are deterministic and don't depend on external resources

## Test Coverage Goals

- **Unit Tests**: Aim for >90% coverage of core functionality
- **Integration Tests**: Cover major workflows and component interactions
- **Security Tests**: Cover all input validation and security-critical paths
- **Edge Cases**: Test boundary conditions and error scenarios