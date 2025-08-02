#!/usr/bin/env python3
"""
Script to reproduce the specific CLI issue mentioned.
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
        print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")
    return result


def main():
    """Reproduce the CLI issue by building and testing the package."""
    project_root = Path(__file__).parent

    print("=== Reproducing the CLI issue ===")

    # Clean any existing build artifacts
    print("\n1. Cleaning existing build artifacts...")
    run_command("rm -rf dist/ build/ *.egg-info/", cwd=project_root)

    # Build the package
    print("\n2. Building the package with poetry...")
    result = run_command("poetry build", cwd=project_root)
    if result.returncode != 0:
        print("ERROR: Failed to build package")
        return 1

    # Create a temporary virtual environment and install the wheel
    with tempfile.TemporaryDirectory() as temp_dir:
        venv_path = Path(temp_dir) / "test_venv"

        print(f"\n3. Creating temporary virtual environment at {venv_path}...")
        run_command(f"python -m venv {venv_path}")

        # Find the built wheel
        dist_dir = project_root / "dist"
        wheel_files = list(dist_dir.glob("*.whl"))
        if not wheel_files:
            print("ERROR: No wheel file found in dist/")
            return 1

        wheel_file = wheel_files[0]
        print(f"Found wheel: {wheel_file}")

        # Install the wheel
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"

        print(f"\n4. Installing wheel in virtual environment...")
        result = run_command(f"{pip_path} install {wheel_file}")
        if result.returncode != 0:
            print("ERROR: Failed to install wheel")
            return 1

        # Test the specific CLI command mentioned in the issue
        print(
            f"\n5. Testing the specific CLI command: python -m moduli_generator.cli -h..."
        )
        result = run_command(f"{python_path} -m moduli_generator.cli -h")
        if result.returncode != 0:
            print("ERROR: CLI command failed - this confirms the issue!")
            return 1

        # Also test the main module command
        print(f"\n6. Testing the main module command: python -m moduli_generator -h...")
        result = run_command(f"{python_path} -m moduli_generator -h")
        if result.returncode != 0:
            print("ERROR: Main module command failed!")
            return 1

        print("\n=== Issue reproduction complete ===")
        return 0


if __name__ == "__main__":
    sys.exit(main())
