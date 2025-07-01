#!/usr/bin/env python
import concurrent.futures
import subprocess
from json import dump
from pathlib import PosixPath as Path
from typing import Any, Dict, List

from mariadb import Error

# Import the default configuration
from config import (
    ISO_UTC_TIMESTAMP,
    default_config
)


class ModuliGenerator:
    def __init__(self, conf=default_config):

        self.config = conf

        # tbd - init logger here
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
        Generate candidate moduli using modern ssh-keygen

        Args:
            key_length: Bit length for moduli generation

        Returns:
            Path to generated candidates file
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
        Screen candidates for safe primes using modern ssh-keygen

        Args:
            candidates_file: File with generated candidates

        Returns:
            Path to the screened moduli file
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
                # '-O', f'lines={self.config.records_per_keylength}',  # tbd - not working as expected 2025-07-01T10:27:02-0500
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
        Generate moduli for all specified key lengths
        Handles multiple instances of the same key size by returning a dictionary
        mapping key lengths to lists of generated moduli files

        Returns:
            Dictionary mapping key lengths to lists of generated moduli files
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
        Parses, processes, and stores screened moduli from a specified directory into the database
        and logs the results. Upon successful storage, moduli source files in the directory are
        intended to be deleted to maintain transactional integrity, although the file removal is
        currently not implemented.

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
        return list(self.config.moduli_dir.glob(self.config.moduli_file_pattern))
