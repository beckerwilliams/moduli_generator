# Default Run Properties

The sole objective of `moduli_generator` is to produce *unique and secure* SSH2 Moduli Files.

The default configuration will produce a complete `/etc/ssh/moduli` file, comprised of 20 moduli for each of 5
key-sizes, `3072`, `4096`, `6144`, `7680`, and `8192` in about 90 hours.

### /etc/ssh/moduli

```bash
    #/etc/ssh/moduli: moduli_generator: 2024-11-15T15:06:25.629025+00:00

    |timestamp    |type|tests|trials|size|generator|moduli|
    |:--------------|:---|:---|:----|:--|:--------------------------------------------------------------------------------|
    |**20241110030855**|2|6|100|3071|2|C8053358B1E47DCB826BA2BCB616739EE826ADB273504CF89F8CF6F5A9946B5576F66A07012DCC10557...|
    |20241110033748|2|6|100|3071|2|C8053358B1E47DCB826BA2BCB616739EE826ADB273504CF89F8CF6F5A9946B5576F66A07012DCC10557...|
```

**Requirements**

- MariaDB installed and Operational
- Two MariaDB Profiles (mysql.cnf) Files:
    - One for DB Initialization (`privileged-mariadb.cnf`)
    - Another for Runtime Operations (`moduli_generator.cnf`)

**Prepare TWO MariaDB User Profiles (mysql.cnf)**

- ~/privileged-mariadb.cnf
    - Specifies privileged user granted `ALL PRIVILEGES WITH GRANT` on the entire installation.
- ~/moduli_generator.cnf
    - username: `moduli_generator`@`%`
    - Specifies restricted user granted `ALL PRIVLEGES ON moduli_db.* WITH GRANT`

During initialization, `~/privileged-mariadb.cnf` will be replaced by `~/.moduli_generator` with the restricted access
profile, `~/.moduli_generator/moduli_generator.cnf`

**ONCE the DB Is Installed:**
Place in *your home directory* the previously prepared mysql.cnf files, privileged-mariadb.cnf, and
moduli_generator.cnf.

# Moduli Generator DB Initialization

## 1. Prepare Mariadb and Locate Moduli Generator User Configuration Files

`~/privilged-mariadb.cnf`, `~/moduli_generator.cnf`

## 2. Initialize DB

### Production Installation

*Build Wheel*

The first task is to build `moduli_generator`'s wheel, and then install in a python virtual environment.

The following script will

- Clone the project
- create and activate a python virtual environment
- install dependencies
- build the python wheel
- copy the resulting wheel `moduli_generator-<x.x.x>-py3-none-any.whl` to your `${HOME}` directory.

```bash
#!/usr/bin/env bash
mkdir mwork
cwd=`pwd`
cd mwork

git clone https://github.com/beckerwilliams/moduli_generator.git
cd moduli_generator
python -m venv .venv
.venv/bin/activate.sh

poetry install
poetry build

wheel_file=$(ls dist/*.whl | cut -d/ -f2)
echo "Moduli Generator Wheel located @ ~/${wheel_file}"
cp dist/*.whl ~/

cd $cwd
rm -rf mwork  # Cleanup transients
```