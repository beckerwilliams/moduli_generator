#!/usr/bin/env python
"""
Configuration module for the moduli generator project.
Centralizes all default configuration values.
"""
from datetime import (UTC, datetime)
from logging import (DEBUG, basicConfig, getLogger)
from os import environ as osenv
from pathlib import PosixPath as Path
from re import (compile, sub)
from typing import Final


def ISO_UTC_TIMESTAMP(compress: bool = False) -> str:
    """
    Generate an ISO formatted UTC timestamp as a string. Optionally, the timestamp can
    be compressed by enabling the `compress` parameter.

    :param compress: Flag indicating whether the timestamp should be in compressed
        format or not.
    :type compress: Bool
    :return: The ISO 8601 formatted a UTC timestamp as a string. If `compress` is
        True, the string will be in a compressed format (numerals only, no punctuation).
    :rtype: Str
    """

    timestamp = datetime.now(UTC).replace(tzinfo=None).isoformat()
    if compress:
        return sub(r'[^0-9]', '', timestamp)
    else:
        return timestamp


# Moduli Generator Module's directory structure
DEFAULT_DIR: Final[Path] = Path.home() / '.moduli'
DEFAULT_CANDIDATES_DIR: Final[str] = '.candidates'
DEFAULT_MODULI_DIR: Final[str] = '.moduli'
DEFAULT_LOG_DIR: Final[str] = '.logs'

# Location of Moduli Configuration File (tbd - not yet used)
DEFAULT_MODULI_GENERATOR_CONFIG: Final[str] = 'moduli_generator.conf'

# The only log file this module recognizes
DEFAULT_LOG_FILE: Final[str] = 'moduli_generator.log'

# The Product: a Complete ssh-moduli file
DEFAULT_MODULI_FILE: Final[str] = f'ssh-moduli_{ISO_UTC_TIMESTAMP(compress=True)}'

# SSH-KEYGEN Generator settings
DEFAULT_KEY_LENGTHS: Final[tuple[int, ...]] = (3072, 4096, 6144, 7680, 8192)
DEFAULT_GENERATOR_TYPE: Final[int] = 2
DEFAULT_NICE_VALUE: Final[int] = 15
DEFAULT_CONFIG_ID: Final[int] = 1  # JOIN to Moduli File Constants

# MariaDB Configuration File (mysql.cnf)
DEFAULT_MARIADB_CNF: Final[str] = "moduli_generator.cnf"

# Operational Database, Tables, and Views
DEFAULT_MARIADB_DB: Final[str] = 'moduli_db'
DEFAULT_MARIADB_TABLE: Final[str] = 'moduli'
DEFAULT_MARIADB_VIEW: Final[str] = 'moduli_view'

# Screened Moduli File Pattern
DEFAULT_MODULI_FILENAME_PATTERN: Final[str] = r'moduli_????_*'

# The number of moduli per key-length to capture in each produced moduli file
DEFAULT_RECORDS_PER_KEYLENGTH: Final[int] = 2


# For Date Formats Sans Punctuation
def compress_datetime_to_string(timestamp: datetime) -> str:
    """Remove all non-numeric characters from the timestamp string"""
    return sub(r'[^0-9]', '', timestamp.isoformat())


def is_valid_identifier(identifier: str) -> bool:
    """
    Validates whether a string is a valid identifier (database or table name) for MariaDB.

    According to MariaDB naming conventions:
    - Identifiers can contain alphanumeric characters, underscores, and dollar signs
    - Identifiers can be quoted with backticks to allow special characters
    - Identifiers shouldn't be empty or too long (max 64 characters)
    - Identifiers shouldn't be reserved words

    Args:
        identifier (str): The database or table name to validate

    Returns:
        bool: True if the identifier is valid, False otherwise
    """
    if not identifier or not isinstance(identifier, str):
        return False

    # Check for empty string or too long identifier
    if len(identifier) == 0 or len(identifier) > 64:
        return False

    # If the identifier is quoted with backticks, we need different validation
    if identifier.startswith('`') and identifier.endswith('`'):
        # For quoted identifiers, make sure the backticks are properly paired
        # and that the identifier isn't just empty backticks
        return len(identifier) > 2

    # For unquoted identifiers, check that they only contain valid characters
    valid_pattern = compile(r'^[a-zA-Z0-9_$]+$')

    # Validate the pattern
    if not valid_pattern.match(identifier):
        return False

    # MariaDB reserved words could be added here to make the validation stricter
    # For a complete solution, a list of reserved words should be checked

    return True


class ModuliConfig:
    def __init__(self, base_dir=None):
        # Use user-provided base dir, or env var, or default to ~/.moduli_assembly
        self.base_dir = Path(base_dir or osenv.get('MODULI_HOME', DEFAULT_DIR))

        # Define subdirectories as properties
        self.candidates_dir = self.base_dir / DEFAULT_CANDIDATES_DIR
        self.moduli_dir = self.base_dir / DEFAULT_MODULI_DIR
        self.log_dir = self.base_dir / DEFAULT_LOG_DIR

        # Default configuration files
        self.moduli_generator_config = self.base_dir / DEFAULT_MODULI_GENERATOR_CONFIG

        # Default log files
        self.log_file = self.log_dir / DEFAULT_LOG_FILE

        # Default moduli output files
        self.moduli_file = self.moduli_dir / DEFAULT_MODULI_FILE

        # Other defaults (For Generation and Screening, And Linking to Moduli File Constants Table (config_id)
        self.key_lengths = DEFAULT_KEY_LENGTHS
        self.generator_type = DEFAULT_GENERATOR_TYPE
        self.nice_value = DEFAULT_NICE_VALUE

        # Constants joined via this record number in the Constants table
        self.config_id = DEFAULT_CONFIG_ID

        # Default Mariadb Configuration
        self.mariadb_cnf = self.base_dir / DEFAULT_MARIADB_CNF
        self.moduli_file_pattern = DEFAULT_MODULI_FILENAME_PATTERN

        self.db_name = DEFAULT_MARIADB_DB
        self.table_name = DEFAULT_MARIADB_TABLE
        self.view_name = DEFAULT_MARIADB_VIEW
        self.records_per_keylength = DEFAULT_RECORDS_PER_KEYLENGTH

    def ensure_directories(self):
        """Create all required directories if they don't exist"""
        for dir_path in [self.base_dir, self.candidates_dir, self.moduli_dir, self.log_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        return self

    @staticmethod
    def with_base_dir(base_dir):
        """Return a new config instance with a different base directory"""
        return ModuliConfig(base_dir)

    def get_logger(self):

        if not self.base_dir.exists():
            Path(self.base_dir).mkdir(parents=True, exist_ok=True)
        if not (self.base_dir / DEFAULT_LOG_DIR).exists():
            Path(self.base_dir / DEFAULT_LOG_DIR).mkdir(parents=True, exist_ok=True)
        if not self.mariadb_cnf.exists():
            mysql_cnf = Path(DEFAULT_MARIADB_CNF).read_text()
            Path(self.mariadb_cnf).write_text(mysql_cnf)

        basicConfig(
            level=DEBUG,
            format='%(asctime)s - %(levelname)s: %(message)s',
            filename=Path(self.log_file),
            filemode='a'
        )
        return getLogger()

    def get_log_file(self, name):
        """Get a full path to a log file"""
        if name:
            return self.log_dir / name
        else:
            return self.log_file


# Create a default configuration instance
default_config = ModuliConfig().ensure_directories()
