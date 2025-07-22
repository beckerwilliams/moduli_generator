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

from .__version__ import version

__all__ = [
    'ModuliConfig',
    'default_config',
    'ISO_UTC_TIMESTAMP',
    'strip_punction_from_datetime_str',
    'is_valid_identifier_sql',
    'DEFAULT_MARIADB',
    'DEFAULT_MARIADB_CNF',
    'DEFAULT_KEY_LENGTHS',
    'TEST_MARIADB'
]

# TEST PARAMETERS
TEST_MARIADB: Final[str] = 'test_moduli_db'

# Moduli Generator Module's directory structure
DEFAULT_DIR: Final[Path] = Path.home() / '.moduli_generator'
DEFAULT_CANDIDATES_DIR: Final[str] = '.candidates'
DEFAULT_MODULI_DIR: Final[str] = '.moduli'
DEFAULT_LOG_DIR: Final[str] = '.logs'
# The only log file this module recognizes
DEFAULT_LOG_FILE: Final[str] = 'moduli_generator.log'
# SSH-KEYGEN Generator settings
DEFAULT_KEY_LENGTHS: Final[tuple[int, ...]] = (3072, 4096, 6144, 7680, 8192)
DEFAULT_GENERATOR_TYPE: Final[int] = 2
DEFAULT_NICE_VALUE: Final[int] = 15
DEFAULT_CONFIG_ID: Final[int] = 1  # JOIN to Moduli File Constants
# MariaDB Configuration File (mysql.cnf)
DEFAULT_MARIADB_CNF: Final[str] = "moduli_generator.cnf"
# Operational Database, Tables, and Views
DEFAULT_MARIADB: Final[str] = 'moduli_db'
DEFAULT_MARIADB_TABLE: Final[str] = 'moduli'
DEFAULT_MARIADB_VIEW: Final[str] = 'moduli_view'
# Flag to Delete Records from Moduli DB after successfully extracting and writing a complete ssh / moduli file
DEFAULT_DELETE_RECORDS_ON_MODULI_WRITE: Final[bool] = False  # tbd - set to TRUE before Production Release
# Screened Moduli File Pattern
DEFAULT_MODULI_FILENAME_PATTERN: Final[str] = r'moduli_????_*'
DEFAULT_MODULI_PREFIX: Final[str] = f'ssh-moduli_'
# The number of moduli per key-length to capture in each produced moduli file
DEFAULT_MODULI_RECORDS_PER_KEYLENGTH: Final[int] = 20


#  ref: https://x.com/i/grok/share/ioGsEbyEPkRYkfUfPMj1TuHgl

def ISO_UTC_TIMESTAMP(compress: bool = False) -> str:
    """
    Generate an ISO formatted UTC timestamp as a string. Optionally, the timestamp can
    be compressed by enabling the `compress` parameter.

    :param compress: Flag indicating whether the timestamp should be in compressed
        format or not.
    :type compress: Bool
    :return: The ISO 8601 formatted a UTC timestamp as a string. If `compress` is
        True, the string will be in a compressed format (numerals only, no punctuation).
    :rtype: str
    """

    timestamp = datetime.now(UTC).replace(tzinfo=None).isoformat()
    if compress:
        return sub(r'[^0-9]', '', timestamp)
    else:
        return timestamp


# The Product: a Complete ssh-moduli file
DEFAULT_MODULI_FILE: Final[str] = f'ssh-moduli_{ISO_UTC_TIMESTAMP(compress=True)}'


##################################################################################


# For Date Formats Sans Punctuation
def strip_punction_from_datetime_str(timestamp: datetime) -> str:
    """
    Compresses a datetime object into a compact string format by removing non-numeric
    characters from its ISO 8601 format string.

    :param timestamp: A datetime object to compress into a string.
    :type timestamp: Datetime
    :return: A string representation of the given datetime with all non-numeric
        characters removed.
    :rtype: str
    """
    return sub(r'[^0-9]', '', timestamp.isoformat())


def is_valid_identifier_sql(identifier: str) -> bool:
    """
    Determines if the given string is a valid identifier following specific
    rules. Valid identifiers must either be unquoted strings containing only
    alphanumeric characters, underscores, and dollar signs, or quoted strings
    wrapped in backticks with proper pairing. Additionally, identifiers must not
    exceed 64 characters.

    :param identifier: The identifier string to validate.
    :type identifier: str
    :return: True if the identifier is valid, otherwise False.
    :rtype: Bool
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
    """
    Represents a configuration structure for moduli assembly, encompassing paths,
    logs, database configurations, and default settings.

    This class provides directory management, default file paths, and configuration
    for moduli generation and related operations. It ensures the existence of required
    directories and offers methods for logging and configuration handling.

    :ivar base_dir: The root directory for all moduli-related operations, derived
         from the provided `base_dir` parameter or environment variables.
    :type base_dir: Path
    :ivar candidates_dir: The directory path designated for candidate files
         involved in the moduli assembly process.
    :type candidates_dir: Path
    :ivar moduli_dir: The directory for storing generated moduli files.
    :type moduli_dir: Path
    :ivar log_dir: The directory housing log files for the moduli assembly process.
    :type log_dir: Path
    :ivar moduli_generator_config: Path to the default moduli generator
         configuration file.
    :type moduli_generator_config: Path
    :ivar log_file: Default log file path.
    :type log_file: Path
    :ivar moduli_file: Default path for storing the primary moduli output file.
    :type moduli_file: Path
    :ivar key_lengths: Default key lengths used during moduli generation.
    :type key_lengths: list[int]
    :ivar generator_type: Type of generator used for moduli generation.
    :type generator_type: str
    :ivar nice_value: Default nice value for process prioritization.
    :type nice_value: int
    :ivar config_id: Identifier used to associate constants with configuration
         tables.
    :type config_id: str
    :ivar mariadb_cnf: Path to the MariaDB configuration file used during moduli
         assembly.
    :type mariadb_cnf: Path
    :ivar moduli_file_pattern: Filename pattern for generated moduli files.
    :type moduli_file_pattern: str
    :ivar delete_records_on_moduli_write: Flag indicating whether records should
         be deleted upon a successful moduli file write operation.
    :type delete_records_on_moduli_write: bool
    :ivar db_name: Default database name for MariaDB configurations.
    :type db_name: str
    :ivar table_name: Name of the table used in the database for moduli record
         storage.
    :type table_name: str
    :ivar view_name: Name of the database view associated with moduli records.
    :type view_name: str
    :ivar records_per_keylength: Number of records associated with each
         key length in the moduli assembly process.
    :type records_per_keylength: int
    :ivar version: Current version of the moduli configuration as derived
         from the `pyproject.toml`.
    :type version: str
    """

    def __init__(self, base_dir=None):
        """
        Represents a configuration and directory structure for moduli assembly
        operation, including paths for candidate files, moduli files, logs, and
        default configurations.

        Provides default values and configurations for various parameters related
        to moduli generation and database management.

        :param base_dir: The base directory path for moduli assembly operations. If not provided,
            defaults to the environment variable 'MODULI_HOME' or a preset default directory.
        :type base_dir: Path or None
        """
        # Use user-provided base dir, or env var, or default to ~/.moduli_assembly
        self.base_dir = Path(base_dir or osenv.get('MODULI_HOME', DEFAULT_DIR))

        # Define subdirectories as properties
        self.candidates_dir = self.base_dir / DEFAULT_CANDIDATES_DIR
        self.moduli_dir = self.base_dir / DEFAULT_MODULI_DIR
        self.log_dir = self.base_dir / DEFAULT_LOG_DIR

        # Default log files
        self.log_file = self.log_dir / DEFAULT_LOG_FILE

        # Other defaults (For Generation and Screening, And Linking to Moduli File Constants Table (config_id)
        self.key_lengths = DEFAULT_KEY_LENGTHS
        self.generator_type = DEFAULT_GENERATOR_TYPE
        self.nice_value = DEFAULT_NICE_VALUE

        # Configure MariaDB
        self.db_name = DEFAULT_MARIADB
        self.table_name = DEFAULT_MARIADB_TABLE
        self.view_name = DEFAULT_MARIADB_VIEW
        self.records_per_keylength = DEFAULT_MODULI_RECORDS_PER_KEYLENGTH

        # Constants joined via this record number in the Constants table
        self.config_id = DEFAULT_CONFIG_ID

        # Default Mariadb Configuration
        self.mariadb_cnf = self.base_dir / DEFAULT_MARIADB_CNF
        self.moduli_file_pattern = DEFAULT_MODULI_FILENAME_PATTERN

        # Default moduli output files
        self.moduli_file_pfx = DEFAULT_MODULI_PREFIX

        # Delete on successful Write Flag
        self.delete_records_on_moduli_write = DEFAULT_DELETE_RECORDS_ON_MODULI_WRITE

        # From pyproject.toml
        # version_path = Path(self.base_dir) / 'config' / '__version__.py'
        self.version = version

    def ensure_directories(self):
        """
        Ensures that a set of directories (base, candidates, moduli, and log directories) exist.
        If they do not exist, they will be created. This method ensures all necessary directories
        are ready for further operations.

        :return: The current instance after ensuring directories exist.
        :rtype: Self
        """
        for dir_path in [self.base_dir, self.candidates_dir, self.moduli_dir, self.log_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        return self

    def get_logger(self):
        """
        Initializes and returns a logger instance configured for file-based logging.

        This function ensures that the required directories and configuration files exist
        before setting up the logging system. It verifies the existence of the base logging
        directory, the default log directory, and the MariaDB configuration file. If they do not
        exist, they are created as needed. Once these prerequisites are met, the logger is
        configured with a specific logging level, format, and file output.

        :raises OSError: If there is an issue, create required directories or files.
        :raises IOError: If there is an issue, read the default MariaDB configuration file.

        :return: Configured logger instance.
        :rtype: Logging.Logger
        """

        if not self.base_dir.exists():
            Path(self.base_dir).mkdir(parents=True, exist_ok=True)
        if not (self.base_dir / DEFAULT_LOG_DIR).exists():
            Path(self.base_dir / DEFAULT_LOG_DIR).mkdir(parents=True, exist_ok=True)

        # Set logging to use UTC time globally
        import logging
        logging.Formatter.converter = lambda *args: datetime.now(UTC).timetuple()

        basicConfig(
            level=DEBUG,
            format='%(asctime)s - %(levelname)s: %(message)s',
            filename=Path(self.log_file),
            filemode='a'
        )
        return getLogger()

    def get_log_file(self, name):
        """
        Retrieve the log file path, either by name or default log file path.

        This method determines whether a specific log file name is provided. If a
        name is given, the method constructs and returns the full path to the named
        log file within the logging directory. If no name is provided, it returns the
        path to the default log file.

        :param name: Name of the log file to retrieve. If None, the default log file
            path is returned.
        :type name: Optional[str]
        :return: The full path to the specified log file if a name is provided, or
            the default log file path otherwise.
        :rtype: Path
        """
        if name:
            return self.log_dir / name
        else:
            return self.log_file

    @staticmethod
    def with_base_dir(base_dir):
        """
        Creates a new instance of ModuliConfig with the given base directory.

        This static method provides a convenience to instantiate the ModuliConfig
        class with a specified base directory. It ensures that the provided base
        directory is explicitly set during the object creation.

        :param base_dir: The base directory to be used for initialization.
        :type base_dir: str
        :return: A new instance of the ModuliConfig class initialized with the given
            base directory.
        :rtype: ModuliConfig
        """
        return ModuliConfig(base_dir)

    @property
    def __version__(self):
        return self.version


# Create a default configuration instance
default_config = ModuliConfig().ensure_directories()
