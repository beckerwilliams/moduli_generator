# Docker MariaDB Setup for Moduli Generator

This document provides a comprehensive guide to setting up MariaDB using Docker for the Moduli Generator project.

## Overview

This solution sets up a MariaDB database in Docker that is:

- Accessible at localhost:3306
- Pre-configured with the required schema for Moduli Generator
- Easily manageable using Docker Compose
- Persistent across restarts with a Docker volume

## Quick Setup

For the fastest setup, run:

```bash
# Make scripts executable (if needed)
chmod +x scripts/setup_docker_mariadb.sh scripts/test_db_connection.py

# Run the automated setup script
./scripts/setup_docker_mariadb.sh

# Test the connection
./scripts/test_db_connection.py
```

## Components

The solution consists of the following components:

1. **docker-compose.yml**: Defines the MariaDB container configuration
2. **scripts/setup_docker_mariadb.sh**: Automated setup script
3. **scripts/test_db_connection.py**: Database connection test script
4. **README.docker.md**: Detailed documentation for Docker setup
5. **DOCKER_MARIADB_SETUP.md**: This overview document

## Manual Setup Steps

If you prefer to set up manually:

1. Start the Docker container:
   ```bash
   docker-compose up -d
   ```

2. Create the configuration file:
   ```bash
   mkdir -p ~/.moduli_generator
   cat > ~/.moduli_generator/moduli_generator.cnf << EOF
   [client]
   host = localhost
   port = 3306
   user = moduli_generator
   password = moduli_password
   database = moduli_db
   EOF
   chmod 600 ~/.moduli_generator/moduli_generator.cnf
   ```

3. Test the connection:
   ```bash
   ./scripts/test_db_connection.py
   ```

## Database Configuration

The database is configured with:

- MariaDB latest version
- Default database name: `moduli_db`
- Default user: `moduli_generator`
- Default password: `moduli_password`
- Root password: `rootpassword`

## Troubleshooting

If you encounter any issues:

1. Verify Docker is running:
   ```bash
   docker ps
   ```

2. Check container logs:
   ```bash
   docker-compose logs mariadb
   ```

3. Ensure the configuration file exists and has the correct settings:
   ```bash
   cat ~/.moduli_generator/moduli_generator.cnf
   ```

4. Try running the test script with verbose output:
   ```bash
   ./scripts/test_db_connection.py
   ```

## Additional Information

For more detailed information about using and managing the Docker setup, please refer to
the [README.docker.md](../../README.docker.md) file.

## Security Considerations

The default configuration uses fixed passwords for development convenience. For production use:

1. Use environment variables or Docker secrets for sensitive information
2. Change default passwords
3. Consider network isolation
4. Follow MariaDB security best practices