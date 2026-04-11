# Focus Metadata Producer Wiring

## Purpose

This work package defines the next narrow execution-ready slice after the landed `WP18` artifact-metadata shape clarification.

Its purpose is to move the repository from "artifact-level focus metadata fields are defined and validated" toward "normal snapshot and bounded-recording save flows can emit that artifact-level focus metadata family through explicit producer wiring instead of manual test-only injection."

The narrow goal is to wire one reusable producer into the existing save paths so selected artifact-level focus metadata, including associated ROI metadata when available, can be emitted without silently freezing broader focus-statistics policy or implying broader ROI-management scope.

## Current Context

`WP16` established the shared traceability/logging path, and `WP18` clarified the narrow artifact-level metadata shape above that path.

`WP19` is the already-landed producer-side follow-up: it wires normal save flows so they can emit that selected artifact-level focus/ROI metadata family when the composition enables it.

## Branch

- intended branch: `feature/focus-metadata-producer-wiring`
- activation state: landed narrow follow-up after `WP18`

## Scope

Included:

- add one reusable producer for the artifact-level focus metadata family
- wire that producer into `SnapshotService` and `RecordingService`
- allow bootstrap / subsystem composition to opt into the producer explicitly
- allow emitted fields to include focus method/value fields, aggregation-basis fields when present, and related artifact-level ROI metadata when present
- keep summary fields gated behind an explicit aggregation basis
- add focused tests for snapshot, recording, and bootstrap wiring
- update docs so the producer path is no longer only implied by traceability structure

Excluded:

- new focus methods
- broad statistics-policy finalization
- ROI editor behavior
- ROI explorer behavior
- general ROI-management infrastructure
- UI or offline workstation expansion
- broad reporting redesign
- transport/API work

## Session Goal

Leave the repository with one explicit producer path so normal snapshot and bounded-recording save handling can emit the selected artifact-level focus/ROI metadata family when the subsystem is configured to do so.

## Execution Plan

1. Inspect the current traceability writer path and existing focus services.
2. Check where focus-related artifact metadata is already available and where associated ROI metadata is already available.
3. Add one reusable artifact-level metadata producer for the selected focus/ROI family.
4. Wire it into snapshot and bounded-recording save flows where those fields can be emitted without broadening the package.
5. Expose the wiring through explicit bootstrap configuration instead of hidden defaults.
6. Keep summary fields conditional on an explicit aggregation basis.
7. Keep missing metadata non-fatal and keep ROI metadata out of stable-header identity.
8. Add targeted tests for snapshot, recording, and bootstrap behavior.
9. Update status and PM docs once the producer path is real.

## Validation

Validation emphasis:

- focus metadata may be emitted when available
- associated artifact-level ROI metadata may be emitted when available
- missing focus or ROI metadata remains non-fatal
- ROI metadata does not become stable-header identity
- no ROI-management or ROI-authoring scope is implied by the producer path

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
- `docs/archive/session_workpackages/wp18_focus_metadata_artifact_extension.md` only if activation wording needs clarification

## Expected Commit Shape

1. `feat: wire focus metadata producers into save flows`
2. `test: cover focus metadata producer wiring`
3. `docs: record focus metadata producer wiring`

## Merge Gate

- the slice remains narrow and centered on producer wiring
- save flows can emit the selected artifact-level focus metadata family, including associated ROI metadata when available
- save flows only emit summary fields when an explicit aggregation basis is present
- missing metadata remains non-fatal
- ROI metadata remains artifact-level metadata rather than stable-header identity
- no new ROI-management scope is implied
- tests pass locally
- docs clearly state that stronger defaults and bounds remain later policy work

## Recovery Note

To activate this work package later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/MODULE_INDEX.md`
4. Read `docs/WORKPACKAGES.md`
5. Read `docs/STATUS.md`
6. Read `docs/archive/session_workpackages/wp18_focus_metadata_artifact_extension.md`
7. Read `services/recording_service/README.md`
8. Read `services/recording_service/STATUS.md`
9. Create the intended branch before any substantive edits
