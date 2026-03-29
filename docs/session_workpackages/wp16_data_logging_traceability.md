# Data And Logging Traceability Extension

## Purpose

This work package defines the next execution-ready extension slice after the first narrow `WP14` visible-format baseline.

Its purpose is to move `Data And Logging Closure` from "saved artifacts exist in practical formats" toward "saved artifacts are experiment-usable and traceable."

The narrow goal is to add one stable, host- and experiment-readable metadata record for saved snapshot and bounded recording artifacts without reopening the broader storage architecture.

## Branch

- intended branch: `feature/data-logging-traceability-manifest`
- activation state: current next execution-ready package after the landed `WP14` and `WP15` narrow slices

## Scope

Included:

- define one narrow metadata record shape for saved image artifacts
- cover the current practical artifact paths first:
  - snapshot save
  - bounded recording save
- make the record suitable for experiment traceability and later offline consumption
- keep the metadata path deterministic and filesystem-local
- add focused tests for metadata record creation and key-field population
- update docs so `Data And Logging Closure` is no longer interpreted mainly as a visible-format lane

Selected slice for this package:

- artifact-level metadata manifest or sidecar support with at least:
  - saved file path or file name
  - system timestamp
  - camera timestamp where available
  - active camera id where available
  - pixel format
  - exposure/shutter value where available
  - gain where available
  - recording bounds or snapshot marker where relevant

Why this slice:

- it closes the most important remaining product-near gap after `WP14`
- it directly supports host-side logging and later offline reporting
- it stays narrow enough to implement without redesigning the full recording/logging stack

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

- can a saved snapshot or bounded recording artifact be paired with a concise, deterministic metadata record that a host or offline tool can consume later?

## Current Context

The repository already has:

- practical saved-image support including `BMP`
- recording CSV logs with some metadata
- offline focus-report reuse for saved `BMP` artifacts

The immediate remaining gap is:

- image artifacts and experiment context are still not linked in one narrow, stable artifact-level traceability path

## Narrow Decisions

- this slice targets artifact traceability, not broad logging redesign
- prefer one deterministic local record shape over multiple competing outputs
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
2. Inspect the current snapshot and bounded recording save paths for the narrowest insertion point for artifact-level metadata output.
3. Define one stable metadata record shape for saved artifacts.
4. Implement the metadata record for:
   - snapshot save
   - bounded recording output
5. Keep field population explicit and deterministic, with clear handling for unavailable values.
6. Add targeted tests for record creation and key metadata fields.
7. Update docs once the traceability path is real.

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

- saved artifacts can be paired with one deterministic metadata record
- key fields are understandable from an experiment and host-logging perspective
- missing camera-side fields degrade clearly instead of silently inventing values

## Documentation Updates

Before this work package is considered complete, update:

- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- `services/recording_service/STATUS.md`
- `services/recording_service/README.md`
- this file if a follow-up offline metadata-consumption slice becomes the natural next step

## Expected Commit Shape

1. `feat: add artifact metadata traceability baseline`
2. `test: cover artifact metadata traceability`
3. `docs: record data logging traceability extension`

## Merge Gate

- the slice remains narrow and centered on artifact traceability
- targeted tests pass locally
- no unrelated transport, UI, or broad storage redesign is bundled
- docs clearly state that this is the next extension inside `Data And Logging Closure`, not closure of the whole lane

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
