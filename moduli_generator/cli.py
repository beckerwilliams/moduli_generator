#!/usr/bin/env python
from datetime import UTC, datetime

# Import the default configuration
from config import (ModuliConfig)
# Import ModuliGenerator
from config.moduli_generator_arg_parser import config as local_config
from moduli_generator import ModuliGenerator



# Import MariaDBConnector

#
# def local_config():
#     """
#     Creates and returns a customized configuration object by overriding the default
#     configuration with values provided via command-line arguments.
#
#     The function modifies various attributes of the configuration object, including
#     directories and specific parameters for the functionality related to moduli
#     generation. It ensures that the required directories exist and updates the
#     configuration with the provided key lengths, nice value, database info, and additional
#     options as needed.
#
#     :param args: Command-line arguments containing values to override the default
#                  configuration.
#     :type args: argparse.Namespace
#
#     :return: A customized configuration object with modified attributes based on
#              the command-line arguments.
#     :rtype: Config
#     """
#     # Create a custom configuration based on the command line arguments
#     config = default_config.with_base_dir(args.moduli_home)
#
#     # Override with command line options if provided
#     config.candidates_dir = config.base_dir / args.candidates_dir
#     config.moduli_dir = config.base_dir / args.moduli_dir
#     config.log_dir = config.base_dir / args.log_dir
#     config.moduli_generator_config = config.base_dir / args.mariadb_cnf
#     config.records_per_keylength = args.records_per_keylength
#     config.delete_records_on_moduli_write = args.delete_records_on_moduli_write
#
#     config.ensure_directories()
#     config.key_lengths = tuple(args.key_lengths)
#     config.nice_value = args.nice_value
#
#     config.moduli_db = args.moduli_db  # tbd - add sql validtion to input arg
#
#     return config


def main(config: ModuliConfig):
    """
    CLI utility for the generation, saving, and storage of moduli. This function
    handles the entire workflow, including configuring paths, processing command-line arguments,
    ensuring the required directories exist, and carrying out moduli generation, storage,
    and cleanup. The workflow includes integration with MariaDB for storing resulting data.

    Detail logs are generated throughout the process to facilitate debugging and tracking.

    :return: The return code of the CLI function where 0 indicates successful execution.
    :rtype: Int
    """

    logger = config.get_logger()
    logger.name = __name__

    logger.debug(f'Using default config: {config}')

    # Generate, Screen, Store, and Write Moduli File
    start_time = datetime.now(UTC).replace(tzinfo=None)
    logger.info(f'Starting Moduli Generation at {start_time}')

    # The Invocation
    # (ModuliGenerator(config)
    #  .generate_moduli()
    #  .store_moduli()
    #  .write_moduli_file())

    ModuliGenerator(config).write_moduli_file()


# Stats and Cleanup
    duration = (datetime.now(UTC).replace(tzinfo=None) - start_time).seconds
    logger.info(f'Moduli Generation Complete. Time taken: {duration / 3600} hours')
    print(f'Moduli Generation Complete. Time taken: ({int(duration)} seconds)')

if __name__ == "__main__":
        exit(main(local_config))
