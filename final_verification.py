#!/usr/bin/env python3
"""
Final verification script to test both CLI command variations.
"""
import subprocess
import sys
import tempfile
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    print(f"Return code: {result.returncode}")
    if result.stdout:
        print(f"STDOUT (first 500 chars):\n{result.stdout[:500]}...")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")
    return result


def main():
    """Final verification of both CLI command variations."""
    project_root = Path(__file__).parent

    print("=== Final Verification ===")

    # Clean and build
    print("\n1. Cleaning and building...")
    run_command("rm -rf dist/ build/ *.egg-info/", cwd=project_root)
    result = run_command("poetry build", cwd=project_root)
    if result.returncode != 0:
        print("ERROR: Failed to build package")
        return 1

    # Test in fresh environment
    with tempfile.TemporaryDirectory() as temp_dir:
        venv_path = Path(temp_dir) / "test_venv"

        print(f"\n2. Creating fresh virtual environment...")
        run_command(f"python -m venv {venv_path}")

        # Install wheel
        wheel_files = list((project_root / "dist").glob("*.whl"))
        wheel_file = wheel_files[0]
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"

        print(f"\n3. Installing wheel...")
        result = run_command(f"{pip_path} install {wheel_file}")
        if result.returncode != 0:
            print("ERROR: Failed to install wheel")
            return 1

        # Test both command variations
        print(f"\n4. Testing 'python -m moduli_generator -h'...")
        result1 = run_command(f"{python_path} -m moduli_generator -h")

        print(f"\n5. Testing 'python -m moduli_generator.cli -h'...")
        result2 = run_command(f"{python_path} -m moduli_generator.cli -h")

        # Check results
        if result1.returncode == 0 and result2.returncode == 0:
            print("\n✅ SUCCESS: Both command variations work correctly!")
            return 0
        else:
            print(
                f"\n❌ FAILURE: Command results - moduli_generator: {result1.returncode}, moduli_generator.cli: {result2.returncode}"
            )
            return 1


if __name__ == "__main__":
    sys.exit(main())
