# `Moduli Generator` Test run

### < `(1 hr elapsed)`

## Comand

```bash
moduli_generator --key-lengths 3072 4096&
```

## Tailing the Run Log

```bash
tail -f ${HOME}/.moduli_generator/moduli_generator.log
```

```bash
2025-08-20 20:57:49,296 - DEBUG: Transaction committed
2025-08-20 21:00:01,420 - DEBUG: Using default config: <config.ModuliConfig object at 0x106b18910>
2025-08-20 21:00:01,420 - INFO: Starting Moduli Generation at 2025-08-20 21:00:01, with (3072, 4096) as moduli key-lengths
2025-08-20 21:00:01,420 - INFO: Using Base directory: /Users/ron/.moduli_generator/.moduli
2025-08-20 21:00:01,420 - INFO: Using Candidates directory: /Users/ron/.moduli_generator/.candidates
2025-08-20 21:00:01,420 - INFO: Using Moduli directory: /Users/ron/.moduli_generator/.moduli
2025-08-20 21:00:01,420 - INFO: Using Log directory: /Users/ron/.moduli_generator/.logs
2025-08-20 21:00:01,420 - INFO: Using MariaDB config: /Users/ron/.moduli_generator/moduli_generator.cnf
2025-08-20 21:00:01,661 - DEBUG: Wed Aug 20 16:00:01 2025 Sieve next 268304384 plus 4095-bit
2025-08-20 21:00:01,661 - DEBUG: Wed Aug 20 16:00:01 2025 Sieve next 150896640 plus 3071-bit
2025-08-20 21:03:07,797 - DEBUG: Wed Aug 20 16:03:07 2025 Sieved with 203277289 small primes in 186 seconds
2025-08-20 21:03:13,760 - DEBUG: Wed Aug 20 16:03:13 2025 Found 128213 candidates
2025-08-20 21:03:13,763 - DEBUG: Generated candidate file 1/2: /Users/ron/.moduli_generator/.candidates/candidates_3072_20250820210001644427
2025-08-20 21:04:06,662 - DEBUG: Wed Aug 20 16:04:06 2025 Sieved with 203277289 small primes in 245 seconds
2025-08-20 21:04:20,496 - DEBUG: Wed Aug 20 16:04:20 2025 Found 226872 candidates
2025-08-20 21:04:20,501 - DEBUG: Generated candidate file 2/2: /Users/ron/.moduli_generator/.candidates/candidates_4096_20250820210001645900
2025-08-20 21:04:20,501 - INFO: Generated 2 candidate files for key-lengths: (3072, 4096)
2025-08-20 21:08:13,209 - DEBUG: Wed Aug 20 16:08:13 2025 processed 56130 of 128213 (43%) in 0:05, ETA 0:06
2025-08-20 21:09:20,204 - DEBUG: Wed Aug 20 16:09:20 2025 processed 25466 of 226872 (11%) in 0:05, ETA 0:39
2025-08-20 21:13:13,208 - DEBUG: Wed Aug 20 16:13:13 2025 processed 110410 of 128213 (86%) in 0:10, ETA 0:01
2025-08-20 21:14:20,211 - DEBUG: Wed Aug 20 16:14:20 2025 processed 50100 of 226872 (22%) in 0:10, ETA 0:35
2025-08-20 21:14:57,225 - DEBUG: Wed Aug 20 16:14:57 2025 Found 16 safe primes of 64286 candidates in 704 seconds
2025-08-20 21:14:57,242 - DEBUG: Screened moduli file 1/2: /Users/ron/.moduli_generator/.moduli/moduli_3072_20250820210001644427
2025-08-20 21:19:20,208 - DEBUG: Wed Aug 20 16:19:20 2025 processed 74615 of 226872 (32%) in 0:15, ETA 0:30
2025-08-20 21:24:20,217 - DEBUG: Wed Aug 20 16:24:20 2025 processed 99495 of 226872 (43%) in 0:20, ETA 0:25
2025-08-20 21:29:20,224 - DEBUG: Wed Aug 20 16:29:20 2025 processed 125151 of 226872 (55%) in 0:25, ETA 0:20
2025-08-20 21:34:20,205 - DEBUG: Wed Aug 20 16:34:20 2025 processed 149670 of 226872 (65%) in 0:30, ETA 0:15
2025-08-20 21:39:20,217 - DEBUG: Wed Aug 20 16:39:20 2025 processed 174098 of 226872 (76%) in 0:35, ETA 0:10
2025-08-20 21:44:20,215 - DEBUG: Wed Aug 20 16:44:20 2025 processed 198245 of 226872 (87%) in 0:40, ETA 0:05
2025-08-20 21:49:20,217 - DEBUG: Wed Aug 20 16:49:20 2025 processed 224556 of 226872 (98%) in 0:45, ETA 0:00
2025-08-20 21:49:45,808 - DEBUG: Wed Aug 20 16:49:45 2025 Found 20 safe primes of 113629 candidates in 2725 seconds
2025-08-20 21:49:45,825 - DEBUG: Screened moduli file 2/2: /Users/ron/.moduli_generator/.moduli/moduli_4096_20250820210001645900
2025-08-20 21:49:45,825 - INFO: Screened 2 candidate files for key-lengths: (3072, 4096)
2025-08-20 21:49:45,883 - DEBUG: Using MariaDB config: /Users/ron/.moduli_generator/moduli_generator.cnf
[1]  + 1127 exit 2     moduli_generator --key-lengths 3072 4096

```