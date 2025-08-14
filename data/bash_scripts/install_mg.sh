#!/usr/bin/env bash
# dev boot moduli_generator installer
#
# Creates a virtual environment in user's `current working directory` (${CWD})
#
# Text colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
RED='\033[0;31m'
YELLOW='\033[0;33m'

# No Color (reset)
NC='\033[0m'

ECHO="echo -e"
MV="mv"
MKDIR="mkdir -p"

CWD=$(pwd)

PROJECT_NAME=moduli_generator
WORK_DIR=.${PROJECT_NAME}_build_env

GITHUB_PROJECT=https://github.com/beckerwilliams/${PROJECT_NAME}.git
GIT=$(which git)

PYTHON=$(which python)
VENV_DIR=.venv
MK_VENV="${PYTHON} -m venv"

ACTIVATE_SCRIPT="${VENV_DIR}/bin/activate"
MODULI_GENERATOR_DIR=${PROJECT_NAME}

# Global variable for wheel file
wheel_file=""

##############################################################################################
echo -e "${PURPLE}Project Name: ${PROJECT_NAME}\n\tWORK_DIR: ${WORK_DIR}\n\tCWD: ${CWD}${NC}"

# Function to verify git installation
verify_git() {
    if command -v git >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Git is installed: $(git --version)${NC}"
        return 0
    else
        echo -e "${RED}✗ Git is not installed or not available in PATH${NC}"
        return 1
    fi
}

# Function to verify Python 3.12 or higher installation
verify_python312() {
    local python_cmd=""
    local python_version=""

    # Try different python commands in order of preference
    for cmd in python3.12 python3.13 python3.14 python3.15 python3 python; do
        if command -v "$cmd" >/dev/null 2>&1; then
            python_cmd="$cmd"
            break
        fi
    done

    if [[ -z "$python_cmd" ]]; then
        echo -e "${RED}✗ Python is not installed or not available in PATH${NC}"
        return 1
    fi

    # Get the version and extract major.minor
    python_version=$($python_cmd --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')

    if [[ -z "$python_version" ]]; then
        echo -e "${RED}✗ Could not determine Python version for: $python_cmd${NC}"
        return 1
    fi

    # Convert version to comparable format (e.g., 3.12 -> 312)
    local major minor version_num required_version
    major=$(echo "$python_version" | cut -d. -f1)
    minor=$(echo "$python_version" | cut -d. -f2)
    version_num=$((major * 100 + minor))
    required_version=$((3 * 100 + 12))  # 3.12 = 312

    if [[ $version_num -ge $required_version ]]; then
        echo -e "${GREEN}✓ Python $python_version is installed (≥3.12 required): $($python_cmd --version)${NC}"
        # Update PYTHON variable to use the found command
        PYTHON="$python_cmd"
        MK_VENV="${PYTHON} -m venv"
        return 0
    else
        echo -e "${RED}✗ Python 3.12 or higher required. Found: $($python_cmd --version)${NC}"
        return 1
    fi
}

# Main verification function
verify_requirements() {
    echo -e "${BLUE}[ Verifying System Requirements ]${NC}"

    local git_ok=0
    local python_ok=0

    verify_git || git_ok=1
    verify_python312 || python_ok=1

    if [[ $git_ok -eq 0 && $python_ok -eq 0 ]]; then
        echo -e "${GREEN}✓ All requirements verified successfully${NC}"
        return 0
    else
        echo -e "${RED}✗ Some requirements are missing. Please install the missing components.${NC}"
        return 1
    fi
}

# Function to activate virtual environment
activate_venv() {
    if [[ -f "$ACTIVATE_SCRIPT" ]]; then
        # shellcheck disable=SC1090
        source "$ACTIVATE_SCRIPT"
        echo -e "${GREEN}✓ Virtual environment activated${NC}"

        # Update paths to use virtual environment versions - CRITICAL FIX
        PIP="${VENV_DIR}/bin/pip --no-cache-dir"
        POETRY="${VENV_DIR}/bin/poetry"

        # Verify we're using the right pip
        echo -e "${BLUE}Using pip: $(which pip) --no-cache-dir${NC}"

        return 0
    else
        echo -e "${RED}✗ Virtual environment activation script not found: $ACTIVATE_SCRIPT${NC}"
        return 1
    fi
}

# Function to check if Poetry project has pyproject.toml
check_poetry_project() {
    if [[ ! -f "pyproject.toml" ]]; then
        echo -e "${RED}✗ No pyproject.toml found. This might not be a Poetry project.${NC}"
        return 1
    fi

    # Check for either format - PEP 621 or legacy Poetry
    if grep -q "tool.poetry\|project.*name" pyproject.toml; then
        echo -e "${GREEN}✓ Poetry/PEP 621 project configuration found${NC}"
        return 0
    else
        echo -e "${RED}✗ pyproject.toml doesn't contain Poetry or PEP 621 configuration.${NC}"
        return 1
    fi
}

# Function to clean up any existing work directories
cleanup_work_dir() {
    if [[ -d "${WORK_DIR}" ]]; then
        echo -e "${YELLOW}[ Cleaning up existing work directory: ${WORK_DIR} ]${NC}"
        rm -rf "${WORK_DIR}"
    fi
}

# Function to install Poetry in virtual environment
install_poetry_in_venv() {
    echo -e "${BLUE}[ Installing Poetry in virtual environment ]${NC}"

    # Remove any existing Poetry installation in venv
    ${PIP} uninstall poetry -y 2>/dev/null || true

    # Install a specific, stable Poetry version
    ${PIP} install poetry==1.8.3 || { echo -e "${RED}Failed to install poetry${NC}"; return 1; }

    # Verify Poetry installation
    if [[ -f "${POETRY}" ]] && ${POETRY} --version; then
        echo -e "${GREEN}✓ Poetry installed successfully: $(${POETRY} --version)${NC}"
        return 0
    else
        echo -e "${RED}✗ Poetry installation verification failed${NC}"
        return 1
    fi
}

create_privileged_config() {
    local config_dir="${HOME}/.moduli_generator"
    local config_file="${config_dir}/privileged.tmp"

    echo -e "${BLUE}[ Database Configuration Setup ]${NC}"
    echo -e "${YELLOW}Please provide MariaDB connection details for the moduli_generator user:${NC}"
    echo

    # Create config directory if it doesn't exist
    ${MKDIR} "${config_dir}"

    # Prompt for database configuration
    while true; do

        # Username is fixed as per the application design
        while true; do
	        read -p "Privilged MariaDB User (root user?): " db_user
	        echo
	        if [[ -n "$db_user" ]]; then
	        	break
	        else
	        	echo "${RED}Username cannot be empty. Please Try Again (or ctrl-c to escape)"
        	fi
        done

        while true; do
            read -s -p "Enter password for ${db_user}: " db_password
            echo
            if [[ -n "$db_password" ]]; then
                break
            else
                echo -e "${RED}Password cannot be empty. Please try again.${NC}"
            fi
        done

        read -p "MariaDB hostname [localhost]: " db_host
        db_host=${db_host:-"localhost"}

        read -p "MariaDB port [3306]: " db_port
        db_port=${db_port:-"3306"}

        read -p "Enable SSL [true]: " db_ssl
        db_ssl=${db_ssl:-"true"}

        # Display configuration summary
        echo
        echo -e "${YELLOW}Configuration Summary:${NC}"
        echo "  User: ${db_user}"
        echo "  SSL: ${db_ssl}"
        echo "  Host: ${db_host}"
        echo "  Port: ${db_port}"

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
user                                = ${db_user}
password                            = ${db_password}
ssl                                 = ${db_ssl}

EOF

    # Set secure permissions on config file
    chmod 600 "${config_file}"

    echo -e "${GREEN}✓ Configuration file created: ${config_file}${NC}"
    echo -e "${BLUE}File permissions set to 600 (owner read/write only)${NC}"

    return 0
}

# Prompt for database configuration
#prompt_database_config() {
#    echo -e "${BLUE}[ Database Configuration ]${NC}"
#
#    while true; do
#        read -p "Enter MariaDB host [localhost]: " db_host
#        db_host=${db_host:-"localhost"}
#
#        read -p "Enter MariaDB port [3306]: " db_port
#        db_port=${db_port:-"3306"}
#
#        read -p "Enter database name [moduli_db]: " db_name
#        db_name=${db_name:-"moduli_db"}
#
#        read -p "Enter MariaDB username [privileged_user]: " db_user
#        db_user='privileged_user'
#        read -s -p "Enter MariaDB password: " db_pass
#        echo
#        if [[ -z "$db_pass" ]]; then
#            echo -e "${RED}Password is required${NC}"
#            continue
#        fi
#
#        break
#    done
#
#
#
#    echo -e "${GREEN}✓ Database configuration complete${NC}"
#}

build_wheel() {
    echo -e "${PURPLE}*** Project Name: ${PROJECT_NAME}\n\tWORK_DIR: ${WORK_DIR}\n\tCWD: ${CWD} ***${NC}"

    # Clean up any existing work directory first
    cleanup_work_dir

	# Save Current Directory
    ${ECHO} "${BLUE}[ Saving Current Directory ${CWD}, entering ${WORK_DIR} ]${NC}"
    ${MKDIR} "${WORK_DIR}" || { echo -e "${RED}Failed to create work directory${NC}"; return 1; }
    cd "${WORK_DIR}" || { echo -e "${RED}Failed to enter work directory${NC}"; return 1; }

    # Clone Project from Github Repo - now should work since we cleaned up
    ${ECHO} "${BLUE}[ Cloning moduli_generator from Github ]${NC}"
    if ! ${GIT} clone "${GITHUB_PROJECT}"; then
        echo -e "${RED}Cloning moduli_generator FAILED!${NC}"
        # Additional debugging information
        echo -e "${YELLOW}Current directory contents:${NC}"
        ls -la
        return 1
    fi

    # Change Directory to Installed 'moduli_generator' (project)
    ${ECHO} "${BLUE}[ Entering Moduli Dev Directory ]${NC}"
    cd "${MODULI_GENERATOR_DIR}" || { echo -e "${RED}Failed to enter moduli_generator directory${NC}"; return 1; }

    # Check if this is a valid Poetry project
    check_poetry_project || return 1

    # Create and Activate BUILD Virtual Environment
    ${ECHO} "${BLUE}[ Creating and Activating Moduli Generator's Wheel Builder ]${NC}"
    ${MK_VENV} "${VENV_DIR}" || { echo -e "${RED}Failed to create virtual environment${NC}"; return 1; }
    activate_venv || { echo -e "${RED}Failed to activate virtual environment${NC}"; return 1; }

    ####################################
    # Install, Update, and Build POETRY
    ####################################
    ${ECHO} "${BLUE}[ Upgrading pip ]${NC}"
    ${PIP} install --upgrade pip || { echo -e "${RED}Failed to upgrade pip${NC}"; return 1; }

    # Install Poetry in the virtual environment
    install_poetry_in_venv || { echo -e "${RED}Failed to install Poetry${NC}"; return 1; }

    # Configure Poetry to not create virtual environments (we're already in one)
    ${POETRY} config virtualenvs.create false || echo -e "${YELLOW}Warning: Failed to configure Poetry${NC}"

    # Install dependencies first
    ${ECHO} "${BLUE}[ Installing project dependencies ]${NC}"
    ${POETRY} install || { echo -e "${RED}Failed to install dependencies${NC}"; return 1; }

    # Try to update/lock dependencies
    ${ECHO} "${BLUE}[ Updating Poetry lock file ]${NC}"
    if ! ${POETRY} lock --no-update; then
        echo -e "${YELLOW}Poetry lock failed, trying to regenerate...${NC}"
        rm -f poetry.lock
        ${POETRY} lock || { echo -e "${RED}Failed to generate poetry.lock${NC}"; return 1; }
    fi

    ${ECHO} "${BLUE}[ Building moduli_generator wheel ]${NC}"
    ${POETRY} build || { echo -e "${RED}Failed to build wheel${NC}"; return 1; }

    #########################################
    # The Product
    #########################################
    if ! ls dist/*.whl >/dev/null 2>&1; then
        echo -e "${RED}No wheel file found in dist directory${NC}"
        return 1
    fi

    wheel_file=$(ls dist/*.whl | head -n1 | xargs basename)
    echo -e "${GREEN}✓ Wheel file created: ${wheel_file}${NC}"

    #############################################################
    # Copy Wheel File to Runtime Directory (Current Working Dir)
    #############################################################
    ${ECHO} "${BLUE}[ Moduli Generator Wheel: ${CWD}/${wheel_file} ]${NC}"
    ${MV} "dist/${wheel_file}" "${CWD}/${wheel_file}" || { echo -e "${RED}Failed to move wheel file${NC}"; return 1; }

    ##################################
    # CLOSE BUILD Virtual Environment
    ##################################
    cd "${CWD}" || { echo -e "${RED}Failed to return to CWD${NC}"; return 1; }
    if [[ "${WORK_DIR}" != "/" && -d "${WORK_DIR}" ]]; then
        rm -rf "${WORK_DIR}"
        ${ECHO} "${PURPLE}Deleted Temporary Work Dir: ${WORK_DIR}${NC}"
    fi

    echo -e "${GREEN}✓ Build wheel completed successfully${NC}"
    return 0
}

build_moduli_generator() {
    echo -e "${PURPLE}*** Project Name: ${PROJECT_NAME}\n\tWORK_DIR: ${WORK_DIR}\n\tCWD: ${CWD} ***${NC}"

    # Check if wheel file exists
    if [[ ! -f "${wheel_file}" ]]; then
        echo -e "${RED}✗ Wheel file not found: ${wheel_file}${NC}"
        return 1
    fi

    # Clean up any existing runtime virtual environment
    if [[ -d "${VENV_DIR}" ]]; then
        echo -e "${YELLOW}[ Cleaning up existing runtime virtual environment ]${NC}"
        rm -rf "${VENV_DIR}"
    fi

    # Create and Activate Runtime Virtual Environment
    ${ECHO} "${BLUE}[ Creating runtime virtual environment ]${NC}"
    ${MK_VENV} "${VENV_DIR}" || { echo -e "${RED}Failed to create runtime virtual environment${NC}"; return 1; }
    activate_venv || { echo -e "${RED}Failed to activate runtime virtual environment${NC}"; return 1; }

    # Upgrade version of PIP, Install Moduli Generator Wheel from BUILD Stage
    ${ECHO} "${BLUE}[ Upgrading Virtual Environment and Installing Moduli Generator wheel ]${NC}"

    ${PIP} install --upgrade pip || { echo -e "${RED}Failed to upgrade pip${NC}"; return 1; }
    ${PIP} install "${wheel_file}" || { echo -e "${RED}Failed to install wheel file${NC}"; return 1; }
    rm "${wheel_file}" || echo -e "${YELLOW}Warning: Failed to remove wheel file${NC}"

    # Print out Build and Install Status
    ${ECHO} "${GREEN}[ Moduli Generator Installed Successfully ]${NC}"
    ${ECHO} "${BLUE}Virtual Environment Package Manifest:${PURPLE}"
    ${PIP} list
    ${ECHO} "${NC}"

    ##############################
    # RUNTIME Environment COMPLETE
    ##############################
     deactivate || true  # Uncomment if you want to deactivate

    echo -e "${GREEN}✓ Runtime installation completed successfully${NC}"
    return 0
}

schema_installer() {
	$(install_schema --mariadb-cnf ${HOME}/.moduli_generator/privilged.tmp)
}

cleanup() {  # Remove Temporary Privileged Credentials -
	rm -rf ${config_dir}/*.tmp 2>&1 /dev/null
}
#########################################################################################################
# MAIN
#########################################################################################################

# Set error handling
set -e
trap 'echo -e "${RED}Script failed at line $LINENO${NC}"' ERR

#####################
# Verify Requirements
#####################
if ! verify_requirements; then
    echo -e "${RED}Requirements verification failed. Exiting.${NC}"
    exit 1
fi

##########################################
# Prompt User for Configuration Parameters
##########################################
if ! create_privileged_config; then
	echo -e "${RED}Configuration Failed. Exiting.${NC}"
	exit 1
fi

###############################################
# Create, Update, BUILD WHEEL, Store in ${CWD}
###############################################
if ! build_wheel; then
    echo -e "${RED}build_wheel FAILED${NC}"
    exit 1
fi

#####################################################
#  BUILD Moduli Generator Virtual RUNTIME (Pristine)
#####################################################
if ! build_moduli_generator; then
    echo -e "${RED}Build Moduli Generator Failed${NC}"
    exit 1
fi

if ! schema_installer; then
	echo -e "${RED}Moduli Generator User and Schema Installer Failed${NC}"
	exit 1
fi

cleanup

echo -e "${GREEN}✓ Installation completed successfully!${NC}"
echo -e "${BLUE}To activate the environment, run: source ${VENV_DIR}/bin/activate${NC}"
echo -e "${BLUE}To test the installation, run: moduli_generator --help${NC}"
