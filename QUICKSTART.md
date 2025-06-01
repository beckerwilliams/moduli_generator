# Quick Start

`moduli-assembly` provides functionality in-module and via exportable shell scripts to generate complete moduli files
with
five steps:

Preparation: Download project Wheel from GitHub

`curl -G
https://github.com/beckerwilliams/ssh-moduli-builder/raw/main/dist/moduli_assembly-0.10.12-py3-none-any.whl
-o moduli_assembly-<version>-py3-none-any.whl`

## Create and/or Startup Python venv

`python -m venv .venv`

`source .venv/bin/activate`

## Install moduli-assembly _wheel_

`pip install moduli_assembly-<version>-py3-none-any.whl`

## Export Bash Build Script

`python -m moduli_assembly.scripts.export_bash_builder > moduli_builder.sh`

## Make Shell Script Executable

`chmod +x moduli_builder.sh`

### Start Moduli Builder

`./moduli_builder.sh > mod.gen.log 2>&1 &`

## When Complete, Display Frequency Distribution of Created Moduli

`python -m moduli_assembly.scripts.moduli_infile [-f ${MODULI_ASSEMBLY_DIR}/MODULI_FILE`]

- where `${MODULI_ASSEMBLY_DIR} is ${HOME}/.moduli_assembly/MODULI_FILE by default`



