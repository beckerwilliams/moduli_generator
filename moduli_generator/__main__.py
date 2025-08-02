#!/usr/bin/env python3
"""
Entry point for running moduli_generator as a module with python -m moduli_generator
"""
from sys import exit

from moduli_generator.cli import main

if __name__ == "__main__":
    exit(main())
