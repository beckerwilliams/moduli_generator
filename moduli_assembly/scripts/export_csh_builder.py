#!/usr/bin/env python

def main():
    """

    :return: Text of Bash Shell Moduli Builder
    :rtype: text
    """
    print('''#!/usr/bin/env csh
    
    set NICE="nice +15"
    set GEN_MODULI="python -m moduli_assembly"
    set GEN_OPTS="--all"
    set LOG="all.gen.log"
    
    # Four Runs of ssh-keygen Per Bitsize will generate a file with sufficient entries per bitsize (~80)
    rm $LOG
    touch $LOG
    foreach run ( 0 1 2 3 )
        $NICE $GEN_MODULI $GEN_OPTS >>& $LOG&
    end
    ''')


if __name__ == '__main__':
    exit(main())
