"""
Pytest tests for moduli generator statistics functionality.

This module tests the database statistics functionality of the moduli generator,
ensuring proper database interaction and error handling.
"""

from unittest.mock import call

import pytest
from mariadb import Error


class TestModuliGeneratorShowStats:
    """Test cases for the moduli generator show_stats functionality."""

    @pytest.mark.unit
    @pytest.mark.integration
    def test_show_stats_success(self, mock_db_connector):
        """Test that stats that it works correctly with a valid database connection."""
        # Call the method
        mock_db_connector.show_stats()

        # Verify that the cursor was created with dictionary=True
        mock_db_connector.connection.cursor.assert_called_with(dictionary=True)

        # Verify that execute was called for each key size (5 sizes)
        assert mock_db_connector.connection.cursor.return_value.__enter__.return_value.execute.call_count == 5

        # Verify that logger.info was called for each size (5 for sizes)
        assert mock_db_connector.logger.info.call_count == 5

        # Verify SQL was called with the last query
        mock_db_connector.sql.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.integration
    def test_show_stats_db_error(self, mock_db_connector):
        """Test that stats handle database errors properly."""
        # Set up the mock cursor to raise an Error
        mock_db_connector.connection.cursor.return_value.__enter__.side_effect = Error("Test DB error")

        # Call the method and check for the expected exception
        with pytest.raises(RuntimeError):
            mock_db_connector.show_stats()

        # Verify that the error was logged
        mock_db_connector.logger.error.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.integration
    def test_show_stats_empty_result(self, mock_db_connector):
        """Test that stats handle empty results correctly."""
        # Set up the mock cursor to return empty count results
        mock_cursor = mock_db_connector.connection.cursor.return_value.__enter__.return_value
        mock_cursor.fetchone.return_value = {"COUNT(*)": 0}

        # Call the method
        mock_db_connector.show_stats()

        # Verify that execute was called for each key size (5)
        assert mock_cursor.execute.call_count == 5

        # Verify that logger.info was called to report the stats (5 sizes)
        assert mock_db_connector.logger.info.call_count == 5

    @pytest.mark.unit
    @pytest.mark.integration
    def test_show_stats_query_construction(self, mock_db_connector):
        """Test that the SQL query is constructed correctly."""
        # Call the method
        mock_db_connector.show_stats()

        # Check that execute was called with the correct query for each size
        expected_query = f"""
                            SELECT COUNT(*) FROM {mock_db_connector.db_name}.{mock_db_connector.view_name}
                            """

        # Get the mock cursor
        mock_cursor = mock_db_connector.connection.cursor.return_value.__enter__.return_value

        # Verify execute was called with the correct query 5 times (once per size)
        expected_calls = [call(expected_query)] * 5
        mock_cursor.execute.assert_has_calls(expected_calls)

        # Verify that SQL was called with the same query at the end
        mock_db_connector.sql.assert_called_once_with(expected_query)

    @pytest.mark.unit
    @pytest.mark.integration
    def test_show_stats_multiple_key_sizes(self, mock_db_connector):
        """Test that stats process all configured key sizes."""
        # Verify the mock has the expected key sizes
        assert mock_db_connector.moduli_query_sizes == [3072, 4096, 6144, 7680, 8192]
        assert mock_db_connector.key_lengths == [3072, 4096, 6144, 7680, 8192]

        # Call the method
        mock_db_connector.show_stats()

        # Verify that execute was called once for each key size (5)
        mock_cursor = mock_db_connector.connection.cursor.return_value.__enter__.return_value
        assert mock_cursor.execute.call_count == len(mock_db_connector.moduli_query_sizes)

    @pytest.mark.unit
    @pytest.mark.integration
    def test_show_stats_database_configuration(self, mock_db_connector):
        """Test that stats use the correct database and view names."""
        # Verify the mock has the expected database configuration
        assert mock_db_connector.db_name == "moduli_db_test"
        assert mock_db_connector.view_name == "moduli_view"

        # Call the method
        mock_db_connector.show_stats()

        # Verify that the query includes the correct database and view names
        expected_query = f"""
                            SELECT COUNT(*) FROM {mock_db_connector.db_name}.{mock_db_connector.view_name}
                            """

        mock_db_connector.sql.assert_called_once_with(expected_query)

    @pytest.mark.unit
    @pytest.mark.integration
    def test_show_stats_cursor_context_manager(self, mock_db_connector):
        """Test that stats properly use cursor context manager."""
        # Call the method
        mock_db_connector.show_stats()

        # Verify that the cursor was called as a context manager
        mock_db_connector.connection.cursor.assert_called_with(dictionary=True)

        # Verify that __enter__ was called (context manager entry)
        mock_db_connector.connection.cursor.return_value.__enter__.assert_called()

    @pytest.mark.unit
    @pytest.mark.integration
    @pytest.mark.parametrize("count_result", [0, 1, 42, 1000, 999999])
    def test_show_stats_various_count_results(self, mock_db_connector, count_result):
        """Test stats with various count results."""
        # Set up the mock cursor to return a specific count
        mock_cursor = mock_db_connector.connection.cursor.return_value.__enter__.return_value
        mock_cursor.fetchone.return_value = {"COUNT(*)": count_result}

        # Call the method
        mock_db_connector.show_stats()

        # Verify that the method completed without error (5 key sizes)
        assert mock_cursor.execute.call_count == 5
        assert mock_db_connector.logger.info.call_count == 5

    @pytest.mark.unit
    @pytest.mark.integration
    def test_show_stats_logging_behavior(self, mock_db_connector):
        """Test that stats log appropriate information."""
        # Call the method
        mock_db_connector.show_stats()

        # Verify that info logging was called the expected number of times
        # Should be called once for each key size (5)
        assert mock_db_connector.logger.info.call_count == 5

        # Verify that no error logging occurred in the successful case
        mock_db_connector.logger.error.assert_not_called()

    @pytest.mark.unit
    @pytest.mark.integration
    def test_show_stats_error_logging(self, mock_db_connector):
        """Test that stats log errors appropriately."""
        # Set up the mock to raise an error
        mock_db_connector.connection.cursor.return_value.__enter__.side_effect = Error("Database connection failed")

        # Call the method and expect it to raise RuntimeError
        with pytest.raises(RuntimeError):
            mock_db_connector.show_stats()

        # Verify that error was logged
        mock_db_connector.logger.error.assert_called_once()
