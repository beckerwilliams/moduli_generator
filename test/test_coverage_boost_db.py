"""
Tests specifically designed to boost coverage for uncovered code paths in db module.
"""
from unittest.mock import MagicMock, patch

import mariadb
import pytest

from config import ModuliConfig
from db import MariaDBConnector


class TestDatabaseCoverageBoost:
    """Tests to cover uncovered code paths in database operations."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock config with invalid identifiers."""
        config = MagicMock(spec=ModuliConfig)
        config.mariadb_cnf = "/path/to/test.cnf"
        config.db_name = "invalid-db-name"  # Invalid SQL identifier
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

    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    @patch('db.is_valid_identifier_sql')
    def test_add_invalid_database_name(self, mock_is_valid, mock_pool, mock_parse_config, mock_config):
        """Test add method with invalid database name."""
        mock_parse_config.return_value = \
            {"client": {"user": "test", "password": "test", "host": "localhost", "port": "3306", "database": "testdb"}}
        mock_pool.return_value = MagicMock()
        mock_is_valid.return_value = False  # Simulate invalid identifier

        connector = MariaDBConnector(mock_config)
        result = connector.add(20231201000000, 4096, "test_modulus")

        assert result == 0
        mock_is_valid.assert_called()

    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    @patch('db.is_valid_identifier_sql')
    def test_add_batch_invalid_database_name(self, mock_is_valid, mock_pool, mock_parse_config, mock_config):
        """Test add_batch method with an invalid database name."""
        mock_parse_config.return_value = \
            {"client": {"user": "test", "password": "test", "host": "localhost", "port": "3306", "database": "testdb"}}
        mock_pool.return_value = MagicMock()
        mock_is_valid.return_value = False  # Simulate invalid identifier

        connector = MariaDBConnector(mock_config)
        records = [(20231201000000, 4096, "test_modulus")]
        result = connector.add_batch(records)

        assert result is False
        mock_is_valid.assert_called()

    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_add_database_error(self, mock_pool, mock_parse_config, valid_mock_config):
        """Test add method with database error."""
        mock_parse_config.return_value = \
            {"client": {"user": "test", "password": "test", "host": "localhost", "port": "3306", "database": "testdb"}}
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = mariadb.Error("Database error")
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(valid_mock_config)
        result = connector.add(20231201000000, 4096, "test_modulus")

        assert result == 0

    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_add_batch_runtime_error(self, mock_pool, mock_parse_config, valid_mock_config):
        """Test add_batch method with a runtime error."""
        mock_parse_config.return_value = \
            {"client": {"user": "test", "password": "test", "host": "localhost", "port": "3306", "database": "testdb"}}
        mock_pool.return_value = MagicMock()

        connector = MariaDBConnector(valid_mock_config)
        # Mock execute_batch to raise RuntimeError
        with patch.object(connector, 'execute_batch', side_effect=RuntimeError("Batch error")):
            records = [(20231201000000, 4096, "test_modulus")]
            result = connector.add_batch(records)

            assert result is False

    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    @patch('db.is_valid_identifier_sql')
    def test_stats_invalid_database_name(self, mock_is_valid, mock_pool, mock_parse_config, mock_config):
        """Test stats method with an invalid database name."""
        mock_parse_config.return_value = \
            {"client": {"user": "test", "password": "test", "host": "localhost", "port": "3306", "database": "testdb"}}
        mock_pool.return_value = MagicMock()
        mock_is_valid.return_value = False  # Simulate invalid identifier

        connector = MariaDBConnector(mock_config)
        connector.key_lengths = [4096]

        with pytest.raises(RuntimeError, match="Invalid database name"):
            connector.stats()

        mock_is_valid.assert_called()

    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_stats_database_error(self, mock_pool, mock_parse_config, valid_mock_config):
        """Test stats method with a database error."""
        mock_parse_config.return_value = \
            {"client": {"user": "test", "password": "test", "host": "localhost", "port": "3306", "database": "testdb"}}
        mock_pool.return_value = MagicMock()

        connector = MariaDBConnector(valid_mock_config)
        connector.key_lengths = [4096]
        connector.records_per_keylength = 10

        # Mock execute_select to raise mariadb.Error
        with patch.object(connector, 'execute_select',
                          side_effect=RuntimeError("Database query failed: Database error")):
            with pytest.raises(RuntimeError, match="Database query failed"):
                connector.stats()

    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_delete_records_error_handling(self, mock_pool, mock_parse_config, valid_mock_config):
        """Test delete_records method error handling."""
        mock_parse_config.return_value = \
            {"client": {"user": "test", "password": "test", "host": "localhost", "port": "3306", "database": "testdb"}}
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = mariadb.Error("Delete error")
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(valid_mock_config)

        with pytest.raises(RuntimeError, match="Error deleting from table"):
            connector.delete_records("test_table", "id = 1")

    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_export_screened_moduli_error_handling(self, mock_pool, mock_parse_config, valid_mock_config):
        """Test export_screened_moduli method error handling."""
        mock_parse_config.return_value = \
            {"client": {"user": "test", "password": "test", "host": "localhost", "port": "3306", "database": "testdb"}}
        mock_connection = MagicMock()
        mock_connection_pool = MagicMock()
        mock_connection_pool.get_connection.return_value = mock_connection
        mock_pool.return_value = mock_connection_pool

        connector = MariaDBConnector(valid_mock_config)

        # Mock _add_without_transaction to raise an error
        with patch.object(connector, '_add_without_transaction', side_effect=Exception("Add error")):
            screened_moduli = {
                "4096": [
                    {"timestamp": 20231201000000, "key-size": 4096, "modulus": "test_modulus"}
                ]
            }
            result = connector.export_screened_moduli(screened_moduli)
            assert result == 1  # Error return code
