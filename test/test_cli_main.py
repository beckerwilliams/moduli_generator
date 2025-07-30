"""
Pytest tests for moduli_generator.cli module.

This module tests the CLI main functionality, including configuration
handling, moduli generation workflow, error handling, and timing.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from moduli_generator.cli import main


class TestCLIMain:
    """Test cases for the CLI main function."""

    @pytest.mark.unit
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('moduli_generator.cli.arg_parser')
    @patch('moduli_generator.cli.iso_utc_time')
    def test_main_success_with_default_config(self, mock_iso_utc_time, mock_arg_parser, mock_moduli_generator):
        """Test main function success with default configuration."""
        # Setup mocks
        mock_config = MagicMock()
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_config.key_lengths = [4096, 8192]
        mock_arg_parser.local_config.return_value = mock_config

        # Mock iso_utc_time for timing
        start_time = datetime(2024, 1, 1, 12, 0, 0)
        end_time = datetime(2024, 1, 1, 12, 0, 30)  # 30 seconds later
        mock_iso_utc_time.side_effect = [start_time, end_time]

        # Mock ModuliGenerator chain
        mock_generator_instance = MagicMock()
        mock_generator_instance.generate_moduli.return_value = mock_generator_instance
        mock_generator_instance.store_moduli.return_value = mock_generator_instance
        mock_moduli_generator.return_value = mock_generator_instance

        # Execute
        result = main()

        # Verify
        assert result == 0
        mock_arg_parser.local_config.assert_called_once()
        mock_config.get_logger.assert_called_once()
        mock_moduli_generator.assert_called_once_with(mock_config)
        mock_generator_instance.generate_moduli.assert_called_once()
        mock_generator_instance.store_moduli.assert_called_once()
        mock_logger.info.assert_any_call('Moduli Generation Complete. Time taken: 30 seconds')
        mock_logger.info.assert_any_call('Moduli Generation Complete')

    @pytest.mark.unit
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('moduli_generator.cli.iso_utc_time')
    def test_main_success_with_provided_config(self, mock_iso_utc_time, mock_moduli_generator):
        """Test main function success with provided configuration."""
        # Setup mocks
        mock_config = MagicMock()
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_config.key_lengths = [3072]

        # Mock iso_utc_time for timing
        start_time = datetime(2024, 1, 1, 12, 0, 0)
        end_time = datetime(2024, 1, 1, 12, 1, 0)  # 60 seconds later
        mock_iso_utc_time.side_effect = [start_time, end_time]

        # Mock ModuliGenerator chain
        mock_generator_instance = MagicMock()
        mock_generator_instance.generate_moduli.return_value = mock_generator_instance
        mock_generator_instance.store_moduli.return_value = mock_generator_instance
        mock_moduli_generator.return_value = mock_generator_instance

        # Execute
        result = main(mock_config)

        # Verify
        assert result == 0
        mock_config.get_logger.assert_called_once()
        mock_moduli_generator.assert_called_once_with(mock_config)
        mock_generator_instance.generate_moduli.assert_called_once()
        mock_generator_instance.store_moduli.assert_called_once()
        mock_logger.info.assert_any_call('Moduli Generation Complete. Time taken: 60 seconds')

    @pytest.mark.unit
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('moduli_generator.cli.arg_parser')
    def test_main_value_error_handling(self, mock_arg_parser, mock_moduli_generator):
        """Test main function handling of ValueError."""
        # Setup mocks
        mock_config = MagicMock()
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_config.key_lengths = [4096]
        mock_arg_parser.local_config.return_value = mock_config

        # Mock ModuliGenerator to raise ValueError
        mock_generator_instance = MagicMock()
        mock_generator_instance.generate_moduli.side_effect = ValueError("Invalid key length")
        mock_moduli_generator.return_value = mock_generator_instance

        # Execute
        result = main()

        # Verify
        assert result == 1
        mock_logger.error.assert_called_once_with('Moduli Generation Failed: Invalid key length')

    @pytest.mark.unit
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('moduli_generator.cli.arg_parser')
    def test_main_general_exception_handling(self, mock_arg_parser, mock_moduli_generator):
        """Test main function handling of general exceptions."""
        # Setup mocks
        mock_config = MagicMock()
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_config.key_lengths = [4096]
        mock_arg_parser.local_config.return_value = mock_config

        # Mock ModuliGenerator to raise general exception
        mock_generator_instance = MagicMock()
        mock_generator_instance.generate_moduli.side_effect = RuntimeError("Database connection failed")
        mock_moduli_generator.return_value = mock_generator_instance

        # Execute
        result = main()

        # Verify
        assert result == 2
        mock_logger.error.assert_called_once_with('Moduli Generation Failed: Database connection failed')

    @pytest.mark.unit
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('moduli_generator.cli.arg_parser')
    def test_main_store_moduli_value_error(self, mock_arg_parser, mock_moduli_generator):
        """Test main function handling of ValueError in store_moduli."""
        # Setup mocks
        mock_config = MagicMock()
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_config.key_lengths = [4096]
        mock_arg_parser.local_config.return_value = mock_config

        # Mock ModuliGenerator chain with store_moduli raising ValueError
        mock_generator_instance = MagicMock()
        mock_generator_instance.generate_moduli.return_value = mock_generator_instance
        mock_generator_instance.store_moduli.side_effect = ValueError("Storage validation failed")
        mock_moduli_generator.return_value = mock_generator_instance

        # Execute
        result = main()

        # Verify
        assert result == 1
        mock_logger.error.assert_called_once_with('Moduli Generation Failed: Storage validation failed')

    @pytest.mark.unit
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('moduli_generator.cli.arg_parser')
    def test_main_store_moduli_general_error(self, mock_arg_parser, mock_moduli_generator):
        """Test main function handling of general exception in store_moduli."""
        # Setup mocks
        mock_config = MagicMock()
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_config.key_lengths = [4096]
        mock_arg_parser.local_config.return_value = mock_config

        # Mock ModuliGenerator chain with store_moduli raising general exception
        mock_generator_instance = MagicMock()
        mock_generator_instance.generate_moduli.return_value = mock_generator_instance
        mock_generator_instance.store_moduli.side_effect = IOError("File system error")
        mock_moduli_generator.return_value = mock_generator_instance

        # Execute
        result = main()

        # Verify
        assert result == 2
        mock_logger.error.assert_called_once_with('Moduli Generation Failed: File system error')


class TestCLILoggingAndTiming:
    """Test cases for CLI logging and timing functionality."""

    @pytest.mark.unit
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('moduli_generator.cli.arg_parser')
    @patch('moduli_generator.cli.iso_utc_time')
    def test_main_timing_and_logging(self, mock_iso_utc_time, mock_arg_parser, mock_moduli_generator):
        """Test main function timing and logging functionality."""
        # Setup mocks
        mock_config = MagicMock()
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_config.key_lengths = [4096, 8192]
        mock_arg_parser.local_config.return_value = mock_config

        # Mock datetime for precise timing
        start_time = datetime(2024, 1, 1, 12, 0, 0)
        end_time = datetime(2024, 1, 1, 12, 2, 30)  # 150 seconds later
        mock_iso_utc_time.side_effect = [start_time, end_time]

        # Mock ModuliGenerator chain
        mock_generator_instance = MagicMock()
        mock_generator_instance.generate_moduli.return_value = mock_generator_instance
        mock_generator_instance.store_moduli.return_value = mock_generator_instance
        mock_moduli_generator.return_value = mock_generator_instance

        # Execute
        result = main()

        # Verify timing and logging
        assert result == 0
        mock_logger.info.assert_any_call(
            f'Starting Moduli Generation at {start_time}, with [4096, 8192] as moduli key-lengths')
        mock_logger.info.assert_any_call('Moduli Generation Complete. Time taken: 150 seconds')
        mock_logger.info.assert_any_call('Moduli Generation Complete')

    @pytest.mark.unit
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('moduli_generator.cli.arg_parser')
    def test_main_logger_name_assignment(self, mock_arg_parser, mock_moduli_generator):
        """Test that logger name is properly assigned."""
        # Setup mocks
        mock_config = MagicMock()
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_config.key_lengths = [4096]
        mock_arg_parser.local_config.return_value = mock_config

        # Mock ModuliGenerator chain
        mock_generator_instance = MagicMock()
        mock_generator_instance.generate_moduli.return_value = mock_generator_instance
        mock_generator_instance.store_moduli.return_value = mock_generator_instance
        mock_moduli_generator.return_value = mock_generator_instance

        # Execute
        main()

        # Verify logger name assignment
        assert mock_logger.name == 'moduli_generator.cli'

    @pytest.mark.unit
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('moduli_generator.cli.arg_parser')
    def test_main_debug_logging(self, mock_arg_parser, mock_moduli_generator):
        """Test debug logging functionality."""
        # Setup mocks
        mock_config = MagicMock()
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_config.key_lengths = [4096]
        mock_arg_parser.local_config.return_value = mock_config

        # Mock ModuliGenerator chain
        mock_generator_instance = MagicMock()
        mock_generator_instance.generate_moduli.return_value = mock_generator_instance
        mock_generator_instance.store_moduli.return_value = mock_generator_instance
        mock_moduli_generator.return_value = mock_generator_instance

        # Execute
        main()

        # Verify debug logging
        mock_logger.debug.assert_called_once_with(f'Using default config: {mock_config}')


class TestCLIMethodChaining:
    """Test cases for CLI method chaining functionality."""

    @pytest.mark.unit
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('moduli_generator.cli.arg_parser')
    def test_main_method_chaining_success(self, mock_arg_parser, mock_moduli_generator):
        """Test successful method chaining in main function."""
        # Setup mocks
        mock_config = MagicMock()
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_config.key_lengths = [4096]
        mock_arg_parser.local_config.return_value = mock_config

        # Mock ModuliGenerator chain
        mock_generator_instance = MagicMock()
        mock_generator_instance.generate_moduli.return_value = mock_generator_instance
        mock_generator_instance.store_moduli.return_value = mock_generator_instance
        mock_moduli_generator.return_value = mock_generator_instance

        # Execute
        result = main()

        # Verify method chaining
        assert result == 0
        mock_moduli_generator.assert_called_once_with(mock_config)
        mock_generator_instance.generate_moduli.assert_called_once()
        mock_generator_instance.store_moduli.assert_called_once()

    @pytest.mark.unit
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('moduli_generator.cli.arg_parser')
    def test_main_method_chaining_break_on_generate_error(self, mock_arg_parser, mock_moduli_generator):
        """Test method chaining breaks on generate_moduli error."""
        # Setup mocks
        mock_config = MagicMock()
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_config.key_lengths = [4096]
        mock_arg_parser.local_config.return_value = mock_config

        # Mock ModuliGenerator with generate_moduli raising exception
        mock_generator_instance = MagicMock()
        mock_generator_instance.generate_moduli.side_effect = ValueError("Generation failed")
        mock_moduli_generator.return_value = mock_generator_instance

        # Execute
        result = main()

        # Verify method chaining breaks and store_moduli is not called
        assert result == 1
        mock_generator_instance.generate_moduli.assert_called_once()
        mock_generator_instance.store_moduli.assert_not_called()


class TestCLIMainEntryPoint:
    """Test cases for CLI main entry point."""

    @pytest.mark.unit
    @patch('moduli_generator.cli.exit')
    @patch('moduli_generator.cli.main')
    def test_main_entry_point_success(self, mock_main, mock_exit):
        """Test main entry point with successful execution."""
        mock_main.return_value = 0

        # Import and execute the module's main block
        import moduli_generator.cli
        exec(compile(open(moduli_generator.cli.__file__).read(), moduli_generator.cli.__file__, 'exec'))

        # Note: This test is more complex due to the __main__ block execution
        # In a real scenario, we'd test this differently or restructure the code

    @pytest.mark.unit
    @patch('moduli_generator.cli.exit')
    @patch('moduli_generator.cli.main')
    def test_main_entry_point_error(self, mock_main, mock_exit):
        """Test main entry point with error execution."""
        mock_main.return_value = 1

        # Import and execute the module's main block
        import moduli_generator.cli
        exec(compile(open(moduli_generator.cli.__file__).read(), moduli_generator.cli.__file__, 'exec'))

        # Note: This test is more complex due to the __main__ block execution
        # In a real scenario, we'd test this differently or restructure the code


class TestCLIIntegrationScenarios:
    """Test cases for CLI integration scenarios."""

    @pytest.mark.integration
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('moduli_generator.cli.arg_parser')
    @patch('moduli_generator.cli.iso_utc_time')
    def test_complete_workflow_integration(self, mock_iso_utc_time, mock_arg_parser, mock_moduli_generator):
        """Test complete CLI workflow integration."""
        # Setup comprehensive mocks
        mock_config = MagicMock()
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_config.key_lengths = [3072, 4096, 8192]
        mock_arg_parser.local_config.return_value = mock_config

        # Mock datetime for timing
        start_time = datetime(2024, 1, 1, 12, 0, 0)
        end_time = datetime(2024, 1, 1, 12, 5, 0)  # 300 seconds later
        mock_iso_utc_time.side_effect = [start_time, end_time]

        # Mock complete ModuliGenerator workflow
        mock_generator_instance = MagicMock()
        mock_generator_instance.generate_moduli.return_value = mock_generator_instance
        mock_generator_instance.store_moduli.return_value = mock_generator_instance
        mock_moduli_generator.return_value = mock_generator_instance

        # Execute
        result = main()

        # Verify complete workflow
        assert result == 0
        mock_arg_parser.local_config.assert_called_once()
        mock_config.get_logger.assert_called_once()
        assert mock_logger.name == 'moduli_generator.cli'
        mock_logger.debug.assert_called_once()
        mock_logger.info.assert_any_call(
            f'Starting Moduli Generation at {start_time}, with [3072, 4096, 8192] as moduli key-lengths')
        mock_moduli_generator.assert_called_once_with(mock_config)
        mock_generator_instance.generate_moduli.assert_called_once()
        mock_generator_instance.store_moduli.assert_called_once()
        mock_logger.info.assert_any_call('Moduli Generation Complete. Time taken: 300 seconds')
        mock_logger.info.assert_any_call('Moduli Generation Complete')

    @pytest.mark.integration
    @patch('moduli_generator.cli.ModuliGenerator')
    @patch('moduli_generator.cli.arg_parser')
    def test_error_recovery_scenarios(self, mock_arg_parser, mock_moduli_generator):
        """Test error recovery scenarios in CLI workflow."""
        # Setup mocks
        mock_config = MagicMock()
        mock_logger = MagicMock()
        mock_config.get_logger.return_value = mock_logger
        mock_config.key_lengths = [4096]
        mock_arg_parser.local_config.return_value = mock_config

        # Test ValueError recovery
        mock_generator_instance = MagicMock()
        mock_generator_instance.generate_moduli.side_effect = ValueError("Test error")
        mock_moduli_generator.return_value = mock_generator_instance

        result = main()
        assert result == 1
        mock_logger.error.assert_called_with('Moduli Generation Failed: Test error')

        # Reset mocks for next test
        mock_logger.reset_mock()

        # Test general exception recovery
        mock_generator_instance.generate_moduli.side_effect = RuntimeError("System error")
        result = main()
        assert result == 2
        mock_logger.error.assert_called_with('Moduli Generation Failed: System error')
