def get_version() -> str:
    """
    Retrieves the version information of the project specified in the `pyproject.toml` file.

        This function locates the `pyproject.toml` file in the project root directory and parses it
        to get the project version from the `[project]` section (PEP 621 standard). If the file is not found
        or the version information is missing, it falls back to checking the `[tool.poetry]` section
        for backward compatibility. It requires the `toml` package to be installed for parsing the `pyproject.toml` file.

    Returns:
        str: Project version string as defined in the `pyproject.toml` file.

    Raises:
        RuntimeError: For all other unexpected issues accessing or parsing the file.
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
        with open(pyproject_path, "r") as f:
            pyproject_data = toml.load(f)

        # First try to extract version from the [project] section (PEP 621 standard)
        version = pyproject_data.get("project", {}).get("version")

        # If not found, fall back to [tool.poetry] section for backward compatibility
        if not version:
            version = pyproject_data.get("tool", {}).get("poetry", {}).get("version")

        if not version:
            raise RuntimeError(
                "Version not found in pyproject.toml [project] or [tool.poetry] section."
            )

        return version

    except ImportError:
        raise RuntimeError(
            "toml package is required to read pyproject.toml. Please install it with: pip install toml"
        )
    except Exception as e:
        raise RuntimeError(f"Unable to read version from pyproject.toml: {str(e)}")
