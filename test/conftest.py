"""
Shared pytest configuration and fixtures for the moduli_generator test suite.

This file provides common fixtures, test data, and configuration that can be
used across all test modules in the project.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from mariadb import Error


@pytest.fixture
def temp_file(sample_config_content):
    """Create a temporary file with sample config content for testing."""
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".cnf") as f:
        f.write(sample_config_content)
        f.flush()
        yield f.name
    # Cleanup
    if os.path.exists(f.name):
        os.unlink(f.name)


@pytest.fixture
def empty_temp_file():
    """Create an empty temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".cnf") as f:
        # Don't write anything - leave it empty
        f.flush()
        yield f.name
    # Cleanup
    if os.path.exists(f.name):
        os.unlink(f.name)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_config_content():
    """Sample MariaDB configuration content for testing."""
    return """
[client]
user=testuser  # inline comment
password=testpass
host=localhost
port=3306

[mysqld]
port=3307
bind-address=127.0.0.1
key_buffer_size=16M
max_allowed_packet=1M

[mysqldump]
quick
max_allowed_packet=16M
"""


@pytest.fixture
def sample_config_dict():
    """Sample parsed configuration dictionary for testing."""
    return {
        "client": {
            "user": "testuser",
            "password": "testpass",
            "host": "localhost",
            "port": "3306",
        },
        "mysqld": {
            "port": "3307",
            "bind-address": "127.0.0.1",
            "key_buffer_size": "16M",
            "max_allowed_packet": "1M",
        },
        "mysqldump": {"quick": None, "max_allowed_packet": "16M"},
    }


@pytest.fixture
def mock_db_connector():
    """Create a properly mocked MariaDBConnector for testing."""
    mock_connector = MagicMock()

    # Set up the expected attributes based on your actual config
    mock_connector.db_name = "moduli_db_test"
    mock_connector.view_name = "moduli_view"
    mock_connector.moduli_query_sizes = [
        3072,
        4096,
        6144,
        7680,
        8192,
    ]  # Your actual key sizes
    mock_connector.key_lengths = [3072, 4096, 6144, 7680, 8192]

    # Set up a mock connection and cursor
    mock_connector.connection = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {"COUNT(*)": 42}  # Default count
    mock_connector.connection.cursor.return_value.__enter__.return_value = mock_cursor

    # Set up logger mock
    mock_connector.logger = MagicMock()

    # Set up sql method mock
    mock_connector.sql = MagicMock()

    # Actually implement the show_stats method behavior
    def mock_show_stats():
        try:
            with mock_connector.connection.cursor(dictionary=True) as cursor:
                query = f"""
                            SELECT COUNT(*) FROM {mock_connector.db_name}.{mock_connector.view_name}
                            """

                # Execute a query for each key size
                for size in mock_connector.moduli_query_sizes:
                    cursor.execute(query)
                    result = cursor.fetchone()
                    count = result["COUNT(*)"] if result else 0
                    mock_connector.logger.info(f"Key size {size}: {count} moduli")

                # Call an SQL method with the final query
                mock_connector.sql(query)

        except Error as e:
            mock_connector.logger.error(f"Database error in show_stats: {e}")
            raise RuntimeError(f"Database error: {e}")

    mock_connector.show_stats = mock_show_stats

    return mock_connector


@pytest.fixture
def sample_moduli_data():
    """Sample moduli data for testing file parsing."""
    return [
        "20230101000000 2 3072 8 0 1234567890abcdef1234567890abcdef12345678 fedcba0987654321fedcba0987654321fedcba09",
        "20230101000001 2 2048 8 0 abcdef1234567890abcdef1234567890abcdef12 09abcdef1234567890abcdef1234567890abcdef",
        "20230101000002 2 4096 8 0 567890abcdef1234567890abcdef1234567890ab cdef1234567890abcdef1234567890abcdef1234",
    ]


@pytest.fixture
def valid_cli_args():
    """Valid CLI arguments for testing argument parsing."""
    return {
        "key_length": 4096,
        "nice_value": 10,
        "verbose": True,
        "config_file": "/etc/moduli_generator.cnf",
        "output_file": "/tmp/moduli_output",
        "database": True,
    }


@pytest.fixture
def invalid_cli_args():
    """Invalid CLI arguments for testing validation."""
    return [
        {"key_length": 256, "nice_value": 10},  # key_length too small
        {"key_length": 32768, "nice_value": 10},  # key_length too large
        {"key_length": 2049, "nice_value": 10},  # key_length not divisible by 8
        {"key_length": 2048, "nice_value": 25},  # nice_value too high
        {"key_length": 2048, "nice_value": -25},  # nice_value too low
        {"key_length": "invalid", "nice_value": 10},  # key_length not numeric
        {"key_length": 2048, "nice_value": "invalid"},  # nice_value not numeric
    ]


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for testing command execution."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Command executed successfully"
        mock_run.return_value.stderr = ""
        yield mock_run


@pytest.fixture
def mock_logger():
    """Mock logger for testing logging functionality."""
    return MagicMock()


@pytest.fixture
def mock_config():
    """Mock configuration object for testing."""
    from pathlib import Path

    config = MagicMock()

    # Common configuration attributes used by tests
    config.key_lengths = (4096, 8192)
    config.nice_value = 10
    config.moduli_home = Path("/test/moduli_home")
    config.candidates_dir = Path("/test/moduli_home/candidates")
    config.moduli_dir = Path("/test/moduli_home/moduli")
    config.log_dir = Path("/test/moduli_home/logs")
    config.mariadb_cnf = Path("/test/moduli_home/mariadb.cnf")
    config.db_name = "test_moduli_db"
    config.table_name = "test_moduli_table"
    config.view_name = "test_moduli_view"
    config.config_id = "test_config"
    config.base_dir = Path("/test/moduli_home")
    config.moduli_file_pfx = "test_moduli"
    config.moduli_file = Path("/test/moduli_home/moduli_file")
    config.moduli_file_pattern = "moduli_*"
    config.records_per_keylength = 100
    config.delete_records_on_moduli_write = False
    config.delete_records_on_read = False
    config.preserve_moduli_after_dbstore = False
    config.generator_type = 2

    # Mock the get_logger method to return a mock logger
    mock_logger_instance = MagicMock()
    config.get_logger.return_value = mock_logger_instance

    # Mock the ensure_directories method
    config.ensure_directories = MagicMock()

    return config


@pytest.fixture
def mock_db_config():
    """Mock configuration specifically for database tests that need MariaDB mocking."""
    from pathlib import Path

    config = MagicMock()

    # Common configuration attributes used by tests
    config.key_lengths = (4096, 8192)
    config.nice_value = 10
    config.moduli_home = Path("/test/moduli_home")
    config.candidates_dir = Path("/test/moduli_home/candidates")
    config.moduli_dir = Path("/test/moduli_home/moduli")
    config.log_dir = Path("/test/moduli_home/logs")
    config.mariadb_cnf = Path("/test/moduli_home/mariadb.cnf")
    config.db_name = "test_moduli_db"
    config.table_name = "test_moduli_table"
    config.view_name = "test_moduli_view"
    config.config_id = "test_config"
    config.base_dir = Path("/test/moduli_home")
    config.moduli_file_pfx = "test_moduli"
    config.moduli_file = Path("/test/moduli_home/moduli_file")
    config.records_per_keylength = 100
    config.delete_records_on_moduli_write = False
    config.delete_records_on_read = False

    # Mock the get_logger method to return a mock logger
    mock_logger_instance = MagicMock()
    config.get_logger.return_value = mock_logger_instance

    # Mock the ensure_directories method
    config.ensure_directories = MagicMock()

    # Mock parse_mysql_config to return proper structure
    with (
        patch("db.parse_mysql_config") as mock_parse,
        patch("db.ConnectionPool") as mock_pool,
    ):
        mock_parse.return_value = {
            "client": {
                "host": "localhost",
                "port": "3306",
                "user": "test_user",
                "password": "test_password",
                "database": "test_moduli_db",
            }
        }

        # Mock the ConnectionPool to prevent actual database connections
        mock_pool_instance = MagicMock()
        mock_pool.return_value = mock_pool_instance

        yield config


@pytest.fixture(autouse=True)
def mock_all_subprocess():
    """Automatically mock all subprocess calls to prevent actual shell command execution."""
    # Only mock at the module level to prevent actual execution, but allow test-specific patches to override
    with (
        patch("moduli_generator.subprocess.run") as mock_mg_run,
        patch("subprocess.Popen") as mock_popen,
        patch("subprocess.call") as mock_call,
        patch("subprocess.check_call") as mock_check_call,
        patch("subprocess.check_output") as mock_check_output,
    ):
        # Configure mock_run (most commonly used)
        mock_result = MagicMock(
            returncode=0,
            stdout="Mocked ssh-keygen output\nGenerated moduli candidates successfully",
            stderr="",
            args=[],
        )
        mock_mg_run.return_value = mock_result

        # Configure other subprocess methods
        mock_popen.return_value = MagicMock(
            returncode=0,
            stdout=MagicMock(read=lambda: "Mocked output"),
            stderr=MagicMock(read=lambda: ""),
            communicate=lambda: ("Mocked output", ""),
        )
        mock_call.return_value = 0
        mock_check_call.return_value = 0
        mock_check_output.return_value = "Mocked output"

        yield {
            "popen": mock_popen,
            "call": mock_call,
            "check_call": mock_check_call,
            "check_output": mock_check_output,
            "mg_run": mock_mg_run,
        }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Automatically set up a test environment for all tests."""
    # Set test environment variables
    os.environ["TESTING"] = "1"
    yield
    # Cleanup
    if "TESTING" in os.environ:
        del os.environ["TESTING"]


# Pytest configuration hooks
def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "security: mark test as a security test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


def pytest_collection_modifyitems(config, items):
    """Modify a test collection to add markers automatically."""
    for item in items:
        # Add unit marker to all tests by default
        if not any(
            marker.name in ["integration", "security", "slow"]
            for marker in item.iter_markers()
        ):
            item.add_marker(pytest.mark.unit)

        # Add slow marker to tests that might be slow
        if "database" in item.name.lower() or "integration" in item.name.lower():
            item.add_marker(pytest.mark.slow)
