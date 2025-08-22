#!/usr/bin/env bash
mariadb --defaults-file=/Users/ron/DOT_CNF/mg_admin.localhost.cnf <<EOF
DROP DATABASE IF EXISTS moduli_db;
DROP USER IF EXISTS 'moduli_generator'@'%';
DROP USER IF EXISTS 'moduli_generator'@'localhost';
FLUSH PRIVILEGES;
EOF
