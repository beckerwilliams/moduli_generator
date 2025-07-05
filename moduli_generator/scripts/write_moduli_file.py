import argparse
from logging import (DEBUG, basicConfig, getLogger)
from pathlib import PosixPath as Path
from sys import exit

from db.moduli_db_utilities import MariaDBConnector
from moduli_generator.config import (ISO_UTC_TIMESTAMP, ModuliConfig, default_config)


def write_moduli_file(
        config: ModuliConfig = default_config,
):
    """
    Generates a moduli file for SSH configuration using parameters derived from the command-line
    or default settings. It pulls required data from a database and writes it to a
     user-specified or default directory as moduli_file.ssh-moduli.

    :param config: Configuration object specifying database and logging details
    :type config: ModuliConfig
    :return: None if executed without errors, otherwise logs appropriate diagnostics.
    :rtype: None
    """
    parser = argparse.ArgumentParser(description='Generate moduli file from database')
    parser.add_argument('--base-dir',
                        type=str,
                        default=None,
                        help='Base directory for moduli generation and storage'
                        )
    parser.add_argument('--output-file',
                        default=None,
                        type=str,
                        help='Path to output file (default: Path.home() / FRESH_MODULI_<COMPRESSED_DATE>.ssh-moduli2)'
                        )

    parser.add_argument('--moduli-per-keylength',
                        type=int,
                        default=80,  # We need 80 moduli per keylength for a robust /etc/ssh/moduli file
                        help='Number of moduli per key-length to capture in each produced moduli file'
                        )
    args = parser.parse_args()

    # Configure logging
    basicConfig(
        level=DEBUG,
        format='%(asctime)s - %(levelname)s: %(message)s',
        filename=config.log_file,
        filemode='a'
    )
    logger = getLogger(__name__)

    if args.base_dir:
        config.base_dir = Path(args.base_dir)
    db = MariaDBConnector(config)
    logger.debug(f'MariaDB Connector Initialized: {config}')

    # Determine the output file path
    if args.output_file:
        moduli_file = Path(args.output_file)
    else:
        moduli_file = Path.home() / f'FRESH_MODULI_{ISO_UTC_TIMESTAMP(compress=True)}.ssh-moduli2'

    if args.moduli_per_keylength:
        config.moduli_per_keylength = args.moduli_per_keylength

    # Get the records and save to the specified file
    fresh_moduli = db.get_moduli(moduli_file)
    if fresh_moduli:
        # Write Out Moduli FIle
        moduli_to_delete = db._write_moduli_to_file(fresh_moduli, moduli_file)
        logger.info(f'{len(fresh_moduli)*config.moduli_per_keylength} Moduli Records written to {moduli_file}')

        # Delete all records from db written to moduli file (tbd - decide when to remove)
        if True != True:
            for modulus in moduli_to_delete:
                db.delete_records(f'{db.db_name}.{db.table_name}', f'modulus = \"{modulus}\"')

        print(f'{len(fresh_moduli)} Moduli Records written to {moduli_file}')
        logger.info(f'{len(moduli_to_delete)} Moduli Records deleted from DB')
        print(f'{len(moduli_to_delete)} Moduli Records deleted from DB')

    return 0


if __name__ == "__main__":


    exit(write_moduli_file())
