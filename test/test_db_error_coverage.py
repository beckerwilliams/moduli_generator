"""
Additional tests to cover remaining uncovered error paths in db module.
These tests target specific missing lines identified in coverage analysis.
"""

import configparser
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import mariadb
import pytest

from config import ModuliConfig
from db import MariaDBConnector, get_mysql_config_value, parse_mysql_config


class TestDBErrorCoverage:
    """Tests to cover remaining uncovered error paths in db module."""

    @pytest.fixture
    def valid_mock_config(self):
        """Create a mock config with valid identifiers."""
        config = MagicMock(spec=ModuliConfig)
        config.mariadb_cnf = "/path/to/test.cnf"
        config.db_name = "valid_db"
        config.table_name = "valid_table"
        config.view_name = "valid_view"
        config.config_id = "test_config"
        config.key_lengths = [4096, 8192]
        config.records_per_keylength = 10
        config.base_dir = "/tmp"
        config.moduli_file_pfx = "moduli"
        config.moduli_file = "moduli.txt"
        config.delete_records_on_moduli_write = False
        config.delete_records_on_read = False
        config.get_logger.return_value = MagicMock()
        return config

    @pytest.mark.unit
    def test_parse_mysql_config_file_like_object(self):
        """Test parse_mysql_config with file-like object - covers line 43."""
        config_content = """
[client]
user = testuser
password = testpass
host = localhost
port = 3306
database = testdb
"""
        # Create a file-like object
        from io import StringIO

        config_file = StringIO(config_content)

        result = parse_mysql_config(config_file)

        assert "client" in result
        assert result["client"]["user"] == "testuser"
        assert result["client"]["password"] == "testpass"

    @pytest.mark.unit
    def test_parse_mysql_config_parsing_error(self):
        """Test parse_mysql_config with invalid config content - covers lines 74, 82-85."""
        # Create invalid config content that will cause parsing error
        invalid_config = """
[client
user = testuser
password = testpass
"""
        from io import StringIO

        config_file = StringIO(invalid_config)

        with pytest.raises(ValueError, match="Error parsing configuration file"):
            parse_mysql_config(config_file)

    @pytest.mark.unit
    def test_parse_mysql_config_duplicate_section_error(self):
        """Test parse_mysql_config with duplicate section error - covers lines 83-84."""
        # Mock configparser to raise DuplicateSectionError
        with patch("configparser.ConfigParser") as mock_parser:
            mock_instance = MagicMock()
            mock_parser.return_value = mock_instance
            mock_instance.read_file.side_effect = configparser.DuplicateSectionError(
                "client"
            )

            from io import StringIO

            config_file = StringIO("[client]\nuser=test")

            with pytest.raises(ValueError, match="Error parsing configuration file"):
                parse_mysql_config(config_file)

    @pytest.mark.unit
    def test_parse_mysql_config_general_exception(self):
        """Test parse_mysql_config with general exception - covers line 85."""
        # Mock configparser to raise a general exception
        with patch("configparser.ConfigParser") as mock_parser:
            mock_instance = MagicMock()
            mock_parser.return_value = mock_instance
            mock_instance.read_file.side_effect = Exception("General parsing error")

            from io import StringIO

            config_file = StringIO("[client]\nuser=test")

            with pytest.raises(ValueError, match="Error parsing configuration file"):
                parse_mysql_config(config_file)

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    def test_mariadb_connector_close_pool_error(
        self, mock_pool, mock_parse_config, valid_mock_config
    ):
        """Test MariaDBConnector __exit__ method with pool error - covers lines 190-191."""
        mock_parse_config.return_value = {
            "client": {
                "user": "test",
                "password": "test",
                "host": "localhost",
                "port": "3306",
                "database": "testdb",
            }
        }
        mock_connection_pool = MagicMock()
        mock_connection_pool.close.side_effect = mariadb.Error("Pool close error")
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(valid_mock_config)

        # This should not raise an exception, just log the error
        connector.__exit__(None, None, None)

        # Verify the error was logged
        valid_mock_config.get_logger.return_value.error.assert_called()

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    def test_transaction_rollback_error(
        self, mock_pool, mock_parse_config, valid_mock_config
    ):
        """Test transaction rollback on error - covers lines 245-247."""
        mock_parse_config.return_value = {
            "client": {
                "user": "test",
                "password": "test",
                "host": "localhost",
                "port": "3306",
                "database": "testdb",
            }
        }
        mock_connection = MagicMock()
        mock_cursor = MagicMock()

        # Make execute raise an error to trigger rollback
        mock_cursor.execute.side_effect = mariadb.Error("Query execution error")
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection.cursor.return_value.__exit__.return_value = None

        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(valid_mock_config)

        # This should trigger the rollback path
        with pytest.raises(RuntimeError):
            connector.execute_batch("INSERT INTO test VALUES (%s)", [(1,)])

        # Verify rollback was called
        mock_connection.rollback.assert_called()

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    def test_file_writer_context_manager(
        self, mock_pool, mock_parse_config, valid_mock_config
    ):
        """Test file_writer context manager - covers line 264."""
        mock_parse_config.return_value = {
            "client": {
                "user": "test",
                "password": "test",
                "host": "localhost",
                "port": "3306",
                "database": "testdb",
            }
        }
        mock_pool.return_value = MagicMock()

        connector = MariaDBConnector(valid_mock_config)

        # Create a temporary file to test the context manager
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file_path = Path(temp_file.name)

        try:
            # Test the file_writer context manager
            with connector.file_writer(temp_file_path) as file_handle:
                file_handle.write("test content")

            # Verify content was written
            with open(temp_file_path, "r") as f:
                content = f.read()
                assert content == "test content"
        finally:
            # Clean up
            os.unlink(temp_file_path)

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    def test_execute_update_query_error(
        self, mock_pool, mock_parse_config, valid_mock_config
    ):
        """Test execute_update_query error handling - covers lines 414, 419-421."""
        mock_parse_config.return_value = {
            "client": {
                "user": "test",
                "password": "test",
                "host": "localhost",
                "port": "3306",
                "database": "testdb",
            }
        }
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = mariadb.Error("Update query error")
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(valid_mock_config)

        with pytest.raises(RuntimeError, match="Update query execution failed"):
            connector.execute_update(
                "UPDATE test SET value = %s WHERE id = %s", ("new_value", 1)
            )

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    def test_execute_batch_query_error(
        self, mock_pool, mock_parse_config, valid_mock_config
    ):
        """Test execute_batch query error handling - covers line 451."""
        mock_parse_config.return_value = {
            "client": {
                "user": "test",
                "password": "test",
                "host": "localhost",
                "port": "3306",
                "database": "testdb",
            }
        }
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = mariadb.Error("Batch query error")
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(valid_mock_config)

        with pytest.raises(RuntimeError):
            connector.execute_batch("INSERT INTO test VALUES (%s)", [(1,), (2,), (3,)])

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    @patch("db.is_valid_identifier_sql")
    def test_invalid_database_table_name_validation(
        self, mock_is_valid, mock_pool, mock_parse_config, valid_mock_config
    ):
        """Test database/table name validation error - covers lines 476-477."""
        mock_parse_config.return_value = {
            "client": {
                "user": "test",
                "password": "test",
                "host": "localhost",
                "port": "3306",
                "database": "testdb",
            }
        }
        mock_pool.return_value = MagicMock()
        mock_is_valid.return_value = False  # Simulate invalid identifier

        connector = MariaDBConnector(valid_mock_config)

        # This should trigger the validation error path
        result = connector.add(20231201000000, 4096, "test_modulus")

        assert result == 0
        # Verify the error was logged
        valid_mock_config.get_logger.return_value.error.assert_called_with(
            "Invalid database or table name"
        )

    @pytest.mark.unit
    def test_get_mysql_config_value_missing_section(self):
        """Test get_mysql_config_value with missing section."""
        config_dict = {"client": {"user": "testuser", "password": "testpass"}}

        result = get_mysql_config_value(config_dict, "missing_section", "user")
        assert result is None

    @pytest.mark.unit
    def test_get_mysql_config_value_missing_key(self):
        """Test get_mysql_config_value with missing key."""
        config_dict = {"client": {"user": "testuser", "password": "testpass"}}

        result = get_mysql_config_value(config_dict, "client", "missing_key")
        assert result is None

    @pytest.mark.unit
    def test_get_mysql_config_value_success(self):
        """Test get_mysql_config_value with valid section and key."""
        config_dict = {"client": {"user": "testuser", "password": "testpass"}}

        result = get_mysql_config_value(config_dict, "client", "user")
        assert result == "testuser"
