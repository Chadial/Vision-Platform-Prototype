# Focus Metadata Producer Wiring

## Purpose

This work package defines the next narrow execution-ready slice after the landed `WP18` artifact-metadata shape clarification.

Its purpose is to move the repository from "artifact-level focus metadata fields are defined and validated" toward "normal snapshot and bounded-recording save flows can emit those fields through explicit producer wiring instead of manual test-only injection."

The narrow goal is to wire one reusable focus-metadata producer into the existing save paths without silently freezing broader focus-statistics policy.

## Branch

- intended branch: `feature/focus-metadata-producer-wiring`
- activation state: landed narrow follow-up after `WP18`

## Scope

Included:

- add one reusable producer for artifact-level focus metadata
- wire that producer into `SnapshotService` and `RecordingService`
- allow bootstrap / subsystem composition to opt into the producer explicitly
- keep summary fields gated behind an explicit aggregation basis
- add focused tests for snapshot, recording, and bootstrap wiring
- update docs so the producer path is no longer only implied by traceability structure

Excluded:

- new focus methods
- broad statistics-policy finalization
- UI or offline workstation expansion
- broad reporting redesign
- transport/API work

## Session Goal

Leave the repository with one explicit producer path so saved artifacts can carry focus metadata through normal save handling when the subsystem is configured to do so.

## Execution Plan

1. Inspect the current traceability writer path and existing focus services.
2. Add one reusable artifact-level focus metadata producer.
3. Wire it into snapshot and bounded-recording save flows.
4. Expose the wiring through explicit bootstrap configuration instead of hidden defaults.
5. Keep summary fields conditional on an explicit aggregation basis.
6. Add targeted tests for snapshot, recording, and bootstrap behavior.
7. Update status and PM docs once the producer path is real.

## Validation

Required automated validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_snapshot_service tests.test_recording_service tests.test_postprocess_tool tests.test_bootstrap
```

Recommended focused validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_focus_core tests.test_snapshot_service tests.test_recording_service tests.test_postprocess_tool tests.test_bootstrap
```

## Documentation Updates

- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- `services/recording_service/README.md`
- `services/recording_service/STATUS.md`
- `docs/session_workpackages/wp18_focus_metadata_artifact_extension.md` only if activation wording needs clarification

## Expected Commit Shape

1. `feat: wire focus metadata producers into save flows`
2. `test: cover focus metadata producer wiring`
3. `docs: record focus metadata producer wiring`

## Merge Gate

- the slice remains narrow and centered on producer wiring
- save flows only emit summary fields when an explicit aggregation basis is present
- tests pass locally
- docs clearly state that stronger defaults and bounds remain later policy work

## Recovery Note

To activate this work package later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/MODULE_INDEX.md`
4. Read `docs/WORKPACKAGES.md`
5. Read `docs/STATUS.md`
6. Read `docs/session_workpackages/wp18_focus_metadata_artifact_extension.md`
7. Read `services/recording_service/README.md`
8. Read `services/recording_service/STATUS.md`
9. Create the intended branch before any substantive edits
