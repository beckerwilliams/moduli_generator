=========
Packaging
=========

``build wheel``
---------------

Dependencies
~~~~~~~~~~~~

- python ^3.11
- poetry ^1.8.2

Initialization
--------------

To Start a Moduli Builder, Clone ssh-moduli-builder project:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ``git clone https://github.com/beckerwilliams/moduli_generator.git``

Navigate to project
~~~~~~~~~~~~~~~~~~~

    ``cd moduli_generator``

Install dependencies
~~~~~~~~~~~~~~~~~~~~

    ``poetry install``

Update poetry
~~~~~~~~~~~~~

    ``poetry update``

Generate ``sdist`` and ``wheel`` distros
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ``poetry build``

Resulting distributions will be found in the ./dist directory