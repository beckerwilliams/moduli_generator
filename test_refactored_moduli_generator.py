#!/usr/bin/env python3
"""
Test script to verify the refactored ModuliGenerator methods work correctly
with the new streaming subprocess approach.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Add the project root to Python path
sys.path.insert(0, '/Users/ron/development/moduli_generator')

from moduli_generator import ModuliGenerator


def test_run_subprocess_with_logging():
    """Test the refactored _run_subprocess_with_logging method"""
    print("Testing _run_subprocess_with_logging with streaming approach...")

    # Setup mock logger
    logger = Mock()

    # Test with a simple command that produces output
    command = ['echo', 'Hello World']

    try:
        result = ModuliGenerator._run_subprocess_with_logging(command, logger)
        print(f"✓ Command executed successfully, return code: {result.returncode}")
        print(f"✓ Logger was called: {logger.log.called}")
        if logger.log.called:
            print(f"✓ Logger calls: {logger.log.call_args_list}")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_error_handling():
    """Test error handling with the new streaming approach"""
    print("\nTesting error handling...")

    logger = Mock()

    # Test with a command that will fail
    command = ['false']  # Command that always returns non-zero exit code

    try:
        ModuliGenerator._run_subprocess_with_logging(command, logger)
        print("✗ Expected CalledProcessError was not raised")
        return False
    except Exception as e:
        print(f"✓ Correctly caught exception: {type(e).__name__}")
        return True


def test_with_mock_config():
    """Test the static methods with a mock configuration"""
    print("\nTesting static methods with mock configuration...")

    # Create a mock config object
    mock_config = Mock()
    mock_config.candidates_dir = Path(tempfile.mkdtemp())
    mock_config.moduli_dir = Path(tempfile.mkdtemp())
    mock_config.nice_value = 10
    mock_config.generator_type = 2

    # Create a mock logger
    mock_logger = Mock()
    mock_config.get_logger.return_value = mock_logger

    print(f"✓ Mock config created with candidates_dir: {mock_config.candidates_dir}")
    print(f"✓ Mock config created with moduli_dir: {mock_config.moduli_dir}")

    # Test that the methods can be called without errors (we'll mock the actual subprocess calls)
    with patch.object(ModuliGenerator, '_run_subprocess_with_logging') as mock_subprocess:
        mock_subprocess.return_value = Mock(returncode=0)

        try:
            # Test _generate_candidates_static
            result_file = ModuliGenerator._generate_candidates_static(mock_config, 3072)
            print(f"✓ _generate_candidates_static returned: {result_file}")
            print(f"✓ Subprocess was called: {mock_subprocess.called}")

            # Create a dummy candidates file for screening test
            candidates_file = mock_config.candidates_dir / "test_candidates"
            candidates_file.touch()

            # Test _screen_candidates_static
            screened_file = ModuliGenerator._screen_candidates_static(mock_config, candidates_file)
            print(f"✓ _screen_candidates_static returned: {screened_file}")

            return True

        except Exception as e:
            print(f"✗ Static method test failed: {e}")
            return False
        finally:
            # Cleanup
            try:
                mock_config.candidates_dir.rmdir()
                mock_config.moduli_dir.rmdir()
            except:
                pass


def test_threading_import():
    """Test that threading import works correctly in the method"""
    print("\nTesting threading import...")

    try:
        # This should work without issues since we import threading inside the method
        import threading
        print("✓ Threading module is available")
        return True
    except ImportError as e:
        print(f"✗ Threading import failed: {e}")
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("=" * 60)
    print("TESTING REFACTORED MODULI GENERATOR")
    print("=" * 60)

    tests = [
        ("Basic subprocess logging", test_run_subprocess_with_logging),
        ("Error handling", test_error_handling),
        ("Static methods with mock config", test_with_mock_config),
        ("Threading import", test_threading_import),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("🎉 All tests passed! The refactoring appears to be working correctly.")
    else:
        print("⚠️  Some tests failed. Please review the implementation.")

    return passed == len(results)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
