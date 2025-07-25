"""
Integration tests for the CLI functionality.

This module tests the main CLI entry point and complete workflow integration,
including argument processing, error handling, and exit codes.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
from datetime import datetime

from moduli_generator.cli import main
from config import ModuliConfig, default_config
from moduli_generator import ModuliGenerator


class TestCLIMainFunction:
    """Test cases for the main CLI function."""

    @pytest.mark.integration
    @patch('db.ConnectionPool')
    @patch('db.parse_mysql_config')
    @patch('concurrent.futures.ProcessPoolExecutor')
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('config.arg_parser.local_config')
    def test_main_success_with_default_config(self, mock_local_config, mock_generator_class, mock_executor, mock_parse,
                                              mock_pool):
        """Test successful CLI execution with default configuration."""
        # Setup MariaDB mocks
        mock_parse.return_value = {
            'client': {
                'host': 'localhost',
                'port': '3306',
                'user': 'test_user',
                'password': 'test_password',
                'database': 'test_moduli_db'
            }
        }
        mock_pool_instance = MagicMock()
        mock_pool.return_value = mock_pool_instance

        # Setup mocks
        mock_config = MagicMock()
        mock_config.key_lengths = (4096, 8192)
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_local_config.return_value = mock_config

        mock_generator = MagicMock()
        mock_generator.generate_moduli.return_value = mock_generator
        mock_generator.store_moduli.return_value = mock_generator
        mock_generator_class.return_value = mock_generator

        # Execute main function
        result = main()

        # Verify success
        assert result == 0
        mock_local_config.assert_called_once()
        mock_generator_class.assert_called_once_with(mock_config)
        mock_generator.generate_moduli.assert_called_once()
        mock_generator.store_moduli.assert_called_once()

        # Verify logging
        mock_logger.info.assert_called()
        assert mock_logger.info.call_count >= 2  # Start and completion messages

    @pytest.mark.integration
    @patch('moduli_generator.cli.ModuliGenerator')
    def test_main_success_with_provided_config(self, mock_generator_class, mock_config):
        """Test successful CLI execution with provided configuration."""
        # Setup mocks
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_config.key_lengths = (4096,)

        mock_generator = MagicMock()
        mock_generator.generate_moduli.return_value = mock_generator
        mock_generator.store_moduli.return_value = mock_generator
        mock_generator_class.return_value = mock_generator

        # Execute main function with provided config
        result = main(mock_config)

        # Verify success
        assert result == 0
        mock_generator_class.assert_called_once_with(mock_config)
        mock_generator.generate_moduli.assert_called_once()
        mock_generator.store_moduli.assert_called_once()

        # Verify logging setup
        mock_logger.info.assert_called()
        assert mock_logger.name == 'moduli_generator.cli'

    @pytest.mark.integration
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('config.arg_parser.local_config')
    def test_main_value_error_handling(self, mock_local_config, mock_generator_class):
        """Test CLI handling of ValueError exceptions."""
        # Setup mocks
        mock_config = MagicMock()
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_local_config.return_value = mock_config

        mock_generator = MagicMock()
        mock_generator.generate_moduli.side_effect = ValueError("Invalid key length")
        mock_generator_class.return_value = mock_generator

        # Execute main function
        result = main()

        # Verify error handling
        assert result == 1
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Moduli Generation Failed: Invalid key length" in error_call

    @pytest.mark.integration
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('config.arg_parser.local_config')
    def test_main_general_exception_handling(self, mock_local_config, mock_generator_class):
        """Test CLI handling of general exceptions."""
        # Setup mocks
        mock_config = MagicMock()
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_local_config.return_value = mock_config

        mock_generator = MagicMock()
        mock_generator.generate_moduli.side_effect = RuntimeError("Database connection failed")
        mock_generator_class.return_value = mock_generator

        # Execute main function
        result = main()

        # Verify error handling
        assert result == 2
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Moduli Generation Failed: Database connection failed" in error_call

    @pytest.mark.integration
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('config.arg_parser.local_config')
    def test_main_store_moduli_value_error(self, mock_local_config, mock_generator_class):
        """Test CLI handling of ValueError in store_moduli step."""
        # Setup mocks
        mock_config = MagicMock()
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_local_config.return_value = mock_config

        mock_generator = MagicMock()
        mock_generator.generate_moduli.return_value = mock_generator
        mock_generator.store_moduli.side_effect = ValueError("Database validation failed")
        mock_generator_class.return_value = mock_generator

        # Execute main function
        result = main()

        # Verify error handling
        assert result == 1
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Moduli Generation Failed: Database validation failed" in error_call

    @pytest.mark.integration
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('config.arg_parser.local_config')
    def test_main_store_moduli_general_error(self, mock_local_config, mock_generator_class):
        """Test CLI handling of general exception in store_moduli step."""
        # Setup mocks
        mock_config = MagicMock()
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_local_config.return_value = mock_config

        mock_generator = MagicMock()
        mock_generator.generate_moduli.return_value = mock_generator
        mock_generator.store_moduli.side_effect = IOError("File system error")
        mock_generator_class.return_value = mock_generator

        # Execute main function
        result = main()

        # Verify error handling
        assert result == 2
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Moduli Generation Failed: File system error" in error_call


class TestCLILoggingAndTiming:
    """Test cases for CLI logging and timing functionality."""

    @pytest.mark.integration
    @patch('datetime.datetime')
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('config.arg_parser.local_config')
    def test_main_timing_and_logging(self, mock_local_config, mock_generator_class, mock_datetime):
        """Test CLI timing and logging functionality."""
        # Setup datetime mocks
        start_time = datetime(2023, 12, 1, 10, 0, 0)
        end_time = datetime(2023, 12, 1, 10, 5, 30)  # 5 minutes 30 seconds later
        mock_datetime.now.side_effect = [start_time, end_time]

        # Setup other mocks
        mock_config = MagicMock()
        mock_config.key_lengths = (4096, 8192)
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_local_config.return_value = mock_config

        mock_generator = MagicMock()
        mock_generator.generate_moduli.return_value = mock_generator
        mock_generator.store_moduli.return_value = mock_generator
        mock_generator_class.return_value = mock_generator

        # Execute main function
        result = main()

        # Verify success
        assert result == 0

        # Verify timing logs
        info_calls = [call[0][0] for call in mock_logger.info.call_args_list]

        # Check start message
        start_message = next((msg for msg in info_calls if "Starting Moduli Generation" in msg), None)
        assert start_message is not None
        assert "(4096, 8192)" in start_message

        # Check completion messages
        completion_messages = [msg for msg in info_calls if "Complete" in msg]
        assert len(completion_messages) >= 1

    @pytest.mark.integration
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('config.arg_parser.local_config')
    def test_main_logger_name_assignment(self, mock_local_config, mock_generator_class):
        """Test that logger name is properly assigned."""
        # Setup mocks
        mock_config = MagicMock()
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_local_config.return_value = mock_config

        mock_generator = MagicMock()
        mock_generator.generate_moduli.return_value = mock_generator
        mock_generator.store_moduli.return_value = mock_generator
        mock_generator_class.return_value = mock_generator

        # Execute main function
        result = main()

        # Verify logger name assignment
        assert result == 0
        assert mock_logger.name == 'moduli_generator.cli'

    @pytest.mark.integration
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('config.arg_parser.local_config')
    def test_main_debug_logging(self, mock_local_config, mock_generator_class):
        """Test debug logging functionality."""
        # Setup mocks
        mock_config = MagicMock()
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_local_config.return_value = mock_config

        mock_generator = MagicMock()
        mock_generator.generate_moduli.return_value = mock_generator
        mock_generator.store_moduli.return_value = mock_generator
        mock_generator_class.return_value = mock_generator

        # Execute main function
        result = main()

        # Verify debug logging
        assert result == 0
        mock_logger.debug.assert_called_once()
        debug_call = mock_logger.debug.call_args[0][0]
        assert "Using default config:" in debug_call


class TestCLIMethodChaining:
    """Test cases for CLI method chaining functionality."""

    @pytest.mark.integration
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('config.arg_parser.local_config')
    def test_main_method_chaining_success(self, mock_local_config, mock_generator_class):
        """Test successful method chaining in CLI."""
        # Setup mocks
        mock_config = MagicMock()
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_local_config.return_value = mock_config

        mock_generator = MagicMock()
        mock_generator.generate_moduli.return_value = mock_generator
        mock_generator.store_moduli.return_value = mock_generator
        mock_generator_class.return_value = mock_generator

        # Execute main function
        result = main()

        # Verify method chaining
        assert result == 0
        mock_generator.generate_moduli.assert_called_once()
        mock_generator.store_moduli.assert_called_once()

        # Verify the chaining pattern
        mock_generator.generate_moduli.return_value.store_moduli.assert_called_once()

    @pytest.mark.integration
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('config.arg_parser.local_config')
    def test_main_method_chaining_break_on_generate_error(self, mock_local_config, mock_generator_class):
        """Test method chaining breaks on generate_moduli error."""
        # Setup mocks
        mock_config = MagicMock()
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_local_config.return_value = mock_config

        mock_generator = MagicMock()
        mock_generator.generate_moduli.side_effect = ValueError("Generation failed")
        mock_generator_class.return_value = mock_generator

        # Execute main function
        result = main()

        # Verify method chaining breaks
        assert result == 1
        mock_generator.generate_moduli.assert_called_once()
        mock_generator.store_moduli.assert_not_called()


class TestCLIConfigurationHandling:
    """Test cases for CLI configuration handling."""

    @pytest.mark.integration
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('config.arg_parser.local_config')
    def test_main_with_none_config_uses_default(self, mock_local_config, mock_generator_class):
        """Test that None config triggers default config loading."""
        # Setup mocks
        mock_config = MagicMock()
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_local_config.return_value = mock_config

        mock_generator = MagicMock()
        mock_generator.generate_moduli.return_value = mock_generator
        mock_generator.store_moduli.return_value = mock_generator
        mock_generator_class.return_value = mock_generator

        # Execute main function with None config
        result = main(None)

        # Verify default config loading
        assert result == 0
        mock_local_config.assert_called_once()
        mock_generator_class.assert_called_once_with(mock_config)

    @pytest.mark.integration
    @patch('moduli_generator.cli.ModuliGenerator')
    def test_main_with_provided_config_skips_loading(self, mock_generator_class, mock_config):
        """Test that provided config skips default config loading."""
        # Setup mocks
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger

        mock_generator = MagicMock()
        mock_generator.generate_moduli.return_value = mock_generator
        mock_generator.store_moduli.return_value = mock_generator
        mock_generator_class.return_value = mock_generator

        # Execute main function with provided config
        with patch('config.arg_parser.local_config') as mock_local_config:
            result = main(mock_config)

            # Verify config loading is skipped
            assert result == 0
            mock_local_config.assert_not_called()
            mock_generator_class.assert_called_once_with(mock_config)

    @pytest.mark.integration
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('config.arg_parser.local_config')
    def test_main_config_key_lengths_logging(self, mock_local_config, mock_generator_class):
        """Test that config key lengths are logged properly."""
        # Setup mocks with specific key lengths
        mock_config = MagicMock()
        mock_config.key_lengths = (3072, 4096, 8192)
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_local_config.return_value = mock_config

        mock_generator = MagicMock()
        mock_generator.generate_moduli.return_value = mock_generator
        mock_generator.store_moduli.return_value = mock_generator
        mock_generator_class.return_value = mock_generator

        # Execute main function
        result = main()

        # Verify key lengths are logged
        assert result == 0
        info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        start_message = next((msg for msg in info_calls if "Starting Moduli Generation" in msg), None)
        assert start_message is not None
        assert "(3072, 4096, 8192)" in start_message


class TestCLIMainEntryPoint:
    """Test cases for the CLI main entry point."""

    @pytest.mark.integration
    @patch('sys.exit')
    @patch('moduli_generator.cli.main')
    def test_main_entry_point_success(self, mock_main_func, mock_exit):
        """Test the __main__ entry point with successful execution."""
        mock_main_func.return_value = 0

        # Simulate the __main__ entry point behavior
        from sys import exit
        from moduli_generator.cli import main
        exit(main())

        mock_main_func.assert_called_once()
        mock_exit.assert_called_once_with(0)

    @pytest.mark.integration
    @patch('sys.exit')
    @patch('moduli_generator.cli.main')
    def test_main_entry_point_error(self, mock_main_func, mock_exit):
        """Test the __main__ entry point with error."""
        mock_main_func.return_value = 1

        # Simulate the __main__ entry point behavior
        from sys import exit
        from moduli_generator.cli import main
        exit(main())

        mock_main_func.assert_called_once()
        mock_exit.assert_called_once_with(1)


class TestCLIIntegrationScenarios:
    """Test cases for complete CLI integration scenarios."""

    @pytest.mark.integration
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('config.arg_parser.local_config')
    def test_complete_workflow_integration(self, mock_local_config, mock_generator_class):
        """Test complete CLI workflow integration."""
        # Setup realistic configuration
        mock_config = MagicMock()
        mock_config.key_lengths = (4096, 8192)
        mock_config.nice_value = 10
        mock_config.candidates_dir = "/tmp/candidates"
        mock_config.moduli_dir = "/tmp/moduli"
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_local_config.return_value = mock_config

        # Setup generator with realistic behavior
        mock_generator = MagicMock()
        mock_generator.generate_moduli.return_value = mock_generator
        mock_generator.store_moduli.return_value = mock_generator
        mock_generator_class.return_value = mock_generator

        # Execute complete workflow
        result = main()

        # Verify complete workflow
        assert result == 0

        # Verify configuration loading
        mock_local_config.assert_called_once()

        # Verify generator instantiation
        mock_generator_class.assert_called_once_with(mock_config)

        # Verify workflow execution
        mock_generator.generate_moduli.assert_called_once()
        mock_generator.store_moduli.assert_called_once()

        # Verify logging
        assert mock_logger.info.call_count >= 3  # Start, completion, and final messages
        assert mock_logger.debug.call_count >= 1  # Config debug message

    @pytest.mark.integration
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('config.arg_parser.local_config')
    def test_cli_error_recovery_scenarios(self, mock_local_config, mock_generator_class):
        """Test CLI error recovery scenarios."""
        # Setup mocks
        mock_config = MagicMock()
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_local_config.return_value = mock_config

        # Test different error scenarios
        error_scenarios = [
            (ValueError("Invalid parameters"), 1),
            (RuntimeError("System error"), 2),
            (IOError("File access error"), 2),
            (Exception("Unknown error"), 2)
        ]

        for error, expected_code in error_scenarios:
            mock_generator = MagicMock()
            mock_generator.generate_moduli.side_effect = error
            mock_generator_class.return_value = mock_generator

            result = main()

            assert result == expected_code
            mock_logger.error.assert_called()

            # Reset mocks for next iteration
            mock_logger.reset_mock()
            mock_generator_class.reset_mock()

    @pytest.mark.integration
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('config.arg_parser.local_config')
    def test_cli_performance_logging(self, mock_local_config, mock_generator_class):
        """Test CLI performance and timing logging."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.key_lengths = (4096,)
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_local_config.return_value = mock_config

        mock_generator = MagicMock()
        mock_generator.generate_moduli.return_value = mock_generator
        mock_generator.store_moduli.return_value = mock_generator
        mock_generator_class.return_value = mock_generator

        # Execute with timing
        with patch('datetime.datetime') as mock_datetime:
            start_time = datetime(2023, 12, 1, 10, 0, 0)
            end_time = datetime(2023, 12, 1, 10, 2, 30)  # 2.5 minutes later
            mock_datetime.now.side_effect = [start_time, end_time]

            result = main()

        # Verify performance logging
        assert result == 0
        info_calls = [call[0][0] for call in mock_logger.info.call_args_list]

        # Check for timing information
        timing_messages = [msg for msg in info_calls if "Time taken" in msg]
        assert len(timing_messages) >= 1
