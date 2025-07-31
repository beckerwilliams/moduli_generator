# Moduli Generator

A Python tool for generating SSH moduli files for secure communication.

## Overview

Moduli Generator creates cryptographically secure prime numbers (moduli) used in SSH Diffie-Hellman key exchange. These
moduli are essential for maintaining secure SSH connections and ensuring forward secrecy.

## Features

- Generate SSH moduli files with configurable parameters
- Database integration using MariaDB for moduli storage
- Command-line interface for easy usage
- Performance optimization and testing capabilities
- Comprehensive configuration management

## Installation

```bash
pip install moduli_generator
```

## Quick Start

```bash
# Display help information
moduli_generator --help

# Basic usage example
moduli_generator [options]

# Run to Completion (Defaults)
moduli_generator \
    --key-lengths 3072 4096 6144 7680 8192 \ # default
    --moduli-home ${HOME}/.moduli_generator # default
    
```

## Documentation

For comprehensive documentation, please visit our [documentation site](https://moduli-generator.readthedocs.io/) or
browse the `docs/` directory.

## API

-** api **: API

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