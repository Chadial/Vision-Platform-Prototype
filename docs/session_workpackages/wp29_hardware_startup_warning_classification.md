# Hardware Startup Warning Classification

## Purpose

This work package defines the next execution-ready follow-up after the landed `WP27` and `WP28` post-closure hardening slices.

Closure lane:

- Post-Closure Python Baseline / Hardening

Slice role:

- residual-driven diagnostics hardening

Scope level:

- startup warning classification and evidence hygiene on the current real-device path

Its purpose is to narrow the remaining ambiguity around successful real-device runs that still emit startup-side warnings such as `vmbpyLog <VmbError.NotAvailable: -30>` or show duplicate SDK visibility for the same tested camera.

This package should be read as:

- warning classification and diagnostics hardening
- not a broad hardware exploration package
- not a full SDK anomaly cleanup package

## Branch

- intended branch: `fix/hardware-startup-warning-classification`
- activation state: landed on March 30, 2026

## Scope

Included:

- inspect the current startup and enumeration paths on the tested hardware camera flow
- identify which observed warning/noise patterns are:
  - actionable lifecycle issues
  - likely SDK / transport-layer noise
  - benign duplicate-visibility observations that should be documented rather than chased immediately
- improve logging or warning classification at the narrowest useful seam
- add the smallest validation path that proves successful runs can be distinguished from true startup failure
- update hardware docs with the clarified interpretation

Excluded:

- broad driver rewrite
- camera matrix testing
- hardware capability expansion
- transport/API redesign

What this package does not close:

- every hardware SDK anomaly
- all future startup-noise classes
- broad hardware reliability closure

## Session Goal

Leave the repository with one clearer interpretation of the remaining startup-side real-device warnings so successful hardware runs are easier to reason about and later sessions do not reopen the same ambiguity repeatedly.

## Current Context

The current integrated hardware baseline is already usable on `DEV_1AB22C046D81`.

The immediate remaining ambiguity is:

- some successful real-device runs still emit `VmbError.NotAvailable: -30>`
- the SDK can show duplicate visibility for the same tested camera id
- current evidence does not yet classify those observations sharply enough for later readers

## Narrow Decisions

- focus on classification and narrow diagnostics first
- prefer documenting benign residuals over speculative broad fixes
- only tighten code if one shared startup seam clearly improves interpretation

Implemented narrowing result:

- capability-probe failures now classify `NotAvailable`-style probe exceptions as non-blocking startup warnings when they do surface through the best-effort probe path
- fresh serial CLI-host-surface proofs on `DEV_1AB22C046D81` for `status` and `snapshot(.bmp)` both succeeded
- those successful runs still emitted `vmbpyLog <VmbError.NotAvailable: -30>` on stderr
- the successful envelopes still reported:
  - `capabilities_available = true`
  - `capability_probe_error = null`
  - `last_error = null`
- current repository interpretation after this slice:
  - the observed `NotAvailable: -30` line is presently classified as non-blocking SDK / logging residual on the successful tested path
  - it is not currently evidenced as an active capability-probe failure in the repository status surface

## Execution Plan

1. Re-read:
   - `docs/HARDWARE_EVALUATION.md`
   - `docs/HARDWARE_CAPABILITIES.md`
   - `integrations/camera/STATUS.md`
2. Inspect startup, enumeration, and warning paths in the current Vimba X integration.
3. Reproduce one minimal hardware startup path and classify the observed warning/noise output.
4. Implement the narrowest useful logging or classification improvement.
5. Record the updated interpretation in the hardware docs.

## Validation

Required validation:

- one real-device startup/status proof on `DEV_1AB22C046D81`
- one follow-up hardware command such as `snapshot` or `recording` after startup classification changes

Recommended supporting local validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_vimbax_camera_driver tests.test_camera_service tests.test_bootstrap
```

## Documentation Updates

- `docs/HARDWARE_EVALUATION.md`
- `docs/HARDWARE_CAPABILITIES.md`
- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- `integrations/camera/STATUS.md` if the driver-facing interpretation changes materially

## Expected Commit Shape

1. `fix: classify hardware startup warnings`
2. `test: cover startup warning interpretation`
3. `docs: record hardware startup warning classification`

## Merge Gate

- the slice remains narrowly centered on startup warning interpretation
- successful hardware runs are easier to distinguish from true startup failure
- no broad SDK or hardware exploration work is bundled
- updated evidence is recorded explicitly

## Completion Note

Landed evidence for this slice:

- automated validation:
  - `.\.venv\Scripts\python.exe -m unittest tests.test_camera_service tests.test_vimbax_camera_driver tests.test_bootstrap`
- serial real-device CLI proofs on `DEV_1AB22C046D81`:
  - `status`
  - `snapshot(.bmp)`
- observed result:
  - both commands succeeded
  - `vmbpyLog <VmbError.NotAvailable: -30>` still appeared on stderr
  - host/status envelopes still reported `capabilities_available = true`, `capability_probe_error = null`, and `last_error = null`

## Recovery Note

To activate this work package later:

1. confirm the camera is attached
2. read `docs/HARDWARE_EVALUATION.md`
3. read `docs/HARDWARE_CAPABILITIES.md`
4. inspect the current Vimba X startup path before editing
