"""
Mock implementations for testing the db module.

This module provides mock implementations for various components used in the db module,
such as file system operations and database connections.
"""


class MockFileSystem:
    """
    A class that mocks file system operations for testing.
    """

    def __init__(self, files=None):
        """
        Initialize with a dictionary of mock files.
        
        Args:
            files (dict): Dictionary mapping file paths to file contents
        """
        self.files = files or {}

    def exists(self, path):
        """Check if a file exists in the mock file system."""
        return str(path) in self.files

    def is_dir(self, path):
        """Check if a path is a directory in the mock file system."""
        return isinstance(self.files.get(str(path)), dict)

    def get_size(self, path):
        """Get the size of a file in the mock file system."""
        content = self.files.get(str(path), "")
        return len(content) if isinstance(content, str) else 0

    def read(self, path):
        """
        Get the content of a file in the mock file system.
        
        Args:
            path: The path to the file
            
        Returns:
            str: The content of the file or the path string if the file doesn't exist
        """
        if str(path) in self.files:
            return self.files[str(path)]
        return str(path)


class MockDatabaseConnection:
    """
    A class that mocks database connection for testing.
    """

    def __init__(self, schema_verification_result=None, should_raise=False, connection_error=None):
        """
        Initialize with optional schema verification result.
        
        Args:
            schema_verification_result (dict): The result to return from verify_schema
            should_raise (bool): Whether verify_schema should raise an exception
            connection_error (str, optional): If provided, get_connection will raise this error
        """
        self.schema_verification_result = schema_verification_result or {
            "overall_status": "PASSED"
        }
        self.should_raise = should_raise
        self.connection_error = connection_error
        self.queries = []
        self.logger = MockLogger()
        self.pool = MockConnectionPool(connection_error)

    def execute(self, query, params=None):
        """
        Mock query execution.
        
        Args:
            query (str): The SQL query to execute
            params (tuple, optional): Parameters for the query
            
        Returns:
            list: Empty list simulating a result set
        """
        self.queries.append((query, params))
        return []

    def verify_schema(self):
        """
        Return the mock schema verification result.
        
        Returns:
            dict: The schema verification result
            
        Raises:
            RuntimeError: If should_raise is True
        """
        if self.should_raise:
            raise RuntimeError("Mock schema verification error")
        return self.schema_verification_result

    def get_connection(self):
        """
        Mock implementation of get_connection that simulates connection errors.
        
        Returns:
            MockConnection: A mock connection object
            
        Raises:
            Error: If connection_error is set to a specific error message
            RuntimeError: If connection_error is set to a generic error
        """
        return self.pool.get_connection()

    def _perform_schema_verification(self):
        """
        Mock for the schema verification method added in Phase 2.
        
        This method mirrors the one added to MariaDBConnector.
        
        Raises:
            RuntimeError: If should_raise is True
        """
        schema_result = self.verify_schema()
        if schema_result is None or schema_result.get("overall_status") in ["FAILED", "ERROR"]:
            self.logger.warning("Database schema verification failed, but continuing initialization")

    def _verify_schema_with_logging(self, config):
        """
        Mock for the schema verification with logging method added in Phase 2.
        
        Args:
            config: The configuration object
        """
        from db.test_utils import is_mock_object

        # Check if this is a test environment or mock object
        is_test_env = is_mock_object(config)

        if is_test_env:
            self.logger.debug("Skipping schema verification for test environment")
            return

        try:
            self._perform_schema_verification()
        except (NameError, RuntimeError) as err:
            self.logger.warning(f"Schema verification failed: {err}, but continuing initialization")


class MockConnectionPool:
    """
    A class that mocks a database connection pool for testing.
    """

    def __init__(self, connection_error=None):
        """
        Initialize the mock connection pool.
        
        Args:
            connection_error (str, optional): If provided, get_connection will raise this error
        """
        self.connection_error = connection_error

    def get_connection(self):
        """
        Mock implementation of get_connection that simulates connection errors.
        
        Returns:
            MockConnection: A mock connection object
            
        Raises:
            Error: If connection_error is set to a specific error message
            RuntimeError: If connection_error is set to a generic error
        """
        from mariadb import Error

        if self.connection_error:
            if self.connection_error in ["Connection error", "Connection failed"]:
                raise Error(self.connection_error)
            else:
                raise RuntimeError(f"Connection error: {self.connection_error}")

        return MockConnection()

    def close(self):
        """Mock implementation of close."""
        pass


class MockConnection:
    """
    A class that mocks a database connection for testing.
    """

    def __init__(self):
        """Initialize the mock connection."""
        self.closed = False
        self.committed = False
        self.rolled_back = False

    def close(self):
        """Mock implementation of close."""
        self.closed = True

    def commit(self):
        """Mock implementation of commit."""
        self.committed = True

    def rollback(self):
        """Mock implementation of rollback."""
        self.rolled_back = True

    def cursor(self, **kwargs):
        """
        Mock implementation of cursor.
        
        Returns:
            MockCursor: A mock cursor object
        """
        return MockCursor(**kwargs)


class MockCursor:
    """
    A class that mocks a database cursor for testing.
    """

    def __init__(self, dictionary=False):
        """
        Initialize the mock cursor.
        
        Args:
            dictionary (bool): Whether to return results as dictionaries
        """
        self.dictionary = dictionary
        self.rowcount = 0
        self.lastrowid = 1
        self.queries = []
        self.params = []

    def execute(self, query, params=None):
        """
        Mock implementation of execute.
        
        Args:
            query (str): The SQL query to execute
            params (tuple, optional): Parameters for the query
        """
        self.queries.append(query)
        self.params.append(params)
        self.rowcount = 1

    def fetchall(self):
        """
        Mock implementation of fetchall.
        
        Returns:
            list: A list of mock results
        """
        if self.dictionary:
            return [{"id": 1, "name": "test"}]
        return [(1, "test")]

    def __enter__(self):
        """
        Mock implementation of context manager entry.
        
        Returns:
            MockCursor: This cursor object
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Mock implementation of context manager exit."""
        pass


class MockLogger:
    """
    A simple mock logger for testing.
    """

    def __init__(self):
        """Initialize the mock logger with empty logs."""
        self.logs = {
            "debug": [],
            "info": [],
            "warning": [],
            "error": [],
            "critical": []
        }
        self.name = "mock_logger"

    def debug(self, message):
        """Log a debug message."""
        self.logs["debug"].append(message)

    def info(self, message):
        """Log an info message."""
        self.logs["info"].append(message)

    def warning(self, message):
        """Log a warning message."""
        self.logs["warning"].append(message)

    def error(self, message):
        """Log an error message."""
        self.logs["error"].append(message)

    def critical(self, message):
        """Log a critical message."""
        self.logs["critical"].append(message)

    def get_logs(self, level=None):
        """
        Get all logs or logs of a specific level.
        
        Args:
            level (str, optional): The log level to get. If None, returns all logs.
            
        Returns:
            list or dict: The logs
        """
        if level:
            return self.logs.get(level, [])
        return self.logs
