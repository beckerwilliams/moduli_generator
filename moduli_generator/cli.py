#!/usr/bin/env python
from datetime import (UTC, datetime)
from logging import (DEBUG, basicConfig, getLogger)
from pathlib import PosixPath as Path
from typing import Final

from db.moduli_db_utilities import MariaDBConnector
from moduli_generator import ModuliGenerator

DEFAULT_DIR: Final[Path] = Path.home() / '.moduli_assembly'
DEFAULT_CANDIDATES_DIR: Final[Path] = DEFAULT_DIR / '.candidates'
DEFAULT_MODULI_DIR: Final[Path] = DEFAULT_DIR / '.moduli'
DEFAULT_LOG_DIR: Final[Path] = DEFAULT_DIR / '.logs'
DEFAULT_MARIADB_CONFIG: Final[Path] = DEFAULT_DIR / "moduli_generator.cnf"


def main():
    """
    Main function for the moduli_generator package

    Default Start Runs 6 Key Lengts: 2048, 3072, 4096, 6144, 7680, 8192
    Takes about 22 hours to complete, yielding about 20 moduli per key_length
    on an i7 quad-core 3.7 GHz CPU with 32GB RAM.

        """
    # Assure Logging Filesytem Exists
    DEFAULT_DIR.mkdir(parents=True, exist_ok=True)
    DEFAULT_LOG_DIR.mkdir(parents=True, exist_ok=True)
    DEFAULT_MODULI_DIR.mkdir(parents=True, exist_ok=True)
    DEFAULT_CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)

    # Configure logging
    basicConfig(
        level=DEBUG,
        format='%(asctime)s - %(levelname)s: %(message)s',
        filename=DEFAULT_LOG_DIR / 'moduli_generator_main.log',
        filemode='a'
    )
    logger = getLogger(__name__)

    # # For testing, we limit to the TUPLE (2048, 2048) as it's ~ 5 minutes to process
    generator = ModuliGenerator(nice_value=20, key_lengths=(3072, 4096, 6144, 7680, 8192))
    logger.info(f'Moduli Generator Initialized')
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
    db = MariaDBConnector(DEFAULT_MARIADB_CONFIG)
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
