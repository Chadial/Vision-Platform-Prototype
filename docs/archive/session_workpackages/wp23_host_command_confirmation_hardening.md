# Host Command Confirmation Hardening

## Purpose

This work package defines the next host-control follow-up after `WP22`.

Closure lane:

- Host Control Closure

Slice role:

- command confirmation hardening

Orientation:

- producer-side command-result shaping for host use

Its purpose is to make one more narrow command-result confirmation slice explicit so hosts do not have to assume that requested capture or recording settings were accepted unchanged.

The narrow goal is to harden explicit post-command confirmation, not to widen runtime polling or redesign the broader command contract.

## Branch

- intended branch: `feature/host-command-confirmation-hardening`
- activation state: landed narrow follow-up after `WP22`; use `WP24` as the next default follow-up

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
- keep this slice explicitly on the command-result side after host calls rather than on the polling side during active work
- landed implementation note:
  - the current CLI host surface now exposes that narrow confirmed subset for `snapshot` and bounded `recording`
  - the status polling payload remains unchanged by this slice so `WP22` and `WP23` stay distinct

Excluded:

- broad command-contract redesign
- runtime polling changes
- new transport DTO families
- API or CLI feature widening beyond the shared command result surface

What this package does not close:

- active runtime polling during ongoing work
- transport/API DTO redesign
- full command-contract closure
- broader host-facing contract redesign outside the narrow confirmed subset

## Session Goal

Leave the repository with one explicit proof that hosts can read back a narrow confirmed command subset instead of assuming that request and applied settings are identical.

This package should be read as:

- `WP22` = active polling subset during current work
- `WP23` = confirmed post-command subset after host-triggered operations

## Validation

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_camera_cli tests.test_command_controller tests.test_request_models tests.test_bootstrap
```

## Merge Gate

- the slice remains additive and command-result-oriented
- the slice remains on producer-side result shaping rather than active polling
- no transport/API DTO redesign or broad command-contract rewrite is bundled
- targeted tests pass locally
