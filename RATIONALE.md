.. ssh-moduli-builder

# Rationale

## You're here - ok - here's the rationale.

SSHDs installation contains a file of random moduli (safe primes) across a set of modulus key lengths.
These moduli provide the basis for SSHDs session keys.

When using SSH, the pragmatic reality is that most system admins use whatever moduli file
arrives with their platform distribution. As keying material, it's certainly no longer random if it's distributed.
This is Challenge #1.

While OpenSSH provides `ssh-keygen` from which to build moduli files,
`ssh-keygen` requires separate execution for generation and then _safe prime_
screening of the generated candidates.
This is Challenge #2

A well constructed `ssh/moduli` file will contain a sufficient (approximately 80)
'safe-primes' for each of five* modulus key lengths: 3072, 4096, 6144, 7680, and 8192.
After Candidate Generation and Safe Prime Screening, each set of safe-primes have to be concatenated and placed in the
final ssh/moduli file.
This is Challenge #3

\*Bitlengths < 3071 are DROPPED - Reference `Hardening`





