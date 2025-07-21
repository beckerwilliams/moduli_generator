#!/usr/bin/env python
import concurrent.futures
import logging
import subprocess
from json import dump
from pathlib import PosixPath as Path
from typing import (Any, Dict, List)

from mariadb import (Error)

from config import (ISO_UTC_TIMESTAMP, default_config)
from db import MariaDBConnector

__all__ = ['ModuliGenerator', 'LoggerWriter']


class LoggerWriter:
    """
    A class that bridges a logger and writable interface.

    LoggerWriter acts as a writable stream that funnels written input to the
    specified logger, making it compatible with interfaces that expect a writable
    object (e.g., sys.stdout or sys.stderr redirection). This allows messages to
    be logged through standard Python logging instead of directly to the console.

    :ivar logger: The logging.Logger instance is used for logging messages.
    :type logger: logging.Logger
    :ivar level: The log level used when logging messages.
    :type level: int
    """

    def __init__(self, logger, level):
        """
        Initializes an instance of a logging class with a specified logger and logging level.

        :param logger: The logging instance to be used for log outputs.
        :param level: The logging level to determine what messages to log.
        """
        self.logger = logger
        self.level = level

    def write(self, message):
        """
        Writes a log message using the configured logging level.

        This method logs the given message using the specified logging level
        and returns the number of characters in the message. Empty or
        whitespace-only messages are excluded from logging.

        :param message: The message string to be logged.
        :type message: str

        :return: The length of the provided message.
        :rtype: int
        """
        if message.strip():  # Only log non-empty lines
            self.logger.log(self.level, message.strip())
        return len(message)

    def flush(self):
        """
        Flush the current state, performing any necessary cleanup or finalization.
        
        For this implementation, no actual flushing is needed since we're logging
        each message immediately, but this method is required to satisfy the 
        file-like interface that the subprocess expects.

        :return: None
        :rtype: None
        """
        pass


class ModuliGenerator:
    """
    Handles the generation, screening, and management of cryptographic modulus files
    used for secure communications. This class provides methods for generating
    moduli candidates, screening them for validity, and organizing them into
    structured formats.

    This utility is intended for cryptographic security operations, where moduli
    are required for operations like key exchange. It uses external tools like
    `ssh-keygen` for candidate generation and screening processes.

    :ivar config: The configuration object contains paths and settings such as
        directory paths and security-related configurations.
    :type config: Configuration
    :ivar version: The version of the moduli generator settings.
    :type version: str
    :ivar logger: The logger used for logging information, warnings, and errors
        during execution.
    :type logger: Logger
    :ivar db: Lazily instantiated attribute for database storage of moduli,
        created as needed.
    :type db: Optional[Any]
    """

    def __init__(self, conf=default_config):
        """
        Initializes the class with a configuration object. This configuration includes
        various paths and settings necessary for operation, such as directories for
        modules, log files, and the MariaDB configuration. Also sets up a logger
        specifically configured for the application and logs the key paths in use.

        The class maintains an internal placeholder for the database instance, which
        is not initialized until required.

        :param conf: Configuration object to initialize the instance. It contains
                     paths and settings used for logging, database configurations,
                     and other operational needs.
        :type conf: Object
        """
        self.config = conf
        self.version = conf.version
        self.logger = self.config.get_logger()
        self.logger.name = __name__

        # Log paths used
        if self.config:
            for path_name, path_obj in [
                ('Base directory', self.config.moduli_dir),
                ('Candidates directory', self.config.candidates_dir),
                ('Moduli directory', self.config.moduli_dir),
                ('Log directory', self.config.log_dir),
                ('MariaDB config', self.config.mariadb_cnf)
            ]:
                self.logger.info(f'Using {path_name}: {path_obj}')

        # Store config for lazy DB initialization instead of creating a connection here
        self._db = None

    @property
    def db(self):
        """
        Lazy initialization of the database connection property.

        This property ensures that the database connection is initialized only once,
        upon first access, and then reused for subsequent operations.

        :return: Initialized database connection object.
        :rtype: MariaDBConnector
        """
        if self._db is None:
            self._db = MariaDBConnector(self.config)
        return self._db

    @property
    def __version__(self):
        """
        Represents the version property of a class that retrieves
        the version information of the instance.

        This property is read-only and provides access to the internal
        `version` attribute of the class instance.

        :return: Current version of the instance.
        :rtype: str
        """
        return self.version

    @staticmethod
    def _generate_candidates_static(config, key_length: int) -> Path:
        """
        Generates candidate key files for the given key length and configuration using the
        `ssh-keygen` tool. This method works as a utility function to create files with
        potential cryptographic moduli that can be further processed.
        """
        candidates_file = config.candidates_dir / f'candidates_{key_length}_{ISO_UTC_TIMESTAMP(compress=True)}'
        logger = config.get_logger()

        try:
            # Generate moduli candidates with text capture
            result = subprocess.run([
                'nice', '-n', str(config.nice_value),
                'ssh-keygen',
                '-M', 'generate',
                '-O', f'bits={key_length}',
                str(candidates_file)
            ], check=True, capture_output=True, text=True)

            # Log the output after successful completion
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        logger.info(line.strip())

            if result.stderr:
                for line in result.stderr.strip().split('\n'):
                    if line.strip():
                        logger.debug(line.strip())

            return candidates_file

        except subprocess.CalledProcessError as err:
            # Log any captured output from the failed process
            if err.stdout:
                for line in err.stdout.strip().split('\n'):
                    if line.strip():
                        logger.error(f"stdout: {line.strip()}")

            if err.stderr:
                for line in err.stderr.strip().split('\n'):
                    if line.strip():
                        logger.error(f"stderr: {line.strip()}")

            logger.error(f'ssh-keygen generate failed for {key_length} bits: {err}')
            raise err

    @staticmethod
    def _screen_candidates_static(config, candidates_file: Path) -> Path:
        """
        Screen candidate moduli files using provided configuration and the `ssh-keygen` tool.
        """
        screened_file = config.moduli_dir / f'{candidates_file.name.replace('candidates', 'moduli')}'
        logger = config.get_logger()

        try:
            checkpoint_file = config.candidates_dir / f".{candidates_file.name}"
            result = subprocess.run([
                'nice', '-n', str(config.nice_value),
                'ssh-keygen',
                '-M', 'screen',
                '-O', f'generator={config.generator_type}',
                '-O', f'checkpoint={str(checkpoint_file)}',
                '-f', str(candidates_file),
                str(screened_file)
            ], check=True, capture_output=True, text=True)

            # Log the output after successful completion
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        logger.info(line.strip())

            if result.stderr:
                for line in result.stderr.strip().split('\n'):
                    if line.strip():
                        logger.debug(line.strip())

            # Cleanup used Moduli Candidates
            candidates_file.unlink()
            return screened_file

        except subprocess.CalledProcessError as err:
            # Log any captured output from the failed process
            if err.stdout:
                for line in err.stdout.strip().split('\n'):
                    if line.strip():
                        logger.error(f"stdout: {line.strip()}")

            if err.stderr:
                for line in err.stderr.strip().split('\n'):
                    if line.strip():
                        logger.error(f"stderr: {line.strip()}")

            logger.error(f'ssh-keygen screen failed for {candidates_file}: {err}')
            raise err

    def _generate_candidates(self, key_length: int) -> Path:
        """
        Generates candidate cryptographic keys of a specified length.

        This method internally uses a static method to generate candidate keys
        based on the provided key length and configuration. Logs the result of
        the operation and handles subprocess errors.

        :param key_length: Length of the key in bits to be generated.
        :type key_length: int
        :return: Path to the generated candidate keys.
        :rtype: Path
        :raises subprocess.CalledProcessError: If the candidate generation fails.
        """
        try:
            result = self._generate_candidates_static(self.config, key_length)
            self.logger.info(f'Generated candidate file for {key_length} bits')
            return result
        except subprocess.CalledProcessError as err:
            self.logger.error(f'Candidate generation failed for {key_length}: {err}')
            raise err

    def _screen_candidates(self, candidates_file: Path) -> Path:
        """
        Screens the provided candidates file by applying a static screening process defined in the configuration.

        The method attempts to process the given candidates file using a static screening function.
        If the process executes successfully, the screened result is logged and returned.
        In case of failure, the error is logged and re-raised for further handling.

        :param candidates_file: Path to the file containing the moduli candidates to be screened.
        :type candidates_file: Path
        :return: Path to the screened candidates file.
        :rtype: Path
        """
        try:
            result = self._screen_candidates_static(self.config, candidates_file)
            self.logger.debug(f'Screened candidate files: {result}')
            return result
        except subprocess.CalledProcessError as e:
            self.logger.error(f'Screening failed for {candidates_file}: {e}')
            raise e

    def _parse_moduli_files(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Parses the moduli files to extract specific data entries and formats them
        into a dictionary structure for further processing. This method iterates
        over a set of screened files, reads their contents line by line, and
        extracts information about timestamp, key size, and modulus if the line
        meets specific criteria.

        :return: A dictionary with parsed moduli data under the key
                 'screened_moduli'. Each entry is a dictionary containing
                 'timestamp', 'key-size', and 'modulus'.
        :rtype: Dict[str, List[Dict[str, Any]]]
        """

        screened_files = self._list_moduli_files()
        screened_moduli = {}

        for file in screened_files:
            try:
                with file.open('r') as f:
                    for line in f:
                        if line.startswith('#') or not line.strip():
                            continue

                        parts = line.split()
                        if len(parts) == 7:
                            moduli_entry = {
                                'timestamp': parts[0],  # TIMESTAMP
                                # 'type': parts[1],         # Constant, Stored in moduli_db.mod_fl_consts
                                # 'tests': parts[2],        # Constant, Stored in moduli_db.mod_fl_consts
                                # 'trials': parts[3],       # Constant, Stored in moduli_db.mod_fl_consts
                                'key-size': parts[4],  # KEY_LENGTH
                                # 'generator': parts[5], # Constant, Stored in moduli_db.mod_fl_consts
                                'modulus': parts[6]  # MODULUS
                            }

                            screened_moduli.setdefault('screened_moduli', []).append(moduli_entry)

            except FileNotFoundError:
                self.logger.warning(f'Moduli file not found: {file}')

        return screened_moduli

    def _list_moduli_files(self):
        """
        Lists all moduli files based on the configured moduli directory and file
        pattern.

        This function retrieves and returns a list of all files in the
        configured moduli directory that match the specified file pattern.

        :return: List of matching moduli files
        :rtype: list[Path]
        """
        return list(self.config.moduli_dir.glob(self.config.moduli_file_pattern))

    def generate_moduli(self) -> Dict[int, List[Path]]:
        """
        Generates and screens Diffie-Hellman moduli files for specified key lengths.

        The method first generates candidate files for Diffie-Hellman moduli in parallel
        using a process pool. Next, it screens these candidates to produce final moduli
        files. Generated moduli are organized by key lengths. The candidate and moduli
        generations are logged for debugging purposes.

        :return: self
        :rtype: ModuliGenerator
        """
        generated_moduli = {}

        with concurrent.futures.ProcessPoolExecutor() as executor:
            # First, generate candidates
            candidate_futures = []
            for length in self.config.key_lengths:
                future = executor.submit(self._generate_candidates_static, self.config, length)
                candidate_futures.append((future, length))

            # Process completed futures and organized candidates by key length
            candidates_by_length = {}
            for future, length in candidate_futures:
                candidate_file = future.result()
                if length not in candidates_by_length:
                    candidates_by_length[length] = []
                candidates_by_length[length].append(candidate_file)
            self.logger.debug(
                f'Generated {len(candidates_by_length)} candidate files for each of the following key-lengths: {self.config.key_lengths}')

            # Then screen candidates
            screening_futures = []
            for length, candidate_files in candidates_by_length.items():
                for candidate_file in candidate_files:
                    future = executor.submit(self._screen_candidates_static, self.config, candidate_file)
                    screening_futures.append((future, length))
            # Process completed screening futures
            for future, length in screening_futures:
                moduli_file = future.result()
                if length not in generated_moduli:
                    generated_moduli[length] = []
                generated_moduli[length].append(moduli_file)
            self.logger.debug(f'Screened {len(screening_futures)} candidate files ' +
                              f'key-lengths: {self.config.key_lengths}')

        return self

    def save_moduli(self, moduli_file_dir: Path = None):
        """
        Saves the processed moduli data to a JSON file in the specified directory or a default location.

        This method processes the moduli data and writes the output as a JSON file. If no directory is
        provided, the JSON file is saved in the default base directory specified in the configuration.
        The filename includes a timestamp in ISO UTC format to ensure a unique name.

        :param moduli_file_dir: Directory where the moduli JSON file should be saved. If not specified,
                                the default base directory from the configuration is used.
        :type moduli_file_dir: Path, optional
        :return: self
        :rtype: ModuliGenerator
        """
        if not moduli_file_dir:
            moduli_file_dir = self.config.base_dir

        moduli_json = moduli_file_dir / f'screened_moduli_{ISO_UTC_TIMESTAMP(True)}.json'
        with moduli_json.open('w') as f:
            # with open(moduli_json, 'w') as f:
            dump(self._parse_moduli_files(), f, indent=2)

        self.logger.info(f'Moduli schema saved to {self.config.moduli_dir / moduli_json}')

        return self

    def store_moduli(self):
        """
        Parse, validate, and store screened moduli into the database and manage their source
        files once the operation is successful. This function ensures that the moduli records
        are stored transactionally. After successful storage, the source files are deleted.

        :return: self
        :rtype: ModuliGenerator
        """
        screened_moduli = self._parse_moduli_files()

        try:
            self.db.export_screened_moduli(screened_moduli)

        except Error as err:
            self.logger.error(f'Error storing moduli: {err}')

        moduli_files = self._list_moduli_files()
        for file in moduli_files:
            file.unlink()

        self.logger.info(f'Moduli Files Parsed & Stored in MariaDB database: {moduli_files}')

        return self

    def write_moduli_file(self) -> None:
        """
        Writes the moduli file using the database interface.

        This method retrieves data necessary for the moduli file from the
        database and then writes it to the appropriate location using
        the database interface.

        :return: self
        :rtype: ModuliGenerator
        """
        try:
            self.db.write_moduli_file()

        except RuntimeError as err:
            self.logger.info(err)

        return self
