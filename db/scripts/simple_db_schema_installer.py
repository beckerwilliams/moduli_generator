from config import default_config
from create_moduli_generator_cnf import create_moduoi_generator_cnf
from db import MariaDBConnector
from db.utils import (InstallSchema, cnf_argparser as argparser, get_moduli_generator_schema_statements)


def main():
    args = argparser().parse_args()
    config = default_config
    config.mariadb_cnf = config.moduli_home / config.privileged_tmp_cnf

    # Create Application Owner's MariaDB Configuration File
    create_moduli_generator_cnf(
        config.get(project_name, 'moduli_generator'),
        args.get(host, 'localhost')
    )
    # _________________________________

    db = MariaDBConnector(config)
    installer = InstallSchema(db, config.db_name,
                              schema_statements=get_moduli_generator_schema_statements(config.db_name))

    if args.batch:
        success = installer.install_schema_batch()
    else:
        success = installer.install_schema()

    if success:
        print("Database schema installed successfully")


if __name__ == "__main__":
    exit(main())
