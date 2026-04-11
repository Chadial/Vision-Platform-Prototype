# Experiment Recovery Validation Extension

## Purpose

This work package defines the next simulator-first reliability validation slice after the host-control tightening sequence.

Closure lane:

- Experiment Reliability Closure

Slice role:

- validation / recovery extension

Orientation:

- simulator-first validation of bounded recovery behavior, with only minimal adjacent fixes if tests expose concrete defects

Its purpose is to prove one tighter recovery block over host-driven recording failures and repeated restart behavior without depending on hardware availability.

The narrow goal is to validate one bounded recovery matrix more tightly, not to redesign the broader runtime, transport, or hardware-validation story.

## Branch

- intended branch: `test/experiment-recovery-validation-extension`
- activation state: landed narrow follow-up after `WP24`; use `WP26` only when the real camera path is attached again

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
- keep the slice simulator-first by design so it can prove behavior tightly before any later hardware-backed confirmation work
- landed implementation note:
  - the integrated bootstrap / command-controller path now proves writer-side recording failure, repeated post-failure stop calls, and successful restart on the same subsystem instance
  - no production runtime redesign was required for this slice; the package landed as validation-first evidence

Excluded:

- broad runtime redesign
- hardware-backed validation
- new transport work

What this package does not close:

- the whole reliability lane
- broad runtime redesign
- hardware validation
- broader transport or host-surface work

## Session Goal

Leave the repository with one tighter locally verifiable proof that the experiment-facing recording path can fail, recover, and be started again without process restart.

This package should be read as:

- a tighter bounded recovery matrix
- simulator-first by design
- later hardware-backed confirmation still remains separate

## Validation

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_recording_service tests.test_command_controller tests.test_bootstrap
```

## Merge Gate

- the slice remains validation-first and simulator-first
- only minimal adjacent fixes are allowed when tests expose concrete defects
- no broad runtime redesign, hardware-validation expansion, or transport work is bundled
- the package is not treated as closure of the whole reliability lane
- targeted tests pass locally
