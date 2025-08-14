import secrets
import string
from argparse import ArgumentParser
from pathlib import Path

from config import DEFAULT_MARIADB_CNF, DEFAULT_MARIADB_DB_NAME, default_config
from db import MariaDBConnector, parse_mysql_config
from db.scripts.db_schema_for_named_db import get_moduli_generator_schema_statements

__all__ = ["InstallSchema"]


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


def create_moduli_generator_user(db_conn, database, password=None):
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


def update_moduli_generator_config(database, username, password):
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
    config_path = Path.home() / ".moduli_generator" / DEFAULT_MARIADB_CNF

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
            self, db_connector: MariaDBConnector, db_name: str = DEFAULT_MARIADB_DB_NAME
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


def argparser() -> ArgumentParser:
    args = ArgumentParser(description="Install SSH Moduli Schema")
    args.add_argument(
        "--mariadb-cnf",
        type=str,
        help="Path to MariaDB configuration file | Mutually Exclusive with Admin Credentials"
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
        default=True)
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
    into a MariaDB database. It allows users to specify the MariaDB database
    configuration either via a configuration file or through separate admin
    credentials. The user can opt for batch execution mode for improved performance.

    The script uses the `argparser` module for parsing command-line arguments and
    handles required parameters for setting up the database connection. The
    database schema installation process is facilitated by creating an installer
    instance for either batch or default execution modes.

    Raises:
        SystemExit: If neither a MariaDB configuration file nor admin credentials
        are provided.

    Args:
        --mariadb-cnf (str): Path to the MariaDB configuration file, if available.
        --admin-username (str): Username of the MariaDB admin user.
        --admin-password (str): Password for the MariaDB admin user.
        --batch (bool): Flag to operate in batch execution mode.
        --moduli-db-name (str): Name of the database to create. Defaults to
        DEFAULT_MARIADB.

    Example Output:
        The script outputs messages regarding the progress and success or failure
        of database schema installation.
    """
    args = argparser().parse_args()

    # Configure database connection
    config = default_config
    config.db_name = args.moduli_db_name

    # 1. If maradb.cnf is provided, use it
    # 2.  otherwise, build mariadb_tmp.cnf from provided credentials AND the connection
    #       temporary mariadb.cnf file, `moduli_generator_tmp.cnf`, from the profile buit during
    #       Command Line Installer

    # Case 1. Privilged mariadb.cnf
    if args.mariadb_cnf:
        config.mariadb_cnf = Path(args.mariadb_cnf)

    # Case 2. Separate Admin credentials
    elif args.mariadb_admin_username and args.mariadb_admin_password:

        config.mariadb_cnf = None

        # READ ${HOME}/.moduli_generator/moduli_generator.cnf, use all but username, password to build temp.cnf
        default_cnf = Path.home() / ".moduli_generator" / DEFAULT_MARIADB_CNF
        if not (default_cnf.exists() and default_cnf.is_file()):
            raise SystemExit(
                "Missing MariaDB configuration file, Please Run `Moduli Generator` Command Line Installer, first."
            )

        # Get current `moduli generator` default profile, Update username and password from user input from args, here
        tmp_config = parse_mysql_config(default_cnf)
        tmp_config["client"]["user"] = args.mariadb_admin_username
        tmp_config["client"]["password"] = args.mariadb_admin_password
        tmp_config["client"]["host"] = args.mariadb_host
        # Eliminate database record from tmp_config if exists.
        # We don't want an error selecting a database that has yet to be created
        if "database" in tmp_config["client"]:
            del tmp_config["client"]["database"]  # assure no database record

        # At installation - we need `None` Specified for DATABASE specified in Connection Request
        config.db_name = args.moduli_db_name

        config.mariadb_cnf = (
                Path.home()
                / ".moduli_generator"
                / Path(DEFAULT_MARIADB_CNF).with_suffix(".tmp")
        )

        # MariaDB.cnf HEADER
        hdr = "\n".join(
            (
                "# This group is read both by the client and the server",
                "# use it for options that affect everything, see",
                "# https://mariadb.com/kb/en/configuring-mariadb-with-option-files/#option-groups",
            )
        )

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

        # assemble priviliged.CNF file content
        tmp_cnf = build_tmp_cnf(tmp_config)
        # Write the Privileged MariaDB config file
        config.mariadb_cnf.write_text("\n".join((hdr, tmp_cnf)))
        # Set the Privileged MariaDB config into local config

    # Failure
    else:
        raise SystemExit("Missing MariaDB configuration file or admin credentials")

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
        print("Database schema installed successfully")

        ######################################################################################################
        # Now let's create `moduli_generator` user and finalize the application owner's `moduli_generator.cnf`
        ######################################################################################################
        print("\nCreating moduli_generator user and finalizing configuration...")

        # 1. Create the moduli_generator user with the generated password and grant privileges
        password = create_moduli_generator_user(db_connector, config.db_name)

        # 2. Update the application owner's configuration file
        config_path = update_moduli_generator_config(
            database=config.db_name,
            username="moduli_generator",
            password=password
        )

        print(f"Successfully created moduli_generator user and updated configuration at {config_path}")
    else:
        print("Failed to install database schema")


if __name__ == "__main__":
    exit(main())
