#!/usr/bin/env python3
"""
Test script to measure performance of the current sequential processing
vs the optimized pipeline processing in generate_moduli().
"""

import tempfile
import time
from pathlib import Path

from config import default_config
from moduli_generator import ModuliGenerator


def test_current_performance():
    """Test the current sequential implementation performance."""
    print("Testing current sequential implementation...")

    # Create a temporary config with smaller key lengths for testing
    # Use the default config but modify it for testing
    config = default_config

    # Store original values to restore later
    original_key_lengths = config.key_lengths
    original_candidates_dir = config.candidates_dir
    original_moduli_dir = config.moduli_dir

    try:
        # Use minimum valid key lengths for faster testing
        config.key_lengths = [3072, 4096]  # Minimum secure key lengths

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
                generator.generate_moduli()
                end_time = time.time()

                duration = end_time - start_time
                print(f"Current implementation took: {duration:.2f} seconds")

                # Count generated files
                moduli_files = list(config.moduli_dir.glob("*"))
                print(f"Generated {len(moduli_files)} moduli files")

                return duration, len(moduli_files)

            except Exception as e:
                print(f"Error during testing: {e}")
                return None, 0

    finally:
        # Restore original configuration
        config.key_lengths = original_key_lengths
        config.candidates_dir = original_candidates_dir
        config.moduli_dir = original_moduli_dir


if __name__ == "__main__":
    test_current_performance()
