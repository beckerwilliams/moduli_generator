Boostrap Dev Installer
======================
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

Configure
=========

Copy the installer script *(below)*, into a file named ``install_gm.sh``.
Place the file in the desired ``./WorkDir``

Set the file's `execute` bit.

.. code-block:: bash

    chmod +x ${WorkDir}/install_gm.sh

And build the runtime

.. code-block:: bash

    cd ${WorkDir}
    ./install_gm.sh

At completion, you will have a python virtual environment located at ${WorkDir}/.venv. To activate, type:

.. code-block:: bash

    source .venv/bin/activate

There will also be two log files.

The first is the output of the ``build wheel`` session, where the installer builds the moduli_generator wheel file.

*build wheel response:*

.. literalinclude:: EXAMPLE_INSTALL_RESPONSE.txt
    :language: bash

The second is the output of the ``create runtime`` section, that displays the creation results of the runtime python environment for modui generator.

*create runtime response:*

.. literalinclude:: EXAMPLE_INSTALL_LOG.txt
    :language: bash

*install_gm.sh*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: install_gm.sh
    :language: bash
