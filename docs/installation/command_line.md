# Moduli Generator Command Line Installer

## Installation Overview

1. Create an application directory, for example `${HOME}/moduli_generator`
2. Download the installation script and save it as `${HOME}/moduli_generator/install_mg.sh`
3. Make the script executable: `chmod +x ${HOME}/moduli_generator/install_mg.sh`
4. Execute the installer
5. Verify installation
6. Test run

## Prepare Command Line Installer

Download the Moduli Generator Command Line Installer from GitHub and move it to your chosen directory, e.g.
`${HOME}/moduli_generator`.

- Raw script URL (
  stable): https://raw.githubusercontent.com/beckerwilliams/moduli_generator/HEAD/data/bash_scripts/install_mg.sh
- Repository view: https://github.com/beckerwilliams/moduli_generator/blob/HEAD/data/bash_scripts/install_mg.sh

```bash
# Create an application directory in your home directory (example - can be any directory)
cd ~
mkdir -p moduli_generator # This is the application home; used as ${CWD} by install_mg.sh

# Change to the build directory for the installation wheel
cd moduli_generator

# Download the installer script and save it in ${HOME}/moduli_generator
curl -fsSL -o install_mg.sh \
  https://raw.githubusercontent.com/beckerwilliams/moduli_generator/HEAD/data/bash_scripts/install_mg.sh

# Make executable
chmod +x ./install_mg.sh

# Run the install
./install_mg.sh
```

When the installer completes, you should have a complete installation of the Moduli Generator application.

Example installation response: [installer_response.md](installer_response.md)

____

### Command Line Installer

If you prefer manual steps, create the file `${HOME}/moduli_generator/install_mg.sh` using the contents of the script
above.

### Example Installer Trace

See: [installer_response.md](installer_response.md)

