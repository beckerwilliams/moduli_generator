============
Requirements
============

Pre-Install
-----------

You will need to verify the following applications are installed on your machine:
    - python v 3.12 *or higher*
    - git v 2.5
    - A MariaDB MYSQL Database 11.4.7 *not tested on now un-supported MySql DB*

You will need an active account on `Github <https://github.com/beckerwilliams/moduli_generator>`_, and a properly configured ~/.git-config and ~/.git-credentials to support command line use.

You will need to configure your MariaDB instance with the Moduli Generator Schema and user profile, prior to full operation. See `MARIADB`_

Install Moduli Generator Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- *Moduli Generator virtual environment*

The Installer

* clones the current project in a working directory
* builds an installable python wheel from the project source
* installs that wheel in a fresh virtual environment, ``.venv``
* eliminates install working directory and moduli_generator wheel

<Install Script Here or Somewhere>

Copy the installer script into a file named ``install_gm.sh``.

Name copied file ``install_gm.sh``, and make executable

.. code-block::

    chmod +x install_gm.sh

Place the file in a directory into which you want to install Moduli Generator virtual environment ``.venv``


Execute the Install

.. code-block::

    ./install_gm.sh

*response*

.. code-block::

    ron@dcrunch:~/MG_TEMP % ./install_mg.sh
    [ Saving Current Directory /home/ron/MG_TEMP, entering .moduli_generator_temp ]
    [ Cloning moduli_generator from Github ]
    [ Entering Moduli Dev Directory: moduli_generator ]
    [ Creating and Activating Python Virtual Enviroment in /home/ron/MG_TEMP/.moduli_generator_temp/moduli_generator ]
    [ Building moduli_generator wheel ]
    [ Copy Moduli Generator Wheel to starting directory: /home/ron/moduli_generator-2.1.12-py3-none-any.whl ]
    [ Creating runtime virtual environment ]
    [ Upgrading Virtual Environment and Installing Moduli Generator wheel: moduli_generator-2.1.12-py3-none-any.whl ]

*install.log*

.. code-block::

    Cloning into 'moduli_generator'...
    The lock file might not be compatible with the current version of Poetry.
    Upgrade Poetry to ensure the lock file is read properly or, alternatively, regenerate the lock file with the `poetry lock` command.
    Updating dependencies
    Resolving dependencies...

    Package operations: 27 installs, 0 updates, 0 removals

      - Installing certifi (2025.7.14)
      - Installing charset-normalizer (3.4.2)
      - Installing markupsafe (3.0.2)
      - Installing idna (3.10)
      - Installing urllib3 (2.5.0)
      - Installing alabaster (0.7.16)
      - Installing babel (2.17.0)
      - Installing imagesize (1.4.1)
      - Installing packaging (25.0)
      - Installing requests (2.32.4)
      - Installing docutils (0.21.2)
      - Installing pygments (2.19.2)
      - Installing jinja2 (3.1.6)
      - Installing snowballstemmer (3.0.1)
      - Installing sphinxcontrib-applehelp (2.0.0)
      - Installing sphinxcontrib-devhelp (2.0.0)
      - Installing sphinxcontrib-htmlhelp (2.1.0)
      - Installing sphinxcontrib-jsmath (1.0.1)
      - Installing sphinxcontrib-qthelp (2.0.0)
      - Installing sphinxcontrib-serializinghtml (2.0.0)
      - Installing sphinx (7.4.7)
      - Installing sphinxcontrib-jquery (4.1)
      - Installing configparser (7.2.0)
      - Installing mariadb (1.1.13)
      - Installing poetry-core (2.1.3)
      - Installing sphinx-rtd-theme (3.0.2)
      - Installing toml (0.10.2)

    Writing lock file
    Building moduli_generator (2.1.12)
      - Building sdist
      - Built moduli_generator-2.1.12.tar.gz
      - Building wheel
      - Built moduli_generator-2.1.12-py3-none-any.whl
    Requirement already satisfied: pip in ./.venv/lib/python3.12/site-packages (25.0.1)
    Collecting pip
      Using cached pip-25.1.1-py3-none-any.whl.metadata (3.6 kB)
    Using cached pip-25.1.1-py3-none-any.whl (1.8 MB)
    Installing collected packages: pip
      Attempting uninstall: pip
        Found existing installation: pip 25.0.1
        Uninstalling pip-25.0.1:
          Successfully uninstalled pip-25.0.1
    Successfully installed pip-25.1.1
    Processing ./moduli_generator-2.1.12-py3-none-any.whl
    Collecting configparser<8.0.0,>=7.2.0 (from moduli-generator==2.1.12)
      Using cached configparser-7.2.0-py3-none-any.whl.metadata (5.5 kB)
    Collecting mariadb<2.0.0,>=1.1.12 (from moduli-generator==2.1.12)
      Using cached mariadb-1.1.13-cp312-cp312-freebsd_14_3_stable_amd64.whl
    Collecting poetry-core<3.0.0,>=2.1.3 (from moduli-generator==2.1.12)
      Using cached poetry_core-2.1.3-py3-none-any.whl.metadata (3.5 kB)
    Collecting toml<0.11.0,>=0.10.2 (from moduli-generator==2.1.12)
      Using cached toml-0.10.2-py2.py3-none-any.whl.metadata (7.1 kB)
    Collecting packaging (from mariadb<2.0.0,>=1.1.12->moduli-generator==2.1.12)
      Using cached packaging-25.0-py3-none-any.whl.metadata (3.3 kB)
    Using cached configparser-7.2.0-py3-none-any.whl (17 kB)
    Using cached poetry_core-2.1.3-py3-none-any.whl (332 kB)
    Using cached toml-0.10.2-py2.py3-none-any.whl (16 kB)
    Using cached packaging-25.0-py3-none-any.whl (66 kB)
    Installing collected packages: toml, poetry-core, packaging, configparser, mariadb, moduli-generator

    Successfully installed configparser-7.2.0 mariadb-1.1.13 moduli-generator-2.1.12 packaging-25.0 poetry-core-2.1.3 toml-0.10.2

**moduli_generator_github_installer.sh**

.. code-block:: bash

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

    echo -e "${BLUE}[ Saving Current Directory ${CWD}, entering ${WORK_DIR} ] ${NC}"
    mkdir ${WORK_DIR} > "${LOG_FILE}"  2>&1
    cd ${WORK_DIR} > "${LOG_FILE}"  2>&1 || exit > "${LOG_FILE}"  2>&1

    echo -e ${BLUE}[ Cloning moduli_generator from Github ] ${NC}
    git clone ${GITHUB_PROJECT} > "${LOG_FILE}"  2>&1

    echo -e ${BLUE}[ Entering Moduli Dev Directory: ${MODULI_GENERATOR_DIR} ] ${NC}
    cd ${MODULI_GENERATOR_DIR} > "${LOG_FILE}"  2>&1 || exit

    # shellcheck disable=SC2046
    echo -e ${BLUE}[ Creating and Activating Python Virtual Enviroment in $(pwd) ] ${NC}
    ${MK_VENV} ${VENV_DIR} > "${LOG_FILE}"  2>&1
    ${ACTIVATE} > "${LOG_FILE}"  2>&1

    echo -e ${BLUE}[ Building moduli_generator wheel ] ${NC}
    ${POETRY} update > "${LOG_FILE}"  2>&1
    ${POETRY} build > "${LOG_FILE}"  2>&1
    deactivate > "${LOG_FILE}"  2>&1

    wheel_file=$(ls dist/*.whl | cut -d/ -f2)   > "${LOG_FILE}"  2>&1

    echo -e ${BLUE}[ Copy Moduli Generator Wheel to starting directory: "${WHEEL_TARGET_DIR}"/"${wheel_file}" ] ${NC}
    mv dist/"${wheel_file}" "${CWD}"/"${wheel_file}"   > "${LOG_FILE}"  2>&1
    cd "${CWD}" > "${LOG_FILE}"  2>&1 || exit   > "${LOG_FILE}"  2>&1

    echo -e ${BLUE}[ Creating runtime virtual environment ] ${NC}
    ${MK_VENV} ${VENV_DIR}  > "${LOG_FILE}"  2>&1

    ${ACTIVATE} > "${LOG_FILE}"  2>&1

    echo -e ${BLUE}[ Upgrading Virtual Environment and Installing Moduli Generator wheel: "${wheel_file}" ] ${NC}
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
    echo -e ${BLUE}[ Removed working directory: ${WORK_DIR} ] ${NC}
