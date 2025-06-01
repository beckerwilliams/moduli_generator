# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information ++++++++++++++++++++++++++++++++++++++++++++++++++---
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sys
from pathlib import Path

sys.path.insert(0, str(Path('..', 'moduli_assembly', 'config_manager').resolve()))

project = 'ssh-moduli-builder'
copyright = '2024 Ron Williams <becker.williams@gmail.com>'
author = 'Ron Williams <becker.williams@gmail.com>'
release = '1.0.7'

# -- General configuration ++++++++++++++++++++++++++++++++++++++++++++++++++-
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',
    'sphinx.ext.autodoc'
]
source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '.venv', '.moduli_assembly']

# -- Options for HTML output ++++++++++++++++++++++++++++++++++++++++---------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
