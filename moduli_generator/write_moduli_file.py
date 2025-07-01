import argparse
from logging import (DEBUG, basicConfig, getLogger)
from pathlib import PosixPath as Path
from sys import exit

from db.moduli_db_utilities import MariaDBConnector
from moduli_generator.config import (ISO_UTC_TIMESTAMP, ModuliConfig, default_config)


def write_moduli_file(
        config: ModuliConfig = default_config,
        output_file=None,
):
    # Configure logging
    basicConfig(
        level=DEBUG,
        format='%(asctime)s - %(levelname)s: %(message)s',
        filename=config.log_file,
        filemode='a'
    )
    logger = getLogger(__name__)

    db = MariaDBConnector(config)
    logger.debug(f'MariaDB Connector Initialized: {config}')

    # Determine the output file path
    if output_file:
        moduli_file = Path(output_file)
    else:
        moduli_file = Path.home() / f'FRESH_MODULI_{ISO_UTC_TIMESTAMP(compress=True)}.ssh'

    # Get the records and save to the specified file
    fresh_moduli = db.get_moduli(moduli_file)
    if fresh_moduli:
        logger.info(f'{len(fresh_moduli)} Moduli Records written to {moduli_file}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate moduli file from database')
    parser.add_argument('--output-file', default=None, type=str, help='Path to output file (default: None)')

    args = parser.parse_args()
    exit(write_moduli_file(output_file=args.output_file))
