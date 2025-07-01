from logging import (DEBUG, basicConfig, getLogger)
from pathlib import PosixPath as Path
from sys import exit

from db.moduli_db_utilities import MariaDBConnector
from moduli_generator.config import (ModuliConfig, default_config)


def write_moduli_file(
    config: ModuliConfig = default_config,
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

    # Or just get the records without saving to a file
    fresh_moduli = db.get_moduli(Path.home() / 'FRESH_MODULI.ssh' )
    if fresh_moduli:
        logger.info(f'{len(fresh_moduli)} Moduli Records written to "FRESH_MODULI.ssh"')


if __name__ == "__main__":
    exit(write_moduli_file())
