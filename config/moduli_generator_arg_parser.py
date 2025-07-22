from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace

from config import (default_config)

__all__ = ['config']


def local_config(namespace: Namespace = None) -> dict[str, any]:
    """
    Create a custom configuration based on the provided command line arguments.

    This function generates a configuration by overriding the default configuration
    with the input parameters passed. It also ensures required directories exist
    and applies specific settings based on the user-provided options.

    :param namespace: A Namespace object containing command line parameters required
        to customize the configuration.
    :type namespace: Namespace
    :return: A customized configuration object with updated properties based on
        the provided namespace.
    :rtype: Config
    """
    # Create a custom configuration based on the command line arguments
    config = default_config.with_base_dir(namespace.moduli_home)

    # Override with command line options if provided
    config.candidates_dir = config.base_dir / namespace.candidates_dir
    config.moduli_dir = config.base_dir / namespace.moduli_dir
    config.log_dir = config.base_dir / namespace.log_dir
    config.moduli_generator_config = config.base_dir / namespace.mariadb_cnf
    config.records_per_keylength = namespace.records_per_keylength
    config.delete_records_on_moduli_write = namespace.delete_records_on_moduli_write

    config.ensure_directories()
    config.key_lengths = tuple(namespace.key_lengths)
    config.nice_value = namespace.nice_value

    config.moduli_db = namespace.moduli_db  # tbd - add sql validtion to input arg

    return config


def moduli_generator_argparser() -> dict[str, any]:
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
        default=str(default_config.candidates_dir.relative_to(default_config.base_dir)),
        help="Directory to store candidate moduli (relative to moduli-home)"
    )
    parser.add_argument("--delete-records-on-moduli-write",
                        type=bool,
                        default=False,
                        help="Delete records from DB written to moduli file")
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
        default=str(default_config.log_dir.relative_to(default_config.base_dir)),
        help="Directory to store log files (relative to moduli-home)"
    )
    parser.add_argument(
        "--mariadb-cnf",
        type=str,
        default=str(default_config.mariadb_cnf.relative_to(default_config.base_dir)),
        help="Path to MariaDB configuration file (relative to moduli-home)"
    )
    parser.add_argument(
        "--moduli-dir",
        type=str,
        default=str(default_config.moduli_dir.relative_to(default_config.base_dir)),
        help="Directory to store generated moduli (relative to moduli-home)"
    )
    parser.add_argument(
        "--moduli-home",
        type=str,
        default=str(default_config.base_dir),
        help="Base directory for moduli generation and storage"
    )
    parser.add_argument("--moduli_db",
                        type=str,
                        default=default_config.db_name,
                        help="Name of the database to create and Initialize")
    # Add a nice_value argument that might be missing
    parser.add_argument(
        "--nice-value",
        type=int,
        default=default_config.nice_value,
        help="Process nice value for CPU inensive operations"
    )
    parser.add_argument("--records-per-keylength",
                        type=int,
                        default=default_config.records_per_keylength,
                        help="Number of moduli per key-length to capture in each produced moduli file"
                        )

    return parser.parse_args()


config = local_config(moduli_generator_argparser())

if __name__ == "__main__":
    print(f'Moduli Generator Commands, Flags, and Options, Using default config: {config}')
    print(f'#Argument: #Value')
    for item in vars(config):
        print(f'{item} : {getattr(config, item)}')