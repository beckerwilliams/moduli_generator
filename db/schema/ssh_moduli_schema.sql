CREATE DATABASE IF NOT EXISTS moduli_db;

-- Configuration table for constant values
CREATE TABLE moduli_db.mod_fl_consts (
    config_id TINYINT UNSIGNED PRIMARY KEY,
    type ENUM('2', '5') NOT NULL COMMENT 'Generator type (2 or 5)',
    tests VARCHAR(50) NOT NULL COMMENT 'Tests performed on the modulus',
    trials INT UNSIGNED NOT NULL COMMENT 'Number of trials performed',
    generator BIGINT UNSIGNED NOT NULL COMMENT 'Generator value',
    description VARCHAR(255) COMMENT 'Optional description of this configuration'
);

-- Main moduli table with a foreign key to config
CREATE TABLE IF NOT EXISTS moduli_db.moduli (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    config_id TINYINT UNSIGNED NOT NULL COMMENT 'Foreign key to moduli constants',
    size INT UNSIGNED NOT NULL COMMENT 'Key size in bits',
    modulus TEXT NOT NULL COMMENT 'Prime modulus value',
    modulus_hash VARCHAR(128) GENERATED ALWAYS AS (SHA2(modulus, 512)) STORED COMMENT 'Hash of modulus for uniqueness check',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (config_id) REFERENCES mod_fl_consts(config_id),
    UNIQUE KEY (modulus_hash)
);

CREATE VIEW IF NOT EXISTS moduli_db.moduli_view AS
SELECT
    m.timestamp,
    c.type,
    c.tests,
    c.trials,
    m.size,
    c.generator,
    m.modulus
FROM
    moduli_db.moduli m
        JOIN
    moduli_db.mod_fl_consts c ON m.config_id = c.config_id;

-- Indexes for commonly queried fields
CREATE INDEX idx_size ON moduli_db.moduli(size);
CREATE INDEX idx_timestamp ON moduli_db.moduli(timestamp);

-- Insert configuration
INSERT INTO moduli_db.mod_fl_consts (config_id, type, tests, trials, generator, description)
VALUES (1, '2', 6, 100, 2, 'Becker Williams SSH moduli properties');

-- Insert moduli using the configuration
# INSERT INTO moduli_db.moduli (timestamp, config_id, size, modulus)
# VALUES (TIMESTAMP, 1, KEYSIZE, MODULUS)
