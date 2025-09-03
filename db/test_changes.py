#!/usr/bin/env python3
"""
Test script to verify the refactored code works correctly.

This script tests:
1. The centralized utility functions in db/common.py
2. The standardized error handling in db/errors.py
"""

import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Import the refactored modules
from db.common import (
    is_valid_identifier_sql,
    parse_mysql_config,
    get_mysql_config_value
)

from db.errors import (
    ConfigError,
    handle_db_error,
    db_operation
)


def test_common_functions():
    """Test the centralized utility functions."""
    logger.info("Testing centralized utility functions...")

    # Test is_valid_identifier_sql
    assert is_valid_identifier_sql("valid_table_name") is True
    assert is_valid_identifier_sql("invalid-table-name") is False
    assert is_valid_identifier_sql("`valid_quoted_name`") is True
    assert is_valid_identifier_sql(None) is False

    # Test get_mysql_config_value
    test_config = {
        "section1": {
            "key1": "value1",
            "key2": "value2"
        }
    }
    assert get_mysql_config_value(test_config, "section1", "key1") == "value1"
    assert get_mysql_config_value(test_config, "section1", "missing", "default") == "default"

    # Test parse_mysql_config with an empty string (safe test)
    empty_config = parse_mysql_config("")
    assert isinstance(empty_config, dict)
    assert len(empty_config) == 0

    # Test with a temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w+') as temp:
        temp.write("[test]\nkey=value\n")
        temp.flush()
        config = parse_mysql_config(temp.name)
        assert isinstance(config, dict)
        assert "test" in config
        assert config["test"]["key"] == "value"

    logger.info("All common function tests passed!")


def test_error_handling():
    """Test the standardized error handling."""
    logger.info("Testing error handling utilities...")

    # Test basic exception handling
    try:
        raise ValueError("Test error")
    except Exception as e:
        # This should log the error and re-raise as ConfigError
        try:
            handle_db_error(e, logger, "Test error handling", reraise=True,
                            reraise_as=ConfigError)
            assert False, "Should have raised an exception"
        except ConfigError:
            logger.info("Correctly caught and converted exception")

    # Test the decorator
    @db_operation(error_message="Test operation failed", reraise=False, default_value=False)
    def failing_operation():
        raise ValueError("Operation failed")
        return True

    result = failing_operation()
    assert result is False, "Should return default value when operation fails"

    logger.info("All error handling tests passed!")


def main():
    """Main test function."""
    logger.info("Starting tests...")

    test_common_functions()
    test_error_handling()

    logger.info("All tests passed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
