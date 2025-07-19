====================================
Install Moduli Generator Application
====================================

- *Moduli Generator virtual environment*

The Installer
-------------
* clones the current project in a working directory
* builds an installable python wheel from the project source
* installs that wheel in a fresh virtual environment, ``.venv``
* eliminates install working directory and moduli_generator wheel

Requirements
============

You will need to verify the following applications are installed on your machine:
    - **python v 3.12** *or higher*
    - **git v 2.5**
    - A **MariaDB MYSQL Database 11.4.7**
        not tested on un-supported MySql DB

You will need an active account on `Github <https://github.com/beckerwilliams/moduli_generator>`_, and properly configured

    ``~/.git-config``

    ``~/.git-credentials``


You will need to configure your MariaDB instance with the Moduli Generator Schema and user profile, prior to full operation. See `MARIADB`_

----

Configure Installer
===================


Copy the installer script into a file named ``install_gm.sh``, and make executable

.. code-block::

    chmod +x install_gm.sh

Place (`move`) the copied file in a directory into which you want to install Moduli Generator virtual environment.

.. code-block:: bash

    cp <obtained_installer> <selected dir>/install_gm.sh

Start the Install

.. code-block::

    ./install_gm.sh

*response*

.. literalinclude:: EXAMPLE_INSTALL_RESPONSE.txt
    :language: bash


*install.log*

.. literalinclude:: EXAMPLE_INSTALL_LOG.txt
    :language: bash

**moduli_generator_github_installer.sh**

.. literalinclude:: moduli_generator_github_installer.sh
   :language: bash
