# Moduli Generator — Improvement and Clarity Report

This report summarizes opportunities for significant improvement and clarity across documentation, developer experience,
testing, packaging, performance, and security. It reflects the current state of the repository and highlights quick wins
and medium‑term steps.

## Executive Summary

The project is generally well‑structured and feature‑complete for generating SSH moduli with MariaDB integration. The
largest gaps impacting users and contributors are documentation clarity, installer UX, and uneven test coverage.
Addressing these will materially improve adoption, reliability, and maintainability.

Top opportunities:

- Documentation and onboarding clarity (installer instructions, links, consistency)
- Test coverage and standardization (pytest, coverage targets)
- API and CLI documentation polish (examples, argument reference)
- Packaging and reproducible builds (wheel + constraints)
- CI and publishing flow (lint, test, build matrix)
- Performance and operability (observability, resumability docs)
- Security and configuration hygiene (least privilege, secrets handling)

## Findings and Recommendations

1. Documentation and Onboarding

- Fix typos, broken links, and filename inconsistencies in docs. ✓ quick win
- Provide a single authoritative installation path (PyPI, then fallback to dev installer script). ✓ quick win
- Ensure all doc links resolve (mkdocs nav, intra‑docs links, raw GitHub links for scripts). ✓ quick win
- Add a Getting Started page with: prerequisites, MariaDB setup, minimum OpenSSH version notes, and a 5‑minute
  quickstart.
- Add a Troubleshooting page (common installer pitfalls, MariaDB auth errors, OpenSSH version issues).
- Consolidate duplicated or overlapping content between docs/readme.md and docs/index.md.

2. CLI and API Documentation

- Generate API docs via mkdocstrings but add human examples for complex flows (generate_moduli, restart_screening).
- Add a CLI reference page with each option, defaults, and examples (current docs assume implicit knowledge).
- Add a clear statement about when you actually need DH moduli vs post‑quantum KEX options (already mentioned in
  about.md; surface this earlier in README to set expectations).

3. Installer UX and Scripts

- Provide a stable raw URL for the installer script (done in command_line_installer.md). ✓ quick win
- Add a checksum or pinned commit link for deterministic installs in regulated environments.
- Provide a non‑interactive mode for install_mg.sh that can read configuration from environment variables or a .env
  file (headless CI/automation).
- Add a minimal fallback path that installs from PyPI only, skipping the Git clone build when a released version exists.

4. Testing and Quality Gates

- Standardize on pytest; add pytest.ini markers and coverage thresholds (e.g., fail under 80%).
- Add unit tests for: file parsing, CLI arg validation, database write paths, restart_screening state recovery, and
  validators edge cases.
- Add integration tests gated by an environment variable to run against a local MariaDB (docker‑compose or service
  container in CI).
- Introduce static analysis (ruff) and type checking (mypy) as pre‑commit and CI steps.

5. CI/CD and Release Engineering

- Set up GitHub Actions (or preferred CI) for: lint, type‑check, tests (matrix 3.12/3.13, macOS + Linux), build wheel,
  and publish on tag.
- Cache Poetry and wheel builds to speed up CI.
- Add artifacts: coverage.xml, built wheels, and mkdocs site preview.

6. Packaging and Reproducibility

- Ensure pyproject.toml contains explicit Python version and dependency constraints compatible with 3.12+; lock only for
  development.
- Provide a constraints.txt for deterministic installs outside Poetry.
- Verify entry points expose CLI correctly and document them in README.

7. Performance and Operability

- Document performance characteristics and knobs (parallelism, nice_value, batch sizes, DB batch insert size).
- Add structured logging context (key length, job id, file name) and a verbose/quiet switch.
- Consider recording operational metrics (counts, durations) for long‑running jobs; at minimum, log summaries per phase.

8. Security and Configuration Hygiene

- Reaffirm parameterized SQL (already done), and add explicit path validations for file outputs.
- Mask or avoid printing secrets during installer prompts and logs (script prompts already keep password silent; ensure
  logs don’t leak).
- Provide example least‑privilege grants for the MariaDB user used at runtime.
- Ensure generated files have safe permissions (e.g., 0640/0600 as appropriate) and document this.

## Quick Wins Implemented Now

- Fixed command_line_installer.md to correct typos, file names, and provide a working raw GitHub URL for the installer
  script, plus a ready‑to‑copy curl command and clearer steps.
- Normalized language in that page (consistent capitalization and simplified step names).

## Additional Quick Wins Suggested (low effort, high impact)

- Add a “Copy” button snippets via mkdocs-material configuration for command blocks.
- Add a direct link to SAMPLE_privileged_mariadb.cnf near the schema install steps in README.
- Surface the “Do you actually need DH moduli?” caveat in the main README and Quick Start.
- Replace ambiguous placeholders with explicit commands (e.g., show both brew and apt install lines for MariaDB with
  versions).

## Medium‑Term Roadmap (2–4 weeks)

1. Docs and Onboarding

- Getting Started and Troubleshooting pages
- CLI reference and API examples
- Link checker in CI (e.g., lychee or mkdocs‑link‑check)

2. Quality and Testing

- pytest with 80%+ coverage target
- Integration tests against MariaDB in CI (service container)
- ruff + mypy in CI and pre‑commit

3. Release and CI

- GitHub Actions: lint, type, test (matrix), build, publish on tag
- Deterministic installer mode (pin to a tag/commit + checksum)

4. Operability

- Structured logging fields and a “--verbose/--quiet” switch
- Summary stats at end of run (per key length)

## Closing Note

The codebase is solid and close to production‑ready. Focusing on documentation clarity, installer UX, and test
standardization will deliver the most immediate improvements for both users and contributors without large code
refactors.