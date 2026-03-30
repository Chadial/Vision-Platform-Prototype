# Python Baseline Operations Runbook

## Purpose

This work package defines the first operational-readiness slice after the immediate residual hardening pair.

Closure lane:

- Post-Closure Python Baseline / Operational Readiness

Slice role:

- runbook and operating-rules clarification

Scope level:

- documented stable operating baseline for the current Python camera subsystem

Its purpose is to make the current post-closure Python baseline easier to run, trust, and hand over by documenting one clear operating runbook for the validated environment and the known-good command paths.

This package should be read as:

- operational-readiness documentation
- not packaging automation
- not broad feature expansion

## Branch

- intended branch: `docs/python-baseline-operations-runbook`
- activation state: landed

## Scope

Included:

- document the currently preferred interpreter, launch paths, and known-good entry points
- document the tested hardware path, current assumptions, and when to prefer simulator-first execution
- document the bounded real-hardware evidence set and the remaining residuals
- document the practical run order for:
  - status
  - snapshot
  - recording
  - interval capture
  - hardware-specific checks when relevant
- document when a session should treat the baseline as stable versus when a residual needs follow-up

Excluded:

- installer creation
- environment automation
- transport or UI redesign

What this package does not close:

- packaging/distribution
- broad deployment automation
- full support across many hardware environments

## Session Goal

Leave the repository with one compact operations runbook so a future user or agent can run the current Python baseline with less rediscovery and less accidental drift into unsupported paths.

Implemented result:

- central runbook added at `docs/PYTHON_BASELINE_RUNBOOK.md`
- central status surfaces now link that runbook and no longer treat this package as pending

## Execution Plan

1. Re-read:
   - `docs/STATUS.md`
   - `docs/HARDWARE_EVALUATION.md`
   - `docs/HARDWARE_CAPABILITIES.md`
   - `apps/camera_cli/STATUS.md`
2. Collect the current stable launch and validation paths.
3. Write one compact runbook document or runbook section in the central docs.
4. Link that runbook from the most relevant central PM/status surfaces.

## Validation

- documentation consistency review against:
  - `docs/STATUS.md`
  - `docs/HARDWARE_EVALUATION.md`
  - `docs/WORKPACKAGES.md`

## Documentation Updates

- one new or updated runbook-oriented central doc
- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- module status docs only if links or operating assumptions need to be surfaced there

## Expected Commit Shape

1. `docs: add python baseline operations runbook`
2. `docs: link runbook from central status surfaces`

## Merge Gate

- the slice stays documentation-only and operational
- the runbook clearly distinguishes stable baseline, known residuals, and deferred areas
- no packaging automation or feature work is bundled

## Recovery Note

To activate this work package later:

1. read `docs/STATUS.md`
2. read `docs/HARDWARE_EVALUATION.md`
3. inspect current CLI and hardware validation docs before writing the runbook
