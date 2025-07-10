import configparser
from configparser import (ConfigParser)
from contextlib import contextmanager
from pathlib import PosixPath as Path
from typing import (
    Dict,
    List,
    Optional
)

from mariadb import (
    Error,
    connect
)

from moduli_generator.config import (ISO_UTC_TIMESTAMP, ModuliConfig, default_config, is_valid_identifier,
                                     strip_punction_from_datetime_str)


def parse_mysql_config(mysql_cnf: str) -> Dict[str, Dict[str, str]]:
    """
    Parses a MySQL configuration file and returns its content as a dictionary.

    This function processes a MySQL configuration file, validates its existence,
    and extracts its content into a nested dictionary structure. The outer dictionary
    keys correspond to section names, and the inner dictionaries map option names
    to their respective values in each section.

    :param mysql_cnf: Path to the MySQL configuration file.
    :type mysql_cnf: str 
    :raises FileNotFoundError: If the specified configuration file does not exist.
    :raises ValueError: If the configuration file has parsing errors.
    :return: Dictionary containing the parsed configuration sections and options.
    :rtype: Dict[str, Dict[str, str]]
    """
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
                           local_key: str) -> str:
    """
    Retrieves a value from a nested dictionary based on the provided section
    and key. The function is primarily used to fetch configurations from a
    MySQL configuration dictionary. If the specified section and key exist
    in the dictionary, their corresponding value is returned. If either the
    section or key is absent, the function returns None.

    :param cnf: A dictionary representing a MySQL configuration where keys
        are section names and values are dictionaries containing key-value
        pairs within those sections.
    :type cnf: Dict[str, Dict[str, str]]
    :param local_section: The section name in the configuration dictionary
        from which the key-value pair should be retrieved.
    :type local_section: str 
    :param local_key: The key within the specified section of the
        configuration dictionary whose associated value needs to be fetched.
    :type local_key: str 
    :return: The value associated with the given section and key if it
        exists, otherwise None.
    :rtype: str  | None
    """
    if local_section in cnf and local_key in cnf[local_section]:
        return cnf[local_section][local_key]
    else:
        return None


class MariaDBConnector:
    """
    Handles connections and operations with a MariaDB database, providing functionality
    for executing SQL queries, managing records, and retrieving data. The class is built
    to interface with a structured schema defined by configuration and support additional
    operations such as moduli retrieval and storage.

    This class automatically establishes a connection to the database upon instantiation,
    using connection details provided in a configuration object. Operations such as SQL
    execution, record addition, deletion, and retrieval are executed using the connection
    while ensuring proper resource management and error handling.

    :ivar config_id: Identifier for the configuration associated with the database.
    :ivar db_name: Name of the database to connect to.
    :ivar table_name: Name of the table in the database used for records.
    :ivar view_name: Name of the view in the database for specialized queries.
    :ivar key_lengths: List of key sizes used for data grouping or retrieval.
    :ivar records_per_keylength: Number of records required per key size.
    :ivar logger: Logger instance for debugging and tracking the class operations.
    :ivar connection: Active connection to the MariaDB database.
    """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            try:
                self.connection.close()
                self.logger.debug("Database connection closed")
            except Error as err:
                self.logger.error(f"Error closing database connection: {err}")
        return False

    @contextmanager
    def transaction(self):
        """
        Context manager for managing database transactions.

        This context manager handles committing or rolling back a transaction
        within a database connection. Upon successful execution of the block, the
        transaction is committed. In the event of an exception, the transaction is
        rolled back, and the error is logged.

        :raises Exception: If an error occurs, it is logged and re-raised.
        """
        try:
            yield
            self.connection.commit()
            self.logger.debug("Transaction committed")
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Transaction rolled back due to error: {e}")
            raise

    @contextmanager
    def file_writer(self, output_file: Path):
        """
        Context manager for safely opening a file for writing.

        When used, this context manager ensures that the specified file is opened for
        writing and properly closed after use, even in the event of an error.

        :param output_file: The path of the file to be written.
        :type output_file: Path
        :return: A file handle for writing.
        :rtype: TextIO
        """
        try:
            with output_file.open('w') as file_handle:
                yield file_handle
        except IOError as err:
            self.logger.error(f"Error writing to file {output_file}: {err}")
            raise

    def __init__(self, config: ModuliConfig = default_config):
        """
        Initializes the database connection and configures the module based on the provided configuration.

        :class ModuliConfig:
            Represents the configuration necessary for initializing the module.

        :param config: The configuration object containing all necessary database and runtime settings.
        :type config: ModuliConfig

        :raises RuntimeError: If a connection to the MariaDB platform fails due to configuration or
                              connection errors.
        """
        for key, value in config.__dict__.items():
            if key in ["mariadb_cnf",
                       "db_name",
                       "table_name",
                       "view_name",
                       "config_id",
                       "key_lengths",
                       "records_per_keylength",
                       "delete_records_on_moduli_write",
                       "delete_records_on_read"
                       'get_logger()'
                       ]:
                setattr(self, key, value)

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

    def sql(self, query: str, params: Optional[tuple] = None, fetch: bool = True) -> Optional[List[Dict]]:
        """
        Executes a given SQL query within a transaction, optionally fetching query results
        or returning the number of affected rows for non-SELECT queries.

        This method handles execution of SQL queries, managing the transaction and logging
        details of the operation. SELECT type queries fetch and return results, while
        INSERT/UPDATE/DELETE type queries commit changes and optionally return affected
        rows information.

        :param query: SQL query to be executed.
        :type query: str
        :param params: Optional tuple of parameters to be bound to the query.
        :type params: Optional[tuple]
        :param fetch: Indicates whether to fetch results (True for SELECT queries).
        :type fetch: bool
        :return: A list of queried rows represented as dictionaries in case of SELECT
                 queries, otherwise None.
        :rtype: Optional[List[Dict]]
        """
        try:
            with self.transaction():
                with self.connection.cursor(dictionary=True) as cursor:
                    # Execute query with optional parameters
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)

                    if fetch:
                        # For SELECT queries, fetch all results
                        results = cursor.fetchall()
                        self.logger.debug(f"Query returned {len(results)} rows")
                        return results
                    else:
                        # For INSERT/UPDATE/DELETE queries, commit and return affected rows info
                        affected_rows = cursor.rowcount
                        self.logger.debug(f"Query affected {affected_rows} rows")
                        return None

        except Error as err:
            self.logger.error(f"Error executing SQL query: {err}")
            self.logger.error(f"Query: {query}")
            if params:
                self.logger.error(f"Parameters: {params}")
            raise RuntimeError(f"Database query failed: {err}")

    def execute_select(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        """
        Executes a SELECT SQL query and returns the results.

        This method takes an SQL query and optional parameters, executes the query,
        and fetches the results from the database. The results are returned as a
        list of dictionaries, where each dictionary corresponds to a row retrieved
        from the database.

        :param query: The SQL query to be executed.
        :type query: str
        :param params: A tuple of optional parameters to use during query execution,
            defaults to None.
        :type params: Optional[tuple]
        :return: A list of dictionaries representing the rows of the result set.
        :rtype: List[Dict]
        """
        return self.sql(query, params, fetch=True)

    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """
        Executes an update query on the database and returns the number of rows affected.

        This method utilizes the database connection to execute an update query. Within
        a transaction block, it uses the provided SQL query and optional parameters to
        execute the query. If the query execution is successful, the number of rows
        affected by the operation is returned. In the event of an error, it logs the
        error message and raises a runtime exception.

        :param query: The SQL query to execute on the database.
        :type query: str
        :param params: Optional tuple of parameters to bind to the query. Defaults to None.
        :type params: Optional[tuple]
        :return: The number of rows affected by the executed query.
        :rtype: int
        """
        try:
            with self.transaction():
                with self.connection.cursor() as cursor:
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    affected_rows = cursor.rowcount
                    self.logger.debug(f"Query affected {affected_rows} rows")
                    return affected_rows

        except Error as err:
            self.logger.error(f"Error executing update query: {err}")
            raise RuntimeError(f"Database update failed: {err}")

    def execute_batch(self, queries: List[str], params_list: Optional[List[tuple]] = None) -> bool:
        """
        Executes a batch of SQL queries within a single transaction. This method ensures
        that all queries are executed successfully together or none at all, maintaining
        data consistency. It logs the success or failure of the operation for debugging purposes.

        :param queries: A list of SQL query strings to be executed in the batch.
        :param params_list: A list of tuples representing the parameters for
            each query. If no parameters are needed for a specific query, it may be
            omitted or set as `None`. Default is `None`.
        :return: Returns `True` if all queries are successfully executed within the batch.
        :rtype: bool
        :raises RuntimeError: If there is an error during the execution of queries
            or committing the transaction.
        """
        try:
            with self.transaction():
                with self.connection.cursor() as cursor:
                    for i, query in enumerate(queries):
                        params = params_list[i] if params_list and i < len(params_list) else None
                        if params:
                            cursor.execute(query, params)
                        else:
                            cursor.execute(query)
                    self.logger.debug(f"Successfully executed {len(queries)} in batch")
                    return True

        except Error as err:
            self.logger.error(f"Error executing batch queries: {err}")
            raise RuntimeError(f"Batch query execution failed: {err}")

    def add(self, timestamp: int, key_size: int, modulus: str) -> int:
        """
        Inserts a record into a specified database table. The record includes details such
        as a timestamp, key size, and modulus value. The method validates the database name
        and table name before attempting to insert data. If the validation fails or there
        is an error during the insertion, the operation will fail gracefully.

        :param timestamp: Timestamp representing the time associated with the record.
        :type timestamp: int
        :param key_size: Size of the key (in bits) to be added.
        :type key_size: int
        :param modulus: The modulus value to be added.
        :type modulus: str
        :return: The identifier of the last inserted row if successful, otherwise 0.
        :rtype: int
        """
        # Validate identifiers
        if not (is_valid_identifier(self.db_name) and is_valid_identifier(self.table_name)):
            self.logger.error("Invalid database or table name")
            return 0

        try:
            with self.transaction():
                with self.connection.cursor() as cursor:
                    query = f"""INSERT INTO {self.db_name}.{self.table_name} 
                               (timestamp, config_id, size, modulus) VALUES (?, ?, ?, ?)"""
                    cursor.execute(query, (timestamp, self.config_id, key_size, modulus))
                    last_id = cursor.lastrowid
                    self.logger.info(f'Successfully added {key_size} bit modulus')
                    return last_id
        except Error as err:
            self.logger.error(f"Error inserting candidate: {err}")
            return 0

    def add_batch(self, records: List[tuple]) -> bool:
        """
        Add a batch of records to the specified table within the database.

        This method validates the database and table names, prepares the SQL query
        for batch insertion, and attempts to execute the batch operation. If the
        execution is successful, a log message is generated indicating the number
        of records successfully added. If an error occurs during the operation,
        the error is logged, and the function returns False.

        :param records: A list of tuples, where each tuple represents a record to
            be inserted. Each record should contain the timestamp, key size, and
            modulus values.
        :type records: List[tuple]
        :return: A boolean indicating whether the batch operation was successful.
            Returns True if successful, False otherwise.
        :rtype: bool
        """
        if not (is_valid_identifier(self.db_name) and is_valid_identifier(self.table_name)):
            self.logger.error("Invalid database or table name")
            return False

        query = f"""
                INSERT INTO {self.db_name}.{self.table_name} (timestamp, config_id, size, modulus)
                VALUES (?, ?, ?, ?)
                """

        # Prepare parameters for batch execution
        params_list = [(timestamp, self.config_id, key_size, modulus)
                       for timestamp, key_size, modulus in records]

        try:
            success = self.execute_batch([query] * len(records), params_list)
            if success:
                self.logger.info(f'Successfully added {len(records)} records to {self.db_name}.{self.table_name}')
            return success
        except RuntimeError as err:
            self.logger.error(f"Error inserting batch records: {err}")
            return False

    def delete_records(self, table_name, where_clause=None) -> int:
        """
        Deletes records from the specified table in the database, with an optional
        WHERE clause to filter the records to be deleted. If no WHERE clause is provided,
        all records in the table will be deleted. The method returns the number of rows
        affected by the DELETE operation.

        :param table_name: The name of the table from which records are to be deleted.
        :type table_name: str
        :param where_clause: An optional SQL WHERE clause to specify the conditions
            for the DELETE operation. Defaults to None.
        :type where_clause: str, optional
        :return: The number of rows deleted from the table.
        :rtype: int
        """
        try:
            with self.transaction():
                with self.connection.cursor() as cursor:
                    if where_clause:
                        query = f"DELETE FROM {table_name} WHERE {where_clause}"
                    else:
                        query = f"DELETE FROM {table_name}"

                    cursor.execute(query)
                    rows_affected = cursor.rowcount

                    self.logger.debug(f"Moduli Consumed from DB: {rows_affected}")
                    print(f"Successfully deleted {rows_affected} rows from table: {table_name}")
                    return rows_affected

        except Error as e:
            print(f"Error deleting from table {table_name}: {e}")
            raise RuntimeError(f"Error deleting from table {table_name}: {e}")

    def store_screened_moduli(self, json_schema: dict) -> int:
        """
        Stores screened moduli data from a given JSON schema into the storage.

        This method iterates over the provided JSON schema dictionary, extracting
        moduli attributes and saving them using an internal method. The operation
        is performed within a database transaction to ensure atomicity. Errors
        encountered during the process are logged, and an appropriate status is
        returned.

        :param json_schema: A dictionary containing moduli data mapped to corresponding keys.
        :type json_schema: dict
        :return: An integer indicating the status of the operation,
                 where 0 indicates success and 1 indicates failure.
        :rtype: int
        """
        try:
            with self.transaction():
                for key, moduli_list in json_schema.items():
                    for modulus in moduli_list:
                        # Use the internal add method without its own transaction
                        self._add_without_transaction(modulus["timestamp"], modulus["key-size"], modulus["modulus"])
            return 0
        except Error as err:
            self.logger.error(f"Error storing moduli: {err}")
            return 1

    def _add_without_transaction(self, timestamp: int, key_size: int, modulus: str) -> int:
        """
        Inserts a new record into the database table without wrapping the operation
        in a transaction. This method directly interacts with the database cursor
        to execute an INSERT statement for storing the provided data.

        :param timestamp: The timestamp for the record being inserted.
        :type timestamp: int
        :param key_size: The size of the cryptographic key in bits.
        :type key_size: int
        :param modulus: The cryptographic modulus as a string.
        :type modulus: str
        :return: The last inserted ID of the record.
        :rtype: int
        :raises Error: If there is an issue during the database operation.
        """
        # Validate identifiers
        if not (is_valid_identifier(self.db_name) and is_valid_identifier(self.table_name)):
            self.logger.error("Invalid database or table name")
            return 0

        try:
            with self.connection.cursor() as cursor:
                query = f"""INSERT INTO {self.db_name}.{self.table_name} 
                           (timestamp, config_id, size, modulus) VALUES (?, ?, ?, ?)"""
                cursor.execute(query, (timestamp, self.config_id, key_size, modulus))
                last_id = cursor.lastrowid
                self.logger.info(f'Successfully added {key_size} bit modulus')
                return last_id
        except Error as err:
            self.logger.error(f"Error inserting candidate: {err}")
            raise  # Re-raise to let transaction context manager handle rollback


def get_moduli(
        self,
        output_file: Path = None
) -> Dict[int, list]:
    """
    Retrieves cryptographic moduli records from the database for specified key lengths.
    Ensures there are sufficient moduli records available for each key size prior to
    retrieval. If a specific output file is provided, the obtained records are also
    written to that file.

    :param self: Instance of the class invoking this method.
    :type self: Any
    :param output_file: Path to a file where the retrieved moduli will be written,
        if specified.
    :type output_file: Path, optional
    :return: Dictionary where key is the key size (int) and value is a list of records.
    :rtype: Dict[int, list]
    """
    # Verify that a sufficient number of moduli for each keysize exist in the db
    stats = self.stats()
    for stat in stats:
        if stats[stat] < self.records_per_keylength:
            self.logger.info(
                f"Insufficient records for key size {stat[0]}: {stat[1]} available,"
                f" {self.records_per_keylength} required"
            )
            raise RuntimeError(
                f"Insufficient records for key size {stat[0]}: {stat[1]} available, "
                f"{self.records_per_keylength} required"
            )

    # If we have enough records for all sizes, proceed with retrieval
    moduli = {}

    try:
        with self.connection.cursor(dictionary=True) as cursor:
            for size in self.key_lengths:
                # Query to get records for the current key size using the view
                query = f"""
                        SELECT timestamp, type, tests, trials, size, generator, modulus
                        FROM {self.db_name}.{self.view_name}
                        WHERE size = {size - 1}  # GOTCHA - The STORED Moduli Size is 1 BIT LESS THAN THE KEY SIZE 
                        LIMIT {self.records_per_keylength} \
                        """

                cursor.execute(query, )

                # Store the results for this key size
                records = list(cursor.fetchall())
                moduli[size] = records

                # Log the number of records found
                self.logger.info(f"Retrieved {len(records)}  records for key size {size}")

    except Error as err:
        self.logger.error(f"Error retrieving moduli: {err}")
        raise RuntimeError(f"Database query failed: {err}")

    # If an output file is specified, and we have enough records for all sizes, write the results
    if output_file:
        self.write_record_to_file(moduli, output_file)
        self.logger.info(f"Successfully created moduli file with {self.records_per_keylength} records per key size")

    return moduli


def write_record_to_file(self, moduli_data: dict, output_file: Path) -> list:
    """
    Writes moduli data records to a specified output file in a structured format.
    This method creates or overwrites the specified output file, writing a header
    and formatted moduli records for various key sizes. The function also maintains
    a list of moduli that need to be removed from the database based on the input data.

    :param self: Instance of the class containing the method.
    :type self: Any
    :param moduli_data: Dictionary containing modulus records categorized by key sizes.
        Each key is a key size, and the value is a list of records containing data such as
        timestamp, type, tests, trials, size, generator, and modulus.
    :type moduli_data: dict
    :param output_file: Path object representing the file where moduli data will be written.
    :type output_file: Path
    :return: List of modulus values that need to be removed from the database.
    :rtype: list
    """
    moduli_to_delete = []
    try:
        with self.file_writer(output_file) as ssh_moduli_file:
            # with output_file.open('w') as of:
            # Write File Header
            ssh_moduli_file.write(
                # of.write(
                f'# /etc/ssh/modul: dcrunch.threatwonk.net: {ISO_UTC_TIMESTAMP()}\n'
            )

            # Write data for each key size
            for size, records in moduli_data.items():
                for record in records:
                    # Format: timestamp type tests trials size generator modulus
                    # The timestamp should already be in compressed format
                    ssh_moduli_file.write(' '.join((
                        # of.write(' '.join((
                        strip_punction_from_datetime_str(record['timestamp']),
                        record['type'],
                        record['tests'],
                        str(record['trials']),
                        str(record['size']),
                        str(record['generator']),
                        record['modulus'],
                        '\n'
                    )))
                    if record['modulus']:
                        moduli_to_delete.append(record['modulus'])

        self.logger.info(f"Successfully wrote moduli to file: {output_file}")
        self.logger.debug(f"Moduli to delete from DB: {moduli_to_delete}")

    except IOError as err:
        self.logger.error(f"Error writing to file {output_file}: {err}")
        raise

    return moduli_to_delete


def stats(self) -> Dict[str, str]:
    """
    Generates and retrieves statistical data on a set of key moduli sizes. Performs
    database queries to calculate and validate the count of available records for
    specific key sizes based on predefined moduli sizes. Results are logged and
    formatted as a dictionary mapping each modulus size to its corresponding count.

    :param self: Represents the instance that holds required attributes like
                 key_lengths, db_name, view_name, logger, and query execution
                 functionalities.
    :type self: object
    :return: A dictionary where the keys are moduli sizes (adjusted from key_lengths)
             and the values are the respective record counts obtained from the
             database query.
    :rtype: Dict[int, int]
    :raises RuntimeError: If there is an error during the database query execution.
    """
    moduli_query_sizes = []
    for item in self.key_lengths:
        moduli_query_sizes.append(item - 1)

    # First, check if we have enough records for each key size
    status: List[int, int] = list()

    # Validate identifiers
    if not (is_valid_identifier(self.db_name) and is_valid_identifier(self.view_name)):
        self.logger.error("Invalid database or table name")
        return 0

    try:
        for size in moduli_query_sizes:
            # Count query to check available records
            count_query = f"""
                              SELECT COUNT(*)
                              FROM {self.db_name}.{self.view_name}
                              WHERE size = ?
                              """
            result = self.execute_select(count_query, (size,))
            count = result[0]['COUNT(*)']
            status.append(count)

    except Exception as err:
        self.logger.error(f"Error retrieving moduli: {err}")
        raise RuntimeError(f"Database query failed: {err}")

    # Output
    results = dict(zip(moduli_query_sizes, status))
    self.logger.info(f"Moduli statistics:")
    self.logger.info('size  count')
    for size, count in results.items():
        self.logger.info(f'{size:>4} {count:>4}')

    return results