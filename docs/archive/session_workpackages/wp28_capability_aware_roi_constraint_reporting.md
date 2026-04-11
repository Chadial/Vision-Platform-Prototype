# Capability-Aware ROI Constraint Reporting

## Purpose

This work package defines the next execution-ready follow-up after `WP27`.

Closure lane:

- Host Control Closure with a narrow overlap into capability-backed configuration validation

Slice role:

- validation/reporting hardening

Scope level:

- clearer host-usable ROI width/height/offset constraint reporting on capability-backed camera paths

Its purpose is to keep the current strict ROI capability enforcement, but make invalid ROI requests easier to diagnose from host, CLI, and validation contexts by returning clearer increment/range guidance.

This package should be read as:

- reporting/validation precision
- not a change to the strict validation policy
- not ROI feature expansion

## Branch

- intended branch: `fix/capability-aware-roi-constraint-reporting`
- activation state: landed on March 30, 2026 as the narrow follow-up behind `WP27`

## Scope

Included:

- inspect current ROI validation messages for width, height, `offset_x`, and `offset_y`
- make capability-backed failure reporting clearer for the current host-facing and CLI-facing paths
- include the most useful narrow guidance such as:
  - expected range
  - required increment
  - base value when relevant
  - one or two nearest valid values where practical
- add focused tests for invalid width/height/offset reporting

Excluded:

- automatic silent normalization of invalid ROI requests
- broader ROI editing features
- new UI controls
- general camera capability redesign

What this package does not close:

- the question of whether future workflows should offer optional auto-normalization
- broader capability-aware validation reporting beyond the ROI family
- broader host contract redesign

## Session Goal

Leave the repository with one stricter-but-clearer ROI validation surface so a caller can understand immediately why a request such as `roi_width=2001` failed on the current device path.

## Current Context

The March 30, 2026 hardware reruns confirmed:

- ROI constraints are correctly enforced
- invalid ROI width fails explicitly
- the current practical pain is not missing enforcement, but missing convenience and clarity in the returned guidance

The immediate small gap is:

- host-/CLI-facing ROI failures should explain device constraints more directly

Implemented narrowing result:

- strict ROI validation remains unchanged
- capability-backed width/height/offset validation now includes requested value, allowed range, increment/base, and nearest valid values where practical
- the CLI host surface now maps apply-configuration validation failures to `configuration_error` instead of only generic `command_error`
- hardware spot-checks on `DEV_1AB22C046D81` confirmed clearer real-device messages for:
  - invalid width `roi_width=2001`
  - invalid offset `roi_offset_x=17`

## Narrow Decisions

- keep strict rejection for invalid ROI requests
- do not silently round or rewrite caller input in this slice
- focus on width/height/offset constraints only
- optimize for clear diagnostics, not broader configuration UX

## Execution Plan

1. Re-read:
   - `docs/HARDWARE_CAPABILITIES.md`
   - `docs/HARDWARE_EVALUATION.md`
   - `apps/camera_cli/STATUS.md`
2. Inspect current ROI validation and error propagation paths.
3. Define one narrow clearer message shape for:
   - width increment failures
   - height increment failures
   - offset increment/range failures
4. Add focused tests for the clearer error behavior.
5. Update docs after validation.

## Validation

Required automated validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_request_models tests.test_command_controller tests.test_camera_cli
```

Recommended hardware spot-check if the camera is still attached:

- one invalid width request
- one invalid offset request

## Documentation Updates

- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- `apps/camera_cli/STATUS.md` if user-visible command errors change materially

## Expected Commit Shape

1. `fix: improve roi constraint error reporting`
2. `test: cover capability-aware roi validation messages`
3. `docs: record roi constraint reporting hardening`

## Merge Gate

- strict ROI validation remains intact
- host-/CLI-facing messages become clearer for at least width and offset constraint failures
- no auto-normalization or broader ROI feature work is bundled
- targeted tests pass locally

## Completion Note

Landed evidence for this slice:

- automated validation:
  - `.\.venv\Scripts\python.exe -m unittest tests.test_camera_configuration_validation_service tests.test_command_controller tests.test_camera_cli tests.test_request_models`
- hardware spot-checks on `DEV_1AB22C046D81`:
  - invalid width `roi_width=2001`
  - invalid offset `roi_offset_x=17`
- observed real-device guidance:
  - width message included feature `Width`, range, increment/base, and nearest valid values
  - offset message included feature `OffsetX`, range, increment/base, and nearest valid values

## Recovery Note

To activate this work package later:

1. read `docs/HARDWARE_CAPABILITIES.md`
2. read `docs/HARDWARE_EVALUATION.md`
3. read `apps/camera_cli/STATUS.md`
4. inspect the current ROI validation path before editing
