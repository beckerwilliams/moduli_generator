def parse_args_local_config():
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
    parser = argparse.ArgumentParser(
        description="Moduli Generator - Generate and manage secure moduli for cryptographic operations",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--key-lengths",
        type=int,
        nargs="+",
        default=default_config.key_lengths,
        help="Space-separated list of key lengths to generate moduli for"
    )
    parser.add_argument(
        "--moduli-home",
        type=str,
        default=str(default_config.base_dir),
        help="Base directory for moduli generation and storage"
    )
    parser.add_argument(
        "--candidates-dir",
        type=str,
        default=str(default_config.candidates_dir.relative_to(default_config.base_dir)),
        help="Directory to store candidate moduli (relative to moduli-home)"
    )
    parser.add_argument(
        "--moduli-dir",
        type=str,
        default=str(default_config.moduli_dir.relative_to(default_config.base_dir)),
        help="Directory to store generated moduli (relative to moduli-home)"
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
    parser.add_argument("--delete-records-on-moduli-write",
                        type=bool,
                        default=False,
                        help="Delete records from DB written to moduli file")
    parser.add_argument("--moduli_db",
                        type=str,
                        default=default_config.db_name,
                        help="Name of the database to create and Initialize")

    return parser.parse_args()


