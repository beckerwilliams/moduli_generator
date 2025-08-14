# MariaDB Docker Setup for Moduli Generator

This document describes how to use the Docker-based MariaDB setup for the Moduli Generator project.

## Prerequisites

- Docker and Docker Compose installed on your system
- Basic knowledge of Docker and Docker Compose
- The Moduli Generator project checked out locally

## Quick Start

1. From the project root directory, start the MariaDB container:

```bash
docker-compose up -d
```

2. This will:
    - Pull the MariaDB Docker image (if not already present)
    - Create a MariaDB container with port 3306 exposed to localhost
    - Initialize the database with required schema from `data/schema/`
    - Create the `moduli_db` database
    - Create a `moduli_generator` user with appropriate permissions

3. Wait a few seconds for the container to initialize completely.

## Connection Details

The MariaDB instance is configured with the following parameters:

- **Host**: localhost
- **Port**: 3306
- **Database**: moduli_db
- **User**: moduli_generator
- **Password**: moduli_password
- **Root Password**: rootpassword

## Using with Moduli Generator

The Moduli Generator application should automatically connect to this database using the settings in the
`~/.moduli_generator/moduli_generator.cnf` file. If this file doesn't exist, you can create it with the following
content:

```ini
[client]
host = localhost
port = 3306
user = moduli_generator
password = moduli_password
database = moduli_db
```

Save this file to `~/.moduli_generator/moduli_generator.cnf` to enable the application to connect to the Docker-based
MariaDB.

## Database Persistence

The MariaDB data is persisted using a Docker volume named `mariadb_data`. This ensures your data remains intact even if
the container is stopped or removed.

## Management Commands

- **Start the container**:
  ```bash
  docker-compose up -d
  ```

- **Stop the container** (preserves data):
  ```bash
  docker-compose stop
  ```

- **Stop and remove the container** (preserves data):
  ```bash
  docker-compose down
  ```

- **Stop and completely remove everything** (including data):
  ```bash
  docker-compose down -v
  ```

- **View container logs**:
  ```bash
  docker-compose logs -f mariadb
  ```

- **Connect to MariaDB CLI**:
  ```bash
  docker exec -it moduli_generator_mariadb mysql -u moduli_generator -pmoduli_password moduli_db
  ```

## Troubleshooting

### Unable to Connect to Database

If the application cannot connect to the database, verify:

1. The Docker container is running:
   ```bash
   docker ps | grep moduli_generator_mariadb
   ```

2. The port is correctly exposed:
   ```bash
   docker-compose ps
   ```

3. Your MariaDB client configuration is pointing to localhost:3306

### Database Initialization Failed

If the database wasn't initialized correctly:

1. Check the container logs:
   ```bash
   docker-compose logs mariadb
   ```

2. Try recreating the container:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

## Security Note

This setup is configured for local development with preset passwords. For production use, you should:

1. Change all default passwords
2. Consider using Docker secrets or environment variables for sensitive information
3. Restrict network access appropriately
4. Follow other security best practices for MariaDB deployments