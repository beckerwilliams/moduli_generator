#!/usr/bin/env python3
from sys import exit

# Import the default configuration
from config import ModuliConfig, argparser_moduli_generator, iso_utc_time_notzinfo
from moduli_generator import ModuliGenerator


def main(config: ModuliConfig = None):
    """
    Store Moduli to DB

    Vacuums remaining Moduli produced in to DB, deleting source files.

    Args:
        config (ModuliConfig, optional): The configuration object for Moduli generation. If no configuration is
            provided, a default local configuration is obtained.

    Returns:
        int: An integer indicating the status of the Moduli generation process. Returns 0 for success, 1 for
            failure caused by a ValueError, and 2 for general exceptions.
    """

    if not config:
        config = argparser_moduli_generator.local_config()

    logger = config.get_logger()
    logger.name = __name__
    logger.debug(f"Using default config: {config}")

    # Generate, Screen, Store, and Write Moduli File
    start_time = iso_utc_time_notzinfo()
    logger.info(
        f'Starting Moduli Generation at {start_time.strftime("%Y-%m-%d %H:%M:%S")}, with {config.key_lengths} as moduli key-lengths'
    )

    # The Invocation - Generates Candidates and Screens for High Qualtiy DH GEX Moduli
    try:
        if config.store_moduli:
            (ModuliGenerator(config).store_moduli())

    except ValueError as err:
        logger.error(f"Moduli Generation Failed: {err}")
        return 1
    except Exception as err:
        logger.error(f"Moduli Generation Failed: {err}")
        return 2
    else:
        # Stats and Cleanup
        end_time = iso_utc_time_notzinfo()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Moduli Generation Complete. Time taken: {int(duration)} seconds")
        logger.info("Moduli Generation Complete")
        return 0


if __name__ == "__main__":
    exit(main())
