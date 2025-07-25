import os
import sys

try:
    from importlib.metadata import version

    __version__ = version('moduli-generator')  # Replace with your actual package name
except ImportError:
    # Fallback for Python < 3.8
    from importlib_metadata import version

    __version__ = version('moduli-generator')
except Exception:
    # Final fallback to pyproject.toml
    from get_version import get_version

    __version__ = get_version()

version = __version__

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_rtd_theme',  # If you're using the ReadTheDocs theme
]

# Add a project root to the system path
sys.path.insert(0, os.path.abspath('.'))  # Try with the current directory first

project = 'Moduli Generator'
exclude_patterns = [
    '.venv',
    'Thumbs.db',
    '.DS_Store',
    'stash'
]
# TBD Fix Version Path below - Need to import RESOURCES
html_theme = 'sphinx_rtd_theme'

copyright = '2024,2025 Ronald Williams General Partner, Becker Williams General Partnership'
