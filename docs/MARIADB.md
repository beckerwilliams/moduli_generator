# MariaDB for `Moduli Generator`

The MariaDB codebase is actively supported by MariaDB.com.
It's the preferred replacement for MySQL Database, which is no longer supported.

In the Moduli Generator pre-Install below, we'll

- Install the `Moduli Generator`'s database, tables, and views. (requires _privilged_ db access)

- Create the `Moduli Generator` application user:  `'moduli_generator'@'%'`, and grant it
  `ALL PRIVILEGES ON moduli_db.*`

- Create `Moduli Generator`'s mariadb.cnf file: `${HOME}/.moduli_generator/moduli_generator.cnf`

## Install Mariadb

### Installers

- **All OS**/Official -
  MariaDB.com - [MariaDB Installation Guide](https://mariadb.com/docs/server/mariadb-quickstart-guides/installing-mariadb-server-guide)
- **MacOsX** - homebrew - `brew install mariadb@11.4`
- **FreeBSD >=14.2** - portmaster - `portmaster databases/mariadb114-server`

#### Moduli Generator's User and DB

Moduli Generator will install its database schema into the MariaDB instance indicated by the _privileged_ user's
configuration
file, `${CWD}/privileged_mariadb.cnf`

- Note: The `privileged user` identified in `privileged_mariadb.cnf` at minimum MUST be GRANTED:

  `CREATE`, `CREATE USER`, and `WITH GRANT OPTION` on `*.*`

_For simplicity_, just grant the privileged user the following:

    GRANT ALL ON *.* TO <PRIVILEGED_USER_NAME> WITH GRANT;
    FLUSH PRIVILEGES;

**Privileged MariaDB User Profile**: `${cwd}/privileged_mariadb.cnf`

```priuileged_mariadb.cnf
#
# This group is read both by the client and the server
# use it for options that affect everything, see
# https://mariadb.com/kb/en/configuring-mariadb-with-option-files/#option-groups
#
[client]
host                                = <HOSTNAME>
port	                            = 3306
socket	                            = /var/run/mysql/mysql.sock
password                            = <PASSWORD>
user                                = <USERNAME>
ssl                                 = true
```

**Moduli Generator Application Owner**: `${HOME}/.moduli_generator/moduli_generator.cnf`

```moduli_generator.cnf
#
# This group is read both by the client and the server
# use it for options that affect everything, see
# https://mariadb.com/kb/en/configuring-mariadb-with-option-files/#option-groups
#
[client]
host                                = <HOSTNAME>
port	                            = 3306
socket	                            = /var/run/mysql/mysql.sock
password                            = <PASSWORD>
user                                = moduli_generator
ssl                                 = true
```

_**Replace**_ `<HOSTNAME>`, `<USERNAME>`, and `<PASSWORD>` above, with credentials as configured in your MariaDB
Instance.

## Install `Moduli Generator` Schema

Pre-requisites:

- Python Virtual Environment: ${cwd}/.venv
- `moduli_generator` installed in virtual environment

Navigate to your chosen runtime directory (where .venv is installed): `${cwd}`
At the command line, type

```bash
source .venv/bin/activate
install_schema
```

## Configure MariaDB for Moduli Generator

### The `'moduli_generator'@'%'` user

### Pre-Requisites

MariaDB >=11.8.2

#### Install Moduli Generator Schema

```bash
python -m moduli_generator.scripts.install_schema
```

or from the virtual environment

```bash
install_schema
```

Assuming a MariaDB has been installed and is operational, we need to install moduli_generator's db schema and configure
the user with ALL PRIVILEGES WITH GRANT on the moduli_generator db.

1. Configure 'moduli_generator'@'%'

## Install Schema

`moduli_generator.scripts.install_schema` installs a schema in a database named `moduli_db` having three tables,
`moduli`, `moduli_view`, and `mod_fl_consts`.

The user `'moduli_generator'@'%'` is granted ALL PRIVILEGES on `'moduli_db'.'*'` with GRANT. No other access for this
user should be allowed.

install_schema privileged_mariadb.cnf --moduli-db-name test_moduli_db --batch

## Command

```bash
poetry run install_schema
```