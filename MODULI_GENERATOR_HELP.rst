---------------------------------------------------------
moduli_generator.cli:main -h
---------------------------------------------------------

usage: cli.py [-h] \

        [--key-lengths KEY_LENGTHS [KEY_LENGTHS ...]] \

        [--moduli-home MODULI_HOME] \

        [--candidates-dir CANDIDATES_DIR] \

        [--moduli-dir MODULI_DIR] \

        [--log-dir LOG_DIR] \

        [--mariadb-cnf MARIADB_CNF] \

        [--nice-value NICE_VALUE] \

        [--records-per-keylength RECORDS_PER_KEYLENGTH]

Moduli Generator - Generate and manage secure moduli for cryptographic operations``

:options:
  -h, --help            show this help message and exit
  --key-lengths KEY_LENGTHS [KEY_LENGTHS ...]
                        Space-separated list of key lengths to generate moduli for (default: (3072, 4096, 6144, 7680, 8192))
  --moduli-home MODULI_HOME
                        Base directory for moduli generation and storage (default: ${HOME}/.moduli_generator)
  --candidates-dir CANDIDATES_DIR
                        Directory to store candidate moduli (relative to moduli-home) (default: .candidates)
  --moduli-dir MODULI_DIR
                        Directory to store generated moduli (relative to moduli-home) (default: .moduli)
  --log-dir LOG_DIR     Directory to store log files (relative to moduli-home) (default: .logs)
  --mariadb-cnf MARIADB_CNF
                        Path to MariaDB configuration file (relative to moduli-home) (default: moduli_generator.conf)
  --nice-value NICE_VALUE
                        Process nice value for CPU inensive operations (default: 15)
  --records-per-keylength RECORDS_PER_KEYLENGTH

