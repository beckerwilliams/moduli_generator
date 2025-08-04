from argparse import ArgumentParser
from pathlib import PosixPath as Path
from sys import exit

from db import MariaDBConnector


def argparse():
    """
    Parse command line arguments for the moduli generator user creation script.

    Returns:
        argparse.Namespace: Parsed command line arguments containing mariadb_cnf path and batch flag.
    """
    argparse = ArgumentParser(description="Install SSH Moduli Schema")
    argparse.add_argument(
        "mariadb_cnf", type=str, help="Path to MariaDB configuration file"
    )
    argparse.add_argument(
        "--batch",
        action="store_true",
        help="Use batch execution mode for better performance",
    )
    return argparse.parse_args()


def create_moduli_generator_user(moduli_generator_owner_pw: str = "<PASSWORD>"):
    """
    Generate SQL statements to create a moduli_generator database user with appropriate privileges.

    Args:
        moduli_generator_owner_pw (str): Password for the moduli_generator user. Defaults to "<PASSWORD>".

    Returns:
        list[str]: List of SQL statements to create user, grant privileges, and flush privileges.
    """
    return [
        "CREATE USER IF NOT EXISTS 'moduli_generator'@'%' "
        + f"IDENTIFIED BY '{moduli_generator_owner_pw}' "
        + "MAX_CONNECTIONS_PER_HOUR 100 "
        + "MAX_UPDATES_PER_HOUR 200 "
        + "MAX_USER_CONNECTIONS 50; ",
        "GRANT ALL PRIVILEGES ON moduli_db.* TO 'moduli_generator'@'%' WITH GRANT OPTION; ",
        "FLUSH PRIVILEGES; ",
    ]


def main():
    """
    Main function to create the moduli_generator database user.

    Parses command line arguments, connects to MariaDB, and executes the user creation SQL statements.
    """
    args = argparse()

    db = MariaDBConnector()
    db.mariadb_cnf = Path(args.mariadb_cnf)
    print(create_moduli_generator_user("faux_password"))
    db.execute_batch(create_moduli_generator_user("faux_password"))


if __name__ == "__main__":
    exit(main())
