# `Moduli Generator`

## Overview

Moduli Generator is a Python tool designed for generating SSH moduli files. SSH moduli are used in the Diffie-Hellman
key exchange process to provide secure communication channels.

____

## Features

- Generate SSH moduli files with configurable parameters
- Command-line interface for easy usage
- Database integration for storing and managing moduli
- Performance optimization and testing capabilities
- Comprehensive configuration management

### What does it do?

- Produces /etc/ssh/moduli
    - 20 unique moduli for each of key lengths 3072, 4096, 6144, 7680, and 8192
    - 100 unique moduli per file

____

## Moduli Generator Home (Default) Directory

MODULI_GENERATOR_HOME = ${HOME}/.moduli_generator

- Linux: `${HOME}/.moduli_generator`
- macOS: `${HOME}/.moduli_generator`
- Windows: `not supported`

____

## Moduli Generator Database Profile

- All OS: `${MODULI_GENERATOR_HOME}/moduli_generator.cnf`

____

## Moduli Generator Runtime Logfile

- Runtime Log: `${MODULI_GENERATOR_HOME}/.logs/moduli_generator.log`

____

## Produced SSH Moduli (/etc/ssh/moduli)

`${MODULI_GENERATOR_HOME}/ssh2-moduli_<timestamp>`

```bash
# Installations
cp ssh-moduli_<timestamp> /etc/ssh/moduli
```

____

## Repository

This project is hosted on GitHub: [
`beckerwilliams/moduli_generator`](https://github.com/beckerwilliams/moduli_generator)

## Getting Help

If you encounter any issues or have questions, please:

1. Check the documentation sections above
2. Visit the [GitHub Issues](https://github.com/beckerwilliams/moduli_generator/issues) page
3. Review the existing documentation files for detailed technical information