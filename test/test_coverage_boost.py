"""
Targeted tests to boost coverage for specific uncovered lines.

This module contains simple, focused tests designed to execute specific
code paths that are currently uncovered, helping achieve the 95% coverage target.
"""

import pytest
import tempfile
import configparser
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
from io import StringIO

from db import parse_mysql_config, get_mysql_config_value, MariaDBConnector
from config import ModuliConfig


class TestParseMyqlConfigCoverage:
    """Tests to cover missing lines in parse_mysql_config function."""

    def test_parse_mysql_config_none_input(self):
        """Test parse_mysql_config with None input - covers line 31."""
        result = parse_mysql_config(None)
        assert result == {}

    def test_parse_mysql_config_empty_string(self):
        """Test parse_mysql_config with empty string - covers line 31."""
        result = parse_mysql_config("")
        assert result == {}

    def test_parse_mysql_config_empty_file(self):
        """Test parse_mysql_config with empty file - covers line 55."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            # Create empty file
            pass

        try:
            result = parse_mysql_config(f.name)
            assert result == {}
        finally:
            Path(f.name).unlink()

    def test_parse_mysql_config_duplicate_section_error(self):
        """Test parse_mysql_config with duplicate section error - covers line 74."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.cnf') as f:
            f.write("[client]\nhost=localhost\n")
            f.flush()

            with patch('configparser.ConfigParser.read') as mock_read:
                mock_read.side_effect = configparser.DuplicateSectionError('client')

                try:
                    with pytest.raises(ValueError, match="Error parsing configuration file"):
                        parse_mysql_config(f.name)
                finally:
                    Path(f.name).unlink()

    def test_parse_mysql_config_parsing_error(self):
        """Test parse_mysql_config with parsing error - covers lines 75-76."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.cnf') as f:
            f.write("[client]\nhost=localhost\n")
            f.flush()

            with patch('configparser.ConfigParser.read') as mock_read:
                mock_read.side_effect = configparser.ParsingError(f.name)

                try:
                    with pytest.raises(ValueError, match="Error parsing configuration file"):
                        parse_mysql_config(f.name)
                finally:
                    Path(f.name).unlink()

    def test_parse_mysql_config_general_configparser_error(self):
        """Test parse_mysql_config with general configparser error - covers lines 77-78."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.cnf') as f:
            f.write("[client]\nhost=localhost\n")
            f.flush()

            with patch('configparser.ConfigParser.read') as mock_read:
                mock_read.side_effect = configparser.Error("General config error")

                try:
                    with pytest.raises(ValueError, match="Error parsing configuration file"):
                        parse_mysql_config(f.name)
                finally:
                    Path(f.name).unlink()

    def test_parse_mysql_config_file_not_found_reraise(self):
        """Test parse_mysql_config re-raises FileNotFoundError - covers lines 79-81."""
        with pytest.raises(FileNotFoundError):
            parse_mysql_config("/nonexistent/path/config.cnf")

    def test_parse_mysql_config_already_exists_error(self):
        """Test parse_mysql_config with 'already exists' error - covers lines 83-84."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.cnf') as f:
            f.write("[client]\nhost=localhost\n")
            f.flush()

            with patch('configparser.ConfigParser.read') as mock_read:
                mock_read.side_effect = Exception("Section already exists")

                try:
                    with pytest.raises(ValueError, match="Error parsing configuration file"):
                        parse_mysql_config(f.name)
                finally:
                    Path(f.name).unlink()

    def test_parse_mysql_config_general_exception(self):
        """Test parse_mysql_config with general exception - covers line 85."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.cnf') as f:
            f.write("[client]\nhost=localhost\n")
            f.flush()

            with patch('configparser.ConfigParser.read') as mock_read:
                mock_read.side_effect = Exception("Some other error")

                try:
                    with pytest.raises(ValueError, match="Error parsing configuration file"):
                        parse_mysql_config(f.name)
                finally:
                    Path(f.name).unlink()


class TestGetMysqlConfigValueCoverage:
    """Tests to cover missing lines in get_mysql_config_value function."""

    def test_get_mysql_config_value_none_config(self):
        """Test get_mysql_config_value with None config - covers lines 103-104."""
        with pytest.raises(TypeError, match="config cannot be None"):
            get_mysql_config_value(None, "section", "key")

    def test_get_mysql_config_value_invalid_config_type(self):
        """Test get_mysql_config_value with invalid config type - covers lines 106-107."""
        with pytest.raises(TypeError, match="config must be dict"):
            get_mysql_config_value("not_a_dict", "section", "key")

    def test_get_mysql_config_value_invalid_section_type(self):
        """Test get_mysql_config_value with invalid section type - covers lines 108-109."""
        with pytest.raises(TypeError, match="section must be string"):
            get_mysql_config_value({}, 123, "key")

    def test_get_mysql_config_value_invalid_key_type(self):
        """Test get_mysql_config_value with invalid key type - covers lines 110-111."""
        with pytest.raises(TypeError, match="key must be string"):
            get_mysql_config_value({}, "section", 123)

    def test_get_mysql_config_value_missing_section(self):
        """Test get_mysql_config_value with missing section - covers lines 113-114."""
        config = {"other_section": {"key": "value"}}
        result = get_mysql_config_value(config, "missing_section", "key", "default")
        assert result == "default"

    def test_get_mysql_config_value_missing_key(self):
        """Test get_mysql_config_value with missing key - covers lines 116-117."""
        config = {"section": {"other_key": "value"}}
        result = get_mysql_config_value(config, "section", "missing_key", "default")
        assert result == "default"


class TestMariaDBConnectorCoverage:
    """Tests to cover missing lines in MariaDBConnector class."""

    @patch('db.parse_mysql_config')
    @patch('db.ConnectionPool')
    def test_mariadb_connector_connection_pool_error(self, mock_pool, mock_parse):
        """Test MariaDBConnector with connection pool creation error - covers lines 324-326."""
        mock_parse.return_value = {
            'client': {
                'host': 'localhost',
                'port': '3306',
                'user': 'test_user',
                'password': 'test_password',
                'database': 'test_db'
            }
        }

        from mariadb import Error
        mock_pool.side_effect = Error("Connection failed")

        config = MagicMock()
        config.mariadb_cnf = Path('/test/config.cnf')
        config.get_logger.return_value = MagicMock()

        with pytest.raises(RuntimeError, match="Connection pool creation failed"):
            MariaDBConnector(config)
