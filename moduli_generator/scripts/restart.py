#!/usr/bin/env python
from sys import exit

# Import the default configuration
from config import default_config
from moduli_generator import ModuliGenerator


def main():
    """
    Main function to restart the screening process for moduli generation.
    Restarts the screening of previously generated candidates and stores the moduli.
    
    Returns:
        int: Exit code indicating the status of the operation. `0` for success,
             non-zero for failure.
    """
    try:
        result = ModuliGenerator(default_config()).restart_screening().store_moduli()
        return 0 if result else 1
    except Exception as e:
        print(f"Error restarting screening: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
