#!/usr/bin/env python

def main():
    """

    :return: Text of Bash Shell Moduli Builder
    :rtype: text
    """
    print('''#!/usr/bin/env bash

    NICE="nice +15"
    GEN_MODULI="python -m moduli_assembly"
    GEN_OPTS="-b 3072 4096 6144 7680 8192"
    LOG="all.gen.log"

    rm $LOG
    touch $LOG

    # Four Runs of ssh-keygen Per Bitsize will generate a file with sufficient entries per bitsize (~80)
    for ((ii = 0; i < 4; i++)); do
      ${NICE} ${GEN_MODULI} ${GEN_OPTS} > $LOG 2>1
    done

    ''')


if __name__ == '__main__':
    exit(main())
