#!/usr/bin/env python
"""
Configuration module for the moduli generator project.
Centralizes all default configuration values.
"""
import re
from datetime import UTC, datetime
from logging import DEBUG, basicConfig, getLogger
from os import environ as osenv
from pathlib import PosixPath as Path
from typing import Final


# Try to get the version from package metadata first
try:
    from importlib.metadata import version

    __version__ = version("moduli_generator")
except ImportError:
    # Fallback for Python < 3.8
    try:
        from importlib_metadata import version

        __version__ = version("moduli_generator")
    except (ImportError, Exception):
        __version__ = None
except Exception:
    __version__ = None

# If package metadata fails, use pyproject.toml fallback
if __version__ is None:
    try:
        from config.get_version import get_version

        __version__ = get_version()
    except Exception as e:
        # Final fallback if all else fails
        __version__ = "0.0.0-dev"

version = __version__

__all__ = [
    "ModuliConfig",
    "default_config",
    "iso_utc_timestamp",
    "iso_utc_time_notzinfo",
    "strip_punction_from_datetime_str",
    "DEFAULT_MARIADB",
    "DEFAULT_MARIADB_CNF",
    "DEFAULT_KEY_LENGTHS",
    "TEST_MARIADB",
    "__version__",
]

# TEST PARAMETERS
TEST_MARIADB: Final[str] = "test_moduli_db"

# Moduli Generator Module's directory structure
DEFAULT_DIR: Final[Path] = Path.home() / ".moduli_generator"
DEFAULT_CANDIDATES_DIR: Final[str] = ".candidates"
DEFAULT_MODULI_DIR: Final[str] = ".moduli"
DEFAULT_LOG_DIR: Final[str] = ".logs"

# The only log file this module recognizes
DEFAULT_LOG_FILE: Final[str] = "moduli_generator.log"

# SSH-KEYGEN Generator settings
DEFAULT_KEY_LENGTHS: Final[tuple[int, ...]] = (3072, 4096, 6144, 7680, 8192)
DEFAULT_GENERATOR_TYPE: Final[int] = 2
DEFAULT_NICE_VALUE: Final[int] = 15
DEFAULT_CONFIG_ID: Final[int] = 1  # JOIN to Moduli File Constants

# MariaDB Configuration File (mysql.cnf)
DEFAULT_MARIADB_CNF: Final[str] = "moduli_generator.cnf"

# Operational Database, Tables, and Views
DEFAULT_MARIADB: Final[str] = "moduli_db"
DEFAULT_MARIADB_TABLE: Final[str] = "moduli"
DEFAULT_MARIADB_VIEW: Final[str] = "moduli_view"

# Flag to Delete Records from Moduli DB after successfully extracting and writing a complete ssh / moduli file
DEFAULT_PRESERVE_MODULI_AFTER_DBSTORE: Final[bool] = True

# Flag to delete records on moduli write
DEFAULT_DELETE_RECORDS_ON_MODULI_WRITE: Final[bool] = False

# Screened Moduli File Pattern
DEFAULT_MODULI_FILENAME_PATTERN: Final[re] = r"moduli_????_*"
DEFAULT_CANDIDATE_IDX_FILENAME_PATTERN: Final[re] = (
    r".candidates_????_????????????????????"
)

DEFAULT_MODULI_PREFIX: Final[str] = f"ssh-moduli_"
# The number of moduli per key-length to capture in each produced moduli file
DEFAULT_MODULI_RECORDS_PER_KEYLENGTH: Final[int] = 20


#  ref: https://x.com/i/grok/share/ioGsEbyEPkRYkfUfPMj1TuHgl


def iso_utc_timestamp(compress: bool = False) -> str:
    """
    Generates a UTC timestamp in ISO 8601 format. Optionally, the output can be compressed
        to remove non-numeric characters.

    Args:
        compress (bool): Specifies whether the timestamp should be compressed by removing         non-numeric characters.

    Returns:
        str: The generated UTC timestamp as a string. If `compress` is True, the         timestamp will only contain numeric characters.
    """

    timestamp = iso_utc_time_notzinfo().isoformat()
    if compress:
        return re.sub(r"[^0-9]", "", timestamp)
    else:
        return timestamp


def iso_utc_time_notzinfo() -> datetime:
    """
    Generates and returns the current time in UTC format, stripped of timezone
        information. This function uses the UTC timezone to fetch the current time
        but removes the timezone information from the resulting datetime object.

    Returns:
        datetime: The current UTC time as a timezone-naive datetime object.
    """
    return datetime.now(UTC).replace(tzinfo=None)


# The Product: a Complete ssh-moduli file
DEFAULT_MODULI_FILE: Final[str] = f"ssh-moduli_{iso_utc_timestamp(compress=True)}"


# For Date Formats Sans Punctuation
def strip_punction_from_datetime_str(timestamp: datetime) -> str:
    """
    Compresses a datetime object into a compact string format by removing non-numeric
        characters from its ISO 8601 format string.

    Args:
        timestamp (Datetime): A datetime object to compress into a string.

    Returns:
        str: A string representation of the given datetime with all non-numeric         characters removed.
    """
    return re.sub(r"[^0-9]", "", timestamp.isoformat())


class ModuliConfig:
    """Class representing the configuration for Moduli generation and management.

    This class is used to define directories, file patterns, database configurations, logging, and
    other essential components required for handling Moduli operations.

    Attributes:
        moduli_home (Path): Base directory for Moduli files, derived from a user-provided path,
            environment variable, or a default directory.
        candidates_dir (Path): Directory for storing candidate files.
        moduli_dir (Path): Directory for storing Moduli files.
        log_dir (Path): Directory for storing log files.
        log_file (Path): Full path to the default log file.
        key_lengths (list): List of default key lengths for Moduli generation.
        generator_type (str): Default generator type used during Moduli generation.
        nice_value (int): Default "nice" value for adjusting process priority.
        db_name (str): Name of the MariaDB database used for storing Moduli data.
        table_name (str): Name of the MariaDB table used for Moduli storage.
        view_name (str): Name of the MariaDB view for querying Moduli data.
        records_per_keylength (int): Number of records generated or stored per key length.
        config_id (int): Unique ID used to link constants in the Moduli file to the database table.
        mariadb_cnf (Path): Path to the MariaDB configuration file.
        moduli_file_pattern (str): Default filename pattern for Moduli files.
        candidate_idx_pattern (str): Default filename pattern for candidate index files.
        moduli_file_pfx (str): Prefix for naming Moduli output files.
        moduli_file (Path): Path to the default Moduli file.
        preserve_moduli_after_dbstore (bool): Flag indicating whether to preserve Moduli files
            after being stored in the database.
        delete_records_on_moduli_write (bool): Flag indicating whether to delete database records
            after writing to Moduli files successfully.
        version (str): The version of the Moduli project.
    """

    def __init__(self, base_dir: str | None = None) -> "ModuliConfig":
        """
        Class representing the configuration for Moduli generation and management. This class is used
        to define directories, file patterns, database configurations, logging, and other essential
        components required for handling Moduli operations.

        Args:
            base_dir (str | None): User-provided base directory for Moduli files. Defaults to an environment
                variable or a pre-defined directory if not specified.
        """
        # Use user-provided base dir, or env var, or default to ~/.moduli_assembly
        self.moduli_home = Path(base_dir or osenv.get("MODULI_HOME", DEFAULT_DIR))

        # Define subdirectories as properties
        self.candidates_dir = self.moduli_home / DEFAULT_CANDIDATES_DIR
        self.moduli_dir = self.moduli_home / DEFAULT_MODULI_DIR
        self.log_dir = self.moduli_home / DEFAULT_LOG_DIR

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
        self.mariadb_cnf = self.moduli_home / DEFAULT_MARIADB_CNF
        self.moduli_file_pattern = DEFAULT_MODULI_FILENAME_PATTERN
        self.candidate_idx_pattern = DEFAULT_CANDIDATE_IDX_FILENAME_PATTERN

        # Default moduli output files
        self.moduli_file_pfx = DEFAULT_MODULI_PREFIX
        self.moduli_file = self.moduli_home / DEFAULT_MODULI_FILE

        # Delete on successful Write Flag
        self.preserve_moduli_after_dbstore = DEFAULT_PRESERVE_MODULI_AFTER_DBSTORE
        self.delete_records_on_moduli_write = DEFAULT_DELETE_RECORDS_ON_MODULI_WRITE

        # Set Project Version Number
        self.version = version

    def ensure_directories(self) -> "ModuliConfig":
        """
        Ensures that a set of directories (base, candidates, moduli, and log directories) exist.
                If they do not exist, they will be created. This method ensures all necessary directories
                are ready for further operations.

        Returns:
            Self: The current instance after ensuring directories exist.
        """
        for dir_path in [
            self.moduli_home,
            self.candidates_dir,
            self.moduli_dir,
            self.log_dir,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

        return self

    def get_logger(self) -> "logging.Logger":
        """
        Initializes and returns a logger instance configured for file-based logging.

                This function ensures that the required directories and configuration files exist
                before setting up the logging system. It verifies the existence of the base logging
                directory, the default log directory, and the MariaDB configuration file. If they do not
                exist, they are created as needed. Once these prerequisites are met, the logger is
                configured with a specific logging level, format, and file output.

        Returns:
            Logging.Logger: Configured logger instance.

        Raises:
            OSError: If there is an issue, create required directories or files.
            IOError: If there is an issue, read the default MariaDB configuration file.
        """

        if not self.moduli_home.exists():
            Path(self.moduli_home).mkdir(parents=True, exist_ok=True)
        if not (self.moduli_home / DEFAULT_LOG_DIR).exists():
            Path(self.moduli_home / DEFAULT_LOG_DIR).mkdir(parents=True, exist_ok=True)

        # Set logging to use UTC time globally
        import logging

        logging.Formatter.converter = lambda *args: datetime.now(UTC).timetuple()

        basicConfig(
            level=DEBUG,
            format="%(asctime)s - %(levelname)s: %(message)s",
            filename=Path(self.log_file),
            filemode="a",
        )
        return getLogger()

    def get_log_file(self, name) -> Path:
        """
        Retrieve the log file path, either by name or default log file path.

                This method determines whether a specific log file name is provided. If a
                name is given, the method constructs and returns the full path to the named
                log file within the logging directory. If no name is provided, it returns the
                path to the default log file.

        Args:
            name (Optional[str]): Name of the log file to retrieve. If None, the default log file             path is returned.

        Returns:
            Path: The full path to the specified log file if a name is provided, or             the default log file path otherwise.
        """
        if name:
            return self.log_dir / name
        else:
            return self.log_file

    @staticmethod
    def with_base_dir(base_dir) -> "ModuliConfig":
        """
        Creates a new instance of ModuliConfig with the given base directory.

                This static method provides a convenience to instantiate the ModuliConfig
                class with a specified base directory. It ensures that the provided base
                directory is explicitly set during the object creation.

        Args:
            base_dir (str): The base directory to be used for initialization.

        Returns:
            ModuliConfig: A new instance of the ModuliConfig class initialized with the given             base directory.
        """
        return ModuliConfig(base_dir)

    @property
    def __version__(self) -> str:
        return self.version


# Create a default configuration instance
default_config = ModuliConfig().ensure_directories()
