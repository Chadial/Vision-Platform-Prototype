# WP96 Runtime Event Family Baseline

## Purpose

This work package defines the minimal runtime-event slice that follows the surface clarification of `WP94` and the internal health-model baseline of `WP95`.

Closure lane:

- Usable Camera Subsystem / Pre-Product Baseline

Slice role:

- runtime-event semantics baseline

Scope level:

- current minimal event-family definition only

Its purpose is to give the repository one explicit minimal runtime-event reading for the camera subsystem so later integration does not continue to infer events indirectly from:

- traceability files
- result envelopes
- published status snapshots
- audit output

This package should be read as:

- event-category clarification
- producer-place identification
- minimal event-shape baseline

It should not be read as:

- an event-bus package
- transport design
- subscription or delivery semantics
- a full lifecycle-event model

## Branch

- current branch carrying the documentation sequence: `docs/camera-embedding-analysis`
- intended narrow execution branch if split later: `docs/wp96-runtime-event-family-baseline`
- activation state: queued

## Scope

Included:

- define the minimal runtime-event family for the current camera integration fore-stage
- identify the existing producer places in the repo that correspond to those events
- distinguish clearly between:
  - event
  - state
  - artifact traceability
  - result/envelope form
  - audit output
- define one minimal event-shape reading that later adapters or transports could carry
- tie health-related events back to the internal `CameraHealth` model from `WP95`

Excluded:

- event transport
- event bus
- delivery guarantees
- subscriber registration
- full lifecycle language
- replay or event-history design

What this package does not close:

- transport-neutral event contract freeze
- full run/session event model
- orchestrator notification semantics
- logging or audit policy
- complete event taxonomy for every subsystem action

## Session Goal

Leave the repository with one explicit minimal camera runtime-event family that is small, first-class, and clearly separated from state snapshots, artifact traces, and audit records.

Expected concrete outputs:

- one active-ready `WP96` session work package
- one repo-near note update that names the minimal event family
- one explicit producer-place mapping and minimal event-shape reading

## Status

- completed as the first code-backed runtime-event semantics baseline after `WP95`

## Sub-Packages

### WP96.A Event Family Naming

- status: completed
- purpose: define the smallest first-class runtime-event family for the current repo phase

### WP96.B Producer Place Mapping

- status: completed
- purpose: identify where the current repo already emits or semantically implies those events

### WP96.C Event Boundary Clarification

- status: completed
- purpose: keep the line explicit between runtime events, state, traceability, and audit output

## Open Questions

- Which current command flows should become first-class runtime events immediately, and which should remain implicit until later?
- How should `CameraHealthChanged` be worded so it depends on the `WP95` health model rather than on raw error text?
- Which current traceability or audit emissions should be referenced only as producer evidence and not as event definitions?

## Learned Constraints

- runtime events must not be redefined as CSV rows or status snapshots.
- this package must stay semantic and structural, not transport-oriented.
- health-related events should depend on the internal health model rather than on ad-hoc warning strings.
- the package stays useful only if the event family remains intentionally small.

## Execution Plan

1. Re-read:
   - `docs/STATUS.md`
   - `docs/WORKPACKAGES.md`
   - `docs/BiggerPictureNotes/camera_integration_surface_v0.1.md`
   - `docs/session_workpackages/wp94_health_and_capabilities_surface_contract.md`
   - `docs/session_workpackages/wp95_camera_health_model_baseline.md`
2. Inspect the current command/result, traceability, recording-log, shell-reflection, and audit-related outputs that imply event-like semantics.
3. Define one minimal event family and one minimal event-shape reading.
4. Record which current repo places produce or semantically imply those events.
5. Keep all transport, delivery, and subscription semantics deferred.

## Validation

- documentation consistency review against the current repo paths named in `WP93` through `WP95`
- confirm the package stays event-semantic rather than transport-semantic
- confirm state, artifact traceability, and audit output remain clearly separated from runtime events

## Documentation Updates

- `docs/BiggerPictureNotes/camera_integration_surface_v0.1.md` or a directly adjacent repo-near camera note if that becomes the clearest home
- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- this work-package file while active

## Expected Commit Shape

1. `docs: add wp96 runtime event family baseline`
2. `docs: define minimal camera runtime event family`

## Merge Gate

- `WP96` is visible from `docs/WORKPACKAGES.md` as the completed runtime-event baseline after `WP95`
- the package keeps the event family intentionally small
- the package distinguishes runtime events from status, artifact traceability, result envelopes, and audit output
- event transport, bus, and delivery semantics remain deferred

## Outcome

- the repo now has first-class runtime-event types in `vision_platform.models.camera_runtime_event`
- the repo now has narrow event builders in `vision_platform.services.camera_runtime_event_service` for:
  - `CameraConfigurationApplied`
  - `CameraSnapshotSaved`
  - `CameraRecordingStarted`
  - `CameraRecordingStopped`
  - `CameraFaulted`
  - `CameraHealthChanged`
- the event slice stays transport-free and explicitly separate from traceability, status snapshots, and audit output

## Recovery Note

To resume this package later:

1. read `docs/STATUS.md`
2. read `docs/WORKPACKAGES.md`
3. read `docs/session_workpackages/wp94_health_and_capabilities_surface_contract.md`
4. read `docs/session_workpackages/wp95_camera_health_model_baseline.md`
5. read `docs/BiggerPictureNotes/camera_integration_surface_v0.1.md`
6. continue only with the minimal runtime-event family
