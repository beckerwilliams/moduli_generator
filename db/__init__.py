import configparser
from configparser import (ConfigParser)
from contextlib import contextmanager
from pathlib import PosixPath as Path
from re import sub
from typing import (
    Dict,
    List,
    Optional
)

from mariadb import (ConnectionPool, Error)  # Add this import

from config import (DEFAULT_KEY_LENGTHS, ISO_UTC_TIMESTAMP, ModuliConfig, default_config, is_valid_identifier)


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
    Provides a connection pool and management functions for interacting with a MariaDB database.

    This class wraps around the MariaDB connection pooling mechanism to offer efficient,
    manageable access to database connections. It includes context managers for safe and
    atomic database operations, as well as utility methods for executing queries and managing
    transactions.

    :ivar mariadb_cnf: Path to the MariaDB configuration file.
    :type mariadb_cnf: str
    :ivar db_name: Name of the target database for operations.
    :type db_name: str
    :ivar base_dir: The base directory for storing files or logs.
    :type base_dir: str
    :ivar moduli_file_pfx: Prefix for generated file names related to database moduli operations.
    :type moduli_file_pfx: str
    :ivar table_name: Name of the table used for database operations.
    :type table_name: str
    :ivar view_name: Name of the view related to database queries.
    :type view_name: str
    :ivar config_id: Identifier representing a specific configuration instance.
    :type config_id: str
    :ivar key_lengths: List of key lengths used for cryptographic or operational purposes.
    :type key_lengths: List[int]
    :ivar records_per_keylength: Number of records tied to each key length.
    :type records_per_keylength: int
    :ivar moduli_file: Path to the file storing database moduli information.
    :type moduli_file: Path
    :ivar delete_records_on_moduli_write: Boolean flag to remove records after writing to the file.
    :type delete_records_on_moduli_write: bool
    :ivar delete_records_on_read: Boolean flag to remove records after they are read from the database.
    :type delete_records_on_read: bool
    :ivar logger: Logger instance for managing log output for the module.
    :type logger: Logger
    """

    def __enter__(self):
        """
        Context manager entry method. When the managed context is entered,
        this method is called to return the resource or object to be used
        within the context.

        :return: The object or resource that should be used within the managed
            context.
        :rtype: The same type as the class implementing this method.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Handles the cleanup process when exiting a context manager for the object. Ensures that
        the connection pool is properly closed if it exists and logs any errors that occur
        during this operation.

        :param exc_type: The exception type if an exception was raised, otherwise None
        :type exc_type: type | None
        :param exc_val: The exception value if an exception was raised, otherwise None
        :type exc_val: Exception | None
        :param exc_tb: The traceback object if an exception was raised, otherwise None
        :type exc_tb: TracebackType | None
        :return: Returns False to re-raise any exception encountered in the context
        :rtype: bool
        """
        if hasattr(self, 'pool') and self.pool:
            try:
                self.pool.close()
                self.logger.debug("Connection pool closed")
            except Error as err:
                self.logger.error(f"Error closing connection pool: {err}")
        return False

    @contextmanager
    def get_connection(self):
        """
        Provides a context manager for safely getting and managing a connection
        from the connection pool. Ensures the connection is properly closed and
        returned to the pool after usage.

        :return: Yields a connection object from the connection pool.
        :rtype: Connection
        """
        connection = None
        try:
            connection = self.pool.get_connection()
            yield connection
        except Error as err:
            self.logger.error(f"Error getting connection from pool: {err}")
            raise
        finally:
            if connection:
                connection.close()  # Returns connection to pool

    @contextmanager
    def transaction(self, connection=None):
        """
        Provides a context manager for handling database transactions. It ensures that the
        transaction is properly committed or rolled back and manages logging for the process.

        :param connection: Optional existing connection to be used in the transaction. If not
            provided, a new connection will be retrieved from the connection pool.
        :type connection: Optional
        :return: Yields the database connection within the transaction context.
        :rtype: ContextManager
        """
        if connection:
            # Use the provided connection
            try:
                yield connection
                connection.commit()
                self.logger.debug("Transaction committed")
            except Exception as e:
                connection.rollback()
                self.logger.error(f"Transaction rolled back due to error: {e}")
                raise
        else:
            # Get connection from pool
            with self.get_connection() as conn:
                try:
                    yield conn
                    conn.commit()
                    self.logger.debug("Transaction committed")
                except Exception as e:
                    conn.rollback()
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
        Initializes a class instance with provided configuration parameters and sets up a MariaDB
        connection pool, along with configured logging for module operations.

        A Detailed connection pool is established using connection parameters parsed from the MariaDB
        configuration file, ensuring efficient database interaction. Logging is configured for the
        module using the provided logger in the configuration.

        :param config: Configuration object containing necessary properties for initialization
                       such as MariaDB setup, table/view names, logging preferences, and other
                       settings.
        :type config: ModuliConfig

        :raises RuntimeError: If the connection pool creation fails due to database-related issues.
        """
        for key, value in config.__dict__.items():
            if key in ["mariadb_cnf",
                       "db_name",
                       "base_dir",
                       "moduli_file_pfx",
                       "table_name",
                       "view_name",
                       "config_id",
                       "key_lengths",
                       "records_per_keylength",
                       "moduli_file",
                       "delete_records_on_moduli_write",
                       "delete_records_on_read",
                       'get_logger()'
                       ]:
                setattr(self, key, value)

        # COnfigure Logger for Module
        self.logger = config.get_logger()
        self.logger.name = __name__

        self.logger.debug(f"Using MariaDB config: {config.mariadb_cnf}")

        mysql_cnf = parse_mysql_config(config.mariadb_cnf)["client"]

        try:
            # Create connection pool instead of single connection
            self.pool = ConnectionPool(
                pool_name='moduli_pool',
                pool_size=10,  # Adjust based on your needs
                pool_reset_connection=True,
                host=mysql_cnf["host"],
                port=int(mysql_cnf["port"]),
                user=mysql_cnf["user"],
                password=mysql_cnf["password"],
                database=mysql_cnf["database"]
            )
            self.logger.info(f"Connection pool created with size: 10")
        except Error as err:
            self.logger.error(f"Error creating connection pool: {err}")
            raise RuntimeError(f"Connection pool creation failed: {err}")

    def sql(self, query: str, params: Optional[tuple] = None, fetch: bool = True) -> Optional[List[Dict]]:
        """
        Executes an SQL query with optional parameters and returns the results or
        affected rows depending on the fetch flag.

        This method manages database transactions, logs the results or errors, and
        ensures proper resource cleanup. It also supports parameterized queries
        for enhanced security against SQL injection.

        :param query: The SQL query to be executed.
        :type query: str
        :param params: Optional tuple of parameters for the query, default is None.
        :type params: Optional[tuple]
        :param fetch: A flag indicating whether to fetch and return query results
            (True) or not (False). Defaults to True.
        :type fetch: bool
        :return: A list of results as dictionaries if fetch is True, or None if
            fetch is False.
        :rtype: Optional[List[Dict]]
        :raises RuntimeError: If an error occurs during query execution.
        """
        try:
            with self.get_connection() as connection:
                with self.transaction(connection):
                    with connection.cursor(dictionary=True) as cursor:
                        if params:
                            cursor.execute(query, params)
                        else:
                            cursor.execute(query)

                        if fetch:
                            results = cursor.fetchall()
                            self.logger.debug(f"Query returned {len(results)} rows")
                            return results
                        else:
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
        Executes an update query on the database and returns the number of rows affected. The
        method ensures the query is executed within a managed connection and transaction block
        to maintain database integrity and handle rollback in case of errors.

        :param query: The SQL query to be executed.
        :type query: str
        :param params: Optional parameters to be used with the query.
        :type params: Optional[tuple]
        :return: The number of rows affected by the query execution.
        :rtype: int
        :raises RuntimeError: If executing the update query fails.
        """
        try:
            with self.get_connection() as connection:
                with self.transaction(connection):
                    with connection.cursor() as cursor:
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
        Execute multiple SQL queries in a batch with optional parameters.

        This method allows execution of a series of SQL queries in a batch,
        using transactions to ensure atomicity of operations. The queries can
        have associated parameter tuples for execution.

        :param queries: A list of SQL query strings to be executed in a batch.
        :type queries: List[str]
        :param params_list: A list of tuples containing parameters to
            correspond with each query. If provided, its length should not
            exceed the length of the queries list. Defaults to None.
        :type params_list: Optional[List[tuple]]
        :return: Boolean indicating whether the batch execution was successful.
        :rtype: bool
        :raises RuntimeError: If any error occurs during the execution of
            the batch queries.
        """
        try:
            with self.get_connection() as connection:
                with self.transaction(connection):
                    with connection.cursor() as cursor:
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

    def _add_without_transaction(self, connection, timestamp: int, key_size: int, modulus: str) -> int:
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
            with connection.cursor() as cursor:
                query = f"""INSERT INTO {self.db_name}.{self.table_name} 
                           (timestamp, config_id, size, modulus) VALUES (?, ?, ?, ?)"""
                cursor.execute(query, (timestamp, self.config_id, key_size, modulus))
                last_id = cursor.lastrowid
                self.logger.debug(f'Successfully added {key_size} bit modulus')
                return last_id
        except Error as err:
            self.logger.error(f"Error inserting candidate: {err}")
            raise  # Re-raise to let transaction context manager handle rollback

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
            with self.get_connection() as connection:
                with self.transaction(connection):
                    with connection.cursor() as cursor:
                        query = f"""INSERT INTO {self.db_name}.{self.table_name} 
                               (timestamp, config_id, size, modulus) VALUES (?, ?, ?, ?)"""
                        cursor.execute(query, (timestamp, self.config_id, key_size, modulus))
                        last_id = cursor.lastrowid
                        self.logger.debug(f'Successfully added {key_size} bit modulus')
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
            with self.get_connection() as connection:
                with self.transaction(connection):
                    with connection.cursor() as cursor:
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

    def export_screened_moduli(self, screened_moduli: dict) -> int:
        """
        Stores screened moduli data from the given dictionary into the storage.

        This method iterates over the provided moduli data, extracting
        moduli attributes and saving them using an internal method. The operation
        is performed within a database transaction to ensure atomicity. Errors
        encountered during the process are logged, and an appropriate status is
        returned.

        :param screened_moduli: A dictionary containing moduli data mapped to corresponding keys.
        :type screened_moduli: dict
        :return: An integer indicating the status of the operation,
                 where 0 indicates success and 1 indicates failure.
        :rtype: int
        """
        try:
            with self.get_connection() as connection:
                with self.transaction(connection):
                    for key, moduli_list in screened_moduli.items():
                        for modulus in moduli_list:
                            # Use the internal add method without its own transaction
                            self._add_without_transaction(connection, modulus["timestamp"], modulus["key-size"],
                                                          modulus["modulus"])
            return 0
        except Error as err:
            self.logger.error(f"Error storing moduli: {err}")
            return 1

    def write_moduli_file(self, output_file: Path = None) -> Dict[int, list]:
        """
        Retrieves cryptographic moduli data from a database, ensuring sufficient
        records exist for predefined key sizes, optionally writing the moduli
        to a specified output file. Raises an exception if the required number
        of records for any key size is unavailable.

        :param output_file: Path to the file where moduli should be written. If None,
            the function only returns the moduli dictionary without writing to a file.
        :type output_file: Path, optional
        :return: A dictionary that maps each key size to a list of its associated
            retrieved moduli records from the database.
        :rtype: Dict[int, list]
        :raises RuntimeError: If there are insufficient records for any key size or
            if the database query fails.
        """
        if not output_file:
            output_file = self.base_dir / ''.join((self.moduli_file_pfx, ISO_UTC_TIMESTAMP(compress=True)))

        self.logger.info(f'ssh-moduli output file: {output_file}')

        # Verify that a sufficient number of moduli for each keysize exist in the db
        stats = self.stats()
        for stat in stats:
            if stats[stat] < self.records_per_keylength:
                self.logger.info(
                    f"Insufficient records for key size {stat}: {stats[stat]} available,"
                    f" {self.records_per_keylength} required"
                )
                raise RuntimeError(
                    f"Insufficient records for key size {stat}: {stats[stat]} available, "
                    f"{self.records_per_keylength} required"
                )

        # Collect Screened Moduli from Database
        moduli = {}
        try:
            with self.get_connection() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    for size in DEFAULT_KEY_LENGTHS:  # We want UNIQUE Key Lengths, Not all the ones used to invoke cli
                        query = f"""
                                SELECT timestamp, type, tests, trials, size, generator, modulus
                                FROM {self.db_name}.{self.view_name}
                                WHERE size = {size - 1}
                                LIMIT {self.records_per_keylength}
                                """
                        cursor.execute(query)
                        records = list(cursor.fetchall())
                        moduli[size] = records
                        self.logger.info(f"Retrieved {len(records)} records for key size {size}")

        except Error as err:
            self.logger.error(f"Error retrieving moduli: {err}")
            raise RuntimeError(f"Database query failed: {err}")

        # Write the moduli file
        moduli_to_write: List[str] = []
        for key, items in moduli.items():
            for item in items:
                # Access dictionary keys instead of object attributes
                line = ' '.join([
                    sub(r'[^0-9]', '', item['timestamp'].isoformat()),
                    str(item['type']),
                    str(item['tests']),
                    str(item['trials']),
                    str(item['size']),
                    str(item['generator']),
                    str(item['modulus']),
                    '\n'
                ])
                moduli_to_write.append(line)

            moduli_hdr = f'# [usr/local]/etc/ssh/moduli from MODULI_GENERATOR: {ISO_UTC_TIMESTAMP()}\n'

            with self.file_writer(output_file.resolve()) as ssh_moduli_file:
                ssh_moduli_file.writelines(moduli_hdr)
                ssh_moduli_file.writelines(moduli_to_write)
        self.logger.info(f"Successfully wrote moduli to file: {output_file}")

    def stats(self) -> Dict[str, str]:
        """
        Generates statistics about moduli files by querying the database for each key size.
        It calculates the number of available records per key size and potential SSH moduli
        files based on the configured records per key length.

        :param self: An instance of the class containing the method.

        :raises RuntimeError: If the database query fails during execution.
        :return: A dictionary containing sizes as keys and their respective counts or calculated
            values as values. The keys represent moduli query sizes, while the values indicate
            counts or moduli file statistics.
        :rtype: Dict[str, str]

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
            # Calculate Number of Moduli Files Available
            status.append(
                {'potential_ssh_moduli_files': f'{int(min(status) / self.config.records_per_keylength)}'}
            )

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
