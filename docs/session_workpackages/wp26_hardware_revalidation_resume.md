# Hardware Revalidation Resume

## Purpose

This work package defines the next bounded hardware-dependent reliability slice once the camera is attached again locally.

Closure lane:

- Experiment Reliability Closure with a hardware-evidence follow-up role

Slice role:

- conditional hardware revalidation

Its purpose is to resume real-device validation against the already improved host-control, traceability, offline-support, and reliability baseline without reopening broad hardware exploration.

This package should be read as:

- resume hardware evidence
- not reopen hardware discovery

## Branch

- intended branch: `test/hardware-revalidation-resume`
- activation state: conditional; activate only when the validated camera path is attached again

Activation condition:

- only when the previously validated real camera path is attached again and the session can execute a bounded real-device pass

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

- one fresh bounded hardware pass over the currently integrated command/preview/recording baseline using the already known camera path where available
- one post-hardening confirmation slice over the already improved host/traceability/reliability baseline rather than a new hardware-capability exploration package

Excluded:

- new hardware capability expansion
- broad camera matrix testing
- UI redesign
- broad performance benchmarking

What this package does not close:

- broad hardware exploration
- camera matrix validation
- broad performance benchmarking
- UI redesign
- full hardware reliability closure

## Session Goal

Leave the repository with one fresh bounded hardware evidence block that narrows the gap between the current simulator-first closure work and the actual target device path.

The package is intentionally evidence-oriented, bounded, and conditional on hardware availability.

## Validation

- hardware-backed manual execution using the current camera path
- update `docs/HARDWARE_EVALUATION.md` or the relevant session note with exact results
