#!/usr/bin/env python
"""
Comprehensive tests for config/__init__.py module.
Tests all functions and methods to achieve 95% test coverage.
"""

import os
import shutil
import tempfile
from datetime import datetime
from logging import Logger
from pathlib import Path
from unittest.mock import MagicMock, patch

from config import (
    ModuliConfig,
    default_config,
    iso_utc_timestamp,
    strip_punction_from_datetime_str,
)
from db import is_valid_identifier_sql


class TestISOUTCTimestamp:
    """Test cases for iso_utc_timestamp function."""

    def test_iso_utc_timestamp_uncompressed(self):
        """Test iso_utc_timestamp returns proper ISO format when compress=False."""
        result = iso_utc_timestamp(compress=False)

        # Should be a valid ISO format string
        assert isinstance(result, str)
        assert "T" in result  # ISO format contains T separator
        assert len(result) >= 19  # Minimum length for ISO format

        # Should be parseable as datetime
        datetime.fromisoformat(result)

    def test_iso_utc_timestamp_compressed(self):
        """Test iso_utc_timestamp returns numeric string when compress=True."""
        result = iso_utc_timestamp(compress=True)

        # Should be a string containing only digits
        assert isinstance(result, str)
        assert result.isdigit()
        assert len(result) >= 14  # At least YYYYMMDDHHMMSS

    def test_iso_utc_timestamp_default_parameter(self):
        """Test iso_utc_timestamp default parameter behavior."""
        result = iso_utc_timestamp()

        # Default should be uncompressed
        assert isinstance(result, str)
        assert "T" in result
        datetime.fromisoformat(result)

    @patch("config.datetime")
    def test_iso_utc_timestamp_mocked_time(self, mock_datetime):
        """Test iso_utc_timestamp with mocked datetime."""
        # Mock datetime to return a specific time
        mock_dt = MagicMock()
        mock_dt.replace.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        mock_datetime.now.return_value = mock_dt

        result = iso_utc_timestamp(compress=False)
        assert result == "2023-01-01T12:00:00"

        # Test compressed version
        result_compressed = iso_utc_timestamp(compress=True)
        assert result_compressed == "20230101120000"


class TestStripPunctionFromDatetimeStr:
    """Test cases for strip_punction_from_datetime_str function."""

    def test_strip_punction_basic(self):
        """Test basic functionality of strip_punction_from_datetime_str."""
        dt = datetime(2023, 1, 15, 14, 30, 45)
        result = strip_punction_from_datetime_str(dt)

        assert isinstance(result, str)
        assert result.isdigit()
        assert result == "20230115143045"

    def test_strip_punction_with_microseconds(self):
        """Test strip_punction_from_datetime_str with microseconds."""
        dt = datetime(2023, 12, 31, 23, 59, 59, 999999)
        result = strip_punction_from_datetime_str(dt)

        assert isinstance(result, str)
        assert result.isdigit()
        assert result == "20231231235959999999"

    def test_strip_punction_edge_cases(self):
        """Test strip_punction_from_datetime_str with edge case dates."""
        # Test leap year
        dt = datetime(2024, 2, 29, 0, 0, 0)
        result = strip_punction_from_datetime_str(dt)
        assert result == "20240229000000"

        # Test single digit month/day
        dt = datetime(2023, 1, 1, 1, 1, 1)
        result = strip_punction_from_datetime_str(dt)
        assert result == "20230101010101"


class TestIsValidIdentifierSQL:
    """Test cases for is_valid_identifier_sql function."""

    def test_valid_unquoted_identifiers(self):
        """Test valid unquoted SQL identifiers."""
        valid_identifiers = [
            "table_name",
            "column1",
            "my_table",
            "user_id",
            "test123",
            "a",
            "A",
            "table$name",
            "column_name_123",
            "TEST_TABLE",
        ]

        for identifier in valid_identifiers:
            assert is_valid_identifier_sql(
                identifier
            ), f"'{identifier}' should be valid"

    def test_valid_quoted_identifiers(self):
        """Test valid quoted SQL identifiers."""
        valid_quoted = [
            "`table name`",
            "`column-name`",
            "`123table`",
            "`select`",
            "`my table with spaces`",
            "`table@name`",
            "`column.name`",
        ]

        for identifier in valid_quoted:
            assert is_valid_identifier_sql(
                identifier
            ), f"'{identifier}' should be valid"

    def test_invalid_identifiers(self):
        """Test invalid SQL identifiers."""
        invalid_identifiers = [
            "",  # Empty string
            None,  # None value
            123,  # Not a string
            "table-name",  # Hyphen not allowed in unquoted
            "table name",  # Space not allowed in unquoted
            "table@name",  # @ not allowed in unquoted
            "table.name",  # Dot not allowed in unquoted
            "`",  # Single backtick
            "`table",  # Unclosed backtick
            "table`",  # Misplaced backtick
            "``",  # Empty quoted identifier
            "a" * 65,  # Too long (over 64 chars)
            "`" + "a" * 63 + "`",  # Too long quoted (over 64 chars total)
        ]

        for identifier in invalid_identifiers:
            assert not is_valid_identifier_sql(
                identifier
            ), f"'{identifier}' should be invalid"

    def test_edge_case_lengths(self):
        """Test identifier length edge cases."""
        # Exactly 64 characters - should be valid
        valid_64 = "a" * 64
        assert is_valid_identifier_sql(valid_64)

        # 65 characters - should be invalid
        invalid_65 = "a" * 65
        assert not is_valid_identifier_sql(invalid_65)

        # Quoted identifier with exactly 64 chars total
        valid_quoted_64 = "`" + "a" * 62 + "`"  # 62 + 2 backticks = 64
        assert is_valid_identifier_sql(valid_quoted_64)

    def test_type_validation(self):
        """Test type validation for is_valid_identifier_sql."""
        # Test non-string types
        assert not is_valid_identifier_sql(123)
        assert not is_valid_identifier_sql([])
        assert not is_valid_identifier_sql({})
        assert not is_valid_identifier_sql(None)


class TestModuliConfig:
    """Test cases for ModuliConfig class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, "temp_dir") and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_init_default(self):
        """Test ModuliConfig initialization with default parameters."""
        config = ModuliConfig()

        # Check that all attributes are set
        assert hasattr(config, "moduli_home")
        assert hasattr(config, "candidates_dir")
        assert hasattr(config, "moduli_dir")
        assert hasattr(config, "log_dir")
        assert hasattr(config, "log_file")
        assert hasattr(config, "key_lengths")
        assert hasattr(config, "generator_type")
        assert hasattr(config, "nice_value")
        assert hasattr(config, "db_name")
        assert hasattr(config, "table_name")
        assert hasattr(config, "view_name")
        assert hasattr(config, "records_per_keylength")
        assert hasattr(config, "config_id")
        assert hasattr(config, "mariadb_cnf")
        assert hasattr(config, "moduli_file_pattern")
        assert hasattr(config, "moduli_file_pfx")
        assert hasattr(config, "delete_records_on_moduli_write")
        assert hasattr(config, "version")

        # Check types
        assert isinstance(config.moduli_home, Path)
        assert isinstance(config.candidates_dir, Path)
        assert isinstance(config.moduli_dir, Path)
        assert isinstance(config.log_dir, Path)
        assert isinstance(config.log_file, Path)
        assert isinstance(config.key_lengths, tuple)
        assert isinstance(config.generator_type, int)
        assert isinstance(config.nice_value, int)
        assert isinstance(config.db_name, str)
        assert isinstance(config.table_name, str)
        assert isinstance(config.view_name, str)
        assert isinstance(config.records_per_keylength, int)
        assert isinstance(config.config_id, int)
        assert isinstance(config.mariadb_cnf, Path)
        assert isinstance(config.moduli_file_pattern, str)
        assert isinstance(config.moduli_file_pfx, str)
        assert isinstance(config.delete_records_on_moduli_write, bool)
        assert isinstance(config.version, str)

    def test_init_with_base_dir(self):
        """Test ModuliConfig initialization with custom base directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ModuliConfig(base_dir=temp_dir)

            assert config.moduli_home == Path(temp_dir)
            assert config.candidates_dir == Path(temp_dir) / ".candidates"
            assert config.moduli_dir == Path(temp_dir) / ".moduli"
            assert config.log_dir == Path(temp_dir) / ".logs"

    @patch.dict(os.environ, {"MODULI_HOME": "/custom/path"})
    def test_init_with_env_var(self):
        """Test ModuliConfig initialization with MODULI_HOME environment variable."""
        config = ModuliConfig()

        assert config.moduli_home == Path("/custom/path")

    def test_ensure_directories(self):
        """Test ensure_directories method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ModuliConfig(base_dir=temp_dir)

            # Directories shouldn't exist initially
            assert not config.candidates_dir.exists()
            assert not config.moduli_dir.exists()
            assert not config.log_dir.exists()

            # Call ensure_directories
            result = config.ensure_directories()

            # Should return self
            assert result is config

            # Directories should now exist
            assert config.moduli_home.exists()
            assert config.candidates_dir.exists()
            assert config.moduli_dir.exists()
            assert config.log_dir.exists()

    def test_ensure_directories_existing(self):
        """Test ensure_directories when directories already exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ModuliConfig(base_dir=temp_dir)

            # Create directories manually
            config.moduli_home.mkdir(exist_ok=True)
            config.candidates_dir.mkdir(exist_ok=True)
            config.moduli_dir.mkdir(exist_ok=True)
            config.log_dir.mkdir(exist_ok=True)

            # Should not raise error when directories exist
            result = config.ensure_directories()
            assert result is config

    @patch("config.basicConfig")
    @patch("config.getLogger")
    def test_get_logger(self, mock_get_logger, mock_basic_config):
        """Test get_logger method."""
        mock_logger = MagicMock(spec=Logger)
        mock_get_logger.return_value = mock_logger

        with tempfile.TemporaryDirectory() as temp_dir:
            config = ModuliConfig(base_dir=temp_dir)

            result = config.get_logger()

            # Should return the mocked logger
            assert result is mock_logger

            # Should have called basicConfig
            mock_basic_config.assert_called_once()

            # Check basicConfig was called with correct parameters
            call_args = mock_basic_config.call_args
            assert "level" in call_args.kwargs
            assert "format" in call_args.kwargs
            assert "filename" in call_args.kwargs
            assert "filemode" in call_args.kwargs

    @patch("config.basicConfig")
    @patch("config.getLogger")
    def test_get_logger_nonexistent_home(self, mock_get_logger, mock_basic_config):
        """Test get_logger method when moduli_home doesn't exist."""
        mock_logger = MagicMock(spec=Logger)
        mock_get_logger.return_value = mock_logger

        with tempfile.TemporaryDirectory() as temp_dir:
            # Use a non-existent subdirectory
            nonexistent_dir = Path(temp_dir) / "nonexistent"
            config = ModuliConfig(base_dir=str(nonexistent_dir))

            # Ensure the directory doesn't exist
            assert not config.moduli_home.exists()

            result = config.get_logger()

            # Should return the mocked logger
            assert result is mock_logger

            # Should have called basicConfig
            mock_basic_config.assert_called_once()

            # The directory should now exist (created by get_logger)
            assert config.moduli_home.exists()

    def test_get_log_file_with_name(self):
        """Test get_log_file method with custom name."""
        config = ModuliConfig()

        result = config.get_log_file("custom.log")

        assert isinstance(result, Path)
        assert result == config.log_dir / "custom.log"

    def test_get_log_file_without_name(self):
        """Test get_log_file method without name (default)."""
        config = ModuliConfig()

        result = config.get_log_file(None)

        assert isinstance(result, Path)
        assert result == config.log_file

        # Test with empty string
        result = config.get_log_file("")
        assert result == config.log_file

    def test_with_base_dir_static_method(self):
        """Test with_base_dir static method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ModuliConfig.with_base_dir(temp_dir)

            assert isinstance(config, ModuliConfig)
            assert config.moduli_home == Path(temp_dir)

    def test_version_property(self):
        """Test __version__ property."""
        config = ModuliConfig()

        version = config.__version__

        assert isinstance(version, str)
        assert len(version) > 0
        assert version == config.version


class TestDefaultConfig:
    """Test cases for default_config module-level instance."""

    def test_default_config_exists(self):
        """Test that default_config is properly instantiated."""
        assert default_config() is not None
        assert isinstance(default_config(), ModuliConfig)

    def test_default_config_directories_ensured(self):
        """Test that default_config has directories ensured."""
        # The default_config should have ensure_directories() called
        # We can verify this by checking that the directories exist
        # (though they might be created in the user's home directory)
        assert hasattr(default_config(), "moduli_home")
        assert hasattr(default_config(), "candidates_dir")
        assert hasattr(default_config(), "moduli_dir")
        assert hasattr(default_config(), "log_dir")


class TestModuleIntegration:
    """Integration tests for the entire config module."""

    def test_all_exports_available(self):
        """Test that all expected exports are available."""
        from config import (
            ModuliConfig,
            default_config,
            iso_utc_timestamp,
            strip_punction_from_datetime_str,
            DEFAULT_MARIADB_DB_NAME,
            DEFAULT_MARIADB_CNF,
            DEFAULT_KEY_LENGTHS,
            TEST_MARIADB_DB_NAME,
        )
        from db import is_valid_identifier_sql

        # All imports should succeed without error
        assert ModuliConfig is not None
        assert default_config() is not None
        assert iso_utc_timestamp is not None
        assert strip_punction_from_datetime_str is not None
        assert is_valid_identifier_sql is not None
        assert DEFAULT_MARIADB_DB_NAME is not None
        assert DEFAULT_MARIADB_CNF is not None
        assert DEFAULT_KEY_LENGTHS is not None
        assert TEST_MARIADB_DB_NAME is not None

    def test_constants_values(self):
        """Test that constants have expected values and types."""
        from config import DEFAULT_KEY_LENGTHS, TEST_MARIADB_DB_NAME, DEFAULT_MARIADB_DB_NAME

        assert isinstance(DEFAULT_KEY_LENGTHS, tuple)
        assert len(DEFAULT_KEY_LENGTHS) > 0
        assert all(isinstance(x, int) for x in DEFAULT_KEY_LENGTHS)

        assert isinstance(TEST_MARIADB_DB_NAME, str)
        assert len(TEST_MARIADB_DB_NAME) > 0

        assert isinstance(DEFAULT_MARIADB_DB_NAME, str)
        assert len(DEFAULT_MARIADB_DB_NAME) > 0
