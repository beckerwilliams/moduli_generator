#!/usr/bin/env python
from sys import exit

# Import the default configuration
from config import ModuliConfig, argparser_moduli_generator, iso_utc_time_notzinfo
from moduli_generator import ModuliGenerator


def main(config: ModuliConfig = None):
    """
    Main function to handle the moduli generation process, including generating,
    screening, storing, and writing moduli files. It also logs the process,
    providing detailed information about the progress and any errors encountered.

    Args:
        config (ModuliConfig, optional): Configuration object that specifies the
            details for moduli generation. If not provided, a default local
            configuration is applied.

    Returns:
        int: Exit code indicating the status of the operation. `0` for success,
        `1` for a ValueError during processing, and `2` for any other exceptions.

    Raises:
        ValueError: Raised if any specific errors related to moduli generation
            occur within the try block.
        Exception: Raised for any unexpected errors during the operation.
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
        if config.restart:
            (ModuliGenerator(config).restart_screening().store_moduli())
        else:
            (ModuliGenerator(config).generate_moduli().store_moduli().write_moduli_file())

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
