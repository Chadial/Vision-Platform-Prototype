# Offline And Measurement Metadata Extension

## Purpose

This work package defines the next execution-ready extension slice after the landed `WP15` offline artifact-reuse baseline and the landed `WP16` traceability baseline.

Its purpose is to move `Offline And Measurement Closure` from "saved artifacts can be re-read for focus checks" toward "the existing offline focus report can reuse the experiment context already written beside those artifacts."

The narrow goal is to make the existing postprocess focus-report path metadata-aware for the current saved-artifact baseline without turning the postprocess tool into a broader measurement, reporting, ROI-exploration, or analytics surface.

## Branch

- intended branch: `feature/offline-measurement-metadata-extension`
- activation state: current next execution-ready package after landed `WP16`

## Scope

Included:

- extend the thin offline focus-report path so it can read the folder-local traceability log created by `WP16`
- join saved artifact rows to offline report entries through deterministic saved-image names
- expose a narrow metadata-aware offline report shape for the currently supported saved-artifact baseline
- keep the offline join path usable when the traceability log is absent or incomplete
- add focused tests for metadata-aware offline reuse over saved `BMP` artifacts
- update docs so the next `Offline And Measurement Closure` slice is no longer only about image reload, but also about artifact-context reuse

Selected slice for this package:

- offline focus-report reuse of `WP16` traceability data for saved `BMP` artifacts in one folder, with at least:
  - `artifact_kind`
  - `run_id` where available
  - `camera_timestamp` where available
  - `system_timestamp_utc` where available
- optional analysis-related artifact metadata reuse where already present in the shared traceability path, with preference for:
  - `analysis_roi_type`
  - `analysis_roi_data`
  - `focus_method`
  - `focus_value_mean`
  - `focus_value_stddev`
- `frame_id` only if the current traceability path already guarantees it cleanly enough to treat it as a stable joined field for this slice
- optional folder-level stable context exposure where already available from the shared trace log header

Why this slice:

- it directly consumes the new traceability baseline instead of leaving `WP16` producer-only
- it keeps the postprocess tool thin while proving one practical offline metadata join
- it stays locally verifiable and within the current `postprocess_tool` plus `recording_service` boundaries

Excluded:

- broad offline workstation behavior
- arbitrary metadata extraction beyond the current shared traceability log
- general-purpose CSV ingestion frameworks
- new artifact formats beyond the current saved-`BMP` offline baseline
- broad reporting/export redesign
- run/session explorer behavior
- general artifact browsing
- ROI explorer behavior
- measurement algorithms beyond the current focus-report path

## Session Goal

Leave the repository with one explicit proof that offline focus results can stay linked to the experiment context already written during artifact creation.

The first completed slice should answer one concrete question:

- can an offline focus report over saved artifacts reuse the folder-local traceability log so artifact context and focus results stay paired?

## Current Context

The repository already has:

- a thin postprocess focus-report path for `.pgm`, `.ppm`, and saved `BMP` artifacts
- one folder-local appendable traceability log for snapshot and bounded recording output
- deterministic per-image rows keyed by saved image name

The immediate remaining gap is:

- the offline report path still ignores that new traceability record, so focus results and artifact metadata are separated again during postprocess use

## Narrow Decisions

- this slice targets metadata consumption, not traceability-log redesign
- this slice is a metadata-aware focus-report extension, not a broad offline measurement package
- the offline join key should stay the deterministic saved image name already written by `WP16`
- the compact joined metadata shape should be frozen only after verifying which per-image fields are actually guaranteed by the current traceability path
- the report must remain usable when no traceability log exists, with metadata fields omitted rather than invented
- if a traceability log exists but one image row is missing, the image should still be evaluated and reported with missing metadata fields
- prefer the conservative minimum joined field set first:
  - `artifact_kind`
  - `run_id` where available
  - `camera_timestamp` where available
  - `system_timestamp_utc` where available
- treat analysis-oriented ROI metadata as optional joined artifact metadata for this slice, not as a reason to widen the report into ROI inspection behavior
- if focus-related artifact metadata is already present in the shared traceability path, it may be joined too, but only in the same compact artifact-metadata shape
- treat `frame_id` as optional for this slice unless the current producer path proves it is stably guaranteed and worth freezing into the compact report shape now
- the first metadata-aware report shape should stay compact and text-oriented rather than introducing a richer export surface
- stable context exposure should stay optional and narrow; do not widen this slice into a full run/session explorer
- do not widen this slice into a general artifact browser, ROI explorer, session explorer, or reporting framework

## Execution Plan

1. Re-read:
   - `docs/STATUS.md`
   - `docs/WORKPACKAGES.md`
   - `apps/postprocess_tool/README.md`
   - `apps/postprocess_tool/STATUS.md`
   - `services/recording_service/README.md`
   - `services/recording_service/STATUS.md`
   - `docs/session_workpackages/wp16_data_logging_traceability.md`
2. Inspect the current postprocess focus-report path and the shared traceability log helper for the narrowest metadata-consumption seam.
3. Verify which per-image metadata fields are actually guaranteed by the current traceability log and freeze a conservative minimum joined field set before changing the report shape.
4. Define one compact metadata-aware offline report shape that extends the existing per-image focus entry instead of replacing it.
   - prefer `artifact_kind`, `run_id`, `camera_timestamp`, and `system_timestamp_utc` where available
   - join analysis ROI metadata only where it is already present in the traceability path and keep it in a compact text-safe shape
   - join focus-related artifact metadata only where it is already present in the traceability path and keep it in the same compact artifact-metadata shape
   - include `frame_id` only if the current traceability path proves it is cleanly guaranteed for this narrow slice
5. Implement a small traceability-reader path that can:
   - read stable context header fields where available
   - read per-image artifact rows
   - map those rows by saved image name
6. Extend the offline report flow to attach metadata to each saved-artifact report entry when available.
7. Keep missing or partial metadata explicit and deterministic.
8. Add targeted tests for:
   - successful metadata join over saved `BMP` artifacts with a matching traceability log
   - successful offline report generation when no traceability log exists
   - successful offline report generation when an image has no matching trace row
   - successful offline report generation when the traceability log is present but only the conservative minimum joined fields are usable
   - successful offline report generation when optional analysis ROI metadata is present for some artifacts and absent for others
   - stable formatting of the added metadata fields in the compact report output
9. Update docs once the metadata-aware offline path is real.

## Validation

Required automated validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_postprocess_tool tests.test_recording_service tests.test_snapshot_service
```

Recommended focused validation if a shared traceability reader is added:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_postprocess_tool tests.test_file_naming tests.test_vision_platform_namespace
```

Manual review points:

- saved `BMP` artifacts can still be evaluated offline without any live camera path
- the offline focus report now reuses traceability metadata when the shared folder-local log is present
- missing traceability data degrades clearly instead of blocking the offline report
- partial traceability data also degrades clearly instead of forcing unstable placeholder fields
- the added metadata stays narrow and understandable from an experiment-follow-up perspective
- optional ROI metadata stays in the same compact artifact-metadata shape and does not turn the report into ROI exploration
- the report shape still reads as a compact focus-report result, not as a run/session explorer, ROI explorer, or broader offline reporting surface

## Documentation Updates

Before this work package is considered complete, update:

- `apps/postprocess_tool/STATUS.md`
- `apps/postprocess_tool/README.md`
- `services/recording_service/STATUS.md` if the shared traceability path gains a new reusable read surface
- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`

## Expected Commit Shape

1. `feat: add metadata-aware offline focus report slice`
2. `test: cover offline metadata-aware focus reporting`
3. `docs: record offline metadata extension slice`

## Merge Gate

- the slice remains narrow and centered on offline reuse of the existing traceability baseline
- targeted tests pass locally
- no run/session explorer behavior is bundled
- no ROI explorer behavior is bundled
- no broad export, UI, API, reporting-framework, or metadata-framework work is bundled
- no general offline workstation behavior or artifact-browser expansion is bundled
- docs clearly state that this is a metadata-consumption slice inside `Offline And Measurement Closure`, not closure of that lane in full

## Recovery Note

To activate this work package later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/MODULE_INDEX.md`
4. Read `docs/WORKPACKAGES.md`
5. Read `docs/STATUS.md`
6. Read `apps/postprocess_tool/README.md`
7. Read `apps/postprocess_tool/STATUS.md`
8. Read `services/recording_service/README.md`
9. Read `services/recording_service/STATUS.md`
10. Read `docs/git_strategy.md`
11. Create the intended branch before any substantive edits
