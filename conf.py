# Configuration file for the Sphinx documentation builder.
#
project = 'moduli_generator'
copyright = '2025 Ron Williams <becker.williams@gmail.com>'
author = 'Ron Williams <becker.williams@gmail.com>'
release = '2.0.15'

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
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '.venv', '.moduli_assembly', '.github']

html_theme = 'alabaster'
html_static_path = ['_static']
