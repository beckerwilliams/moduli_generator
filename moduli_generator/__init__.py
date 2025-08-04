#!/usr/bin/env python
import concurrent.futures
import subprocess
from logging import DEBUG, INFO, Logger
from pathlib import PosixPath as Path
from typing import Any, Dict, List

from config import ModuliConfig, default_config, iso_utc_timestamp
from db import MariaDBConnector
from moduli_generator.validators import validate_subprocess_args

# Constants
SSH2_MODULI_FILE_FIELD_COUNT = 7  # Expected number of fields in moduli file format

__all__ = ["ModuliGenerator"]


class ModuliGenerator:
    """Handles the generation, screening, and management of cryptographic modulus files.

    This class provides methods for generating moduli candidates, screening them for
    validity, and organizing them into structured formats used for secure communications.

    This utility is intended for cryptographic security operations, where moduli
    are required for operations like key exchange. It uses external tools like
    `ssh-keygen` for candidate generation and screening processes.

    Attributes:
        config: The configuration object containing paths and settings such as
            directory paths and security-related configurations.
        version: The version of the moduli generator settings.
        logger: The logger used for logging information, warnings, and errors
            during execution.
        db: Lazily instantiated attribute for database storage of moduli,
            created as needed.
    """

    def __init__(self, config: ModuliConfig = default_config) -> "ModuliGenerator":
        """
        Class responsible for managing moduli configuration and related utilities. Handles
        logging configuration paths and supports lazy database initialization to optimize
        resource usage. Leverages the provided configuration to set up essential properties
        and integrate logging behavior.

        Args:
            config (ModuliConfig): Configuration instance that contains moduli settings and utilities.
        """
        self.config = config
        self.version = config.version
        self.logger = self.config.get_logger()
        self.logger.name = __name__

        # Log paths used
        if self.config:
            for path_name, path_obj in [
                ("Base directory", self.config.moduli_dir),
                ("Candidates directory", self.config.candidates_dir),
                ("Moduli directory", self.config.moduli_dir),
                ("Log directory", self.config.log_dir),
                ("MariaDB config", self.config.mariadb_cnf),
            ]:
                self.logger.info(f"Using {path_name}: {path_obj}")

        # Store config for lazy DB initialization instead of creating a connection here
        self._db = None

    @property
    def db(self) -> MariaDBConnector:
        """Lazy initialization of the database connection property.

        This property ensures that the database connection is initialized only once,
        upon first access, and then reused for subsequent operations.

        Returns:
            MariaDBConnector: Initialized database connection object.
        """
        if self._db is None:
            self._db = MariaDBConnector(self.config)
        return self._db

    @property
    def __version__(self) -> str:
        """
        Represents the version property of a class that retrieves
                the version information of the instance.

                This property is read-only and provides access to the internal
                `version` attribute of the class instance.

        Returns:
            str: Current version of the instance.
        """
        return self.version

    @staticmethod
    def _run_subprocess_with_logging(
        command: str,
        logger: Logger,
        info_level: int = INFO,
        debug_level: int = DEBUG,
    ) -> subprocess.CompletedProcess:
        """
        Executes a subprocess command with real-time logging for both `stdout` and `stderr`. This method
                handles the logging of subprocess output streams directly as they are produced, using a
                threaded approach to ensure asynchronous handling of stream data.

                Subprocess outputs are logged in real-time using the provided logger object, and the function
                returns a custom `StreamedResult` object containing information about the command execution
                (omitting `stdout` and `stderr` data as they're already logged). Exceptions encountered during the
                operation, such as errors in the process execution or issues with logging, are propagated
                appropriately.

        Args:
            command: The command to be executed as a list of strings.
            debug_level: Logging level used for `stderr` stream messages. Defaults to DEBUG.
            info_level: Logging level used for `stdout` stream messages. Defaults to INFO.
            logger: Logger instance used for logging the subprocess output.

        Returns:
            subprocess.CompletedProcess: A custom result object containing command arguments and a return code.
        """
        import threading

        def log_stream(stream, log_func, prefix):
            """Helper to log stream output in real-time"""
            try:
                for line in iter(stream.readline, ""):
                    if line.strip():
                        log_func(f"{line.strip()}")
            except Exception as err:
                logger.error(f"Error reading {prefix} stream: {err}")
            finally:
                stream.close()

        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered for real-time output
                universal_newlines=True,
            )

            # Start threads to handle stdout and stderr streams concurrently
            stdout_thread = threading.Thread(
                target=log_stream,
                args=(
                    process.stdout,
                    lambda msg: logger.log(info_level, msg),
                    "stdout",
                ),
                daemon=True,
            )
            stderr_thread = threading.Thread(
                target=log_stream,
                args=(
                    process.stderr,
                    lambda msg: logger.log(debug_level, msg),
                    "stderr",
                ),
                daemon=True,
            )

            stdout_thread.start()
            stderr_thread.start()

            # Wait for the process to complete
            return_code = process.wait()

            # Wait for logging threads to finish
            stdout_thread.join(timeout=5.0)  # Prevent hanging
            stderr_thread.join(timeout=5.0)

            if return_code != 0:
                raise subprocess.CalledProcessError(return_code, command)

            # Create a CompletedProcess-like object for compatibility
            class StreamedResult:
                def __init__(self, returncode, args):
                    self.returncode = returncode
                    self.args = args
                    self.stdout = ""  # Output already logged in real-time
                    self.stderr = ""  # Errors already logged in real-time

            return StreamedResult(return_code, command)

        except subprocess.CalledProcessError:
            raise
        except Exception as err:
            logger.error(f"Unexpected error running command {command}: {err}")
            raise subprocess.CalledProcessError(1, command) from e

    @staticmethod
    def _generate_candidates_static(config: ModuliConfig, key_length: int) -> Path:
        """
        Generate a moduli candidate file using the SSH key generation utility.

                This method runs the `ssh-keygen` command-line tool to generate moduli candidates for
                Diffie-Hellman group exchange, leveraging subprocess handling for system command execution.
                The output and errors are captured using subprocess.PIPE and then logged appropriately.
                The generated file is returned as a `Path` object pointing to its location.

        Args:
            config (Any): The configuration object contains the necessary parameters for the process,
            including paths and logging setup.
            key_length (int): The desired key length in bits for the moduli candidate generation.

        Returns:
            Path: Path to the generated moduli candidate file.
        """
        candidates_file = (
            config.candidates_dir
            / f"candidates_{key_length}_{iso_utc_timestamp(compress=True)}"
        )
        logger = config.get_logger()

        # nice_value and key_length(s) CAN Be User provided Variables. We need to make sure they're safe.
        safe_key_length, safe_nice_value = validate_subprocess_args(
            key_length, config.nice_value
        )

        # try:
        command = [
            "nice",
            "-n",
            f"{safe_nice_value}",
            "ssh-keygen",
            "-M",
            "generate",
            "-O",
            f"bits={safe_key_length}",
            str(candidates_file),
        ]

        try:
            ModuliGenerator._run_subprocess_with_logging(command, logger)

        except subprocess.CalledProcessError as err:
            logger.error(f"ssh-keygen generate failed for {key_length} bits: {err}")
            # stderr is already logged in real-time by the streaming implementation
            raise err

        return candidates_file

    @staticmethod
    def _screen_candidates_static(config: ModuliConfig, candidates_file: Path) -> Path:
        """
        Screen candidate moduli files using the provided configuration and the `ssh-keygen` tool.
                This method takes a configuration object and a path to a candidate moduli file and processes
                the file to generate a screened moduli file. The `ssh-keygen` tool is used with the `-M screen`
                option to evaluate and filter candidate moduli using various configuration parameters. Output
                is captured using subprocess.PIPE and logged appropriately.

                If the operation is successful, the processed moduli file is returned. The candidate file is
                removed from the filesystem after processing. In case of errors during execution, log and re-raises
                exceptions.

        Args:
            candidates_file (Path): Path to the candidate moduli file to be screened.
            config (Any): Configuration object providing required details for processing such as modul
            directory, logger, generator type, candidates directory, and nice value.

        Returns:
            Path: Path to the generated screened moduli file.

        Raises:
            CalledProcessError: If the `ssh-keygen` tool fails during execution.
        """
        screened_file = (
            config.moduli_dir
            / f"{candidates_file.name.replace('candidates', 'moduli')}"
        )
        logger = config.get_logger()

        # We only need to validate a nice value, Using valid key_length(int(3072)) to pass argument validator
        _, safe_nice_value = validate_subprocess_args(int(3072), config.nice_value)

        # try:
        checkpoint_file = config.candidates_dir / f".{candidates_file.name}"
        command = [
            "nice",
            "-n",
            f"{safe_nice_value}",
            "ssh-keygen",
            "-M",
            "screen",
            "-O",
            f"generator={config.generator_type}",
            "-O",
            f"checkpoint={str(checkpoint_file)}",
            "-f",
            str(candidates_file),
            str(screened_file),
        ]
        try:
            # Use a streaming approach for real-time output logging
            ModuliGenerator._run_subprocess_with_logging(command, logger)

        except subprocess.CalledProcessError as err:
            logger.error(f"ssh-keygen screen failed for {candidates_file}: {err}")
            # stderr is already logged in real-time by the streaming implementation
            raise err

        # Cleanup used Moduli Candidates
        candidates_file.unlink()

        return screened_file

    def _parse_moduli_files(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Parses the moduli files to extract specific key-length entries and formats them
                into a dictionary structure for further processing. This method iterates
                over a set of screened files, reads their contents line by line, and
                extracts information about timestamp, key size, and modulus if the line
                meets specific criteria.

        Returns:
            Dict[str, List[Dict[str, Any]]]: A dictionary with parsed moduli installers under the key
            'screened_moduli'. Each entry is a dictionary containing 'timestamp', 'key-size', and 'modulus'.
        """

        screened_files = self._list_moduli_files()
        screened_moduli = {}

        for file in screened_files:
            try:
                with file.open("r") as f:
                    for line in f:
                        if line.startswith("#") or not line.strip():
                            continue

                        parts = line.split()
                        if len(parts) == SSH2_MODULI_FILE_FIELD_COUNT:
                            moduli_entry = {
                                "timestamp": parts[0],  # TIMESTAMP
                                # 'type': parts[1],         # Constant, Stored in moduli_db.mod_fl_consts
                                # 'tests': parts[2],        # Constant, Stored in moduli_db.mod_fl_consts
                                # 'trials': parts[3],       # Constant, Stored in moduli_db.mod_fl_consts
                                "key-size": parts[4],  # KEY_LENGTH
                                # 'generator': parts[5], # Constant, Stored in moduli_db.mod_fl_consts
                                "modulus": parts[6],  # MODULUS
                            }

                            screened_moduli.setdefault("screened_moduli", []).append(
                                moduli_entry
                            )

            except FileNotFoundError:
                self.logger.warning(f"Moduli file not found: {file}")

        return screened_moduli

    def _list_moduli_files(self) -> List[Path]:
        """
        Lists all moduli files based on the configured moduli directory and file
                pattern.

                This function retrieves and returns a list of all files in the
                configured moduli directory that match the specified file pattern.

        Returns:
            list[Path]: List of matching moduli files
        """
        return list(self.config.moduli_dir.glob(self.config.moduli_file_pattern))

    def generate_moduli(self) -> "ModuliGenerator":
        """
        Generates and screens Diffie-Hellman moduli files for specified key lengths using
                pipeline processing for optimal performance.

                This method uses a pipeline approach where candidate generation and screening happen
                concurrently. As soon as a candidate file is generated, it's immediately submitted
                for screening, rather than waiting for all candidates to be generated first.
                This optimization reduces overall processing time by overlapping I/O and CPU operations.

        Returns:
            ModuliGenerator: self
        """
        generated_moduli = {}

        with concurrent.futures.ProcessPoolExecutor() as executor:
            # Submit all candidate generation tasks
            candidate_futures = []
            for length in self.config.key_lengths:
                future = executor.submit(
                    self._generate_candidates_static, self.config, length
                )
                candidate_futures.append((future, length))

            # Pipeline processing: screen candidates as they become available
            screening_futures = []
            candidates_generated = 0

            # Process candidates as they complete and immediately submit for screening
            for future in concurrent.futures.as_completed(
                [f for f, _ in candidate_futures]
            ):
                # Find the corresponding length for this future
                length = None
                for candidate_future, candidate_length in candidate_futures:
                    if candidate_future == future:
                        length = candidate_length
                        break

                try:
                    candidate_file = future.result()
                    candidates_generated += 1
                    self.logger.debug(
                        f"Generated candidate file {candidates_generated}/{len(candidate_futures)}: {candidate_file}"
                    )

                    # Immediately submit for screening (pipeline processing)
                    screening_future = executor.submit(
                        self._screen_candidates_static, self.config, candidate_file
                    )
                    screening_futures.append((screening_future, length))

                except Exception as e:
                    self.logger.error(
                        f"Error generating candidate for length {length}: {e}"
                    )
                    raise

            self.logger.info(
                f"Generated {candidates_generated} candidate files for key-lengths: {self.config.key_lengths}"
            )

            # Process screening results as they complete
            screened_count = 0
            for future in concurrent.futures.as_completed(
                [f for f, _ in screening_futures]
            ):
                # Find the corresponding length for this future
                length = None
                for screening_future, screening_length in screening_futures:
                    if screening_future == future:
                        length = screening_length
                        break

                try:
                    moduli_file = future.result()
                    screened_count += 1
                    self.logger.debug(
                        f"Screened moduli file {screened_count}/{len(screening_futures)}: {moduli_file}"
                    )

                    if length not in generated_moduli:
                        generated_moduli[length] = []
                    generated_moduli[length].append(moduli_file)

                except Exception as err:
                    self.logger.error(
                        f"Error screening candidate for length {length}: {err}"
                    )
                    raise

            self.logger.info(
                f"Screened {screened_count} candidate files for key-lengths: {self.config.key_lengths}"
            )

        return self

    def store_moduli(self) -> "ModuliGenerator":
        """
        Parse, validate, and store screened moduli into the database and manage their source
                files once the operation is successful. This function ensures that the moduli records
                are stored transactionally. After successful storage, the source files are deleted.

        Returns:
            ModuliGenerator: self
        """
        screened_moduli = self._parse_moduli_files()
        try:
            self.db.export_screened_moduli(screened_moduli)

            # Cleanup lefover moduli files
            moduli_files = self._list_moduli_files()
            if len(moduli_files) and not self.config.preserve_moduli_after_dbstore:
                for file in moduli_files:
                    file.unlink()
        except Error as err:
            self.logger.error(f"Error storing moduli: {err}")

        self.logger.info(f"Moduli Stored in MariaDB database: {len(screened_moduli)}")

        return self

    def write_moduli_file(self) -> "ModuliGenerator":
        """
        Writes the moduli file using the database interface.

                This method retrieves the moduli necessary for the moduli file from the
                database and then writes it to the appropriate location using
                the database interface.

        Returns:
            ModuliGenerator: self
        """
        try:
            self.db.write_moduli_file()

        except RuntimeError as err:
            self.logger.info(err)

        return self

    def restart_screening(self) -> "ModuliGenerator":
        """
        Restarts the screening process for candidates grouped by their respective lengths
                and generates moduli files for each key length. This method processes candidates
                from the specified directory, screens them using a thread pool executor, and returns
                an updated instance of the ModuliGenerator.

        Returns:
            ModuliGenerator: The current instance of ModuliGenerator for method chaining.
        """

        def _get_restart_candidates_by_length() -> List[Path]:
            """
            Retrieves a mapping of restart candidates grouped by their length. The function
                        iterates through directories and file patterns specified in the configuration
                        to build a dictionary. Each key in the dictionary represents a unique length,
                        and the value is a list of paths to the corresponding candidate files.

            Returns:
                dict[int, List[Path]]: A dictionary where the keys are lengths (int) and the values are
                    lists of Path objects representing restart candidate files.
            """
            results = {}
            for idx in self.config.candidates_dir.glob(
                self.config.candidate_idx_pattern
            ):
                candidate = Path(self.config.candidates_dir) / idx.name.replace(
                    ".candidates", "candidates"
                )
                local_length = int(idx.name.split("_")[1])
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
                        future = executor.submit(
                            self._screen_candidates_static, self.config, candidate_file
                        )
                        screening_futures.append((future, length))

                # Process completed screening futures
                generated_moduli = {}
                for future, length in screening_futures:
                    moduli_file = future.result()
                    if length not in generated_moduli:
                        generated_moduli[length] = []
                    generated_moduli[length].append(moduli_file)
                self.logger.info(
                    f"Produced {len(screening_futures)} files of screened moduli\n"
                    f"for key-lengths:" + f"{self.config.key_lengths}"
                )
        else:
            self.logger.info(f"No Unscreened Candidates Found for Restart")

        return self
