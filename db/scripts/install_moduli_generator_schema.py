#!/usr/bin/env python3
from config import default_config as config
from db import MariaDBConnector
from db.utils import (InstallSchema, cnf_argparser as argparser, get_moduli_generator_db_schema_statements,
                      get_moduli_generator_user_schema_statements)


def main():
    args = argparser().parse_args()
    # Privileged MariaDB Configuration File, DEFAULT `moduli_generator` user DOES NOT HAVE THESE PRIVILEGES
    config.mariadb_cnf = config.moduli_home / config.privileged_tmp_cnf
    db = MariaDBConnector(config)

    # Install `Moduli Generator` schema
    db_install = InstallSchema(db, get_moduli_generator_db_schema_statements(config.db_name))
    user_install = InstallSchema(db, config.db_name, get_moduli_generator_user_schema_statements(config.db_name))

    if args.batch:
        db_success = db_install.install_schema_batch()
        user_success = user_install.install_schema_batch()
        if not db_success or not user_success:
            return 1
    else:
        db_success = db_install.install_schema()
        user_success = user_install.install_schema()
        if not db_success or not user_success:
            return 2

    print("Database and User schema installed successfully")
    return 0


if __name__ == "__main__":
    exit(main())
