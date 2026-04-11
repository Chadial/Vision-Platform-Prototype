# Focus Metadata Policy Hardening

## Purpose

This work package defines the next execution-ready extension slice after the landed `WP17`, `WP18`, and `WP19` metadata-consumption and producer-wiring steps.

Closure lane:

- focus-metadata clarification and hardening inside the existing traceability-based artifact-metadata line

Slice role:

- narrow validation-policy hardening for the currently supported focus-summary metadata baseline

Its purpose is to move the artifact-level focus metadata shape from "explicit but still partly policy-open" toward "explicitly validated and testable for the currently supported summary fields and currently supported aggregation-basis handling."

The narrow goal is to harden the shared focus-summary validation seam at the traceability boundary without widening the repository into broader focus-statistics-policy design, reporting, analysis, or default-wiring redesign.

## Branch

- intended branch: `feature/focus-metadata-policy-hardening`
- activation state: current next execution-ready package after landed `WP19`

## Scope

Included:

- define one narrow validation policy for artifact-level focus summary metadata in the shared traceability helper
- reject ambiguous or internally inconsistent focus-summary metadata combinations before they are written into trace logs
- keep the policy reusable for both explicit tests and normal producer wiring
- add focused automated coverage for accepted and rejected combinations
- update docs so the current metadata shape is no longer only "aggregation basis required", but also explicitly bounded for the current summary-field baseline

Selected slice for this package:

- harden the shared `build_trace_artifact_metadata(...)` / traceability validation path so that:
  - summary fields still require an explicit aggregation basis
  - summary fields also require an explicit `focus_method`
  - the aggregation basis must be a positive integer for the current `focus_score_frame_interval` field
  - `focus_value_stddev`, when present, must be numeric and non-negative
- keep the existing producer behavior compatible with that narrower policy

Why this slice:

- `WP18` already clarified the stored metadata shape for the current summary-field family
- `WP19` already wired that shape into normal producer-side save flows where explicitly enabled
- this slice now hardens the shared validation seam those producer and consumer paths depend on
- it stays inside the existing traceability and producer boundaries
- it is locally verifiable through narrow unit coverage

Excluded:

- repository-wide mandatory default producer wiring
- broader focus-statistics redesign
- multiple aggregation-basis field types
- richer summary families or broader summary-field combinations
- richer reporting or offline export changes
- UI, CLI, API, or host payload expansion
- run/session explorer behavior

What this package does not close:

- the full long-term focus-statistics policy space
- future aggregation-policy variants beyond the currently supported `focus_score_frame_interval` baseline
- broader design decisions about additional summary families or stronger future policy rules

## Session Goal

Leave the repository with one explicit, shared rule set for the currently supported focus-summary metadata fields so later producers and consumers do not silently freeze incompatible assumptions.

The first completed slice should answer one concrete question:

- are the current artifact-level focus summary fields validated tightly enough that obviously ambiguous or invalid combinations are rejected at the shared traceability boundary?

## Current Context

The repository already has:

- a shared artifact-level traceability log
- an explicit aggregation-basis field for the current focus-summary metadata shape through `WP18`
- producer wiring for snapshot and bounded-recording save flows through `WP19`
- offline consumption of the saved focus metadata

The immediate remaining gap is:

- the current shared builder still accepts some ambiguous or weakly bounded combinations inside that already-supported summary-field baseline, and those combinations should be rejected explicitly before they become de facto policy

Remaining open policy questions after this slice:

- whether later packages should allow additional aggregation-basis variants
- whether later packages should add broader summary families or richer statistics outputs
- whether later packages should apply stricter or more specialized policy for different producer or consumer contexts

## Narrow Decisions

- this slice targets validation policy hardening, not metadata-shape redesign
- the current supported aggregation basis remains `focus_score_frame_interval`
- that field is treated as a positive integer count for this slice
- focus summary values remain optional
- if any focus summary value is present, `focus_method` must also be present
- `focus_value_stddev` must be numeric and non-negative when present
- the slice should not invent repository-wide default summary emission
- the slice should not widen into broader statistics policy such as min/max/median support
- this slice should be read as "the current supported summary-field baseline is now validated more explicitly", not as "all future focus-summary policy is now final"

## Execution Plan

1. Re-read:
   - `docs/STATUS.md`
   - `docs/WORKPACKAGES.md`
   - `services/recording_service/README.md`
   - `services/recording_service/STATUS.md`
2. Inspect the current traceability builder and artifact focus metadata producer for the narrowest shared validation seam.
3. Freeze the minimal policy additions for the current summary-field baseline:
   - `focus_method` required when summary values are present
   - `focus_score_frame_interval` must be a positive integer when present
   - `focus_value_stddev` must be numeric and non-negative when present
4. Implement the shared validation at the traceability boundary so explicit producers and tests both reuse the same rule.
5. Add focused tests for:
   - valid summary metadata
   - rejected summary metadata without `focus_method`
   - rejected non-positive or non-integer aggregation-basis values
   - rejected negative `focus_value_stddev`
6. Update docs once the policy is implemented and verified.

## Validation

Required automated validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_snapshot_service tests.test_recording_service tests.test_postprocess_tool tests.test_bootstrap
```

Recommended focused validation if producer behavior changes:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_snapshot_service tests.test_recording_service
```

## Documentation Updates

Before this work package is considered complete, update:

- `services/recording_service/STATUS.md`
- `services/recording_service/README.md`
- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`

## Expected Commit Shape

1. `feat: harden focus metadata summary policy`
2. `test: cover focus metadata summary validation`
3. `docs: record focus metadata policy hardening`

## Merge Gate

- the slice remains narrow and centered on shared validation for the current supported focus-summary metadata baseline
- accepted producer behavior remains compatible with the current explicit producer wiring
- invalid summary metadata is rejected deterministically
- targeted tests pass locally
- no UI, API, CLI, offline explorer, or broad reporting work is bundled
- no broader focus-policy expansion, statistics redesign, or richer summary-family design is bundled

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
