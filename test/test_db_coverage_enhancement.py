"""
Tests specifically designed to enhance coverage for the db module,
targeting remaining uncovered code paths.
"""

from unittest.mock import MagicMock, patch

import mariadb
import pytest

from config import ModuliConfig
from db import MariaDBConnector


class TestDBCoverageEnhancement:
    """Tests to enhance coverage for the db module."""

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
        # Add moduli_home attribute
        from pathlib import Path
        config.moduli_home = Path("/tmp")
        return config

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    @patch("db.is_valid_identifier_sql")
    def test_write_moduli_file_invalid_identifiers(
        self, mock_is_valid, mock_pool, mock_parse_config, valid_mock_config
    ):
        """Test write_moduli_file with invalid identifiers."""
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

        # First call for db_name validation, second for table_name, third for view_name
        mock_is_valid.side_effect = [True, False, True]

        connector = MariaDBConnector(valid_mock_config)
        # Ensure connector has the required attributes to avoid attribute errors
        connector.moduli_file = "test_moduli.txt"
        connector.moduli_home = valid_mock_config.moduli_home
        # Import and set pathlib.Path to access the home directory
        from pathlib import Path
        connector.moduli_home = Path("/tmp")

        with pytest.raises(RuntimeError, match="Invalid database, table, or view name:"):
            connector.write_moduli_file()

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    @patch("db.is_valid_identifier_sql")
    @patch("builtins.open", new_callable=MagicMock)
    def test_write_moduli_file_io_error(
        self, mock_open, mock_is_valid, mock_pool, mock_parse_config, valid_mock_config
    ):
        """Test write_moduli_file with IO error."""
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

        # Make sure identifier validation passes
        mock_is_valid.return_value = True

        # Simulate file open error
        mock_open.side_effect = IOError("Permission denied")

        # Mock execute_select to return some data
        mock_execute_select = MagicMock()
        mock_execute_select.return_value = [
            {"timestamp": 123, "size": 4096, "modulus": "test"}
        ]

        connector = MariaDBConnector(valid_mock_config)
        connector.execute_select = mock_execute_select

        with pytest.raises(RuntimeError, match="Moduli file writing failed"):
            connector.write_moduli_file()

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    @patch("db.MariaDBConnector.execute_select")
    def test_write_moduli_file_database_error(
        self, mock_execute_select, mock_pool, mock_parse_config, valid_mock_config
    ):
        """Test write_moduli_file with database error."""
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

        # Simulate database query error
        mock_execute_select.side_effect = RuntimeError("Database query failed")

        connector = MariaDBConnector(valid_mock_config)

        with pytest.raises(RuntimeError, match="Moduli file writing failed"):
            connector.write_moduli_file()

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    def test_verify_schema_no_db_name(
        self, mock_pool, mock_parse_config, valid_mock_config
    ):
        """Test verify_schema without db_name."""
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

        # Remove db_name to trigger that code path
        delattr(connector, "db_name")

        result = connector.verify_schema()

        assert result["overall_status"] == "FAILED"
        assert "Database name not configured" in result["errors"]

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    @patch("db.MariaDBConnector.execute_select")
    def test_verify_schema_missing_database(
        self, mock_execute_select, mock_pool, mock_parse_config, valid_mock_config
    ):
        """Test verify_schema with missing database."""
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

        # Return empty result for database existence check
        mock_execute_select.return_value = []

        connector = MariaDBConnector(valid_mock_config)

        result = connector.verify_schema()

        assert result["overall_status"] == "FAILED"
        assert not result["database_exists"]
        assert (
            f"Database `{valid_mock_config.db_name}` does not exist" in result["errors"]
        )

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    @patch("db.MariaDBConnector.execute_select")
    def test_verify_schema_exception(
        self, mock_execute_select, mock_pool, mock_parse_config, valid_mock_config
    ):
        """Test verify_schema with exception."""
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

        # Simulate database query error
        mock_execute_select.side_effect = Exception("Unexpected error")

        connector = MariaDBConnector(valid_mock_config)

        result = connector.verify_schema()

        assert result["overall_status"] == "ERROR"
        assert (
            "Schema verification failed with exception: Unexpected error"
            in result["errors"]
        )

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    @patch("db.MariaDBConnector.execute_select")
    def test_verify_schema_partial_validation(
        self, mock_execute_select, mock_pool, mock_parse_config, valid_mock_config
    ):
        """Test verify_schema with partial validation success."""
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

        # Define mock responses for different queries in verify_schema
        def mock_execute_select_side_effect(query, params=None):
            # DB exists
            if "INFORMATION_SCHEMA.SCHEMATA" in query:
                return [{"SCHEMA_NAME": "valid_db"}]
            # Only some tables exist
            elif "INFORMATION_SCHEMA.TABLES" in query:
                return [
                    {"TABLE_NAME": "mod_fl_consts", "TABLE_TYPE": "BASE TABLE"},
                    {"TABLE_NAME": "moduli", "TABLE_TYPE": "BASE TABLE"},
                ]
            # View exists
            elif "INFORMATION_SCHEMA.VIEWS" in query:
                return [{"TABLE_NAME": "moduli_view"}]
            # Only some indexes exist
            elif "INFORMATION_SCHEMA.STATISTICS" in query:
                return [
                    {"INDEX_NAME": "idx_size", "TABLE_NAME": "moduli"},
                    {"INDEX_NAME": "idx_timestamp", "TABLE_NAME": "moduli"},
                ]
            # No foreign keys
            elif "INFORMATION_SCHEMA.KEY_COLUMN_USAGE" in query:
                return []
            # Config data exists
            elif "COUNT(*)" in query:
                return [{"count": 5}]
            return []

        mock_execute_select.side_effect = mock_execute_select_side_effect

        connector = MariaDBConnector(valid_mock_config)

        result = connector.verify_schema()

        assert result["overall_status"] == "FAILED"
        assert result["database_exists"]
        assert result["tables"]["mod_fl_consts"]
        assert result["tables"]["moduli"]
        assert not result["tables"]["moduli_archive"]
        assert result["views"]["moduli_view"]
        assert result["indexes"]["idx_size"]
        assert result["indexes"]["idx_timestamp"]
        assert not result["indexes"]["idx_size_archive"]
        assert not result["indexes"]["idx_timestamp_archive"]
        assert not result["foreign_keys"]["moduli -> mod_fl_consts.config_id"]
        assert result["configuration_data"]

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    @patch("db.is_valid_identifier_sql")
    @patch("db.MariaDBConnector.execute_select")
    def test_delete_records_invalid_table_name(
        self,
        mock_execute_select,
        mock_is_valid,
        mock_pool,
        mock_parse_config,
        valid_mock_config,
    ):
        """Test delete_records with invalid table name."""
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
        mock_is_valid.return_value = False  # Invalid table name

        connector = MariaDBConnector(valid_mock_config)

        with pytest.raises(RuntimeError, match="Invalid table name"):
            connector.delete_records("invalid-table")

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    def test_transaction_context_manager_with_provided_connection(
        self, mock_pool, mock_parse_config, valid_mock_config
    ):
        """Test transaction context manager with provided connection."""
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

        # Create a mock connection
        mock_connection = MagicMock()

        # Test successful transaction
        with connector.transaction(mock_connection) as conn:
            assert conn is mock_connection

        # Verify commit was called
        mock_connection.commit.assert_called_once()

        # Reset for next test
        mock_connection.reset_mock()

        # Test transaction with error
        with pytest.raises(RuntimeError, match="Test error"):
            with connector.transaction(mock_connection):
                raise RuntimeError("Test error")

        # Verify rollback was called
        mock_connection.rollback.assert_called_once()

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    def test_execute_update_with_create_user_error(
        self, mock_pool, mock_parse_config, valid_mock_config
    ):
        """Test execute_update with CREATE USER privilege error."""
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
        # Simulate error message containing "create user privilege"
        mock_cursor.execute.side_effect = mariadb.Error(
            "ERROR 1227 (42000): Access denied; you need (at least one of) the CREATE USER privilege(s) for this operation"
        )
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(valid_mock_config)

        with pytest.raises(RuntimeError, match="Insufficient database privileges"):
            connector.execute_update(
                "CREATE USER 'test'@'localhost' IDENTIFIED BY 'password'"
            )

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    def test_execute_update_with_access_denied_error(
        self, mock_pool, mock_parse_config, valid_mock_config
    ):
        """Test execute_update with Access Denied error."""
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
        # Simulate error message containing "access denied"
        mock_cursor.execute.side_effect = mariadb.Error(
            "ERROR 1045 (28000): Access denied for user 'test'@'localhost'"
        )
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(valid_mock_config)

        with pytest.raises(RuntimeError, match="Database access denied"):
            connector.execute_update("SELECT * FROM mysql.user")

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    @patch("db.MariaDBConnector._add_without_transaction")
    def test_export_screened_moduli_duplicate_error(
        self, mock_add, mock_pool, mock_parse_config, valid_mock_config
    ):
        """Test export_screened_moduli with duplicate error."""
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

        # Simulate a duplicate key error
        mock_add.side_effect = mariadb.Error(
            "Duplicate entry 'value' for key 'PRIMARY'"
        )

        connector = MariaDBConnector(valid_mock_config)

        screened_moduli = {
            "4096": [
                {
                    "timestamp": 20231201000000,
                    "key-size": 4096,
                    "modulus": "test_modulus",
                }
            ]
        }

        # Should continue past the duplicate error and return success
        result = connector.export_screened_moduli(screened_moduli)
        assert result == 0

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    def test_sql_with_params(self, mock_pool, mock_parse_config, valid_mock_config):
        """Test sql method with parameters."""
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
        mock_cursor.fetchall.return_value = [{"id": 1, "name": "test"}]
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(valid_mock_config)

        # Test with parameters and fetch=True
        result = connector.sql("SELECT * FROM test WHERE id = %s", (1,), fetch=True)

        # Verify execute was called with parameters
        mock_cursor.execute.assert_called_with("SELECT * FROM test WHERE id = %s", (1,))
        # Verify fetchall was called
        mock_cursor.fetchall.assert_called_once()
        # Verify the result
        assert result == [{"id": 1, "name": "test"}]

        # Reset mocks
        mock_cursor.reset_mock()
        mock_cursor.fetchall.return_value = []

        # Test with parameters and fetch=False
        result = connector.sql(
            "UPDATE test SET name = %s WHERE id = %s", ("new_name", 1), fetch=False
        )

        # Verify execute was called with parameters
        mock_cursor.execute.assert_called_with(
            "UPDATE test SET name = %s WHERE id = %s", ("new_name", 1)
        )
        # Verify fetchall was not called
        mock_cursor.fetchall.assert_not_called()
        # Verify the result is None
        assert result is None

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    def test_stats_with_no_results(
        self, mock_pool, mock_parse_config, valid_mock_config
    ):
        """Test stats method with no results."""
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

        # Mock execute_select to return empty results
        with patch.object(connector, "execute_select", return_value=[]):
            result = connector.stats()

            # Should return an empty dictionary
            assert result == {}

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    def test_stats_with_single_result(
        self, mock_pool, mock_parse_config, valid_mock_config
    ):
        """Test stats method with a single result."""
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
        connector.records_per_keylength = 10

        # Mock execute_select to return a single size result
        with patch.object(
            connector, "execute_select", return_value=[{"size": 4096, "count": 20}]
        ):
            result = connector.stats()

            # Should have the size and available files count
            assert result["4096"] == 20
            assert (
                result["available moduli files"] == 2
            )  # 20 / records_per_keylength=10

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    def test_init_with_test_environment(self, mock_pool, mock_parse_config):
        """Test MariaDBConnector initialization in test environment."""
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

        # Create a mock config with mock attributes to indicate test environment
        mock_config = MagicMock()
        mock_config.__class__ = MagicMock()
        mock_config.__class__.__str__.return_value = "MockConfig"
        mock_config.mariadb_cnf = "/path/to/test.cnf"
        mock_config.db_name = "test_db"
        mock_config.table_name = "test_table"
        mock_config.view_name = "test_view"
        mock_config.get_logger.return_value = MagicMock()

        # Mock verify_schema to raise a RuntimeError
        with patch(
            "db.MariaDBConnector.verify_schema",
            side_effect=RuntimeError("Schema verification failed"),
        ):
            # Should not raise an error due to test environment detection
            connector = MariaDBConnector(mock_config)
            assert hasattr(connector, "pool")

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    def test_init_with_nameError_in_verify_schema(self, mock_pool, mock_parse_config):
        """Test MariaDBConnector initialization with NameError in verify_schema."""
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

        # Create a mock config with mock attributes
        mock_config = MagicMock()
        mock_config.__class__ = MagicMock()
        mock_config.__class__.__str__.return_value = "MockConfig"
        mock_config.mariadb_cnf = "/path/to/test.cnf"
        mock_config.db_name = "test_db"
        mock_config.table_name = "test_table"
        # Intentionally don't set view_name to trigger NameError
        mock_config.get_logger.return_value = MagicMock()

        # Mock verify_schema to raise a NameError
        with patch(
            "db.MariaDBConnector.verify_schema",
            side_effect=NameError("view_name not defined"),
        ):
            # Should not raise an error as we handle NameError in __init__
            connector = MariaDBConnector(mock_config)
            assert hasattr(connector, "pool")

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    def test_get_connection_error(
        self, mock_pool, mock_parse_config, valid_mock_config
    ):
        """Test get_connection with error."""
        mock_parse_config.return_value = {
            "client": {
                "user": "test",
                "password": "test",
                "host": "localhost",
                "port": "3306",
                "database": "testdb",
            }
        }

        # Configure the mock pool to raise an error when get_connection is called
        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.side_effect = mariadb.Error(
            "Connection error"
        )
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(valid_mock_config)

        # Should raise the error from get_connection
        with pytest.raises(mariadb.Error, match="Connection error"):
            with connector.get_connection():
                pass  # This should not execute

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    def test_file_writer_error(self, mock_pool, mock_parse_config, valid_mock_config):
        """Test file_writer with IOError."""
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

        # Create a mock Path object that raises IOError when opened
        mock_path = MagicMock()
        mock_path.open.side_effect = IOError("File IO error")

        # Should raise IOError from file_writer
        with pytest.raises(IOError, match="File IO error"):
            with connector.file_writer(mock_path):
                pass  # This should not execute

    @patch("db.parse_mysql_config")
    @patch("db.ConnectionPool")
    def test_execute_select_error(
        self, mock_pool, mock_parse_config, valid_mock_config
    ):
        """Test execute_select with error."""
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
        # Simulate a database error during query execution
        mock_cursor.execute.side_effect = mariadb.Error("Query execution error")
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(valid_mock_config)

        # Should raise RuntimeError from execute_select
        with pytest.raises(RuntimeError, match="Database query failed"):
            connector.execute_select("SELECT * FROM example")
