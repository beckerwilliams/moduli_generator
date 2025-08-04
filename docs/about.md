# About Moduli Generator

## What is Moduli Generator?

### Caveat Emptor

Embrace Modern, Post-Quantum Safe SSH Protocols**

For enhanced security, consider adopting modern SSH key exchange protocols like ECDH (Elliptic Curve Diffie-Hellman) or
post-quantum algorithms such as CRYSTALS-Kyber, instead of relying on traditional Diffie-Hellman with /etc/ssh/moduli
files. These advanced protocols offer stronger protection against emerging threats, including quantum computing risks,
ensuring your connections remain secure and future-proof.

Consider updating your SSH configurations to prioritize these safer alternatives.

____

If you have a _secure_ OpenSSH installation, you're running version at least OpenSSH v. 9.9p2 or greater,
you _should_ be configured to use a secure protocol, like `Kex=sntrup761x25519-sha512@openssh.com`,
rather than Diffie Hellman Exchange protocol.

Unless you have _legacy clients_ back-leveled and incapable of OpenSSH quantum safe protocols,
you **do not need** `Moduli Generator`

If you _have_ legacy clients, and require _**Unique, Secure, and Complete**_ /etc/ssh/moduli files, `Moduli Generator`
was made for you.

## Why Moduli Generator, I understand it uses `ssh-keygen` under the covers?

OpenSSH's `ssh-keygen` is a _high performance, fit for purpose_ moduli generator. However, ssh-keygen provides
two methods, one to generate potential moduli candidates, and a second to screen and test those moduli for primality.

Each run is per key size, meaning you have to run `ssh-keygen -m generate`, and `ssh-keygen -m screen`
for each key length needed, and then assemple the screened moduli into a single file and install in /etc/ssh/moduli.

`Moduli Generator` provies you with a VERY simple mechanism to produce a high-quality moduli file every 60 hours
(on a quad core i7).

## Technical Overview

The Moduli Generator provides:

### Core Functionality

- **Moduli Generation**: Creates cryptographically secure prime numbers for use as Diffie-Hellman group exchange
- **Database Integration**: Stores and manages generated moduli using MariaDB
- **Performance Optimization**: Efficient implementation for large-scale moduli generation

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