# WP94 Health And Capabilities Surface Contract

## Purpose

This work package defines the first explicit follow-up slice after the `WP93` surface-mapping baseline.

Closure lane:

- Usable Camera Subsystem / Pre-Product Baseline

Slice role:

- surface-contract clarification baseline

Scope level:

- current `GetHealth` and `GetCapabilities` contract only

Its purpose is to close the first two explicit surface gaps that `WP93` left open:

- `GetHealth`
- `GetCapabilities`

This package should be read as:

- surface-contract sharpening
- explicit result-meaning clarification
- current source-of-truth narrowing
- `WP94 = surface contract`

It should not be read as:

- the full `CameraHealth` model
- `WP95 = internal derivation model`
- supervisor or safety policy
- transport expansion
- event-system design

## Branch

- current branch carrying the documentation sequence: `docs/camera-embedding-analysis`
- intended narrow execution branch if split later: `docs/wp94-health-capabilities-surface-contract`
- activation state: active

## Scope

Included:

- define the minimal surface-facing meaning of `GetHealth`
- define the minimal surface-facing meaning of `GetCapabilities`
- identify the current repo signals and structures those two calls can legitimately build on
- distinguish:
  - surface-facing result meaning
  - adapter/result-envelope form
- record the smallest stable-now field sets for both calls
- distinguish for capabilities between:
  - `supported`
  - `currently available`
  - `currently enabled`
- state what remains deferred to `WP95` and later

Excluded:

- full `CameraHealth` derivation design
- new runtime command implementations
- end-to-end transport or API redesign
- event-bus or subscription semantics
- global safety classification

What this package does not close:

- the internal `CameraHealth` model
- runtime event semantics
- artifact/logging policy beyond what is needed to keep the two calls well-bounded
- orchestrator-facing lifecycle language

Minimal interpretation rule:

- `GetHealth` returns one compact current readable health state
- it does not return an incident feed, audit history, or warning/event stream

## Session Goal

Leave the repository with one explicit, repo-facing contract note for `GetHealth` and `GetCapabilities` so later health-model and event work starts from an agreed surface meaning instead of inference.

Expected concrete outputs:

- one active `WP94` session work package
- an updated `docs/BiggerPictureNotes/camera_integration_surface_v0.1.md` with explicit `GetHealth` / `GetCapabilities` contract framing
- clear stable-now vs deferred-later wording for both calls

## Status

- completed as the first code-backed surface-contract slice after `WP93`; follow-up now moves to `WP95`

## Sub-Packages

### WP94.A GetHealth Surface Meaning

- status: completed
- purpose: define what `GetHealth` means on the v0.1 surface before the internal health model is expanded

### WP94.B GetCapabilities Surface Meaning

- status: completed
- purpose: define what `GetCapabilities` means on the v0.1 surface before broader capability modeling or richer profiles are introduced

### WP94.C Deferred-Boundary Marking

- status: completed
- purpose: keep the line explicit between this contract slice and the later `CameraHealth` and runtime-event slices

## Open Questions

- Which currently available capability signals are stable enough to expose as minimal surface fields without freezing too much profile or probe detail?
- Which current warning or failure signals should appear in `GetHealth` now, and which should stay deferred to the later `CameraHealth` model?
- How should the current status-driven and audit-driven warning sources be referenced without turning `GetHealth` into a log or incident feed?
- Which currently known capability fields can already be grouped cleanly into `supported`, `currently available`, and `currently enabled` without over-freezing the model?

## Learned Constraints

- `GetHealth` must not collapse into a renamed `GetStatus`.
- `GetHealth` must not absorb audit history, failure reflection history, or non-current warning streams.
- `GetCapabilities` must not collapse into raw internal probe output.
- `GetCapabilities` must not mix `supported`, `currently available`, and `currently enabled` into one undifferentiated capability bag.
- this package stays useful only if it defines surface meaning first and leaves the internal health model to `WP95`.
- current CLI, API, and companion result forms are still useful examples, but they must not define the contract by accident.

## Execution Plan

1. Re-read:
   - `docs/STATUS.md`
   - `docs/WORKPACKAGES.md`
   - `docs/BiggerPictureNotes/camera_integration_surface_v0.1.md`
   - `docs/BiggerPictureNotes/camera_subsystem_role_and_boundaries.md`
   - `docs/session_workpackages/wp93_camera_integration_surface_v0_1_contract_mapping.md`
2. Inspect the current status, capability, audit, and payload seams relevant to health and capabilities.
3. Update `camera_integration_surface_v0.1.md` with:
   - one explicit `GetHealth` subsection
   - one explicit `GetCapabilities` subsection
   - minimal stable-now field sets
   - one explicit rule that `GetHealth` is current-state only, not incident-feed semantics
   - one explicit capability reading split for `supported`, `currently available`, and `currently enabled`
   - deferred-later notes tied to `WP95`
4. Update the central PM docs if the active-next wording changes further.

## Validation

- documentation consistency review against the current repo structures named in `WP93`
- confirm the slice remains contract-focused and does not absorb the later `CameraHealth` model
- confirm `GetHealth` and `GetCapabilities` are described as surface meanings, not transport envelopes
- confirm `GetHealth` is framed as compact current state, not as audit/feed output
- confirm the capability wording preserves the `supported` / `currently available` / `currently enabled` split

## Documentation Updates

- `docs/BiggerPictureNotes/camera_integration_surface_v0.1.md`
- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- this work-package file while active

## Expected Commit Shape

1. `docs: activate wp94 health and capabilities surface contract`
2. `docs: sharpen gethealth and getcapabilities surface meaning`

## Merge Gate

- `WP94` is visible from `docs/WORKPACKAGES.md` as the completed code-backed surface-contract slice before `WP95`
- `WP93` is no longer described as the active next slice
- `camera_integration_surface_v0.1.md` contains explicit stable-now contract language for `GetHealth` and `GetCapabilities`
- the note explicitly states `WP94 = surface contract` and keeps `WP95 = internal derivation model`
- the package keeps `CameraHealth` modeling deferred to `WP95`
- no transport, event-bus, or supervisor-policy redesign is bundled into the slice

## Outcome

- `CommandController` now exposes `get_health()` and `get_capabilities()` as explicit narrow surface calls above the existing core
- the current repo now has bounded internal models for:
  - `CameraHealth`
  - `CameraCapabilities`
  - `CapabilityState`
- the API-service layer now exposes adapter-facing payload mappers for the new health and capabilities surfaces
- focused controller and API-service tests now cover the implemented `WP94` slice

## Recovery Note

To resume this package later:

1. read `docs/STATUS.md`
2. read `docs/WORKPACKAGES.md`
3. read `docs/session_workpackages/wp93_camera_integration_surface_v0_1_contract_mapping.md`
4. read `docs/BiggerPictureNotes/camera_integration_surface_v0.1.md`
5. continue with `GetHealth` / `GetCapabilities` contract sharpening only
