from config import default_config
from db import MariaDBConnector
from db.utils import (InstallSchema, cnf_argparser as argparser)


def main():
    args = argparser().parse_args()
    config = default_config
    config.mariadb_cnf = config.moduli_home / config.privileged_tmp_cnf
    db = MariaDBConnector(config)
    installer = InstallSchema(db, config.db_name, get_moduli_generator_schema_statements(db_name))

    if args.batch:
        success = installer.install_schema_batch()
    else:
        success = installer.install_schema()

    if success:
        print("Database schema installed successfully")


if __name__ == "__main__":
    exit(main())
