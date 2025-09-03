#!/usr/bin/env python3
"""
MkDocs server script for the moduli_generator project.

This script provides a convenient way to start the MkDocs documentation
server directly through Poetry.
"""

import importlib.util
import os
import subprocess
import sys


def is_mkdocs_installed():
    """Check if mkdocs is installed."""
    return importlib.util.find_spec("mkdocs") is not None


def get_mkdocs_path():
    """Get the path to the mkdocs executable."""
    try:
        result = subprocess.run(
            ["which", "mkdocs"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return None


def find_project_root():
    """Find the project root directory (where mkdocs.yaml is located)."""
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Navigate up to find project root
    while current_dir != os.path.dirname(current_dir):  # Stop at filesystem root
        if os.path.exists(os.path.join(current_dir, "mkdocs.yaml")) or \
                os.path.exists(os.path.join(current_dir, "mkdocs.yml")):
            return current_dir
        current_dir = os.path.dirname(current_dir)

    return None


def main():
    """Start the MkDocs server."""
    # Check if mkdocs is installed
    if not is_mkdocs_installed():
        print("Error: MkDocs is not installed. Please install it with:")
        print("  poetry install --with docs")
        return 1

    # Find the project root
    project_root = find_project_root()
    if not project_root:
        print("Error: Could not find project root directory with mkdocs.yaml/yml")
        return 1

    # Find the mkdocs executable
    mkdocs_path = get_mkdocs_path()
    if not mkdocs_path:
        print("Error: Could not find mkdocs executable")
        return 1

    # Change to project root
    os.chdir(project_root)

    # Start the mkdocs server
    print(f"Starting MkDocs server for moduli_generator documentation...")
    try:
        # Pass all command line arguments to mkdocs
        cmd = [mkdocs_path, "serve"]
        # Add any additional arguments passed to this script
        if len(sys.argv) > 1:
            cmd.extend(sys.argv[1:])

        return subprocess.call(cmd)
    except KeyboardInterrupt:
        print("\nMkDocs server stopped")
        return 0


if __name__ == "__main__":
    sys.exit(main())
