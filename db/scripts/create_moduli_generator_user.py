from argparse import ArgumentParser
from pathlib import PosixPath as Path
from sys import exit

from db.moduli_db_utilities import MariaDBConnector


def argparse():
    argparse = ArgumentParser(description='Install SSH Moduli Schema')
    argparse.add_argument(
        'mariadb_cnf',
        type=str,
        help='Path to MariaDB configuration file'
    )
    argparse.add_argument(
        '--batch',
        action='store_true',
        help='Use batch execution mode for better performance'
    )
    return argparse.parse_args()


def create_moduli_generator_user(mg_password: str = "<PASSWORD>"):
    return [
        "CREATE USER IF NOT EXISTS 'moduli_generator'@'%' " +
        f"IDENTIFIED BY '{mg_password}' " +
        "MAX_CONNECTIONS_PER_HOUR 100 " +
        "MAX_UPDATES_PER_HOUR 200 " +
        "MAX_USER_CONNECTIONS 50; ",
        "GRANT ALL PRIVILEGES ON moduli_db.* TO 'moduli_generator'@'%' WITH GRANT OPTION; ",
        "FLUSH PRIVILEGES; "
    ]


def main():
    args = argparse()

    db = MariaDBConnector()
    db.mariadb_cnf = Path(args.mariadb_cnf)
    print(create_moduli_generator_user('faux_password'))
    db.execute_batch(create_moduli_generator_user('faux_password'))


if __name__ == "__main__":
    exit(main())
