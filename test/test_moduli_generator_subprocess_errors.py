"""
Tests to cover subprocess error handling paths in moduli_generator module.
These tests target specific missing lines identified in coverage analysis.
"""

import pytest
from unittest.mock import patch, MagicMock
import subprocess
from pathlib import Path
import tempfile
import os

from moduli_generator import ModuliGenerator
from moduli_generator.validators import validate_subprocess_args
from config import ModuliConfig


class TestModuliGeneratorSubprocessErrors:
    """Tests to cover subprocess error handling paths in moduli_generator module."""

    @pytest.fixture
    def valid_mock_config(self):
        """Create a mock config for testing."""
        config = MagicMock(spec=ModuliConfig)
        config.key_lengths = [4096]
        config.records_per_keylength = 10
        config.base_dir = "/tmp"
        config.moduli_file_pfx = "moduli"
        config.moduli_file = "moduli.txt"
        config.nice_value = 10
        config.generator_type = 2
        config.candidates_dir = Path("/tmp/candidates")
        config.moduli_dir = Path("/tmp/moduli")
        config.log_dir = Path("/tmp/logs")
        config.mariadb_cnf = Path("/tmp/mariadb.cnf")
        config.version = "2.1.22"
        config.get_logger.return_value = MagicMock()
        return config

    @pytest.mark.unit
    @patch('subprocess.run')
    def test_generate_candidates_static_subprocess_error(self, mock_run, valid_mock_config):
        """Test _generate_candidates_static with subprocess error - covers lines 186-191."""
        # Mock subprocess.run to raise CalledProcessError
        error = subprocess.CalledProcessError(
            returncode=1,
            cmd=['ssh-keygen', '-G'],
            stderr="ssh-keygen error output"
        )
        mock_run.side_effect = error

        key_length = 4096

        with pytest.raises(subprocess.CalledProcessError):
            ModuliGenerator._generate_candidates_static(valid_mock_config, key_length)

        # Verify error logging
        logger = valid_mock_config.get_logger.return_value
        logger.error.assert_called()
        # Check that the error message contains expected content
        error_calls = [call[0][0] for call in logger.error.call_args_list]
        assert any("ssh-keygen generate failed" in call for call in error_calls)
        assert any("ssh-keygen stderr" in call for call in error_calls)

    @pytest.mark.unit
    @patch('subprocess.run')
    def test_generate_candidates_static_subprocess_error_no_stderr(self, mock_run, valid_mock_config):
        """Test _generate_candidates_static with subprocess error without stderr."""
        # Mock subprocess.run to raise CalledProcessError without stderr
        error = subprocess.CalledProcessError(
            returncode=1,
            cmd=['ssh-keygen', '-G'],
            stderr=None
        )
        mock_run.side_effect = error

        key_length = 4096

        with pytest.raises(subprocess.CalledProcessError):
            ModuliGenerator._generate_candidates_static(valid_mock_config, key_length)

        # Verify error logging (should not log stderr since it's None)
        logger = valid_mock_config.get_logger.return_value
        logger.error.assert_called()
        error_calls = [call[0][0] for call in logger.error.call_args_list]
        assert any("ssh-keygen generate failed" in call for call in error_calls)
        # Should not have stderr logging
        assert not any("ssh-keygen stderr" in call for call in error_calls)

    @pytest.mark.unit
    @patch('subprocess.run')
    def test_screen_candidates_static_subprocess_error(self, mock_run, valid_mock_config):
        """Test _screen_candidates_static with subprocess error - covers lines 238-243."""
        # Mock subprocess.run to raise CalledProcessError
        error = subprocess.CalledProcessError(
            returncode=1,
            cmd=['ssh-keygen', '-T'],
            stderr="ssh-keygen screening error"
        )
        mock_run.side_effect = error

        candidates_file = Path("/tmp/test_candidates")

        with pytest.raises(subprocess.CalledProcessError):
            ModuliGenerator._screen_candidates_static(valid_mock_config, candidates_file)

        # Verify error logging
        logger = valid_mock_config.get_logger.return_value
        logger.error.assert_called()
        error_calls = [call[0][0] for call in logger.error.call_args_list]
        assert any("ssh-keygen screen failed" in call for call in error_calls)
        assert any("ssh-keygen stderr" in call for call in error_calls)

    @pytest.mark.unit
    @patch('subprocess.run')
    def test_screen_candidates_static_subprocess_error_no_stderr(self, mock_run, valid_mock_config):
        """Test _screen_candidates_static with subprocess error without stderr."""
        # Mock subprocess.run to raise CalledProcessError without stderr
        error = subprocess.CalledProcessError(
            returncode=1,
            cmd=['ssh-keygen', '-T'],
            stderr=""
        )
        mock_run.side_effect = error

        candidates_file = Path("/tmp/test_candidates")

        with pytest.raises(subprocess.CalledProcessError):
            ModuliGenerator._screen_candidates_static(valid_mock_config, candidates_file)

        # Verify error logging (should not log stderr since it's empty)
        logger = valid_mock_config.get_logger.return_value
        logger.error.assert_called()
        error_calls = [call[0][0] for call in logger.error.call_args_list]
        assert any("ssh-keygen screen failed" in call for call in error_calls)
        # Should not have stderr logging for empty stderr
        assert not any("ssh-keygen stderr" in call for call in error_calls)

    @pytest.mark.unit
    @patch('concurrent.futures.ProcessPoolExecutor')
    @patch('moduli_generator.ModuliGenerator._generate_candidates_static')
    def test_moduli_generator_generate_moduli_subprocess_error(self, mock_generate_static, mock_executor,
                                                               valid_mock_config):
        """Test ModuliGenerator.generate_moduli with subprocess error - covers lines 268-270."""
        # Mock ProcessPoolExecutor to avoid multiprocessing
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance

        # Mock _generate_candidates_static to raise CalledProcessError
        error = subprocess.CalledProcessError(
            returncode=1,
            cmd=['ssh-keygen', '-G']
        )
        mock_generate_static.side_effect = error

        # Mock submit to call the actual static method and return a future
        def mock_submit(func, *args):
            mock_future = MagicMock()
            try:
                # Call the actual mocked function to trigger the side_effect
                result = func(*args)
                mock_future.result.return_value = result
            except Exception as e:
                mock_future.result.side_effect = e
            return mock_future

        mock_executor_instance.submit.side_effect = mock_submit

        generator = ModuliGenerator(valid_mock_config)

        with pytest.raises(subprocess.CalledProcessError):
            generator.generate_moduli()

        # Verify the static method was called
        mock_generate_static.assert_called()

    @pytest.mark.unit
    @patch('concurrent.futures.ProcessPoolExecutor')
    @patch('moduli_generator.ModuliGenerator._screen_candidates_static')
    @patch('moduli_generator.ModuliGenerator._generate_candidates_static')
    def test_moduli_generator_screen_subprocess_error(self, mock_generate_static, mock_screen_static, mock_executor,
                                                      valid_mock_config):
        """Test ModuliGenerator screening subprocess error - covers line 291."""
        # Mock ProcessPoolExecutor to avoid multiprocessing
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance

        # Mock _generate_candidates_static to succeed
        mock_generate_static.return_value = Path("/tmp/test_candidates")

        # Mock _screen_candidates_static to raise CalledProcessError
        error = subprocess.CalledProcessError(
            returncode=1,
            cmd=['ssh-keygen', '-T']
        )
        mock_screen_static.side_effect = error

        # Mock submit to return different futures for generate and screen
        def mock_submit(func, *args):
            mock_future = MagicMock()
            if func == mock_generate_static:
                mock_future.result.return_value = Path("/tmp/test_candidates")
            else:  # screen function
                mock_future.result.side_effect = error
            return mock_future

        mock_executor_instance.submit.side_effect = mock_submit

        generator = ModuliGenerator(valid_mock_config)

        with pytest.raises(subprocess.CalledProcessError):
            generator.generate_moduli()

    @pytest.mark.integration
    @patch('concurrent.futures.ProcessPoolExecutor')
    @patch('moduli_generator.ModuliGenerator._generate_candidates_static')
    def test_moduli_generator_full_subprocess_error_flow(self, mock_generate_static, mock_executor, valid_mock_config):
        """Test full ModuliGenerator flow with subprocess errors."""
        # Mock ProcessPoolExecutor to avoid multiprocessing
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance

        # Mock _generate_candidates_static to raise CalledProcessError
        error = subprocess.CalledProcessError(
            returncode=1,
            cmd=['ssh-keygen', '-G'],
            stderr="Generation failed"
        )
        mock_generate_static.side_effect = error

        # Mock submit to call the actual static method and return a future
        def mock_submit(func, *args):
            mock_future = MagicMock()
            try:
                # Call the actual mocked function to trigger the side_effect
                result = func(*args)
                mock_future.result.return_value = result
            except Exception as e:
                mock_future.result.side_effect = e
            return mock_future

        mock_executor_instance.submit.side_effect = mock_submit

        generator = ModuliGenerator(valid_mock_config)

        with pytest.raises(subprocess.CalledProcessError):
            generator.generate_moduli()

        # Verify the static method was called
        mock_generate_static.assert_called()

    @pytest.mark.unit
    def test_subprocess_error_attributes(self):
        """Test that subprocess errors have expected attributes."""
        # Test CalledProcessError with stderr
        error_with_stderr = subprocess.CalledProcessError(
            returncode=1,
            cmd=['ssh-keygen'],
            stderr="Error message"
        )
        assert error_with_stderr.stderr == "Error message"
        assert error_with_stderr.returncode == 1

        # Test CalledProcessError without stderr
        error_without_stderr = subprocess.CalledProcessError(
            returncode=2,
            cmd=['ssh-keygen']
        )
        assert error_without_stderr.stderr is None
        assert error_without_stderr.returncode == 2

    @pytest.mark.unit
    @patch('subprocess.run')
    def test_generate_candidates_error_logging_details(self, mock_run, valid_mock_config):
        """Test detailed error logging in _generate_candidates_static."""
        # Mock subprocess.run to raise CalledProcessError with detailed stderr
        error = subprocess.CalledProcessError(
            returncode=1,
            cmd=['ssh-keygen', '-G', '/tmp/candidates', '4096'],
            stderr="Detailed error: Invalid key length specified"
        )
        mock_run.side_effect = error

        key_length = 4096

        with pytest.raises(subprocess.CalledProcessError):
            ModuliGenerator._generate_candidates_static(valid_mock_config, key_length)

        # Verify specific error message format
        logger = valid_mock_config.get_logger.return_value
        logger.error.assert_called()
        error_calls = logger.error.call_args_list

        # Should have at least 2 calls: main error and stderr
        assert len(error_calls) >= 2

        # Check main error message
        main_error = error_calls[0][0][0]
        assert "ssh-keygen generate failed for 4096 bits" in main_error

        # Check stderr message
        stderr_error = error_calls[1][0][0]
        assert "ssh-keygen stderr:" in stderr_error
        assert "Detailed error: Invalid key length specified" in stderr_error
