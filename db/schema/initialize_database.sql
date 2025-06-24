-- Create database and user
CREATE DATABASE IF NOT EXISTS ssh_moduli;
CREATE USER IF NOT EXISTS 'moduli_user'@'localhost' IDENTIFIED BY 'PLACEHOLDER_PASSWORD';
GRANT ALL PRIVILEGES ON ssh_moduli.* TO 'moduli_user'@'localhost';
FLUSH PRIVILEGES;