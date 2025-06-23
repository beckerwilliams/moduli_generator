-- Schema for storing SSH moduli candidates
CREATE DATABASE IF NOT EXISTS mod_gen;
USE mod_gen;

CREATE TABLE screened_candidates (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    candidate_type ENUM('2', '5') NOT NULL COMMENT 'Generator type',
    tests VARCHAR(50) NOT NULL COMMENT 'Tests performed',
    trials INT UNSIGNED NOT NULL COMMENT 'Number of trials',
    key_size INT UNSIGNED NOT NULL COMMENT 'Key size in bits',
    generator BIGINT UNSIGNED NOT NULL COMMENT 'Generator value',
    modulus TEXT NOT NULL COMMENT 'Prime modulus',
    file_origin VARCHAR(255) NOT NULL COMMENT 'Source file of the modulus',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for performance optimization
CREATE INDEX idx_key_size ON screened_candidates(key_size);
CREATE INDEX idx_timestamp ON screened_candidates(timestamp);