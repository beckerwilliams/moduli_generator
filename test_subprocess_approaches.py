#!/usr/bin/env python3
"""
Test script to compare streaming vs capturing subprocess output approaches.
This will help analyze the advantages of each method for the ModuliGenerator refactoring.
"""

import logging
import subprocess
import threading
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def current_approach_capture_then_log(command):
    """Current approach: capture all output, then log it"""
    print("\n=== CURRENT APPROACH: Capture then Log ===")
    start_time = time.time()

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        # Log stdout if present (after completion)
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    logger.info(f"STDOUT: {line.strip()}")

        # Log stderr if present (after completion)
        if result.stderr:
            for line in result.stderr.strip().split('\n'):
                if line.strip():
                    logger.debug(f"STDERR: {line.strip()}")

        end_time = time.time()
        print(f"Total time: {end_time - start_time:.2f}s")
        print(f"Memory usage: All output held in memory until completion")
        return result

    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        if e.stderr:
            logger.error(f"Error output: {e.stderr}")
        raise


def streaming_approach_real_time_log(command):
    """Alternative approach: stream output in real-time"""
    print("\n=== STREAMING APPROACH: Real-time Log ===")
    start_time = time.time()

    def log_stream(stream, log_func, prefix):
        """Helper to log stream output in real-time"""
        for line in iter(stream.readline, ''):
            if line.strip():
                log_func(f"{prefix}: {line.strip()}")

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True
        )

        # Start threads to handle stdout and stderr streams
        stdout_thread = threading.Thread(
            target=log_stream,
            args=(process.stdout, logger.info, "STDOUT")
        )
        stderr_thread = threading.Thread(
            target=log_stream,
            args=(process.stderr, logger.debug, "STDERR")
        )

        stdout_thread.start()
        stderr_thread.start()

        # Wait for process to complete
        return_code = process.wait()

        # Wait for logging threads to finish
        stdout_thread.join()
        stderr_thread.join()

        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, command)

        end_time = time.time()
        print(f"Total time: {end_time - start_time:.2f}s")
        print(f"Memory usage: Minimal - output streamed as generated")

        # Create a mock result object for compatibility
        class MockResult:
            def __init__(self, returncode):
                self.returncode = returncode
                self.stdout = ""  # Already logged
                self.stderr = ""  # Already logged

        return MockResult(return_code)

    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        raise


def test_with_sample_command():
    """Test both approaches with a sample command that produces output"""
    # Use a command that produces some output over time
    test_command = ['python3', '-c', '''
import time
import sys
for i in range(5):
    print(f"Output line {i+1}")
    sys.stdout.flush()
    if i == 2:
        print(f"Error line {i+1}", file=sys.stderr)
        sys.stderr.flush()
    time.sleep(0.5)
print("Final output line")
''']

    print("Testing subprocess output handling approaches...")

    # Test current approach
    try:
        current_approach_capture_then_log(test_command)
    except Exception as e:
        print(f"Current approach failed: {e}")

    # Test streaming approach
    try:
        streaming_approach_real_time_log(test_command)
    except Exception as e:
        print(f"Streaming approach failed: {e}")


def analyze_advantages():
    """Analyze the advantages of each approach"""
    print("\n=== ANALYSIS OF APPROACHES ===")
    print("\nCURRENT APPROACH (Capture then Log):")
    print("Advantages:")
    print("- Simple implementation")
    print("- All output available for post-processing")
    print("- Easy error handling with complete stderr")
    print("\nDisadvantages:")
    print("- High memory usage for large outputs")
    print("- No real-time feedback during long operations")
    print("- User sees no progress until completion")

    print("\nSTREAMING APPROACH (Real-time Log):")
    print("Advantages:")
    print("- Low memory usage - constant regardless of output size")
    print("- Real-time feedback for long-running operations")
    print("- Better user experience with immediate progress visibility")
    print("- Can handle very large outputs without memory issues")
    print("\nDisadvantages:")
    print("- More complex implementation")
    print("- Requires threading for concurrent stdout/stderr handling")
    print("- Output not available for post-processing")


if __name__ == "__main__":
    test_with_sample_command()
    analyze_advantages()
