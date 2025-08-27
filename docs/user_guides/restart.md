# Response

## Restart Interrupted Screening

### Run Command

```bash
moduli_generator restart&
```

### Tail the run log

```bash
tail -f ${MODULI_HOME}/.logs/moduli_generator.log
```

```log
2025-08-06 20:48:06,519 - INFO: Starting Moduli Restart at 2025-08-06 20:48:06.519624, with (3072, 4096, 6144, 7680,
8192) as moduli key-lengths
2025-08-06 20:48:06,519 - INFO: Using Base directory: /Users/ron/.moduli_generator/.moduli
2025-08-06 20:48:06,519 - INFO: Using Candidates directory: /Users/ron/.moduli_generator/.candidates
2025-08-06 20:48:06,519 - INFO: Using Moduli directory: /Users/ron/.moduli_generator/.moduli
2025-08-06 20:48:06,519 - INFO: Using Log directory: /Users/ron/.moduli_generator/.logs
2025-08-06 20:48:06,519 - INFO: Using MariaDB config: /Users/ron/.moduli_generator/moduli_generator.cnf
2025-08-06 20:48:07,618 - DEBUG: Loaded checkpoint from '
/Users/ron/.moduli_generator/.candidates/.candidates_8192_20250728200331371527' line 770450
2025-08-06 20:53:08,153 - DEBUG: Wed Aug 6 15:53:08 2025 processed 3476 of 137365 (2%) in 0:05, ETA 3:12
2025-08-06 20:58:18,543 - DEBUG: Wed Aug 6 15:58:18 2025 processed 6713 of 137365 (4%) in 0:10, ETA 3:17
2025-08-06 21:03:28,411 - DEBUG: Wed Aug 6 16:03:28 2025 processed 10380 of 137365 (7%) in 0:15, ETA 3:07
2025-08-06 21:08:35,577 - DEBUG: Wed Aug 6 16:08:35 2025 processed 13628 of 137365 (9%) in 0:20, ETA 3:05
2025-08-06 21:13:35,153 - DEBUG: Wed Aug 6 16:13:35 2025 processed 16800 of 137365 (12%) in 0:25, ETA 3:02
2025-08-06 21:18:37,910 - DEBUG: Wed Aug 6 16:18:37 2025 processed 20280 of 137365 (14%) in 0:30, ETA 2:55
2025-08-06 21:23:37,140 - DEBUG: Wed Aug 6 16:23:37 2025 processed 24835 of 137365 (18%) in 0:35, ETA 2:40
2025-08-06 21:28:37,105 - DEBUG: Wed Aug 6 16:28:37 2025 processed 28618 of 137365 (20%) in 0:40, ETA 2:33
2025-08-06 21:33:37,126 - DEBUG: Wed Aug 6 16:33:37 2025 processed 32730 of 137365 (23%) in 0:45, ETA 2:25
2025-08-06 21:38:43,353 - DEBUG: Wed Aug 6 16:38:43 2025 processed 35741 of 137365 (26%) in 0:50, ETA 2:23
2025-08-06 21:43:49,630 - DEBUG: Wed Aug 6 16:43:49 2025 processed 38663 of 137365 (28%) in 0:55, ETA 2:22
2025-08-06 21:48:49,093 - DEBUG: Wed Aug 6 16:48:49 2025 processed 42970 of 137365 (31%) in 1:00, ETA 2:13
2025-08-06 21:53:49,108 - DEBUG: Wed Aug 6 16:53:49 2025 processed 46906 of 137365 (34%) in 1:05, ETA 2:06
2025-08-06 21:58:55,890 - DEBUG: Wed Aug 6 16:58:55 2025 processed 50195 of 137365 (36%) in 1:10, ETA 2:02
2025-08-06 22:03:55,571 - DEBUG: Wed Aug 6 17:03:55 2025 processed 53714 of 137365 (39%) in 1:15, ETA 1:58
2025-08-06 22:09:05,540 - DEBUG: Wed Aug 6 17:09:05 2025 processed 57421 of 137365 (41%) in 1:20, ETA 1:52
2025-08-06 22:14:05,200 - DEBUG: Wed Aug 6 17:14:05 2025 processed 60870 of 137365 (44%) in 1:25, ETA 1:48
2025-08-06 22:19:05,151 - DEBUG: Wed Aug 6 17:19:05 2025 processed 64979 of 137365 (47%) in 1:30, ETA 1:41
2025-08-06 22:24:05,192 - DEBUG: Wed Aug 6 17:24:05 2025 processed 67974 of 137365 (49%) in 1:35, ETA 1:37
2025-08-06 22:29:05,166 - DEBUG: Wed Aug 6 17:29:05 2025 processed 71611 of 137365 (52%) in 1:40, ETA 1:32
2025-08-06 22:34:05,204 - DEBUG: Wed Aug 6 17:34:05 2025 processed 76036 of 137365 (55%) in 1:45, ETA 1:25
2025-08-06 22:39:13,794 - DEBUG: Wed Aug 6 17:39:13 2025 processed 80290 of 137365 (58%) in 1:51, ETA 1:18
2025-08-06 22:44:23,044 - DEBUG: Wed Aug 6 17:44:23 2025 processed 85335 of 137365 (62%) in 1:56, ETA 1:10
2025-08-06 22:49:32,025 - DEBUG: Wed Aug 6 17:49:32 2025 processed 89788 of 137365 (65%) in 2:01, ETA 1:04
2025-08-06 22:54:31,286 - DEBUG: Wed Aug 6 17:54:31 2025 processed 93291 of 137365 (67%) in 2:06, ETA 0:59
2025-08-06 22:59:39,012 - DEBUG: Wed Aug 6 17:59:39 2025 processed 97017 of 137365 (70%) in 2:11, ETA 0:54
2025-08-06 23:04:38,211 - DEBUG: Wed Aug 6 18:04:38 2025 processed 99996 of 137365 (72%) in 2:16, ETA 0:51
2025-08-06 23:09:38,712 - DEBUG: Wed Aug 6 18:09:38 2025 processed 103858 of 137365 (75%) in 2:21, ETA 0:45
2025-08-06 23:14:38,207 - DEBUG: Wed Aug 6 18:14:38 2025 processed 108029 of 137365 (78%) in 2:26, ETA 0:39
2025-08-06 23:19:38,238 - DEBUG: Wed Aug 6 18:19:38 2025 processed 111815 of 137365 (81%) in 2:31, ETA 0:34
2025-08-06 23:24:39,193 - DEBUG: Wed Aug 6 18:24:39 2025 processed 116780 of 137365 (85%) in 2:36, ETA 0:27
2025-08-06 23:29:48,734 - DEBUG: Wed Aug 6 18:29:48 2025 processed 121283 of 137365 (88%) in 2:41, ETA 0:21
2025-08-06 23:34:51,527 - DEBUG: Wed Aug 6 18:34:51 2025 processed 125963 of 137365 (91%) in 2:46, ETA 0:15
2025-08-06 23:39:51,272 - DEBUG: Wed Aug 6 18:39:51 2025 processed 129238 of 137365 (94%) in 2:51, ETA 0:10
2025-08-06 23:44:51,233 - DEBUG: Wed Aug 6 18:44:51 2025 processed 133788 of 137365 (97%) in 2:56, ETA 0:04
2025-08-06 23:49:22,747 - DEBUG: Wed Aug 6 18:49:22 2025 Found 2 safe primes of 68634 candidates in 10875 seconds
2025-08-06 23:49:22,849 - INFO: Produced 1 files of screened moduli
for key-lengths:(3072, 4096, 6144, 7680, 8192)
2025-08-06 23:49:22,864 - DEBUG: Using MariaDB config: /Users/ron/.moduli_generator/moduli_generator.cnf
2025-08-06 23:49:23,339 - INFO: Connection pool created with size: 10
2025-08-06 23:49:23,340 - DEBUG: Query returned 1 rows
2025-08-06 23:49:23,341 - DEBUG: Transaction committed
2025-08-06 23:49:23,346 - DEBUG: Query returned 3 rows
2025-08-06 23:49:23,346 - DEBUG: Transaction committed
2025-08-06 23:49:23,348 - DEBUG: Query returned 1 rows
2025-08-06 23:49:23,349 - DEBUG: Transaction committed
2025-08-06 23:49:23,350 - DEBUG: Query returned 4 rows
2025-08-06 23:49:23,350 - DEBUG: Transaction committed
2025-08-06 23:49:23,352 - DEBUG: Query returned 2 rows
2025-08-06 23:49:23,352 - DEBUG: Transaction committed
2025-08-06 23:49:23,353 - DEBUG: Query returned 1 rows
2025-08-06 23:49:23,353 - DEBUG: Transaction committed
2025-08-06 23:49:23,354 - INFO: Schema verification completed with status: PASSED
2025-08-06 23:49:23,359 - DEBUG: Transaction committed
2025-08-06 23:49:23,360 - INFO: Moduli Stored in MariaDB database: 1
2025-08-06 23:49:23,361 - INFO: Moduli Generation Complete. Time taken: 10876 seconds

```
