#!/usr/bin/env python
import argparse
from datetime import UTC, datetime
from sys import exit

# Import the default configuration
from config import (ModuliConfig, default_config)
# Import ModuliGenerator
from moduli_generator import ModuliGenerator


# Import MariaDBConnector

def parse_args_local_config():
    """
    Parse command-line arguments for the Moduli Generator and return the parsed arguments.

    This function uses the `argparse` module to define and parse command-line options used
    for managing the secure moduli generation process. It provides a variety of configurable
    options, including base directory settings, directory paths for storing generated moduli,
    and specific configuration file paths. Additionally, the function supports specifying
    key lengths for moduli generation as well as process priority settings through a nice value.

    :return: Parsed command-line arguments
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        description="Moduli Generator - Generate and manage secure moduli for cryptographic operations",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--key-lengths",
        type=int,
        nargs="+",
        default=default_config.key_lengths,
        help="Space-separated list of key lengths to generate moduli for"
    )
    parser.add_argument(
        "--moduli-home",
        type=str,
        default=str(default_config.moduli_home),
        help="Base directory for moduli generation and storage"
    )
    parser.add_argument(
        "--candidates-dir",
        type=str,
        default=str(default_config.candidates_dir.relative_to(default_config.moduli_home)),
        help="Directory to store candidate moduli (relative to moduli-home)"
    )
    parser.add_argument(
        "--moduli-dir",
        type=str,
        default=str(default_config.moduli_dir.relative_to(default_config.moduli_home)),
        help="Directory to store generated moduli (relative to moduli-home)"
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default=str(default_config.log_dir.relative_to(default_config.moduli_home)),
        help="Directory to store log files (relative to moduli-home)"
    )
    parser.add_argument(
        "--mariadb-cnf",
        type=str,
        default=str(default_config.mariadb_cnf.relative_to(default_config.moduli_home)),
        help="Path to MariaDB configuration file (relative to moduli-home)"
    )
    # Add a nice_value argument that might be missing
    parser.add_argument(
        "--nice-value",
        type=int,
        default=default_config.nice_value,
        help="Process nice value for CPU inensive operations"
    )
    parser.add_argument("--records-per-keylength",
                        type=int,
                        default=default_config.records_per_keylength,
                        help="Number of moduli per key-length to capture in each produced moduli file"
                        )
    parser.add_argument("--delete-records-on-moduli-write",
                        type=bool,
                        default=False,
                        help="Delete records from DB written to moduli file")
    parser.add_argument("--moduli_db",
                        type=str,
                        default=default_config.db_name,
                        help="Name of the database to create and Initialize")
    args = parser.parse_args()

    # Create a custom configuration based on the command line arguments
    config = default_config.with_base_dir(args.moduli_home)

    # Override with command line options if provided
    config.candidates_dir = config.moduli_home / args.candidates_dir
    config.moduli_dir = config.moduli_home / args.moduli_dir
    config.log_dir = config.moduli_home / args.log_dir
    config.moduli_generator_config = config.moduli_home / args.mariadb_cnf
    config.records_per_keylength = args.records_per_keylength
    config.delete_records_on_moduli_write = args.delete_records_on_moduli_write

    config.ensure_directories()
    config.key_lengths = tuple(args.key_lengths)
    config.nice_value = args.nice_value

    return config


def main(config: ModuliConfig):
    """
    CLI utility for the generation, saving, and storage of moduli. This function
    handles the entire workflow, including configuring paths, processing command-line arguments,
    ensuring the required directories exist, and carrying out moduli generation, storage,
    and cleanup. The workflow includes integration with MariaDB for storing resulting installers.

    Detail logs are generated throughout the process to facilitate debugging and tracking.

    :return: The return code of the CLI function where 0 indicates successful execution.
    :rtype: Int
    """

    logger = config.get_logger()
    logger.name = __name__

    logger.debug(f'Using default config: {config}')

    # Generate, Screen, Store, and Write Moduli File
    start_time = datetime.now(UTC).replace(tzinfo=None)

    logger.info(f'Starting Moduli Load {start_time}')
    db = ModuliGenerator(config)
    db.store_moduli()

    # Stats and Cleanup
    duration = (datetime.now(UTC).replace(tzinfo=None) - start_time).seconds
    logger.info(f'Moduli Generation Complete. Time taken: {duration/3600} hours')
    print(f'Moduli Generation Complete. Time taken: {duration/3600} hours')

    return 0


if __name__ == "__main__":
    exit(main(parse_args_local_config()))
