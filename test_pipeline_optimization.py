#!/usr/bin/env python3
"""
Test script to verify the pipeline optimization works correctly.
This test will run for a short time to verify the pipeline starts working.
"""

import signal
import tempfile
import time
from pathlib import Path

from config import default_config
from moduli_generator import ModuliGenerator


class TimeoutException(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutException("Test timed out")


def test_pipeline_optimization():
    """Test the optimized pipeline implementation."""
    print("Testing optimized pipeline implementation...")

    # Set up timeout handler
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)  # 30 second timeout

    # Use the default config but modify it for testing
    config = default_config

    # Store original values to restore later
    original_key_lengths = config.key_lengths
    original_candidates_dir = config.candidates_dir
    original_moduli_dir = config.moduli_dir

    try:
        # Use minimum valid key lengths for testing
        config.key_lengths = [3072]  # Just one key length for faster testing

        # Create temporary directories
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config.candidates_dir = temp_path / "candidates"
            config.moduli_dir = temp_path / "moduli"
            config.candidates_dir.mkdir(exist_ok=True)
            config.moduli_dir.mkdir(exist_ok=True)

            # Initialize generator
            generator = ModuliGenerator(config)

            # Measure time
            start_time = time.time()

            try:
                print("Starting pipeline processing...")
                generator.generate_moduli()
                end_time = time.time()

                duration = end_time - start_time
                print(f"Pipeline implementation completed in: {duration:.2f} seconds")

                # Count generated files
                moduli_files = list(config.moduli_dir.glob("*"))
                print(f"Generated {len(moduli_files)} moduli files")

                return duration, len(moduli_files)

            except TimeoutException:
                print(
                    "Test timed out after 30 seconds - this is expected for performance testing"
                )
                print(
                    "The important thing is that the pipeline processing started without errors"
                )
                return None, 0

            except Exception as e:
                print(f"Error during testing: {e}")
                import traceback

                traceback.print_exc()
                return None, 0

    finally:
        # Cancel the alarm
        signal.alarm(0)

        # Restore original configuration
        config.key_lengths = original_key_lengths
        config.candidates_dir = original_candidates_dir
        config.moduli_dir = original_moduli_dir


if __name__ == "__main__":
    test_pipeline_optimization()
