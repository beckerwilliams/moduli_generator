from datetime import (UTC, datetime)

from db.moduli_db_utilities import MariaDBConnector
from moduli_generator import (ModuliGenerator)

if __name__ == "__main__":
    generator = ModuliGenerator(nice_value=15, key_lengths=(2048,))

    # Generate moduli
    start_time = datetime.now(UTC).replace(tzinfo=None)
    generated_files = generator.generate_moduli()

    # Save moduli schema to JSON File after Each Run
    generator.save_moduli_schema()  # to $HOME/.moduli_assembly

    # Store Screened Moduli in MariaDB
    db = MariaDBConnector("/Users/ron/development/moduli_generator/moduli_generator.cnf")
    generator.store_moduli_schema(db)  # To DB

    duration = (datetime.now(UTC).replace(tzinfo=None) - start_time).seconds
    print(f'Moduli Generation Complete. Time taken: {duration}')
