# Interval Capture Timing And Polling Tightening

## Purpose

This work package defines the next execution-ready follow-up behind `WP29`.

Closure lane:

- Post-Closure Python Baseline / Hardening

Slice role:

- bounded timing and polling hardening

Scope level:

- current interval-capture timing confidence and active-run polling meaning on the integrated baseline

Its purpose is to tighten the remaining confidence gap around interval-capture timing, especially where recent real-device evidence showed `skipped_intervals=1` and where active polling should remain meaningful during work.

This package should be read as:

- bounded interval-capture hardening
- not a scheduler redesign
- not a broad transport/status expansion

## Branch

- intended branch: `fix/interval-capture-timing-polling-tightening`
- activation state: active lane

## Scope

Included:

- inspect current interval-capture pacing, skip accounting, and active polling surfaces
- clarify whether the current observed skip behavior is acceptable timing variance or one tighter fix target
- tighten one narrow seam around:
  - skip accounting
  - active-run progress visibility
  - completion-state clarity
- add focused validation for simulator and, if hardware is attached, one bounded real-device timing proof

Excluded:

- full timing-accuracy campaign
- transport redesign
- broad status-model redesign
- trigger-mode capture work

What this package does not close:

- full real-time scheduling guarantees
- all timing drift concerns across every device path
- general performance benchmarking

## Session Goal

Leave the repository with one tighter interval-capture baseline where skip behavior and active polling are explicit enough that later sessions do not have to infer whether the current path is behaving acceptably.

## Current Context

The integrated baseline already supports interval capture and active-run polling.

The immediate remaining gap is:

- a recent bounded hardware rerun showed one skipped interval
- the current baseline should classify and expose that behavior more clearly before broader expansion is considered

## Narrow Decisions

- keep the slice centered on the current interval-capture path only
- treat one bounded real-device proof as sufficient if hardware is attached
- prefer clearer accounting over broader scheduling ambition

## Execution Plan

1. Re-read:
   - `docs/HARDWARE_EVALUATION.md`
   - `services/recording_service/STATUS.md`
   - `apps/camera_cli/STATUS.md`
2. Inspect interval-capture status, skip accounting, and polling payload paths.
3. Freeze one narrow improvement target.
4. Add focused tests for skip/polling behavior.
5. Re-run one bounded interval-capture proof and document the result.

## Validation

Required automated validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_interval_capture_service tests.test_command_controller tests.test_camera_cli tests.test_api_service
```

Recommended hardware validation if the camera is attached:

- one bounded interval-capture run with active polling on `DEV_1AB22C046D81`

## Documentation Updates

- `docs/HARDWARE_EVALUATION.md` if hardware proof is rerun
- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- relevant module `STATUS.md` if polling or interval behavior changes materially

## Expected Commit Shape

1. `fix: tighten interval capture timing and polling`
2. `test: cover interval skip and polling behavior`
3. `docs: record interval timing tightening`

## Merge Gate

- the slice remains bounded to interval timing and polling meaning
- no broad scheduler or status redesign is bundled
- targeted tests pass locally
- any hardware observation is recorded explicitly if rerun

## Recovery Note

To activate this work package later:

1. read `docs/HARDWARE_EVALUATION.md`
2. read `services/recording_service/STATUS.md`
3. inspect the current interval-capture status and polling path before editing
