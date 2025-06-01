#!/usr/bin/env python3

import argparse
from pathlib import Path
from typing import (Dict, List, Optional)

from moduli_assembly import ModuliAssembly  # Assuming this is correct, adjust if necessary
from moduli_assembly.scripts.moduli_infile import moduli_infile


def cl_args() -> argparse.ArgumentParser:
    """
    Set up command-line arguments for the Moduli Assembly utility.

    :return: Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(prog='Moduli Assembly',
                                     description='Utility to automate creation of SSH2 Moduli Files')

    me_group = parser.add_mutually_exclusive_group()
    ## Mutually Exclusive Options go in GROUP
    # Moduli Generation Functions

    me_group.add_argument('-C', '--remove-config-dir', action='store_true', help='Delete configuration directory.')
    me_group.add_argument('-D', '--moduli-distribution', action='store_true',
                          help='Print frequency distribution of the given moduli file.')
    me_group.add_argument('-M', '--display-moduli-frequencies', action='store_true',
                          help='Show Production Stats of moduli_assembly')
    me_group.add_argument('-a', '--all', action='store_true', help='Generate moduli for all supported it sizes')
    me_group.add_argument('-b', '--bitsizes', nargs='*', type=int, help='Space-delimited list of modulus sizes')
    me_group.add_argument('-r', '--restart', action='store_true',
                          help='Restart interrupted moduli screening. Ignores `-b, -a, -all')

    me_group.add_argument('-w', '--generate-moduli-file', action='store_true',
                          help='Write moduli to .moduli/MODULI_FILE from current screened files and exit.')
    me_group.add_argument('-x', '--export-config', action='store_true', help="Print running configuration.")

    # Universal parameters - Available to all functions above
    parser.add_argument('-c', '--clear-artifacts', action='store_true',
                        help="Clear generated candidate and screening files.")
    parser.add_argument('-f', '--config-file', default=Path.home() / '.moduli_assembly' / 'config_file', type=Path,
                        help='Select Moduli File Path, default=$HOME/.moduli_assembly/config_file')
    parser.add_argument('-m', '--moduli-dir', default=Path.home() / '.moduli', type=Path, )
    parser.add_argument('-V', '--version', action='store_true', help='Display moduli-assembly version.')

    return parser


def main() -> None:
    """
    Main entry point for all Moduli Assembly operations.
    """
    parser = cl_args()
    args = parser.parse_args()

    if args.config_file.exists():
        cm = ModuliAssembly(config={'config_file': args.config_file.read_text()}, root_dir=args.moduli_dir)
    else:
        cm = ModuliAssembly()

    # Exclusive Functions
    if args.remove_config_dir:
        # Delete Config Directory At START (Refresh)
        cm = ModuliAssembly()
        try:
            cm.remove_config()
        except Exception as e:
            print(f"Error removing config directory: {e}")
        return

    if args.export_config:
        cm.print_config()
        return

    if args.moduli_distribution:
        try:
            moduli_infile(cm.config['moduli_file'])
        except Exception as e:
            print(f'Error displaying moduli distribution: {e}')

    if args.generate_moduli_file:
        # Compile stored moduli into new MODULI_FILE
        try:
            cm.create_moduli_file(cm.config['moduli_file'])
            print(f'Wrote moduli file to {cm.config["moduli_file"]} and exiting.')
        except Exception as e:
            print(f"Error creating moduli file: {e}")
        return

    if args.restart:
        print('Restarting candidate screening')
        cm.restart_candidate_screening()
        cm.create_moduli_file()
        return

    # Non-exclusive arguments - handle FIRST
    if args.version:
        print(f'{parser.prog}: Version: {cm.version}')

    if args.clear_artifacts:
        try:
            cm.clear_artifacts()
            print(f'Artifacts Cleared: {cm.config["config_dir"] / cm.config["moduli_dir"]}')
        except Exception as e:
            print(f"Error clearing artifacts: {e}")

    # Now Handle actual Production
    if args.bitsizes or args.all:

        bitsizes = args.bitsizes if args.bitsizes else list(cm.config['auth_bitsizes']) if args.all else None
        if not bitsizes:
            print('ERROR: No bitsizes specified. Use -a, -b, or -r')
            return

        bitsizes.sort()

        run_bits: Dict[int, int] = {}
        for key_length in bitsizes:
            if key_length not in cm.config['auth_bitsizes']:
                print(f'Bitsize {key_length} is not enabled. Available: {cm.config["auth_bitsizes"]}')
                return
            run_bits[key_length] = run_bits.get(key_length, 0) + 1

        candidates: List[Optional[Path]] = []
        for key_length, count in run_bits.items():
            candidates.extend([cm.generate_candidates(key_length, count) for _ in range(count)])

        screened_file_path = cm.config["config_dir"] / 'screened-files.txt'
        with screened_file_path.open('a') as cf:
            for candidate in candidates:
                if candidate:
                    cf.write(f'Screened File: {cm.get_screened_path(candidate)}\n')

        for candidate in candidates:
            if candidate:
                cm.screen_candidates(candidate)

        cm.create_moduli_file()

        return


if __name__ == '__main__':
    main()
