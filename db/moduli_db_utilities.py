import configparser
from configparser import (ConfigParser)
from pathlib import PosixPath as Path
from typing import (Dict, Optional)

from mariadb import (Error, connect)

from moduli_generator.config import (ISO_UTC_TIMESTAMP, ModuliConfig, compress_datetime_to_string, default_config,
                                     is_valid_identifier)


# DEFAULT_CONFIG_ID,; DEFAULT_KEY_LENGTHS,; DEFAULT_MARIADB_DB,;
# DEFAULT_MARIADB_TABLE,; DEFAULT_MARIADB_VIEW,; DEFAULT_RECORDS_PER_KEYLENGTH,


def parse_mysql_config(mysql_cnf: str) -> Dict[str, Dict[str, str]]:
    if not (Path(mysql_cnf).is_file() and Path(mysql_cnf).exists()):
        raise FileNotFoundError(f"Configuration file not found: {Path(mysql_cnf).resolve()}")

    cnf = ConfigParser(allow_no_value=True)
    try:
        cnf.read(mysql_cnf)
        result = {local_section: dict(cnf[local_section]) for local_section in cnf.sections()}

        return result
    except configparser.Error as err:
        raise ValueError(f"Error parsing configuration filerr: {err}")


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


# db/moduli_db_utilities.py
class MariaDBConnector:
    """
    Provides functionalities to connect to a MariaDB database using credentials
    and configurations specified in a configuration file.

    This class is used to establish a connection to a MariaDB database instance
    by parsing database credentials from a provided configuration file and using
    those parameters to initialize the database connection.

    :ivar logger: Logger instance for logging messages related to the database
        connection process.
    :type logger: Logging.Logger
    :ivar connection: Connection object used to interact with the MariaDB database.
    :type connection: Mariadb.Connection
    """

    def __init__(self, config: ModuliConfig = default_config):

        # SQL Properties for Moduli DB
        self.config_id = config.config_id
        self.db_name = config.db_name
        self.table_name = config.table_name
        self.view_name = config.view_name

        self.key_lengths = config.key_lengths
        self.records_per_keylength = config.records_per_keylength

        # COnfigure Logger for Module
        self.logger = config.get_logger()
        self.logger.name = __name__

        self.logger.debug(f"Using MariaDB config: {config.mariadb_cnf}")

        mysql_cnf = parse_mysql_config(config.mariadb_cnf)["client"]

        try:
            self.connection = connect(
                host=mysql_cnf["host"],
                port=int(mysql_cnf["port"]),
                user=mysql_cnf["user"],
                password=mysql_cnf["password"],
                database=mysql_cnf["database"]
            )
        except configparser.Error as err:
            self.logger.error(f"Error connecting to MariaDB Platform: {err}")
            raise RuntimeError(f"Database connection failed: {err}")

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
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(query)
                for row in cursor:
                    self.logger.info(row)
                cursor.close()
            except Error as err:
                self.logger.error(f"Error executing SQL query: {err}")
                raise RuntimeError(f"Database query failed: {err}")

    def add(self, timestamp: int, key_size: int, modulus: str) -> int:
        """
        Adds a new record to the specified database table with the details provided.

        This method inserts a record into the database table defined by `self.db_name`
        and `self.table_name` using the provided input values. If the operation is
        successful, the method commits the transaction and returns the identifier of
        the newly inserted row.

        :param timestamp: The time at which the record should be inserted.
        :type timestamp: Int
        :param key_size: The size of the key in bits.
        :type key_size: Int
        :param modulus: The modulus value to be stored in the record.
        :type modulus: Int
        :return: The identifier of the newly inserted row in the database.
        :rtype: Int
        """
        # Validate identifiers
        if not (is_valid_identifier(self.db_name) and is_valid_identifier(self.table_name)):
            self.logger.error("Invalid database or table name")
            return 0

        try:
            with self.connection.cursor() as cursor:
                query = f"""
                        INSERT INTO {self.db_name}.{self.table_name} (timestamp, config_id, size, modulus)
                        VALUES (?, ?, ?, ?) \
                        """
                cursor.execute(query, (
                    timestamp,
                    self.config_id,
                    key_size,
                    modulus,
                ))
                self.connection.commit()
                last_id = cursor.lastrowid
                cursor.close()

                # Log success only after successful insertion
                self.logger.info(f'Successfully added {key_size} bit modulus to {self.db_name}.{self.table_name}')
                self.logger.debug(f'Last inserted row ID: {last_id}')

                return last_id

        except Error as err:
            self.logger.error(f"Error inserting candidate: {err}")
            return 0

    def delete_records(self, table_name, where_clause=None):
        """
        Deletes records from a specified table in the database. It supports conditional deletion
        using a WHERE clause. The method executes a DELETE SQL statement and commits the changes.
        If the operation is successful, the number of rows affected is returned. If there is an
        error during the operation, it raises a RuntimeError.

        :param table_name: The name of the database table from which records should be deleted.
        :type table_name: str
        :param where_clause: An optional SQL condition to filter which records should be deleted.
                             If not provided, all records in the table will be deleted.
        :type where_clause: Optional[str]
        :return: The number of rows affected by the DELETE operation.
        :rtype: int
        """

        try:
            with self.connection.cursor() as cursor:
                if where_clause:
                    query = f"""
                            DELETE FROM {table_name} WHERE {where_clause}
                            """
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
            raise RuntimeError(f"Error deleting from table {table_name}: {e}")

    def store_screened_moduli(self, json_schema: dict):
        """
        Save moduli from JSON schema to the database
        
        Args:
            json_schema: Dictionary with moduli data
            
        Returns:
            int: 0 for success, 1 for failure
        """
        for key, moduli_list in json_schema.items():
            for modulus in moduli_list:
                try:
                    self.add(modulus["timestamp"], modulus["key-size"], modulus["modulus"])
                except Error as err:
                    self.logger.error(f"Error storing modulus{modulus['timestamp']}: {err}")
                    return 1
        return 0

    def get_moduli(
            self,
            output_file: Path = None
    ):
        """
        Retrieves random moduli records from a database and optionally writes them to an output file. Ensures that
        sufficient records are available for each specified key size before proceeding. Logs the results and
        handles database interaction, including error management.

        :param output_file: Path to the output file where moduli records will be written. If None,
                            the results will not be written to a file.
        :type output_file: Path, optional
        :return: A dictionary containing the retrieved moduli records categorized by key size. The dictionary
                 keys represent the key sizes, and the values are lists of records for the corresponding key
                 size. Returns None if insufficient records are available for any key size.
        :rtype: dict or None
        """
        moduli_query_sizes = []
        for item in self.key_lengths:
            moduli_query_sizes.append(item - 1)

        # First, check if we have enough records for each key size
        insufficient_sizes = []

        try:
            with self.connection.cursor() as cursor:
                for size in moduli_query_sizes:
                    # Count query to check available records
                    count_query = f"""
                              SELECT COUNT(*)
                              FROM {self.db_name}.{self.view_name}
                              WHERE size = {size} \
                              """
                # count_query = f'SELECT COUNT(*) FROM {db}.{table} WHERE size = ? '
                cursor.execute(count_query)
                count = cursor.fetchone()[0]

                if count < self.records_per_keylength:
                    insufficient_sizes.append((size, count))
                    self.logger.warning(
                        f'Insufficient records for complete /etc/ssh/moduli:' +
                        f' key size {size}: {count} available, {self.records_per_keylength} required')

        except Error as err:
            self.logger.error(f"Error retrieving random moduli: {err}")
            raise RuntimeError(f"Database query failed: {err}")

        # If any size has insufficient records, log and return None
        if insufficient_sizes:
            self.logger.error(f"Cannot create moduli file. Insufficient records for key sizes: {insufficient_sizes}")
            return None

        # If we have enough records for all sizes, proceed with retrieval
        results = {}

        try:
            with self.connection.cursor(dictionary=True) as cursor:
                for size in moduli_query_sizes:
                    # Query to get random records for the current key size using the view
                    query = f"""
                        SELECT timestamp, type, tests, trials, size, generator, modulus
                        FROM {self.db_name}.{self.view_name}
                        WHERE size = {size}
                        LIMIT {self.records_per_keylength} \
                        """

                    cursor.execute(query, )

                    # Store the results for this key size
                    records = list(cursor.fetchall())
                    results[size] = records

                    # Log the number of records found
                    self.logger.info(f"Retrieved {len(records)} random records for key size {size}")

        except Error as err:
            self.logger.error(f"Error retrieving random moduli: {err}")
            raise RuntimeError(f"Database query failed: {err}")

        # If an output file is specified, and we have enough records for all sizes, write the results
        if output_file:
            self._write_moduli_to_file(results, output_file)
            self.logger.info(f"Successfully created moduli file with {self.records_per_keylength} records per key size")

        return results

    def _write_moduli_to_file(self, moduli_data: dict, output_file: Path):
        try:
            with output_file.open('w') as of:
                # Write File Header
                of.write(
                    f'# /etc/ssh/modul: dcrunch.threatwonk.net: {ISO_UTC_TIMESTAMP()}\n'
                )

                # Write data for each key size
                for size, records in moduli_data.items():
                    for record in records:
                        # Format: timestamp type tests trials size generator modulus
                        # The timestamp should already be in compressed format
                        of.write(' '.join((
                            compress_datetime_to_string(record['timestamp']),
                            record['type'],
                            record['tests'],
                            str(record['trials']),
                            str(record['size']),
                            str(record['generator']),
                            record['modulus'],
                            '\n'
                        )))

            self.logger.info(f"Successfully wrote moduli to file: {output_file}")

        except IOError as err:
            self.logger.error(f"Error writing to file {output_file}: {err}")
            raise
