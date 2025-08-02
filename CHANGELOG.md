# Changelog

This document tracks the changes made to the moduli_generator project.

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

## 2025-07-16

* **Bug Fixes**: Testing Installer - Fixing script definitions (moduli_stats)
* **Documentation**: Build_docs.py - main() | Changed Output Directory to ${project_root}/docs, from $
  {project_root}/moduli_generator/docs

## 2025-07-15

* **Database Improvements**: Cleaned up MariaDBConnector.stats() function to output human readable data
* **Milestones**: * Checkpoint *

## 2025-07-14

* **Database Improvements**: * MariadbConnector.get_and_write_moduli_file Uniquifying key_lengths list, and ordering by
  key length. Stop producing more than DEFAULT_RECORDS_PER_KEYLENGTH
* **General**: Moduli_generator.cli

## 2025-07-12

* **Database Improvements**: Refactoring Documentation - In Progress tbd * Database Integration
  **Features**:

    * Committing new RST Files
    * Adding function 'main' to 'generate_changelog' in pyproject.toml specification

## 2025-07-11

* **Features**: Refactored Changelog Processing will full featured changelog_generator.py. (Thank you Claude 4 Sonnet)

## 2025-07-10

* **Database Improvements**: Converted MariaDBConnector to context_manager and modified methods for proper transactional
  handling

## 2025-07-09

* **Releases**: Candidate Release w/ PRODUCTION ARGUMENTS

## Project Information

* **License**: See LICENSE.md
