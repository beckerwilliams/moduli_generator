#!/usr/bin/env python
from moduli_generator import ModuliGenerator


def doItAll():
    """
    The simplest invocation with which to create a moduli file
    """
    (ModuliGenerator()
     .generate_moduli()
     .save_moduli()
     .store_moduli()
     .write_moduli())


if __name__ == "__main__":
    doItAll()
