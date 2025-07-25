"""
Pytest tests for LoggerWriter functionality.

This module tests the LoggerWriter class which bridges logger and writable interfaces,
ensuring proper logging functionality and file-like interface compatibility.
"""

import logging
import pytest
import sys
from unittest.mock import MagicMock, patch

from moduli_generator.logger_writer import LoggerWriter


class TestLoggerWriter:
    """Test cases for LoggerWriter class functionality."""

    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger for testing."""
        return MagicMock(spec=logging.Logger)

    @pytest.fixture
    def logger_writer(self, mock_logger):
        """Create a LoggerWriter instance for testing."""
        return LoggerWriter(mock_logger, logging.INFO)

    @pytest.mark.unit
    def test_init(self, mock_logger):
        """Test LoggerWriter initialization."""
        level = logging.DEBUG
        writer = LoggerWriter(mock_logger, level)

        assert writer.logger is mock_logger
        assert writer.level == level

    @pytest.mark.unit
    def test_write_with_content(self, logger_writer, mock_logger):
        """Test write method with non-empty message."""
        message = "Test log message"
        result = logger_writer.write(message)

        # Should log the message
        mock_logger.log.assert_called_once_with(logging.INFO, message)
        # Should return message length
        assert result == len(message)

    @pytest.mark.unit
    def test_write_with_whitespace_content(self, logger_writer, mock_logger):
        """Test write method with message containing whitespace."""
        message = "  Test log message with spaces  \n"
        result = logger_writer.write(message)

        # Should log the stripped message
        mock_logger.log.assert_called_once_with(logging.INFO, "Test log message with spaces")
        # Should return original message length
        assert result == len(message)

    @pytest.mark.unit
    def test_write_with_empty_message(self, logger_writer, mock_logger):
        """Test write method with empty message."""
        message = ""
        result = logger_writer.write(message)

        # Should not log empty message
        mock_logger.log.assert_not_called()
        # Should return message length (0)
        assert result == 0

    @pytest.mark.unit
    def test_write_with_whitespace_only(self, logger_writer, mock_logger):
        """Test write method with whitespace-only message."""
        message = "   \n\t  "
        result = logger_writer.write(message)

        # Should not log whitespace-only message
        mock_logger.log.assert_not_called()
        # Should return message length
        assert result == len(message)

    @pytest.mark.unit
    def test_flush(self, logger_writer):
        """Test flush method."""
        # Should not raise any exceptions
        result = logger_writer.flush()
        assert result is None

    @pytest.mark.unit
    def test_fileno(self, logger_writer):
        """Test fileno method returns stderr file descriptor."""
        with patch('sys.stderr') as mock_stderr:
            mock_stderr.fileno.return_value = 2
            result = logger_writer.fileno()

            mock_stderr.fileno.assert_called_once()
            assert result == 2

    @pytest.mark.unit
    def test_different_log_levels(self, mock_logger):
        """Test LoggerWriter with different log levels."""
        levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]

        for level in levels:
            writer = LoggerWriter(mock_logger, level)
            message = f"Test message for level {level}"

            writer.write(message)
            mock_logger.log.assert_called_with(level, message)

            # Reset mock for next iteration
            mock_logger.reset_mock()

    @pytest.mark.unit
    def test_multiple_writes(self, logger_writer, mock_logger):
        """Test multiple consecutive writes."""
        messages = ["First message", "Second message", "Third message"]

        for message in messages:
            result = logger_writer.write(message)
            assert result == len(message)

        # Verify all messages were logged
        assert mock_logger.log.call_count == len(messages)
        for i, message in enumerate(messages):
            assert mock_logger.log.call_args_list[i][0] == (logging.INFO, message)

    @pytest.mark.integration
    def test_real_logger_integration(self):
        """Test LoggerWriter with a real logger."""
        # Create a real logger with a handler
        logger = logging.getLogger('test_logger_writer')
        logger.setLevel(logging.DEBUG)

        # Create a handler to capture log records
        handler = logging.Handler()
        handler.setLevel(logging.DEBUG)
        log_records = []

        def capture_record(record):
            log_records.append(record)

        handler.emit = capture_record
        logger.addHandler(handler)

        try:
            # Test with real logger
            writer = LoggerWriter(logger, logging.INFO)
            test_message = "Integration test message"

            result = writer.write(test_message)

            assert result == len(test_message)
            assert len(log_records) == 1
            assert log_records[0].getMessage() == test_message
            assert log_records[0].levelno == logging.INFO

        finally:
            # Clean up
            logger.removeHandler(handler)

    @pytest.mark.unit
    def test_file_like_interface_compatibility(self, logger_writer):
        """Test that LoggerWriter implements required file-like interface methods."""
        # Check that all required methods exist and are callable
        assert hasattr(logger_writer, 'write')
        assert callable(logger_writer.write)

        assert hasattr(logger_writer, 'flush')
        assert callable(logger_writer.flush)

        assert hasattr(logger_writer, 'fileno')
        assert callable(logger_writer.fileno)

        # Test that methods return expected types
        assert isinstance(logger_writer.write("test"), int)
        assert logger_writer.flush() is None
        assert isinstance(logger_writer.fileno(), int)
