#!/usr/bin/env python
from sys import exit

# Import the default configuration
from config import ModuliConfig, arg_parser, iso_utc_time
from moduli_generator import ModuliGenerator


def main(config: ModuliConfig = None):
    """
    CLI utility for the generation, saving, and storage of moduli. This function
    handles the entire workflow, including configuring paths, processing command-line arguments,
    ensuring the required directories exist, and carrying out moduli generation, storage,
    and cleanup. The workflow includes integration with MariaDB for storing resulting installers.

    Detail logs are generated throughout the process to facilitate debugging and tracking.

    :return: The return code of the CLI function where 0 indicates successful execution.
    :rtype: Int
    """

    if not config:
        config = arg_parser.local_config()

    logger = config.get_logger()
    logger.name = __name__
    logger.debug(f'Using default config: {config}')

    # Generate, Screen, Store, and Write Moduli File
    start_time = iso_utc_time()
    logger.info(
        f'Starting Moduli Generation at {start_time.strftime("%Y-%m-%d %H:%M:%S")}, with {config.key_lengths} as moduli key-lengths')

    # The Invocation
    try:
        (ModuliGenerator(config)
         .generate_moduli()
         .store_moduli()
         .write_moduli_file())

    except ValueError as err:
        logger.error(f'Moduli Generation Failed: {err}')
        return 1
    except Exception as err:
        logger.error(f'Moduli Generation Failed: {err}')
        return 2
    else:
        # Stats and Cleanup
        end_time = iso_utc_time()
        duration = (end_time - start_time).total_seconds()
        logger.info(f'Moduli Generation Complete. Time taken: {int(duration)} seconds')
        logger.info('Moduli Generation Complete')
        return 0


if __name__ == "__main__":
    exit(main())
