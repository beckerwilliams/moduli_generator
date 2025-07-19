__all__ = ['installer_script']

def installer_script():

    return """#!/usr/bin/env bash

# moduli_generator installer
#
# Creates a virtual environment in user's HOME directory
#
# Text colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color (reset)

BELL='\007'

# Moduli_Generator Constants
WORK_DIR=.moduli_generator_temp
GITHUB_PROJECT=https://github.com/beckerwilliams/moduli_generator.git
PYTHON="/usr/bin/env python"
MK_VENV="${PYTHON} -m venv"
VENV_DIR=.venv
POETRY="/usr/bin/env poetry"
ACTIVATE="source .venv/bin/activate"
MODULI_GENERATOR_DIR=moduli_generator
CWD=$(pwd)
WHEEL_TARGET_DIR=$(pwd)
LOG_FILE="> ${CWD}/install.log 2>&1"

# Notify of our state
echo -e ${GREEN}"Run Constants"
echo -e "\tCurrent Working Directory: ${CWD}"
echo -e "\tGITHUB_PROJECT: ${GITHUB_PROJECT}"
echo -e "\tPYTHON: ${PYTHON}"
echo -e "\tMK_VENV: ${MK_VENV}"
echo -e "\tVENV_DIR: ${VENV_DIR}"
echo -e "\tPOETRY": ${POETRY}
echo -e "\tACTIVATE: ${ACTIVATE}"
echo -e "\tMODULI_GENERATOR_DIR: ${MODULI_GENERATOR_DIR}"
echo -e "\tWHEEL_TARGET_DIR: ${WHEEL_TARGET_DIR}"
echo -e	'\t#########################################################'${NC}

echo -e "${BLUE}[ Saving Current Directory ${CWD}, entering ${WORK_DIR} ]"
mkdir ${WORK_DIR} "${LOG_FILE}"
cd ${WORK_DIR} "${LOG_FILE}" || exit "${LOG_FILE}"

echo -e [ Cloning moduli_generator from Github ]
git clone ${GITHUB_PROJECT} "${LOG_FILE}"

echo -e [ Entering Moduli Dev Directory: ${MODULI_GENERATOR_DIR} ]
cd ${MODULI_GENERATOR_DIR} "${LOG_FILE}" || exit "${LOG_FILE}"

echo -e [ Creating and Activating Python Virtual Enviroment in $(pwd) ]
${MK_VENV} ${VENV_DIR} "${LOG_FILE}"
${ACTIVATE} > "${LOG_FILE}"

echo -e [ Building moduli_generator wheel ]
${POETRY} update > "${LOG_FILE}"
${POETRY} build > "${LOG_FILE}"
deactivate > "${LOG_FILE}"

wheel_file=$(ls dist/*.whl | cut -d/ -f2) > "${LOG_FILE}"
echo -e [ Successfully built fresh wheel ] \n ${NC}
echo -e ${GREEN}[ Building Local Virtual Enironment ] ${BELL}


echo -e [ Copy Moduli Generator Wheel to starting directory: "${WHEEL_TARGET_DIR}"/"${wheel_file}" ]
mv dist/"${wheel_file}" "${CWD}"/"${wheel_file}"   > "${LOG_FILE}"
cd "${CWD}" > "${LOG_FILE}" || exit  "${LOG_FILE}"

#####################################################################################################

echo -e [ Creating runtime virtual environment ]
${MK_VENV} ${VENV_DIR} "${LOG_FILE}"

${ACTIVATE} > "${LOG_FILE}"

echo -e [ Upgrading Virtual Environment and Installing Moduli Generator wheel: "${wheel_file}" ] ${NC}
pip install pip --upgrade  > "${LOG_FILE}"

pip install "${CWD}"/"${wheel_file}"  > "${LOG_FILE}"
rm "${CWD}"/"${wheel_file}"  > "${LOG_FILE}"
rm -rf ${WORK_DIR} "${LOG_FILE}"  # Cleanup transients

echo
echo -e ${BLUE}Moduli Generator Installed Successfully to ${CWD}
pip list

# CLEANUP
deactivate

if [ "${CWD}" != "/" ]; then rm -rf "${CWD}"/"${wheel_file}" "${LOG_FILE}" ; fi
echo -e [ Removed working directory: ${WORK_DIR} ] ${NC}
"""
