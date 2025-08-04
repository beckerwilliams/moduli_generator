# `Moduli Generator` usage

```
moduli_generator [-h] [--candidates-dir CANDIDATES_DIR] [--key-lengths KEY_LENGTHS [KEY_LENGTHS ...]] [--log-dir LOG_DIR] [--mariadb-cnf MARIADB_CNF] [--moduli-dir MODULI_DIR] [--moduli-home MODULI_HOME] [--moduli-db MODULI_DB] [--nice-value NICE_VALUE] [--records-per-keylength RECORDS_PER_KEYLENGTH] [--preserve-moduli-after-dbstore]
                        [--delete-records-on-moduli-write]

Moduli Generator - Generate and manage secure moduli for cryptographic operations

options:
  -h, --help            show this help message and exit
  --candidates-dir CANDIDATES_DIR
                        Directory to store candidate moduli (relative to moduli-home) (default: .candidates)
  --key-lengths KEY_LENGTHS [KEY_LENGTHS ...]
                        Space-separated list of key lengths to generate moduli for (default: (3072, 4096, 6144, 7680, 8192))
  --log-dir LOG_DIR     Directory to store log files (relative to moduli_home) (default: .logs)
  --mariadb-cnf MARIADB_CNF
                        Path to MariaDB configuration file (relative to moduli_home) (default: moduli_generator.cnf)
  --moduli-dir MODULI_DIR
                        Directory to store generated moduli (relative to moduli_home) (default: .moduli)
  --moduli-home MODULI_HOME
                        Base directory for moduli generation and storage (default: /home/ron/.moduli_generator)
  --moduli-db MODULI_DB
                        Name of the database to create and Initialize (default: moduli_db)
  --nice-value NICE_VALUE
                        Process nice value for CPU intensive operations (default: 15)
  --records-per-keylength RECORDS_PER_KEYLENGTH
                        Number of moduli per key-length to capture in each produced moduli file (default: 20)
  --preserve-moduli-after-dbstore
                        Delete records from DB written to moduli file (default: False)
  --delete-records-on-moduli-write
                        Delete records on moduli write (default: False)
```

# Do it all

```bash
moduli_generator&
```

# Default Run Properties

The sole objective of `moduli_generator` is to produce *unique and secure* SSH2 Moduli Files.

The default configuration will produce a complete `/etc/ssh/moduli` file, comprised of 20 moduli for each of 5
key-sizes, `3072`, `4096`, `6144`, `7680`, and `8192` in about Sixty (60) hours on a quad-core i7 processor.

## /etc/ssh/moduli

```bash
# aragorn.local::ModuliGenerator: ssh2 moduli generated at 2025-07-28T02:25:52.957733Z
# timestamp,type,tests,trials,size,generator,moduli
20241110031151 2 6 100 3071 2 C8053358B1E47DCB826BA2BCB616739EE826ADB273504CF89F8CF6F5A9946B5576F66A07012DCC10557 ...
...
20241110060903 2 6 100 4095 2 C92D504439184AF104BD1EB6B99B7DF5339FD2323BB478F5BCEA801424F6315AD0A7D403AF3A3709D2F ...
...
20241110071459 2 6 100 6143 2 DD1A312259F4DF35F5C20EB8521AA221893A3AF334A093F89E35F1E6EE67D964274532E2D746FA0457E ...
...
20241111144509 2 6 100 7679 2 D67CA060C8E92DE3F554DE7BA796DC1CEBF6B6AB90B7A2DABCF591CE616E9AF45B296B68E7EEEA7984F ...
...
20241113040322 2 6 100 8191 2 C5B5F76D4765087CDE6FF53147EEC9A1410EBEBE915F7759F0FC609E43BA83BACCC1F9A8D0CD73724E3 ...
... 
```
