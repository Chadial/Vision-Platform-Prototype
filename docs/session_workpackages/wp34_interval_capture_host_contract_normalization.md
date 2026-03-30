# Interval Capture Host Contract Normalization

## Purpose

This work package defines the next narrow host-surface follow-up after the landed host-contract clarification slice.

Closure lane:

- Post-Closure Python Baseline / Hardening

Slice role:

- bounded host-contract normalization

Scope level:

- current `interval-capture` result and status surface only

Its purpose is to remove the most visible remaining host-surface asymmetry by bringing `interval-capture` closer to the same bounded host-envelope expectations already used for `status`, `snapshot`, and bounded `recording`.

This package should be read as:

- one narrow host-surface normalization slice
- not broader transport expansion
- not CLI feature growth

## Branch

- intended branch: `fix/interval-capture-host-contract-normalization`
- activation state: current next

## Scope

Included:

- inspect the current `interval-capture` CLI result shape and status ownership
- normalize one bounded result subset so host-facing behavior is less special-case-driven
- keep the change aligned with the existing bounded command-envelope model
- add focused tests for the normalized shape

Excluded:

- detached interval-capture lifecycle control
- new interval-capture commands
- broader transport/API DTO work

What this package does not close:

- full host-contract closure for all future capture modes
- broader long-running remote control semantics

## Session Goal

Leave the repository with one less special-case host command by making the current bounded `interval-capture` path clearer and closer to the rest of the host-oriented baseline.

## Validation

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_camera_cli tests.test_command_controller tests.test_api_service
```

