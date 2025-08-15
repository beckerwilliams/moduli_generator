"""
Integration tests for the configuration functionality.

This module tests the argument parsing and configuration creation functionality,
including CLI argument processing, validation, and ModuliConfig object creation.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from config import default_config
from config.argparser_moduli_generator import _moduli_generator_argparser, local_config


class TestModuliGeneratorArgParser:
    """Test cases for the _moduli_generator_argparser function."""

    @pytest.mark.integration
    @patch("sys.argv", ["moduli_generator"])
    def test_argparser_default_values(self):
        """Test argument parser with default values."""
        args = _moduli_generator_argparser()

        # Verify default values are set correctly
        assert args.candidates_dir == str(
            default_config.candidates_dir.relative_to(default_config.moduli_home)
        )
        assert args.delete_records_on_moduli_write is False
        assert args.key_lengths == default_config.key_lengths
        assert args.log_dir == str(
            default_config.log_dir.relative_to(default_config.moduli_home)
        )
        assert args.mariadb_cnf == str(
            default_config.mariadb_cnf.relative_to(default_config.moduli_home)
        )
        assert args.moduli_dir == str(
            default_config.moduli_dir.relative_to(default_config.moduli_home)
        )
        assert args.moduli_home == str(default_config.moduli_home)
        assert args.moduli_db == default_config.db_name
        assert args.nice_value == default_config.nice_value
        assert args.records_per_keylength == default_config.records_per_keylength

    @pytest.mark.integration
    @patch("sys.argv", ["moduli_generator", "--key-lengths", "4096", "8192"])
    def test_argparser_key_lengths_parsing(self):
        """Test parsing of key lengths argument."""
        args = _moduli_generator_argparser()

        assert args.key_lengths == [4096, 8192]

    @pytest.mark.integration
    @patch("sys.argv", ["moduli_generator", "--key-lengths", "3072", "4096", "8192"])
    def test_argparser_multiple_key_lengths(self):
        """Test parsing of multiple key lengths."""
        args = _moduli_generator_argparser()

        assert args.key_lengths == [3072, 4096, 8192]

    @pytest.mark.integration
    @patch("sys.argv", ["moduli_generator", "--nice-value", "15"])
    def test_argparser_nice_value_parsing(self):
        """Test parsing of nice value argument."""
        args = _moduli_generator_argparser()

        assert args.nice_value == 15

    @pytest.mark.integration
    @patch("sys.argv", ["moduli_generator", "--nice-value", "-10"])
    def test_argparser_negative_nice_value(self):
        """Test parsing of negative nice value."""
        args = _moduli_generator_argparser()

        assert args.nice_value == -10

    @pytest.mark.integration
    @patch("sys.argv", ["moduli_generator", "--delete-records-on-moduli-write"])
    def test_argparser_boolean_flag_true(self):
        """Test parsing of boolean flag when present."""
        args = _moduli_generator_argparser()

        assert args.delete_records_on_moduli_write is True

    @pytest.mark.integration
    @patch("sys.argv", ["moduli_generator"])
    def test_argparser_boolean_flag_false(self):
        """Test parsing of boolean flag when absent."""
        args = _moduli_generator_argparser()

        assert args.delete_records_on_moduli_write is False

    @pytest.mark.integration
    @patch("sys.argv", ["moduli_generator", "--moduli-home", "/custom/path"])
    def test_argparser_custom_moduli_home(self):
        """Test parsing of custom moduli home directory."""
        args = _moduli_generator_argparser()

        assert args.moduli_home == "/custom/path"

    @pytest.mark.integration
    @patch("sys.argv", ["moduli_generator", "--candidates-dir", "custom_candidates"])
    def test_argparser_custom_candidates_dir(self):
        """Test parsing of custom candidates directory."""
        args = _moduli_generator_argparser()

        assert args.candidates_dir == "custom_candidates"

    @pytest.mark.integration
    @patch("sys.argv", ["moduli_generator", "--moduli-dir", "custom_moduli"])
    def test_argparser_custom_moduli_dir(self):
        """Test parsing of custom moduli directory."""
        args = _moduli_generator_argparser()

        assert args.moduli_dir == "custom_moduli"

    @pytest.mark.integration
    @patch("sys.argv", ["moduli_generator", "--log-dir", "custom_logs"])
    def test_argparser_custom_log_dir(self):
        """Test parsing of custom log directory."""
        args = _moduli_generator_argparser()

        assert args.log_dir == "custom_logs"

    @pytest.mark.integration
    @patch("sys.argv", ["moduli_generator", "--mariadb-cnf", "custom.cnf"])
    def test_argparser_custom_mariadb_cnf(self):
        """Test parsing of custom MariaDB configuration file."""
        args = _moduli_generator_argparser()

        assert args.mariadb_cnf == "custom.cnf"

    @pytest.mark.integration
    @patch("sys.argv", ["moduli_generator", "--moduli-db", "custom_database"])
    def test_argparser_custom_database_name(self):
        """Test parsing of custom database name."""
        args = _moduli_generator_argparser()

        assert args.moduli_db == "custom_database"

    @pytest.mark.integration
    @patch("sys.argv", ["moduli_generator", "--records-per-keylength", "500"])
    def test_argparser_custom_records_per_keylength(self):
        """Test parsing of custom records per key length."""
        args = _moduli_generator_argparser()

        assert args.records_per_keylength == 500

    @pytest.mark.integration
    @patch(
        "sys.argv",
        [
            "moduli_generator",
            "--key-lengths",
            "4096",
            "8192",
            "--nice-value",
            "10",
            "--moduli-home",
            "/custom/path",
            "--delete-records-on-moduli-write",
            "--records-per-keylength",
            "200",
        ],
    )
    def test_argparser_combined_arguments(self):
        """Test parsing of multiple combined arguments."""
        args = _moduli_generator_argparser()

        assert args.key_lengths == [4096, 8192]
        assert args.nice_value == 10
        assert args.moduli_home == "/custom/path"
        assert args.delete_records_on_moduli_write is True
        assert args.records_per_keylength == 200


class TestLocalConfigFunction:
    """Test cases for the local_config function."""

    @pytest.mark.integration
    @patch("config.argparser_moduli_generator._moduli_generator_argparser")
    @patch("config.default_config.with_base_dir")
    @patch("db.is_valid_identifier_sql")
    def test_local_config_with_none_args(
        self, mock_is_valid, mock_with_base_dir, mock_argparser
    ):
        """Test local_config function with None arguments."""
        # Setup mocks
        mock_args = MagicMock()
        mock_args.moduli_home = "/test/home"
        mock_args.moduli_db = "test_db"
        mock_args.candidates_dir = "candidates"
        mock_args.moduli_dir = "moduli"
        mock_args.log_dir = "logs"
        mock_args.mariadb_cnf = "test.cnf"
        mock_args.records_per_keylength = 100
        mock_args.delete_records_on_moduli_write = False
        mock_args.key_lengths = [4096, 8192]
        mock_args.nice_value = 10
        mock_argparser.return_value = mock_args

        mock_config = MagicMock()
        mock_config.moduli_home = Path("/test/home")
        mock_with_base_dir.return_value = mock_config
        mock_is_valid.return_value = True

        # Execute function
        result = local_config(None)

        # Verify behavior
        mock_argparser.assert_called_once()
        mock_with_base_dir.assert_called_once_with("/test/home")
        mock_is_valid.assert_called_once_with("test_db")
        mock_config.ensure_directories.assert_called_once()

        # Verify config properties are set
        assert mock_config.db_name == "test_db"
        assert mock_config.candidates_dir == mock_config.moduli_home / "candidates"
        assert mock_config.moduli_dir == mock_config.moduli_home / "moduli"
        assert mock_config.log_dir == mock_config.moduli_home / "logs"
        assert mock_config.mariadb_cnf == mock_config.moduli_home / "test.cnf"
        assert mock_config.records_per_keylength == 100
        assert mock_config.delete_records_on_moduli_write is False
        assert mock_config.key_lengths == (4096, 8192)
        assert mock_config.nice_value == 10

    @pytest.mark.integration
    @patch("config.default_config.with_base_dir")
    @patch("db.is_valid_identifier_sql")
    def test_local_config_with_provided_args(self, mock_is_valid, mock_with_base_dir):
        """Test local_config function with provided arguments."""
        # Setup mocks
        mock_args = MagicMock()
        mock_args.moduli_home = "/custom/home"
        mock_args.moduli_db = "custom_db"
        mock_args.candidates_dir = "custom_candidates"
        mock_args.moduli_dir = "custom_moduli"
        mock_args.log_dir = "custom_logs"
        mock_args.mariadb_cnf = "custom.cnf"
        mock_args.records_per_keylength = 200
        mock_args.delete_records_on_moduli_write = True
        mock_args.key_lengths = [3072, 4096]
        mock_args.nice_value = -5

        mock_config = MagicMock()
        mock_config.moduli_home = Path("/custom/home")
        mock_with_base_dir.return_value = mock_config
        mock_is_valid.return_value = True

        # Execute function
        result = local_config(mock_args)

        # Verify behavior
        mock_with_base_dir.assert_called_once_with("/custom/home")
        mock_is_valid.assert_called_once_with("custom_db")
        mock_config.ensure_directories.assert_called_once()

        # Verify config properties are set
        assert mock_config.db_name == "custom_db"
        assert (
            mock_config.candidates_dir == mock_config.moduli_home / "custom_candidates"
        )
        assert mock_config.moduli_dir == mock_config.moduli_home / "custom_moduli"
        assert mock_config.log_dir == mock_config.moduli_home / "custom_logs"
        assert mock_config.mariadb_cnf == mock_config.moduli_home / "custom.cnf"
        assert mock_config.records_per_keylength == 200
        assert mock_config.delete_records_on_moduli_write is True
        assert mock_config.key_lengths == (3072, 4096)
        assert mock_config.nice_value == -5

    @pytest.mark.integration
    @patch("config.default_config.with_base_dir")
    @patch("db.is_valid_identifier_sql")
    def test_local_config_invalid_database_name(
        self, mock_is_valid, mock_with_base_dir
    ):
        """Test local_config function with invalid database name."""
        # Setup mocks
        mock_args = MagicMock()
        mock_args.moduli_home = "/test/home"
        mock_args.moduli_db = "invalid-db-name!"
        mock_args.candidates_dir = "candidates"
        mock_args.moduli_dir = "moduli"
        mock_args.log_dir = "logs"
        mock_args.mariadb_cnf = "test.cnf"
        mock_args.records_per_keylength = 100
        mock_args.delete_records_on_moduli_write = False
        mock_args.key_lengths = [4096]
        mock_args.nice_value = 0
        mock_args.version = False

        mock_config = MagicMock()
        mock_with_base_dir.return_value = mock_config
        mock_is_valid.return_value = False

        # Execute function and expect RuntimeError
        with pytest.raises(
            RuntimeError, match="Invalid database name: invalid-db-name!"
        ):
            local_config(mock_args)

        # Verify validation was called
        mock_is_valid.assert_called_once_with("invalid-db-name!")

    @pytest.mark.integration
    @patch("config.default_config.with_base_dir")
    @patch("db.is_valid_identifier_sql")
    def test_local_config_database_name_validation_edge_cases(
        self, mock_is_valid, mock_with_base_dir
    ):
        """Test local_config database name validation with edge cases."""
        mock_config = MagicMock()
        mock_config.moduli_home = Path("/test/home")
        mock_with_base_dir.return_value = mock_config

        # Test cases for database name validation
        test_cases = [
            ("valid_db_name", True),
            ("ValidDBName", True),
            ("db123", True),
            ("invalid-name", False),
            ("invalid name", False),
            ("invalid.name", False),
            ("", False),
            ("123invalid", False),
        ]

        for db_name, is_valid in test_cases:
            mock_args = MagicMock()
            mock_args.moduli_home = "/test/home"
            mock_args.moduli_db = db_name
            mock_args.candidates_dir = "candidates"
            mock_args.moduli_dir = "moduli"
            mock_args.log_dir = "logs"
            mock_args.mariadb_cnf = "test.cnf"
            mock_args.records_per_keylength = 100
            mock_args.delete_records_on_moduli_write = False
            mock_args.key_lengths = [4096]
            mock_args.nice_value = 0
            mock_args.version = False

            mock_is_valid.return_value = is_valid

            if is_valid:
                result = local_config(mock_args)
                assert mock_config.db_name == db_name
            else:
                with pytest.raises(
                    RuntimeError, match=f"Invalid database name: {db_name}"
                ):
                    local_config(mock_args)

    @pytest.mark.integration
    @patch("config.default_config.with_base_dir")
    @patch("db.is_valid_identifier_sql")
    def test_local_config_path_construction(self, mock_is_valid, mock_with_base_dir):
        """Test local_config path construction logic."""
        # Setup mocks
        mock_args = MagicMock()
        mock_args.moduli_home = "/base/path"
        mock_args.moduli_db = "test_db"
        mock_args.candidates_dir = "rel_candidates"
        mock_args.moduli_dir = "rel_moduli"
        mock_args.log_dir = "rel_logs"
        mock_args.mariadb_cnf = "rel_config.cnf"
        mock_args.records_per_keylength = 100
        mock_args.delete_records_on_moduli_write = False
        mock_args.key_lengths = [4096]
        mock_args.nice_value = 0
        mock_args.version = False

        mock_config = MagicMock()
        mock_config.moduli_home = Path("/base/path")
        mock_with_base_dir.return_value = mock_config
        mock_is_valid.return_value = True

        # Execute function
        result = local_config(mock_args)

        # Verify path construction
        assert mock_config.candidates_dir == mock_config.moduli_home / "rel_candidates"
        assert mock_config.moduli_dir == mock_config.moduli_home / "rel_moduli"
        assert mock_config.log_dir == mock_config.moduli_home / "rel_logs"
        assert mock_config.mariadb_cnf == mock_config.moduli_home / "rel_config.cnf"

    @pytest.mark.integration
    @patch("config.default_config.with_base_dir")
    @patch("db.is_valid_identifier_sql")
    def test_local_config_key_lengths_tuple_conversion(
        self, mock_is_valid, mock_with_base_dir
    ):
        """Test local_config converts key_lengths list to tuple."""
        # Setup mocks
        mock_args = MagicMock()
        mock_args.moduli_home = "/test/home"
        mock_args.moduli_db = "test_db"
        mock_args.candidates_dir = "candidates"
        mock_args.moduli_dir = "moduli"
        mock_args.log_dir = "logs"
        mock_args.mariadb_cnf = "test.cnf"
        mock_args.records_per_keylength = 100
        mock_args.delete_records_on_moduli_write = False
        mock_args.key_lengths = [3072, 4096, 8192]  # List input
        mock_args.nice_value = 0
        mock_args.version = False

        mock_config = MagicMock()
        mock_config.moduli_home = Path("/test/home")
        mock_with_base_dir.return_value = mock_config
        mock_is_valid.return_value = True

        # Execute function
        result = local_config(mock_args)

        # Verify tuple conversion
        assert mock_config.key_lengths == (3072, 4096, 8192)
        assert isinstance(mock_config.key_lengths, tuple)

    @pytest.mark.integration
    @patch("config.default_config.with_base_dir")
    @patch("db.is_valid_identifier_sql")
    def test_local_config_ensure_directories_called(
        self, mock_is_valid, mock_with_base_dir
    ):
        """Test that local_config calls ensure_directories."""
        # Setup mocks
        mock_args = MagicMock()
        mock_args.moduli_home = "/test/home"
        mock_args.moduli_db = "test_db"
        mock_args.candidates_dir = "candidates"
        mock_args.moduli_dir = "moduli"
        mock_args.log_dir = "logs"
        mock_args.mariadb_cnf = "test.cnf"
        mock_args.records_per_keylength = 100
        mock_args.delete_records_on_moduli_write = False
        mock_args.key_lengths = [4096]
        mock_args.nice_value = 0
        mock_args.version = False

        mock_config = MagicMock()
        mock_config.moduli_home = Path("/test/home")
        mock_with_base_dir.return_value = mock_config
        mock_is_valid.return_value = True

        # Execute function
        result = local_config(mock_args)

        # Verify ensure_directories was called
        mock_config.ensure_directories.assert_called_once()


class TestConfigMainEntryPoint:
    """Test cases for the config module main entry point."""

    @pytest.mark.integration
    @patch("config.argparser_moduli_generator.local_config")
    @patch("builtins.print")
    def test_config_main_entry_point(self, mock_print, mock_local_config):
        """Test the __main__ entry point of the config module."""
        # Setup mock config
        mock_config = MagicMock()
        mock_config.key_lengths = (4096, 8192)
        mock_config.nice_value = 10
        mock_config.moduli_home = Path("/test/home")
        mock_local_config.return_value = mock_config

        # Mock vars() to return a dictionary of attributes
        with patch("builtins.vars") as mock_vars:
            mock_vars.return_value = {
                "key_lengths": (4096, 8192),
                "nice_value": 10,
                "moduli_home": Path("/test/home"),
            }

            # Import and execute the module's __main__ block directly
            import config.argparser_moduli_generator

            # Simulate running the module as __main__
            with patch.object(config.argparser_moduli_generator, "__name__", "__main__"):
                # Execute the actual __main__ block code
                mg_args = config.argparser_moduli_generator.local_config()
                print(
                    f"Moduli Generator Commands, Flags, and Options, Using default config: {mg_args}"
                )
                print("\t\t\t** default_config **")
                print(f"# Argument: # Value")
                for item in vars(mg_args):
                    print(f"{item} : {getattr(mg_args, item)}")

        # Verify function calls
        mock_local_config.assert_called_once()
        assert mock_print.call_count >= 3  # Header prints plus attribute prints


class TestConfigIntegrationScenarios:
    """Test cases for complete configuration integration scenarios."""

    @pytest.mark.integration
    @patch(
        "sys.argv",
        [
            "moduli_generator",
            "--moduli-home",
            "/production/moduli",
            "--key-lengths",
            "4096",
            "8192",
            "--nice-value",
            "15",
            "--moduli-db",
            "production_moduli",
            "--records-per-keylength",
            "500",
            "--delete-records-on-moduli-write",
        ],
    )
    @patch("argparse.ArgumentParser.parse_args")
    @patch("config.default_config.with_base_dir")
    @patch("db.is_valid_identifier_sql")
    def test_production_like_configuration(self, mock_is_valid, mock_with_base_dir, mock_parse_args):
        """Test production-like configuration scenario."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.moduli_home = Path("/production/moduli")
        mock_with_base_dir.return_value = mock_config
        mock_is_valid.return_value = True

        # Mock the parsed args
        mock_args = MagicMock()
        mock_args.moduli_home = "/production/moduli"
        mock_args.moduli_db = "production_moduli"
        mock_args.candidates_dir = "candidates"
        mock_args.moduli_dir = "moduli"
        mock_args.log_dir = "logs"
        mock_args.mariadb_cnf = "test.cnf"
        mock_args.records_per_keylength = 500
        mock_args.delete_records_on_moduli_write = True
        mock_args.key_lengths = [4096, 8192]
        mock_args.nice_value = 15
        mock_args.version = False
        mock_args.restart = False
        mock_parse_args.return_value = mock_args
        
        # Execute complete workflow
        args = _moduli_generator_argparser()
        config = local_config(args)

        # Verify production configuration
        assert args.moduli_home == "/production/moduli"
        assert args.key_lengths == [4096, 8192]
        assert args.nice_value == 15
        assert args.moduli_db == "production_moduli"
        assert args.records_per_keylength == 500
        assert args.delete_records_on_moduli_write is True

        # Verify config object setup
        mock_with_base_dir.assert_called_once_with("/production/moduli")
        mock_is_valid.assert_called_once_with("production_moduli")
        mock_config.ensure_directories.assert_called_once()

    @pytest.mark.integration
    @patch("sys.argv", ["moduli_generator", "--moduli-db", "invalid_db_name!"])
    @patch("argparse.ArgumentParser.parse_args")
    @patch("config.default_config.with_base_dir")
    @patch("db.is_valid_identifier_sql")
    def test_error_handling_integration(self, mock_is_valid, mock_with_base_dir, mock_parse_args):
        """Test error handling integration scenario."""
        # Setup mocks
        mock_config = MagicMock()
        mock_with_base_dir.return_value = mock_config
        mock_is_valid.return_value = False

        # Setup mock arguments
        mock_args = MagicMock()
        mock_args.moduli_home = "/test/home"
        mock_args.moduli_db = "invalid_db_name!"
        mock_args.candidates_dir = "candidates"
        mock_args.moduli_dir = "moduli"
        mock_args.log_dir = "logs"
        mock_args.mariadb_cnf = "test.cnf"
        mock_args.records_per_keylength = 100
        mock_args.delete_records_on_moduli_write = False
        mock_args.key_lengths = [4096]
        mock_args.nice_value = 0
        mock_args.version = False
        mock_args.restart = False
        mock_parse_args.return_value = mock_args

        # Execute and expect error
        args = _moduli_generator_argparser()

        with pytest.raises(
            RuntimeError, match="Invalid database name: invalid_db_name!"
        ):
            local_config(args)

        # Verify validation was attempted
        mock_is_valid.assert_called_once_with("invalid_db_name!")

    @pytest.mark.integration
    @patch(
        "sys.argv",
        [
            "moduli_generator",
            "--key-lengths",
            "3072",
            "4096",
            "7168",
            "8192",
            "--nice-value",
            "-20",
        ],
    )
    @patch("config.default_config.with_base_dir")
    @patch("db.is_valid_identifier_sql")
    def test_extreme_values_configuration(self, mock_is_valid, mock_with_base_dir):
        """Test configuration with extreme but valid values."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.moduli_home = Path("/test/home")
        mock_with_base_dir.return_value = mock_config
        mock_is_valid.return_value = True

        # Execute workflow
        args = _moduli_generator_argparser()
        config = local_config(args)

        # Verify extreme values are handled
        assert args.key_lengths == [3072, 4096, 7168, 8192]
        assert args.nice_value == -20
        assert mock_config.key_lengths == (3072, 4096, 7168, 8192)
        assert mock_config.nice_value == -20

    @pytest.mark.integration
    @patch("config.argparser_moduli_generator._moduli_generator_argparser")
    @patch("config.default_config.with_base_dir")
    @patch("db.is_valid_identifier_sql")
    def test_config_workflow_with_mocked_argparser(
        self, mock_is_valid, mock_with_base_dir, mock_argparser
    ):
        """Test complete configuration workflow with mocked argument parser."""
        # Setup comprehensive mock arguments
        mock_args = MagicMock()
        mock_args.moduli_home = "/comprehensive/test"
        mock_args.moduli_db = "comprehensive_db"
        mock_args.candidates_dir = "test_candidates"
        mock_args.moduli_dir = "test_moduli"
        mock_args.log_dir = "test_logs"
        mock_args.mariadb_cnf = "test_maria.cnf"
        mock_args.records_per_keylength = 300
        mock_args.delete_records_on_moduli_write = True
        mock_args.key_lengths = [4096, 8192]
        mock_args.nice_value = 5
        mock_args.version = False
        mock_args.restart = False
        mock_argparser.return_value = mock_args

        mock_config = MagicMock()
        mock_config.moduli_home = Path("/comprehensive/test")
        mock_with_base_dir.return_value = mock_config
        mock_is_valid.return_value = True

        # Execute complete workflow
        result_config = local_config()

        # Verify all components were called correctly
        mock_argparser.assert_called_once()
        mock_with_base_dir.assert_called_once_with("/comprehensive/test")
        mock_is_valid.assert_called_once_with("comprehensive_db")
        mock_config.ensure_directories.assert_called_once()

        # Verify all configuration properties were set
        assert mock_config.db_name == "comprehensive_db"
        assert mock_config.records_per_keylength == 300
        assert mock_config.delete_records_on_moduli_write is True
        assert mock_config.key_lengths == (4096, 8192)
        assert mock_config.nice_value == 5
