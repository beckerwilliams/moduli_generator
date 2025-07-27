"""
Integration tests for the database functionality.

This module tests the MariaDBConnector class and related database operations,
including connection management, SQL execution, and moduli storage operations.
"""

from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import mariadb
import pytest

from db import MariaDBConnector, get_mysql_config_value, parse_mysql_config


class TestMariaDBConfigParsing:
    """Test cases for MariaDB configuration parsing functions."""

    @pytest.mark.integration
    @patch('builtins.open', new_callable=mock_open, read_data="""
[client]
user = testuser
password = testpass
host = localhost
port = 3306

[mysqld]
port = 3307
bind-address = 127.0.0.1
key_buffer_size = 16M
""")
    def test_parse_mysql_config_success(self, mock_file):
        """Test successful parsing of MySQL configuration file."""
        config_path = Path("/test/my.cnf")

        result = parse_mysql_config(config_path)

        assert isinstance(result, dict)
        assert "client" in result
        assert "mysqld" in result
        assert result["client"]["user"] == "testuser"
        assert result["client"]["password"] == "testpass"
        assert result["mysqld"]["port"] == "3307"

    @pytest.mark.integration
    @patch('builtins.open', side_effect=FileNotFoundError("Config file not found"))
    def test_parse_mysql_config_file_not_found(self, mock_file):
        """Test parsing MySQL config when file doesn't exist."""
        config_path = Path("/nonexistent/my.cnf")

        result = parse_mysql_config(config_path)

        assert result == {}

    @pytest.mark.integration
    @patch('builtins.open', new_callable=mock_open, read_data="[invalid config\nmalformed")
    @patch('configparser.ConfigParser.read')
    def test_parse_mysql_config_parser_error(self, mock_read, mock_file):
        """Test parsing MySQL config with parser error."""
        mock_read.side_effect = Exception("Parser error")
        config_path = Path("/test/my.cnf")

        with pytest.raises(ValueError, match="Error parsing configuration file"):
            parse_mysql_config(config_path)

    @pytest.mark.integration
    def test_get_mysql_config_value_existing_key(self):
        """Test getting existing configuration value."""
        config = {
            "client": {"user": "testuser", "password": "testpass"},
            "mysqld": {"port": "3307"}
        }

        result = get_mysql_config_value(config, "client", "user")
        assert result == "testuser"

        result = get_mysql_config_value(config, "mysqld", "port")
        assert result == "3307"

    @pytest.mark.integration
    def test_get_mysql_config_value_nonexistent_key(self):
        """Test getting non-existent configuration key."""
        config = {"client": {"user": "testuser"}}

        result = get_mysql_config_value(config, "client", "nonexistent")
        assert result is None

        result = get_mysql_config_value(config, "client", "nonexistent", "default_value")
        assert result == "default_value"

    @pytest.mark.integration
    def test_get_mysql_config_value_nonexistent_section(self):
        """Test getting value from non-existent section."""
        config = {"client": {"user": "testuser"}}

        result = get_mysql_config_value(config, "nonexistent", "key")
        assert result is None

        result = get_mysql_config_value(config, "nonexistent", "key", "default")
        assert result == "default"

    @pytest.mark.integration
    def test_get_mysql_config_value_empty_config(self):
        """Test getting value from empty configuration."""
        config = {}

        result = get_mysql_config_value(config, "client", "user")
        assert result is None

        result = get_mysql_config_value(config, "client", "user", "default")
        assert result == "default"


class TestMariaDBConnectorInitialization:
    """Test cases for MariaDBConnector initialization."""

    @pytest.mark.integration
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_mariadb_connector_init_default_config(self, mock_pool, mock_parse_config, mock_config):
        """Test MariaDBConnector initialization with default configuration."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}
        }
        mock_pool.return_value = MagicMock()

        connector = MariaDBConnector(mock_config)

        assert hasattr(connector, 'mariadb_cnf')
        assert hasattr(connector, 'pool')
        mock_parse_config.assert_called_once()
        mock_pool.assert_called_once()

    @pytest.mark.integration
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_mariadb_connector_init_custom_config(self, mock_pool, mock_parse_config, mock_config):
        """Test MariaDBConnector initialization with custom configuration."""
        mock_parse_config.return_value = {
            "client": {"user": "customuser", "password": "custompass", "host": "customhost", "port": "3307",
                       "database": "customdb"}
        }
        mock_pool.return_value = MagicMock()

        connector = MariaDBConnector(mock_config)

        assert hasattr(connector, 'mariadb_cnf')
        assert hasattr(connector, 'pool')
        mock_parse_config.assert_called_once_with(mock_config.mariadb_cnf)

    @pytest.mark.integration
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_mariadb_connector_init_connection_error(self, mock_pool, mock_parse_config, mock_config):
        """Test MariaDBConnector initialization with connection error."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}}
        mock_pool.side_effect = mariadb.Error("Connection failed")

        with pytest.raises(RuntimeError, match="Connection pool creation failed: Connection failed"):
            MariaDBConnector(mock_config)


class TestMariaDBConnectorContextManager:
    """Test cases for MariaDBConnector context manager functionality."""

    @pytest.mark.integration
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_context_manager_enter_exit(self, mock_pool, mock_parse_config, mock_config):
        """Test context manager enter and exit methods."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}}
        mock_connection_pool = MagicMock()
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(mock_config)

        # Test __enter__
        result = connector.__enter__()
        assert result == connector

        # Test __exit__ with no exception
        connector.__exit__(None, None, None)

        # Test __exit__ with exception
        connector.__exit__(Exception, Exception("test"), None)

    @pytest.mark.integration
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_context_manager_with_statement(self, mock_pool, mock_parse_config, mock_config):
        """Test using MariaDBConnector with 'with' statement."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}}
        mock_pool.return_value = MagicMock()

        with MariaDBConnector(mock_config) as connector:
            assert isinstance(connector, MariaDBConnector)
            assert hasattr(connector, 'mariadb_cnf')
            assert hasattr(connector, 'pool')


class TestMariaDBConnectorConnectionManagement:
    """Test cases for database connection management."""

    @pytest.mark.integration
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_get_connection_success(self, mock_pool, mock_parse_config, mock_config):
        """Test successful database connection retrieval."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}}
        mock_connection = MagicMock()
        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(mock_config)

        # Test that get_connection returns a context manager
        with connector.get_connection() as connection:
            assert connection == mock_connection
        mock_connection_pool.get_connection.assert_called_once()
        mock_connection.close.assert_called_once()

    @pytest.mark.integration
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_get_connection_error(self, mock_pool, mock_parse_config, mock_config):
        """Test database connection retrieval error."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}}
        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.side_effect = mariadb.Error("Connection failed")
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(mock_config)

        with pytest.raises(mariadb.Error, match="Connection failed"):
            with connector.get_connection():
                pass

    @pytest.mark.integration
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_transaction_context_manager(self, mock_pool, mock_parse_config, mock_config):
        """Test transaction context manager."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}}
        mock_connection = MagicMock()
        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(mock_config)

        with connector.transaction() as conn:
            assert conn == mock_connection

        mock_connection.commit.assert_called_once()
        mock_connection.close.assert_called_once()

    @pytest.mark.integration
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_transaction_rollback_on_exception(self, mock_pool, mock_parse_config, mock_config):
        """Test transaction rollback on exception."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}}
        mock_connection = MagicMock()
        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(mock_config)

        with pytest.raises(ValueError):
            with connector.transaction() as conn:
                raise ValueError("Test error")

        mock_connection.rollback.assert_called_once()
        mock_connection.close.assert_called_once()


class TestMariaDBConnectorSQLExecution:
    """Test cases for SQL execution methods."""

    @pytest.mark.integration
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_sql_select_query(self, mock_pool, mock_parse_config, mock_config):
        """Test SQL SELECT query execution."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}}
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("result1",), ("result2",)]
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(mock_config)
        result = connector.sql("SELECT * FROM test_table", fetch=True)

        assert result == [("result1",), ("result2",)]
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test_table")
        mock_cursor.fetchall.assert_called_once()

    @pytest.mark.integration
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_sql_insert_query(self, mock_pool, mock_parse_config, mock_config):
        """Test SQL INSERT query execution."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}}
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(mock_config)
        result = connector.sql("INSERT INTO test_table VALUES (?)", ("value1",), fetch=False)

        assert result is None
        mock_cursor.execute.assert_called_once_with("INSERT INTO test_table VALUES (?)", ("value1",))
        mock_cursor.fetchall.assert_not_called()

    @pytest.mark.integration
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_execute_select_method(self, mock_pool, mock_parse_config, mock_config):
        """Test execute_select method."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}}
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("result1",), ("result2",)]
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(mock_config)
        result = connector.execute_select("SELECT * FROM test_table")

        assert result == [("result1",), ("result2",)]

    @pytest.mark.integration
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_execute_update_method(self, mock_pool, mock_parse_config, mock_config):
        """Test execute_update method."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}}
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(mock_config)
        result = connector.execute_update("UPDATE test_table SET col1 = ?", ("value1",))

        assert result == 1
        mock_cursor.execute.assert_called_once()

    @pytest.mark.integration
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_execute_batch_method(self, mock_pool, mock_parse_config, mock_config):
        """Test execute_batch method."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}}
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(mock_config)
        queries = ["INSERT INTO test_table VALUES (?)", "INSERT INTO test_table VALUES (?)"]
        params_list = [("value1",), ("value2",)]

        connector.execute_batch(queries, params_list)

        assert mock_cursor.execute.call_count == 2


class TestMariaDBConnectorModuliOperations:
    """Test cases for moduli-specific database operations."""

    @pytest.mark.integration
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_add_single_modulus(self, mock_pool, mock_parse_config, mock_config):
        """Test adding a single modulus to the database."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}}
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(mock_config)
        connector.add(20231201000000, 4096, "test_modulus")

        mock_cursor.execute.assert_called()

    @pytest.mark.integration
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_add_batch_moduli(self, mock_pool, mock_parse_config, mock_config):
        """Test adding multiple moduli in batch."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}}
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(mock_config)
        records = [
            (20231201000000, 4096, "test_modulus_1"),
            (20231201000001, 4096, "test_modulus_2")
        ]

        connector.add_batch(records)

        # add_batch uses execute_batch which calls execute() multiple times
        assert mock_cursor.execute.call_count == len(records)

    @pytest.mark.integration
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_delete_records(self, mock_pool, mock_parse_config, mock_config):
        """Test deleting records from database."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}}
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 5
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(mock_config)
        result = connector.delete_records("test_table", "key_size = 4096")

        assert result == 5
        mock_cursor.execute.assert_called()

    @pytest.mark.integration
    @patch('pathlib.Path.open', new_callable=mock_open)
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_file_writer_context_manager(self, mock_pool, mock_parse_config, mock_file, mock_config):
        """Test file writer context manager."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}}
        mock_pool.return_value = MagicMock()

        connector = MariaDBConnector(mock_config)
        output_file = Path("/test/output.txt")

        with connector.file_writer(output_file) as writer:
            assert writer is not None

        mock_file.assert_called_once_with('w')


class TestMariaDBConnectorStatistics:
    """Test cases for database statistics functionality."""

    @pytest.mark.integration
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_stats_method(self, mock_pool, mock_parse_config, mock_config):
        """Test stats method for database statistics."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}}
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        # Mock the execute_select method to return dictionary results
        mock_cursor.fetchall.return_value = [{'size': 4095, 'count': 100}, {'size': 8191, 'count': 50}]
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(mock_config)
        # Mock the key_lengths and records_per_keylength attributes
        connector.key_lengths = [4096, 8192]
        connector.records_per_keylength = 10

        result = connector.stats()

        # stats() returns a dictionary with key sizes and counts
        assert isinstance(result, dict)
        mock_cursor.execute.assert_called()


    @pytest.mark.integration
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_show_stats_method(self, mock_pool, mock_parse_config, mock_config):
        """Test show_stats method."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}}
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        # Mock the execute_select method to return dictionary results
        mock_cursor.fetchall.return_value = [{'size': 4095, 'count': 100}]
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(mock_config)
        # Mock the key_lengths and records_per_keylength attributes
        connector.key_lengths = [4096]
        connector.records_per_keylength = 10

        result = connector.show_stats()

        # show_stats is an alias for stats() and returns a dictionary
        assert isinstance(result, dict)


class TestMariaDBConnectorExportOperations:
    """Test cases for export and file operations."""

    @pytest.mark.integration
    @patch('builtins.open', new_callable=mock_open)
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_export_screened_moduli(self, mock_pool, mock_parse_config, mock_file, mock_config):
        """Test exporting screened moduli to files."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}}
        mock_connection_pool = MagicMock()
        mock_connection = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(mock_config)
        screened_moduli = {
            4096: [
                {"timestamp": 20231201000000, "key-size": 4096, "modulus": "modulus1"},
                {"timestamp": 20231201000001, "key-size": 4096, "modulus": "modulus2"}
            ],
            8192: [
                {"timestamp": 20231201000002, "key-size": 8192, "modulus": "modulus3"}
            ]
        }

        result = connector.export_screened_moduli(screened_moduli)

        # Verify the operation was successful
        assert result == 0

    @pytest.mark.integration
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_write_moduli_file(self, mock_pool, mock_parse_config, mock_config):
        """Test writing moduli file from database."""
        from datetime import datetime
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}}
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        # Return dictionary format to match execute_select behavior
        mock_cursor.fetchall.return_value = [
            {
                'modulus': 'test_modulus_1',
                'size': 4095,  # key_length - 1
                'generator': 2,
                'timestamp': datetime(2023, 12, 1, 0, 0, 0)
            },
            {
                'modulus': 'test_modulus_2',
                'size': 4095,  # key_length - 1
                'generator': 2,
                'timestamp': datetime(2023, 12, 1, 0, 0, 1)
            }
        ]
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        with patch('builtins.open', mock_open()) as mock_file:
            connector = MariaDBConnector(mock_config)
            # Set required attributes for the test
            connector.key_lengths = [4096]
            connector.records_per_keylength = 2
            connector.moduli_file = '/tmp/test_moduli'
            connector.db_name = 'test_db'
            connector.view_name = 'test_view'

            connector.write_moduli_file()

            mock_file.assert_called()
            mock_cursor.execute.assert_called()


class TestMariaDBConnectorErrorHandling:
    """Test cases for database error handling."""

    @pytest.mark.integration
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_sql_execution_error(self, mock_pool, mock_parse_config, mock_config):
        """Test SQL execution error handling."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}}
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = mariadb.Error("SQL execution failed")
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(mock_config)

        with pytest.raises(RuntimeError, match="Database query failed: SQL execution failed"):
            connector.sql("SELECT * FROM nonexistent_table")

    @pytest.mark.integration
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_batch_execution_error(self, mock_pool, mock_parse_config, mock_config):
        """Test batch execution error handling."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}}
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = mariadb.Error("Batch execution failed")
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(mock_config)

        with pytest.raises(RuntimeError, match="Batch query execution failed: Batch execution failed"):
            connector.execute_batch(["INSERT INTO test VALUES (?)"], [("value1",)])

    @pytest.mark.integration
    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_connection_pool_exhaustion(self, mock_pool, mock_parse_config, mock_config):
        """Test handling of connection pool exhaustion."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}}
        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.side_effect = mariadb.Error("Connection pool exhausted")
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(mock_config)

        with pytest.raises(mariadb.Error, match="Connection pool exhausted"):
            with connector.get_connection():
                pass
