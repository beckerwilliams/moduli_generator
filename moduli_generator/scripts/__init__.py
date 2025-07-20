from contextlib import contextmanager
from logging import getLogger
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import mariadb
from mariadb import Error, PoolError

from config import is_valid_identifier


def parse_mysql_config(config_file: Path) -> dict:
    """
    Parse a MySQL configuration file and return a dictionary of configuration values.
    
    Args:
        config_file: Path to the MySQL configuration file
        
    Returns:
        Dictionary containing parsed configuration values
        
    Raises:
        FileNotFoundError: If the configuration file doesn't exist
        ValueError: If the configuration file format is invalid
    """
    config = {}
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    try:
        with open(config_file, 'r') as f:
            current_section = None
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#') or line.startswith(';'):
                    continue

                # Handle sections
                if line.startswith('[') and line.endswith(']'):
                    current_section = line[1:-1]
                    if current_section not in config:
                        config[current_section] = {}
                    continue

                # Handle key-value pairs
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')

                    if current_section:
                        config[current_section][key] = value
                    else:
                        config[key] = value
                else:
                    raise ValueError(f"Invalid configuration format at line {line_num}: {line}")

    except Exception as e:
        raise ValueError(f"Error parsing configuration file {config_file}: {e}")

    return config


def get_mysql_config_value(config: dict, section: str, key: str, default: Any = None) -> Any:
    """
    Get a configuration value from the parsed MySQL config dictionary.
    
    Args:
        config: Parsed configuration dictionary
        section: Configuration section name
        key: Configuration key name  
        default: Default value if key not found
        
    Returns:
        Configuration value or default
    """
    try:
        if section in config and key in config[section]:
            value = config[section][key]

            # Convert common types
            if value.lower() in ('true', 'yes', '1', 'on'):
                return True
            elif value.lower() in ('false', 'no', '0', 'off'):
                return False
            elif value.isdigit():
                return int(value)
            elif '.' in value and value.replace('.', '').isdigit():
                return float(value)
            else:
                return value
        else:
            return default
    except (KeyError, AttributeError):
        return default


class MariaDBConnector:
    """
    A MariaDB database connector class that provides connection management,
    transaction handling, and database operations for moduli generation.
    """

    def __init__(self, config):
        """
        Initialize the MariaDB connector with configuration settings.
        
        Args:
            config: Configuration object containing database settings
            
        Raises:
            RuntimeError: If initialization fails
        """
        try:
            self.logger = getLogger(__name__)
            self.connection = None  # Initialize connection attribute

            # Parse MySQL configuration file
            mysql_config = parse_mysql_config(Path(config.mariadb_cnf))

            # Extract database connection parameters
            self.host = get_mysql_config_value(mysql_config, 'client', 'host', 'localhost')
            self.port = get_mysql_config_value(mysql_config, 'client', 'port', 3306)
            self.user = get_mysql_config_value(mysql_config, 'client', 'user', 'root')
            self.password = get_mysql_config_value(mysql_config, 'client', 'password', '')
            self.database = get_mysql_config_value(mysql_config, 'client', 'database', 'moduli_db')

            # Store configuration attributes
            self.db_name = config.db_name
            self.table_name = config.table_name
            self.view_name = config.view_name
            self.key_lengths = config.key_lengths
            self.records_per_keylength = config.records_per_keylength

            # Create connection pool
            self.pool = mariadb.ConnectionPool(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database,
                pool_name='moduli_pool',
                pool_size=5
            )

            self.logger.info(f"MariaDB connector initialized for {self.host}:{self.port}/{self.database}")

        except Exception as e:
            self.logger.error(f"Failed to initialize MariaDB connector: {e}")
            raise RuntimeError(f"Database initialization failed: {e}")

    def __enter__(self):
        """
        Context manager entry point.
        
        Returns:
            self: The MariaDBConnector instance
        """
        try:
            self.get_connection()
            self.logger.debug("Entered MariaDBConnector context")
            return self
        except Exception as e:
            self.logger.error(f"Error entering context: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit point that handles cleanup and connection closure.
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred  
            exc_tb: Exception traceback if an exception occurred
            
        Returns:
            None: Always returns None to propagate exceptions
        """
        try:
            if hasattr(self, 'connection') and self.connection:
                if exc_type is not None:
                    # An exception occurred, rollback transaction
                    try:
                        self.connection.rollback()
                        self.logger.warning(f"Transaction rolled back due to {exc_type.__name__}: {exc_val}")
                    except Exception as rollback_error:
                        self.logger.error(f"Error during rollback: {rollback_error}")
                else:
                    # No exception, commit transaction
                    try:
                        self.connection.commit()
                        self.logger.debug("Transaction committed successfully")
                    except Exception as commit_error:
                        self.logger.error(f"Error during commit: {commit_error}")

                # Close connection
                try:
                    self.connection.close()
                    self.logger.debug("Database connection closed")
                except Exception as close_error:
                    self.logger.error(f"Error closing connection: {close_error}")

            self.logger.debug("Exited MariaDBConnector context")

        except Exception as e:
            self.logger.error(f"Error in context exit: {e}")

        # Return None to propagate any exceptions
        return None

    def get_connection(self):
        """
        Establish a connection to the MariaDB database using connection pooling.
        
        Returns:
            mariadb.Connection: Database connection object
            
        Raises:
            RuntimeError: If connection cannot be established
        """
        try:
            if not self.connection:
                self.connection = self.pool.get_connection()
                self.logger.debug("Database connection established from pool")
            return self.connection
        except (Error, PoolError) as e:
            self.logger.error(f"Failed to get database connection: {e}")
            raise RuntimeError(f"Database connection failed: {e}")

    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions with automatic commit/rollback.
        
        Yields:
            mariadb.Connection: Database connection within transaction context
            
        Raises:
            RuntimeError: If transaction operations fail
        """
        connection = self.get_connection()
        try:
            # Start transaction
            connection.autocommit = False
            self.logger.debug("Transaction started")

            yield connection

            # Commit transaction
            connection.commit()
            self.logger.debug("Transaction committed")

        except Exception as e:
            # Rollback transaction on error
            try:
                connection.rollback()
                self.logger.warning(f"Transaction rolled back: {e}")
            except Exception as rollback_error:
                self.logger.error(f"Error during rollback: {rollback_error}")
            raise RuntimeError(f"Transaction failed: {e}")
        finally:
            # Restore autocommit
            connection.autocommit = True

    def file_writer(self, moduli_file: Path, records: List[Dict[str, Any]]) -> int:
        """
        Write moduli records to a file in SSH moduli format.
        
        Args:
            moduli_file: Path to output moduli file
            records: List of moduli record dictionaries
            
        Returns:
            int: Number of records written
            
        Raises:
            RuntimeError: If file writing fails
        """
        try:
            with open(moduli_file, 'w') as f:
                f.write(f"# Moduli file generated by moduli_generator\n")
                for record in records:
                    # Format record according to SSH moduli format
                    line = f"{
                    record['timestamp']} {
                    record['type']} {
                    record['tests']} {
                    record['tries']} {
                    record['size']} {
                    record['generator']} {
                    record['modulus']}\n"
                    f.write(line)

            self.logger.info(f"Successfully wrote {len(records)} records to {moduli_file}")
            return len(records)

        except Exception as e:
            self.logger.error(f"Error writing moduli file {moduli_file}: {e}")
            raise RuntimeError(f"File writing failed: {e}")

    def sql(self, query: str, params: Optional[Tuple] = None) -> str:
        """
        Execute a SQL query and return a formatted result string.
        
        Args:
            query: SQL query string
            params: Optional query parameters
            
        Returns:
            str: Formatted query results
            
        Raises:
            RuntimeError: If query execution fails
        """
        try:
            with self.transaction() as connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, params or ())
                results = cursor.fetchall()

                if not results:
                    return "No results found"

                # Format results as a table
                if isinstance(results[0], dict):
                    headers = list(results[0].keys())
                    output = []
                    output.append(" | ".join(headers))
                    output.append("-" * len(output[0]))

                    for row in results:
                        values = [str(row[header]) for header in headers]
                        output.append(" | ".join(values))

                    return "\n".join(output)
                else:
                    return str(results)

        except Exception as e:
            self.logger.error(f"SQL query failed: {e}")
            raise RuntimeError(f"Database query failed: {e}")

    def execute_select(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results as a list of dictionaries.
        
        Args:
            query: SQL SELECT query string
            params: Optional query parameters
            
        Returns:
            List[Dict[str, Any]]: Query results as list of dictionaries
            
        Raises:
            RuntimeError: If query execution fails
        """
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            results = cursor.fetchall()

            self.logger.debug(f"SELECT query returned {len(results)} rows")
            return results

        except Exception as e:
            self.logger.error(f"SELECT query failed: {e}")
            raise RuntimeError(f"Database query failed: {e}")

    def execute_update(self, query: str, params: Optional[Tuple] = None) -> int:
        """
        Execute an UPDATE, INSERT, or DELETE query.
        
        Args:
            query: SQL query string
            params: Optional query parameters
            
        Returns:
            int: Number of affected rows
            
        Raises:
            RuntimeError: If query execution fails
        """
        try:
            with self.transaction() as connection:
                cursor = connection.cursor()
                cursor.execute(query, params or ())
                affected_rows = cursor.rowcount

                self.logger.debug(f"UPDATE query affected {affected_rows} rows")
                return affected_rows

        except Exception as e:
            self.logger.error(f"UPDATE query failed: {e}")
            raise RuntimeError(f"Database query failed: {e}")

    def execute_batch(self, query: str, params_list: List[Tuple]) -> int:
        """
        Execute a batch of queries with different parameters.
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            int: Total number of affected rows
            
        Raises:
            RuntimeError: If batch execution fails
        """
        try:
            total_affected = 0
            with self.transaction() as connection:
                cursor = connection.cursor()

                for params in params_list:
                    cursor.execute(query, params)
                    total_affected += cursor.rowcount

                self.logger.debug(f"Batch execution affected {total_affected} total rows")
                return total_affected

        except Exception as e:
            self.logger.error(f"Batch execution failed: {e}")
            raise RuntimeError(f"Database batch execution failed: {e}")

    def _add_without_transaction(self, modulus_hex: str, size: int, generator: int) -> bool:
        """
        Add a single modulus record without transaction management.
        
        Args:
            modulus_hex: Hexadecimal representation of the modulus
            size: Size of the modulus in bits
            generator: Generator value
            
        Returns:
            bool: True if record was added successfully
            
        Raises:
            RuntimeError: If insertion fails
        """
        try:
            # Validate identifiers
            if not (is_valid_identifier(self.db_name) and is_valid_identifier(self.table_name)):
                raise RuntimeError("Invalid database or table name")

            connection = self.get_connection()
            cursor = connection.cursor()

            insert_query = f"""
                INSERT IGNORE INTO {self.db_name}.{self.table_name} 
                (modulus, size, generator) 
                VALUES (?, ?, ?)
            """

            cursor.execute(insert_query, (modulus_hex, size, generator))
            success = cursor.rowcount > 0

            if success:
                self.logger.debug(f"Added modulus record: size={size}, generator={generator}")
            else:
                self.logger.debug(f"Duplicate modulus record skipped: size={size}, generator={generator}")

            return success

        except Exception as e:
            self.logger.error(f"Error adding modulus record: {e}")
            raise RuntimeError(f"Database insertion failed: {e}")

    def add(self, modulus_hex: str, size: int, generator: int) -> bool:
        """
        Add a single modulus record with transaction management.
        
        Args:
            modulus_hex: Hexadecimal representation of the modulus
            size: Size of the modulus in bits
            generator: Generator value
            
        Returns:
            bool: True if record was added successfully
            
        Raises:
            RuntimeError: If insertion fails
        """
        try:
            with self.transaction():
                return self._add_without_transaction(modulus_hex, size, generator)

        except Exception as e:
            self.logger.error(f"Error adding modulus with transaction: {e}")
            raise RuntimeError(f"Database transaction failed: {e}")

    def add_batch(self, moduli_list: List[Tuple[str, int, int]]) -> int:
        """
        Add multiple modulus records in a single transaction.
        
        Args:
            moduli_list: List of tuples (modulus_hex, size, generator)
            
        Returns:
            int: Number of records successfully added
            
        Raises:
            RuntimeError: If batch insertion fails
        """
        try:
            added_count = 0

            with self.transaction() as connection:
                cursor = connection.cursor()

                # Validate identifiers
                if not (is_valid_identifier(self.db_name) and is_valid_identifier(self.table_name)):
                    raise RuntimeError("Invalid database or table name")

                insert_query = f"""
                    INSERT IGNORE INTO {self.db_name}.{self.table_name} 
                    (modulus, size, generator) 
                    VALUES (?, ?, ?)
                """

                for modulus_hex, size, generator in moduli_list:
                    cursor.execute(insert_query, (modulus_hex, size, generator))
                    if cursor.rowcount > 0:
                        added_count += 1

                self.logger.info(f"Added {added_count} modulus records in batch")
                return added_count

        except Exception as e:
            self.logger.error(f"Error adding moduli batch: {e}")
            raise RuntimeError(f"Database batch insertion failed: {e}")

    def delete_records(self, size: int) -> int:
        """
        Delete all modulus records of a specific size.
        
        Args:
            size: Size of moduli to delete
            
        Returns:
            int: Number of records deleted
            
        Raises:
            RuntimeError: If deletion fails
        """
        try:
            # Validate identifiers
            if not (is_valid_identifier(self.db_name) and is_valid_identifier(self.table_name)):
                raise RuntimeError("Invalid database or table name")

            with self.transaction() as connection:
                cursor = connection.cursor()

                delete_query = f"""
                    DELETE FROM {self.db_name}.{self.table_name} 
                    WHERE size = ?
                """

                cursor.execute(delete_query, (size,))
                deleted_count = cursor.rowcount

                self.logger.info(f"Deleted {deleted_count} modulus records of size {size}")
                return deleted_count

        except Exception as e:
            self.logger.error(f"Error deleting modulus records: {e}")
            raise RuntimeError(f"Database deletion failed: {e}")

    def export_screened_moduli(self, size: int, limit: int) -> List[Dict[str, Any]]:
        """
        Export screened moduli records for a specific size.
        
        Args:
            size: Size of moduli to export
            limit: Maximum number of records to export
            
        Returns:
            List[Dict[str, Any]]: List of moduli records
            
        Raises:
            RuntimeError: If export fails
        """
        try:
            # Validate identifiers
            if not (is_valid_identifier(self.db_name) and is_valid_identifier(self.view_name)):
                raise RuntimeError("Invalid database or view name")

            query = f"""
                SELECT modulus, size, generator, created_at
                FROM {self.db_name}.{self.view_name}
                WHERE size = ?
                ORDER BY created_at DESC
                LIMIT ?
            """

            results = self.execute_select(query, (size, limit))

            self.logger.info(f"Exported {len(results)} screened moduli records of size {size}")
            return results

        except Exception as e:
            self.logger.error(f"Error exporting screened moduli: {e}")
            raise RuntimeError(f"Database export failed: {e}")

    def write_moduli_file(self, output_file: Path, sizes_and_counts: Dict[int, int]) -> Dict[str, Any]:
        """
        Write moduli records to a file in SSH moduli format.
        
        Args:
            output_file: Path to output file
            sizes_and_counts: Dictionary mapping sizes to record counts
            
        Returns:
            Dict[str, Any]: Statistics about the write operation
            
        Raises:
            RuntimeError: If file writing fails
        """
        try:
            total_records = 0
            stats = {}

            # Validate identifiers
            if not (is_valid_identifier(self.db_name) and is_valid_identifier(self.view_name)):
                raise RuntimeError("Invalid database or view name")

            with open(output_file, 'w') as f:
                # Write header
                from datetime import datetime
                timestamp = datetime.utcnow().isoformat() + 'Z'
                f.write(f"# SSH moduli file generated by moduli_generator at {timestamp}\n")

                for size, count in sizes_and_counts.items():
                    if count <= 0:
                        continue

                    # Query moduli for this size
                    query = f"""
                        SELECT modulus, size, generator, created_at
                        FROM {self.db_name}.{self.view_name}
                        WHERE size = ?
                        ORDER BY RAND()
                        LIMIT ?
                    """

                    records = self.execute_select(query, (size, count))

                    for record in records:
                        # Format as SSH moduli format
                        timestamp_str = record['created_at'].strftime('%Y%m%d%H%M%S')
                        line = f"{timestamp_str} 2 6 100 {record['size']} {record['generator']} {record['modulus']}\n"
                        f.write(line)
                        total_records += 1

                    stats[size] = len(records)
                    self.logger.debug(f"Wrote {len(records)} records of size {size}")

            stats['total_records'] = total_records
            stats['output_file'] = str(output_file)

            self.logger.info(f"Successfully wrote {total_records} moduli records to {output_file}")
            return stats

        except Exception as e:
            self.logger.error(f"Error writing moduli file: {e}")
            raise RuntimeError(f"Moduli file writing failed: {e}")

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
        status: List[int] = list()

        # Validate identifiers
        if not (is_valid_identifier(self.db_name) and is_valid_identifier(self.view_name)):
            self.logger.error("Invalid database or table name")
            return {}

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
            min_count = min(status) if status else 0
            potential_files = int(min_count / self.records_per_keylength) if min_count > 0 else 0
            status.append(potential_files)
            moduli_query_sizes.append('potential_ssh_moduli_files')

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
