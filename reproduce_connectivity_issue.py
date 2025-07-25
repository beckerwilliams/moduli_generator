#!/usr/bin/env python3
"""
Script to reproduce the test connectivity issue.

This script demonstrates that tests are passing but not testing production code,
resulting in 0% coverage of production modules despite 100% test pass rate.
"""

import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a command and capture its output."""
    print(f"\n{'=' * 60}")
    print(f"RUNNING: {description}")
    print(f"COMMAND: {cmd}")
    print('=' * 60)

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        print(f"RETURN CODE: {result.returncode}")
        return result
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def main():
    """Demonstrate the test connectivity issue."""

    print("MODULI GENERATOR - TEST CONNECTIVITY ISSUE REPRODUCTION")
    print("=" * 60)
    print("This script demonstrates that tests pass but don't test production code")

    # 1. Show current test imports
    print(f"\n1. CURRENT PROBLEMATIC IMPORTS:")
    print("-" * 40)

    # Show the problematic import in test_parameter_validation.py
    try:
        with open('test/test_parameter_validation.py', 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[13:18], 14):  # Lines 14-18
                print(f"Line {i}: {line.rstrip()}")
    except FileNotFoundError:
        print("test/test_parameter_validation.py not found")

    # Show that test_cli_argument_parsing.py has no CLI imports
    print(f"\n2. MISSING CLI IMPORTS:")
    print("-" * 40)
    try:
        with open('test/test_cli_argument_parsing.py', 'r') as f:
            lines = f.readlines()
            print("First 15 lines of test_cli_argument_parsing.py:")
            for i, line in enumerate(lines[:15], 1):
                print(f"Line {i}: {line.rstrip()}")
    except FileNotFoundError:
        print("test/test_cli_argument_parsing.py not found")

    # 3. Show that local test implementations exist
    print(f"\n3. LOCAL TEST IMPLEMENTATIONS:")
    print("-" * 40)
    if os.path.exists('test/parameter_validation.py'):
        print("✗ FOUND: test/parameter_validation.py (duplicate implementation)")
        print("  This file duplicates moduli_generator/validators.py functionality")
    else:
        print("✓ test/parameter_validation.py not found")

    # 4. Run tests to show they pass
    print(f"\n4. RUNNING TESTS (should pass but test wrong code):")
    print("-" * 40)
    test_result = run_command(
        "python -m pytest test/test_parameter_validation.py -v",
        "Run parameter validation tests"
    )

    # 5. Run coverage to show 0% production coverage
    print(f"\n5. RUNNING COVERAGE ANALYSIS:")
    print("-" * 40)
    coverage_result = run_command(
        "python -m pytest test/test_parameter_validation.py --cov=moduli_generator --cov=db --cov=config --cov-report=term-missing",
        "Run coverage analysis on production modules"
    )

    # 6. Show production code exists and is robust
    print(f"\n6. PRODUCTION CODE EXISTS AND IS ROBUST:")
    print("-" * 40)
    if os.path.exists('moduli_generator/validators.py'):
        print("✓ FOUND: moduli_generator/validators.py (production implementation)")
        try:
            with open('moduli_generator/validators.py', 'r') as f:
                lines = f.readlines()
                print(f"  - {len(lines)} lines of production code")
                print(f"  - Contains: {lines[0].strip()}")  # __all__ declaration
        except Exception as e:
            print(f"  - Error reading file: {e}")
    else:
        print("✗ moduli_generator/validators.py not found")

    if os.path.exists('moduli_generator/cli.py'):
        print("✓ FOUND: moduli_generator/cli.py (production CLI)")
    else:
        print("✗ moduli_generator/cli.py not found")

    # 7. Summary
    print(f"\n7. ISSUE SUMMARY:")
    print("-" * 40)
    print("PROBLEM: Tests import from test directory, not production code")
    print("IMPACT:")
    print("  - Tests pass (100% success rate)")
    print("  - But test local implementations, not production code")
    print("  - Production modules show 0% coverage")
    print("  - Creates false confidence in code quality")
    print("")
    print("SOLUTION: Update imports to use production modules:")
    print("  - Change: from parameter_validation import ...")
    print("  - To: from moduli_generator.validators import ...")
    print("  - Add: from moduli_generator.cli import main")
    print("  - Remove: sys.path.insert() manipulations")


if __name__ == "__main__":
    main()
