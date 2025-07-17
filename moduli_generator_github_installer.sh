#!/usr/bin/env bash
# moduli_generator installer
#
# Creates a virtual environment in user's HOME directory
#
# Text colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color (reset)

WORK_DIR=.moduli_generator_temp
GITHUB_PROJECT=https://github.com/beckerwilliams/moduli_generator.git
PYTHON="/usr/bin/env python"
MK_VENV="${PYTHON} -m venv"
VENV_DIR=.venv
POETRY="/usr/bin/env poetry"
ACTIVATE="source .venv/bin/activate"
MODULI_GENERATOR_DIR=moduli_generator
WHEEL_TARGET_DIR=${HOME}

CWD=$(pwd)
LOG_FILE=${CWD}/install.log

echo -e "${BLUE}[Saving Current Directory ${CWD}, entering ${WORK_DIR}] ${NC}"
mkdir ${WORK_DIR} > "${LOG_FILE}"  2>&1
cd ${WORK_DIR} > "${LOG_FILE}"  2>&1 || exit > "${LOG_FILE}"  2>&1

echo -e ${BLUE}[Cloning moduli_generator from Github] ${NC}
git clone ${GITHUB_PROJECT} > "${LOG_FILE}"  2>&1

echo -e ${BLUE}[Entering Moduli Dev Directory: ${MODULI_GENERATOR_DIR} ${NC}
cd ${MODULI_GENERATOR_DIR} > "${LOG_FILE}"  2>&1 || exit

# shellcheck disable=SC2046
echo -e ${BLUE}[Creating and Activating Python Virtual Enviroment in $(pwd)] ${NC}
${MK_VENV} ${VENV_DIR} > "${LOG_FILE}"  2>&1
${ACTIVATE} > "${LOG_FILE}"  2>&1

echo -e ${BLUE}[Building moduli_generator wheel] ${NC}
${POETRY} update > "${LOG_FILE}"  2>&1
${POETRY} build > "${LOG_FILE}"  2>&1
deactivate > "${LOG_FILE}"  2>&1

wheel_file=$(ls dist/*.whl | cut -d/ -f2)   > "${LOG_FILE}"  2>&1

echo -e ${BLUE}[Copy Moduli Generator Wheel to starting directory: "${WHEEL_TARGET_DIR}"/"${wheel_file}"] ${NC}
mv dist/"${wheel_file}" "${CWD}"/"${wheel_file}"   > "${LOG_FILE}"  2>&1
cd "${CWD}" > "${LOG_FILE}"  2>&1 || exit   > "${LOG_FILE}"  2>&1

echo -e ${BLUE}[Creating runtime virtual environment] ${NC}
${MK_VENV} ${VENV_DIR}  > "${LOG_FILE}"  2>&1

${ACTIVATE} > "${LOG_FILE}"  2>&1

echo -e ${BLUE}[Upgrading Virtual Environment and Installing Moduli Generator wheel: "${wheel_file}"] ${NC}
pip install pip --upgrade  > "${LOG_FILE}"  2>&1

pip install "${CWD}"/"${wheel_file}"  > "${LOG_FILE}"  2>&1
rm "${CWD}"/"${wheel_file}"  > "${LOG_FILE}"  2>&1
rm -rf ${WORK_DIR}  > "${LOG_FILE}"  2>&1  # Cleanup transients

echo
echo -e ${GREEN}Moduli Generator Installed Successfully to ${CWD}${NC}
pip list

# CLEANUP
deactivate

if [ "${CWD}" != "/" ]; then rm -rf "${CWD}"/"${wheel_file}" > "${LOG_FILE}" 2>&1 ; fi
echo -e ${BLUE}[Removed working directory: ${WORK_DIR}] ${NC}
