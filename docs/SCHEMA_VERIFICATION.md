# Schema Verification

This document describes the schema verification functionality for the moduli generator database.

## Overview

The `verify_schema()` method in the `MariaDBConnector` class provides comprehensive verification of the database schema
installation. It checks for the existence and proper configuration of all required database objects.

## What is Verified

The schema verification function checks:

### Database

- **moduli_db** - Main database existence

### Tables

- **mod_fl_consts** - Configuration constants table
- **moduli** - Main moduli storage table
- **moduli_archive** - Archive table for processed moduli

### Views

- **moduli_view** - Combined view of moduli and configuration data

### Indexes

- **idx_size** - Index on moduli.size column
- **idx_timestamp** - Index on moduli.timestamp column
- **idx_size_archive** - Index on moduli_archive.size column
- **idx_timestamp_archive** - Index on moduli_archive.timestamp column

### Foreign Key Constraints

- **moduli.config_id → mod_fl_consts.config_id**
- **moduli_archive.config_id → mod_fl_consts.config_id**

### Configuration Data

- Presence of required configuration records in mod_fl_consts table

## Usage

### Basic Usage

```python
from db import MariaDBConnector
from config import default_config

# Create connector instance
connector = MariaDBConnector(default_config)

# Run schema verification
results = connector.verify_schema()

# Check overall status
if results['overall_status'] == 'PASSED':
    print("Schema verification passed!")
elif results['overall_status'] == 'PASSED_WITH_WARNINGS':
    print("Schema verification passed with warnings")
else:
    print("Schema verification failed!")
```

### Detailed Results Analysis

```python
# Check specific components
if results['database_exists']:
    print("Database exists")

# Check tables
for table, exists in results['tables'].items():
    if exists:
        print(f"Table {table}: OK")
    else:
        print(f"Table {table}: MISSING")

# Check views
for view, exists in results['views'].items():
    if exists:
        print(f"View {view}: OK")
    else:
        print(f"View {view}: MISSING")

# Check indexes
for index, exists in results['indexes'].items():
    if exists:
        print(f"Index {index}: OK")
    else:
        print(f"Index {index}: MISSING")

# Check foreign keys
for fk, exists in results['foreign_keys'].items():
    if exists:
        print(f"Foreign Key {fk}: OK")
    else:
        print(f"Foreign Key {fk}: MISSING")

# Check configuration data
if results['configuration_data']:
    print("Configuration data: OK")
else:
    print("Configuration data: MISSING")
```

### Error and Warning Handling

```python
# Display errors
if results['errors']:
    print("Errors found:")
    for error in results['errors']:
        print(f"  - {error}")

# Display warnings
if results['warnings']:
    print("Warnings:")
    for warning in results['warnings']:
        print(f"  - {warning}")
```

## Return Value Structure

The `verify_schema()` method returns a dictionary with the following structure:

```python
{
    'database_exists': bool,           # True if database exists
    'tables': {                        # Table existence status
        'mod_fl_consts': bool,
        'moduli': bool,
        'moduli_archive': bool
    },
    'views': {                         # View existence status
        'moduli_view': bool
    },
    'indexes': {                       # Index existence status
        'idx_size': bool,
        'idx_timestamp': bool,
        'idx_size_archive': bool,
        'idx_timestamp_archive': bool
    },
    'foreign_keys': {                  # Foreign key constraint status
        'moduli -> mod_fl_consts.config_id': bool,
        'moduli_archive -> mod_fl_consts.config_id': bool
    },
    'configuration_data': bool,        # True if config data exists
    'overall_status': str,             # 'PASSED', 'PASSED_WITH_WARNINGS', 'FAILED', or 'ERROR'
    'errors': [str],                   # List of error messages
    'warnings': [str]                  # List of warning messages
}
```

## Status Values

- **PASSED** - All components verified successfully
- **PASSED_WITH_WARNINGS** - All critical components exist, but some non-critical issues found
- **FAILED** - One or more critical components missing
- **ERROR** - Exception occurred during verification

## Command Line Usage

You can create a simple script to verify the schema:

```python
#!/usr/bin/env python3
from db import MariaDBConnector
from config import default_config


def main():
    try:
        connector = MariaDBConnector(default_config)
        results = connector.verify_schema()

        print(f"Schema verification: {results['overall_status']}")

        if results['errors']:
            print("Errors:")
            for error in results['errors']:
                print(f"  - {error}")

        if results['warnings']:
            print("Warnings:")
            for warning in results['warnings']:
                print(f"  - {warning}")

    except Exception as e:
        print(f"Verification failed: {e}")


if __name__ == "__main__":
    main()
```

## Notes

- The verification function uses the database name from the configuration (default: 'moduli_db')
- Missing indexes are treated as warnings, not errors
- Missing tables, views, or foreign keys are treated as errors
- The function requires an active database connection
- All SQL queries use parameterized statements for security