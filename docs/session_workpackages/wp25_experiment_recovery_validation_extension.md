# Experiment Recovery Validation Extension

## Purpose

This work package defines the next simulator-first reliability validation slice after the host-control tightening sequence.

Its purpose is to prove one tighter recovery block over host-driven recording failures and repeated restart behavior without depending on hardware availability.

## Branch

- intended branch: `test/experiment-recovery-validation-extension`
- activation state: prepared queued follow-up after `WP24`

## Scope

Included:

- extend simulator-first validation around repeated start/stop, writer failure, and recovery-to-next-run behavior
- cover the host-facing command/controller path where practical
- keep changes focused on validation and minimal adjacent fixes only when tests expose a concrete defect

Selected slice for this package:

- one bounded recovery matrix covering:
  - recording failure during write
  - subsequent successful restart
  - host-visible status recovery after failure
  - repeated stop/restart idempotence around the affected flow

Excluded:

- broad runtime redesign
- hardware-backed validation
- new transport work

## Session Goal

Leave the repository with one tighter locally verifiable proof that the experiment-facing recording path can fail, recover, and be started again without process restart.

## Validation

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_recording_service tests.test_command_controller tests.test_bootstrap
```
