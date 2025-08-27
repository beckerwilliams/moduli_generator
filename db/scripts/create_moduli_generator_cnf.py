#!/usr/bin/env python3
import os
from argparse import ArgumentParser
from pathlib import Path

from config import default_config
from db.utils import create_moduli_generator_cnf


def argparser():
    """Create an ArgumentParser for create_moduli_generator_cnf command."""
    parser = ArgumentParser(
        description="Create a MariaDB configuration file for the moduli_generator user"
    )
    parser.add_argument(
        "--mariadb-cnf",
        type=str,
        help="Path to save the MariaDB configuration file",
    )
    parser.add_argument(
        "--user",
        type=str,
        default="moduli_generator",
        help="Username for MariaDB connection (default: moduli_generator)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Hostname for MariaDB connection (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=str,
        default="3306",
        help="Port for MariaDB connection (default: 3306)",
    )
    parser.add_argument(
        "--ssl",
        type=str,
        default="true",
        help="Whether to use SSL for MariaDB connection (default: true)",
    )
    parser.add_argument(
        "--password",
        type=str,
        help="Password for MariaDB connection (default: auto-generated)",
    )
    return parser


def main():
    """Create a MariaDB configuration file for the moduli_generator user."""
    config = default_config()
    args = argparser().parse_args()

    # Set up kwargs for create_moduli_generator_cnf
    kwargs = {
        "port": args.port,
        "ssl": args.ssl,
    }

    # Add password if provided
    if args.password:
        kwargs["password"] = args.password

    # Set output path
    if args.mariadb_cnf:
        mariadb_cnf_path = Path(args.mariadb_cnf)
        # If only directory is provided, use default filename
        if os.path.isdir(args.mariadb_cnf):
            mariadb_cnf_path = Path(args.mariadb_cnf) / "moduli_generator.cnf"
    else:
        mariadb_cnf_path = config.mariadb_cnf

    # Create the CNF file
    try:
        cnf_path = create_moduli_generator_cnf(args.user, args.host, **kwargs)

        # If a custom path was specified, move/copy the file
        if args.mariadb_cnf and cnf_path != mariadb_cnf_path:
            # Ensure directory exists
            os.makedirs(os.path.dirname(mariadb_cnf_path), exist_ok=True)
            # Copy content to the specified location
            with open(cnf_path, 'r') as src, open(mariadb_cnf_path, 'w') as dst:
                dst.write(src.read())
            print(f"Configuration file created at: {mariadb_cnf_path}")
        else:
            print(f"Configuration file created at: {cnf_path}")
        return 0
    except Exception as e:
        print(f"Error creating configuration file: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
