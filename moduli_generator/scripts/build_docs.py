import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Build documentation and include it in the package."""
    project_root = Path(__file__).resolve().parent.parent.parent
    docs_dir = project_root

    # Check if sphinx-build is available
    try:
        subprocess.run(['sphinx-build', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: sphinx-build is not installed or not in PATH.")
        print("Please install it with: pip install sphinx")
        return 1

    # Check if conf.py exists in the docs directory
    if not (docs_dir / 'conf.py').exists():
        print(f"Error: conf.py not found in {docs_dir}")
        print("Make sure you're running this script from the correct directory")
        print("or that your Sphinx documentation is properly set up.")
        return 1

    print("Building HTML documentation...")

    # Build HTML documentation - removing the invalid --ignore-dir flag
    try:
        process = subprocess.run([
            'sphinx-build',
            '-b', 'html',
            '-d', '_build/doctrees',
            '.',
            '_build/html'
        ], cwd=docs_dir, check=True, capture_output=True, text=True)

        # Print output for debugging
        print(process.stdout)

    except subprocess.CalledProcessError as e:
        print(f"Error: Sphinx build failed with exit code {e.returncode}")
        print("Sphinx output:")
        print(e.stdout)
        print("Sphinx errors:")
        print(e.stderr)
        return 1

    # Create a docs directory in the package
    package_docs_dir = project_root / 'doc'
    package_docs_dir.mkdir(exist_ok=True)

    # Copy the built docs into the package
    try:
        shutil.copytree(
            docs_dir / '_build' / 'html',
            package_docs_dir / 'html',
            dirs_exist_ok=True
        )
        print("Documentation built and copied to package successfully!")
        return 0
    except FileNotFoundError as e:
        print(f"Error copying documentation: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
