# Run Identity And Trace Linkage

## Purpose

This work package defines the next cross-lane linkage slice after the current host-control tightening work.

Closure lane:

- cross-lane linkage between Host Control Closure and Data / Logging traceability

Slice role:

- linkage / identity alignment

Scope level:

- deterministic run/session identity only

Its purpose is to align one deterministic run identity across host-facing command or status outputs and the existing artifact traceability structures.

The narrow goal is to align one already-needed run identity across existing narrow surfaces, not to introduce a broader run model, browsing layer, or historical indexing framework.

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
- keep the package centered on identity alignment across already-existing narrow surfaces rather than inventing a broader run/session model

Excluded:

- broad session explorer behavior
- historical run indexing
- offline browser expansion
- transport redesign

What this package does not close:

- session browsing
- offline explorer work
- historical indexing
- broad identity framework work

## Session Goal

Leave the repository with one explicit proof that a host-visible experiment run can be linked deterministically to the saved traceability artifacts it produced.

This package should be read as:

- one deterministic run identity aligned across existing surfaces
- not a broader run/session exploration package

## Validation

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_recording_service tests.test_command_controller tests.test_postprocess_tool
```

## Merge Gate

- the slice remains linkage-side and identity-alignment-focused
- no session browser, offline explorer, or historical indexing behavior is bundled
- no broad identity-framework redesign is bundled
- targeted tests pass locally
