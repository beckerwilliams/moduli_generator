=======
MariaDB
=======

To install MariaDB for your site, see:

    `Official MariaDB Installation Guide <https://mariadb.com/docs/server/mariadb-quickstart-guides/installing-mariadb-server-guide>`_

Configure MariaDB for Moduli Generator
    Assuming an MariaDB has been installed and is operational, we need to install moduli_generator's db schema and
    configure the the user with ALL PRIVILEGES WITH GRANT on the moduli_generator db.

    1. Configure 'moduli_generator'@'%'

**Install Schema**

``moduli_generator.scripts.install_schema`` installs a schema in a database named ``moduli_db`` having three tables, ``moduli``, ``moduli_view``, and ``mod_fl_consts``.

The user ``'moduli_generator'@'%'`` is granted ALL PRIVILEGES on ``'moduli_db'.'*'`` with GRANT. No other access for this user should be allowed.


install_schema privileged_mariadb.cnf --moduli-db-name test_moduli_db --batch

command
    poetry run install_schema

    or

    python -m db.moduli_db_utilities.install_schema:main

.. code-block:: bash

    poetry run install_schema privileged_mariadb.cnf --moduli-db-name test_moduli_db --batch

*response*

.. code-block:: bash

    Installing schema for database: test_moduli_db with MariaDB config file: privileged_mariadb.cnf
    Installing schema for database: test_moduli_db
    Schema installation completed successfully (batch mode)
    Database schema installed successfully