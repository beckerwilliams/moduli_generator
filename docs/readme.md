# Moduli Generator

## QuickStart

A Python tool for generating SSH moduli files for secure communication.

### Overview

Moduli Generator creates cryptographically secure prime numbers (moduli) used in SSH Diffie-Hellman key exchange,
formatted in an `ssh/moduli` file, containing 20 moduli per key lengths 3072, 4096, 6144, 7680, and 8192 bits long.

## Features

- Generate SSH moduli files with configurable parameters
- Database integration using MariaDB for moduli storage
- Command-line interface for easy usage
- Performance optimization and testing capabilities
- Comprehensive configuration management

## Requirements

#### Operating Systems

- MacOsX:

  Sequoia >=15.5


- FreeBSD:

  FreeBSD >=14.2

- Linux:

  Debian, RHEL, SLES, Ubuntu

- Windows:

  _not supported_

#### O/S Installed Applications

- openssh>=9.9p2

#### Python

- mariadb==1.1.13
- configparser>=7.2.0
- typing-extensions>=4.14.1,<5.0.0
- mkdocstrings[python]>=0.30.0,<0.31.0,
- black>=25.1.0,<26.0.0"

### Database

#### MariaDB Version Requirement

    mariadb >=11.8.2

MariaDB is used as the supported replacement for MySql. MariaDB uses the same style of configuration file as does MySql.

Access to the MariaDB Instance is controlled by user, `'moduli_generator'@'%'`. Moduli Generator provides the schema to
creates the user, granting the user with `GRANT ALL PRIVILEGES on moduli_db.*`.

##### MariaDB Installation Guide

- [MariaDB Installation Guide](https://mariadb.com/docs/server/mariadb-quickstart-guides/installing-mariadb-server-guide)
  _This link will take you **directly** to MariaDB's Installation Guide_

____

##### Preparing MariaDB for Moduli Generator

[Preparing the MariaDB Instance](MARIADB.md)

## Installation Overview

- Install `Moduli Generator`, from `PyPi` or `Wheel`
- Prepare Credentials for chosen MariaDB Instance, both privileged and application owner
- Install `Moduli Generator` SQL Schema
- Create and Grant privileges to Application Owner `'moduli_generator'@'%'`
- Test install to verify successful operation


1. Create, activate, and update `python` virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install pip --upgrade
```

### Install `moduli_generator` from `wheel`

```bash
pip install moduli_generator-<x.x.x>-py3-none-any.whl
```

### Install `moduli_generator` (PyPi)

```bash
pip install moduli_generator
```

### Initialize `moduli_generator`

#### Deactivate (if activated) and _re_-activate virtual environment

```bash
deactivate
source .venv/bin/activate
```

_This will assure `moduli_generator`'s scripts are available in your $PATH_

### Test initial install

```

```

### Install `moduli_generator` SQL Schema

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