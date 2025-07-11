import os
import sys

from moduli_generator.version import get_version

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'myst_parser',  # If you're using MyST markdown
    'sphinx_rtd_theme',  # If you're using the ReadTheDocs theme
]

# Add a project root to the system path
sys.path.insert(0, os.path.abspath('.'))  # Try with the current directory first

project = 'Moduli Generator'
exclude_patterns = [
    '.venv',
    'Thumbs.db',
    '.DS_Store'
]

html_theme = 'sphinx_rtd_theme'

release = get_version()