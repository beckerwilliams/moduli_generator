#!/usr/bin/env python3
from sys import exit

from config import default_config
from db import MariaDBConnector

if __name__ == "__main__":
    db = MariaDBConnector(default_config())
    exit(db.write_moduli_file())
