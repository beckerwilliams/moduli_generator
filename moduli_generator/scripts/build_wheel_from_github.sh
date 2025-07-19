#!/usr/bin/env bash
# moduli_generator installer
#
# Creates a virtual environment in user's HOME directory
#
# Text colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
# No Color (reset)
NC='\033[0m'

PROJECT_NAME=moduli_generator
WORK_DIR=.moduli_generator_temp
GITHUB_PROJECT=https://github.com/beckerwilliams/moduli_generator.git
GIT="/usr/bin/env git"
PYTHON="/usr/bin/env python"
MK_VENV="${PYTHON} -m venv"
VENV_DIR=.venv
ECHO="echo -e"
MV="mv"
MKDIR="mkdir -p"
POETRY="/usr/bin/env poetry"
PIP="pip"
ACTIVATE="source .venv/bin/activate"
MODULI_GENERATOR_DIR=moduli_generator
WHEEL_TARGET_DIR=${HOME}

###############################################
# BUILD WORKING Virtual Environment
# Create, Update, BUILD WHEEL, Store in ${HOME}
###############################################
CWD=$(pwd)

${ECHO} "${BLUE}[ Saving Current Directory ${CWD}, entering ${WORK_DIR} ] ${NC}"
${MKDIR} ${WORK_DIR}
cd ${WORK_DIR} || exit

${ECHO} "${BLUE}"[ Cloning moduli_generator from Github ] "${NC}"
${GIT} clone "${GITHUB_PROJECT}" || exit

${ECHO} "${BLUE}"[ Entering Moduli Dev Directory ] "${NC}"
# ${WORKDIR} -> ${MODULI_GENERATOR_DIR}
cd ${MODULI_GENERATOR_DIR} || exit

############################################
# CREATE and Activate Wheel Build Environment
############################################
${ECHO} "${BLUE}"[ Creating and Activating Python Virtual Enviroment ] "${NC}"
${MK_VENV} ${VENV_DIR}
${ACTIVATE}

 #################
 # Install POETRY
 #################
${PIP} intall pip --upgrade
${PIP} install poetry --upgrade
${POETRY} update
${ECHO} "${BLUE}"[ Building moduli_generator wheel ] "${NC}"
${POETRY} build

# The Product
wheel_file=$(ls dist/*.whl | cut -d/ -f2)

${ECHO} "${BLUE}"[ Copy Moduli Generator Wheel to current directory: "${WHEEL_TARGET_DIR}"/"${wheel_file}" ] "${NC}"
${MV} dist/"${wheel_file}" "${CWD}"/"${wheel_file}"

##################
# CLOSE BUILD Venv
##################
deactivate

cd "${CWD}" || exit
if [ "${WORK_DIR}" != "/" ]; then rm -rf "${WORK_DIR}"; fi

exit