import secrets
import string
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Callable, Dict, List

from config import default_config
from db import MariaDBConnector
from db.common import (get_mysql_config_value, is_valid_identifier_sql, parse_mysql_config)

__all__ = [
    "InstallSchema",
    "build_cnf",
    "cnf_argparser",
    "create_moduli_generator_cnf",
    "generate_random_password",
    "get_moduli_generator_db_schema_statements",
    "get_moduli_generator_user_schema_statements",
    "get_mysql_config_value",
    "parse_mysql_config",
    "update_mariadb_app_owner",
    "is_valid_identifier_sql"
]


class InstallSchema(object):
    """
    Manages the installation of database schemas in a MariaDB database.

    This class provides functionality to manage and execute database schema installation
    via direct schema statements, batch execution, or from a schema file. It leverages
    a MariaDB connector for database operations and supports configurable schema statements.

    Attributes:
        config (Config): The default configuration object for the application.
        db (MariaDBConnector): The database connector instance used to execute schema statements.
        schema_statements (List[Dict[str, Any]]): List of schema statements to be executed, including
            SQL queries and optional parameters.
    """

    def __init__(
            self,
            db: MariaDBConnector,
            schema_statements_function: Callable[[str], List[Dict[str, Any]]],
            db_name: str = default_config().db_name
    ):
        """
        Initializes the class with database connection, database name, and schema statements.
                The initialization process sets up the schema for the specified database.

        Args:
            db (MariaDBConnector): Instance of MariaDBConnector used for connecting to the MariaDB database.
            db_name (str): Name of the database where the schema will be installed. If not provided,
            it defaults to the configured DEFAULT_MARIADB constant.7
        """
        self.config = default_config()
        self.db = db
        self.schema_statements = schema_statements_function(db_name)

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
                self.db.sql(query, params, fetch)

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
            success = self.db.execute_batch(queries, params_list)

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
                self.db.sql(statement, fetch=False)

            print("Schema installation from file completed successfully")
            return True

        except Exception as err:
            print(f"Error installing schema from file: {err}")
            return False


def cnf_argparser() -> ArgumentParser:
    config = default_config()
    args = ArgumentParser(description="Install SSH Moduli Schema")
    args.add_argument(
        "--mariadb-cnf",
        type=str,
        default=None,
        help="Path to Standard 'moduli_generator' MariaDB Config: "
             "default ${MODULI_GENERATOR_HOME}/.moduli_generator/privileged.tmp"
    )
    args.add_argument(
        "--mariadb-privilged-cnf",
        type=str,
        default=None,
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
        "--mariadb-db-name",
        type=str,
        default=config.db_name,
        help="Name of the database to create"
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
        default=None,
    )
    args.add_argument(
        "--mariadb-ssl",
        action="store_true",
        help="SSL Mode of MariaDB Server | Mutually Exclusive with MariaDB Configuration File",
    )

    args.add_argument(
        "--batch",
        action="store_true",
        help="Use batch execution mode for better performance",
    )
    args.add_argument(
        "--output-cnf",
        type=str,
        default=str(config.moduli_home / "moduli_generator.cnf"),
        help="Path to output configuration file"
    )

    return args


def get_moduli_generator_user_schema_statements(database) -> List[Dict[str, Any]]:
    """
    Generates a series of SQL statements required to create a database user, assign relevant
    privileges, and manage connections and updates for the `moduli_generator` user. This
    method ensures that both remote and localhost access configurations for the user are
    created, and privileges are applied effectively.

    Args:
        database (str): The name of the database for which the user privileges need to
            be set.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries where each dictionary contains an
            SQL query string (`query`), its corresponding parameters (`params`), and a
            `fetch` flag indicating whether the operation requires fetching data.
    """
    config = default_config()
    password = generate_random_password()

    # Create `moduli_generator.cnf` MariaDB CNF File
    create_moduli_generator_cnf(
        'moduli_generator',
        'localhost',
        **{
            "port": 3306,
            "ssl": "false",
            "database": config.db_name,
            "password": password
        })

    # SQL statements to create user, grant privileges, and flush privileges
    return [
        {
            "query": "CREATE USER IF NOT EXISTS 'moduli_generator'@'%' IDENTIFIED BY %s "
                     "WITH MAX_CONNECTIONS_PER_HOUR 100 MAX_UPDATES_PER_HOUR 200 MAX_USER_CONNECTIONS 50",
            "params": (password,),
            "fetch": False,
        },
        {
            "query": f"GRANT ALL PRIVILEGES ON {database}.* TO 'moduli_generator'@'%'",
            "params": None,
            "fetch": False,
        },
        {
            "query": "FLUSH PRIVILEGES",
            "params": None,
            "fetch": False,
        },
        {
            "query": "CREATE USER IF NOT EXISTS 'moduli_generator'@'localhost' IDENTIFIED BY %s "
                     "WITH MAX_CONNECTIONS_PER_HOUR 100 MAX_UPDATES_PER_HOUR 200 MAX_USER_CONNECTIONS 50",
            "params": (password,),
            "fetch": False,
        },
        {
            "query": f"GRANT ALL PRIVILEGES ON {database}.* TO 'moduli_generator'@'localhost'",
            "params": None,
            "fetch": False,
        },
        {
            "query": "FLUSH PRIVILEGES",
            "params": None,
            "fetch": False,
        }
    ]


def get_moduli_generator_db_schema_statements(moduli_db: str = "test_moduli_db") -> List[Dict[str, Any]]:
    """
    Generates MySQL schema creation and configuration statements for a moduli generator database.

    This function produces a list of SQL query dictionaries necessary to create the database
    and its tables, views, and indexes to store and manage moduli and related information.
    It also includes initialization statements for constants required in the database.

    Args:
        moduli_db (str): Name of the database to hold moduli-related tables and data. Defaults to
            "test_moduli_db".

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing SQL queries, optional parameters,
        and fetch flags for creating and configuring the database schema.

    Raises:
        ValueError: If the provided `moduli_db` name contains invalid characters.
    """
    # Note: Database/table names cannot be parameterized in MySQL/MariaDB,
    # so we still need to validate and use f-strings for identifiers
    if not moduli_db.replace("_", "").replace("-", "").isalnum():
        raise ValueError(f"Invalid database name: moduli_db")

    return [
        {
            "query": "CREATE DATABASE IF NOT EXISTS moduli_db",
            "params": None,
            "fetch": False,
        },
        {
            "query": f"""
            CREATE TABLE moduli_db.mod_fl_consts 
            (
                config_id TINYINT UNSIGNED PRIMARY KEY,
                type ENUM('2', '5') NOT NULL COMMENT 'Generator type (2 or 5)',
                tests VARCHAR(50) NOT NULL COMMENT 'Tests performed on the modulus',
                trials INT UNSIGNED NOT NULL COMMENT 'Number of trials performed',
                generator BIGINT UNSIGNED NOT NULL COMMENT 'Generator value',
                description VARCHAR(255) COMMENT 'Moduli Generator (R) OpenSSH2 moduli properties'
            )""",
            "params": None,
            "fetch": False,
        },
        {
            "query": f"""INSERT INTO moduli_db.mod_fl_consts (config_id, type, tests, trials, generator, description)
                VALUES (%s, %s, %s, %s, %s, %s) \
                """,
            "params": (
                1,
                "2",
                "6",
                100,
                2,
                "Moduli Generator (R) SSH moduli properties",
            ),
            "fetch": False,
        },
        {
            "query": f"""CREATE TABLE IF NOT EXISTS moduli_db.moduli (
                id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME NOT NULL,
                config_id TINYINT UNSIGNED NOT NULL COMMENT 'Foreign key to moduli constants',
                size INT UNSIGNED NOT NULL COMMENT 'Key size in bits',
                modulus TEXT NOT NULL COMMENT 'Prime modulus value',
                modulus_hash VARCHAR(128) GENERATED ALWAYS AS (SHA2(modulus, 512)) STORED COMMENT 'Hash of modulus',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (config_id) REFERENCES mod_fl_consts(config_id),
                UNIQUE KEY (modulus_hash)
            )""",
            "params": None,
            "fetch": False,
        },
        {
            "query": f"""CREATE VIEW IF NOT EXISTS moduli_db.moduli_view AS
            SELECT
                m.timestamp,
                c.type,
                c.tests,
                c.trials,
                m.size,
                c.generator,
                m.modulus
            FROM
                moduli_db.moduli m
                    JOIN
                moduli_db.mod_fl_consts c ON m.config_id = c.config_id""",
            "params": None,
            "fetch": False,
        },
        {
            "query": f"CREATE INDEX idx_size ON moduli_db.moduli(size)",
            "params": None,
            "fetch": False,
        },
        {
            "query": f"CREATE INDEX idx_timestamp ON moduli_db.moduli(timestamp)",
            "params": None,
            "fetch": False,
        },
        {
            "query": f"""CREATE TABLE IF NOT EXISTS moduli_db.moduli_archive
                        (
                            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                            timestamp DATETIME NOT NULL,
                            config_id TINYINT UNSIGNED NOT NULL COMMENT 'Foreign key to moduli constants',
                            size INT UNSIGNED NOT NULL COMMENT 'Key size in bits',
                            modulus TEXT NOT NULL COMMENT 'Prime modulus value',
                            modulus_hash VARCHAR(128) GENERATED ALWAYS AS (SHA2(modulus, 512)) STORED COMMENT 'Hash of modulus',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (config_id) REFERENCES mod_fl_consts(config_id),
                            UNIQUE KEY (modulus_hash)
                       )""",
            "params": None,
            "fetch": False
        },
        {
            "query": f"""CREATE VIEW IF NOT EXISTS moduli_db.moduli_archive_view AS
        SELECT
            m.timestamp,
            c.type,
            c.tests,
            c.trials,
            m.size,
            c.generator,
            m.modulus
        FROM
            moduli_db.moduli_archive m
                JOIN
            moduli_db.mod_fl_consts c ON m.config_id = c.config_id""",
            "params": None,
            "fetch": False,
        },
        {
            "query": f"CREATE INDEX idx_size ON moduli_db.moduli_archive(size)",
            "params": None,
            "fetch": False
        },
        {
            "query": f"CREATE INDEX idx_timestamp ON moduli_db.moduli_archive(timestamp)",
            "params": None,
            "fetch": False
        }
    ]


def update_mariadb_app_owner(host, database, username, password) -> Path:
    """
    Updates the MariaDB client's application owner configuration file.

    This function generates a MariaDB client configuration file with the specified
    connection parameters. It ensures the necessary directory exists, formats the
    configuration content, includes a header with relevant documentation, and writes
    it to a local configuration file. The final configuration file is saved in the home
    directory under `.moduli_generator`.

    Args:
        host (str): The hostname or IP address of the MariaDB server.
        database (str): The name of the database to connect to.
        username (str): The MariaDB username.
        password (str): The password for the specified MariaDB user.

    Returns:
        Path: The path to the generated configuration file.
    """
    # Path to the final configuration file
    config_path = config.moduli_home / "moduli_generator.cnf"

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




def build_cnf(cnf_attrs: dict) -> str:
    """
    Builds a configuration text from a nested dictionary structure.

    This function takes a dictionary representing configuration attributes and their
    values, iterates over the structure, and constructs a configuration (CNF) file
    representation in text format. Each top-level key in the dictionary is treated
    as a section, while its corresponding dictionary value defines key-value pairs
    within that section.

    Args:
        cnf_attrs (dict): A dictionary where each key is a section name, and its
            value is another dictionary containing key-value pairs for that
            section.

    Returns:
        str: A string representing the generated configuration (CNF) file content.
    """
    local_cnf = ""
    for key, value in cnf_attrs.items():
        local_cnf += f"[{key}]\n"
        for k, v in value.items():
            local_cnf += f"{k} = {v}\n"
        local_cnf += "\n"
    return local_cnf


def create_moduli_generator_cnf(user: str, host: str, **kwargs: Dict[str, str]) -> Path:
    """
    Creates and returns a MariaDB configuration file (CNF) for the moduli generator.

    This function builds and writes a MariaDB CNF file based on the provided client
    configuration details. If a password is not supplied in the optional arguments,
    a random password is generated. The CNF file is assembled with a predefined
    header and client-specific settings derived from the arguments and keyword
    arguments.

    Args:
        user (str): The username for the client configuration.
        host (str): The host for the client configuration.
        **kwargs: Arbitrary keyword arguments to include additional client-specific
            configuration settings. If `password` is included, it is used;
            otherwise, a random password is generated.

    Returns:
        Path: The path to the generated MariaDB CNF file.
    """
    config = default_config()
    cnf_attrs = {
        "client": {
            "user": user,
            "host": host
        },
    }
    for attr in kwargs:
        cnf_attrs["client"][attr] = kwargs[attr]
    # Create a new Random Password if not provided
    if kwargs.get("password"):
        cnf_attrs["client"]["password"] = kwargs.get("password")
    else:  # Generate a random password
        cnf_attrs["client"]["password"] = generate_random_password()

    # BUILD MariaDB.cnf HEADER
    hdr = "\n".join(
        (
            "# This group is read by the client only.",
            "# Use it for options that only affect the client, see",
            "# https://mariadb.com/kb/en/configuring-mariadb-with-option-files/#option-groups",
        )
    )

    config.mariadb_cnf.write_text("\n".join((hdr, build_cnf(cnf_attrs))))
    return config.mariadb_cnf


def generate_random_password(length=default_config().password_length) -> str:
    """
    Generates a random password of the specified length, consisting of letters, digits,
    and MariaDB-recommended safe special characters. This method uses cryptographically
    secure random number generation to ensure unpredictability of the password.

    Args:
        length (int): The desired length of the generated password.

    Returns:
        str: A randomly generated password containing letters, digits, and safe special characters.
    """
    # Define character sets
    letters_digits = string.ascii_letters + string.digits
    # Include only MariaDB.com recommended safe special characters, excluding quotes and backslash
    safe_punctuation = '+-*/,.,:;!?$%&@=^_~|<>()[]{}'
    alphabet = letters_digits + safe_punctuation

    # Generate the password using secrets module
    password = ''.join(secrets.choice(alphabet) for _ in range(length))

    return password
