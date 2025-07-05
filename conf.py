import os
import re
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath('..'))

project = 'Moduli Generator'
exclude_patterns = [
    '.venv',
    'Thumbs.db',
    '.DS_Store'
]

try:
    from moduli_generator import __version__ as version
except ImportError:
    # Fallback to regex extraction
    with open("../pyproject.toml", "r") as f:
        content = f.read()
    version_match = re.search(r'version\s*=\s*"([^"]+)"', content)
    version = version_match.group(1) if version_match else "0.0.0"

# Use for Sphinx
release = version
