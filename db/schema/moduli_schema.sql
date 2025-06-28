-- Schema for storing SSH moduli candidates
CREATE DATABASE IF NOT EXISTS mod_gen;

CREATE TABLE mod_gen.screened_moduli (
    timestamp DATETIME NOT NULL,
    candidate_type ENUM('2', '5') NOT NULL COMMENT 'Generator type',
    tests VARCHAR(50) NOT NULL COMMENT 'Tests performed',
    trials INT UNSIGNED NOT NULL COMMENT 'Number of trials',
    key_size INT UNSIGNED NOT NULL COMMENT 'Key size in bits',
    generator BIGINT UNSIGNED NOT NULL COMMENT 'Generator value',
    modulus TEXT NOT NULL COMMENT 'Prime modulus',
    modulus_hash VARCHAR(64) GENERATED ALWAYS AS (SHA2(modulus, 256)) STORED COMMENT 'SHA256 hash of the modulus',
    file_origin VARCHAR(255) NOT NULL COMMENT 'Source file of the modulus',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (timestamp, key_size),
    UNIQUE KEY (modulus_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Index for performance optimization
CREATE INDEX idx_key_size ON mod_gen.screened_moduli(key_size);
CREATE INDEX idx_timestamp ON mod_gen.screened_moduli(timestamp);
CREATE INDEX idx_created_at ON mod_gen.screened_moduli(created_at);