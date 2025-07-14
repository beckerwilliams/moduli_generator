import argparse
from logging import (DEBUG, basicConfig, getLogger)
from sys import exit

from db.moduli_db_utilities import MariaDBConnector
from moduli_generator.config import (ModuliConfig, default_config)


def write_moduli_file(
        args: argparse.Namespace = None,
        config: ModuliConfig = default_config,
):
    """
    Writes a moduli file based on the given arguments and configuration. This function retrieves fresh moduli
    records from the database, writes them to a file, and optionally deletes records from the database if
    configured to do so.

    :param args: Arguments passed to configure the moduli file writing process. It should typically contain
                 options such as `base_dir`, `output_file`, and `records_per_keylength`.
    :type args: argparse.Namespace, optional
    :param config: A configuration object specifying parameters for database interaction and file output.
    :type config: ModuliConfig, optional
    :return: The status code indicating the result of the operation. Zero (0) signifies success.
    :rtype: int
    """

    if args is not None:
        if args.base_dir is not None:
            config = config.with_base_dir(args.base_dir)
        if args.output_file is not None:
            config.moduli_file = args.output_file
        if args.records_per_keylength is not None:
            config.records_per_keylength = args.records_per_keylength
        if args.delete_records_on_moduli_write is not None:
            config.delete_records_on_moduli_write = args.delete_records_on_moduli_write

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

    # Get the records and save to the specified file
    fresh_moduli = db.get_and_write_moduli_file(config.moduli_file)
    if fresh_moduli:
        # Write Out Moduli File, Capture Moduli to Delete from DB
        moduli_to_delete = db.write_moduli_file(fresh_moduli, config.moduli_file)
        logger.info(
            f'{len(fresh_moduli) * config.records_per_keylength} Moduli Records written to {config.moduli_file}')
        print(f'{len(fresh_moduli)} Moduli Records written to {config.moduli_file}')

        # Delete all records from db written to moduli file (tbd - decide when to remove)
        if db.delete_records_on_moduli_write:
            for modulus in moduli_to_delete:
                db.delete_records(f'{db.db_name}.{db.table_name}', f'modulus = \"{modulus}\"')
                logger.info(f'{len(moduli_to_delete)} Moduli Records deleted from DB')
                print(f'{len(moduli_to_delete)} Moduli Records deleted from DB')

    return 0


if __name__ == "__main__":
    """
    Entrypoint for the script. This function parses command-line arguments and calls the write_moduli_file function
    """
    parser = argparse.ArgumentParser(description='Generate moduli file from database')
    parser.add_argument(
        '--base-dir',
        type=str,
        default=None,
        help='Base directory for moduli generation and storage'
    )
    parser.add_argument(
        '--output-file',
        default=None,
        type=str,
        help='Path to output file (default: Path.home() / FRESH_MODULI_<COMPRESSED_DATE>.ssh-moduli2)'
    )
    parser.add_argument(
        '--records-per-keylength',
        type=int,
        default=2,  # We need 80 moduli per keylength for a robust /etc/ssh/moduli file
        help='Number of moduli per key-length to capture in each produced moduli file'
    )
    parser.add_argument(
        "--delete-records-on-moduli-write",
        type=bool,
        default=False,
        help="Delete records from DB written to moduli file"
    )
    args = parser.parse_args()

    exit(write_moduli_file(args))
