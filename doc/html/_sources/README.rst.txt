=====================
SSH2 Moduli Generator
=====================

.. image:: https://img.shields.io/badge/python-3.12+-blue.svg
    :target: https://www.python.org/downloads/

.. image:: https://img.shields.io/badge/license-MIT-green.svg
    :target: LICENSE.rst

A command-line utility for generating SSH moduli files used in SSH key exchange processes.

Do `it all`:

.. code-block::

    python -m moduli_generator.cli

At completion, you will find
    ${HOME}/.moduli_generator/
    ${HOME}/.moduli_generator/ssh2-moduli_<timestamp>

Features
--------

- Generate *Unique and Secure*, SSH2 Compliant moduli files
- Mysql/MariaDB integration for storing and managing screened moduli
- Command-line interface for easy automation
- Comprehensive documentation and changelog
- Support standard mysql.cnf connection files
- Statistics and analysis tools

---------------
Getting Started
---------------

Install SSH2 Moduli Generator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pip install moduli_generator


*Response*

.. code-block:: bash

    "tbd : installation response"

Install Moduli_Generator Schema
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Requirements`
    A Running MariaDB SQL Database

=================
Configure MariaDB
=================

To install MariaDB for your site, see:

    `Official MariaDB Installation Guide <https://mariadb.com/docs/server/mariadb-quickstart-guides/installing-mariadb-server-guide>`_


In the provided target MariaDB Instance, **SSH2 Moduli Generator** creates a database, ``moduli_db``, a view ``moduli_view``
, and a constants table ``mod_fl_consts``.

To configure, you will need to prepare Two (2) mysql.cnf files, ``moduli_generator.cnf``, and ``privileged.cnf``. Substitute the <HOST>, <USERNAME>, and <PASSWORD>, with the appropriate ``host``, ``username``, and ``password`` of your <privileged> account into a file named ``privileged.cnf``


    The `moduli_generator` application ``owner`` is configured and limited to this database on the server.

    The `moduli_generator` privileged ``user`` is configured for *installation* of the `moduli_generator` schema and user.

**Configure MariaDB for Moduli Generator**

    Assuming an MariaDB is operational and available, we need to install `moduli_generator`'s db `schema` and
    configure the the user, `moduli_generator`, with ALL PRIVILEGES WITH GRANT on the moduli_generator db.


    ``moduli_generator.scripts.install_schema`` installs a schema in a database named ``moduli_db`` having three tables, ``moduli``, ``moduli_view``, and ``mod_fl_consts``.


A system user `'`<privileged>`'@'%'`, must be granted ALL PRIVILEGES on `'`*`'.'*'` with Grant. This configuration can be deleted after schema install.


.. literalinclude:: SAMPLE_privileged_mariadb.cnf
    :language: bash

The user `'`moduli_generator'@'%`'` is created and granted ALL PRIVILEGES on `'`**moduli_db**`'.'*'` with GRANT. No other access for this user should be allowed.

.. literalinclude:: SAMPLE_moduli_generator.cnf
    :language: bash

1. Configure Moduli Generator User (and Installer Privileged Profile)

    Inputs:
        privilged.cnf, a privileged user account having
            `GRANT ALL PRIVILEGES on moduli_db.* WITH GRANT`

        moduli_generator.cnf, the *will be assigned* an application owner account with
            `GRANT ALL PRIVILEGES on *.* WITH GRANT` with schema installation.

Place both *.cnf files in ${HOME}, and then cut and paste the script below into a terminal session to install schema.

.. code-block:: bash

    # moduli_generator_dir home directory = ${HOME}/moduli_generator
    MODULI_GENERATOR_HOME=${HOME}.moduli_generator
    cp ${HOME}/moduli_generator.cnf ${MODULI_GENERATOR}

    # Install Schema
    python -m db.moduli_db_utilities.install_schema:main \
        --moduli-db-name moduli_db \
        --mariadb-cnf ${HOME}/privileged_mariadb.cnf
        --batch



*response:*

.. code-block:: bash

    Installing schema for database: moduli_db with MariaDB config file: privileged_mariadb.cnf
    Installing schema for database: moduli_db
    Schema installation completed successfully (batch mode)
    Database schema installed successfully

*completion:*

.. code-block:: bash

    rm ${HOME}/privileged_mariadb.cnf


**MODULI_GENERATOR DB Schema**

.. literalinclude:: db/schema/create_db_owner.sql
    :language: sql

**MODULI_GENERATOR CREATE USER Schema**

.. literalinclude:: db/schema/ssh_moduli_schema.sql
    :language: sql
