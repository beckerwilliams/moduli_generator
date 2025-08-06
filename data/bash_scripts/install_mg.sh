#!/usr/bin/env bash
# dev boot moduli_generator installer
#
# Creates a virtual environment in user's HOME directory
#
# Text colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
RED='\033[0;31m'

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
VENV_DIR=.test_venv
MK_VENV="${PYTHON} -m venv"

POETRY=$(which poetry)
PIP=$(which pip)

ACTIVATE="source ${VENV_DIR}/bin/activate"
MODULI_GENERATOR_DIR=${PROJECT_NAME}


echo "${PURPLE}Project Name: ${PROJECT_NAME}\n\tWORD_DIR: ${WORK_DIR}\n\tCWD: ${CWD}"

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
    # shellcheck disable=SC2155
    local major=$(echo "$python_version" | cut -d. -f1)
    # shellcheck disable=SC2155
    local minor=$(echo "$python_version" | cut -d. -f2)
    local version_num=$((major * 100 + minor))
    local required_version=$((3 * 100 + 12))  # 3.12 = 312

    if [[ $version_num -ge $required_version ]]; then
        echo -e "${GREEN}✓ Python $python_version is installed (≥3.12 required): $($python_cmd --version)${NC}"
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

build_wheel() {
	# Set Wheel BUILD Logfile
	BUILD_MG_LOG="${CWD}/build.log"

	echo "${PURPLE}*** Project Name: ${PROJECT_NAME}\n\tWORD_DIR: ${WORK_DIR}\n\tCWD: ${CWD} ***${NV}"
	
	# shellcheck disable=SC2188
	> "${BUILD_MG_LOG}"

	${ECHO} "${BLUE}[ Saving Current Directory ${CWD}, entering ${WORK_DIR} ] ${NC}"
	${MKDIR} ${WORK_DIR} # >> "${BUILD_MG_LOG}" 2>&1
	cd ${WORK_DIR} # >> "${BUILD_MG_LOG}" 2>&1  || exit 1

	# Clone Project from Github Repo
	${ECHO} "${BLUE}"[ Cloning moduli_generator from Github ] "${NC}"
	${GIT} clone "${GITHUB_PROJECT}" || exit 1  # >> "${BUILD_MG_LOG}" 2>&1  || echo "Cloning moduli_generator FAILED!" && exit 1

	# Change Directory to Installed 'moduli_generator' (project)
	${ECHO} "${BLUE}"[ Entering Moduli Dev Directory ] "${NC}"
	cd ${MODULI_GENERATOR_DIR} # >> "${BUILD_MG_LOG}" 2>&1  \
	#		|| echo "Changing directory to installed moduli_generator FAILED" && exit 1

	# Create and Activate BUILD Virtrual Enviroment
	${ECHO} "${BLUE}"[ Creating and Activating Moduli Generator\'s Wheel Builder ] "${NC}"
	${MK_VENV} ${VENV_DIR} # >> "${BUILD_MG_LOG}" 2>&1
	${ACTIVATE} # >> "${BUILD_MG_LOG}" 2>&1

	####################################
	# Install, Update, and Build POETRY
	####################################
	${PIP} install pip --upgrade # >> "${BUILD_MG_LOG}" 2>&1  # Fixed typo: intall -> install
	${PIP} install poetry --upgrade # >> "${BUILD_MG_LOG}" 2>&1
	${POETRY} update # >> "${BUILD_MG_LOG}" 2>&1
	${ECHO} "${BLUE}"[ Building moduli_generator wheel ] "${NC}"
	${POETRY} build # >> "${BUILD_MG_LOG}" 2>&1

	#########################################
	# The Product
	#########################################
	# shellcheck disable=SC2155
	export wheel_file=$(ls dist/*.whl | cut -d/ -f2)

	#############################################################
	# Copy Wheel File to Runtime Directory (Current Working Dir)
	#############################################################
	${ECHO} "${BLUE}"[ Moduli Generator Wheel: "${CWD}"/"${wheel_file}" ] "${NC}"
	${MV} dist/"${wheel_file}" "${CWD}"/"${wheel_file}" # >> "${BUILD_MG_LOG}" 2>&1

	##################################
	# CLOSE BUILD Virtual Environment
	##################################
	cd "${CWD}" # >> "${BUILD_MG_LOG}" 2>&1|| exit 1
	if [ "${WORK_DIR}" != "/" ]; then rm -rf "${WORK_DIR}"; fi
	${ECHO} "${PURPLE}" Deleted Temporary Work Dir: "${WORK_DIR}"  # >> "${BUILD_MG_LOG}" 2>&1 "${NC}"
}

build_moduli_generator() {
	BUILD_MG_LOG=${CWD}/runtime_install.log
	echo "${PURPLE}*** Project Name: ${PROJECT_NAME}\n\tWORD_DIR: ${WORK_DIR}\n\tCWD: ${CWD} ***${NV}"
	
	# shellcheck disable=SC2188
	> "${BUILD_MG_LOG}"

	# Create and Activate Runtime Virtual Environent
	${ECHO} "${BLUE}"[ Creating runtime virtual environment ] "${NC}"
	${MK_VENV} ${VENV_DIR} # >> "${BUILD_MG_LOG}" 2>&1
	${ACTIVATE} # >> "${BUILD_MG_LOG}" 2>&1

	# Upgrade version of PIP, Install Moduli Generator Wheel from BUILD Stage
	${ECHO} "${BLUE}"[ Upgrading Virtual Environment and Installing Moduli Generator wheel ] "${NC}"

	# shellcheck disable=SC2129
	${PIP} install pip --upgrade  # >> "${BUILD_MG_LOG}" 2>&1
	${PIP} install "${wheel_file}"  # >> "${BUILD_MG_LOG}" 2>&1
	rm "${wheel_file}" # >> "${BUILD_MG_LOG}" 2>&1

	# Print out Build and Install Status, Deactivate RUNTIME Virtual Enviornment
	${ECHO} "${GREEN}"[ Moduli Generator Installed Successfully ] "${NC}"
	${ECHO} "${BLUE}"Virual Environment Package Manifest: "${PURPLE}"
	${PIP} list
	${ECHO} "${NC}"

	##############################
	# RUNTIME Environment COMPLETE
#	##############################
#	deactivate || 0

}

###################################
# MAIN
###################################


#####################
# Verify Requirements
#####################
verify_requirements || exit 1

###############################################
# Create, Update, BUILD WHEEL, Store in ${CWD}
###############################################
build_wheel || echo "build_wheel FAILED" && exit 1

#####################################################
#  BUILD Moduli Generator Virtual RUNTIME (Pristine)
#####################################################
# build_moduli_generator || echo "Build Moduli Generator Failed" && exit 1
