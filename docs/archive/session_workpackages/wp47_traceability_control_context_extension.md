# Traceability Control Context Extension

## Purpose

This work package defines one narrow post-closure traceability follow-up above the existing snapshot and bounded-recording artifact-log baseline.

Closure lane:

- Post-Closure Python Baseline / data and logging follow-up

Slice role:

- additive traceability control-context extension

Scope level:

- folder-level stable-context extension for the current snapshot and bounded-recording traceability path

Producer / Consumer / Structure impact:

- producer-facing and consumer-facing

Its purpose is to preserve a little more operational context around how a run was addressed and configured from the host side, without widening the traceability path into a broader inventory, query, or experiment-session system.

The narrow goal is to carry whether the current save flow used a resolved camera id, a camera alias, and a named configuration profile into the existing traceability context where that information is actually available.

## Branch

- intended branch: `feature/traceability-control-context-extension`
- activation state: landed

## Scope

Included:

- additive stable-context fields for current snapshot and bounded-recording traceability
- bounded producer wiring from the current CLI / request path into those fields
- compact offline stable-context exposure when those fields are present
- focused tests for request mapping, traceability output, and offline stable-context reuse

Excluded:

- traceability redesign
- run/session explorer behavior
- interval-capture traceability expansion
- camera inventory or alias-discovery behavior
- profile-management implementation itself

What this package does not close:

- the broader profile-management work from `WP45`
- a broader host-contract redesign
- per-run historical search or browsing
- any inventory or device-management layer

Which policy questions remain open:

- whether future profile-aware paths should also surface camera-class information beyond the current optional field
- whether interval-capture should ever gain the same traceability coverage
- whether any future host result surface should expose more of this control context directly

## Session Goal

Leave the repository with one additive proof that the current snapshot and bounded-recording traceability logs can preserve how the current save flow was selected and configured, including camera alias and later profile identity when supplied.

Landed outcome:

- `SnapshotRequest`, `RecordingRequest`, `SaveSnapshotRequest`, and `StartRecordingRequest` now carry optional `camera_alias`, `configuration_profile_id`, and `configuration_profile_camera_class` fields in addition to the existing resolved `camera_id`
- the current CLI now passes alias context into snapshot and bounded-recording save requests while preserving the existing resolved `camera_id` path
- snapshot and bounded-recording stable traceability context now records `camera_alias` when used and is ready to carry profile identity when later profile support is activated
- the offline focus-report stable-context view now exposes those fields additively when present
- March 31, 2026 hardware validation on the attached tested device confirmed alias-backed snapshot and bounded-recording traceability headers on the current real camera path

## Validation

- focused tests for request-model mapping of the added control-context fields
- focused traceability tests for bounded-recording and snapshot-side stable-context output
- focused offline/reporting tests for additive stable-context exposure
- bounded hardware proof for alias-backed snapshot and bounded recording on the tested camera path

## Documentation Updates

- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- `services/recording_service/STATUS.md`
- `services/recording_service/README.md`
- `apps/postprocess_tool/STATUS.md`
- `apps/postprocess_tool/README.md`

## Expected Commit Shape

1. `feat: extend traceability with control context`
2. `test: cover traceability control context`
3. `docs: record traceability control context extension`

## Merge Gate

- the slice remains additive to current snapshot and bounded-recording traceability
- no inventory, query, or history system is introduced
- alias and profile fields remain optional context rather than required identity keys
- the current traceability consumer path keeps degrading cleanly when those fields are absent

## Recovery Note

To activate this work package later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/MODULE_INDEX.md`
4. Read `docs/WORKPACKAGES.md`
5. Read `docs/STATUS.md`
6. Create the intended branch before substantive edits
