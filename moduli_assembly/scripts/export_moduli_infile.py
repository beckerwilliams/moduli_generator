#!/usr/bin/env python

def main():
    """

    :return: Text of Bash Shell Moduli Builder
    :rtype: text
    """
    print('''#!/usr/bin/env bash
    
    WCL="/usr/bin/wc -l"
    GREP=/usr/bin/grep
    MODULI_FILE=${1:-/etc/ssh/moduli}
    
    echo "\nProcessing Moduli File: ${MODULI_FILE}"
    
    for moduli in 2047 3071 4095 6143 7679 8191
    do
        count=`$GREP " $moduli " $MODULI_FILE | $WCL`
        echo "${moduli}: ${count}"
    done
    
    ''')


if __name__ == '__main__':
    exit(main())
