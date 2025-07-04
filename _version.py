"""Version information."""
import tomllib
from pathlib import PosixPath as Path


def get_version():
    """Read version from pyproject.toml."""
    # Find the project root directory
    current_dir = Path(__file__).resolve().parent
    # Path to pyproject.toml
    pyproject_path = current_dir / 'pyproject.toml'

    try:
        with pyproject_path.open("rb") as ppf:
            pyproject_data = tomllib.load(ppf)
            return pyproject_data["tool"]["poetry"]["version"]
    except (FileNotFoundError, KeyError):
        # Fallback version if pyproject.toml can't be read
        return "1.0.1"


__version__ = get_version()
