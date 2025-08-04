from argparse import ArgumentParser
from pathlib import PosixPath as Path
from sys import exit

from config import DEFAULT_MARIADB_CNF, TEST_MARIADB, default_config
from db.scripts.install_schema import InstallSchema
from moduli_generator import ModuliGenerator


def arg_parser():
    """
    Parses command-line arguments for the SSH Moduli Schema installation script.

        This function creates an argument parser to handle input parameters and options
        for the SSH Moduli Schema installation process. The parser allows customization
        of parameters, such as the base directory for moduli generation and storage,
        the path to the MariaDB configuration file, and the execution mode.

    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    argparse = ArgumentParser(description="Install SSH Moduli Schema")
    argparse.add_argument(
        "--moduli-home",
        default=str(default_config.moduli_home),
        help=f"Change the Base directory for moduli generation and storage: default {default_config.moduli_home}",
    )
    argparse.add_argument(
        "--mariadb-cnf",
        type=str,
        default=str(Path.home() / DEFAULT_MARIADB_CNF),
        help="Path to MariaDB configuration file",
    )
    argparse.add_argument(
        "--mariadb-name",
        type=str,
        default=TEST_MARIADB,
        help="Name of the database to create and Initialize",
    )
    argparse.add_argument(
        "--batch",
        action="store_true",
        help="Use batch execution mode for better performance",
    )
    return argparse.parse_args()


def create_moduli_generator_home():
    """
    Creates a home directory setup for the ModuliGenerator tool. This function initializes the
        ModuliGenerator instance and configures its base directory using the provided arguments. Additionally,
        it ensures that a specified MariaDB configuration file is copied, if it exists, into the ModuliGenerator's
        home directory.

    Returns:
        int: Exit code indicating the result of the operation. Returns 0 on success, 1 if the MariaDB              configuration file is not found.

    Raises:
        FileNotFoundError: If the MariaDB configuration file specified in the arguments does not exist.
    """
    args = arg_parser()
    config = default_config
    config.db_name = args.mariadb_name
    config.moduli_home = Path(args.moduli_home)
    generator = ModuliGenerator(config)

    # Move Identified mysql.cnf to Moduli Generator run directory, `${HOME}/.moduli_generator/moduli_generator.cnf`
    if Path(args.mariadb_cnf).exists():
        """
        Copy  file from arguments to .moduli_generator base directory
        Default Location for `moduli_generator.cnf` is user's Home Directory
        """
        if not Path(generator.config.mariadb_cnf).exists():
            Path(generator.config.mariadb_cnf).write_text(
                Path(args.mariadb_cnf).read_text()
            )

        # Now let's Initialize the MariaDB Database
        installer = InstallSchema(
            generator.db,
            (
                generator.config.db_name
                if hasattr(generator.config, "db_name")
                else "moduli_db"
            ),
        )
        if args.batch:
            installer.install_schema_batch()
        else:
            installer.install_schema()

    else:
        print(f"MariaDB config file not found: {args.mariadb_cnf}")
        return 1

    return 0


if __name__ == "__main__":
    exit(create_moduli_generator_home())
