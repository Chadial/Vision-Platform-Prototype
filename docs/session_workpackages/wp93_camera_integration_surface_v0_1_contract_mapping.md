# WP93 Camera Integration Surface v0.1 Contract Mapping

## Purpose

This work package defines the first explicit repository-facing integration-fore-stage slice for the current usable-camera-subsystem phase.

Closure lane:

- Usable Camera Subsystem / Pre-Product Baseline

Slice role:

- contract clarification and boundary mapping baseline

Scope level:

- current camera command/state/result/payload baseline only

Its purpose is to turn the already documented `Camera Integration Surface v0.1` idea into one execution-ready repository slice that:

- does not rebuild the core
- does not replace the current host/status/payload paths
- does make the current surface legible as one explicit integration contract

This package should be read as:

- current surface clarification
- current source-of-truth mapping
- current boundary tightening

It should not be read as:

- runtime redesign
- transport expansion
- event-bus preparation
- shell-bridge replacement

## Branch

- current branch carrying the preparation docs: `docs/camera-embedding-analysis`
- intended narrow execution branch if split later: `docs/wp93-camera-integration-surface-contract-mapping`
- activation state: active

## Scope

Included:

- sharpen `docs/BiggerPictureNotes/camera_integration_surface_v0.1.md` into a repo-facing reference
- add one explicit mapping table for:
  - current commands
  - current state/status surfaces
  - current payload/result shapes
  - current artifact references
- add one explicit `Action` column per mapped row:
  - `keep as-is`
  - `rename in docs`
  - `narrow`
  - `defer`
  - `promote to surface later`
- classify each mapped element as:
  - `Surface`
  - `Adapter`
  - `Companion-only`
  - `Transition-only`
- record the current source of truth for each mapped element
- distinguish explicitly between:
  - `surface-facing result meaning`
  - adapter- or transport-near result form
- mark the smallest explicit gaps that must remain for `GetHealth`, `GetCapabilities`, and the first event family

Excluded:

- adding new runtime commands
- defining a final DTO family
- changing the shell bridge
- adding event delivery infrastructure
- implementing the later `CameraHealth` model
- broad code refactors in `src/`

What this package does not close:

- full `GetHealth` / `GetCapabilities` contract design
- the `CameraHealth` derivation model
- runtime-event semantics beyond naming and producer identification
- final orchestrator/logging/safety boundaries

## Session Goal

Leave the repository with one active, execution-ready work package and one sharper v0.1 surface reference that together make the current camera integration fore-stage concrete enough for direct follow-up work.

Expected concrete outputs:

- an updated `docs/BiggerPictureNotes/camera_integration_surface_v0.1.md`
- one explicit mapping table from repo reality to surface categories plus action guidance
- one explicit `Surface vs Adapter vs Companion-only` boundary block
- one explicit distinction between `Companion-only` and `Transition-only`
- explicit carry-forward gaps for `WP94`, `WP95`, and `WP96`

## Status

- completed as the contract-mapping gatekeeper slice; follow-up now moves to `WP94`

## Sub-Packages

### WP93.A Surface Inventory Baseline

- status: completed
- purpose: inventory the current command, status, payload, and artifact-facing repo surfaces

### WP93.B Surface Category Mapping

- status: completed
- purpose: map those inventory items into `Surface`, `Adapter`, `Companion-only`, and `Transition-only`, with one explicit action decision per row

### WP93.C Source-Of-Truth And Gap Marking

- status: completed
- purpose: mark which current classes/services/files own each mapped element and which minimal gaps remain deferred to the next slices

## Open Questions

- Which existing payload families should be treated as the clearest source-of-truth layer for surface-facing result meanings: controller result types, `api_service` payload mappers, or the extracted companion contract seam?
- Which current shell-published status subsets should be called out explicitly as `Companion-only` instead of being left implicit?
- How far should artifact references be mapped in `WP93` before `WP96`-adjacent event and artifact follow-up becomes the cleaner home?

## Learned Constraints

- The current repo already has multiple host-facing and shell-facing contract fragments, so `WP93` must map them instead of pretending there is one pristine contract source already.
- The work package stays useful only if it produces explicit repo artifacts, not another essay-level note.
- The shell bridge must remain readable as a bounded current mechanism without becoming the primary integration surface.
- `Companion-only` must not be collapsed into `Transition-only`: a legitimate local consumer view is not the same thing as a historical or non-target mechanism.
- current payloads and result envelopes are useful source material, but they must not silently define the surface meaning on their own.

## Execution Plan

1. Re-read:
   - `docs/STATUS.md`
   - `docs/WORKPACKAGES.md`
   - `docs/BiggerPictureNotes/camera_integration_surface_v0.1.md`
   - `docs/BiggerPictureNotes/camera_subsystem_role_and_boundaries.md`
2. Inspect the current controller, API payload, status-model, and companion-contract surfaces.
3. Update `camera_integration_surface_v0.1.md` with:
   - one mapping table
   - one `Action` column that makes the table directive, not merely descriptive
   - one `Surface / Adapter / Companion-only / Transition-only` boundary section
   - one explicit distinction between `surface-facing result meaning` and adapter/result-envelope form
   - one explicit source-of-truth note
4. Record in the same note which narrow gaps remain for:
   - `GetHealth`
   - `GetCapabilities`
   - `CameraHealth`
   - the minimal runtime-event family
5. Update the central PM docs if the active-next wording or recovery guidance changes.

## Validation

- documentation consistency review against the current repo structure
- path/reference sanity check for all named modules, classes, and notes
- confirm that the package remains documentation-only and does not smuggle in end-architecture commitments

## Documentation Updates

- `docs/BiggerPictureNotes/camera_integration_surface_v0.1.md`
- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- this work-package file while active

## Expected Commit Shape

1. `docs: activate wp93 camera integration surface mapping slice`
2. `docs: sharpen camera integration surface v0.1 mapping`

## Merge Gate

- `wp93` is visible from `docs/WORKPACKAGES.md` as the completed gatekeeper slice before `WP94`
- the active work-package file is present under `docs/session_workpackages/`
- `camera_integration_surface_v0.1.md` contains explicit repo-facing mapping output instead of prose-only framing
- the mapping table includes `category`, `source of truth`, and `action`
- the boundary block distinguishes `Companion-only` from `Transition-only` explicitly
- deferred items for `GetHealth`, `GetCapabilities`, `CameraHealth`, and runtime events are explicit and narrow
- no transport, shell-runtime, or event-bus redesign is bundled into the slice

## Outcome

- `camera_integration_surface_v0.1.md` now contains a repo-facing mapping table with `category`, `source of truth`, and `action`
- the note now distinguishes `surface-facing result meaning` from adapter or envelope form
- the note now separates `Companion-only` from `Transition-only`
- `WP93` therefore closes the mapping and boundary-clarification gate and hands off the first explicit surface gaps to `WP94`

## Recovery Note

To resume this package later:

1. read `docs/STATUS.md`
2. read `docs/WORKPACKAGES.md`
3. read `docs/BiggerPictureNotes/camera_integration_surface_v0.1.md`
4. read `docs/BiggerPictureNotes/camera_subsystem_role_and_boundaries.md`
5. continue only with mapping and boundary clarification, not runtime redesign
