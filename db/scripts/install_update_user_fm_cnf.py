import os
import secrets
import string
from argparse import ArgumentParser
from pathlib import PosixPath as Path
from sys import exit

from config import default_config
from db import MariaDBConnector, parse_mysql_config

__all__ = ["create_moduli_generator_user",
           "generate_random_password"]


def argparse():
    """
    Parse command line arguments for the moduli generator user creation script.

    Returns:
        argparser.Namespace: Parsed command line arguments containing mariadb_cnf path and batch flag.
    """
    argparse = ArgumentParser(description="Install SSH Moduli Schema")
    argparse.add_argument(
        "login_cnf",
        default=str(Path.home() / ".moduli_generator" / "privileged.tmp"),
        type=str,
        help="Path to Privileged MariaDB configuration file: CANNOT BE Application's MariaDB Config"
    )
    argparse.add_argument(
        "--new-user-password",
        type=str,
        help="Password for the moduli_generator user. If not provided, a random password is generated.",
        default=None
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
    # Define character sets, Use MariaDB Safe Punctiuation (no ", ', or \)
    safe_punctuation = '+-*/,.,:;!?#$%&@=^_~|<>()[]{}'

    alphabet = (string.ascii_letters + string.digits + safe_punctuation)

    # Generate the password using the secrets module
    password = ''.join(secrets.choice(alphabet) for _ in range(length))

    return password


def create_moduli_generator_user(db_conn, database=default_config.db_name, password=None):
    """
    Create a moduli_generator database user with appropriate privileges.

    Args:
        db_conn (MariaDBConnector): Database connector instance to execute queries.
        database (str): The database name to grant privileges for.
        password (str, optional): Password for the moduli_generator user. If None, a random password is generated.

    Returns:
        str: The password used for the moduli_generator user.
    """
    if password is None:
        password = generate_random_password(32)

    # Check if the configuration file exists before attempting to parse it
    if not os.path.exists(db_conn.mariadb_cnf):
        raise FileNotFoundError(f"Configuration file not found: {db_conn.mariadb_cnf}")

    # Get config from the database connector's configuration
    parsed_cnf = parse_mysql_config(db_conn.mariadb_cnf)

    if 'client' not in parsed_cnf or 'host' not in parsed_cnf['client']:
        raise RuntimeError("Invalid configuration file. Missing 'host' in [client] section in configuration file.")

    host = parsed_cnf['client'].get('host', 'localhost')
    database = parsed_cnf['client'].get('database', database)
    port = parsed_cnf['client'].get('port', '3306')
    ssl = parsed_cnf['client'].get('ssl', 'true')
    username = parsed_cnf['client'].get('user', 'root')

    print(f"Using MariaDB connection: {username}@{host}:{port}")
    print(f"Using MariaDB SSL: {ssl}")
    print(f"Using MariaDB Database: {database}")

    # SQL statements to create user, grant privileges, and flush privileges
    statements = [
        # Create user if not exists
        f"CREATE USER IF NOT EXISTS 'moduli_generator'@'%' IDENTIFIED BY '{password}' "
        "WITH MAX_CONNECTIONS_PER_HOUR 100 "
        "MAX_UPDATES_PER_HOUR 200 "
        "MAX_USER_CONNECTIONS 50",

        # Grant privileges
        f"GRANT ALL PRIVILEGES ON {database}.* TO 'moduli_generator'@'%' WITH GRANT OPTION",

        # Flush privileges
        "FLUSH PRIVILEGES"
    ]

    # Execute the statements
    for statement in statements:
        db_conn.sql(statement, fetch=False)
        print(f"Executed: {statement[:50]}...")

    print(f"Created 'moduli_generator' user with access to '{database}' database")
    return


def main():
    """
    Main function to create or update the moduli_generator database user.

    Parses command line arguments, connects to MariaDB, and executes the user creation SQL statements.
    """
    args = argparse()

    # Verify the login_cnf file exists before proceeding
    login_cnf_path = Path(args.login_cnf)
    if not login_cnf_path.exists():
        print(f"Error: Configuration file not found: {login_cnf_path}")
        print("Please create the configuration file first using build_moduli_generator_mariadb_config.sh")
        return 1

    db = MariaDBConnector()
    db.mariadb_cnf = login_cnf_path
    print(f"Using provided MariaDB config file: {db.mariadb_cnf}")

    try:
        password = create_moduli_generator_user(db, password=args.new_user_password)
        print(f"Successfully created moduli_generator user")
        if args.new_user_password is None:
            print(f"Generated password: {password}")
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except RuntimeError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
