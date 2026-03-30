# Host Command Confirmation Hardening

## Purpose

This work package defines the next host-control follow-up after `WP22`.

Its purpose is to make one more narrow command-result confirmation slice explicit so hosts do not have to assume that requested capture or recording settings were accepted unchanged.

## Branch

- intended branch: `feature/host-command-confirmation-hardening`
- activation state: prepared follow-up after `WP22`

## Scope

Included:

- inspect snapshot, recording, and save-directory command results
- choose one conservative confirmed-settings subset to return explicitly
- keep the change additive and command-result-oriented
- add focused tests for accepted and rejected command paths

Selected slice for this package:

- explicit confirmation of a small resolved subset such as:
  - resolved save directory
  - resolved file stem / extension where applicable
  - accepted frame limit / duration / target frame rate where applicable

Excluded:

- broad command-contract redesign
- new transport DTO families
- API or CLI feature widening beyond the shared command result surface

## Session Goal

Leave the repository with one explicit proof that hosts can read back a narrow confirmed command subset instead of assuming that request and applied settings are identical.

## Validation

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_command_controller tests.test_request_models tests.test_bootstrap
```
