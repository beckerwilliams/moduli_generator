from argparse import (ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace)

from config import (ModuliConfig, default_config)
from db import is_valid_identifier_sql

__all__ = ['local_config']


def _moduli_generator_argparser() -> Namespace:
    """
    Parse command-line arguments for the Moduli Generator and return the parsed arguments.

    This function uses the `argparse` module to define and parse command-line options used
    for managing the secure moduli generation process. It provides a variety of configurable
    options, including base directory settings, directory paths for storing generated moduli,
    and specific configuration file paths. Additionally, the function supports specifying
    key lengths for moduli generation as well as process priority settings through a nice value.

    :return: Parsed command-line arguments
    :rtype: argparse.Namespace
    """
    parser = ArgumentParser(
        description="Moduli Generator - Generate and manage secure moduli for cryptographic operations",
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--candidates-dir",
        type=str,
        default=str(default_config.candidates_dir.relative_to(default_config.moduli_home)),
        help="Directory to store candidate moduli (relative to moduli-home)")

    parser.add_argument(
        "--key-lengths",
        type=int,
        nargs="+",
        default=default_config.key_lengths,
        help="Space-separated list of key lengths to generate moduli for"
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default=str(default_config.log_dir.relative_to(default_config.moduli_home)),
        help="Directory to store log files (relative to moduli_home)"
    )
    parser.add_argument(
        "--mariadb-cnf",
        type=str,
        default=str(default_config.mariadb_cnf.relative_to(default_config.moduli_home)),
        help="Path to MariaDB configuration file (relative to moduli_home)"
    )
    parser.add_argument(
        "--moduli-dir",
        type=str,
        default=str(default_config.moduli_dir.relative_to(default_config.moduli_home)),
        help="Directory to store generated moduli (relative to moduli_home)"
    )
    parser.add_argument(
        "--moduli-home",
        type=str,
        default=str(default_config.moduli_home),
        help="Base directory for moduli generation and storage"
    )
    parser.add_argument(
        "--moduli-db",
        type=str,
        default=default_config.db_name,
        help="Name of the database to create and Initialize")
    # Add a nice_value argument that might be missing
    parser.add_argument(
        "--nice-value",
        type=int,
        default=default_config.nice_value,
        help="Process nice value for CPU intensive operations"
    )
    parser.add_argument(
        "--records-per-keylength",
        type=int,
        default=default_config.records_per_keylength,
        help="Number of moduli per key-length to capture in each produced moduli file"
    )
    parser.add_argument(
        "--preserve-moduli-after-dbstore",
        action='store_true',
        help="Delete records from DB written to moduli file")
    return parser.parse_args()


def local_config(args: Namespace = None) -> ModuliConfig:
    """
    Create a custom configuration based on the provided command line arguments.

    This function generates a configuration by overriding the default configuration
    with the input parameters passed. It also ensures required directories exist
    and applies specific settings based on the user-provided options.

    :param args: A Namespace object containing command line parameters that are required
        to customize the configuration.
    :type args: Namespace
    :return: A customized configuration object with updated properties based on
        the provided namespace.
    :rtype: ModuliConfig
    """

    # Create a custom configuration based on the command line arguments
    if args is None:
        args = _moduli_generator_argparser()

    # Create the config object first
    config = default_config.with_base_dir(args.moduli_home)

    # Verify user input prior to initialization
    if is_valid_identifier_sql(args.moduli_db):
        config.db_name = args.moduli_db
    else:
        raise RuntimeError(f"Invalid database name: {args.moduli_db}")

    # Override with command line options if provided
    config.candidates_dir = config.moduli_home / args.candidates_dir
    config.moduli_dir = config.moduli_home / args.moduli_dir
    config.log_dir = config.moduli_home / args.log_dir
    config.mariadb_cnf = config.moduli_home / args.mariadb_cnf
    config.records_per_keylength = args.records_per_keylength
    config.preserve_moduli_after_dbstore = args.preserve_moduli_after_dbstore

    config.ensure_directories()
    config.key_lengths = tuple(args.key_lengths)
    config.nice_value = args.nice_value

    return config


if __name__ == "__main__":
    # Only execute this when the module is run directly, not when imported
    mg_args = local_config()
    print(f'Moduli Generator Commands, Flags, and Options, Using default config: {mg_args}')
    print('\t\t\t** default_config **')
    print(f'# Argument: # Value')
    for item in vars(mg_args):
        print(f'{item} : {getattr(mg_args, item)}')
