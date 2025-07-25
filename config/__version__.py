from pathlib import Path

import toml


def _get_version_from_pyproject():
    """Get the version from pyproject.toml"""
    project_root = Path(__file__).parent.parent
    pyproject_path = project_root / "pyproject.toml"

    if not pyproject_path.exists():
        raise RuntimeError("pyproject.toml file not found in project root.")

    with open(pyproject_path, 'r') as f:
        pyproject_data = toml.load(f)

    # Try PEP 621 standard first
    project_version = pyproject_data.get('project', {}).get('version')

    # Fall back to the Poetry section
    if not project_version:
        project_version = pyproject_data.get('tool', {}).get('poetry', {}).get('version')

    if not project_version:
        raise RuntimeError("Version not found in pyproject.toml")

    return project_version


version = _get_version_from_pyproject()
