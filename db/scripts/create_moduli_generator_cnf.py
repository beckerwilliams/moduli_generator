#!/usr/bin/env python3
from config import default_config as config
from db.utils import cnf_argparser as argparser, create_moduli_generator_cnf, generate_random_password


def main(args):

    create_moduli_generator_cnf(
        config.project_name or 'moduli_generator',
        args.mariadb_host or 'localhost',
        **{
            "port": args.mariadb_port or 3306,
            "ssl": args.mariadb_ssl or "false",
            "database": args.mariadb_db_name or config.db_name,
            "password": generate_random_password()
        })


if __name__ == "__main__":
    args = argparser().parse_args()
    exit(main(args))
