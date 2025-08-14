import secrets
import string
from argparse import ArgumentParser
from pathlib import PosixPath as Path
from sys import exit

from config import DEFAULT_MARIADB_DB
from db import MariaDBConnector


def argparse():
    """
    Parse command line arguments for the moduli generator user creation script.

    Returns:
        argparser.Namespace: Parsed command line arguments containing mariadb_cnf path and batch flag.
    """
    argparse = ArgumentParser(description="Install SSH Moduli Schema")
    argparse.add_argument(
        "--mariadb_cnf",
        default=str(Path.home() / ".moduli_generator" / "moduli_generator.tmp"),
        type=str,
        help="Path to Privileged MariaDB configuration file"
    )
    argparse.add_argument(
        "--batch",
        action="store_true",
        help="Use batch execution mode for better performance",
    )
    return argparse.parse_args()


def generate_random_password(length=16):
    """
    Generate a cryptographically secure random password.

    Args:
        length (int): Length of the password. Default is 16 characters.

    Returns:
        str: A random password containing a mix of letters, digits, and punctuation.
    """
    # Define character sets
    alphabet = string.ascii_letters + string.digits + string.punctuation

    # Generate the password using secrets module
    password = ''.join(secrets.choice(alphabet) for _ in range(length))

    return password


def create_moduli_generator_user(database, username, password=None):
    """
    Generate SQL statements to create a moduli_generator database user with appropriate privileges.

    Args:
        password (str, optional): Password for the moduli_generator user. If None, a random password is generated.

    Returns:
        list[str]: List of SQL statements to create user, grant privileges, and flush privileges.
    """
    if not database:
        database = DEFAULT_MARIADB_DB
    if not username:
        username = DEFAULT_MARIADB_USER
    if password is None:
        password = generate_random_password()

    statements = [
        "CREATE USER IF NOT EXISTS 'moduli_generator'@'%' "
        + f"IDENTIFIED BY '{password}' "
        + "MAX_CONNECTIONS_PER_HOUR 100 "
        + "MAX_UPDATES_PER_HOUR 200 "
        + "MAX_USER_CONNECTIONS 50; ",
        f"GRANT ALL PRIVILEGES ON {database}.* TO 'moduli_generator'@'%' WITH GRANT OPTION; ",
        "FLUSH PRIVILEGES; ",
    ]

    return password, statements


def main():
    """
    Main function to create the moduli_generator database user.

    Parses command line arguments, connects to MariaDB, and executes the user creation SQL statements.
    """
    args = argparse()

    db = MariaDBConnector()
    db.mariadb_cnf = Path(args.mariadb_cnf)
    # print(create_moduli_generator_user())
    db.execute_batch(create_moduli_generator_user())


if __name__ == "__main__":
    exit(main())
