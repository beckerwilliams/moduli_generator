import secrets
import string
from argparse import ArgumentParser
from pathlib import Path

from config import DEFAULT_MARIADB_DB_NAME, default_config
from db import Error, MariaDBConnector
from db.scripts.db_schema_for_named_db import get_moduli_generator_schema_statements

__all__ = ["InstallSchema"]


# MariaDB.cnf Temporary Config File Attributes
def build_tmp_cnf(local_config: dict) -> str:
    # Assure no DB is specified
    if "database" in local_config["client"]:
        del local_config["client"]["database"]

    """Build MariaDB Config File from Config"""
    local_cnf = ""
    for key, value in local_config.items():
        local_cnf += f"[{key}]\n"
        for k, v in value.items():
            local_cnf += f"{k} = {v}\n"
        local_cnf += "\n"
    return local_cnf


def generate_random_password(length=default_config.password_length) -> str:
    """
    Generates a random password of the specified length, consisting of letters, digits,
    and MariaDB-recommended safe special characters. This method utilizes cryptographically
    secure random number generation to ensure unpredictability of the password.

    Args:
        length (int): The desired length of the generated password.

    Returns:
        str: A randomly generated password containing letters, digits, and safe special characters.
    """
    # Define character sets
    letters_digits = string.ascii_letters + string.digits
    # Include only MariaDB.com recommended safe special characters, excluding quotes and backslash
    safe_punctuation = '+-*/,.,:;!?#$%&@=^_~|<>()[]{}'
    alphabet = letters_digits + safe_punctuation

    # Generate the password using secrets module
    password = ''.join(secrets.choice(alphabet) for _ in range(length))

    return password


def create_moduli_generator_user(db_conn, database, password=None) -> str:
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
        password = generate_random_password()

    # SQL statements to create user, grant privileges, and flush privileges
    statements = [
        # Create User 'moduli_generator'@'%' and Grant All
        f"CREATE USER IF NOT EXISTS 'moduli_generator'@'%' IDENTIFIED BY '{password}' "
        "WITH MAX_CONNECTIONS_PER_HOUR 100 MAX_UPDATES_PER_HOUR 200 MAX_USER_CONNECTIONS 50",

        # GRANT ALL with GRANT OPTION on `moduli_generator`@'%'
        f"GRANT ALL PRIVILEGES ON {database}.* TO 'moduli_generator'@'%'",
        f"GRANT PROXY ON ''@'%' TO 'moduli_generator'@'%'",
        "FLUSH PRIVILEGES",

        # CREATE USER `moduli_generator`@`localhost` & GRANT ALL with GRANT OPTION on `moduli_generator`@'localhost'
        f"CREATE USER IF NOT EXISTS 'moduli_generator'@'localhost' IDENTIFIED BY '{password}' "
        "WITH MAX_CONNECTIONS_PER_HOUR 100 MAX_UPDATES_PER_HOUR 200 MAX_USER_CONNECTIONS 50",

        f"GRANT ALL PRIVILEGES ON {database}.* TO 'moduli_generator'@'localhost'",
        "FLUSH PRIVILEGES"
    ]

    # Execute the statements
    for statement in statements:
        db_conn.sql(statement, fetch=False)
        print(f"Executed: {statement[:50]}...")

    print(f"Created 'moduli_generator' user with access to '{database}' database")
    return password


def update_moduli_generator_config(host, database, username, password) -> Path:
    """
    Update the application owner's moduli_generator.cnf file with the new credentials.

    Args:
        database (str): The database name to connect to.
        username (str): The username for database connection.
        password (str): The password for database connection.

    Returns:
        Path: Path to the updated configuration file.
    """
    # Path to the final configuration file
    config_path = Path.home() / ".moduli_generator" / "moduli_generator.cnf"

    # Ensure directory exists
    config_dir = config_path.parent
    config_dir.mkdir(parents=True, exist_ok=True)

    # MariaDB.cnf HEADER
    hdr = "\n".join(
        (
            "# This group is read both by the client and the server",
            "# use it for options that affect everything, see",
            "# https://mariadb.com/kb/en/configuring-mariadb-with-option-files/#option-groups",
        )
    )

    # Build the configuration content
    config_content = {
        "client": {
            "user": username,
            "password": password,
            "database": database,
            "host": host,
            "default-character-set": "utf8mb4"
        }
    }

    # Format the configuration file content
    tmp_cnf = ""
    for key, value in config_content.items():
        tmp_cnf += f"[{key}]\n"
        for k, v in value.items():
            tmp_cnf += f"{k} = {v}\n"
        tmp_cnf += "\n"

    # Write the configuration file
    config_path.write_text("\n".join((hdr, tmp_cnf)))

    print(f"Updated configuration file: {config_path}")
    return config_path


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

    Args:
        db_conn (MariaDBConnector): Parameter description.
        db_name (str): Parameter description.
        schema_statements (list): Parameter description.
    """

    def __init__(
            self, db_connector: MariaDBConnector, db_name: str = default_config.db_name
    ):
        """
        Initializes the class with database connection, database name, and schema statements.
                The initialization process sets up the schema for the specified database.

        Args:
            db_connector (MariaDBConnector): Instance of MariaDBConnector used for connecting to the MariaDB database.
            db_name (str): Name of the database where the schema will be installed. If not provided,
            it defaults to the configured DEFAULT_MARIADB constant.7
        """
        self.db_conn = db_connector
        self.db_name = db_name
        self.schema_statements = get_moduli_generator_schema_statements(db_name)
        print(f"Installing schema for database: {db_name}")

    def install_schema(self) -> bool:
        """
        Executes a series of schema installation statements stored in `schema_statements`. Each statement
                is executed using the provided database connection interface `db_conn`. If the installation is
                successful, it returns True; otherwise, if an exception occurs, it returns False.

                Schema installation includes iterating over the `schema_statements` and executing the statements
                with optional parameters and fetching capabilities as defined in the `schema_statements` list.

        Returns:
            bool: Boolean indicating the success or failure of the schema installation process.

        Raises:
            Exception: If any error occurs during the execution of schema statements.
        """
        try:
            for i, statement_info in enumerate(self.schema_statements):
                query = statement_info["query"]
                params = statement_info.get("params")
                fetch = statement_info.get("fetch", False)

                # Skip empty statements
                if not query.strip():
                    continue

                print(
                    f"Executing statement {i + 1}/{len(self.schema_statements)}: {query[:50]}..."
                )

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

        Returns:
            bool: A boolean indicating whether the schema installation succeeded in batch mode.
        """
        try:
            # Separate queries and parameters
            queries = []
            params_list = []

            for statement_info in self.schema_statements:
                query = statement_info["query"]
                params = statement_info.get("params")

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

        Args:
            schema_file (Path): Path to the SQL schema file. If not provided, the default
                   schema file from the data.schema.ssh_moduli_schema.sql package resource is used.

        Returns:
            bool: True if the schema installation completes successfully, False otherwise.
        """
        try:
            # If no schema file is provided, return False
            if schema_file is None:
                print("No schema file provided")
                return False

            # Check if the provided schema file exists
            if not schema_file.exists():
                print(f"Schema file not found: {schema_file}")
                return False

            # Read the SQL schema file
            with open(schema_file, "r") as sql_f:
                schema_content = sql_f.read()

            # Split into statements and execute
            sql_statements = [
                stmt.strip() for stmt in schema_content.split(";") if stmt.strip()
            ]

            for statement in sql_statements:
                if statement.startswith("#") or not statement.strip():
                    continue

                print(f"Executing SQL statement: {statement[:50]}...")
                self.db_conn.sql(statement, fetch=False)

            print("Schema installation from file completed successfully")
            return True

        except Error as err:
            print(f"Error installing schema from file: {err}")
            return False


# NOTE: If config.privleged_tmp_file EXISTS - USE IT (Ignore other inputs)
# NOTE: If config.privleged_tmp_file DOES NOT EXIST - USE ALL OTHER INPUTS

def argparser() -> ArgumentParser:
    args = ArgumentParser(description="Install SSH Moduli Schema")
    args.add_argument(
        "--mariadb-cnf",
        type=str,
        default="privileged.tmp",
        help="Path to Privileged MariaDB Config: default ${MODULI_GENERATOR_HOME}/.moduli_generator/privileged.tmp"
    )
    args.add_argument(
        "--mariadb-admin-username",
        help="Privileged MariaDB Username (Admin) | Mutually Exclusive with MariaDB Configuration File",
        default=None
    )
    args.add_argument(
        "--mariadb-admin-password",
        help="Privileged MariaDB Password (Admin) | Mutually Exclusive with MariaDB Configuration File",
        default=None,
    )
    args.add_argument(

        "--mariadb-host",
        help="Hostname of MariaDB Server | Mutually Exclusive with MariaDB Configuration File",
        default="localhost"
    )
    args.add_argument(
        "--mariadb-port",
        type=int,
        help="Port of MariaDB Server | Mutually Exclusive with MariaDB Configuration File",
        default=3306
    )
    args.add_argument(
        "--mariadb-socket",
        type=str,
        help="Socket of MariaDB Server | Mutually Exclusive with MariaDB Configuration File",
        default="/var/run/mysql/mysql.sock",
    )
    args.add_argument(
        "--mariadb-ssl",
        help="SSL Mode of MariaDB Server | Mutually Exclusive with MariaDB Configuration File",
        default=True
    )
    args.add_argument(
        "--mariadb-db-name",
        type=str,
        default=DEFAULT_MARIADB_DB_NAME,
        help="Name of the database to create"
    )
    args.add_argument(
        "--batch",
        action="store_true",
        help="Use batch execution mode for better performance",
    )
    args.add_argument(
        "--moduli-db-name",
        type=str,
        default=DEFAULT_MARIADB_DB_NAME,
        help="Name of the database to create",
    )
    return args


def main():
    """
    Main script for installing SSH Moduli's database schema.

    This script provides functionality to configure and install a database schema
    into a MariaDB database. It supports four use cases for configuration:

    1. Using a MariaDB configuration file specified via --mariadb-cnf
    2. Using admin credentials (username, password, host, port) to create a temporary config
    3. Using an existing configuration file at ${HOME}/.moduli_generator/moduli_generator.cnf
    4. Failing if none of the above conditions are met

    The user can opt for batch execution mode for improved performance.

    The script uses the `argparser` module for parsing command-line arguments and
    handles required parameters for setting up the database connection. The
    database schema installation process is facilitated by creating an installer
    instance for either batch or default execution modes.

    Raises:
        SystemExit: If no valid configuration method is available.

    Args:
        --mariadb-cnf (str): Path to the MariaDB configuration file.
        --mariadb-admin-username (str): Username of the MariaDB admin user.
        --mariadb-admin-password (str): Password for the MariaDB admin user.
        --mariadb-host (str): Hostname of the MariaDB server (default: localhost).
        --mariadb-port (int): Port of the MariaDB server (default: 3306).
        --mariadb-socket (str): Socket path for the MariaDB server.
        --mariadb-ssl (bool): Whether to use SSL for the connection.
        --batch (bool): Flag to operate in batch execution mode.
        --moduli-db-name (str): Name of the database to create. Defaults to
        DEFAULT_MARIADB_DB_NAME.

    Example Output:
        The script outputs messages regarding the progress and success or failure
        of database schema installation.
    """

    # NOTE: ANYTIME We're HERE - moduli_home has ALREADY been SETUP but NO LOCAL `moduli_generator.cnf` EXISTS
    # So the NO CREDENTIALS Setup is Bogus

    args = argparser().parse_args()

    # Configure database connection
    config = default_config
    config.db_name = args.moduli_db_name
    config.mariadb_host = args.mariadb_host
    config.mariadb_port = args.mariadb_port
    config.mariadb_socket = args.mariadb_socket
    config.mariadb_ssl = args.mariadb_ssl
    config.mariadb_db_name = args.mariadb_db_name

    # Default path for the moduli_generator.cnf file
    default_cnf_path = config.moduli_generator_home / config.mariadb_cnf_file
    temporary_cnf_path = config.moduli_generator_home / config.privileged_tmp_file

    # Case A: config.privileged_cnf_file EXISTS - USE IT (Ignore other inputs)

    # Case B: config.privileged_cnf_file DOES NOT EXIST - USE ALL OTHER INPUTS

    if config.privileged_cnf_file.exists() and config.privileged_cnf_file.is_file():
        config.mariadb_cnf = config.privileged_cnf_file
        print(f"Using existing config file: {config.mariadb_cnf}")
    else:
        create_args = (args.mariadb_admin_username, args.mariadb_admin_password, args.host)
        config.mariadb_cnf = create_moduli_generator_cnf(*create_args)

    if temporary_cnf_path.exists() and temporary_cnf_path.is_file():
        config.mariadb_cnf = temporary_cnf_path
        print(f"Using existing temporary config file: {config.mariadb_cnf}")

    # Case 1: --mariadb-cnf is provided on command line, use that file
    if args.mariadb_cnf:
        config.mariadb_cnf = Path(args.mariadb_cnf)
        print(f"Using provided MariaDB config file: {config.mariadb_cnf}")

        # Check if the file exists
        if not config.mariadb_cnf.exists():
            raise SystemExit(f"MariaDB configuration file not found: {config.mariadb_cnf}")

    # Case 2: admin credentials are provided, create a temporary config file  -

    elif args.mariadb_admin_username and args.mariadb_admin_password and args.host:
        print("Using provided admin credentials and host argument to create temporary config file")

        user_build_args = (args.mariadb_admin_username, args.mariadb_admin_password, args.host)

        # Create a new config dictionary with the provided credentials
        tmp_config = {
            "client": {
                "user": args.mariadb_admin_username,
                "password": args.mariadb_admin_password,
                "host": args.mariadb_host,
                "port": args.mariadb_port,
                "socket": args.mariadb_socket,
                "ssl": args.mariadb_ssl
            }
        }

        # Set the path for the temporary config file
        config.mariadb_cnf = (
                Path.home()
                / ".moduli_generator"
                / config.privileged_tmp_file
        )

        # Ensure the .moduli_generator directory exists
        config.mariadb_cnf.parent.mkdir(parents=True, exist_ok=True)

        # MariaDB.cnf HEADER
        hdr = "\n".join(
            (
                "# This group is read both by the client and the server",
                "# use it for options that affect everything, see",
                "# https://mariadb.com/kb/en/configuring-mariadb-with-option-files/#option-groups"
                "[client]"
            )
        )

        # Assemble and write the temporary config file
        tmp_cnf = build_tmp_cnf(tmp_config)
        config.mariadb_cnf.write_text("\n".join((hdr, tmp_cnf)))

    # Case 3: Use the existing moduli_generator.cnf file
    elif default_cnf_path.exists() and default_cnf_path.is_file():
        config.mariadb_cnf = default_cnf_path
        print(f"Using existing MariaDB config file: {config.mariadb_cnf}")

    # Case 4: Fail if none of the above conditions exist
    else:
        raise SystemExit(
            "No valid configuration method available. Either:\n"
            "1. Provide --mariadb-cnf parameter\n"
            "2. Provide --mariadb-admin-username and --mariadb-admin-password\n"
            "3. Ensure ${HOME}/.moduli_generator/moduli_generator.cnf exists"
        )

    print(
        f"Installing schema for database: {config.db_name} "
        f"with MariaDB config file: {config.mariadb_cnf}"
    )

    # Create a single database connector instance
    db_connector = MariaDBConnector(config)

    # Create an installer and run installation
    installer = InstallSchema(db_connector, config.db_name)

    if args.batch:
        success = installer.install_schema_batch()
    else:
        success = installer.install_schema()

    if success:

        print(f"Successfully created moduli_generator user and updated configuration at {config_path}")
    else:
        print("Failed to install database schema")


if __name__ == "__main__":
    exit(main())
