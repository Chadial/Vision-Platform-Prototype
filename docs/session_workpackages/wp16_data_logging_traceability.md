# Data And Logging Traceability Extension

## Purpose

This work package defines the next execution-ready extension slice after the first narrow `WP14` visible-format baseline.

Its purpose is to move `Data And Logging Closure` from "saved artifacts exist in practical formats" toward "saved artifacts are experiment-usable and traceable."

The narrow goal is to add one stable, deterministic traceability baseline for saved snapshot and bounded recording artifacts without reopening the broader storage architecture.

## Branch

- intended branch: `feature/data-logging-traceability-manifest`
- activation state: current next execution-ready package after the landed `WP14` and `WP15` narrow slices

## Scope

Included:

- define one narrow metadata record shape for snapshot artifacts and one narrow session-level metadata record for bounded recording
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
- bounded-recording session-level manifest with at least:
  - session output directory or session identity
  - system start timestamp
  - system end timestamp where available
  - bounded-recording end state marker indicating regular or failed completion
  - camera id where available
  - pixel format
  - exposure/shutter where available
  - gain where available
  - recording bounds used such as frame limit and duration when present
  - marker that the record belongs to a bounded recording session

Why this slice:

- it closes the most important remaining product-near gap after `WP14`
- it directly supports host-side logging and later offline reporting
- it keeps snapshot and recording treatment intentionally asymmetric, which is the narrower practical choice for the current repository shape

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

- can a saved snapshot or bounded recording run be paired with a concise, deterministic local metadata record that a host or offline tool can consume later?

## Current Context

The repository already has:

- practical saved-image support including `BMP`
- recording CSV logs with some metadata
- offline focus-report reuse for saved `BMP` artifacts

The immediate remaining gap is:

- image artifacts and experiment context are still not linked in one narrow, stable traceability path

## Narrow Decisions

- this slice targets artifact traceability, not broad logging redesign
- snapshot artifacts use direct sidecar metadata because they are naturally one-file outputs
- bounded recording uses one minimal session-level manifest because per-frame sidecars would broaden the package too early
- prefer one deterministic local metadata path per save mode over multiple competing outputs
- this package does not replace the existing CSV path; it adds one narrower host-/experiment-readable traceability baseline beside it
- bounded-recording traceability should make start, end, and regular-vs-failed completion understandable without turning this slice into a broad lifecycle redesign
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
   - bounded-recording session manifest output
3. Define one stable snapshot sidecar shape and one stable bounded-recording session manifest shape.
4. Implement snapshot traceability as direct artifact-level sidecar output.
5. Implement bounded-recording traceability as one minimal session-level manifest.
6. Keep field population explicit and deterministic, with clear handling for unavailable values.
7. Add targeted tests for:
   - snapshot sidecar creation and key fields
   - bounded-recording manifest creation and key fields
   - deterministic markers distinguishing snapshot vs. bounded recording records
8. Update docs once the traceability path is real.

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
- bounded recording runs receive one minimal session-level manifest rather than per-frame metadata output
- bounded recording start, end, and regular-vs-failed completion are understandable from the manifest
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
- targeted tests pass locally
- no unrelated transport, UI, or broad storage redesign is bundled
- docs clearly state that this is a traceability baseline extension inside `Data And Logging Closure`, not closure of the whole lane

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
