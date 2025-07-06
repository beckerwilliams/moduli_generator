#!/usr/bin/env python
import concurrent.futures
import subprocess
from json import dump
from pathlib import PosixPath as Path
from typing import Any, Dict, List

from mariadb import Error

from moduli_generator.config import (
    ISO_UTC_TIMESTAMP,
    ModuliConfig, default_config
)

__all__ = ['ModuliGenerator']


class ModuliGenerator:
    def __init__(self, config=default_config):
        """
        Initializes an instance of the class with the given configuration and sets up
        necessary logging mechanisms. Various important directories and configuration
        paths provided by the configuration are logged for reference. This constructor
        ensures that all critical paths and the logger are properly set during
        initialization.

        :param config: The configuration object containing paths and logging settings.
        :type config: Optional, default is `default_config`
        """
        self.config = config
        self.version = config.version
        self.logger = self.config.get_logger()
        self.logger.name = __name__

        # Log paths
        if self.config:
            for path_name, path_obj in [
                ('Base directory', self.config.moduli_dir),
                ('Candidates directory', self.config.candidates_dir),
                ('Moduli directory', self.config.moduli_dir),
                ('Log directory', self.config.log_dir),
                ('MariaDB config', self.config.mariadb_cnf)
            ]:
                self.logger.info(f'Using {path_name}: {path_obj}')

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

        candidates_file = self.config.candidates_dir / f'candidates_{key_length}_{ISO_UTC_TIMESTAMP(compress=True)}'

        try:
            # Generate moduli candidates with new ssh-keygen syntax
            subprocess.run([
                'nice', '-n', str(self.config.nice_value),
                'ssh-keygen',
                '-M', 'generate',
                '-O', f'bits={key_length}',  # Specify the bit length
                str(candidates_file)  # Output a file specification
            ], check=True)

            self.logger.info(f'Generated candidates for {key_length} bits')
            return candidates_file

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
        screened_file = self.config.moduli_dir / f'{candidates_file.name.replace('candidates', 'moduli')}'

        try:
            # Screen candidates with new ssh-keygen syntax
            checkpoint_file = self.config.candidates_dir / f".{candidates_file.name}"
            subprocess.run([
                'nice', '-n', str(self.config.nice_value),
                'ssh-keygen',
                '-M', 'screen',
                '-O', f'generator={self.config.generator_type}',  # Specify screening type
                '-O', f'checkpoint={str(checkpoint_file)}',
                '-f', str(candidates_file),
                str(screened_file)
            ], check=True)

            self.logger.debug(f'Screened candidates: {screened_file}')

            # Cleanup used Moduli Candidates
            candidates_file.unlink()  # Cleanup Used Candidate File

            return screened_file

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

        screened_files = self.list_moduli_files()
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

    def generate_moduli(self) -> Dict[int, List[Path]]:
        """
        Generates cryptographic modulus files by first generating candidates and then
        screening the generated candidates. This method uses a process pool executor
        to perform operations concurrently for efficiency.

        :return: A dictionary mapping integer key lengths to lists of file paths where
            modulus files are stored. Each key represents a specific key length, and
            the corresponding value is a list of paths to files containing moduli
            of that key length.
        :rtype: Dict[int, List[Path]]
        """
        generated_moduli = {}

        with concurrent.futures.ProcessPoolExecutor() as executor:
            # First, generate candidates
            candidate_futures = []
            for length in self.config.key_lengths:
                future = executor.submit(self._generate_candidates, length)
                candidate_futures.append((future, length))

            # Process completed futures and organized candidates by key length
            candidates_by_length = {}
            for future, length in candidate_futures:
                candidate_file = future.result()
                if length not in candidates_by_length:
                    candidates_by_length[length] = []
                candidates_by_length[length].append(candidate_file)

            # Then screen candidates
            screening_futures = []
            for length, candidate_files in candidates_by_length.items():
                for candidate_file in candidate_files:
                    future = executor.submit(self._screen_candidates, candidate_file)
                    screening_futures.append((future, length))

            # Process completed screening futures
            for future, length in screening_futures:
                moduli_file = future.result()
                if length not in generated_moduli:
                    generated_moduli[length] = []
                generated_moduli[length].append(moduli_file)

        return generated_moduli

    def save_moduli(self, moduli_dir: Path = None):
        """
        Saves moduli schema to a JSON file for backup and reference purposes. The schema
        is parsed and written into a new JSON file which is named using the current UTC
        timestamp for uniqueness.

        :param moduli_dir: Optional directory path to save the moduli schema. If not
            provided, the default directory from configuration (`self.config.moduli_dir`)
            is used.
        :type moduli_dir: Path
        :return: None
        :rtype: None
        """
        if not moduli_dir:
            moduli_dir = self.config.moduli_dir

        moduli_json = moduli_dir / f'moduli_{ISO_UTC_TIMESTAMP(True)}.json'
        with moduli_json.open('w') as f:
            # with open(moduli_json, 'w') as f:
            dump(self._parse_moduli_files(), f, indent=2)

        self.logger.info(f'Moduli schema saved to {self.config.moduli_dir / moduli_json}')

    def store_moduli(self, db):
        """
        Stores moduli data into a given database and removes source files after successful storage.
        This function processes moduli files, parses them into a suitable format, stores them in the
        database using the provided database object, and then deletes the source files only after
        ensuring they have been stored in the database.

        :param db: The database object used to store the parsed moduli data.
        :type db: Object
        :return: None
        :rtype: None
        """
        screened_moduli = self._parse_moduli_files()

        try:
            db.store_screened_moduli(screened_moduli)

        except Error as err:
            self.logger.error(f'Error storing moduli: {err}')

        # Now we get Transactional - When Moduli are Stored in the DB - DELETE Their Sources
        # tbd - We should check that the records are installed properly before hand
        moduli_files = self.list_moduli_files()
        for file in moduli_files:
            file.unlink()

        self.logger.info(f'Moduli Files Parsed & Stored in MariaDB database: {moduli_files}')

    def list_moduli_files(self):
        """
        Retrieves a list of files matching the specified pattern from the configured directory.

        This method searches within the directory defined in the `moduli_dir` configuration
        attribute for files that match the pattern defined in the `moduli_file_pattern` attribute.
        Returns them as a list of Path objects.

        :return: A list of Path objects representing the files matching the specified pattern.
        :rtype: List[pathlib.Path]
        """
        return list(self.config.moduli_dir.glob(self.config.moduli_file_pattern))

    @property
    def __version__(self):
        return self.config.version
