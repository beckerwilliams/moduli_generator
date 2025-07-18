import unittest
from unittest.mock import MagicMock, call

from mariadb import Error

from db import MariaDBConnector


class TestModuliGeneratorShowStats(unittest.TestCase):
    def setUp(self):
        # Create a mock database connector
        self.mock_db = MagicMock(spec=MariaDBConnector)
        self.mock_db.moduli_query_sizes = [1024, 2048, 4096]  # Add this attribute
        self.mock_db.key_lengths = [1024, 2048, 4096]  # Make sure this is also available
        self.mock_db.db_name = "moduli_db_test"
        self.mock_db.view_name = "moduli_view"
        self.mock_db.logger = MagicMock()

        # Mock cursor and connection
        self.mock_cursor = MagicMock()
        self.mock_connection = MagicMock()
        self.mock_connection.cursor.return_value.__enter__.return_value = self.mock_cursor
        self.mock_db.connection = self.mock_connection

        # Mock the SQL method
        self.mock_db.sql = MagicMock(return_value="Query result")

        # Set up fetchone to return a dictionary with COUNT(*)
        self.mock_cursor.fetchone.return_value = {"COUNT(*)": 42}

    def test_show_stats_success(self):
        """Test that stats works correctly with valid data"""
        # Call the method
        self.mock_db.show_stats()

        # Verify that the cursor was created with dictionary=True
        self.mock_connection.cursor.assert_called_with(dictionary=True)

        # Verify that execute was called for each key size (once per size)
        self.assertEqual(self.mock_cursor.execute.call_count, 3)

        # Verify that logger.info was called for each size
        self.assertEqual(self.mock_db.logger.info.call_count, 4)  # 3 for sizes + 1 for final SQL

        # Verify SQL was called with the last query
        self.mock_db.sql.assert_called_once()

    def test_show_stats_db_error(self):
        """Test that stats handles database errors properly"""
        # Set up the mock cursor to raise an Error
        self.mock_connection.cursor.return_value.__enter__.side_effect = Error("Test DB error")

        # Call the method and check for the expected exception
        with self.assertRaises(RuntimeError):
            self.mock_db.show_stats()

        # Verify that the error was logged
        self.mock_db.logger.error.assert_called_once()

    def test_show_stats_empty_result(self):
        """Test that stats handles empty results correctly"""
        # Set up the mock cursor to return empty count data
        self.mock_cursor.fetchone.return_value = {"COUNT(*)": 0}

        # Call the method
        self.mock_db.show_stats()

        # Verify that execute was called for each key size
        self.assertEqual(self.mock_cursor.execute.call_count, 3)

        # Verify that logger.info was called to report the stats (3 sizes + final SQL)
        self.assertEqual(self.mock_db.logger.info.call_count, 4)

    def test_show_stats_query_construction(self):
        """Test that the SQL query is constructed correctly"""
        # Call the method
        self.mock_db.show_stats()

        # Check that execute was called with the correct query for each size
        expected_query = f"""
                            SELECT COUNT(*) FROM moduli_db_test.moduli_view
                            """

        # Verify execute was called with the correct query 3 times (once per size)
        expected_calls = [call(expected_query, )] * 3
        self.mock_cursor.execute.assert_has_calls(expected_calls)

        # Verify that SQL was called with the same query at the end
        self.mock_db.sql.assert_called_once_with(expected_query)


if __name__ == "__main__":
    unittest.main()
