-- Schema for storing SSH moduli candidates
CREATE DATABASE IF NOT EXISTS mod_gen;
USE mod_gen;

CREATE TABLE screened_candidates (
#     id BIGINT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME PRIMARY KEY NULL,
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


# [2025-06-23 18:26:28] Connecting to ron@maraidb.threatwonk.net…
# [2025-06-23 18:26:30] Using batch mode, maximum number of INSERT/UPDATE/DELETE statements is 1000
# [2025-06-23 18:26:30] Run /Users/ron/development/moduli_generator/db/moduli_schema.sql
# CREATE DATABASE IF NOT EXISTS mod_gen
# [2025-06-23 18:26:30] 0 row(s) affected in 6 ms
# USE mod_gen
# [2025-06-23 18:26:30] 0 row(s) affected in 7 ms
# CREATE TABLE screened_candidates (
# #     id BIGINT AUTO_INCREMENT PRIMARY KEY,
# timestamp DATETIME PRIMARY KEY NULL,
# candidate_type ENUM('2', '5') NOT NULL COMMENT 'Generator type',
# tests VARCHAR(50) NOT NULL COMMENT 'Tests perfo...
# [2025-06-23 18:26:30] 0 row(s) affected in 16 ms
# CREATE INDEX idx_key_size ON screened_candidates(key_size)
# [2025-06-23 18:26:30] 0 row(s) affected in 26 ms
# CREATE INDEX idx_timestamp ON screened_candidates(timestamp)
# [2025-06-23 18:26:30] 0 row(s) affected in 21 ms
# [2025-06-23 18:26:30] Summary: 5 of 5 statements executed in 226 ms (782 symbols in file)