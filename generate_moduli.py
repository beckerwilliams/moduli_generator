from json import loads
from pathlib import PosixPath as Path
from time import time

from db.mg_mariadb_connector import MariaDBConnector, store_screened_moduli
from moduli_generator import ModuliGenerator


def generate_moduli(
        key_lengths: tuple[int, ...] = (3072, 4098, 6144, 7680, 8192),
        output_dir: Path = Path.home() / '.moduli_assembly',
        nice_value: int = 15,
        db_cnf: str = None
):
    generator = ModuliGenerator(
        key_lengths=(3072, 4098, 6144, 7680, 8192),
        nice_value=15
    )

    # Generate moduli
    start_time = time()
    generated_files = generator.generate_moduli()

    # Save moduli schema
    generator.save_moduli_schema()
    print(f'Moduli Generation Complete. Time taken: {time.time() - start_time:.2f} seconds')
    print('Generated Files: ', generated_files)

    # Test DB Work
    db = MariaDBConnector("/Users/ron/development/moduli_generator/moduli_generator.cnf")

    moduli = loads(Path('/Users/ron/development/moduli_generator/.moduli_assembly/moduli_schema.json').read_text())
    store_screened_moduli(db, moduli)


if __name__ == "__main__":
    generate_moduli()
