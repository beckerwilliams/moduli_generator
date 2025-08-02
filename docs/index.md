# Moduli Generator

Welcome to the Moduli Generator documentation!

## Overview

Moduli Generator is a Python tool designed for generating SSH moduli files. SSH moduli are used in the Diffie-Hellman
key exchange process to provide secure communication channels.

## Features

- Generate SSH moduli files with configurable parameters
- Database integration for storing and managing moduli
- Command-line interface for easy usage
- Performance optimization and testing capabilities
- Comprehensive configuration management

## Quick Start

To get started with Moduli Generator:

1. Install the package:
   ```bash
   pip install moduli_generator
   ```

2. Run the basic command:
   ```bash
   moduli_generator --help
   ```

`moduli_generator` home directory

   ```bash
   moduli_home                 default: ${HOME}/.moduli_generator
   - moduli_generator.cnf      moduli_generator user profile, default: "moduli_generator.cnf"
   - .logs                     log directory, permanent
       - moduli_generator.log  runtime log, default: "moduli_home/.logs/moduli_generator.log"
   - .candidates               Internal generated candidate moduli, Transient
   - .moduli                   Internal Screened and Tested Moduli, Transient
   ```

The internal directories `.candidates` and `.moduli` are the locations for the working storage of
`ssh-keygen -m generate` and `ssh-keygen -m screen`.

## Documentation Structure

- **[About](about.md)** - Learn more about the project and its purpose
- **[Analysis](moduli_generator_analysis_and_improvements.md)** - Technical analysis and improvements
- **[Project Improvements](project_improvement_recommendations.md)** - Recommended enhancements
- **[Refactoring Summary](REFACTORING_SUMMARY.md)** - Code refactoring documentation

## Repository

This project is hosted on GitHub: [beckerwilliams/moduli_generator](https://github.com/beckerwilliams/moduli_generator)

## Getting Help

If you encounter any issues or have questions, please:

1. Check the documentation sections above
2. Visit the [GitHub Issues](https://github.com/beckerwilliams/moduli_generator/issues) page
3. Review the existing documentation files for detailed technical information