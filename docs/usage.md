# Default Run Properties

The sole objective of `moduli_generator` is to produce *unique and secure* SSH2 Moduli Files.

The default configuration will produce a complete `/etc/ssh/moduli` file, comprised of 20 moduli for each of 5
key-sizes, `3072`, `4096`, `6144`, `7680`, and `8192` in about 90 hours.

## /etc/ssh/moduli

```bash
# aragorn.local::ModuliGenerator: ssh2 moduli generated at 2025-07-28T02:25:52.957733Z
# timestamp,type,tests,trials,size,generator,moduli
20241110030855 2 6 100 3071 2 C8053358B1E47DCB826BA2BCB616739EE826ADB273504CF89F8CF6F5A9946B5576F66A07012DCC10557... 
20241110033748 2 6 100 3071 2 C8053358B1E47DCB826BA2BCB616739EE826ADB273504CF89F8CF6F5A9946B5576F66A0773504CF89FA ... 
```

## Default Configuration

The default configuration is designed to provide a complete ssh/moduli file,
consisting of 20 entries for each key-length 3072, 4096, 6144, 7680, and 8192.
A full run will take around 90 Hours on an quad-core i7.

```bash
moduli_generator&
```

# usage

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
