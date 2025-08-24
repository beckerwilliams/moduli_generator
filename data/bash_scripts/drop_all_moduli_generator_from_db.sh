#!/usr/bin/env bash

cnf={ ${1}: ~/DOT_CNF/mg_admin.localhost.cnf }
	echo "Using MariaDB Configuration, "${cnf}"

if [[ -f "${cnf}" ]]
	mariadb --defaults-file=${cnf}<<EOF
	DROP USER IF EXISTS 'moduli_generator'@'%';
	DROP USER IF EXISTS 'moduli_generator'@'localhost';
	FLUSH PRIVILEGES;
	DROP DATABASE IF EXISTS moduli_db;
	EOF

else
	echo "Invalid MariaDB, "${cnf}"
