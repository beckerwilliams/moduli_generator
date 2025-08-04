"""
Pytest tests for MariaDB configuration parser functionality.

This module tests the configuration parsing functions that handle MariaDB
configuration files, ensuring proper parsing and error handling.
"""

import configparser
import os
import tempfile
from unittest.mock import patch

import pytest

# Import the functions to test
from db import get_mysql_config_value, parse_mysql_config


@pytest.fixture
def duplicate_section_config_content():
    """Configuration content with duplicate sections for testing."""
    return """
[client]
user=user1
password=pass1

[mysqld]
port=3306
bind-address=127.0.0.1

[mysql]
default-character-set=utf8mb4

# Some other configuration...
[mysql]
# This is a duplicate section that should be merged
socket=/var/run/mysqld/mysqld.sock
"""


@pytest.fixture
def duplicate_section_temp_file(duplicate_section_config_content):
    """Create a temporary file with duplicate sections for testing."""
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".cnf") as f:
        f.write(duplicate_section_config_content)
        f.flush()
        yield f.name
    # Cleanup
    if os.path.exists(f.name):
        os.unlink(f.name)


class TestGetMariaDBConfigValue:
    """Test cases for the get_mysql_config_value function."""

    @pytest.mark.unit
    def test_get_mysql_config_value_existing(self, sample_config_dict):
        """Test retrieving existing config values."""
        # Test regular key-value pairs
        assert (
            get_mysql_config_value(sample_config_dict, "client", "user") == "testuser"
        )
        assert get_mysql_config_value(sample_config_dict, "mysqld", "port") == "3307"

        # Test key with None value
        assert get_mysql_config_value(sample_config_dict, "mysqldump", "quick") is None

    @pytest.mark.unit
    def test_get_mysql_config_value_nonexistent_key(self, sample_config_dict):
        """Test retrieving nonexistent keys."""
        assert (
            get_mysql_config_value(sample_config_dict, "client", "nonexistent_key")
            is None
        )

    @pytest.mark.unit
    def test_get_mysql_config_value_nonexistent_section(self, sample_config_dict):
        """Test retrieving from nonexistent sections."""
        assert (
            get_mysql_config_value(sample_config_dict, "nonexistent_section", "user")
            is None
        )

    @pytest.mark.unit
    def test_get_mysql_config_value_with_empty_config(self):
        """Test get_mysql_config_value with empty config."""
        empty_config = {}
        assert get_mysql_config_value(empty_config, "client", "user") is None

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "section,key,expected",
        [
            ("client", "user", "testuser"),
            ("client", "password", "testpass"),
            ("client", "host", "localhost"),
            ("client", "port", "3306"),
            ("mysqld", "port", "3307"),
            ("mysqld", "bind-address", "127.0.0.1"),
            ("mysqld", "key_buffer_size", "16M"),
            ("mysqld", "max_allowed_packet", "1M"),
            ("mysqldump", "quick", None),
            ("mysqldump", "max_allowed_packet", "16M"),
        ],
    )
    def test_get_mysql_config_value_all_sample_values(
        self, sample_config_dict, section, key, expected
    ):
        """Test retrieving all values from sample config."""
        result = get_mysql_config_value(sample_config_dict, section, key)
        assert result == expected

    @pytest.mark.unit
    def test_get_mysql_config_value_case_sensitivity(self, sample_config_dict):
        """Test that config value retrieval is case-sensitive."""
        # These should return None because keys are case-sensitive
        assert get_mysql_config_value(sample_config_dict, "CLIENT", "user") is None
        assert get_mysql_config_value(sample_config_dict, "client", "USER") is None

    @pytest.mark.unit
    def test_get_mysql_config_value_with_default(self, sample_config_dict):
        """Test get_mysql_config_value with default values."""
        # Note: The current implementation doesn't support default values,
        # but we test the current behavior
        assert get_mysql_config_value(sample_config_dict, "nonexistent", "key") is None

    @pytest.mark.unit
    def test_get_mysql_config_value_with_none_config(self):
        """Test get_mysql_config_value with None config."""
        with pytest.raises(TypeError):
            get_mysql_config_value(None, "client", "user")

    @pytest.mark.unit
    def test_get_mysql_config_value_with_invalid_types(self):
        """Test that get_mysql_config_value raises TypeError for invalid types."""

        # Test with an invalid config type (should be ConfigParser, dict, or None)
        with pytest.raises(TypeError):
            get_mysql_config_value("invalid_config", "section", "key")

        with pytest.raises(TypeError):
            get_mysql_config_value(123, "section", "key")

        with pytest.raises(TypeError):
            get_mysql_config_value([], "section", "key")

        # Test with an invalid section type
        valid_config = {}
        with pytest.raises(TypeError):
            get_mysql_config_value(valid_config, 123, "key")

        with pytest.raises(TypeError):
            get_mysql_config_value(valid_config, None, "key")

        # Test with an invalid key type
        with pytest.raises(TypeError):
            get_mysql_config_value(valid_config, "section", 123)

        with pytest.raises(TypeError):
            get_mysql_config_value(valid_config, "section", None)

    # @pytest.mark.unit
    # def test_parse_mysql_config_with_empty_file(self, empty_temp_file):
    #     """Test parsing an empty configuration file."""
    #     result = parse_mysql_config(empty_temp_file)
    #     # Should return empty ConfigParser (which evaluates to empty dict when checked)
    #     assert len(result.sections()) == 0
    #     assert dict(result) == {}
    #
    # @pytest.mark.unit
    # def test_parse_mysql_config_with_valid_file(self, temp_file):
    #     """Test parsing a valid configuration file"""
    #     result = parse_mysql_config(temp_file)
    #
    #     # Check structure and values
    #     assert 'client' in result
    #     assert 'mysqld' in result
    #     assert 'mysqldump' in result
    #
    #     # Check specific values - comments should be stripped
    #     assert result['client']['user'] == 'testuser'  # Comment should be stripped
    #     assert result['client']['password'] == 'testpass'
    #     assert result['mysqld']['port'] == '3307'
    #     assert result['mysqldump']['quick'] is None
    #     assert result['mysqldump']['max_allowed_packet'] == '16M'

    @pytest.mark.unit
    def test_parse_mysql_config_with_comments(self, temp_file):
        """Test parsing a configuration file with comments."""
        result = parse_mysql_config(temp_file)

        # Check structure and values
        assert "client" in result
        assert "mysqld" in result
        assert "mysqldump" in result

        # Check specific values - inline comments should be stripped
        assert (
            result["client"]["user"] == "testuser"
        )  # Should NOT include "# inline comment"
        assert result["client"]["password"] == "testpass"
        assert result["mysqld"]["port"] == "3307"
        assert result["mysqldump"]["quick"] is None
        assert result["mysqldump"]["max_allowed_packet"] == "16M"


class TestParseMariaDBConfig:
    """Test cases for parsing MariaDB configuration files."""

    @pytest.mark.unit
    def test_parse_mysql_config_with_comments(self, temp_file):
        """Test parsing a configuration file with comments."""
        result = parse_mysql_config(temp_file.name)

        # Check structure and values
        assert "client" in result
        assert "mysqld" in result
        assert "mysqldump" in result

        # Check specific values
        assert result["client"]["user"] == "testuser"
        assert result["client"]["password"] == "testpass"
        assert result["mysqld"]["port"] == "3307"
        assert result["mysqldump"]["quick"] is None
        assert result["mysqldump"]["max_allowed_packet"] == "16M"

    @pytest.mark.unit
    def test_parse_mysql_config_with_nonexistent_file(self):
        """Test parsing a file that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            parse_mysql_config("/path/to/nonexistent/file.cnf")

    # @pytest.mark.unit
    # def test_parse_mysql_config_with_empty_file(self, temp_file):
    #     """Test parsing an empty configuration file."""
    #     # temp_file is already empty when created
    #     result = parse_mysql_config(temp_file)
    #     assert result == {} # Should return empty dict

    @pytest.mark.unit
    @patch("configparser.ConfigParser.read")
    def test_parse_mysql_config_with_parser_error(self, mock_read, temp_file):
        """Test handling of parser errors."""
        # Set up a mock to raise an exception
        mock_read.side_effect = configparser.Error("Test parsing error")

        with pytest.raises(ValueError, match="Error parsing configuration file"):
            parse_mysql_config(temp_file)

    @pytest.mark.unit
    def test_parse_mysql_config_with_malformed_file(self, temp_file):
        """Test parsing a malformed configuration file."""
        # Write malformed content to a temp file
        with open(temp_file, "w") as f:
            f.write("This is not a valid INI file format")

        # Should still parse without error, just with an empty result
        try:
            result = parse_mysql_config(temp_file)
            assert result == {}
        except ValueError:
            # This is also acceptable behavior for malformed files
            pass

    @pytest.mark.unit
    def test_parse_mysql_config_with_sections_only(self, temp_file):
        """Test parsing a file with sections but no values."""
        config_content = """
[client]
[mysqld]
[mysqldump]
"""
        with open(temp_file, "w") as f:
            f.write(config_content)

        result = parse_mysql_config(temp_file)

        # Should have sections but they should be empty
        assert "client" in result
        assert "mysqld" in result
        assert "mysqldump" in result
        assert len(result["client"]) == 0
        assert len(result["mysqld"]) == 0
        assert len(result["mysqldump"]) == 0

    @pytest.mark.unit
    def test_parse_mysql_config_with_comments(self, temp_file):
        """Test parsing a file with comments."""
        config_content = """
# This is a comment
[client]
user=testuser  # inline comment
# Another comment
password=testpass

[mysqld]
# Section comment
port=3307
"""
        with open(temp_file, "w") as f:
            f.write(config_content)

        result = parse_mysql_config(temp_file)

        # Comments should be ignored
        assert result["client"]["user"] == "testuser"
        assert result["client"]["password"] == "testpass"
        assert result["mysqld"]["port"] == "3307"


class TestMariaDBConfigIntegration:
    """Integration tests for MariaDB configuration parsing."""

    @pytest.mark.integration
    def test_parse_and_retrieve_workflow(self, temp_file, sample_config_content):
        """Test the complete workflow of parsing and retrieving values."""
        # Write sample config to a temp file
        with open(temp_file, "w") as f:
            f.write(sample_config_content)

        # Parse the config
        parsed_config = parse_mysql_config(temp_file)

        # Retrieve values using the parsed config
        user = get_mysql_config_value(parsed_config, "client", "user")
        password = get_mysql_config_value(parsed_config, "client", "password")
        port = get_mysql_config_value(parsed_config, "mysqld", "port")

        # Verify the values
        assert user == "testuser"
        assert password == "testpass"
        assert port == "3307"

    @pytest.mark.integration
    def test_real_world_config_structure(self, temp_file):
        """Test with a more realistic MariaDB configuration."""
        realistic_config = """
[mysql]
default-character-set=utf8mb4

[client]
port=3306
socket=/var/run/mysqld/mysqld.sock
default-character-set=utf8mb4

[mysqld_safe]
socket=/var/run/mysqld/mysqld.sock
nice=0

[mysqld]
user=mysql
pid-file=/var/run/mysqld/mysqld.pid
socket=/var/run/mysqld/mysqld.sock
port=3306
basedir=/usr
datadir=/var/lib/mysql
tmpdir=/tmp
lc-messages-dir=/usr/share/mysql
skip-external-locking
bind-address=127.0.0.1
key_buffer_size=16M
max_allowed_packet=16M
thread_stack=192K
thread_cache_size=8
myisam-recover-options=BACKUP
query_cache_limit=1M
query_cache_size=16M
log_error=/var/log/mysql/error.log
expire_logs_days=10
max_binlog_size=100M

[mysqldump]
quick
quote-names
max_allowed_packet=16M

[mysql]
no-auto-rehash

[isamchk]
key_buffer=16M
"""
        with open(temp_file, "w") as f:
            f.write(realistic_config)

        # Parse the config
        parsed_config = parse_mysql_config(temp_file)

        # Test various sections and values
        assert get_mysql_config_value(parsed_config, "client", "port") == "3306"
        assert get_mysql_config_value(parsed_config, "mysqld", "user") == "mysql"
        assert (
            get_mysql_config_value(parsed_config, "mysqld", "bind-address")
            == "127.0.0.1"
        )
        assert (
            get_mysql_config_value(parsed_config, "mysqldump", "quick") is None
        )  # Flag without value
        assert (
            get_mysql_config_value(parsed_config, "mysqldump", "max_allowed_packet")
            == "16M"
        )
        assert get_mysql_config_value(parsed_config, "isamchk", "key_buffer") == "16M"

    @pytest.mark.integration
    @pytest.mark.security
    def test_config_security_considerations(self, temp_file):
        """Test-security-related aspects of config parsing."""
        # Test config with potentially sensitive information
        sensitive_config = """
[client]
user=root
password=super_secret_password
host=production-db.company.com

[mysqld]
bind-address=0.0.0.0
"""
        with open(temp_file, "w") as f:
            f.write(sensitive_config)

        parsed_config = parse_mysql_config(temp_file)

        # Verify that sensitive data is parsed correctly
        # (In a real application, you'd want to ensure this data is handled securely)
        assert (
            get_mysql_config_value(parsed_config, "client", "password")
            == "super_secret_password"
        )
        assert (
            get_mysql_config_value(parsed_config, "client", "host")
            == "production-db.company.com"
        )
        assert (
            get_mysql_config_value(parsed_config, "mysqld", "bind-address") == "0.0.0.0"
        )
