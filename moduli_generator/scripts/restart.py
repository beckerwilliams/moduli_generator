#!/usr/bin/env python
from sys import exit

# Import the default configuration
from moduli_generator import ModuliGenerator

if __name__ == "__main__":
    exit((ModuliGenerator(default_config()).restart_screening().store_moduli()))
