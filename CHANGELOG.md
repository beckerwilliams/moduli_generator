# Changelog

This document tracks the changes made to the moduli_generator project.

## Version 1.0.1

## 2025-08-09

* **Database Improvements**: Simplified Doc - Installation - Single Page, Complete Install (sans MariaDB Config)

## 2025-08-08

* **Documentation**: Doc Prep for .readthedocs

## 2025-08-07

* **Milestones**: Urgent Checkpoint - Temp directory picked up in GIT Push, Eliminating

## 2025-08-06

* **Bug Fixes**: Github_installer.py - Working of Fixes
* **Features**: Moduli_generator.ModuliGenerator - *ADDED* classmethod `write_install_script(self)`
  **General**:

    * Pyproject.toml - Down leveled poetry to v1.8.3 - Reformatted from `project` to `tool.poetry` syntax
    * POETRY and INSTALL Refresh

* **Milestones**: Checkpoint

## 2025-08-05

* **Documentation**: Checkpoint - Documentation Re-Write in Progress

## 2025-08-02

* **Documentation**: Document Re-Write in Progress - MARIA.md - index.md - readme.md - about.md
* **Milestones**: Sat Checkpoint - Doc rewrite In Progress

## 2025-07-31

* **Configuration**: Config.__init__ - exporting ModuliConfig __version__
* **Refactoring**: Conversion to `mkdocs` from `Sphinx` - Refactoring for Cleanup in Progress

## 2025-07-30

* **Database Improvements**: Db.__init__ - Added `self.verify_schema` before __init__ closes
* **General**: Pytproject.toml - elimininated spurious entries in [depenedencies]

## 2025-07-29

**Features**:

* Test - Added test.test_cli_main.py - added add'l integration tests
* Config - DEFAULT_CANDIDATE_IDX_FILENAME_PATTERN new constant | identifies unfinished candidiate files for resumed
  screening

* **General**: .gitignore - eliminate pre-processed doc (/doc/**/*)

## 2025-07-28

* **Refactoring**: Moved Validator Functions to their appropropriate modules, Refactored TEST Suite to accomodate
  changes

## 2025-07-27

* **Configuration**: Config - reset moduli_generator home default to ${HOME}/.moduli_generator
  **Database Improvements**:

    * Config - refactored import of mariadb to accomodate lazy loading - __init__.py - db.__init__.py -
      moduli_generator.__init__.py
    * MariaDBConnector - .status2 - *Eliminated* - .status - Refactored, optimizing by iterating over keysizes in SQL
      rather than Python - Resulting implementation MUCH FASTER

## 2025-07-26

* **General**: Pyproject.toml - Removed final vestiges of tool.poetry. Using `project` instead to support `poetry` >
  2.1.0

## 2025-07-25

* **Features**: Pyproject.toml - Refactored to align with PEP 621 - Including automatic versioning - Implemented PEP
  440-compliant version
* **General**: Including CHANGELOG.rst in git image
* **Refactoring**: Config/__version__.py - Refactored to import version from importlib.metadata (for wheel
  installations)

## 2025-07-23

* **Bug Fixes**: Changelog_generator/__init__.py - Refactored, Fixed RST Header Line (Project) - Separated Class from
  main/test

## 2025-07-21

* **Features**: Moduli_generator.ModuliGenerator - ._generator_candidates_static()     - Added Validation Checking to
  key_length & nice_value - ._screen_candidates_static()       - Added Validation Checking to key_length & nice_value

## 2025-07-20

* **Bug Fixes**: Refactored Changelog into it's own module. - pyproject.toml fixed script 'changelog'
* **Database Improvements**: Db.scripts.moduli_stats.py
* **General**: Changelog_generator.py

## 2025-07-18

* **General**: Pyproject.toml

## 2025-07-17

* **Features**: Moduli_generator_github_install.sh - Create and Tested - Successfully installs Python virtual
  environment with Updated PIP and freshly built moduli_generator wheel
* **General**: Moduli_generator_github_install.sh - Refining Install - Looking Good!
* **Refactoring**: Significant Install Documentation Refactor

## Project Information

* **Project**: moduli_generator
* **Version**: 1.0.1
* **Description**: A secure, high-performance SSH moduli file generator with database integration for cryptographic key
  exchange operations
* **Author**: Ron Williams <becker.williams@gmail.com>
* **Repository**: https://github.com/beckerwilliams/moduli_generator.git
* **Homepage**: https://github.com/beckerwilliams/moduli_generator
* **License**: See LICENSE.md
