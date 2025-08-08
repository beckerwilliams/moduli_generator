#!/usr/bin/env bash
# Function to prompt for database configuration and create config file
create_moduli_config() {
    local config_dir="${HOME}/.moduli_generator"
    local config_file="${config_dir}/moduli_generator.cnf"

    echo -e "${BLUE}[ Database Configuration Setup ]${NC}"
    echo -e "${YELLOW}Please provide MariaDB connection details for the moduli_generator user:${NC}"
    echo

    # Create config directory if it doesn't exist
    ${MKDIR} "${config_dir}"

    # Prompt for database configuration
    while true; do
        read -p "MariaDB hostname [localhost]: " db_host
        db_host=${db_host:-"localhost"}

        read -p "MariaDB port [3306]: " db_port
        db_port=${db_port:-"3306"}

        read -p "MariaDB socket [/var/run/mysql/mysql.sock]: " db_socket
        db_socket=${db_socket:-"/var/run/mysql/mysql.sock"}

        read -p "Database name [moduli_db]: " db_name
        db_name=${db_name:-"moduli_db"}

        # Username is fixed as per the application design
        db_user="moduli_generator"
        echo -e "${BLUE}Using application user: ${db_user}${NC}"

        while true; do
            read -s -p "Enter password for ${db_user}: " db_password
            echo
            if [[ -n "$db_password" ]]; then
                break
            else
                echo -e "${RED}Password cannot be empty. Please try again.${NC}"
            fi
        done

        read -p "Enable SSL [true]: " db_ssl
        db_ssl=${db_ssl:-"true"}

        # Display configuration summary
        echo
        echo -e "${YELLOW}Configuration Summary:${NC}"
        echo "  Host: ${db_host}"
        echo "  Port: ${db_port}"
        echo "  Socket: ${db_socket}"
        echo "  Database: ${db_name}"
        echo "  User: ${db_user}"
        echo "  SSL: ${db_ssl}"
        echo

        while true; do
            read -p "Is this configuration correct? (y/n): " confirm
            case $confirm in
                [Yy]* ) break 2;;
                [Nn]* )
                    echo -e "${YELLOW}Let's try again...${NC}"
                    echo
                    break;;
                * ) echo "Please answer yes or no.";;
            esac
        done
    done

    # Generate the configuration file
    cat > "${config_file}" << EOF
# This group is read both by the client and the server
# use it for options that affect everything, see
# https://mariadb.com/kb/en/configuring-mariadb-with-option-files/#option-groups
#
[client]
host                                = ${db_host}
port	                            = ${db_port}
socket	                            = ${db_socket}
password                            = ${db_password}
user                                = ${db_user}
database                            = ${db_name}
ssl                                 = ${db_ssl}

EOF

    # Set secure permissions on config file
    chmod 600 "${config_file}"

    echo -e "${GREEN}✓ Configuration file created: ${config_file}${NC}"
    echo -e "${BLUE}File permissions set to 600 (owner read/write only)${NC}"

    return 0
}

# Function to test database connection
test_database_connection() {
    local config_file="${HOME}/.moduli_generator/moduli_generator.cnf"

    if [[ ! -f "${config_file}" ]]; then
        echo -e "${RED}✗ Configuration file not found: ${config_file}${NC}"
        return 1
    fi

    echo -e "${BLUE}[ Testing Database Connection ]${NC}"

    # Test connection using mariadb client if available
    if command -v mariadb >/dev/null 2>&1; then
        if mariadb --defaults-file="${config_file}" -e "SELECT 1;" >/dev/null 2>&1; then
            echo -e "${GREEN}✓ Database connection successful${NC}"
            return 0
        else
            echo -e "${RED}✗ Database connection failed${NC}"
            echo -e "${YELLOW}Please verify your credentials and database server status${NC}"
            return 1
        fi
    elif command -v mysql >/dev/null 2>&1; then
        if mysql --defaults-file="${config_file}" -e "SELECT 1;" >/dev/null 2>&1; then
            echo -e "${GREEN}✓ Database connection successful${NC}"
            return 0
        else
            echo -e "${RED}✗ Database connection failed${NC}"
            echo -e "${YELLOW}Please verify your credentials and database server status${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠ Cannot test connection - MariaDB/MySQL client not found${NC}"
        echo -e "${BLUE}Configuration file created, but connection not verified${NC}"
        return 0
    fi
}
######
# Main
######
create_moduli_config
test_database_connection