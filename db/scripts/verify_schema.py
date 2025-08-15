#!/usr/bin/env python
# Import the default configuration
from config import ModuliConfig, argparser_moduli_generator, iso_utc_time_notzinfo
from db import MariaDBConnector


def main(config: ModuliConfig = None):
    """
    CLI utility for the generation, saving, and storage of moduli. This function
        handles the entire workflow, including configuring paths, processing command-line arguments,
        ensuring the required directories exist, and carrying out moduli generation, storage,
        and cleanup. The workflow includes integration with MariaDB for storing resulting installers.

        Detail logs are generated throughout the process to facilitate debugging and tracking.

    Returns:
        Int: The return code of the CLI function where 0 indicates successful execution.
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

    # The Invocation
    try:
        MariaDBConnector(config)
    except RuntimeError as err:
        logger.error(
            "Are you pointing to the correct MariaDB instance and *.cnf?\n"
            f"Instantiating MariaDBConnector Failed: {err}"
        )
        return 1
    except ValueError as err:
        logger.error(f"ModuliDB Verification Failed: {err}")
        return 1
    except Exception as err:
        logger.error(f"ModuliDB Verification FAILED: {err}")
        return 2
    else:
        # Stats and Cleanup
        end_time = iso_utc_time_notzinfo()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"MariaDB Schema Validated. Time taken: {int(duration)} seconds")
        return 0

    logger.info(f"self: {self}: Connector Validated and Instantiated")


if __name__ == "__main__":
    exit(main())
