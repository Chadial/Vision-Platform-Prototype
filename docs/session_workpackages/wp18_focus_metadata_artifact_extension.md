# Focus Metadata Artifact Extension

## Purpose

This work package defines the next narrow execution-ready extension after the landed `WP16` traceability/log-structure baseline.

Its purpose is to move the repository from "artifact traceability can carry acquisition-context metadata" toward "artifact traceability can also preserve one explicit, reusable baseline for analysis-related focus metadata."

The narrow goal is to define and harden one deterministic optional per-artifact metadata shape for focus-related values, including the analysis-/focus-related ROI metadata that belongs with those values, without widening this slice into broader focus-analysis, ROI-management, reporting, or UI work.

## Branch

- intended branch: `feature/focus-metadata-artifact-extension`
- activation state: queued follow-up after the current traceability/logging baseline and the current offline metadata-consumption slice

## Scope

Included:

- define one stable optional artifact-level focus metadata shape for saved artifacts
- define one deterministic serialization baseline for analysis-/focus-related ROI metadata when present
- keep focus- and ROI-related metadata at the per-image / per-artifact level by default
- keep missing focus metadata explicit and non-fatal
- wire the selected fields into the existing traceability structures only as optional artifact-level metadata
- add focused tests for deterministic storage and reuse behavior when this slice includes implementation work
- update docs so focus- and analysis-ROI-related artifact metadata is an explicit narrow extension, not an implied side effect

Selected slice for this package:

- one optional per-artifact analysis-metadata family for saved artifacts with narrow support for:
  - `analysis_roi_id`
  - `analysis_roi_type`
  - `analysis_roi_data`
  - `focus_method` / `focus_art`
  - `focus_score_frame_interval` or equivalent explicit aggregation-basis field when summary values are present
  - `focus_value_mean`
  - `focus_value_stddev`
  - `focus_roi_type`
  - `focus_roi_data`
- one deterministic ROI serialization baseline limited to the current portable ROI shapes where relevant:
  - `global`
  - `rectangle(x1,y1,x2,y2)`
  - `ellipse(x_c,y_c,x_corner,y_corner)`
  - `freehand(x1,y1,x2,y2,...,xn,yn)`

Why this slice:

- it keeps `WP16` focused on the core traceability/log structure instead of continuing to absorb analysis-specific metadata concerns
- it provides one explicit reusable baseline for later offline/reporting consumers without requiring a broader reporting redesign
- it keeps focus-related metadata below the threshold of a larger focus-method or measurement package

Excluded:

- broad focus-method expansion
- live preview focus UI or overlay work
- broader measurement algorithms or measurement tooling
- broad offline reporting redesign
- general-purpose ROI editor or ROI explorer behavior
- general ROI-management infrastructure
- transport/API payload work
- large metadata-architecture redesign

## Session Goal

Leave the repository with one explicit, deterministic baseline for storing and reusing focus-related artifact metadata so later consumers do not need to infer or invent those fields ad hoc.

The first completed slice should answer one concrete question:

- can the repository preserve optional focus-related artifact metadata, including the relevant analysis ROI shape, without treating those values as stable-header or run/session identity?

## Current Context

The repository already has:

- a shared folder-local traceability log baseline from `WP16`
- one narrow offline metadata-consumption path for saved artifacts
- existing focus and ROI contracts that already define portable methods and shapes

The immediate remaining gap is:

- focus-related artifact metadata is now visible as a real need, but it should not further blur the responsibility of the core traceability/log-structure package

## Narrow Decisions

- this slice targets artifact-level analysis metadata, not broad focus-analysis expansion
- focus-related values are optional per-artifact metadata, not default stable-header identity
- analysis-/focus-related ROI metadata is optional per-artifact metadata, not default stable-header identity
- `focus_value_mean` and `focus_value_stddev` should only be used when their aggregation basis is made explicit
- if interval-based aggregation is used, that basis should be stored explicitly through `focus_score_frame_interval` or an equivalent field already compatible with the repository contracts
- changing focus values must not force a new log file
- changing focus ROI must not automatically force a new stable context header
- changing analysis ROI metadata must not automatically force a new stable context header
- the deterministic ROI serialization baseline should stay narrow and text-oriented
- missing focus metadata should remain representable without inventing placeholder values
- if a caller does not have enough basis information to support summary fields cleanly, `focus_value_mean` and `focus_value_stddev` should be omitted rather than guessed
- exact defaults and allowed bounds for any future focus-statistics policy are not finalized in this package and remain follow-up work unless they are already enforced elsewhere in the repository
- if a later slice wants constant focus configuration mirrored at run level, that remains separate follow-up work
- this package must not drift into an ROI explorer, ROI editor, reporting framework, or broader offline workstation surface

## Open Questions

- if `focus_score_frame_interval` is the chosen aggregation-basis field, what default value should eventually be used when a caller wants summary metadata by default?
- if interval-based aggregation becomes standard, what bounds or validation rules should eventually apply to that interval?
- should later focus-summary policy stay interval-based only, or should additional explicit aggregation-basis forms be allowed?
- these questions should be tested and defined later; this package should only make the need for an explicit aggregation basis visible, not silently finalize the policy

## Execution Plan

1. Re-read:
   - `docs/STATUS.md`
   - `docs/WORKPACKAGES.md`
   - `docs/session_workpackages/wp16_data_logging_traceability.md`
   - `docs/session_workpackages/wp17_offline_measurement_metadata_extension.md`
   - `services/recording_service/README.md`
   - `services/recording_service/STATUS.md`
   - `apps/postprocess_tool/README.md`
   - `apps/postprocess_tool/STATUS.md`
2. Inspect the current traceability writer/reader path and identify the narrowest seams for explicit focus-related artifact metadata handling.
3. Freeze one compact artifact-level metadata shape for:
   - focus-method/value fields
   - analysis ROI fields
   - focus ROI fields
4. Define one explicit aggregation-basis rule for `focus_value_mean` and `focus_value_stddev`:
   - they must not appear as ambiguous standalone values
   - if they are stored, the aggregation basis must be carried explicitly
   - if interval-based aggregation is used, store that interval explicitly through `focus_score_frame_interval` or equivalent compatible naming
   - omit mean/stddev when that aggregation basis is not available cleanly for the artifact
   - if exact defaults or bounds are not yet validated by current repository behavior, record them as still-open policy work instead of freezing them implicitly here
5. Freeze one deterministic serialization rule for supported ROI forms:
   - `global`
   - `rectangle(...)`
   - `ellipse(...)`
   - `freehand(...)`
6. Decide and document how unavailable focus metadata is represented without broadening the log or offline-report shape.
7. Implement or tighten the traceability write/read path only as needed to make the selected field shape explicit and stable.
8. Add targeted tests for:
   - deterministic serialization of supported ROI forms
   - stable storage of optional focus-related artifact fields
   - stable handling of explicit aggregation-basis metadata when summary fields are present
   - stable reuse behavior when focus or ROI metadata differs between artifacts in the same reusable log
   - graceful handling when some artifacts have no focus metadata
9. Record any still-unresolved aggregation-policy defaults or bounds explicitly in docs instead of letting implementation assumptions become implicit.
10. Update docs once the artifact-level focus metadata path is explicit and validated.

## Validation

Required automated validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_snapshot_service tests.test_recording_service tests.test_postprocess_tool
```

Recommended focused validation if ROI-serialization helpers or shared traceability helpers change:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_focus_core tests.test_snapshot_service tests.test_recording_service tests.test_postprocess_tool
```

Manual review points:

- focus-related artifact metadata is clearly modeled as optional per-image metadata
- analysis ROI and focus ROI metadata stay at the artifact level and do not become stable-header identity by default
- `focus_value_mean` and `focus_value_stddev` are tied to an explicit aggregation basis instead of being ambiguous standalone fields
- differing focus values or ROI metadata do not cause unnecessary log splitting
- deterministic ROI serialization is understandable and stable across the supported narrow shape set
- unresolved defaults, bounds, or other aggregation-policy choices are documented explicitly instead of being silently assumed
- the result still reads as a traceability/offline extension, not as a broader focus-analysis, ROI-management, or focus-statistics-policy package

## Documentation Updates

Before this work package is considered complete, update:

- `docs/STATUS.md`
- `services/recording_service/STATUS.md`
- `services/recording_service/README.md` if the shared traceability contract becomes more explicit
- `apps/postprocess_tool/STATUS.md` if offline consumption changes materially
- `docs/WORKPACKAGES.md` only at the minimal PM-registration level

## Expected Commit Shape

1. `feat: add artifact-level focus metadata baseline`
2. `test: cover focus metadata artifact handling`
3. `docs: record focus metadata artifact extension`

## Merge Gate

- the slice remains narrow and centered on optional per-artifact focus/analysis metadata
- focus and ROI metadata do not become stable-header identity by default
- targeted tests pass locally
- no broad focus-method, reporting, ROI-management, UI, or transport work is bundled
- docs clearly state that this is a narrow follow-up extension after the core traceability/log-structure baseline

## Recovery Note

To activate this work package later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/MODULE_INDEX.md`
4. Read `docs/WORKPACKAGES.md`
5. Read `docs/STATUS.md`
6. Read `docs/session_workpackages/wp16_data_logging_traceability.md`
7. Read `docs/session_workpackages/wp17_offline_measurement_metadata_extension.md`
8. Read `services/recording_service/README.md`
9. Read `services/recording_service/STATUS.md`
10. Read `apps/postprocess_tool/README.md`
11. Read `apps/postprocess_tool/STATUS.md`
12. Read `docs/git_strategy.md`
13. Create the intended branch before any substantive edits
