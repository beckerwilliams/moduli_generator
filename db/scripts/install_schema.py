from argparse import ArgumentParser
from pathlib import Path

from db.scripts.db_schema_for_named_db import get_moduli_generator_schema_statements
from db.moduli_db_utilities import (Error, MariaDBConnector, default_config)
from moduli_generator.config import DEFAULT_MARIADB


class InstallSchema(object):
    """
    Handles the installation of database schemas using various methods such
    as parameterized queries, batch execution, or from a schema file.

    This class provides functions to install the database schema efficiently,
    either by processing defined schema statements, using batch execution
    for improved performance, or reading and executing schema statements
    from a file. Its primary purpose is to ensure the database structure
    is correctly set up based on predefined schema definitions.

    :ivar db_conn: Database connector instance to execute queries.
    :type db_conn: MariaDBConnector
    :ivar db_name: Name of the database for schema installation.
    :type db_name: str
    :ivar schema_statements: List of schema statements required for
        installation. Contains queries, parameters, and fetch options.
    :type schema_statements: list
    """

    def __init__(self, db_connector: MariaDBConnector, db_name: str = DEFAULT_MARIADB):
        """
        Initializes the class with database connection, database name, and schema statements.
        The initialization process sets up the schema for the specified database.

        :param db_connector: Instance of MariaDBConnector used for connecting to the MariaDB database.
        :type db_connector: MariaDBConnector
        :param db_name: Name of the database where the schema will be installed. If not provided,
            it defaults to the configured DEFAULT_MARIADB constant.
        :type db_name: str
        """
        self.db_conn = db_connector
        self.db_name = db_name
        self.schema_statements = get_moduli_generator_schema_statements(db_name)
        print(f'Installing schema for database: {db_name}')

    def install_schema(self) -> bool:
        """
        Executes a series of schema installation statements stored in `schema_statements`. Each statement
        is executed using the provided database connection interface `db_conn`. If the installation is
        successful, it returns True; otherwise, if an exception occurs, it returns False.

        Schema installation includes iterating over the `schema_statements` and executing the statements
        with optional parameters and fetching capabilities as defined in the `schema_statements` list.

        :raises Exception: If any error occurs during the execution of schema statements.

        :return: Boolean indicating the success or failure of the schema installation process.
        :rtype: bool
        """
        try:
            for i, statement_info in enumerate(self.schema_statements):
                query = statement_info['query']
                params = statement_info.get('params')
                fetch = statement_info.get('fetch', False)

                # Skip empty statements
                if not query.strip():
                    continue

                print(f"Executing statement {i + 1}/{len(self.schema_statements)}: {query[:50]}...")

                # Execute the statement with parameters
                self.db_conn.sql(query, params, fetch)

            print("Schema installation completed successfully")
            return True

        except Exception as e:
            print(f"Error installing schema: {e}")
            return False

    def install_schema_batch(self) -> bool:
        """
        Installs schema statements in batch mode using a database connection.
        The method executes all provided schema statements within a single transaction
        to ensure atomicity. Each statement may include associated parameters.

        If the execution is successful, a success message is logged, and the method
        returns True. Otherwise, a failure message is logged, and the method returns False.
        In the case of an error, an exception message is printed, and the method also
        returns False.

        :return: A boolean indicating whether the schema installation succeeded
                 in batch mode.
        :rtype: bool
        """
        try:
            # Separate queries and parameters
            queries = []
            params_list = []

            for statement_info in self.schema_statements:
                query = statement_info['query']
                params = statement_info.get('params')

                if query.strip():
                    queries.append(query)
                    params_list.append(params)

            # Execute all statements in a single transaction
            success = self.db_conn.execute_batch(queries, params_list)

            if success:
                print("Schema installation completed successfully (batch mode)")
                return True
            else:
                print("Schema installation failed")
                return False

        except Exception as e:
            print(f"Error installing schema in batch mode: {e}")
            return False

    def install_schema_file(self, schema_file: Path = None) -> bool:
        """
        Install a database schema from a specified SQL file. The method reads the schema
        file, splits the content into individual SQL statements, and executes them.

        :param schema_file: Path to the SQL schema file. If not provided, a default
            file path "db/schema/ssh_moduli_schema.sql" is used.
        :type schema_file: Path
        :return: True if the schema installation completes successfully,
            False otherwise.
        :rtype: bool
        """
        if schema_file is None:
            schema_file = Path("db/schema/ssh_moduli_schema.sql")

        try:
            # Check if the schema file exists
            if not schema_file.exists():
                print(f"Schema file not found: {schema_file}")
                return False

            # Read the SQL schema file
            with open(schema_file, 'r') as sql_f:
                schema_content = sql_f.read()

            # Split into statements and execute
            sql_statements = [stmt.strip() for stmt in schema_content.split(';') if stmt.strip()]

            for statement in sql_statements:
                if statement.startswith('#') or not statement.strip():
                    continue

                print(f"Executing SQL statement: {statement[:50]}...")
                self.db_conn.sql(statement, fetch=False)

            print("Schema installation from file completed successfully")
            return True

        except Error as err:
            print(f"Error installing schema from file: {err}")
            return False


argparse = ArgumentParser(description='Install SSH Moduli Schema')

argparse.add_argument(
    '--moduli-db-name',
    type=str,
    default=DEFAULT_MARIADB,
    help='Name of the database to create'
)

argparse.add_argument(
    '--batch',
    action='store_true',
    help='Use batch execution mode for better performance'
)


def main():
    """
    Parses command line arguments to configure and connect to a database and
    installs a database schema using predefined configurations. The schema
    installation process can be executed in batch mode or in a standard mode.

    :raises SystemExit: If invalid arguments are passed during parsing.

    :return: Status of the database schema installation.
    :rtype: None
    """
    # Parse command line arguments
    args = argparse.parse_args()
    db_name = args.moduli_db_name
    use_batch = args.batch

    # Configure database connection
    config = default_config
    config.db_name = db_name
    config.mariadb_cnf = Path('rons_mariadb.cnf')

    print(
        f"Installing schema for database: {db_name} "
        f"with MariaDB config file: {config.mariadb_cnf}"
    )

    # Create an installer and run installation
    installer = InstallSchema(MariaDBConnector(config), db_name)

    if use_batch:
        success = installer.install_schema_batch()
    else:
        success = installer.install_schema()

    if success:
        print("Database schema installed successfully")
    else:
        print("Failed to install database schema")


if __name__ == "__main__":
    main()
