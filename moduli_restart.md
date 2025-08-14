```logs
(.venv) ron@dcrunch:~/moduli % mg_logs
2025-08-14 15:08:42,644 - INFO: Starting Moduli Restart at 2025-08-14 15:08:42.644455, with (3072, 4096, 6144, 7680, 8192) as moduli key-lengths
2025-08-14 15:08:42,644 - INFO: Using Base directory: /home/moduli_generator/.moduli_generator/.moduli
2025-08-14 15:08:42,644 - INFO: Using Candidates directory: /home/moduli_generator/.moduli_generator/.candidates
2025-08-14 15:08:42,644 - INFO: Using Moduli directory: /home/moduli_generator/.moduli_generator/.moduli
2025-08-14 15:08:42,644 - INFO: Using Log directory: /home/moduli_generator/.moduli_generator/.logs
2025-08-14 15:08:42,644 - INFO: Using MariaDB config: /home/moduli_generator/.moduli_generator/moduli_generator.cnf
2025-08-14 15:08:43,891 - DEBUG: Loaded checkpoint from '/home/moduli_generator/.moduli_generator/.candidates/.candidates_7680_20250813012737465629' line 217221
2025-08-14 15:08:43,926 - DEBUG: Loaded checkpoint from '/home/moduli_generator/.moduli_generator/.candidates/.candidates_7680_20250813155056893541' line 4881
2025-08-14 15:08:43,962 - DEBUG: Loaded checkpoint from '/home/moduli_generator/.moduli_generator/.candidates/.candidates_7680_20250813012737464972' line 219438

```

```logs
2025-08-14 15:31:40,290 - INFO: Starting Moduli Restart at 2025-08-14 15:31:40.290461, with (3072, 4096, 6144, 7680, 8192) as moduli key-lengths
2025-08-14 15:31:40,290 - INFO: Using Base directory: /Users/ron/.moduli_generator/.moduli
2025-08-14 15:31:40,290 - INFO: Using Candidates directory: /Users/ron/.moduli_generator/.candidates
2025-08-14 15:31:40,290 - INFO: Using Moduli directory: /Users/ron/.moduli_generator/.moduli
2025-08-14 15:31:40,290 - INFO: Using Log directory: /Users/ron/.moduli_generator/.logs
2025-08-14 15:31:40,290 - INFO: Using MariaDB config: /Users/ron/.moduli_generator/moduli_generator.cnf
2025-08-14 15:31:40,910 - DEBUG: Loaded checkpoint from '/Users/ron/.moduli_generator/.candidates/.candidates_6144_20250808205216234469' line 354775
2025-08-14 15:31:41,283 - DEBUG: Loaded checkpoint from '/Users/ron/.moduli_generator/.candidates/.candidates_7680_20250808205216237775' line 194047
2025-08-14 15:31:41,449 - DEBUG: Loaded checkpoint from '/Users/ron/.moduli_generator/.candidates/.candidates_8192_20250808205216239038' line 167848
```

```logs
mariadb --defaults-extra-file=${HOME}/.moduli_generator/moduli_generator.cnf                                                                                                                                                                                                                                       [12:03:20]
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 193
Server version: 12.0.2-MariaDB Homebrew

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [moduli_db]> show grants;
+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Grants for moduli_generator@localhost                                                                                                                                                                                                    |
+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| GRANT USAGE ON *.* TO `moduli_generator`@`localhost` IDENTIFIED BY PASSWORD '*0AB8CC16043DDC9D0AE13E1C96507FF5E232046F' WITH MAX_UPDATES_PER_HOUR 200 MAX_CONNECTIONS_PER_HOUR 100 MAX_USER_CONNECTIONS 50                               |
| GRANT ALL PRIVILEGES ON `moduli_db`.* TO `moduli_generator`@`localhost` WITH GRANT OPTION                                                                                                                                                |
| GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, REFERENCES, INDEX, ALTER, CREATE TEMPORARY TABLES, LOCK TABLES, CREATE VIEW, SHOW VIEW, CREATE ROUTINE, EVENT, TRIGGER, DELETE HISTORY, SHOW CREATE ROUTINE ON `test`.* TO PUBLIC    |
| GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, REFERENCES, INDEX, ALTER, CREATE TEMPORARY TABLES, LOCK TABLES, CREATE VIEW, SHOW VIEW, CREATE ROUTINE, EVENT, TRIGGER, DELETE HISTORY, SHOW CREATE ROUTINE ON `test\_%`.* TO PUBLIC |
+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
4 rows in set (0.000 sec)

```