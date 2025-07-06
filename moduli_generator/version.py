import tomllib
from pathlib import PosixPath as Path


def get_version() -> str:
    """
    Retrieves the version of the package from the pyproject.toml file.

    The method locates the `pyproject.toml` file from the parent directory of
    the current module and parses it to extract the version specified under
    `tool.poetry.version`. If the file is not found or the version is not
    specified correctly, an exception is raised.

    :return: The version of the package as specified in the pyproject.toml file
    :rtype: str
    :raises RuntimeError: If the pyproject.toml file can't be found or the version
        string is not specified.
    """
    current_dir = Path(__file__).resolve().parent.parent
    pyproject_path = current_dir / 'pyproject.toml'

    try:
        with pyproject_path.open("rb") as ppf:
            pyproject_data = tomllib.load(ppf)

    except (FileNotFoundError, KeyError):
        raise RuntimeError("Unable to find moduli_generator/version.py string.")

    return pyproject_data["tool"]["poetry"]["version"]


if __name__ == "__main__":
    print(get_version())
