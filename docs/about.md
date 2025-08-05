# About Moduli Generator

`Moduli Generator` simply produces _unique_ SSH2 Moduli files (`/etc/ssh/moduli`),
with a single command, `moduli_generator.`

`Moduli Generator` uses Open SSH2's `ssh-keygen -m generate` and `ssh-keygen -m screen` under-the-covers, effectively
managing the process of candidate generation, screening, and assembly into high quality moduli files.

_**IFF you've read**_ the Caveat Emptor below, and _**still**_ want to generate your own moduli files,
this is the tool for you.

### Caveat Emptor

#### Embrace Modern, Post-Quantum Safe SSH Protocols

If you have a _secure_ OpenSSH installation, you're running a version at least OpenSSH v. 9.9p2 or greater,
you _should_ be configured to use a secure protocol, like `Kex=sntrup761x25519-sha512@openssh.com`,
rather than Diffie-Hellman Group Exchange.

Unless you have _legacy clients_ back-leveled and incapable of OpenSSH quantum safe protocols,
**you do not need** `Moduli Generator`

_**If you _have_ legacy clients ssh clients**_, and require _**Unique, Secure, and Complete**_ /etc/ssh/moduli files,
`Moduli Generator`
was made for you.

## Technical Overview

The Moduli Generator provides:

### Core Functionality

- **Moduli Generation**: Creates cryptographically secure prime numbers for use as Diffie-Hellman group exchange
- **Database Integration**: Stores and manages generated moduli using MariaDB
- **Performance Optimization**: Efficient implementation for large-scale moduli generation
- **Candidate Restart**: For efficient restart of interrupted candidate screening.
- **Database Moduli Stats**: Basic Inventory of DH GEX Moduli by Key Length

### Architecture

- **Command-Line Interface**: Easy-to-use CLI for interactive and batch operations
- **Modular Design**: Well-structured codebase with separate modules for different functionalities
- **Database Schema**: Comprehensive database design for moduli storage and retrieval
- **Testing Framework**: Extensive test suite ensuring reliability and correctness

## Use Cases

The Moduli Generator is suitable for:

- **System Administrators**: Managing SSH security infrastructure
- **Security Engineers**: Implementing custom SSH configurations
- **Researchers**: Studying cryptographic properties of SSH key exchange
- **Organizations**: Maintaining secure SSH environments at scale

## Development and Maintenance

This project is actively maintained and includes:

- Comprehensive documentation and analysis
- Regular refactoring and improvements
- Performance testing and optimization
- Database integration and schema management

## Contributing

The project welcomes contributions in areas such as:

- Performance improvements
- Additional cryptographic features
- Documentation enhancements
- Testing and validation

For more information about contributing, please visit
the [GitHub repository](https://github.com/beckerwilliams/moduli_generator).

## License and Support

Please refer to the project repository for licensing information and support resources.