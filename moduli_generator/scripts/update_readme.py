#!/usr/bin/env python3
"""
Update README.rst with current Python package requirements from pyproject.toml
"""

import re
from pathlib import Path

import toml


def load_pyproject_toml(project_root: Path) -> dict:
    """Load and parse pyproject.toml file."""
    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.exists():
        raise FileNotFoundError(f"pyproject.toml not found at {pyproject_path}")

    with open(pyproject_path, 'r', encoding='utf-8') as f:
        return toml.load(f)


def format_dependencies(dependencies: dict, title: str) -> str:
    """Format dependencies into RST format."""
    if not dependencies:
        return ""

    lines = [f"    {title}:", ""]

    for package, version in dependencies.items():
        # Format version constraints nicely
        if isinstance(version, str):
            version_str = version
        else:
            version_str = str(version)

        lines.append(f"    - **{package}** {version_str}")

    return "\n".join(lines) + "\n"


def extract_requirements_section(pyproject_data: dict) -> str:
    """Extract and format all dependencies from pyproject.toml."""
    sections = []

    # Main dependencies
    if 'tool' in pyproject_data and 'poetry' in pyproject_data['tool']:
        poetry_config = pyproject_data['tool']['poetry']

        if 'dependencies' in poetry_config:
            main_deps = poetry_config['dependencies'].copy()
            # Remove python version requirement as it's handled separately
            python_version = main_deps.pop('python', None)

            if python_version:
                sections.append(f"    **Python Version:** {python_version}")
                sections.append("")

            if main_deps:
                sections.append(format_dependencies(main_deps, "Runtime Dependencies"))

        # Development dependencies
        if 'group' in poetry_config and 'dev' in poetry_config['group']:
            dev_deps = poetry_config['group']['dev'].get('dependencies', {})
            if dev_deps:
                sections.append(format_dependencies(dev_deps, "Development Dependencies"))

    return "\n".join(sections)


def update_readme_requirements(project_root: Path) -> bool:
    """Update README.rst with current requirements from pyproject.toml."""
    readme_path = project_root / "README.rst"
    if not readme_path.exists():
        raise FileNotFoundError(f"README.rst not found at {readme_path}")

    # Load pyproject.toml
    pyproject_data = load_pyproject_toml(project_root)

    # Generate new requirements section
    new_requirements = extract_requirements_section(pyproject_data)

    # Read current README
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define the pattern to match the Python Requirements section
    pattern = r'(Python Requirements\s*\n\s*.*?)(    The following Python packages are required.*?)(    All Python dependencies are managed through Poetry.*?poetry install.*?``)'

    # Replacement text
    replacement = f"""Python Requirements
    The following Python packages are required (automatically installed via Poetry):

{new_requirements}
    All Python dependencies are managed through Poetry and will be installed automatically when you run ``poetry install``."""

    # Perform the replacement
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # Check if any changes were made
    if new_content == content:
        # If no match found, try to find just the Python Requirements section
        alt_pattern = r'(Python Requirements\s*\n\s*.*?)(    The following Python packages.*?)(\n\n|$)'
        if re.search(alt_pattern, content, flags=re.DOTALL):
            new_content = re.sub(alt_pattern, replacement + '\n\n', content, flags=re.DOTALL)
        else:
            print("Warning: Could not find Python Requirements section in README.rst")
            return False

    # Write the updated content back
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True


def main():
    """Main function to update README requirements."""
    try:
        # Get project root (assumes script is run from project root or subdirectory)
        current_dir = Path.cwd()

        # Try to find pyproject.toml in current directory or parent directories
        project_root = current_dir
        while project_root != project_root.parent:
            if (project_root / "pyproject.toml").exists():
                break
            project_root = project_root.parent
        else:
            raise FileNotFoundError("Could not find pyproject.toml in current directory or parent directories")

        print(f"Found project root at: {project_root}")

        # Update README
        if update_readme_requirements(project_root):
            print("✅ Successfully updated README.rst with current requirements from pyproject.toml")
        else:
            print("❌ Failed to update README.rst")
            return 1

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
