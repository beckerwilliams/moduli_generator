#!/usr/bin/env python
from sys import exit

# Import the default configuration
from config import ModuliConfig, arg_parser, iso_utc_time_notzinfo
from moduli_generator import ModuliGenerator


def main(config: ModuliConfig = None):
    """
    Write GeneratorModuli SSH2 Moduli File

    Args:
        config (ModuliConfig or None): Configuration object for moduli generation. Defaults to None, in which case                    a local configuration instance is used.

    Returns:
        int: Status code indicating the result of the moduli generation process.              0 - Success              1 - Failure due to a ValueError              2 - General failure due to other exceptions
    """

    if not config:
        config = arg_parser.local_config()

    logger = config.get_logger()
    logger.name = __name__
    logger.debug(f'Using default config: {config}')

    # Generate, Screen, Store, and Write Moduli File
    start_time = iso_utc_time_notzinfo()
    logger.info(
        f'Starting Moduli Generation at {start_time.isoformat()}, with {config.key_lengths} as moduli key-lengths')

    # The Invocation
    try:
        (ModuliGenerator(config)
         .write_moduli_file())

    except ValueError as err:
        logger.error(f'Moduli Generation Failed: {err}')
        return 1
    except Exception as err:
        logger.error(f'Moduli Generation Failed: {err}')
        return 2
    else:
        # Stats and Cleanup
        end_time = iso_utc_time_notzinfo()
        duration = (end_time - start_time).total_seconds()
        logger.info(f'Moduli Generation Complete @{end_time.isoformat()}: Seconds: {int(duration)}')
        return 0


if __name__ == "__main__":
    exit(main())
