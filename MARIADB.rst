MariaDB
====

To install MariaDB for your site, see:

    `Official MariaDB Installation Guide <https://mariadb.com/docs/server/mariadb-quickstart-guides/installing-mariadb-server-guide>`_

**Install Schema**

``moduli_generator.scripts.install_schema`` installs a schema in a database named ``moduli_db`` having three tables, ``moduli``, ``moduli_view``, and ``mod_fl_consts``.

The user ``'moduli_generator'@'%'`` is granted ALL PRIVILEGES on ``'moduli_db'.'*'`` with GRANT. No other access for this user should be allowed.


