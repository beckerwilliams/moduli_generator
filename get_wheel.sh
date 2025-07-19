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

###############################################
# BUILD WORKING Virtual Environment
# Create, Update, BUILD WHEEL, Store in ${HOME}
###############################################
CWD="$(pwd)"

LOG_FILE="${CWD}/get_wheel.log"

# Clear the log file at the start
> ${LOG_FILE}

${ECHO} "${BLUE}[ Saving Current Directory ${CWD}, entering ${WORK_DIR} ] ${NC}"
${MKDIR} ${WORK_DIR} >> ${LOG_FILE} 2>&1
cd ${WORK_DIR} >> ${LOG_FILE} 2>&1  || exit

${ECHO} "${BLUE}"[ Cloning moduli_generator from Github ] "${NC}"
${GIT} clone "${GITHUB_PROJECT}" >> ${LOG_FILE} 2>&1  || exit

${ECHO} "${BLUE}"[ Entering Moduli Dev Directory ] "${NC}"
# ${WORKDIR} -> ${MODULI_GENERATOR_DIR}
cd ${MODULI_GENERATOR_DIR} >> ${LOG_FILE} 2>&1  || exit

############################################
# CREATE and Activate Wheel Build Environment
############################################
${ECHO} "${BLUE}"[ Creating and Activating Python BUILD Enviroment ] "${NC}"
${MK_VENV} ${VENV_DIR} >> ${LOG_FILE} 2>&1
${ACTIVATE} >> ${LOG_FILE} 2>&1

 #################
 # Install POETRY
 #################
${PIP} install pip --upgrade >> ${LOG_FILE} 2>&1  # Fixed typo: intall -> install
${PIP} install poetry --upgrade >> ${LOG_FILE} 2>&1
${POETRY} update >> ${LOG_FILE} 2>&1
${ECHO} "${BLUE}"[ Building moduli_generator wheel ] "${NC}"
${POETRY} build >> ${LOG_FILE} 2>&1

# The Product
wheel_file=$(ls dist/*.whl | cut -d/ -f2)

${ECHO} "${BLUE}"[ Moduli Generator Wheel: "${CWD}"/"${wheel_file}" ] "${NC}"
${MV} dist/"${wheel_file}" "${CWD}"/"${wheel_file}" >> ${LOG_FILE} 2>&1

##################
# CLOSE BUILD Venv
##################
deactivate

cd "${CWD}" >> ${LOG_FILE} 2>&1|| exit
if [ "${WORK_DIR}" != "/" ]; then rm -rf "${WORK_DIR}"; fi
${ECHO} "${PURPLE}" Deleted Temporary Work Dir: "${WORK_DIR}"  >> ${LOG_FILE} 2>&1 ${NC}
