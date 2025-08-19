"""
Test utilities for the db module.

This module provides utilities for testing the db module, including helpers for
environment detection, mock implementations, and feature flags.
"""

import inspect
import os


def is_test_environment():
    """
    Check if the code is running in a test environment.
    
    Returns:
        bool: True if running in a test environment, False otherwise
    """
    return os.environ.get('DB_TEST_MODE') == 'True'


def is_mock_object(obj):
    """
    Check if an object is a mock object.
    
    Args:
        obj: The object to check
        
    Returns:
        bool: True if the object is a mock object, False otherwise
    """
    # Check for common mock object patterns
    if obj is None:
        return False

    # Check for Mock in class name
    if hasattr(obj, "__class__") and "Mock" in str(obj.__class__):
        return True

    # Check for pytest in type
    if "pytest" in str(type(obj)):
        return True

    # Check for _mock_name attribute
    if hasattr(obj, "_mock_name"):
        return True

    # Check for string representation starting with <Mock
    if str(obj).startswith("<Mock"):
        return True

    return False


def get_config_mock_status(config):
    """
    Check if a configuration object is a mock or real configuration.
    
    This function checks various properties of the config object to determine
    if it's a mock object or a real configuration object.
    
    Args:
        config: The configuration object to check
        
    Returns:
        dict: A dictionary with status information about the config object
    """
    result = {
        "is_mock": is_mock_object(config),
        "details": {},
    }

    # Add detailed information about why it's considered a mock
    if hasattr(config, "__class__"):
        result["details"]["class"] = str(config.__class__)

    if hasattr(config, "_mock_name"):
        result["details"]["mock_name"] = config._mock_name

    # Add frame information if in test context
    if is_test_environment():
        frame = inspect.currentframe()
        if frame:
            frame_info = inspect.getframeinfo(frame.f_back)
            result["details"]["caller"] = f"{frame_info.filename}:{frame_info.lineno}"

    return result


def setup_test_environment():
    """
    Set up the test environment by setting the DB_TEST_MODE environment variable.
    This should be called at the beginning of tests.
    """
    os.environ['DB_TEST_MODE'] = 'True'


def teardown_test_environment():
    """
    Clean up the test environment by removing the DB_TEST_MODE environment variable.
    This should be called at the end of tests.
    """
    if 'DB_TEST_MODE' in os.environ:
        del os.environ['DB_TEST_MODE']
