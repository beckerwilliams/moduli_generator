# moduli_generator/__main__.py
from datetime import (UTC, datetime)
from logging import (DEBUG, basicConfig, getLogger)
from pathlib import PosixPath as Path

from db.moduli_db_utilities import MariaDBConnector
from moduli_generator import ModuliGenerator


def main():
    """
    Main function for the moduli_generator package
    """
    # Configure logging
    basicConfig(
        level=DEBUG,
        format='%(asctime)s - %(levelname)s: %(message)s',
        filename=Path.home() / '.moduli_assembly' / 'moduli_generation_main.log',
        filemode='a'
    )
    logger = getLogger(__name__)

    generator = ModuliGenerator(nice_value=15, key_lengths=(2048, 2048, 3074, 4096))

    # Generate moduli
    start_time = datetime.now(UTC).replace(tzinfo=None)
    logger.info(f'Starting Moduli Generation at {start_time}')

    generated_files = generator.generate_moduli()
    logger.info(f'Generated Moduli: {generated_files}')
    # Save moduli schema to JSON File after Each Run
    generator.save_moduli()  # to $HOME/.moduli_assembly

    # Store Screened Moduli in MariaDB
    db = MariaDBConnector("/Users/ron/development/moduli_generator/moduli_generator.cnf")
    generator.store_moduli(db)  # To DB
    logger.info(f'Moduli stored in DB')
    print('Moduli Stored in DB.')

    # Summary
    duration = (datetime.now(UTC).replace(tzinfo=None) - start_time).seconds
    logger.info(f'Moduli Generation Complete. Time taken: {duration} seconds')
    print(f'Moduli Generation Complete. Time taken: {duration} seconds')

    return 0


if __name__ == "__main__":
    exit(main())
