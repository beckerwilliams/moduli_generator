from datetime import datetime
from pathlib import PosixPath as Path
from sys import exit

import mariadb

from db.mariadb_cnf_parser import parse_mysql_config


class MariaDBConnector:

    def __init__(self, mycnf: str):

        if not mycnf:
            mycnf = Path.home() / ".my.cnf"

        conf = parse_mysql_config(mycnf)["client"]
        try:
            self.connection = mariadb.connect(
                host=conf["host"],
                port=int(conf["port"]),
                user=conf["user"],
                password=conf["password"],
                database=conf["database"]
            )
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            exit(1)

    def sql(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        for row in cursor:
            print(row)
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
        except mariadb.Error as e:
            print(f"Error inserting candidate: {e}")
            return None


if __name__ == "__main__":

    db = MariaDBConnector("/Users/ron/development/moduli_generator/moduli_generator.cnf")

    try:
        db.sql("SHOW DATABASES")
    except mariadb.Error as e:
        print(f"Error executing SQL query: {e}")

    try:
        db.sql("USE mod_gen")
    except mariadb.Error as e:
        print(f"Error selecting database: {e}")

    db.sql("SHOW TABLES")

    # Example usage of the insert_candidate function
    # Uncomment to test
    """
    test_timestamp = datetime.now()
    test_id = db.add(
        timestamp=test_timestamp,
        candidate_type="2",
        tests="primality,miller-rabin",
        trials=10,
        key_size=2048,
        generator=2,
        modulus="ABCDEF123456789...",  # This would be a long prime number
        file_origin="/path/to/source/file.txt"
    )

    if test_id:
        print(f"Successfully inserted candidate with ID: {test_id}")
    """

    test_timestamp = datetime.now()
    test_id = db.add(timestamp=test_timestamp,
                     candidate_type="2",
                     tests="primality,miller-rabin",
                     trials=10,
                     key_size=2048,
                     generator=2,
                     modulus="ABCDEF123456789...",  # This would be a long prime number
                     file_origin="/path/to/source/file.txt")
