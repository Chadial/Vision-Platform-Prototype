# Host Status Polling Hardening

## Purpose

This work package defines the next execution-ready slice after the landed offline metadata and traceability follow-ups.

Its purpose is to tighten the host-readable polling surface during active experiment runs without widening the repository into broader API or transport work.

## Branch

- intended branch: `feature/host-status-polling-hardening`
- activation state: current next execution-ready package after landed `WP21`

## Scope

Included:

- inspect the current `SubsystemStatus` and adapter-facing status payload path
- add one conservative active-run polling subset for host use during bounded recording and interval capture
- keep the change additive and host-readable
- add focused automated coverage for active and idle polling states
- update docs to mark the status surface as narrowed for active experiment polling

Selected slice for this package:

- expose a compact additive status subset such as:
  - active operation kind
  - active file stem where available
  - active save directory where available
  - frames written or equivalent progress field where already available
  - last error or failure marker where already present

Excluded:

- new transport work
- broad status redesign
- run/session history
- UI changes
- hardware-only validation

## Session Goal

Leave the repository with one explicit proof that a host can poll a running experiment and receive a tighter, additive active-run status subset without inferring it indirectly from scattered fields.

## Execution Plan

1. Re-read:
   - `docs/STATUS.md`
   - `docs/WORKPACKAGES.md`
   - `services/recording_service/STATUS.md`
2. Inspect the current `SubsystemStatus`, controller status mapper, API DTO mapper, and CLI status envelope.
3. Freeze one conservative additive active-run polling subset.
4. Implement the narrow status expansion without widening command or transport scope.
5. Add focused tests for idle, active recording, active interval capture, and failure-degraded polling states.
6. Update docs once the status shape is verified.

## Validation

Required automated validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_command_controller tests.test_bootstrap tests.test_request_models
```

## Documentation Updates

- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- relevant host/control module `STATUS.md` if touched

## Expected Commit Shape

1. `feat: harden host status polling slice`
2. `test: cover host status polling details`
3. `docs: record host status polling hardening`

## Merge Gate

- the slice stays additive and polling-focused
- no transport or UI widening is bundled
- targeted tests pass locally

## Recovery Note

To activate this work package later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/MODULE_INDEX.md`
4. Read `docs/WORKPACKAGES.md`
5. Read `docs/STATUS.md`
6. Create the intended branch before substantive edits
