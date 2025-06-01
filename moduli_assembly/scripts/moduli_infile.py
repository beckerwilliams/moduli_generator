#!/usr/bin/env python
from argparse import ArgumentParser
from pathlib import PosixPath as Path


def args():
    parser = ArgumentParser(description='Moduli In File')
    parser.add_argument('-f', '--file', type=str, default='/etc/ssh/moduli',
                        help='moduli_infile -f <moduli_file')
    return parser.parse_args()


def moduli_infile(infile):
    """
    Determine Frequency Distribution of Moduli Keylengths in Local [/usr/local]/etc/ssh/moduli
    :param infile: Path to moduli file
    :type infile: PosixPath
    :return: Frequency Table of Moduli Keylengths in Selected moduli file
    :rtype: text
    """
    authorized_bitsizes = (2047, 3071, 4095, 6143, 7679, 8191)
    bitsizes = {}
    for bs in authorized_bitsizes:
        bitsizes[str(bs)] = 0

    if infile.exists():
        lines = infile.read_text().split('\n')
        for line in lines:
            if line.startswith('#') or line.startswith(' '):
                continue
            # Skip Comment and Blank Lines, Bypasses MODULI Header Line
            if line:
                bitsizes[line.split(' ')[4]] += 1

        return bitsizes
    else:
        print(f'Error: Provided moduli file, {infile.name}, Doesn\'t Exist')
        exit(1)


def main():
    largs = args()
    freq_table = moduli_infile(Path(largs.file))
    print(f'\nModulus Frequency of {largs.file}:')
    print(f'Mod  Count')
    for modulus in freq_table:
        print(modulus, freq_table[modulus])


if __name__ == '__main__':
    exit(main())
