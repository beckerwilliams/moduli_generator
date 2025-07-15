====================
Database Integration
====================


**MariaDB Official** Installation, Configuration, and Administration Documentation
    `Maria DB Documentation <https://mariadb.com/docs/server>`_


Install Moduli Generator DB Schema
    - ``python -m db.scripts.install_schema``


1. Configure the database connection in ``moduli_generator.cnf``
`<SAMPLE_moduli_generator.cnf>`_


3. Timestamps are stored in compressed format (no punctuation or spaces)

Retrieving Moduli from Database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When using the ``--write`` option, the generator will:

- Verify sufficient records exist for each key size (minimum 80 per size)
- Only create the moduli file if all sizes have enough entries
- Randomly select entries from the database to create a balanced moduli file


**moduli_generator** uses a mariadb database as mysql for storage of moduli for moduli file creation.
We use Mariadb in lieu of mysql as Mariadb is still under support. Mysql's support has expired.


Maria DB's Official Documentation Site
    `MariaDB Documentation <https://mariadb.com/docs/server>`_.




:privileged_mariadb.cnf: `<privileged_mariadb.cnf>`_

Installation of Mariadb
    - Mac OS X
        (Homebrew): ``brew install mariadb``
    - Freebsd
        (FreshPorts): ``portmaster databases/mariadb104-server``

moduli_generator.cnf
    Is the name of the MariaDB (or mysql) Moduli Generator User configuration file.

    To use, modify <HOST>, <USER>, and <PASSWORD> in ``${HOME}/.moduli_generator/moduli_generator.cnf`` to reflect the user.

Configuration
    From the root (super) user account on your mariadB
        mariadb