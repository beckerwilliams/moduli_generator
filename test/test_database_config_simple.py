"""
Simple integration tests for database configuration functionality.

This module tests the basic database configuration parsing functions
without complex MariaDBConnector mocking.
"""

from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from db import get_mysql_config_value, parse_mysql_config


class TestDatabaseConfigParsing:
    """Test cases for database configuration parsing functions."""

    @pytest.mark.integration
    def test_parse_mysql_config_with_valid_file(self):
        """Test parsing a valid MySQL configuration file."""
        config_content = """
[client]
user = testuser
password = testpass
host = localhost
port = 3306

[mysqld]
port = 3307
bind-address = 127.0.0.1
key_buffer_size = 16M
max_allowed_packet = 1M

[mysqldump]
quick
max_allowed_packet = 16M
"""

        with patch("builtins.open", mock_open(read_data=config_content)):
            result = parse_mysql_config(Path("/test/my.cnf"))

        # Verify the structure
        assert isinstance(result, dict)
        assert "client" in result
        assert "mysqld" in result
        assert "mysqldump" in result

        # Verify client section
        assert result["client"]["user"] == "testuser"
        assert result["client"]["password"] == "testpass"
        assert result["client"]["host"] == "localhost"
        assert result["client"]["port"] == "3306"

        # Verify mysqld section
        assert result["mysqld"]["port"] == "3307"
        assert result["mysqld"]["bind-address"] == "127.0.0.1"
        assert result["mysqld"]["key_buffer_size"] == "16M"
        assert result["mysqld"]["max_allowed_packet"] == "1M"

        # Verify mysqldump section
        assert result["mysqldump"]["max_allowed_packet"] == "16M"

    @pytest.mark.integration
    def test_parse_mysql_config_file_not_found(self):
        """Test parsing when configuration file doesn't exist."""
        with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
            result = parse_mysql_config(Path("/nonexistent/my.cnf"))

        assert result == {}

    @pytest.mark.integration
    def test_parse_mysql_config_permission_error(self):
        """Test parsing when configuration file has permission issues."""
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            result = parse_mysql_config(Path("/restricted/my.cnf"))

        assert result == {}

    @pytest.mark.integration
    def test_parse_mysql_config_with_comments_and_empty_lines(self):
        """Test parsing configuration file with comments and empty lines."""
        config_content = """
# This is a comment
[client]
# User configuration
user = testuser
password = testpass

# Empty line above
host = localhost

[mysqld]
# Server configuration
port = 3307
"""

        with patch("builtins.open", mock_open(read_data=config_content)):
            result = parse_mysql_config(Path("/test/my.cnf"))

        assert result["client"]["user"] == "testuser"
        assert result["client"]["password"] == "testpass"
        assert result["client"]["host"] == "localhost"
        assert result["mysqld"]["port"] == "3307"

    @pytest.mark.integration
    def test_parse_mysql_config_malformed_file(self):
        """Test parsing malformed configuration file."""
        malformed_content = """
[client
user = testuser
invalid line without equals
[mysqld]
port = 3307
"""

        with patch("builtins.open", mock_open(read_data=malformed_content)):
            # Should raise ValueError on parsing error
            with pytest.raises(ValueError, match="Error parsing configuration file"):
                parse_mysql_config(Path("/test/malformed.cnf"))

    @pytest.mark.integration
    def test_parse_mysql_config_empty_file(self):
        """Test parsing empty configuration file."""
        with patch("builtins.open", mock_open(read_data="")):
            result = parse_mysql_config(Path("/test/empty.cnf"))

        assert result == {}

    @pytest.mark.integration
    def test_parse_mysql_config_only_sections(self):
        """Test parsing configuration file with only section headers."""
        config_content = """
[client]
[mysqld]
[mysqldump]
"""

        with patch("builtins.open", mock_open(read_data=config_content)):
            result = parse_mysql_config(Path("/test/sections_only.cnf"))

        assert "client" in result
        assert "mysqld" in result
        assert "mysqldump" in result
        assert len(result["client"]) == 0
        assert len(result["mysqld"]) == 0
        assert len(result["mysqldump"]) == 0


class TestGetMySQLConfigValue:
    """Test cases for get_mysql_config_value function."""

    @pytest.mark.integration
    def test_get_existing_value(self):
        """Test getting an existing configuration value."""
        config = {
            "client": {
                "user": "testuser",
                "password": "testpass",
                "host": "localhost",
                "port": "3306",
            },
            "mysqld": {"port": "3307", "bind-address": "127.0.0.1"},
        }

        # Test client section values
        assert get_mysql_config_value(config, "client", "user") == "testuser"
        assert get_mysql_config_value(config, "client", "password") == "testpass"
        assert get_mysql_config_value(config, "client", "host") == "localhost"
        assert get_mysql_config_value(config, "client", "port") == "3306"

        # Test mysqld section values
        assert get_mysql_config_value(config, "mysqld", "port") == "3307"
        assert get_mysql_config_value(config, "mysqld", "bind-address") == "127.0.0.1"

    @pytest.mark.integration
    def test_get_nonexistent_key(self):
        """Test getting a non-existent configuration key."""
        config = {"client": {"user": "testuser", "password": "testpass"}}

        # Test non-existent key in existing section
        assert get_mysql_config_value(config, "client", "nonexistent") is None

        # Test with default value
        assert (
            get_mysql_config_value(config, "client", "nonexistent", "default")
            == "default"
        )

    @pytest.mark.integration
    def test_get_value_from_nonexistent_section(self):
        """Test getting value from non-existent section."""
        config = {"client": {"user": "testuser"}}

        # Test non-existent section
        assert get_mysql_config_value(config, "nonexistent", "key") is None

        # Test with default value
        assert (
            get_mysql_config_value(config, "nonexistent", "key", "default") == "default"
        )

    @pytest.mark.integration
    def test_get_value_from_empty_config(self):
        """Test getting value from empty configuration."""
        config = {}

        assert get_mysql_config_value(config, "client", "user") is None
        assert get_mysql_config_value(config, "client", "user", "default") == "default"

    @pytest.mark.integration
    def test_get_value_with_various_defaults(self):
        """Test getting values with various default types."""
        config = {"client": {"user": "testuser"}}

        # Test different default types
        assert (
            get_mysql_config_value(config, "client", "missing", "string_default")
            == "string_default"
        )
        assert get_mysql_config_value(config, "client", "missing", 123) == 123
        assert get_mysql_config_value(config, "client", "missing", True) is True
        assert get_mysql_config_value(config, "client", "missing", [1, 2, 3]) == [
            1,
            2,
            3,
        ]
        assert get_mysql_config_value(
            config, "client", "missing", {"key": "value"}
        ) == {"key": "value"}

    @pytest.mark.integration
    def test_get_value_case_sensitivity(self):
        """Test that configuration keys are case-sensitive."""
        config = {
            "client": {
                "User": "testuser",
                "user": "lowercase_user",
                "PASSWORD": "uppercase_pass",
                "password": "lowercase_pass",
            }
        }

        # Verify case sensitivity
        assert get_mysql_config_value(config, "client", "User") == "testuser"
        assert get_mysql_config_value(config, "client", "user") == "lowercase_user"
        assert get_mysql_config_value(config, "client", "PASSWORD") == "uppercase_pass"
        assert get_mysql_config_value(config, "client", "password") == "lowercase_pass"

        # Verify non-existent case variations
        assert get_mysql_config_value(config, "client", "USER") is None
        assert get_mysql_config_value(config, "client", "Password") is None

    @pytest.mark.integration
    def test_get_value_with_none_values(self):
        """Test getting configuration values that are None."""
        config = {"client": {"user": None, "password": "testpass"}}

        # None values should be returned as-is
        assert get_mysql_config_value(config, "client", "user") is None
        assert get_mysql_config_value(config, "client", "password") == "testpass"

        # Default should not override None values
        assert get_mysql_config_value(config, "client", "user", "default") is None

    @pytest.mark.integration
    def test_get_value_with_empty_string_values(self):
        """Test getting configuration values that are empty strings."""
        config = {"client": {"user": "", "password": "testpass"}}

        # Empty strings should be returned as-is
        assert get_mysql_config_value(config, "client", "user") == ""
        assert get_mysql_config_value(config, "client", "password") == "testpass"

        # Default should not override empty strings
        assert get_mysql_config_value(config, "client", "user", "default") == ""


class TestDatabaseConfigIntegration:
    """Test cases for integrated database configuration functionality."""

    @pytest.mark.integration
    def test_parse_and_retrieve_workflow(self):
        """Test the complete parse and retrieve workflow."""
        config_content = """
[client]
user = production_user
password = secure_password
host = db.example.com
port = 3306

[mysqld]
port = 3307
bind-address = 0.0.0.0
max_connections = 100
"""

        with patch("builtins.open", mock_open(read_data=config_content)):
            # Parse the configuration
            config = parse_mysql_config(Path("/etc/mysql/my.cnf"))

            # Retrieve various values
            db_user = get_mysql_config_value(config, "client", "user")
            db_password = get_mysql_config_value(config, "client", "password")
            db_host = get_mysql_config_value(config, "client", "host")
            db_port = get_mysql_config_value(config, "client", "port")

            server_port = get_mysql_config_value(config, "mysqld", "port")
            bind_address = get_mysql_config_value(config, "mysqld", "bind-address")
            max_connections = get_mysql_config_value(
                config, "mysqld", "max_connections"
            )

            # Verify all values
            assert db_user == "production_user"
            assert db_password == "secure_password"
            assert db_host == "db.example.com"
            assert db_port == "3306"
            assert server_port == "3307"
            assert bind_address == "0.0.0.0"
            assert max_connections == "100"

    @pytest.mark.integration
    def test_configuration_with_defaults_workflow(self):
        """Test configuration parsing with default value fallbacks."""
        config_content = """
[client]
user = testuser
# password is missing
host = localhost
# port is missing
"""

        with patch("builtins.open", mock_open(read_data=config_content)):
            config = parse_mysql_config(Path("/test/partial.cnf"))

            # Get values with defaults
            user = get_mysql_config_value(config, "client", "user", "default_user")
            password = get_mysql_config_value(
                config, "client", "password", "default_password"
            )
            host = get_mysql_config_value(config, "client", "host", "localhost")
            port = get_mysql_config_value(config, "client", "port", "3306")

            # Verify values and defaults
            assert user == "testuser"  # Existing value
            assert password == "default_password"  # Default used
            assert host == "localhost"  # Existing value
            assert port == "3306"  # Default used

    @pytest.mark.integration
    def test_error_handling_workflow(self):
        """Test error handling in the complete workflow."""
        # Test with non-existent file
        with patch("builtins.open", side_effect=FileNotFoundError()):
            config = parse_mysql_config(Path("/nonexistent/my.cnf"))

            # Should handle gracefully with defaults
            user = get_mysql_config_value(config, "client", "user", "fallback_user")
            password = get_mysql_config_value(
                config, "client", "password", "fallback_password"
            )

            assert user == "fallback_user"
            assert password == "fallback_password"
