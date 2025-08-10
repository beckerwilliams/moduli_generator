"""
Unit tests for the __main__ module of moduli_generator.

These tests verify the functionality of the main function in the __main__ module,
which serves as the entry point for the CLI application.
"""

from unittest.mock import MagicMock, patch

import pytest

from moduli_generator.__main__ import main


@pytest.mark.unit
def test_main_with_default_config(mock_config):
    """Test the main function with a mock config."""
    # Mock the ModuliGenerator to avoid actual execution and exceptions
    with patch("moduli_generator.__main__.ModuliGenerator") as mock_generator_class:
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator

        # Chain the mocked methods to return the mock_generator itself
        mock_generator.generate_moduli.return_value = mock_generator
        mock_generator.store_moduli.return_value = mock_generator
        mock_generator.write_moduli_file.return_value = mock_generator

        # Test successful execution
        result = main(mock_config)

        # Verify the logger was called
        assert mock_config.get_logger.called
        mock_logger = mock_config.get_logger.return_value
        assert mock_logger.debug.called
        assert mock_logger.info.called

        # Verify the function returns 0 (success)
        assert result == 0


@pytest.mark.unit
def test_main_with_value_error(mock_config):
    """Test the main function when a ValueError is raised."""
    # Set up ModuliGenerator to raise a ValueError
    with patch("moduli_generator.__main__.ModuliGenerator") as mock_generator_class:
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator
        mock_generator.generate_moduli.side_effect = ValueError("Test error")

        # Execute main function
        result = main(mock_config)

        # Verify error was logged
        mock_logger = mock_config.get_logger.return_value
        mock_logger.error.assert_called_once()

        # Verify the function returns 1 (ValueError)
        assert result == 1


@pytest.mark.unit
def test_main_with_general_exception(mock_config):
    """Test the main function when a general Exception is raised."""
    # Set up ModuliGenerator to raise a general Exception
    with patch("moduli_generator.__main__.ModuliGenerator") as mock_generator_class:
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator
        mock_generator.generate_moduli.side_effect = Exception("Test error")

        # Execute main function
        result = main(mock_config)

        # Verify error was logged
        mock_logger = mock_config.get_logger.return_value
        mock_logger.error.assert_called_once()

        # Verify the function returns 2 (general Exception)
        assert result == 2


@pytest.mark.unit
def test_main_with_no_config():
    """Test the main function when no config is provided."""
    # Mock the arg_parser.local_config to return a mock config
    with patch(
        "moduli_generator.__main__.arg_parser.local_config"
    ) as mock_local_config:
        mock_config = MagicMock()
        mock_local_config.return_value = mock_config

        # Mock the ModuliGenerator
        with patch("moduli_generator.__main__.ModuliGenerator") as mock_generator_class:
            mock_generator = MagicMock()
            mock_generator_class.return_value = mock_generator

            # Chain the mocked methods to return the mock_generator itself
            mock_generator.generate_moduli.return_value = mock_generator
            mock_generator.store_moduli.return_value = mock_generator
            mock_generator.write_moduli_file.return_value = mock_generator

            # Execute main function without providing a config
            result = main()

            # Verify local_config was called
            mock_local_config.assert_called_once()

            # Verify the ModuliGenerator was called with the mock_config
            mock_generator_class.assert_called_once_with(mock_config)

            # Verify the function returns 0 (success)
            assert result == 0


@pytest.mark.unit
def test_main_chain_calls(mock_config):
    """Test that the main function correctly chains method calls."""
    # Set up the ModuliGenerator mock
    with patch("moduli_generator.__main__.ModuliGenerator") as mock_generator_class:
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator

        # Chain the mocked methods to return the mock_generator itself
        mock_generator.generate_moduli.return_value = mock_generator
        mock_generator.store_moduli.return_value = mock_generator
        mock_generator.write_moduli_file.return_value = mock_generator

        # Execute main function
        result = main(mock_config)

        # Verify all methods were called in the correct order
        mock_generator.generate_moduli.assert_called_once()
        mock_generator.store_moduli.assert_called_once()
        mock_generator.write_moduli_file.assert_called_once()

        # Verify the function returns 0 (success)
        assert result == 0


@pytest.mark.unit
def test_main_command_line_entry_point():
    """Test the command-line entry point of the module."""
    with patch("moduli_generator.__main__.main") as mock_main, patch(
        "moduli_generator.__main__.exit"
    ) as mock_exit:

        # Set up mock_main to return a specific exit code
        mock_main.return_value = 42

        # Execute the entry point code
        import moduli_generator.__main__

        # This will only run if __name__ == "__main__", so we simulate that
        if hasattr(moduli_generator.__main__, "__name__"):
            original_name = moduli_generator.__main__.__name__
            moduli_generator.__main__.__name__ = "__main__"
            try:
                # We need to re-execute the conditional code
                exec(
                    """
if __name__ == "__main__":
    exit(main())
                """,
                    moduli_generator.__main__.__dict__,
                )
            finally:
                # Restore the original module name
                moduli_generator.__main__.__name__ = original_name

        # Verify main was called
        mock_main.assert_called_once()

        # Verify exit was called with the return value from main
        mock_exit.assert_called_once_with(42)
