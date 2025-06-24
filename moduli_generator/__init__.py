#!/usr/bin/env python
import concurrent.futures
import logging
import subprocess
import time
from json import (dump, loads)
from pathlib import PosixPath as Path
from typing import Any, Dict, Final, List, Sequence

from db.mg_mariadb_connector import (MariaDBConnector, store_screened_moduli)


class ModuliGenerator:
    # Using typing.Final to explicitly mark immutable constants
    DEFAULT_KEY_LENGTHS: Final[tuple[int, ...]] = (3072, 4096, 6144, 7680, 8192)
    DEFAULT_OUTPUT_DIR: Final[Path] = Path.home() / '.moduli_assembly'
    DEFAULT_GENERATOR_TYPE: Final[int] = 2
    DEFAULT_NICE_VALUE: Final[int] = 20

    def __init__(self,
                 key_lengths: Sequence[int] = DEFAULT_KEY_LENGTHS,
                 output_dir: Path = DEFAULT_OUTPUT_DIR,
                 nice_value: int = DEFAULT_NICE_VALUE,
                 db_cnf: str = None  # tbd - If exists - store moduli, if not, ignore
                 ):
        """
        Initialize Moduli Generator with configurable parameters

        Args:
            key_lengths: Sequence of bit lengths for moduli generation
            output_dir: Directory for storing generated files
            nice_value: Value for nice command to set for moduli generation
        """
        # Create an immutable copy of the input sequence
        self.key_lengths = tuple(key_lengths)
        self.generator_type = self.DEFAULT_GENERATOR_TYPE
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.nice_value = self.DEFAULT_NICE_VALUE

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s',
            filename=self.output_dir / 'moduli_generation.log'
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
        candidates_file = self.output_dir / f'candidates_{key_length}'

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
            raise

    def _screen_candidates(self, candidates_file: Path) -> Path:
        """

        Screen candidates for safe primes using modern ssh-keygen

        Args:
            candidates_file: File with generated candidates

        Returns:
            Path to the screened moduli file
        """
        screened_file = self.output_dir / f'screened_{candidates_file.stem}'

        try:
            # Screen candidates with new ssh-keygen syntax
            subprocess.run([
                'nice', '-n', str(self.nice_value),
                'ssh-keygen',
                '-M', 'screen',
                '-O', f'generator={self.generator_type}',  # Specify screening type
                '-O', f'checkpoint={self.output_dir / f".{candidates_file.name}"}',
                '-f', str(candidates_file),
                str(screened_file)
            ], check=True)

            self.logger.info(f'Screened candidates: {screened_file}')
            return screened_file

        except subprocess.CalledProcessError as e:
            self.logger.error(f'Screening failed for {candidates_file}: {e}')
            raise

    def _parse_moduli_files(self, moduli_path: Path = Path('/etc/ssh/moduli')) -> Dict[str, List[Dict[str, Any]]]:
        """
        Parse the existing /etc/ssh/moduli file and convert to structured JSON

        Args:
            moduli_path: Path to the existing moduli file

        Returns:
            Structured JSON representation of moduli
        """
        moduli_json = {}

        try:
            with open(moduli_path, 'r') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue

                    parts = line.split()
                    if len(parts) == 7:
                        moduli_entry = {
                            'timestamp': parts[0],
                            'type': parts[1],
                            'tests': parts[2],
                            'trials': parts[3],
                            'size': parts[4],
                            'generator': parts[5],
                            'modulus': parts[6]
                        }

                        moduli_json.setdefault(parts[3], []).append(moduli_entry)

        except FileNotFoundError:
            self.logger.warning(f'Moduli file not found: {moduli_path}')

        return moduli_json

    def generate_moduli(self) -> Dict[int, Path]:
        """
        Generate moduli for all specified key lengths

        Returns:
            Dictionary mapping key lengths to generated moduli files
        """
        generated_moduli = {}

        with concurrent.futures.ProcessPoolExecutor() as executor:
            # First, generate candidates
            candidate_futures = {
                executor.submit(self._generate_candidates, length): length
                for length in self.key_lengths
            }

            candidates = {}
            for future in concurrent.futures.as_completed(candidate_futures):
                length = candidate_futures[future]
                candidates[length] = future.result()

            # Then screen candidates
            screening_futures = {
                executor.submit(self._screen_candidates, candidates[length]): length
                for length in candidates
            }

            for future in concurrent.futures.as_completed(screening_futures):
                length = screening_futures[future]
                generated_moduli[length] = future.result()

        return generated_moduli

    def save_moduli_schema(self, output_path: Path = None):
        """
        Save existing moduli schema as structured JSON

        Args:
            output_path: Custom output path for JSON file
        """
        if output_path is None:
            output_path = self.output_dir / 'moduli_schema.json'

        moduli_schema = self._parse_moduli_files()

        with open(output_path, 'w') as f:
            dump(moduli_schema, f, indent=2)

        self.logger.info(f'Moduli schema saved to {output_path}')


def main():
    generator = ModuliGenerator(nice_value=15)

    # Generate moduli
    start_time = time.time()
    generated_files = generator.generate_moduli()

    # Save moduli schema
    generator.save_moduli_schema()
    print(f'Moduli Generation Complete. Time taken: {time.time() - start_time:.2f} seconds')
    print('Generated Files: ', generated_files)

    # Test DB Work
    db = MariaDBConnector("/Users/ron/development/moduli_generator/moduli_generator.cnf")

    moduli = loads(Path('/Users/ron/development/moduli_generator/.moduli_assembly/moduli_schema.json').read_text())
    store_screened_moduli(db, moduli)


if __name__ == "__main__":
    main()
