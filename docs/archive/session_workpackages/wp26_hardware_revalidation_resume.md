# Hardware Revalidation Resume

## Purpose

This work package defines the next bounded hardware-dependent reliability slice once the camera is attached again locally.

Closure lane:

- Experiment Reliability Closure with a hardware-evidence follow-up role

Slice role:

- conditional hardware revalidation

Scope level:

- bounded real-device confidence pass over the current integrated Python camera baseline

Its purpose is to resume real-device validation against the already improved host-control, traceability, offline-support, and reliability baseline without reopening broad hardware exploration.

At the current repository maturity, this package should be read as:

- fresh evidence on the current integrated baseline
- not a search for broad new hardware functionality
- not a discovery-oriented camera study
- not a broad hardware productization step

This package should be read as:

- resume hardware evidence
- not reopen hardware discovery

## Branch

- intended branch: `test/hardware-revalidation-resume`
- activation state: conditional; activate only when the validated camera path is attached again

Activation condition:

- only when the previously validated real camera path is attached again and the session can execute a bounded real-device pass
- only when the session can validate the already integrated baseline meaningfully, not merely check that one frame can be acquired

## Scope

Included:

- rerun one bounded real-hardware confidence block over the current integrated baseline
- capture fresh evidence for the now-hardened integrated path, not just device detection
- cover the smallest useful real-device validation blocks for:
  - preview readiness and basic device-path viability
  - snapshot save through the current integrated command/save path
  - bounded recording on the real device path
  - interval capture where the current attached setup supports the shared-stream path as expected
  - host-readable status polling during active work where practical
  - traceability, artifact landing, and plausible metadata/run linkage where the current baseline exposes them
  - immediate reuse confidence after normal completed runs
- document results and any newly exposed gaps

Selected slice for this package:

- one fresh bounded hardware pass over the currently integrated command/preview/recording baseline using the already known camera path where available
- one post-hardening confirmation slice over the already improved host/traceability/reliability baseline rather than a new hardware-capability exploration package
- one evidence-oriented check that the current integrated host/traceability/reliability baseline behaves on the real path closely enough to the simulator-backed closure evidence to be trusted as a working basis

Recommended bounded evidence blocks:

- `A. Device-path baseline`
  - prove camera initialization, preview readiness, one snapshot save, and explicit save-directory behavior on the current real path
- `B. Active run behavior`
  - prove bounded recording, interval capture where relevant, and meaningful active polling during work
- `C. Traceability and data path`
  - prove artifacts, traceability files, and current metadata/run-linkage surfaces are coherent enough for the present baseline
- `D. Recovery and reuse confidence`
  - prove the subsystem returns to a reusable state after normal bounded real-device runs without requiring process restart

What this package is explicitly trying to answer:

- does the current Python camera subsystem still behave as the repository now claims it does on the real camera path?
- are there one or two concrete remaining real-device gaps that should be fixed before treating the current baseline as reliably usable?

Excluded:

- new hardware capability expansion
- broad camera matrix testing
- broad hardware discovery
- UI redesign
- broad performance benchmarking
- long-running soak or stress campaigns
- transport or API expansion
- large new implementation scope unless a narrow blocking defect is exposed directly by the bounded rerun

What this package does not close:

- broad hardware exploration
- camera matrix validation
- broad performance benchmarking
- UI redesign
- hardware capability discovery
- full runtime reliability closure across all failure classes
- full hardware reliability closure

## Session Goal

Leave the repository with one fresh bounded hardware evidence block that narrows the gap between the current simulator-first closure work and the actual target device path.

The goal is not just "camera alive", but bounded confidence that the current integrated Python subsystem still works acceptably on the real-device path across:

- basic preview/snapshot viability
- active run behavior
- traceability and artifact confidence
- normal reuse after completed runs

The package is intentionally evidence-oriented, bounded, and conditional on hardware availability.

Evidence interpretation for this package:

- `confirmed / acceptable`
  - preview, snapshot, bounded recording, and the selected data/logging surfaces work on the real path without leaving ambiguous runtime state
- `acceptable with residual issues`
  - the core pass succeeds, but one or two concrete bounded quirks remain that do not break baseline use and can be documented clearly
- `not yet acceptable`
  - a core real-device baseline flow fails reproducibly, leaves ambiguous active state, or breaks the current traceability/host-visibility expectations materially

## Validation

- hardware-backed manual execution using the current camera path
- update `docs/HARDWARE_EVALUATION.md` or the relevant session note with exact results

## Latest Result Note

Latest bounded rerun completed on March 30, 2026 against camera `DEV_1AB22C046D81`.

Observed result:

- preview readiness, snapshot, bounded recording, interval capture, active polling visibility, traceability output, offline BMP reuse, and same-subsystem reuse all passed on the current integrated baseline
- the rerun should be read as `acceptable with residual issues`, not as full closure of all hardware reliability questions

Residual observations kept open:

- successful runs still emitted a `vmbpyLog <VmbError.NotAvailable: -30>` line
- SDK enumeration exposed duplicate entries for the tested camera id
- one interval-capture rerun reported `skipped_intervals=1`
