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
MV=mv
MKDIR="mkdir -p"
POETRY="/usr/bin/env poetry"
PIP="pip"
ACTIVATE="source .venv/bin/activate"
MODULI_GENERATOR_DIR=moduli_generator
WHEEL_TARGET_DIR=${HOME}
WHEEL_FILE=$(ls moduli_generator-*.*.*-py3-none-any.whl)

CWD=$(pwd)

##############################################
# BUILDING (Pristine) RUNTIME Virtual Environment
##############################################
${ECHO} "${BLUE}"[ Creating runtime virtual environment ] "${NC}"
${MK_VENV} ${VENV_DIR} > install.log 2>&1
${ACTIVATE} > install.log 2>&1

${ECHO} "${BLUE}"[ Upgrading Virtual Environment and Installing Moduli Generator wheel: "${wheel_file}" ] "${NC}"
${PIP} install pip --upgrade > install.log 2>&1
${PIP} install "${WHEEL_FILE}" > install.log 2>&1
rm "${WHEEL_FILE}" > install.log 2>&1

${ECHO} "${GREEN}"Moduli Generator Installed Successfully to "${CWD}""${NC}"
${ECHO} "${PURPLE}", Work Directory "${WORK_DIR}" DELETED ${NC}
${PIP} list

deactivate
##############################
# RUNTIME Environment COMPLETE
##############################

