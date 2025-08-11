# MariaDB for `Moduli Generator`

## Installations and Configuration

### Pre-requisites

- **Initial, Pre-MariaDB Integration Installation of [Moduli Generator](../installation/command_line_installer.md).**

The MariaDB User Spec `${MODULI_HOME}/moduli_generator.cnf` is the _runtime_ owner of the application and its database.
It is limited to `Moduli Generator`'s database, `moduli_db`, and it's associated tables and views.

To bootstrap, we need a MariaDB `priviliged` or `administrative` user, granted privileges to create the `moduli_db`
database, tables, and views, and to create the `moduli_generator` application user.

The script below, `install_schema`, will prompt for the `privileged` user's `name` and `password`. It relies on the
client connection parameters created in the [Command Line Installer](../installation/command_line_installer.md) to
obtain the
balance of MariaDB configuration parameters before attemtping installation of `moduli_generator`'s database or user.

____

## MariaDB

The MariaDB codebase is actively supported by MariaDB.com.
It's the preferred replacement for MySQL Database, which is no longer supported.

The `install_schema` script below will:

- Use `Moduli Generator`'s previously created  **`mariadb.cnf`**: `${HOME}/.moduli_generator/moduli_generator.cnf`

- Install the `Moduli Generator`'s database, tables, and views. (requires _privilged_ db access credentials)

- Create the `Moduli Generator` application user:  `'moduli_generator'@'%'`, and grant it
  `ALL PRIVILEGES ON moduli_db.*`

## Install MariaDB

### Installers

- **All OS**/Official -
  MariaDB.com - [MariaDB Installation Guide](https://mariadb.com/docs/server/mariadb-quickstart-guides/installing-mariadb-server-guide)
- **MacOsX** - homebrew - `brew install mariadb@11.4`
- **FreeBSD >=14.2** - portmaster - `portmaster databases/mariadb114-server`

____

## Configuring MariaDB for `Moduli Generator`

### Moduli Generator's User and DB

Moduli Generator will install its database schema into the MariaDB instance indicated by the _privileged_ user's
configuration
file, `${CWD}/privileged_mariadb.cnf`

- Note: The `privileged user` identified in `privileged_mariadb.cnf` at minimum MUST be GRANTED:

  `CREATE`, `CREATE USER`, and `WITH GRANT OPTION` on `*.*`


**Moduli Generator Application Owner**: `${HOME}/.moduli_generator/moduli_generator.cnf`

This profile is created during the [Command Line Installer](../installation/command_line_installer.md) steps.
```moduli_generator.cnf
#
# This group is read both by the client and the server
# use it for options that affect everything, see
# https://mariadb.com/kb/en/configuring-mariadb-with-option-files/#option-groups
#
[client]
host                                = <actual.hostname.hostname.provided.by.installer>
port                                = 3306
socket	                            = /var/run/mysql/mysql.sock
user                                = moduli_generator
password                            = <actual.password.provided.by.installer>
ssl                                 = true
```

____

## Install `Moduli Generator` Schema

### Pre-requisites

- [Command_Line_installer](../installation/command_line_installer.md)
- `${HOME}/.moduli_generator/moduli_generator.cnf` exists after command line installer
- `username` and `password` for administrative user.

### Install

Navigate to your chosen runtime directory (where .venv is installed): `${cwd}`
At the command line, type

```bash
cd ${HOME}/moduli_generator
source .venv/bin/activate
install_schema <privileged_mariadb.cnf> --moduli-db-name moduli_db
```

Upon successful completion, you will observe a new MariaDB database named `moduli_db`, having tables `moduli`,
`mod-fl-consts`,
and
`moduli_archive`, and a view named `moduli_view`. At which point, **You're Live!**

____

## Create `Moduli Generator` Application Owner

### The `'moduli_generator'@'%'` user

You can create the user manually, from a privileged account, with the following SQl:

```mysql
CREATE USER IF NOT EXISTS 'moduli_generator'@'%'
IDENTIFIED BY '<MODULI_GENERATOR_PASSWORD>'
WITH MAX_QUERIES_PER_HOUR 500
MAX_CONNECTIONS_PER_HOUR 100
MAX_UPDATES_PER_HOUR 200
MAX_USER_CONNECTIONS 50;
GRANT ALL PRIVILEGES ON 'moduli_db.*' TO 'moduli_generator'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

Replace '<MODULI_GENERATOR_PASSWORD>' with your chosen `moduli_generator` user password.

### Pre-Requisites

MariaDB >=11.4.2

#### Install Moduli Generator Schema

```bash
python -m moduli_generator.scripts.install_schema
```

or from the virtual environments command line

```bash
install_schema
```

# Success

Once the `Moduli Generator` application user `moduli_generator`@`%` has been created, and the schema succesfully
installed, you're ready for `Moduli Generator` to connect.