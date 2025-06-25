from db.moduli_db_utilities import MariaDBConnector
from mariadb import (Error, connect)
# Example usage
db = MariaDBConnector("/path/to/config.cnf")
db.truncate_table("screened_candidates")

def delete_from_table(self, table_name, where_clause=None):
    """
    Delete entries from a table in the database.

    Args:
        table_name (str): The name of the table to delete from
        where_clause (str, optional): SQL WHERE clause to filter records to delete.
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

    except mariadb.Error as e:
        print(f"Error deleting from table {table_name}: {e}")
        return -1