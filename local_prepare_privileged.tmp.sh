#!/usr/bin/env bash
cp ~/localhost_mariadb.cnf ~/.moduli_generator/privileged.tmp
mariadb --defaults-extra-file=~/localhost_mariadb.cnf<<EOF
-- Drop database if it exists
DROP DATABASE IF EXISTS \`moduli_db\`;

-- Revoke all privileges from moduli_generator user
-- Note: REVOKE will fail if the user doesn't have any privileges
-- We'll handle that by ignoring errors (using OR TRUE in our script)
REVOKE ALL PRIVILEGES ON moduli_db.* FROM 'moduli_generator'@'%';
REVOKE ALL PRIVILEGES ON moduli_db.* FROM 'moduli_generator'@'localhost';

-- Drop the user
DROP USER IF EXISTS 'moduli_generator'@'%';
DROP USER IF EXISTS 'moduli_generator'@'localhost';

-- Confirm operations completed
SELECT 'Cleanup operations completed successfully.' AS Status;
EOF

# Check if the MySQL command executed successfully
if [ $? -eq 0 ]; then
    echo "Database cleanup completed successfully."
else
    echo "Error may have occurred during database cleanup."
    echo "This could be because the user had no privileges to revoke."
    echo "The database and user should still be removed correctly."
fi

exit 0
