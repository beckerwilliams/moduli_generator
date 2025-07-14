MariaDB
====

To install MariaDB for your site, see:

    `Official MariaDB Installation Guide <https://mariadb.com/docs/server/mariadb-quickstart-guides/installing-mariadb-server-guide>`_

**Install Schema**

The *moduli_generator* installs a schema in a database named *moduli_db* having three tables, *moduli*, *moduli_view*, and *mod_fl_consts*
user should have full access to 'moduli_db'.'moduli', 'moduli_db'.'moduli_view'.

It has one user, `'moduli_generator'@'%'`

The tool uses a configuration file (``moduli_generator.cnf``) to customize generation parameters.
A sample configuration file is provided as ``SAMPLE_moduli_generator.cnf``.

The default location for your moduli_generator.cnf is the configuration directory (default: ~/.moduli_generator)
