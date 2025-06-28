#!/usr/bin/env python
import concurrent.futures
import logging
import subprocess
from datetime import UTC, datetime
from json import (dump)
from pathlib import PosixPath as Path
from re import sub
from typing import Any, Dict, Final, List, Sequence

from mariadb import Error

from db.moduli_db_utilities import (MariaDBConnector, store_screened_moduli)


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


class ModuliGenerator:
    # Using typing.Final to explicitly mark immutable constants\
    DEFAULT_KEY_LENGTHS: Final[tuple[int, ...]] = (3072, 4096, 6144, 7680, 8192)
    DEFAULT_GENERATOR_TYPE: Final[int] = 2
    DEFAULT_NICE_VALUE: Final[int] = 20

    # Filesystem Layout
    DEFAULT_DIR: Final[Path] = Path.home() / '.moduli_assembly'
    DEFAULT_CANDIDATES_DIR: Final[Path] = DEFAULT_DIR / '.candidates'
    DEFAULT_MODULI_DIR: Final[Path] = DEFAULT_DIR / '.moduli'
    DEFAULT_LOG_DIR: Final[Path] = DEFAULT_DIR / '.logs'
    DEFAULT_MARIADB_CONFIG: Final[Path] = DEFAULT_DIR / "moduli_generator.cnf"

    def __init__(self,
                 key_lengths: Sequence[int] = DEFAULT_KEY_LENGTHS,
                 nice_value: int = DEFAULT_NICE_VALUE,
                 default_dir: Path = DEFAULT_DIR,
                 candidates_dir: Path = DEFAULT_CANDIDATES_DIR,
                 moduli_dir: Path = DEFAULT_MODULI_DIR,
                 log_dir: Path = DEFAULT_LOG_DIR,
                 ):
        """
        Initialize Moduli Generator with configurable parameters

        Args:
            key_lengths: Sequence of bit lengths for moduli generation
            candidates_dir: Directory for storing generated files
            nice_value: Value for 'nice' command to set for moduli generation
        """
        # Create an immutable copy of the input sequence
        self.generator_type = self.DEFAULT_GENERATOR_TYPE
        self.key_lengths = tuple(key_lengths)
        self.nice_value = nice_value

        self.default_dir = default_dir
        self.candidates_dir = candidates_dir
        self.moduli_dir = moduli_dir
        self.log_dir = log_dir

        # Assure Filesytem Exists
        for pathobject in [self.candidates_dir, self.moduli_dir, self.log_dir]:
            pathobject.mkdir(parents=True, exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s',
            filename=self.log_dir / 'moduli_generator.log',
            filemode='a'
        )
        self.logger = logging.getLogger(__name__)

    def _generate_candidates(self, key_length: int) -> Path:
        """
        Generate candidate moduli using modern ssh-keygen

        Args:
            key_length: Bit length for moduli generation

        Returns:
            Path to generated candidates file
        """
        candidates_file = self.candidates_dir / f'candidates_{key_length}_{ISO_UTC_TIMESTAMP(compress=True)}'

        try:
            # Generate moduli candidates with new ssh-keygen syntax
            subprocess.run([
                'nice', '-n', str(self.nice_value),
                'ssh-keygen',
                '-M', 'generate',
                '-O', f'bits={key_length}',  # Specify the bit length
                str(candidates_file)  # Output a file specification
            ], check=True)

            self.logger.info(f'Generated candidates for {key_length} bits')
            return candidates_file

        except subprocess.CalledProcessError as e:
            self.logger.error(f'Candidate generation failed for {key_length}: {e}')
            raise e

    def _screen_candidates(self, candidates_file: Path) -> Path:
        """
        Screen candidates for safe primes using modern ssh-keygen

        Args:
            candidates_file: File with generated candidates

        Returns:
            Path to the screened moduli file
        """
        screened_file = self.moduli_dir / f'{candidates_file.name.replace('candidates', 'moduli')}'

        try:
            # Screen candidates with new ssh-keygen syntax
            checkpoint_file = self.candidates_dir / f".{candidates_file.name}"
            subprocess.run([
                'nice', '-n', str(self.nice_value),
                'ssh-keygen',
                '-M', 'screen',
                '-O', f'generator={self.generator_type}',  # Specify screening type
                '-O', f'checkpoint={str(checkpoint_file)}',
                '-f', str(candidates_file),
                str(screened_file)
            ], check=True)

            self.logger.info(f'Screened candidates: {screened_file}')

            # Cleanup used Moduli Candidates
            candidates_file.unlink()  # Cleanup Used Candidate File

            return screened_file

        except subprocess.CalledProcessError as e:
            self.logger.error(f'Screening failed for {candidates_file}: {e}')
            raise e

    def _parse_moduli_files(
            self, moduli_path: Path = DEFAULT_MODULI_DIR
    ) -> Dict[str, List[Dict[str, Any]]]:

        screened_files = list(Path.glob(moduli_path, 'moduli_????_*'))
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
                self.logger.warning(f'Moduli file not found: {moduli_path}')

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
            for length in self.key_lengths:
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

    def save_moduli(self, default_dir: Path = DEFAULT_DIR):
        """
        Saves the existing moduli schema to a structured JSON file. If no custom output
        path is specified, the schema will be saved to a default location.

        :param default_dir: The path where the moduli schema JSON file should be saved.
            If not provided, a default output path is used.
        :type default_dir: Path, optional
        :return: None
        :rtype: None
        """
        moduli_json = default_dir / f'moduli_{ISO_UTC_TIMESTAMP(True)}.json'
        with open(moduli_json, 'w') as f:
            dump(self._parse_moduli_files(self.moduli_dir), f, indent=2)

        self.logger.info(f'Moduli schema saved to {default_dir}')

    def store_moduli(self, db: MariaDBConnector):
        """
        Store the existing moduli schema parsed from files into the database.

        This function parses moduli files to extract the schema and subsequently
        saves it into the specified database. After successfully storing the
        schema, an informational log message is generated to confirm the action.

        :param db: Database connector interface used to interact
                   with the MariaDB database.
        :type db: MariaDBConnector
        """
        screened_moduli = self._parse_moduli_files(self.moduli_dir)

        try:
            store_screened_moduli(db, screened_moduli)

        except Error as err:
            self.logger.error(f'Error storing moduli: {err}')

        # Now we get Transactional - When Moduli are Stored in the DB - DELETE Their Sources
        # tbd - We should check that the records are installed properly before hand
        moduli_files = list(Path.glob(self.moduli_dir, 'moduli_????_*'))
        for file in moduli_files:
            file.unlink()

        self.logger.debug(f'Moduli  Stored in MariaDB database.')
