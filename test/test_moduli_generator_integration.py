"""
Integration tests for the ModuliGenerator class.

This module tests the core ModuliGenerator functionality including moduli generation,
file processing, database storage, and the complete workflow integration.
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import subprocess
import logging
from datetime import datetime

from moduli_generator import ModuliGenerator
from config import ModuliConfig, default_config
from db import MariaDBConnector


class TestModuliGeneratorInitialization:
    """Test cases for ModuliGenerator initialization and configuration."""

    @pytest.mark.integration
    def test_moduli_generator_init_default_config(self):
        """Test ModuliGenerator initialization with default configuration."""
        generator = ModuliGenerator()

        assert generator.config == default_config
        assert generator.config.key_lengths == default_config.key_lengths
        assert generator.config.nice_value == default_config.nice_value

    @pytest.mark.integration
    def test_moduli_generator_init_custom_config(self, mock_config):
        """Test ModuliGenerator initialization with custom configuration."""
        generator = ModuliGenerator(mock_config)

        assert generator.config == mock_config
        assert generator.config != default_config

    @pytest.mark.integration
    def test_moduli_generator_db_property(self, mock_db_config):
        """Test the database property returns MariaDBConnector instance."""
        generator = ModuliGenerator(mock_db_config)

        db_instance = generator.db
        assert isinstance(db_instance, MariaDBConnector)
        # MariaDBConnector copies config attributes, not the config object itself
        assert db_instance.db_name == mock_db_config.db_name
        assert db_instance.table_name == mock_db_config.table_name

    @pytest.mark.integration
    def test_moduli_generator_version_property(self):
        """Test the __version__ property returns version information."""
        generator = ModuliGenerator()

        version = generator.__version__
        assert isinstance(version, str)
        assert len(version) > 0


class TestModuliGeneratorSubprocessExecution:
    """Test cases for subprocess execution with logging."""

    @pytest.mark.integration
    @patch('subprocess.run')
    def test_run_subprocess_with_logging_success(self, mock_subprocess):
        """Test successful subprocess execution with logging."""
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="Test output",
            stderr=""
        )

        logger = MagicMock()
        command = ["echo", "test"]

        result = ModuliGenerator._run_subprocess_with_logging(
            command, logger, logging.INFO, logging.DEBUG
        )

        assert result.returncode == 0
        mock_subprocess.assert_called_once()
        logger.log.assert_called_with(logging.INFO, "Test output")

    @pytest.mark.integration
    @patch('subprocess.run')
    def test_run_subprocess_with_logging_failure(self, mock_subprocess):
        """Test subprocess execution failure with error logging."""
        mock_subprocess.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Test error"
        )

        logger = MagicMock()
        command = ["false"]

        result = ModuliGenerator._run_subprocess_with_logging(
            command, logger, logging.INFO, logging.DEBUG
        )

        assert result.returncode == 1
        mock_subprocess.assert_called_once()
        logger.log.assert_called_with(logging.DEBUG, "Test error")

    @pytest.mark.integration
    @patch('subprocess.run')
    def test_run_subprocess_with_logging_exception(self, mock_subprocess):
        """Test subprocess execution with exception handling."""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "test")

        logger = MagicMock()
        command = ["invalid_command"]

        with pytest.raises(subprocess.CalledProcessError):
            ModuliGenerator._run_subprocess_with_logging(
                command, logger, logging.INFO, logging.DEBUG
            )


class TestModuliGeneratorCandidateGeneration:
    """Test cases for candidate generation functionality."""

    @pytest.mark.integration
    @patch('moduli_generator.ModuliGenerator._run_subprocess_with_logging')
    def test_generate_candidates_static_success(self, mock_subprocess, mock_config):
        """Test static candidate generation method."""
        mock_subprocess.return_value = MagicMock(returncode=0)

        result = ModuliGenerator._generate_candidates_static(mock_config, 4096)

        # The method returns a Path object, not subprocess result
        assert isinstance(result, Path)
        mock_subprocess.assert_called_once()

        # Verify the command structure
        call_args = mock_subprocess.call_args[0]
        command = call_args[0]
        assert "ssh-keygen" in command
        assert "-M" in command
        assert "generate" in command

    @pytest.mark.integration
    @patch('moduli_generator.ModuliGenerator._run_subprocess_with_logging')
    def test_generate_candidates_instance_method(self, mock_subprocess, mock_config):
        """Test instance candidate generation method."""
        mock_subprocess.return_value = MagicMock(returncode=0)

        generator = ModuliGenerator(mock_config)
        result = generator._generate_candidates(4096)

        # The method returns a Path object, not subprocess result
        assert isinstance(result, Path)
        mock_subprocess.assert_called_once()

    @pytest.mark.integration
    @patch('moduli_generator.ModuliGenerator._run_subprocess_with_logging')
    def test_generate_candidates_with_nice_value(self, mock_subprocess, mock_config):
        """Test candidate generation with nice value setting."""
        mock_config.nice_value = 10
        mock_subprocess.return_value = MagicMock(returncode=0)

        generator = ModuliGenerator(mock_config)
        result = generator._generate_candidates(4096)

        # The method returns a Path object, not subprocess result
        assert isinstance(result, Path)

        # Verify nice command is included
        call_args = mock_subprocess.call_args[0]
        command = call_args[0]
        assert "nice" in command
        assert "-n" in command
        assert "10" in command


class TestModuliGeneratorCandidateScreening:
    """Test cases for candidate screening functionality."""

    @pytest.mark.integration
    @patch('moduli_generator.ModuliGenerator._run_subprocess_with_logging')
    def test_screen_candidates_static_success(self, mock_subprocess, mock_config, temp_file):
        """Test static candidate screening method."""
        mock_subprocess.return_value = MagicMock(returncode=0)

        candidates_file = Path(temp_file)
        result = ModuliGenerator._screen_candidates_static(mock_config, candidates_file)

        # The method returns a Path object, not subprocess result
        assert isinstance(result, Path)
        mock_subprocess.assert_called_once()

        # Verify the command structure
        call_args = mock_subprocess.call_args[0]
        command = call_args[0]
        assert "ssh-keygen" in command
        assert "-M" in command
        assert "screen" in command

    @pytest.mark.integration
    @patch('moduli_generator.ModuliGenerator._run_subprocess_with_logging')
    def test_screen_candidates_instance_method(self, mock_subprocess, mock_config, temp_file):
        """Test instance candidate screening method."""
        mock_subprocess.return_value = MagicMock(returncode=0)

        generator = ModuliGenerator(mock_config)
        candidates_file = Path(temp_file)
        result = generator._screen_candidates(candidates_file)

        # The method returns a Path object, not subprocess result
        assert isinstance(result, Path)
        mock_subprocess.assert_called_once()


class TestModuliGeneratorFileProcessing:
    """Test cases for moduli file processing functionality."""

    @pytest.mark.integration
    @patch('pathlib.Path.glob')
    def test_list_moduli_files(self, mock_glob, mock_config):
        """Test listing moduli files in the moduli directory."""
        mock_files = [Path("moduli_4096"), Path("moduli_8192")]
        mock_glob.return_value = mock_files

        generator = ModuliGenerator(mock_config)
        files = generator._list_moduli_files()

        assert files == mock_files
        mock_glob.assert_called_once_with("moduli_*")

    @pytest.mark.integration
    @patch('pathlib.Path.glob')
    def test_list_moduli_files_empty(self, mock_glob, mock_config):
        """Test listing moduli files when directory is empty."""
        mock_glob.return_value = []

        generator = ModuliGenerator(mock_config)
        files = generator._list_moduli_files()

        assert files == []

    @pytest.mark.integration
    @patch('pathlib.Path.open', new_callable=mock_open, read_data="20231201000000 2 4096 5 4096 2 test_modulus\n")
    @patch('pathlib.Path.glob')
    def test_parse_moduli_files_success(self, mock_glob, mock_file, mock_config):
        """Test parsing moduli files successfully."""
        mock_files = [Path("moduli_4096")]
        mock_glob.return_value = mock_files

        generator = ModuliGenerator(mock_config)
        moduli_data = generator._parse_moduli_files()

        assert isinstance(moduli_data, dict)
        assert 'screened_moduli' in moduli_data
        assert len(moduli_data['screened_moduli']) > 0

        # Verify the parsed data structure
        record = moduli_data['screened_moduli'][0]
        assert 'timestamp' in record
        assert 'key-size' in record
        assert 'modulus' in record

    @pytest.mark.integration
    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    @patch('pathlib.Path.glob')
    def test_parse_moduli_files_io_error(self, mock_glob, mock_file, mock_config):
        """Test parsing moduli files with IO error."""
        mock_files = [Path("moduli_4096")]
        mock_glob.return_value = mock_files

        generator = ModuliGenerator(mock_config)

        # The method handles FileNotFoundError gracefully and returns empty dict
        moduli_data = generator._parse_moduli_files()
        assert isinstance(moduli_data, dict)
        # Should be empty since no files could be read
        assert moduli_data == {}


class TestModuliGeneratorWorkflow:
    """Test cases for the complete ModuliGenerator workflow."""

    @pytest.mark.integration
    @patch('concurrent.futures.ProcessPoolExecutor')
    @patch('moduli_generator.ModuliGenerator._screen_candidates_static')
    @patch('moduli_generator.ModuliGenerator._generate_candidates_static')
    def test_generate_moduli_success(self, mock_generate_static, mock_screen_static, mock_executor, mock_config):
        """Test the complete generate_moduli workflow."""
        mock_config.key_lengths = (4096, 8192)

        # Mock the static methods to return file paths
        mock_generate_static.return_value = Path('/tmp/candidates_4096.txt')
        mock_screen_static.return_value = Path('/tmp/moduli_4096.txt')

        # Mock the executor to avoid multiprocessing
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance

        # Mock futures
        mock_future = MagicMock()
        mock_future.result.return_value = Path('/tmp/test_file.txt')
        mock_executor_instance.submit.return_value = mock_future

        generator = ModuliGenerator(mock_config)
        result = generator.generate_moduli()

        assert result == generator  # Method chaining
        assert mock_executor_instance.submit.call_count == 4  # 2 for generation + 2 for screening

    @pytest.mark.integration
    @patch('concurrent.futures.ProcessPoolExecutor')
    @patch('moduli_generator.ModuliGenerator._screen_candidates_static')
    @patch('moduli_generator.ModuliGenerator._generate_candidates_static')
    def test_generate_moduli_generation_failure(self, mock_generate_static, mock_screen_static, mock_executor,
                                                mock_config):
        """Test generate_moduli with candidate generation failure."""
        mock_config.key_lengths = (4096,)

        # Mock the executor to avoid multiprocessing
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance

        # Mock futures to simulate failure
        mock_future = MagicMock()
        mock_future.result.side_effect = Exception("Generation failed")
        mock_executor_instance.submit.return_value = mock_future

        generator = ModuliGenerator(mock_config)

        with pytest.raises(Exception, match="Generation failed"):
            generator.generate_moduli()

    @pytest.mark.integration
    @patch('concurrent.futures.ProcessPoolExecutor')
    @patch('moduli_generator.ModuliGenerator._screen_candidates_static')
    @patch('moduli_generator.ModuliGenerator._generate_candidates_static')
    def test_generate_moduli_screening_failure(self, mock_generate_static, mock_screen_static, mock_executor,
                                               mock_config):
        """Test generate_moduli with candidate screening failure."""
        mock_config.key_lengths = (4096,)

        # Mock the executor to avoid multiprocessing
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance

        # Mock futures - first call succeeds (generation), second fails (screening)
        mock_future_success = MagicMock()
        mock_future_success.result.return_value = Path('/tmp/candidates.txt')
        mock_future_failure = MagicMock()
        mock_future_failure.result.side_effect = Exception("Screening failed")
        mock_executor_instance.submit.side_effect = [mock_future_success, mock_future_failure]

        generator = ModuliGenerator(mock_config)

        with pytest.raises(Exception, match="Screening failed"):
            generator.generate_moduli()

    @pytest.mark.integration
    @patch('db.ConnectionPool')
    @patch('db.parse_mysql_config')
    @patch('moduli_generator.ModuliGenerator._parse_moduli_files')
    @patch('db.MariaDBConnector.export_screened_moduli')
    def test_store_moduli_success(self, mock_export, mock_parse, mock_parse_config, mock_pool, mock_config):
        """Test storing moduli in database successfully."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}
        }
        mock_pool.return_value = MagicMock()
        mock_parse.return_value = {
            "4096": [
                {"timestamp": 20231201000000, "key-size": 4096, "modulus": "test_modulus_1"},
                {"timestamp": 20231201000001, "key-size": 4096, "modulus": "test_modulus_2"}
            ]
        }

        generator = ModuliGenerator(mock_config)
        result = generator.store_moduli()

        assert result == generator  # Method chaining
        mock_parse.assert_called_once()
        mock_export.assert_called_once()

    @pytest.mark.integration
    @patch('db.ConnectionPool')
    @patch('db.parse_mysql_config')
    @patch('moduli_generator.ModuliGenerator._parse_moduli_files')
    def test_store_moduli_no_data(self, mock_parse, mock_parse_config, mock_pool, mock_config):
        """Test storing moduli when no data is available."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}
        }
        mock_pool.return_value = MagicMock()
        mock_parse.return_value = {}

        generator = ModuliGenerator(mock_config)
        result = generator.store_moduli()

        assert result == generator  # Method chaining
        mock_parse.assert_called_once()

    @pytest.mark.integration
    @patch('db.ConnectionPool')
    @patch('db.parse_mysql_config')
    @patch('moduli_generator.dump')
    @patch('pathlib.Path.open', new_callable=mock_open)
    @patch('moduli_generator.ModuliGenerator._parse_moduli_files')
    def test_save_moduli_success(self, mock_parse, mock_file, mock_json_dump, mock_parse_config, mock_pool, mock_config,
                                 temp_dir):
        """Test saving moduli to JSON file successfully."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}
        }
        mock_pool.return_value = MagicMock()
        mock_parse.return_value = [
            (20231201000000, 4096, "test_modulus_1"),
            (20231201000001, 4096, "test_modulus_2")
        ]

        generator = ModuliGenerator(mock_config)
        output_dir = Path(temp_dir)
        result = generator.save_moduli(output_dir)

        assert result == generator  # Method chaining
        mock_parse.assert_called_once()
        mock_json_dump.assert_called_once()

    @pytest.mark.integration
    @patch('db.ConnectionPool')
    @patch('db.parse_mysql_config')
    @patch('db.MariaDBConnector.write_moduli_file')
    def test_write_moduli_file_success(self, mock_write, mock_parse_config, mock_pool, mock_config):
        """Test writing moduli file from database successfully."""
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}
        }
        mock_pool.return_value = MagicMock()
        generator = ModuliGenerator(mock_config)
        result = generator.write_moduli_file()

        assert result == generator  # Method chaining
        mock_write.assert_called_once()


class TestModuliGeneratorErrorHandling:
    """Test cases for error handling in ModuliGenerator."""

    @pytest.mark.integration
    def test_moduli_generator_with_invalid_config(self):
        """Test ModuliGenerator with invalid configuration."""
        # Test with None config should use default
        generator = ModuliGenerator()
        assert generator.config == default_config

    @pytest.mark.integration
    @patch('db.ConnectionPool')
    @patch('db.parse_mysql_config')
    @patch('db.MariaDBConnector.export_screened_moduli')
    @patch('moduli_generator.ModuliGenerator._parse_moduli_files')
    def test_store_moduli_database_error(self, mock_parse, mock_export, mock_parse_config, mock_pool, mock_config):
        """Test store_moduli with database error."""
        from mariadb import Error
        mock_parse_config.return_value = {
            "client": {"user": "testuser", "password": "testpass", "host": "localhost", "port": "3306",
                       "database": "testdb"}
        }
        mock_pool.return_value = MagicMock()
        mock_parse.return_value = {
            "screened_moduli": [{"timestamp": "20231201000000", "key-size": "4096", "modulus": "test_modulus"}]}
        mock_export.side_effect = Error("Database connection failed")

        generator = ModuliGenerator(mock_config)

        # The method catches Error and logs it but doesn't re-raise
        result = generator.store_moduli()
        assert result == generator  # Method chaining should still work

    @pytest.mark.integration
    @patch('pathlib.Path.open')
    @patch('json.dump')
    @patch('moduli_generator.ModuliGenerator._parse_moduli_files')
    def test_save_moduli_directory_creation_error(self, mock_parse, mock_json_dump, mock_open, mock_config, temp_dir):
        """Test save_moduli with file creation error."""
        mock_parse.return_value = [(20231201000000, 4096, "test_modulus")]
        mock_open.side_effect = PermissionError("Permission denied")

        generator = ModuliGenerator(mock_config)
        output_dir = Path(temp_dir) / "nonexistent"

        with pytest.raises(PermissionError):
            generator.save_moduli(output_dir)
