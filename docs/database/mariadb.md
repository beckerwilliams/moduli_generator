# MariaDB for `Moduli Generator`

The MariaDB codebase is actively supported by MariaDB.com.
It's the preferred replacement for MySQL Database, which is no longer supported.

In the Moduli Generator pre-Install below, we'll

- Create `Moduli Generator`'s **`mariadb.cnf`** file: `${HOME}/.moduli_generator/moduli_generator.cnf`

- Install the `Moduli Generator`'s database, tables, and views. (requires _privilged_ db access)

- Create the `Moduli Generator` application user:  `'moduli_generator'@'%'`, and grant it
  `ALL PRIVILEGES ON moduli_db.*`

## Install MariaDB

### Installers

- **All OS**/Official -
  MariaDB.com - [MariaDB Installation Guide](https://mariadb.com/docs/server/mariadb-quickstart-guides/installing-mariadb-server-guide)
- **MacOsX** - homebrew - `brew install mariadb@11.4`
- **FreeBSD >=14.2** - portmaster - `portmaster databases/mariadb114-server`

## Configuring MariaDB for `Moduli Generator`

### Moduli Generator's User and DB

Moduli Generator will install its database schema into the MariaDB instance indicated by the _privileged_ user's
configuration
file, `${CWD}/privileged_mariadb.cnf`

- Note: The `privileged user` identified in `privileged_mariadb.cnf` at minimum MUST be GRANTED:

  `CREATE`, `CREATE USER`, and `WITH GRANT OPTION` on `*.*`

**Privileged MariaDB User Profile (temporary/configuration only)**: `${cwd}/privileged_mariadb.cnf`

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

____

## Install `Moduli Generator` Schema

### Pre-requisites

- Python Virtual Environment: ${cwd}/.venv
- `moduli_generator` installed in virtual environment

### Install

Navigate to your chosen runtime directory (where .venv is installed): `${cwd}`
At the command line, type

```bash
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

MariaDB >=11.8.2

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