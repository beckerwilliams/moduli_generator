# tbd - this is cleaner than change log . . . lets simplify and incorporate!
def get_version() -> str:
    """
    Retrieves the version information of the project specified in the `pyproject.toml` file.

    This function locates the `pyproject.toml` file in the project root directory and parses it
    to get the project version from the `[tool.poetry]` section. If the file is not found
    or the version information is missing, an appropriate error is raised. It requires the `toml`
    package to be installed for parsing the `pyproject.toml` file.

    :raises RuntimeError: If the `pyproject.toml` file is not found, if the version cannot be
        retrieved from the `[tool.poetry]` section, or if the `toml` package is not installed.
    :raises RuntimeError: For all other unexpected issues accessing or parsing the file.
    :return: Project version string as defined in the `pyproject.toml` file.
    :rtype: str
    """
    try:
        import toml
        from pathlib import Path

        # Get the project root directory (assuming config.py is in moduli_generator/)
        project_root = Path(__file__).parent.parent
        pyproject_path = project_root / "pyproject.toml"

        if not pyproject_path.exists():
            raise RuntimeError("pyproject.toml file not found in project root.")

        # Parse the TOML file
        with open(pyproject_path, 'r') as f:
            pyproject_data = toml.load(f)

        # Extract version from the [tool.poetry] section
        version = pyproject_data.get('tool', {}).get('poetry', {}).get('version')

        if not version:
            raise RuntimeError("Version not found in pyproject.toml [tool.poetry] section.")

        return version

    except ImportError:
        raise RuntimeError("toml package is required to read pyproject.toml. Please install it with: pip install toml")
    except Exception as e:
        raise RuntimeError(f"Unable to read version from pyproject.toml: {str(e)}")

