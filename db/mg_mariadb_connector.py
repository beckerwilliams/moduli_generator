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


if __name__ == "__main__":

    db = MariaDBConnector("/Users/ron/development/moduli_generator/moduli_generator.cnf")

    try:
        db.sql("SHOW DATABASES")
    except mariadb.Error as e:
        print(f"Error executing SQL query: {e}")

    db.sql("SHOW TABLES")
