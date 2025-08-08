# `Moduli Generator`

A Python tool for generating SSH moduli files for secure communication.

### Overview

Moduli Generator creates cryptographically secure prime numbers (moduli) used in SSH Diffie-Hellman key exchange,
formatted in an `ssh/moduli` file, containing 20 moduli each per key lengths 3072, 4096, 6144, 7680, and 8192 bits long.

## Features

- Runs to completion to produce sufficient moduli, twenty (20) moduli/key-length, for a complete /etc/ssh/moduli
- Database integration with MariaDB designed to produce unique moduli and files
- Command-line interface for easy usage
- Performance optimization and testing capabilities
- Comprehensive configuration management

____

## Requirements

### Operating Systems

- MacOsX: Sequoia >=15.5

- FreeBSD: >14.2

- Linux: LTS

- Windows: _not supported_

### O/S Installed Applications

- openssh >=9.9p2 (Provides `ssh-keygen`)

### Python

- mariadb ==1.1.13
- configparser >=7.2.0
- typing-extensions >=4.14.1

### Database

#### MariaDB Version Requirement

    mariadb >=11.4.0

MariaDB is used as the supported replacement for MySql. MariaDB uses the same style of configuration file as does MySql.

Access to the MariaDB Instance is controlled by mariadb user, `'moduli_generator'@'%'`. Moduli Generator provides the
schema to
create and grant to the user `GRANT ALL PRIVILEGES on moduli_db.*`.

____

## Installation Overview

- Verify `MariaDB` Credentials
    - Prepare Credentials for chosen `MariaDB` Instance, both privileged and application owner
    - _Optional (if absent)_: Install `MariaDB`
- Install `Moduli Generator`, from `github`, `PyPi`
- Install `Moduli Generator` SQL Schema
- Create and Grant privileges to Application Owner `'moduli_generator'@'%'`
- Test installation to verify successful installation and operation

____

# `Moduli Generator` Installation

## Install `moduli_generator`

### pre-PyPi Installer Script

Copy and paste `Moduli Generator` Install Script: [_moduli_generator_installer_](command_line_installer.md)

#### from `wheel`

```bash
pip install moduli_generator-<x.x.x>-py3-none-any.whl
```

#### from PyPi

```bash
pip install moduli_generator
```

## Install `Moduli Generator` Database Schema

### Initialize `moduli_generator`

#### Deactivate (if activated) and _re_-activate virtual environment

```bash
deactivate
source .venv/bin/activate
```

_This will assure `moduli_generator's` scripts are found in $PATH_

### Verify that `install_schema` is Available

At the comand line, in your chosen directory, type:

```bash
install_schema -h
```

will respond with the following, indicating `moduli_generator.install_schema` is properly installed:

```bash
usage: install_schema [-h] [--batch] [--moduli-db-name MODULI_DB_NAME] mariadb_cnf

Install SSH Moduli Schema

positional arguments:
  mariadb_cnf           Path to MariaDB configuration file

options:
  -h, --help            show this help message and exit
  --batch               Use batch execution mode for better performance
  --moduli-db-name MODULI_DB_NAME
                        Name of the database to create

```

## MariaDB

After completing the `Moduli Generator` command line install, you are ready for MariaDB Integration.

_If_ you need a MariaDB Database, create one!:

### Official MariaDB Installation Guide

- [MariaDB Installation Guide](https://mariadb.com/docs/server/mariadb-quickstart-guides/installing-mariadb-server-guide)
  _This link will take you **directly** to MariaDB's Installation Guide_

#### Install MacOS X: `brew install mariadbW@11.4>=`

#### Install Linux (LTS): `apt -y install mariadb@>=11.4`

#### Windows: `unsupported`

Initial `MariaDB` configuration _requires_ a user privileged with `ALL PRIVILEGES ON *.* WITH GRANT.
Having previously identified this user and their credentials, 
create a `priviledged_mariadb.cnf` and place it in your `${HOME}` directory.

##### [SAMPLE_privileged_mariadb.cnf](SAMPLE_privileged_mariadb.cnf)

### Install `Moduli Generator` SQL Schema
```bash
install_schema privileged_mariadb.cnf --moduli-db-name test_moduli_db --batch
```

You need Two (2) MariaDB.cnf (.my.sql.conf) Files
In your _working_directory_ create `privileged_mariadb.cnf`. This profile contains `MariaDB privileged user` access
in order to create the necessary database, tables, and views.
Privileged user

With your prepared

```bash
install_schema
```

# Quick Start

```bash
# Display help information
moduli_generator --help
```

## Run to Completion (default config)

```bash
moduli_generator&  # Background Process
```

is equivalent to:

```bash
    moduli_generator \
        --moduli-home ${HOME}/.moduli_generator \
        --key-lengths 3072 4096 6144 7680 8192  \
        --nice_value 15 \ 
        --db_name moduli_db \ 
        --table_name moduli \ 
        --view_name moduli_view \
        --records-per-keylength 20 \
        --mariadb-cnf ${HOME}/.moduli_generator/moduli_generator.cnf
        --moduli-file ssh2-moduli_<current_timestamp> \
        --delete-records-on-moduli-write

```

## Documentation

For comprehensive documentation, please visit our [documentation site](https://moduli-generator.readthedocs.io/) or
browse the `docs/` directory.

## API

- **api**: [API](api.md)

## Repository Structure

- `moduli_generator/` - Main package source code
- `docs/` - Documentation files
- `test/` - Test suite
- `db/` - Database scripts and schema
- `config/` - Configuration management

## Contributing

We welcome contributions! Please see our documentation for guidelines on:

- Performance improvements
- Additional cryptographic features
- Documentation enhancements
- Testing and validation

## Links

- **Repository**: [GitHub](https://github.com/beckerwilliams/moduli_generator)
- **Issues**: [GitHub Issues](https://github.com/beckerwilliams/moduli_generator/issues)
- **Documentation**: [Read the Docs](https://moduli-generator.readthedocs.io/)

## License

Please refer to the LICENSE file for licensing information.