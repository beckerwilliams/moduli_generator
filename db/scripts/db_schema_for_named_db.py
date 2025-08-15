from typing import Any, Dict, List


def get_moduli_generator_schema_statements(
    moduli_db: str = "test_moduli_db",
) -> List[Dict[str, Any]]:
    """
    Generates and returns a list of database schema setup statements for creating the required
        moduli-related tables, views, and indexes within a specified database. Additionally, it
        includes an initial insert statement for populating configuration constants.

    Args:
        moduli_db (str): Name of the database where the schema will be created. Defaults        to 'test_moduli_db'.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each representing an SQL query statement with optional        parameters to execute and whether a fetch operation is required.
    """
    # Note: Database/table names cannot be parameterized in MySQL/MariaDB,
    # so we still need to validate and use f-strings for identifiers
    if not moduli_db.replace("_", "").replace("-", "").isalnum():
        raise ValueError(f"Invalid database name: {moduli_db}")

    statements = [
        {
            "query": f"CREATE DATABASE IF NOT EXISTS {moduli_db}",
            "params": None,
            "fetch": False,
        },
        {
            "query": f"""CREATE TABLE {moduli_db}.mod_fl_consts (
                config_id TINYINT UNSIGNED PRIMARY KEY,
                type ENUM('2', '5') NOT NULL COMMENT 'Generator type (2 or 5)',
                tests VARCHAR(50) NOT NULL COMMENT 'Tests performed on the modulus',
                trials INT UNSIGNED NOT NULL COMMENT 'Number of trials performed',
                generator BIGINT UNSIGNED NOT NULL COMMENT 'Generator value',
                description VARCHAR(255) COMMENT 'Moduli Generator (R) OpenSSH2 moduli properties'
            )""",
            "params": None,
            "fetch": False,
        },
        {
            "query": f"""CREATE TABLE IF NOT EXISTS {moduli_db}.moduli (
                id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME NOT NULL,
                config_id TINYINT UNSIGNED NOT NULL COMMENT 'Foreign key to moduli constants',
                size INT UNSIGNED NOT NULL COMMENT 'Key size in bits',
                modulus TEXT NOT NULL COMMENT 'Prime modulus value',
                modulus_hash VARCHAR(128) GENERATED ALWAYS AS (SHA2(modulus, 512)) STORED COMMENT 'Hash of modulus',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (config_id) REFERENCES mod_fl_consts(config_id),
                UNIQUE KEY (modulus_hash)
            )""",
            "params": None,
            "fetch": False,
        },
        {
            "query": f"""CREATE VIEW IF NOT EXISTS {moduli_db}.moduli_view AS
            SELECT
                m.timestamp,
                c.type,
                c.tests,
                c.trials,
                m.size,
                c.generator,
                m.modulus
            FROM
                {moduli_db}.moduli m
                    JOIN
                {moduli_db}.mod_fl_consts c ON m.config_id = c.config_id""",
            "params": None,
            "fetch": False,
        },
        {
            "query": f"""CREATE TABLE IF NOT EXISTS {moduli_db}.moduli_archive (
            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME NOT NULL,
            config_id TINYINT UNSIGNED NOT NULL COMMENT 'Foreign key to moduli constants',
            size INT UNSIGNED NOT NULL COMMENT 'Key size in bits',
            modulus TEXT NOT NULL COMMENT 'Prime modulus value',
            modulus_hash VARCHAR(128) GENERATED ALWAYS AS (SHA2(modulus, 512)) STORED COMMENT 'Hash of modulus',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (config_id) REFERENCES mod_fl_consts(config_id),
            UNIQUE KEY (modulus_hash)
        )""",
            "params": None,
            "fetch": False,
        },
        {
            "query": f"CREATE INDEX idx_size ON {moduli_db}.moduli(size)",
            "params": None,
            "fetch": False,
        },
        {
            "query": f"CREATE INDEX idx_timestamp ON {moduli_db}.moduli(timestamp)",
            "params": None,
            "fetch": False,
        },
        {
            "query": f"CREATE INDEX idx_size ON {moduli_db}.moduli_archive(size)",
            "params": None,
            "fetch": False,
        },
        {
            "query": f"CREATE INDEX idx_timestamp ON {moduli_db}.moduli_archive(timestamp)",
            "params": None,
            "fetch": False,
        },
        {
            "query": f"""INSERT INTO {moduli_db}.mod_fl_consts (config_id, type, tests, trials, generator, description)
                        VALUES (%s, %s, %s, %s, %s, %s) \
                        """,
            "params": (
                1,
                "2",
                "6",
                100,
                2,
                "Moduli Generator (R) SSH moduli properties",
            ),
            "fetch": False,
        },
    ]

    return statements
