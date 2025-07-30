#!/usr/bin/env python
import concurrent.futures
import subprocess
from json import dump
from logging import (DEBUG, INFO)
from pathlib import PosixPath as Path
from typing import (Any, Dict, List)

from config import (default_config, iso_utc_timestamp)
from db import (Error, MariaDBConnector)
from moduli_generator.validators import validate_subprocess_args

# Constants
SSH2_MODULI_FILE_FIELD_COUNT = 7  # Expected number of fields in moduli file format

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
    def _run_subprocess_with_logging(command,
                                     logger,
                                     info_level=INFO,
                                     debug_level=DEBUG
                                     ) -> subprocess.CompletedProcess:
        """
        Run a subprocess command and capture output for logging.

        This method uses subprocess.PIPE to capture stdout and stderr,
        then logs the captured output using the provided logger.

        :param command: List of command arguments to execute
        :type command: List[str]
        :param logger: Logger instance for logging output
        :type logger: logging.Logger
        :param info_level: Log level for stdout messages
        :type info_level: int
        :param debug_level: Log level for stderr messages
        :type debug_level: int
        :return: CompletedProcess instance
        :rtype: subprocess.CompletedProcess
        :raises CalledProcessError: If the subprocess fails
        """
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        # Log stdout if present
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    logger.log(info_level, line.strip())

        # Log stderr if present
        if result.stderr:
            for line in result.stderr.strip().split('\n'):
                if line.strip():
                    logger.log(debug_level, line.strip())

        return result

    @staticmethod
    def _generate_candidates_static(config, key_length: int) -> Path:
        """
        Generate a moduli candidate file using the SSH key generation utility.

        This method runs the `ssh-keygen` command-line tool to generate moduli candidates for
        Diffie-Hellman group exchange, leveraging subprocess handling for system command execution.
        The output and errors are captured using subprocess.PIPE and then logged appropriately.
        The generated file is returned as a `Path` object pointing to its location.

        :param config: The configuration object contains the necessary parameters for the process,
                       including paths and logging setup.
        :type config: Any
        :param key_length: The desired key length in bits for the moduli candidate generation.
        :type key_length: int
        :return: Path to the generated moduli candidate file.
        :rtype: Path
        """
        candidates_file = config.candidates_dir / f'candidates_{key_length}_{iso_utc_timestamp(compress=True)}'
        logger = config.get_logger()

        # nice_value and key_length(s) CAN Be User provided Variables. We need to make sure they're safe.
        safe_key_length, safe_nice_value = validate_subprocess_args(key_length, config.nice_value)

        # try:
        command = [
            'nice', '-n', f'{safe_nice_value}',
            'ssh-keygen',
            '-M', 'generate',
            '-O', f'bits={safe_key_length}',
            str(candidates_file)
        ]

        try:
            ModuliGenerator._run_subprocess_with_logging(command, logger)

        except subprocess.CalledProcessError as err:
            logger.error(f'ssh-keygen generate failed for {key_length} bits: {err}')
            # Log captured stderr if available
            if err.stderr:
                logger.error(f'ssh-keygen stderr: {err.stderr}')
            raise err

        return candidates_file

    @staticmethod
    def _screen_candidates_static(config, candidates_file: Path) -> Path:
        """
        Screen candidate moduli files using the provided configuration and the `ssh-keygen` tool.
        This method takes a configuration object and a path to a candidate moduli file and processes
        the file to generate a screened moduli file. The `ssh-keygen` tool is used with the `-M screen`
        option to evaluate and filter candidate moduli using various configuration parameters. Output
        is captured using subprocess.PIPE and logged appropriately.

        If the operation is successful, the processed moduli file is returned. The candidate file is
        removed from the filesystem after processing. In case of errors during execution, log and re-raises
        exceptions.

        :param config: Configuration object providing required details for processing such as moduli
                       directory, logger, generator type, candidates directory, and nice value.
        :type config: Any
        :param candidates_file: Path to the candidate moduli file to be screened.
        :type candidates_file: Path
        :return: Path to the generated screened moduli file.
        :rtype: Path
        :raises CalledProcessError: If the `ssh-keygen` tool fails during execution.
        """
        screened_file = config.moduli_dir / f'{candidates_file.name.replace('candidates', 'moduli')}'
        logger = config.get_logger()

        # We only need to validate a nice value, Using valid key_length(int(3072)) to pass argument validator
        _, safe_nice_value = validate_subprocess_args(int(3072), config.nice_value)

        # try:
        checkpoint_file = config.candidates_dir / f".{candidates_file.name}"
        command = [
            'nice', '-n', f'{safe_nice_value}',
            'ssh-keygen',
            '-M', 'screen',
            '-O', f'generator={config.generator_type}',
            '-O', f'checkpoint={str(checkpoint_file)}',
            '-f', str(candidates_file),
            str(screened_file)
        ]
        try:
            # Use subprocess.PIPE to capture and log output
            ModuliGenerator._run_subprocess_with_logging(command, logger)

        except subprocess.CalledProcessError as err:
            logger.error(f'ssh-keygen screen failed for {candidates_file}: {err}')
            # Log captured stderr if available
            if err.stderr:
                logger.error(f'ssh-keygen stderr: {err.stderr}')
            raise err

        # Cleanup used Moduli Candidates
        candidates_file.unlink()

        return screened_file


    def _parse_moduli_files(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Parses the moduli files to extract specific installers entries and formats them
        into a dictionary structure for further processing. This method iterates
        over a set of screened files, reads their contents line by line, and
        extracts information about timestamp, key size, and modulus if the line
        meets specific criteria.

        :return: A dictionary with parsed moduli installers under the key
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
                        if len(parts) == SSH2_MODULI_FILE_FIELD_COUNT:
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

    def _list_moduli_files(self) -> List[Path]:
        """
        Lists all moduli files based on the configured moduli directory and file
        pattern.

        This function retrieves and returns a list of all files in the
        configured moduli directory that match the specified file pattern.

        :return: List of matching moduli files
        :rtype: list[Path]
        """
        return list(self.config.moduli_dir.glob(self.config.moduli_file_pattern))

    def generate_moduli(self) -> 'ModuliGenerator':
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

        # with concurrent.futures.ProcessPoolExecutor() as executor: - TBD
        #  Testint ThreadPool vs. ProcessPool executor
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
                f'Generated {len(candidate_futures)} candidate files for key-lengths: {self.config.key_lengths}')

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
            self.logger.info(f'Screened {len(screening_futures)} candidate files for key-lengths:' +
                             f'{self.config.key_lengths}')

        return self

    def save_moduli(self, moduli_file_dir: Path = None) -> 'ModuliGenerator':
        """
        Saves the processed moduli installers to a JSON file in the specified directory or a default location.

        This method processes the moduli installers and writes the output as a JSON file. If no directory is
        provided, the JSON file is saved in the default base directory specified in the configuration.
        The filename includes a timestamp in ISO UTC format to ensure a unique name.

        :param moduli_file_dir: Directory where the moduli JSON file should be saved. If not specified,
                                the default base directory from the configuration is used.
        :type moduli_file_dir: Path, optional
        :return: self
        :rtype: ModuliGenerator
        """
        if not moduli_file_dir:
            moduli_file_dir = self.config.moduli_home

        moduli_json = moduli_file_dir / f'screened_moduli_{iso_utc_timestamp(True)}.json'
        with moduli_json.open('w') as f:
            # with open(moduli_json, 'w') as f:
            dump(self._parse_moduli_files(), f, indent=2)

        self.logger.info(f'Moduli schema saved to {self.config.moduli_dir / moduli_json}')

        return self

    def store_moduli(self) -> 'ModuliGenerator':
        """
        Parse, validate, and store screened moduli into the database and manage their source
        files once the operation is successful. This function ensures that the moduli records
        are stored transactionally. After successful storage, the source files are deleted.

        :return: self
        :rtype: ModuliGenerator
        """
        screened_moduli = self._parse_moduli_files()

        # tbd - Verify Successful DB Load prior to Deletion
        try:
            self.db.export_screened_moduli(screened_moduli)

            # Cleanup lefover moduli files
            moduli_files = self._list_moduli_files()
            if len(moduli_files) and not self.config.preserve_moduli_after_dbstore:
                for file in moduli_files:
                    file.unlink()

        except Error as err:
            self.logger.error(f'Error storing moduli: {err}')

        self.logger.info(f'Moduli Stored in MariaDB database: {len(screened_moduli)}')

        return self

    def write_moduli_file(self) -> 'ModuliGenerator':
        """
        Writes the moduli file using the database interface.

        This method retrieves the installers necessary for the moduli file from the
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

    def restart_screening(self) -> 'ModuliGenerator':
        """
        Restarts the screening process for candidates grouped by their respective lengths
        and generates moduli files for each key length. This method processes candidates
        from the specified directory, screens them using a thread pool executor, and returns
        an updated instance of the ModuliGenerator.

        :return: The current instance of ModuliGenerator for method chaining.
        :rtype: ModuliGenerator
        """

        def _get_restart_candidates_by_length() -> List[Path]:
            """
            Retrieves a mapping of restart candidates grouped by their length. The function
            iterates through directories and file patterns specified in the configuration
            to build a dictionary. Each key in the dictionary represents a unique length,
            and the value is a list of paths to the corresponding candidate files.

            :return: A dictionary where the keys are lengths (int) and the values are
                lists of Path objects representing restart candidate files.
            :rtype: dict[int, List[Path]]
            """
            results = {}
            for idx in self.config.candidates_dir.glob(self.config.candidate_idx_pattern):
                candidate = Path(self.config.candidates_dir) / idx.name.replace('.candidates', 'candidates')
                local_length = int(idx.name.split('_')[1])
                if local_length not in results:
                    results[local_length] = []
                results[local_length].append(candidate)
            return results

        candidates_by_length = _get_restart_candidates_by_length()

        if len(candidates_by_length) != 0:

            with concurrent.futures.ProcessPoolExecutor() as executor:
                """
                TBD - Testint ThreadPool vs ProcessPool executor"""
                # Then screen candidates
                screening_futures = []
                for length, candidate_files in candidates_by_length.items():
                    for candidate_file in candidate_files:
                        future = executor.submit(self._screen_candidates_static, self.config, candidate_file)
                        screening_futures.append((future, length))

                # Process completed screening futures
                generated_moduli = {}
                for future, length in screening_futures:
                    moduli_file = future.result()
                    if length not in generated_moduli:
                        generated_moduli[length] = []
                    generated_moduli[length].append(moduli_file)
                self.logger.info(f'Produced {len(screening_futures)} files of screened moduli\n'
                                 f'for key-lengths:' + f'{self.config.key_lengths}')
        else:
            self.logger.info(f'No Unscreened Candidates Found for Restart')

        return self
