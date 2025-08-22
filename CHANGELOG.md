# Changelog

This document tracks the changes made to the moduli_generator project.

## Version 1.0.1

## 2025-08-22

* **Features**: Config.ModuliGenerator - Refactored to emit `default_config` as a `function` that returns the
  default_config, instead of a pointer to an already created default_config - Modified all usages of `default_config` to
  assure function is invoked and results in `instance`

## 2025-08-20

**Database Improvements**:

* Db.utils - Eliminated unneceeary dynamic load for db_name, db_password
* Db.utils - fixed missing and `password=password` parameter in `getmoduli_generator_db_schema_statements` to support
  InstallSchema syntax
* Db.utils - fixed missing `password=password` parameter
* Db.utils - Fixed incorrect reference to `self.db_name`. Should be (is now) just `db_name`
* Db.utils - Chaned typing on InstallSchema imports from Function to Callable[[str], List[Dict[str, Any]]]
* Db.utils.get_moduli_generator_user_schema_statements - Creating ./moduli_generator/moduli_generator.cnf configuratoin
  file
* Db - Type's set Constants - Updated function docstrings

* **Documentation**: Docs/installation/install_logs.md - Capture Example Install Logs
  **Features**:

    * Data/bash_scripts/install_mg.sh - Added `create_application_cnf`
    * Data.bash_scripts.install_wcnf_mg.sh - Created to take installation credentials from existing CNF, rather than
      usesrname, password, host

## 2025-08-19

* **Configuration**: Package Configuration Tests - Multi-Commit
  **Database Improvements**:

    * Db.utils.get_moduli_generator_user_schema_statements - Removed failing PROXY Grant (need root user!)
    * Install_moduli_generator_schema.py - Fixed typo causing `install_schema` to fail
    * Db - Refactored to separate test mocks from production code - Remedidated all Tests

**General**:

* Doc Rebuild
* Revert "Doc Rebuild"


## 2025-08-18

* **Database Improvements**: Db.scripts.simple_schema_installer.py - Operational and Optimized

## 2025-08-17

* **Milestones**: ** Checkpoint **

## 2025-08-16

* **Releases**: Reset project versioning, pre-Release, to 1.0.1 Removed --no-cache-dir from script `pip` usage

## 2025-08-15

* **Database Improvements**: Install_schema.py - Properly Handles Install Case and switching fromTemporarty Privileged
  Credentials to app owner 'moduli_generator'
* **General**: ** Version Bump **
* **Refactoring**: Test Suites refactored for recent changes in source. - All Tests Successful

## 2025-08-14

**Database Improvements**:

* Install_schema.py - generate_random_passwords : modified to use MariaDB Safe Characters (We were failing with quotes,
  double quotes, and backslash)
* Install_mg.sh - Completed Consolidation of App Install and DB Integration from One Script - testing

* **General**: Re-established --restart - Validated Poetry Scripts - All Operational
* **Testing**: Command line installer operationally successful!

## 2025-08-10

* **Database Improvements**: Docs/database/mariadb.md - Refactoring DB Integration
* **General**: Moduli_generator.ModuliGenerator - eliminated json `save` function (unnecessary)

## 2025-08-09

* **Database Improvements**: Simplified Doc - Installation - Single Page, Complete Install (sans MariaDB Config)

## 2025-08-08

* **Documentation**: Doc Prep for .readthedocs

## 2025-08-07

* **Milestones**: Urgent Checkpoint - Temp directory picked up in GIT Push, Eliminating

## Project Information

* **Project**: moduli_generator
* **Version**: 1.0.1
* **Description**: A secure, high-performance SSH moduli file generator with database integration for cryptographic key
  exchange operations
* **Author**: Ron Williams <becker.williams@gmail.com>
* **Repository**: https://github.com/beckerwilliams/moduli_generator.git
* **Homepage**: https://github.com/beckerwilliams/moduli_generator
* **License**: See LICENSE.md
