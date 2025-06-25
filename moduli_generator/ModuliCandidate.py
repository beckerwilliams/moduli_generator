from datetime import UTC, datetime
from pathlib import Path
from typing import Dict

import sqlalchemy as sa
from sqlalchemy.orm import (declarative_base, sessionmaker)

from db.mariadb_cnf_parser import parse_mysql_config
from db.moduli_db_utilities import MariaDBConnector
from moduli_generator import ModuliGenerator

Base = declarative_base()


class ModuliCandidate(ModuliGenerator, Base):
    __tablename__ = 'screened_candidates'

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    timestamp = sa.Column(sa.DateTime, nullable=False)
    candidate_type = sa.Column(sa.Enum('2', '5'), nullable=False)
    tests = sa.Column(sa.String(50), nullable=False)
    trials = sa.Column(sa.Integer, nullable=False)
    key_size = sa.Column(sa.Integer, nullable=False)
    generator = sa.Column(sa.BigInteger, nullable=False)
    modulus = sa.Column(sa.Text, nullable=False)
    file_origin = sa.Column(sa.String(255), nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.now(UTC))


class ModuliDatabaseManager:
    def __init__(self, client_config):
     # def __init__(self,
     #             connection_string='jdbc:mariadb://moduli_generator:pEAkTNc41u8XCs0@mariadb.threatwonk.net:3306/mod_gen'):
     #    """
     self.db = MariaDBConnector(
         client_conf["host"] | "localhost",
         client_conf["port"] | 3306,
         client_conf["user"] | "",
         client_conf["password"] | "unknown",
         client_conf["database"] | "unknown"
     )

    def parse_and_store_screened_candidates(self, screened_file: Path, key_length: int):
        """
        Parse screened candidates file and store in the database

        Args:
            screened_file: Path to screened candidates file
            key_length: Key length of the candidates
        """
        # session = self.Session()

        try:
            with open(screened_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    parts = line.split()
                    if len(parts) == 7:
                        candidate = ModuliCandidate(
                            timestamp=datetime.fromtimestamp(int(parts[0])),
                            candidate_type=parts[1],
                            tests=parts[2],
                            trials=int(parts[3]),
                            key_size=key_length,
                            generator=int(parts[5]),
                            modulus=parts[6],
                            file_origin=str(screened_file)
                        )
                        db.sql()

            session.commit()
            self.logger.info(f'Stored {screened_file} candidates in database')

        except Exception as e:
            session.rollback()
            self.logger.error(f'Failed to store candidates: {e}')

        finally:
            session.close()

    def generate_moduli(self) -> Dict[int, Path]:
        """
        Override generate_moduli to include database storage
        """
        generated_moduli = super().generate_moduli()

        db_manager = ModuliDatabaseManager()
        for key_length, screened_file in generated_moduli.items():
            db_manager.parse_and_store_screened_candidates(screened_file, key_length)

        return generated_moduli


if __name__ == "__main__":

    client_conf = parse_mysql_config('/Users/ron/development/moduli_generator/moduli_generator.cnf')["client"]
    db = MariaDBConnector(
        client_conf["host"] | "localhost",
        client_conf["port"] | 3306,
        client_conf["user"] | "",
        client_conf["password"] | "unknown",
        client_conf["database"] | "unknown"
    )
