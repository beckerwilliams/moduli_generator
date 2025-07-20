Moduli Generator Application Installer
======================================

The Installer
-------------
* clones current github repo,
* creates new virtual environment and installs freshly built wheel
* builds an installable python wheel from the project source
* installs that wheel in a fresh virtual environment

Requirements
============

*Verify* the following applications are installed on your machine:
    - **python v 3.12** *or higher*
    - **git v 2.5**

Verify that you have cli (`git`) access to `Github <https://github.com/beckerwilliams/moduli_generator>`_.

Note:
    Moduli Generator can be installed and configured without Maria DB installed and available. You will need to Install Maria DB and the Moduli Generator Schema prior to operation. See `MARIADB`_

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
