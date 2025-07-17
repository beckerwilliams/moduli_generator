#!/usr/bin/env bash
# moduli_generator
#
WORK_DIR=.tmp_mwork
GITHUB_PROJECT=https://github.com/beckerwilliams/moduli_generator.git
PYTHON="/usr/bin/env python"
MK_VENV="${PYTHON} -m venv"
VENV_DIR=.venv
POETRY="/usr/bin/env poetry"
ACTIVATE=".venv/bin/activate.sh"
MODULI_GENERATOR_DIR=moduli_generator
WHEEL_TARGET_DIR=${HOME}

CWD=$(pwd)
mkdir ${WORK_DIR}
cd ${WORK_DIR}

git clone ${GITHUB_PROJECT}
cd ${MODULI_GENERATOR_DIR}

${MK_VENV} ${VENV_DIR}
${ACTIVATE}

${POETRY} update
${POETRY} build
deactivate

wheel_file=$(ls dist/*.whl | cut -d/ -f2)
echo "Moduli Generator PIP Installable Wheel: ${WHEEL_TARGET_DIR}/${wheel_file}"
mv dist/${wheel_file} ${WHEEL_TARGET_DIR}/${wheel_file}

${MK_VENV} {VENV_DIR}
${ACTIVATE}
pip install pip --upgrade
pip install ${WHEEL_TARGET_DIR}/${wheel_file}
rm ${WHEEL_TARGET_DIR}/${wheel_file}

cd ${CWD}
rm -rf ${WORK_DIR} # Cleanup transients

