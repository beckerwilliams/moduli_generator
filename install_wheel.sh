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
GITHUB_PROJECT=https://github.com/beckerwilliams/${PROJECT_NAME}.git
GIT="/usr/bin/env git"
PYTHON="/usr/bin/env python"
MK_VENV="${PYTHON} -m venv"
VENV_DIR=.venv
ECHO="echo -e"
MV=mv
MKDIR="mkdir -p"
POETRY="/usr/bin/env poetry"
PIP="pip"
ACTIVATE="source .venv/bin/activate"
WHEEL_FILE=$(ls ${PROJECT_NAME}-*.*.*-py3-none-any.whl)
LOG_FILE=install.log
> ${LOG_FILE}

##############################################
# BUILDING (Pristine) RUNTIME Virtual Environment
##############################################
${ECHO} "${BLUE}"[ Creating runtime virtual environment ] "${NC}"
${MK_VENV} ${VENV_DIR} >> ${LOG_FILE} 2>&1
${ACTIVATE} >> ${LOG_FILE} 2>&1

${ECHO} "${BLUE}"[ Upgrading Virtual Environment and Installing Moduli Generator wheel ] "${NC}"
${PIP} install pip --upgrade >> ${LOG_FILE} 2>&1
${PIP} install "${WHEEL_FILE}" >> ${LOG_FILE} 2>&1
rm "${WHEEL_FILE}" >> ${LOG_FILE} 2>&1

${ECHO} "${GREEN}"[ Moduli Generator Installed Successfully ] ${NC}
${ECHO} "${BLUE}"Virual Environment Package Manifest: ${PURPLE}
${PIP} list
${ECHO} ${NC}
deactivate
##############################
# RUNTIME Environment COMPLETE
##############################

