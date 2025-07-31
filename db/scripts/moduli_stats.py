import argparse
from json import (dump)
from logging import (DEBUG, basicConfig, getLogger)
from pathlib import PosixPath as Path
from sys import exit

from config import (ModuliConfig, default_config, iso_utc_timestamp)
from db import MariaDBConnector


def main(config: ModuliConfig = default_config, output_file=None):
    """
    Writes moduli records to a specified output file. Configures logging, connects to
        the MariaDB database using the provided configuration, retrieves moduli records,
        and writes them to the determined output file. The output file path can be
        specified or defaults to the home directory with a timestamped filename.

    Args:
        config (ModuliConfig, optional): Configuration object containing the necessary settings for the         database connection and logging.
        output_file (str or None, optional): Path to the desired output file where moduli records will         be written. Defaults to None, in which case a timestamped file will be         created in the user's home directory.

    Returns:
        List: A list of moduli records retrieved from the database and written to the         output file.
    """
    parser = argparse.ArgumentParser(description='Get modulus-counts by key-length from database')
    parser.add_argument(
        '--output-file',
        type=str,
        help='Path to output file (default: ${HOME}/FRESH_MODULI_<UTC_TIMESTAMP>.ssh2-moduli2)'
    )
    args = parser.parse_args()

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

    if output_file is None:
        status_file = Path.home() / f'MG_STATUS_{iso_utc_timestamp(compress=True)}.txt'
    else:
        status_file = Path(args.output_file)

    # Get the records and save to the specified file
    status = db.stats()
    with status_file.open('w') as of:
        dump(status, of, indent=4)

    # Print a header and then the installers
    logger.info(f'Key-Length: #Records')
    print(f'Key-Length: #Records')

    logger.info(f'Key-Length: #Records')
    for keysize in status:
        logger.info(f'{keysize}: {status[keysize]}')
        print(f'{keysize}: {status[keysize]}')


if __name__ == "__main__":
    exit(main())
