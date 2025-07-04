import argparse
from logging import (DEBUG, basicConfig, getLogger)
from pathlib import PosixPath as Path
from sys import exit

from db.moduli_db_utilities import MariaDBConnector
from moduli_generator.config import (ISO_UTC_TIMESTAMP, ModuliConfig, default_config)


def test_show_stats(
        config: ModuliConfig = default_config,
        output_file=None,
):
    """
    Writes moduli records to a specified output file. Configures logging, connects to
    the MariaDB database using the provided configuration, retrieves moduli records,
    and writes them to the determined output file. The output file path can be
    specified or defaults to the home directory with a timestamped filename.

    :param config: Configuration object containing the necessary settings for the
        database connection and logging.
    :type config: ModuliConfig, optional
    :param output_file: Path to the desired output file where moduli records will
        be written. Defaults to None, in which case a timestamped file will be
        created in the user's home directory.
    :type output_file: str or None, optional
    :return: A list of moduli records retrieved from the database and written to the
        output file.
    :rtype: list
    """
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

    # Determine the output file path
    if output_file:
        moduli_file = Path(output_file)
    else:
        moduli_file = Path.home() / f'FRESH_MODULI_{ISO_UTC_TIMESTAMP(compress=True)}.ssh-moduli2'

    # Get the records and save to the specified file
    status = db.stats()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate moduli file from database')
    parser.add_argument('--output-file', default=None, type=str, help='Path to output file (default: None)')

    args = parser.parse_args()
    exit(test_show_stats(output_file=args.output_file))
