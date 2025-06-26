import configparser
from configparser import (ConfigParser)
from datetime import datetime
from logging import (DEBUG, basicConfig, getLogger)
from pathlib import PosixPath as Path
from sys import exit
from typing import (Dict, Final, Optional)

from mariadb import (Error, connect)

DEFAULT_DIR: Final[Path] = Path.home() / '.moduli_assembly'
DEFAULT_MARIADB_CNF: Final[Path] = DEFAULT_DIR / 'moduli_generator.cnf'

# Def compress_datestr(datestring: str):
#     """
#     Compress a given date string, as produced from mariadb, by removing all non-numeric characters.
#
#     This function processes a string expected to represent a date by stripping
#     out any characters that are not numeric. The resulting string contains only
#     digits, which may be useful for specific date manipulations or validations.
#
#     :param datestring: The input date string potentially containing non-numeric
#         characters that should be removed.
#     :type datestring: Str
#     :return: A compressed string containing only numeric characters from the
#         original date string.
#     :rtype: Str
#     """
#     # Remove all non-numeric characters using regex
#     return sub(r'[^0-9]', '', datestring)


def parse_mysql_config(config_path: Path = DEFAULT_MARIADB_CNF) -> Dict[str, Dict[str, str]]:
    """
    Parse a MySQL configuration file and return a dictionary of sections and their key-value pairs.

    Args:
        config_path (str): Path to the MySQL configuration file

    Returns:
        Dict[str, Dict[str, str]]: Dictionary with sections as keys and
                                  dictionaries of key-value pairs as values

    Raises:
        FileNotFoundError: If the configuration file doesn't exist,
        ValueError: If there's an issue parsing the file
    """
    if not (config_path.is_file() and config_path.exists()):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    cnf = ConfigParser(allow_no_value=True)
    try:
        cnf.read(config_path)
        result = {local_section: dict(cnf[local_section]) for local_section in cnf.sections()}
        return result
    except configparser.Error as error:
        raise ValueError(f"Error parsing configuration filerr: {error}")


def get_mysql_config_value(cnf: Dict[str, Dict[str, str]],
                           local_section: str,
                           local_key: str):
    """
    Get a specific value from a parsed MySQL configuration.

    Args:
        cnf (Dict[str, Dict[str, str]]): Parsed configuration dictionary
        local_section (str): Section name
        local_key (str): Key name

    Returns:
        Optional[str]: Value from the configuration or default
    """
    if local_section in cnf and local_key in cnf[local_section]:
        return cnf[local_section][local_key]
    else:
        return None


class MariaDBConnector:

    def __init__(self,
                 mycnf: Path = DEFAULT_MARIADB_CNF,
                 default_dir: Path = DEFAULT_DIR
                 ):
        """
        Initializes the MariaDB connector by setting up a connection to the database using the
        configuration parameters specified in a MySQL configuration file. Configures logging to
        write to a file located within an output directory.

        :param mycnf: Path to the MySQL configuration file, which should contain the necessary
                      connection details under the "client" group.
        :type mycnf: Str
        :param default_dir: Output directory path where the log file, 'mariadb_connector.log',
                           will be created and used for logging.
        :type default_dir: Path

        :raises Error: Raised when a connection to the MariaDB Platform fails due to invalid
                       or missing configuration parameters.
        """

        # Configure logging
        basicConfig(
            level=DEBUG,
            format='%(asctime)s - %(levelname)s: %(message)s',
            filename=default_dir / 'mariadb_connector.log',
            filemode='a'
        )
        self.logger = getLogger(__name__)

        conf = parse_mysql_config(mycnf)["client"]
        try:
            self.connection = connect(
                host=conf["host"],
                port=int(conf["port"]),
                user=conf["user"],
                password=conf["password"],
                database=conf["database"]
            )
        except Error as mdbconn_error:
            self.logger.error(f"Error connecting to MariaDB Platform: {mdbconn_error}")
            exit(1)

    def sql(self, query):
        """
        Executes a given SQL query using the database connection, logs the results,
        and ensures the cursor is properly closed after execution. This function
        is used to run SQL commands and log each resulting row using the logger
        associated with this object.

        :param query: The SQL query to be executed on the database.
        :type query: Str
        :return: None
        :rtyperr: None
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            for row in cursor:
                self.logger.info(row)
            cursor.close()
        except Error as mdbconn_error:
            self.logger.error(f"Error executing SQL query: {mdbconn_error}")
            exit(1)

    def add(self, timestamp, candidate_type, tests, trials, key_size,
            generator, modulus, file_origin):
        """
        Insert a candidate into the screened_moduli table

        Args:
            timestamp (datetime): Timestamp when the candidate was generated
            candidate_type (str): Generator type ('2' or '5')
            tests (str): Tests performed
            trials (int): Number of trials
            key_size (int): Key size in bits
            generator (int): Generator value
            modulus (str): Prime modulus
            file_origin (str): Source file of the modulus

        Returns:
            int: The ID of the inserted record or None if insertion failed
        """
        try:
            cursor = self.connection.cursor()
            query = """
                    INSERT INTO screened_moduli
                    (timestamp, candidate_type, tests, trials, key_size, generator, modulus, file_origin)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?) \
                    """
            cursor.execute(query, (
                timestamp,
                candidate_type,
                tests,
                trials,
                key_size,
                generator,
                modulus,
                file_origin
            ))
            self.connection.commit()
            last_id = cursor.lastrowid
            cursor.close()
            return last_id

        except Error as err:
            self.logger.error(f"Error inserting candidate: {err}")

    def delete_records(self, table_name, where_clause=None):
        """
        Delete entries from a table in the database.

        Args:
            table_name (str): The name of the table to delete from
            where_clause (str, optional): SQL WHERE clause to filter records for deletion.
                                         If None, all records will be deleted.

        Returns:
            int: Number of rows deleted, or -1 if an error occurred
        """

        try:
            cursor = self.connection.cursor()

            if where_clause:
                query = f"DELETE FROM {table_name} WHERE {where_clause}"
            else:
                query = f"DELETE FROM {table_name}"

            cursor.execute(query)
            rows_affected = cursor.rowcount
            self.connection.commit()
            cursor.close()

            print(f"Successfully deleted {rows_affected} rows from table: {table_name}")
            return rows_affected

        except Error as e:
            print(f"Error deleting from table {table_name}: {e}")
            return -1


def store_screened_moduli(db_conn: MariaDBConnector, json_schema: dict):
    """
    Save from JSON moduli schema file (JSON of screened moduli)

    Args:
        db_conn: MariaDB connector instance
        json_schema: Dictionary with moduli data
    """
    for key, moduli_list in json_schema.items():
        for modulus in moduli_list:
            try:
                db_conn.add(modulus["timestamp"], modulus["type"], modulus["tests"],
                            modulus["trials"], modulus["size"], modulus["generator"],
                            modulus["modulus"], "screened_moduli")

                db_conn.logger.info(f'Stored {modulus["timestamp"]} candidate in database')

            except Error as err:

                db_conn.logger.error(f"Error storing modulus{modulus['timestamp']}: {err}")
