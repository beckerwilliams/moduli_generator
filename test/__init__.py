from get_version import get_version

"""
Test Suite for Moduli Generator

This package contains comprehensive tests for the moduli_generator project,
including unit tests, integration tests, and security tests.

The test suite covers:
- Configuration management and validation
- CLI argument parsing and integration
- Database operations and error handling
- Moduli generation and screening processes
- Logging and utility functions

Test Categories:
- Unit tests: Fast, isolated tests for individual components
- Integration tests: Tests that verify component interactions
- Security tests: Tests focused on security-related functionality
- Slow tests: Long-running tests marked for optional execution

To run the tests:
    pytest                    # Run all tests
    pytest -m unit           # Run only unit tests
    pytest -m integration    # Run only integration tests
    pytest -v                # Verbose output
"""

__version__ = get_version
__author__ = "Ron Williams"
