#!/usr/bin/env python
import concurrent.futures
import subprocess
from json import dump
from pathlib import PosixPath as Path
from typing import (Any, Dict, List)

from mariadb import Error

from config import (ISO_UTC_TIMESTAMP, default_config)
from db.moduli_db_utilities import MariaDBConnector

__all__ = ['ModuliGenerator']


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

        # Store config for lazy DB initialization instead of creating connection here
        self._db = None

    @property
    def db(self):
        """Lazy initialization of database connection."""
        if self._db is None:
            self._db = MariaDBConnector(self.config)
        return self._db

    @property
    def __version__(self):
        """
        Provides an accessor for the version of the object.

        The **__version__.py** property allows retrieval of the current version or
        state of an object. The value returned by this property is generally
        used for keeping track of versioning or specific configurations.

        :return: The version attribute of the object.
        :rtype: str
        """
        return self.version

    @staticmethod
    def _generate_candidates_static(config, key_length: int) -> Path:
        """
        Static method for generating candidates - can be pickled for multiprocessing.
        """
        candidates_file = config.candidates_dir / f'candidates_{key_length}_{ISO_UTC_TIMESTAMP(compress=True)}'

        try:
            # Generate moduli candidates with new ssh-keygen syntax
            subprocess.run([
                'nice', '-n', str(config.nice_value),
                'ssh-keygen',
                '-M', 'generate',
                '-O', f'bits={key_length}',  # Specify the bit length
                str(candidates_file)  # Output a file specification
            ], check=True)

            return candidates_file

        except subprocess.CalledProcessError as err:
            raise err

    @staticmethod
    def _screen_candidates_static(config, candidates_file: Path) -> Path:
        """
        Static method for screening candidates - can be pickled for multiprocessing.
        """
        screened_file = config.moduli_dir / f'{candidates_file.name.replace('candidates', 'moduli')}'

        try:
            # Screen candidates with new ssh-keygen syntax
            checkpoint_file = config.candidates_dir / f".{candidates_file.name}"
            subprocess.run([
                'nice', '-n', str(config.nice_value),
                'ssh-keygen',
                '-M', 'screen',
                '-O', f'generator={config.generator_type}',  # Specify screening type
                '-O', f'checkpoint={str(checkpoint_file)}',
                '-f', str(candidates_file),
                str(screened_file)
            ], check=True)

            # Cleanup used Moduli Candidates
            candidates_file.unlink()  # Cleanup Used Candidate File

            return screened_file

        except subprocess.CalledProcessError as e:
            raise e

    def _generate_candidates(self, key_length: int) -> Path:
        """
        internally generates cryptographic key candidates of a specified bit length
        and stores them in a designated file.

        This function executes the `ssh-keygen` command with the required arguments
        to generate modular exponentiation candidates for cryptographic usage. The
        resulting candidates are saved to a file in the designated directory defined
        in the configuration. Any exceptions raised during command execution are
        logged and re-raised for handling by the caller.

        :param key_length: The bit length of the cryptographic key to be generated.
        :type key_length: int
        :return: A path object pointing to the file containing key candidates.
        :rtype: Path
        :raises subprocess.CalledProcessError: If the `ssh-keygen` command fails to
            execute successfully.
        """
        try:
            result = self._generate_candidates_static(self.config, key_length)
            self.logger.info(f'Generated candidates for {key_length} bits')
            return result
        except subprocess.CalledProcessError as err:
            self.logger.error(f'Candidate generation failed for {key_length}: {err}')
            raise err

    def _screen_candidates(self, candidates_file: Path) -> Path:
        """
        Screens the given moduli candidate file by using the `ssh-keygen` command and processes it into a
        screened moduli file. The method also performs cleanup by removing the original candidate file
        after successful screening.

        :param candidates_file: The path to the file containing moduli candidates that need to be screened.
        :type candidates_file: Path
        :return: The path to the screened moduli file generated after processing.
        :rtype: Path
        """
        try:
            result = self._screen_candidates_static(self.config, candidates_file)
            self.logger.debug(f'Screened candidates: {result}')
            return result
        except subprocess.CalledProcessError as e:
            self.logger.error(f'Screening failed for {candidates_file}: {e}')
            raise e

    def _parse_moduli_files(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Parses moduli files to extract relevant data and structures it into a dictionary.
        This method processes each line of a moduli file, skipping comments and blank
        lines. It extracts specific fields and organizes them into dictionaries,
        grouped under the 'screened_moduli' key.

        :raises FileNotFoundError: If a moduli file is not found during processing.

        :return: A dictionary where the key is 'screened_moduli' and the value is a list
            of dictionaries containing parsed moduli entries.
        :rtype: Dict[str, List[Dict[str, Any]]]
        """

        screened_files = self._list_moduli_files()
        moduli_json = {}

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

                            moduli_json.setdefault('screened_moduli', []).append(moduli_entry)

            except FileNotFoundError:
                self.logger.warning(f'Moduli file not found: {file}')

        return moduli_json

    def _list_moduli_files(self):
        """
        Retrieves a list of files matching the specified pattern from the configured directory.

        This method searches within the directory defined in the `moduli_dir` configuration
        attribute for files that match the pattern defined in the `moduli_file_pattern` attribute.
        Returns them as a list of Path objects.

        :return: A list of Path objects representing the files matching the specified pattern.
        :rtype: List[pathlib.Path]
        """
        return list(self.config.moduli_dir.glob(self.config.moduli_file_pattern))

    def generate_moduli(self) -> Dict[int, List[Path]]:
        """
        Generates moduli files grouped by key lengths specified in the configuration.

        This method performs the generation of moduli through several key steps:
        1. It first generates candidate files for each key length defined in the configuration
           by utilizing parallel processing.
        2. The candidate files are then screened and organized by key length using additional
           parallel processing.
        3. Generated moduli files for each key length are stored and returned as a dictionary.

        The method uses a `ProcessPoolExecutor` to ensure efficient parallel processing
        of both candidate generation and candidate screening.

        :return: Returns the current instance of the object for method chaining.
        :rtype: Dict[int, List[Path]]
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
            self.logger.debug(f'Generated {len(candidates_by_length)} candidates for {self.config.key_lengths}')

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
            self.logger.debug(f'Screened {len(screening_futures)} candidates for {self.config.key_lengths}')

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
        :return: Returns the current instance of the object for method chaining.
        :rtype: self
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
        Parse, validate, and store screened moduli into the database, and manage their source
        files once the operation is successful. This function ensures that the moduli records
        are stored transactionally. After successful storage, the source files are deleted.

        :return: The instance of the object to facilitate method chaining
        :rtype: object
        """
        screened_moduli = self._parse_moduli_files()

        try:
            self.db.store_screened_moduli(screened_moduli)

        except Error as err:
            self.logger.error(f'Error storing moduli: {err}')

        # tbd - We should check that the records are installed properly before hand
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

        :return: The instance of the class.
        :rtype: self
        """
        self.db.get_and_write_moduli_file()

        return self
