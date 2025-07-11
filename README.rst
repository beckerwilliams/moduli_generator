SSH2 Moduli File Generator
==========================

Generate Complete and Secure `ssh moduli` files

Getting Started
    * `Dependencies`_
    * `Installation`_
    * `Usage`_
    * `License`_

Dependencies
############

- OpenSSH2 ssh-keygen, *supporting* ``-M generate`` *and* ``-M screen``
- Python version >=3.9
- OpenSSH version >=9.9p2
- OpenSSL version >=3.0.6

Overview
========

.. note:: *Elapsed to complete run is about 7* **days** *on an Intel Quad Core i7*

Capabilities
------------

Builds Complete /etc/ssh/moduli file

- python: ``python -m moduli_generator.cli``

Installation
------------

Platform Dependencies
~~~~~~~~~~~~~~~~~~~~~

SSH2 Moduli Generator depends on the SSH being installed and ssh-keygen available for Moduli production.

Install Wheel
~~~~~~~~~~~~~

In a working directory, Create a python virtual environment, install ssh-moduli-builder wheel, run.

- Create Virtual Environment
    - ``python -m venv .venv  # Create Virtual Environment``

- Install Wheel
    - ``pip install ./moduli_generator-<version>-py3-none-any.whl``

Usage
-----

RUN
~~~

- Start Virtual Environment
  - ``.venv/bin/activate``
  - ``.venv/bin/activate.sh``
  - or ``.venv/bin{.csh,.sh}``

Reference
---------

SSH Audit
~~~~~~~~~

`SSH Audit <https://github.com/jtesta/ssh-audit>`_

SSH Hardening Guides
~~~~~~~~~~~~~~~~~~~~

`SSH Hardening Guides <https://www.ssh-audit.com/hardening_guides.html>`_

HackTricks (SSH)
~~~~~~~~~~~~~~~~

`HackTricks <https://book.hacktricks.xyz/network-services-pentesting/pentesting-ssh>`_

On the Sufficient Number of Moduli by Keysize
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`On the Sufficient Number of Moduli by Keysize (grok): <https://x.com/i/grok/share/ioGsEbyEPkRYkfUfPMj1TuHgl>`_

License
-------

MIT License
~~~~~~~~~~~

`MIT License <#LICENSE>`_

Copyright (c) 2024, 2025 Ron Williams, General Partner, Becker Williams Trading General Partnership

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Database Integration
--------------------

SSH2 Moduli Generator now includes MariaDB integration for storing and retrieving moduli values. 
This allows for persistent storage of generated moduli across sessions.

Database Setup
~~~~~~~~~~~~~~

1. Configure the database connection in ``moduli_generator.cnf``
2. The database automatically stores screened moduli values
3. Timestamps are stored in compressed format (no punctuation or spaces)

Retrieving Moduli from Database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When using the ``--write`` option, the generator will:

- Verify sufficient records exist for each key size (minimum 80 per size)
- Only create the moduli file if all sizes have enough entries
- Randomly select entries from the database to create a balanced moduli file

Technical Details
-----------------

Timestamp Format
~~~~~~~~~~~~~~~~

All timestamps in generated moduli files use a compressed format with no punctuation or spaces.
This ensures compatibility with all SSH implementations while maintaining proper chronological ordering.

Database Schema
~~~~~~~~~~~~~~~

The generator uses a view-based database schema that joins moduli values with their configuration constants.
This approach allows for efficient retrieval and consistent formatting of moduli entries.