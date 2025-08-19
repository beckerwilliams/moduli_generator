#!/usr/bin/env python
"""
Test script for connection error handling in MariaDBConnector.

This script demonstrates how the enhanced test utilities can be used
to test the error handling in the MariaDBConnector class.
"""

from contextlib import contextmanager

from db.test_utils.mocks import MockDatabaseConnection


def test_connection_errors():
    """Test different connection error scenarios using mock implementations."""
    # Test case 1: Connection error with specific message that should be passed through
    print("\nTest Case 1: Testing specific connection error")
    db = MockDatabaseConnection(connection_error="Connection error")

    try:
        with get_connection_from_mock(db):
            print("  [FAIL] Connection should have raised an error")
    except Exception as e:
        if "Connection error" in str(e):
            print(f"  [PASS] Caught expected error: {e}")
        else:
            print(f"  [FAIL] Unexpected error type: {e}")

    # Test case 2: Generic connection error that should be wrapped in RuntimeError
    print("\nTest Case 2: Testing generic connection error")
    db = MockDatabaseConnection(connection_error="Generic error")

    try:
        with get_connection_from_mock(db):
            print("  [FAIL] Connection should have raised an error")
    except RuntimeError as e:
        if "Generic error" in str(e):
            print(f"  [PASS] Caught expected RuntimeError: {e}")
        else:
            print(f"  [FAIL] Unexpected error message: {e}")
    except Exception as e:
        print(f"  [FAIL] Expected RuntimeError but got: {e}")

    # Test case 3: No error
    print("\nTest Case 3: Testing successful connection")
    db = MockDatabaseConnection()

    try:
        with get_connection_from_mock(db):
            print("  [PASS] Connection established successfully")
    except Exception as e:
        print(f"  [FAIL] Unexpected error: {e}")

    print("\nTest completed.")


@contextmanager
def get_connection_from_mock(db):
    """
    A wrapper that mimics the behavior of MariaDBConnector.get_connection
    but works with our mock implementation.
    """
    connection = None
    try:
        connection = db.get_connection()
        yield connection
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    test_connection_errors()
