===============================
SSH2 Moduli Generator
===============================

.. image:: https://img.shields.io/badge/python-3.12+-blue.svg
    :target: https://www.python.org/downloads/

.. image:: https://img.shields.io/badge/license-MIT-green.svg
    :target: LICENSE.rst

A command-line utility for generating SSH moduli files used in SSH key exchange processes.

Does *it all* with this python file:

.. code-block:: bash

    #!/usr/bin/env python
    from moduli_generator import ModuliGenerator

    def doItAll():
        """
        The simplest invocation with which to create a moduli file
        """
        ModuliGenerator()
            .generate_moduli()
            .save_moduli()
            .store_moduli()
            .write_moduli()

    if __name__ == "__main__":
        doItAll()



Or from an installation of moduli_generator's python wheel, executed from the command line:

.. code-block::

    python -m moduli_generator.cli

At completion, you will find
    ${HOME}/.moduli_generator/


Features
--------

- Generate *Unique and Secure*, SSH2 Compliant moduli files
- Mysql/MariaDB integration for storing and managing screened moduli
- Command-line interface for easy automation
- Comprehensive documentation and changelog
- Support standard mysql.cnf connection files
- Statistics and analysis tools

Installation
------------

Tasks
    - install Poetry application
    - clone the Git repository
    - create a Python Virtual Environment
    - install moduli_generator
    - Prepare and locate mysql.cnf (moduli_generator.cnf)

Install Poetry Application
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    MacOSX: Homebrew: brew install poetry
    Linux: apt -y install poetry, apk install poetry, dpkg install poetry
    Freebsd: FreshPorts: portmaster -y --no-confirm devel/py-poetry

Clone Repository
~~~~~~~~~~~~~~~~

.. code-block:: bash

    git clone https://github.com/beckerwilliams/moduli_generator.git

*Response*

.. code-block:: bash

        [freebsd-14.3.0] ron% git clone https://github.com/beckerwilliams/moduli_generator.git
            Cloning into 'moduli_generator'...
            remote: Enumerating objects: 707, done.
            remote: Counting objects: 100% (113/113), done.
            remote: Compressing objects: 100% (74/74), done.
            remote: Total 707 (delta 54), reused 66 (delta 37), pack-reused 594 (from 1)
            Receiving objects: 100% (707/707), 34.89 MiB | 63.46 MiB/s, done.
            Resolving deltas: 100% (358/358), done.


Create Python Virtual Envionrment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: bash

    cd moduli_generator
    python -m venv .venv
    pip install pip --upgrade
    poetry install

*Response*

.. code-block:: bash

        Installing dependencies from lock file

        Package operations: 27 installs, 0 updates, 0 removals

          - Installing certifi (2025.7.9)
          - Installing charset-normalizer (3.4.2)
          - Installing idna (3.10)
          - Installing markupsafe (3.0.2)
          - Installing urllib3 (2.5.0)
          - Installing alabaster (0.7.16)
          - Installing babel (2.17.0)
          - Installing docutils (0.21.2)
          - Installing imagesize (1.4.1)
          - Installing jinja2 (3.1.6)
          - Installing packaging (25.0)
          - Installing pygments (2.19.2)
          - Installing requests (2.32.4)
          - Installing snowballstemmer (3.0.1)
          - Installing sphinxcontrib-applehelp (2.0.0)
          - Installing sphinxcontrib-devhelp (2.0.0)
          - Installing sphinxcontrib-htmlhelp (2.1.0)
          - Installing sphinxcontrib-jsmath (1.0.1)
          - Installing sphinxcontrib-qthelp (2.0.0)
          - Installing sphinxcontrib-serializinghtml (2.0.0)
          - Installing sphinx (7.4.7)
          - Installing sphinxcontrib-jquery (4.1)
          - Installing configparser (7.2.0)
          - Installing poetry-core (2.1.3)
          - Installing toml (0.10.2)
          - Installing sphinx-rtd-theme (3.0.2)
          - Installing mariadb (1.1.13)

        Installing the current project: moduli_generator (2.1.10)

Test Core Access
~~~~~~~~~~~~~~~~

.. code-block:: bash

    python -m moduli_generator.cli -h

*Response*

    .. code-block:: bash


            usage: moduli_generator [-h] [--key-lengths KEY_LENGTHS [KEY_LENGTHS ...]] [--moduli-home MODULI_HOME] [--candidates-dir CANDIDATES_DIR] [--moduli-dir MODULI_DIR] [--log-dir LOG_DIR] [--mariadb-cnf MARIADB_CNF] [--nice-value NICE_VALUE]
                                    [--records-per-keylength RECORDS_PER_KEYLENGTH] [--delete-records-on-moduli-write DELETE_RECORDS_ON_MODULI_WRITE]

            Moduli Generator - Generate and manage secure moduli for cryptographic operations

            options:
              -h, --help            show this help message and exit
              --key-lengths KEY_LENGTHS [KEY_LENGTHS ...]
                                    Space-separated list of key lengths to generate moduli for (default: (3072, 4096, 6144, 7680, 8192))
              --moduli-home MODULI_HOME
                                    Base directory for moduli generation and storage (default: /Users/ron/.moduli_generator)
              --candidates-dir CANDIDATES_DIR
                                    Directory to store candidate moduli (relative to moduli-home) (default: .candidates)
              --moduli-dir MODULI_DIR
                                    Directory to store generated moduli (relative to moduli-home) (default: .moduli)
              --log-dir LOG_DIR     Directory to store log files (relative to moduli-home) (default: .logs)
              --mariadb-cnf MARIADB_CNF
                                    Path to MariaDB configuration file (relative to moduli-home) (default: moduli_generator.conf)
              --nice-value NICE_VALUE
                                    Process nice value for CPU inensive operations (default: 15)
              --records-per-keylength RECORDS_PER_KEYLENGTH
                                    Number of moduli per key-length to capture in each produced moduli file (default: 20)
              --delete-records-on-moduli-write DELETE_RECORDS_ON_MODULI_WRITE
                                    Delete records from DB written to moduli file (default: False)

Quick Start
-----------



Command Line Tools
------------------

The package provides several command-line utilities:

- ``moduli_generator.cli`` - Main moduli generation tool
- ``db_moduli_stats`` - Database statistics and analysis
- ``write_moduli`` - Write moduli to file
- ``install_schema`` - Install database schema

Basic usage
~~~~~~~~~~~

Default Run includes keysizes 3072, 4096,  6144, 7680, and 8192.
Will produce enough moduli for ONE complete Moduli File (about 20 moduli/keysize)
It will take 5-7 days on a 4-core i7.

.. code-block:: bash

    # Default Invocation will produce 1 File of 20 moduli per key size
    python -m moduli_generator.cli

    # Is Equivalent to
    python -m moduli_generator.cli --key-sizes 3072 4096  6144 7680 8192

**With database connection file (moduli_generator.cnf)**

.. code-block:: bash

    python -m moduli_generator.cli --config <path to your mysql.cnf>

**View current db moduli counts by key-size**

.. code-block:: bash

    python -m db.scripts.moduli_stats

..

*Response*

.. code-block:: bash

    Size: #Records
    3071: 1084
    4095: 213
    6143: 148
    7679: 58
    8191: 44

MariaDB Configuration
---------------------

To install MariaDB for your site, see:
    `Official MariaDB Installation Guide <https://mariadb.com/docs/server/mariadb-quickstart-guides/installing-mariadb-server-guide>`_

**Install Schema**

The ``moduli_generator`` module can installs schema in a database named ``moduli_db``, and having three tables, ``moduli``, ``moduli_view``, and ``mod_fl_consts``.

The user, ``moduli_generator``, should have full access to ``moduli_db.moduli``, ``moduli_db.moduli_view``

The tool uses a configuration file (``moduli_generator.cnf``) to customize mysql or mariadb connection parameters.

The default location for your ``moduli_generator.cnf`` is in the root configuration directory (default: ${HOME}/.moduli_generator)

**Sample Mysql CNF**

- Replace <HOSTNAME> with your db's hostname
- Replace <PASSWORD> with the password for `'moduli_generator'@'%'`

.. code-block:: bash

    # This group is read both by the client and the server
    # use it for options that affect everything, see
    # https://mariadb.com/kb/en/configuring-mariadb-with-option-files/#option-groups
    #
    [client]
    host     = <HOSTNAME>
    port     = 3306
    socket   = /var/run/mysql/mysql.sock
    password = <PASSWORD>
    user     = moduli_generator
    database = moduli_db
    ssl      = true




.. tbd - Need to output the Sample

Database Integration
--------------------

The tool supports MariaDB for storing and managing moduli. Use the ``install_schema`` command to set up the database schema.

Development
-----------

This project uses Poetry for dependency management. To set up a development environment:

.. code-block:: bash

    git clone https://github.com/beckerwilliams/moduli_generator.git
    cd moduli_generator
    poetry install

Requirements
------------

- Python 3.12+
- MariaDB (for database features)
- Poetry (for development)

License
-------

This project is licensed under the MIT License - see the ``LICENSE.rst`` file for details.

Contributing
------------

Contributions are welcome! Please see the contributing guidelines in the documentation.

Links
-----

- **Homepage**: https://github.com/beckerwilliams/moduli_generator
- **Documentation**: https://github.com/beckerwilliams/moduli_generator/README.rst
- **Repository**: https://github.com/beckerwilliams/moduli_generator.git
- **Issues**: https://github.com/beckerwilliams/moduli_generator/issues

Author
------

Ron Williams <becker.williams@gmail.com>