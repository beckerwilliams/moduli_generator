import os
import sys


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
    '.DS_Store'
]

html_theme = 'sphinx_rtd_theme'

copyright = '2024,2025 Ron Williams'

release = (Path('config') / '__version__.py').read_text().strip()

version = release