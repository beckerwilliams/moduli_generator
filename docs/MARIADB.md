# MariaDB for Moduli Generator

## Overview

Moduli Generator uses MariaDB for database storage. This guide will help you set up and configure MariaDB for use with
Moduli Generator.

____

## Install MariaDB

- **All OS** (
  Official): [MariaDB Installation Guide](https://mariadb.com/docs/server/mariadb-quickstart-guides/installing-mariadb-server-guide)
- **MacOS**: `brew install mariadb@11.4`
- **FreeBSD >=14.2**: `portmaster databases/mariadb114-server`

____

## Configuration Files

### Privileged User Configuration (Temporary)

Location: `${cwd}/privileged_mariadb.cnf`

```ini
[client]
host = <HOSTNAME>
port = 3306
socket = /var/run/mysql/mysql.sock
password = <PASSWORD>
user = <USERNAME>
ssl = true
```

### Moduli Generator Application Configuration

Location: `${HOME}/.moduli_generator/moduli_generator.cnf`

```ini
[client]
host = <HOSTNAME>
port = 3306
socket = /var/run/mysql/mysql.sock
password = <PASSWORD>
user = moduli_generator
ssl = true
```

> Replace `<HOSTNAME>`, `<USERNAME>`, and `<PASSWORD>` with your actual MariaDB credentials.

____

## Setup Process

### Prerequisites

- Python Virtual Environment: `${cwd}/.venv`
- `moduli_generator` installed in virtual environment

### Install Database Schema

```bash
source .venv/bin/activate
install_schema <privileged_mariadb.cnf> --moduli-db-name moduli_db
```

This will create:

- A database named `moduli_db`
- Tables: `moduli`, `mod-fl-consts`, and `moduli_archive`
- A view: `moduli_view`

### Create Application User

You can create the user manually with:

```sql
CREATE USER IF NOT EXISTS 'moduli_generator'@'%'
IDENTIFIED BY '<MODULI_GENERATOR_PASSWORD>'
WITH MAX_QUERIES_PER_HOUR 500
MAX_CONNECTIONS_PER_HOUR 100
MAX_UPDATES_PER_HOUR 200
MAX_USER_CONNECTIONS 50;
GRANT ALL PRIVILEGES ON 'moduli_db.*' TO 'moduli_generator'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

Alternatively, use the provided script:

```bash
python -m moduli_generator.scripts.install_schema
```

or simply:

```bash
install_schema
```

____

## Requirements

- MariaDB >=11.8.2

____

## Verification

Once setup is complete, Moduli Generator will be able to connect to the database using the created user and schema.