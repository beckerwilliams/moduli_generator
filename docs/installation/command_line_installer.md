# Moduli Generator Command Line Installer

## Pre-Requisites

- OpenSSH >=9.9p2
    - Assure installed at or above the required version
- MariaDB >=11.4
    - Assure `'moduli_generator'@'%'` has been created, and that you have the password available at install

- **MariaDB is Operational, `'moduli_generator'@'%'` has been created and the user's `password` obtained.**

## Installation Overview

The installer script will:

- Prompt the use for the `'moduli_generatort'@'%'` password
- Create and install the MariaDB User Profile, `${MODULI_HOME}/moduli_generator.cnf
- Creates a temporary virtual environment and build the python wheel
- Installs wheel and launches the `moduli_generator` virtual application environment

____

At start, the Installer will prompt the user for the MariaDB user attributes for the `'`moduli_generator'@'%'`,
and create the runtime profile in `${MODULI_HOME}/moduli_generator.cnf`:

```bash
[ Database Configuration ]
Enter MariaDB host [localhost]:            # Default
Enter MariaDB port [3306]:                 # Default
Enter database name [moduli_db]:           # Default
Enter MariaDB username [moduli_generator]: # Default
Enter MariaDB password:  # (YOUR moduli_generator pass word)
✓ Database configuration complete
```

After entering the MariaDB password, the installer will run to completion.
____

## The Installation Script

In the example below, we download the Moduli Generator Command Line Installer from GitHub and move it to the chosen
application home, `${HOME}/moduli_generator`.

- Raw script URL (
  stable): https://raw.githubusercontent.com/beckerwilliams/moduli_generator/HEAD/data/bash_scripts/install_mg.sh
    - [download install_mg (right-click to download)](https://raw.githubusercontent.com/beckerwilliams/moduli_generator/HEAD/data/bash_scripts/install_mg.sh)

- Repository view: https://github.com/beckerwilliams/moduli_generator/blob/HEAD/data/bash_scripts/install_mg.sh

## Open a Terminal session

### Perform the Installation

### Create `Moduli Generator` Application Home

```bash
cd ~
mkdir -p moduli_generator # This is the application home; used as ${CWD} by install_mg.sh
```

### Change to the application build directory

``` bash
cd moduli_generator
```

### Download the installer script

```bash
curl -fsSL -o install_mg.sh \
  https://raw.githubusercontent.com/beckerwilliams/moduli_generator/HEAD/data/bash_scripts/install_mg.sh
```

### Make installer script executable

```bash
chmod +x ./install_mg.sh
```

### Run the install

```bash
./install_mg.sh
```

#### Example Install Reponse Trace:

[Sample Install Response Log](installer_response.md)

If successful, the installation will display the following at completion:

```bash
✓ Runtime installation completed successfully
✓ Installation completed successfully!
To activate the environment, run: source .venv/bin/activate
To test the installation, run: moduli_generator --help
```

When the installer completes, you should have a complete installation of the Moduli Generator application.

____

## Try it Out!

```bash
moduli_generator -h
```


