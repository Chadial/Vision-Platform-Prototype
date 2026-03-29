# Data And Logging Traceability Extension

## Purpose

This work package defines the next execution-ready extension slice after the first narrow `WP14` visible-format baseline.

Its purpose is to move `Data And Logging Closure` from "saved artifacts exist in practical formats" toward "saved artifacts are experiment-usable, append-friendly, and traceable."

The narrow goal is to add one stable, deterministic traceability baseline for saved snapshot and bounded recording artifacts without reopening the broader storage architecture or forcing a brand-new log file for every bounded run.

## Branch

- intended branch: `feature/data-logging-traceability-manifest`
- activation state: current next execution-ready package after the landed `WP14` and `WP15` narrow slices

## Scope

Included:

- define one narrow metadata record shape for snapshot artifacts and one narrow folder-local traceability log structure for bounded recording
- cover the current practical artifact paths first:
  - snapshot save
  - bounded recording save
- make the record suitable for experiment traceability and later offline consumption
- keep the metadata path deterministic and filesystem-local
- add focused tests for metadata record creation and key-field population
- update docs so `Data And Logging Closure` is no longer interpreted mainly as a visible-format lane

Selected slice for this package:

- snapshot-side direct sidecar metadata record with at least:
  - saved file path or file name
  - system timestamp
  - camera timestamp where available
  - camera id where available
  - pixel format
  - exposure/shutter where available
  - gain where available
  - marker that the record belongs to a snapshot artifact
- bounded-recording folder-local traceability log with:
  - one stable context header for log reuse decisions
  - one or more run/session blocks inside the same log
  - one per-image row for each saved artifact
- bounded-recording run/session block fields with at least:
  - run start timestamp
  - run end timestamp where available
  - bounded-recording end state marker indicating regular or failed completion
  - run/session id or equivalent deterministic run marker
  - recording bounds used such as frame limit and duration when present
  - target frame rate where present
- bounded-recording stable context fields with at least:
  - save directory
  - camera id where available
  - pixel format
  - exposure/shutter where available
  - gain where available
  - ROI / offsets where present and treated as experiment-relevant
  - marker that this log belongs to bounded recording traceability

Why this slice:

- it closes the most important remaining product-near gap after `WP14`
- it directly supports host-side logging and later offline reporting
- it keeps snapshot and recording treatment intentionally asymmetric, which is the narrower practical choice for the current repository shape
- it supports repeated appended runs in one folder without treating every run-level change as a mandatory new-log event

Excluded:

- database or indexing work
- broad CSV redesign
- full folder-series redesign
- transport or API payload work
- broad UI/reporting changes
- arbitrary metadata extraction beyond the current camera and command baselines

## Session Goal

Leave the repository with one explicit, stable metadata-traceability baseline for saved artifacts so experiment output is not just visible, but also attributable.

The first completed slice should answer one concrete question:

- can a saved snapshot or appended bounded recording run be paired with a concise, deterministic local traceability record that a host or offline tool can consume later?

## Current Context

The repository already has:

- practical saved-image support including `BMP`
- recording CSV logs with some metadata
- offline focus-report reuse for saved `BMP` artifacts

The immediate remaining gap is:

- image artifacts and experiment context are still not linked in one narrow, stable traceability path that also behaves sensibly when repeated runs are appended in the same folder

## Narrow Decisions

- this slice targets artifact traceability, not broad logging redesign
- snapshot artifacts use direct sidecar metadata because they are naturally one-file outputs
- bounded recording uses one deterministic folder-local log rather than per-run or per-frame sidecars because append-style experiment use is the narrower practical fit
- bounded-recording log reuse is based on stable context match, not on run start time alone
- changes in run/session fields such as start time, end time, duration, frame limit, or target frame rate should create a new run block inside the existing log, not necessarily a new log file
- a new bounded-recording log file is only required when the stable context no longer matches cleanly
- prefer one deterministic local metadata path per save mode over multiple competing outputs
- this package does not replace the existing CSV path; it adds one narrower host-/experiment-readable traceability baseline beside it
- bounded-recording traceability should make stable context, run/session values, per-image rows, and regular-vs-failed completion understandable without turning this slice into a broad lifecycle redesign
- metadata fields may be omitted when unavailable, but the record shape itself should stay stable
- the result must stay usable by later offline/reporting slices without requiring a transport layer

## Execution Plan

1. Re-read:
   - `docs/STATUS.md`
   - `docs/WORKPACKAGES.md`
   - `services/recording_service/README.md`
   - `services/recording_service/STATUS.md`
   - `apps/postprocess_tool/README.md`
   - `apps/postprocess_tool/STATUS.md`
2. Inspect the current snapshot and bounded recording save paths for the narrowest insertion points for:
   - snapshot sidecar output
   - bounded-recording folder-local traceability log output
3. Define one stable snapshot sidecar shape and one bounded-recording log structure with:
   - stable context header
   - run/session block fields
   - per-image rows
4. Implement snapshot traceability as direct artifact-level sidecar output.
5. Decide and freeze the stable bounded-recording context field set used for log reuse.
6. Decide and freeze the bounded-recording run/session field set that may vary inside one reused log.
7. Implement bounded-recording traceability with append/reuse behavior based on stable context match.
8. Keep field population explicit and deterministic, with clear handling for unavailable values.
9. Add targeted tests for:
   - snapshot sidecar creation and key fields
   - bounded-recording log reuse when stable context still matches
   - creation of a new run/session block when only run/session fields differ
   - creation of a new log only when stable context changes
   - deterministic markers distinguishing snapshot vs. bounded recording records
10. Update docs once the traceability path is real.

## Validation

Required automated validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_snapshot_service tests.test_recording_service tests.test_file_naming
```

Recommended focused validation if a shared metadata helper is added:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_snapshot_service tests.test_recording_service tests.test_postprocess_tool tests.test_bootstrap
```

Manual review points:

- snapshot artifacts receive one direct sidecar record
- bounded recording uses one folder-local appendable log rather than per-run sidecars
- stable context and run/session information are clearly separated in the bounded-recording path
- a repeated run in the same folder reuses the existing log when stable context still matches
- a repeated run creates a new run/session block when only run fields differ
- a new bounded-recording log file is only created when the stable context no longer matches
- bounded recording start, end, and regular-vs-failed completion are understandable from the log structure
- key fields are understandable from an experiment and host-logging perspective
- missing camera-side fields degrade clearly instead of silently inventing values

## Documentation Updates

Before this work package is considered complete, update:

- `docs/STATUS.md`
- `services/recording_service/STATUS.md`
- `services/recording_service/README.md`
- `docs/WORKPACKAGES.md` only if the implementation changes the PM interpretation or next-step ordering
- this file if a follow-up offline metadata-consumption slice becomes the natural next step

## Expected Commit Shape

1. `feat: add artifact metadata traceability baseline`
2. `test: cover artifact metadata traceability`
3. `docs: record data logging traceability extension`

## Merge Gate

- the slice remains narrow and centered on artifact traceability
- snapshot and bounded recording are not forced into the same metadata granularity
- bounded recording remains append-friendly for repeated experiment use in one folder
- targeted tests pass locally
- no unrelated transport, UI, or broad storage redesign is bundled
- docs clearly state that this is a narrow append-friendly traceability baseline inside `Data And Logging Closure`, not closure of the whole lane

## Recovery Note

To activate this work package later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/MODULE_INDEX.md`
4. Read `docs/WORKPACKAGES.md`
5. Read `docs/STATUS.md`
6. Read `services/recording_service/README.md`
7. Read `services/recording_service/STATUS.md`
8. Read `docs/git_strategy.md`
9. Create the intended branch before any substantive edits
