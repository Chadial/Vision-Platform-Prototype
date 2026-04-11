# WP67 Recording Log Policy Alignment

## Purpose

Tighten the remaining recording-log policy so reused save directories and repeated sessions produce predictable append/continuation behavior without forcing operators to manually reconcile multiple near-duplicate log files.

## Closure lane

- Usable Camera Subsystem / Pre-Product Baseline

## Slice role

- bounded recording-log policy and artifact-log usability hardening

## Scope level

- one narrow follow-up after timestamp-anchor alignment

## Branch

- intended branch: `feature/recording-log-policy-alignment`
- activation state: landed

## Scope

Included:

- define the intended policy for `series_recording_log*.csv` reuse versus per-run splitting
- align recording-log behavior with the existing append/resume artifact naming semantics where justified
- keep snapshot/recording traceability and per-run recording logs clearly distinct in purpose
- document the chosen operator-facing behavior briefly in central status/workpackage docs

Excluded:

- new database storage
- audit redesign
- broad offline analysis tooling
- transport or API work

## Validation

- repeated recording into the same save directory follows one explicit and documented log policy
- the resulting policy is covered by local unit tests
- traceability and recording-log responsibilities stay easy to distinguish
- local validation passed with `.\.venv\Scripts\python.exe -m unittest tests.test_file_naming tests.test_recording_service tests.test_snapshot_service`
