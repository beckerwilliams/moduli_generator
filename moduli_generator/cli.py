#!/usr/bin/env python
import argparse
from datetime import (UTC, datetime)
from logging import (DEBUG, basicConfig, getLogger)
from pathlib import PosixPath as Path
from typing import Final

from db.moduli_db_utilities import MariaDBConnector
from moduli_generator import ModuliGenerator

DEFAULT_DIR: Final[str] = str(Path.home() / '.moduli_assembly')
DEFAULT_CANDIDATES_DIR: Final[str] = '.candidates'
DEFAULT_MODULI_DIR: Final[str] = '.moduli'
DEFAULT_LOG_DIR: Final[str] = '.logs'
DEFAULT_MARIADB_CONFIG: Final[str] = "moduli_generator.cnf"

DEFAULT_KEY_LENGTHS: Final[tuple[int, ...]] = (3072, 4096, 6144, 7680, 8192)


def parse_args():
    """Parse command line arguments for moduli_generator."""
    parser = argparse.ArgumentParser(
        description="Moduli Generator - Generate and manage secure moduli for cryptographic operations",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--key-lengths",
        type=int,
        nargs="+",
        default=DEFAULT_KEY_LENGTHS,
        help="Space-separated list of key lengths to generate moduli for"
    )
    parser.add_argument(
        "--moduli-home",
        type=str,
        default=DEFAULT_DIR,
        help="Base directory for moduli generation and storage"
    )
    parser.add_argument(
        "--candidates-dir",
        type=str,
        default=DEFAULT_CANDIDATES_DIR,
        help="Directory to store candidate moduli"
    )
    parser.add_argument(
        "--moduli-dir",
        type=str,
        default=DEFAULT_MODULI_DIR,
        help="Directory to store generated moduli"
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default=DEFAULT_LOG_DIR,
        help="Directory to store log files"
    )
    parser.add_argument(
        "--mariadb-config",
        type=str,
        default=DEFAULT_MARIADB_CONFIG,
        help="Path to MariaDB configuration file"
    )

    return parser.parse_args()


def main():
    """
    Main function for the moduli_generator package

    Default Start Runs 6 Key Lengts: 2048, 3072, 4096, 6144, 7680, 8192
    Takes about 22 hours to complete, yielding about 20 moduli per key_length
    on an i7 quad-core 3.7 GHz CPU with 32GB RAM.
    """
    # Parse command line arguments
    args = parse_args()

    # Set variables from args
    key_lengths = tuple(args.key_lengths)

    # setup File System
    moduli_home = Path(args.moduli_home)
    candidates_dir = moduli_home / args.candidates_dir
    moduli_dir = moduli_home / args.moduli_dir
    log_dir = moduli_home / args.log_dir
    mariadb_config = moduli_home / args.mariadb_config

    # Configure logging
    basicConfig(
        level=DEBUG,
        format='%(asctime)s - %(levelname)s: %(message)s',
        filename=log_dir / 'moduli_generator_main.log',
        filemode='a'
    )
    logger = getLogger(__name__)

    # Assure moduli filesystem exists or create it
    for pathobject in moduli_home, candidates_dir, moduli_dir, log_dir:
        pathobject.mkdir(parents=True, exist_ok=True)
        logger.info(f'Assure Operational: {pathobject}')

    generator = ModuliGenerator(nice_value=20,
                                key_lengths=key_lengths)
    logger.info(f'Moduli Generator Initialized wtih key_lengths: {key_lengths}')
    #
    # # Generate moduli
    start_time = datetime.now(UTC).replace(tzinfo=None)
    logger.info(f'Starting Moduli Generation at {start_time}')
    generated_files = generator.generate_moduli()
    logger.debug(f'Generated Moduli: {generated_files}')

    # Save moduli schema to JSON File after Each Run
    generator.save_moduli()  # to
    logger.debug(f'Save Moduli for run in JSON')

    # Store Screened Moduli in MariaDB
    db = MariaDBConnector(mariadb_config)
    logger.debug(f'MariaDB Connector Initialized')
    generator.store_moduli(db)  # To DB
    logger.info(f'Moduli stored in DB')

    # Summary
    duration = (datetime.now(UTC).replace(tzinfo=None) - start_time).seconds
    logger.debug(f'Moduli Generation Complete. Time taken: {duration} seconds')
    print(f'Moduli Generation Complete. Time taken: {duration} seconds')

    return 0


if __name__ == "__main__":
    exit(main())
