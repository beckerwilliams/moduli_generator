# Command Line Installation Guide

This guide walks you through installing the Moduli Generator using the command line installer.

## Prerequisites

Before installation, ensure you're platform meets the following requirements:

- Python ≥ 3.12
- OpenSSH ≥ 9.9p2
- MariaDB Client ≥ 11.4
- A MariaDB user account `'moduli_generator'@'%'` with appropriate permissions
- The password for your `'moduli_generator'@'%'` database user

## Installation Process

### Step 1: Download the Installer

Download the installer script from one of these sources:

- Direct
  download: [install_mg.sh](https://raw.githubusercontent.com/beckerwilliams/moduli_generator/HEAD/data/bash_scripts/install_mg.sh) (
  right-click to save)
- Terminal download (using curl):
  ```bash
  curl -fsSL -o install_mg.sh https://raw.githubusercontent.com/beckerwilliams/moduli_generator/HEAD/data/bash_scripts/install_mg.sh
  ```

### Step 2: Create and Use Application Directory

```bash
mkdir -p ~/moduli_generator
cd ~/moduli_generator
```

### Step 3: Prepare and Run the Installer

Make the installer executable and run it:

```bash
chmod +x ./install_mg.sh
./install_mg.sh
```

### Step 4: Configuration

When prompted, enter your database connection details:

```
[ Database Configuration ]
Enter MariaDB host [localhost]:            # Press Enter for default
Enter MariaDB port [3306]:                 # Press Enter for default
Enter database name [moduli_db]:           # Press Enter for default
Enter MariaDB username [moduli_generator]: # Press Enter for default
Enter MariaDB password:                    # Enter your password
```

## What the Installer Does

The installer performs these tasks automatically:

1. Collects database configuration information
2. Creates the database connection profile at `${MODULI_HOME}/moduli_generator.cnf`
3. Creates a temporary virtual environment and builds the Python wheel
4. Installs the wheel and sets up the application environment

## Verification

On successful installation, you'll see:

```
✓ Runtime installation completed successfully
✓ Installation completed successfully!
To activate the environment, run: source .venv/bin/activate
To test the installation, run: moduli_generator --help
```

## Testing Your Installation

Verify your installation works by running:

```bash
moduli_generator -h
```

This should display the help information for the Moduli Generator tool.

## Troubleshooting

If you encounter any issues during installation, check:

- [Sample Installation Log](installation_response.md) for comparison
- That your MariaDB user has the correct permissions
- That all prerequisites are correctly installed

For additional help, please refer to the
project's [GitHub issues page](https://github.com/beckerwilliams/moduli_generator/issues).