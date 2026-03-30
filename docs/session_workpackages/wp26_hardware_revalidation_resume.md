# Hardware Revalidation Resume

## Purpose

This work package defines the next bounded hardware-dependent reliability slice once the camera is attached again locally.

Its purpose is to resume real-device validation against the now-hardened host-control, traceability, and offline-support baseline without reopening broad hardware exploration.

## Branch

- intended branch: `test/hardware-revalidation-resume`
- activation state: conditional; activate only when the validated camera path is attached again

## Scope

Included:

- rerun one bounded real-hardware block over the current integrated baseline
- capture fresh evidence for:
  - snapshot save
  - preview readiness
  - interval capture
  - bounded recording
  - host-readable status polling during active work where practical
- document results and any newly exposed gaps

Selected slice for this package:

- one fresh hardware pass over the currently integrated command/preview/recording baseline using the already known camera path where available

Excluded:

- new hardware capability expansion
- broad camera matrix testing
- UI redesign
- broad performance benchmarking

## Session Goal

Leave the repository with one fresh bounded hardware evidence block that narrows the gap between the current simulator-first closure work and the actual target device path.

## Validation

- hardware-backed manual execution using the current camera path
- update `docs/HARDWARE_EVALUATION.md` or the relevant session note with exact results
