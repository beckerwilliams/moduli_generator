from argparse import ArgumentParser
from pathlib import Path

from config import DEFAULT_MARIADB_DB_NAME, default_config
from .install_update_user_fm_cnf import generate_random_password


def build_cnf(cnf_attrs: dict) -> str:
    """Build MariaDB Config File from Config"""
    local_cnf = ""
    for key, value in cnf_attrs.items():
        local_cnf += f"[{key}]\n"
        for k, v in value.items():
            local_cnf += f"{k} = {v}\n"
        local_cnf += "\n"
    return local_cnf


def create_moduli_generator_cnf(user, host, **kwargs) -> Path:
    """
    Creates a temporary MariaDB configuration file for the moduli generator with
    defined client connection settings based on the provided arguments and
    optional configurations.

    Args:
        user (str): The username for connecting to the MariaDB server.
        password (str): The password associated with the provided username.
        host (str): The host address of the MariaDB server.
        **kwargs: Additional optional configurations for the MariaDB connection.
            Supported keys:
            - "db_name" (str): The name of the database (default: DEFAULT_MARIADB_DB_NAME).
            - "port" (int): The port of the MariaDB server (default: 3306).
            - "ssl" (str): The SSL mode for the connection (default: "disabled").

    Returns:
        Path: The path to the created temporary MariaDB configuration file.
    """
    cnf_attrs = {
        "client": {
            "user": user,
            "host": host
        },
    }
    for attr in kwargs:
        cnf_attrs["client"][attr] = kwargs[attr]

    #            "database": kwargs.get("db_name", DEFAULT_MARIADB_DB_NAME),
    #            "Port": kwargs.get("port", 3306),
    #            "ssl": kwargs.get("ssl", "false"),
    #           "default-character-set": "utf8mb4"
    #        }
    #    }
    # Create a new Random Password if not provided
    if kwargs.get("password"):
        cnf_attrs["client"]["password"] = kwargs.get("password")
    else:  # Generate a random password
        cnf_attrs["client"]["password"] = generate_random_password()

    # BUILD MariaDB.cnf HEADER
    hdr = "\n".join(
        (
            "# This group is read by the client only.",
            "# Use it for options that only affect the client, see",
            "# https://mariadb.com/kb/en/configuring-mariadb-with-option-files/#option-groups",
        )
    )

    # Assemble and write the = config file
    tmp_cnf = build_cnf(cnf_attrs)
    mariadb_cnf = default_config.mariadb_cnf

    mariadb_cnf.write_text("\n".join((hdr, tmp_cnf)))
    return mariadb_cnf


def argparser() -> ArgumentParser:
    args = ArgumentParser(description="Create Moduli Generator Configuration File")
    args.add_argument(
        "username",
        help="Privileged MariaDB Username (Admin) | Mutually Exclusive with MariaDB Configuration File",
        default="'moduli_generator'@'%'"
    )
    args.add_argument(
        "host",
        help="Hostname of MariaDB Server | Mutually Exclusive with MariaDB Configuration File",
        default="localhost"
    )
    args.add_argument(
        "--password",
        type=str,
        help="Password for MariaDB CNF File. Will be generated if not provided",
        default=None
    )
    args.add_argument(
        "--port",
        type=int,
        help="Port of MariaDB Server | Mutually Exclusive with MariaDB Configuration File",
        default=3306
    )
    args.add_argument(
        "--ssl",
        type=str,
        help="SSL Mode of MariaDB Server | Mutually Exclusive with MariaDB Configuration File",
        default="false"
    )
    args.add_argument(
        "--db-name",
        type=str,
        default=DEFAULT_MARIADB_DB_NAME,
        help="The Name of User's Primary DB"
    )
    return args


def main():
    args = argparser().parse_args()

    create_moduli_generator_cnf(args.username, args.host, {
        "port": args.port,
        "ssl": args.ssl,
        "database": args.db_name,
        "password": args.password
    })


if __name__ == "__main__":
    exit(main)
