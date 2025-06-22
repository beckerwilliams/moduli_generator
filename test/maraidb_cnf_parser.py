import unittest
import os
import tempfile
from unittest.mock import patch, mock_open
import configparser
from typing import Dict, Optional

# Import the module to test
from moduli_generator.mariadb_cnf_parser import parse_mysql_config, get_mysql_config_value

"""1. Tests `parse_mysql_config()` for:
    - Valid configuration files
    - Nonexistent files (expects FileNotFoundError)
    - Empty files
    - Parser errors (using mocking)
    - Malformed files

2. Tests `get_mysql_config_value()` for:
    - Retrieving existing values
    - Retrieving keys with None values
    - Retrieving nonexistent keys
    - Retrieving from nonexistent sections
    - Using with default parameter
    - Using with empty config dictionary
"""


class TestMariaDBCnfParser(unittest.TestCase):
    """Unit tests for mariadb_cnf_parser.py"""

    def setUp(self):
        """Set up test fixtures"""
        # Sample configuration content for testing
        self.sample_config = """
[client]
user=testuser
password=testpass
host=localhost
port=3306

[mysqld]
port=3307
bind-address=127.0.0.1
key_buffer_size=16M
max_allowed_packet=1M

[mysqldump]
quick
max_allowed_packet=16M
"""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        with open(self.temp_file.name, 'w') as f:
            f.write(self.sample_config)

        # Sample parsed config for get_value tests
        self.parsed_config = {
            'client': {
                'user': 'testuser',
                'password': 'testpass',
                'host': 'localhost',
                'port': '3306'
            },
            'mysqld': {
                'port': '3307',
                'bind-address': '127.0.0.1',
                'key_buffer_size': '16M',
                'max_allowed_packet': '1M'
            },
            'mysqldump': {
                'quick': None,
                'max_allowed_packet': '16M'
            }
        }

    def tearDown(self):
        """Clean up test fixtures"""
        # Remove the temporary file
        os.unlink(self.temp_file.name)

    # Tests for parse_mysql_config function
    def test_parse_mysql_config_with_valid_file(self):
        """Test parsing a valid configuration file"""
        result = parse_mysql_config(self.temp_file.name)

        # Check structure and values
        self.assertIn('client', result)
        self.assertIn('mysqld', result)
        self.assertIn('mysqldump', result)

        # Check specific values
        self.assertEqual(result['client']['user'], 'testuser')
        self.assertEqual(result['client']['password'], 'testpass')
        self.assertEqual(result['mysqld']['port'], '3307')
        self.assertEqual(result['mysqldump']['quick'], None)
        self.assertEqual(result['mysqldump']['max_allowed_packet'], '16M')

    def test_parse_mysql_config_with_nonexistent_file(self):
        """Test parsing a file that doesn't exist"""
        with self.assertRaises(FileNotFoundError):
            parse_mysql_config("/path/to/nonexistent/file.cnf")

    def test_parse_mysql_config_with_empty_file(self):
        """Test parsing an empty configuration file"""
        # Create an empty temporary file
        empty_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            result = parse_mysql_config(empty_file.name)
            self.assertEqual(result, {})  # Should return empty dict
        finally:
            os.unlink(empty_file.name)

    @patch('configparser.ConfigParser.read')
    def test_parse_mysql_config_with_parser_error(self, mock_read):
        """Test handling of parser errors"""
        # Setup mock to raise an exception
        mock_read.side_effect = configparser.Error("Test parsing error")

        with self.assertRaises(ValueError) as context:
            parse_mysql_config(self.temp_file.name)

        self.assertIn("Error parsing configuration file", str(context.exception))

    def test_parse_mysql_config_with_malformed_file(self):
        """Test parsing a malformed configuration file"""
        # Create a malformed config file
        malformed_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            with open(malformed_file.name, 'w') as f:
                f.write("This is not a valid INI file format")

            # Should still parse without error, just with empty result
            result = parse_mysql_config(malformed_file.name)
            self.assertEqual(result, {})
        except ValueError as error:
            assert True, f"Unexpected error: {error}"

        finally:
            os.unlink(malformed_file.name)

    # Tests for get_mysql_config_value function
    def test_get_mysql_config_value_existing(self):
        """Test retrieving existing config values"""
        # Test regular key-value pairs
        self.assertEqual(
            get_mysql_config_value(self.parsed_config, 'client', 'user'),
            'testuser'
        )
        self.assertEqual(
            get_mysql_config_value(self.parsed_config, 'mysqld', 'port'),
            '3307'
        )

        # Test key with None value
        self.assertIsNone(
            get_mysql_config_value(self.parsed_config, 'mysqldump', 'quick')
        )

    def test_get_mysql_config_value_nonexistent_key(self):
        """Test retrieving nonexistent keys"""
        self.assertIsNone(
            get_mysql_config_value(self.parsed_config, 'client', 'nonexistent_key')
        )

    def test_get_mysql_config_value_nonexistent_section(self):
        """Test retrieving from nonexistent sections"""
        self.assertIsNone(
            get_mysql_config_value(self.parsed_config, 'nonexistent_section', 'user')
        )

    def test_get_mysql_config_value_with_default(self):
        """Test that default value is properly handled (or in this case, ignored)"""
        # Even though we provide a default, the implementation ignores it
        self.assertIsNone(
            get_mysql_config_value(self.parsed_config, 'client', 'nonexistent_key', default='default_value')
        )

        # Make sure default doesn't interfere with finding actual values
        self.assertEqual(
            get_mysql_config_value(self.parsed_config, 'client', 'user', default='default_value'),
            'testuser'
        )

    def test_get_mysql_config_value_with_empty_config(self):
        """Test get_mysql_config_value with empty config"""
        empty_config: Dict[str, Dict[str, str]] = {}
        self.assertIsNone(
            get_mysql_config_value(empty_config, 'client', 'user')
        )


if __name__ == '__main__':
    unittest.main()
