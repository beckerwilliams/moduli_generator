import configparser
from configparser import (ConfigParser, NoOptionError, NoSectionError)
from datetime import datetime
from json import loads
from logging import (DEBUG, basicConfig, getLogger)
from pathlib import PosixPath as Path
from sys import exit
from typing import (Dict, Optional)

from mariadb import (Error, connect)


def parse_mysql_config(config_path: str) -> Dict[str, Dict[str, str]]:
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
    cpath = Path(config_path)
    if not (cpath.is_file() and cpath.exists()):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    cnf = ConfigParser(allow_no_value=True)
    try:
        cnf.read(config_path)
        result = {local_section: dict(cnf[local_section]) for local_section in cnf.sections()}
        return result
    except configparser.Error as error:
        raise ValueError(f"Error parsing configuration file: {error}")


def get_mysql_config_value(cnf: Dict[str, Dict[str, str]],
                           local_section: str,
                           local_key: str,
                           default: Optional[str] = None) -> Optional[str]:
    """
    Get a specific value from a parsed MySQL configuration.

    Args:
        cnf (Dict[str, Dict[str, str]]): Parsed configuration dictionary
        local_section (str): Section name
        local_key (str): Key name
        default (Optional[str]): Default value if section or key doesn't exist

    Returns:
        Optional[str]: Value from the configuration or default
    """
    if local_section in cnf and local_key in cnf[local_section]:
        return cnf[local_section][local_key]
    else:
        return None


class MariaDBConnector:
    """

    """

    def __init__(self,
                 mycnf: str = Path.home() / ".my.cnf",
                 output_dir: Path = Path.home() / ".moduli_assembly"
                 ):
        """
        Initializes the MariaDB connector by setting up a connection to the database using the
        configuration parameters specified in a MySQL configuration file. Configures logging to
        write to a file located within an output directory.

        :param mycnf: Path to the MySQL configuration file, which should contain the necessary
                      connection details under the "client" group.
        :type mycnf: str
        :param output_dir: Output directory path where the log file, 'mariadb_connector.log',
                           will be created and used for logging.
        :type output_dir: Path

        :raises Error: Raised when a connection to the MariaDB Platform fails due to invalid
                       or missing configuration parameters.
        """
        # Configure logging
        basicConfig(
            level=DEBUG,
            format='%(asctime)s - %(levelname)s: %(message)s',
            filename=output_dir / 'mariadb_connector.log'
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
        except Error as e:
            self.logger.error(f"Error connecting to MariaDB Platform: {e}")
            exit(1)

        # assure logger output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "mariadb-connector.log").touch(exist_ok=True)

    def sql(self, query):
        """
        Executes a given SQL query using the database connection, logs the results,
        and ensures the cursor is properly closed after execution. This function
        is used to run SQL commands and log each resulting row using the logger
        associated with this object.

        :param query: The SQL query to be executed on the database.
        :type query: str
        :return: None
        :rtype: None
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        for row in cursor:
            self.logger.info(row)
        cursor.close()

    def add(self, timestamp, candidate_type, tests, trials, key_size,
            generator, modulus, file_origin):
        """
        Insert a candidate into the screened_candidates table

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
                    INSERT INTO screened_candidates
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
        except Error as e:
            self.logger.error(f"Error inserting candidate: {e}")
            return None


def store_screened_moduli(db: MariaDBConnector, json_schema: dict):
    """
    Save from JSON moduli schema file (JSON of screened moduli)

    Args:
        db: MariaDB connector instance
        json_schema: Dictionary with moduli data
    """
    for key, moduli_list in json_schema.items():
        for modulus in moduli_list:
            db.add(modulus["timestamp"], modulus["type"], modulus["tests"],
                   modulus["trials"], modulus["size"], modulus["generator"],
                   modulus["modulus"], "screened_candidates")
            db.logger.info(f'Stored {modulus["timestamp"]} candidate in database')


if __name__ == "__main__":

    db = MariaDBConnector("/Users/ron/development/moduli_generator/moduli_generator.cnf")

    try:
        db.sql("SHOW DATABASES")
    except Error as e:
        db.logger.error(f"Error executing SQL query: {e}")

    try:
        db.sql("USE mod_gen")
    except Error as e:
        db.logger.error(f"Error selecting database: {e}")

    try:
        db.sql("SHOW TABLES")
    except Error as e:
        db.logger.error(f"Error executing SQL query: {e}")

    test_timestamp = datetime.now()
    test_id = db.add(timestamp=test_timestamp,
                     candidate_type="2",
                     tests="primality,miller-rabin",
                     trials=10,
                     key_size=2048,
                     generator=2,
                     modulus="ABCDEF123456789...",  # This would be a long prime number
                     file_origin="/path/to/source/file.txt")

    # Let's Store the Current File
    moduli_file = Path("/Users/ron/development/moduli_generator/.moduli_assembly/moduli_schema.json").read_text()
    moduli_json = loads(moduli_file)
    store_screened_moduli(db, moduli_json)
