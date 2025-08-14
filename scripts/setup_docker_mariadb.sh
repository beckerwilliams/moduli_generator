#!/bin/bash
# Script to set up MariaDB Docker container and configure the client

# Function to check if Docker is installed
check_docker() {
  if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
  fi

  if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
  fi
}

# Function to start the MariaDB Docker container
start_mariadb_container() {
  echo "Starting MariaDB Docker container..."
  docker-compose up -d
  
  # Wait for container to be ready
  echo "Waiting for MariaDB to initialize..."
  sleep 10
  
  # Check if container is running
  if ! docker ps | grep -q "moduli_generator_mariadb"; then
    echo "Failed to start MariaDB container. Check Docker logs for details."
    echo "Run: docker-compose logs mariadb"
    exit 1
  fi
  
  echo "MariaDB container is running."
}

# Function to create the moduli_generator config file
create_config_file() {
  CONFIG_DIR="$HOME/.moduli_generator"
  CONFIG_FILE="$CONFIG_DIR/moduli_generator.cnf"
  
  # Create directory if it doesn't exist
  mkdir -p "$CONFIG_DIR"
  
  # Create config file
  echo "Creating MariaDB configuration file at $CONFIG_FILE"
  cat > "$CONFIG_FILE" << EOF
[client]
host = localhost
port = 3306
user = moduli_generator
password = moduli_password
database = moduli_db
EOF
  
  # Set permissions
  chmod 600 "$CONFIG_FILE"
  
  echo "Configuration file created successfully."
}

# Main function
main() {
  echo "Setting up MariaDB Docker container for Moduli Generator"
  echo "========================================================="
  
  # Check if Docker is installed
  check_docker
  
  # Check if we're in the project root directory
  if [ ! -f "docker-compose.yml" ]; then
    echo "Error: docker-compose.yml not found."
    echo "Please run this script from the project root directory."
    exit 1
  fi
  
  # Start the MariaDB container
  start_mariadb_container
  
  # Create the config file
  create_config_file
  
  echo "========================================================="
  echo "Setup complete! The MariaDB Docker container is running and"
  echo "the configuration file has been created."
  echo ""
  echo "You can now use the Moduli Generator application with the"
  echo "dockerized MariaDB database."
  echo ""
  echo "To stop the container, run: docker-compose stop"
  echo "To start it again, run: docker-compose start"
  echo "========================================================="
}

# Run the main function
main