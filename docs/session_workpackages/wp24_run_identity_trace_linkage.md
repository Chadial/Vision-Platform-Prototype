# Run Identity And Trace Linkage

## Purpose

This work package defines the next cross-lane linkage slice after the current host-control tightening work.

Its purpose is to align one deterministic run identity across host-facing command or status outputs and the existing artifact traceability structures.

## Branch

- intended branch: `feature/run-identity-trace-linkage`
- activation state: prepared queued follow-up after `WP23`

## Scope

Included:

- inspect existing run identifiers across bounded recording, traceability blocks, and host-visible outputs
- freeze one deterministic run identity rule for the current bounded experiment baseline
- expose that same identity in the narrowest shared surfaces that already need it
- add focused tests for linkage consistency

Selected slice for this package:

- one deterministic run identity reused across:
  - traceability run blocks
  - recording-side metadata output where applicable
  - host-visible command or status output where appropriate

Excluded:

- broad session explorer behavior
- historical run indexing
- offline browser expansion
- transport redesign

## Session Goal

Leave the repository with one explicit proof that a host-visible experiment run can be linked deterministically to the saved traceability artifacts it produced.

## Validation

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_recording_service tests.test_command_controller tests.test_postprocess_tool
```
