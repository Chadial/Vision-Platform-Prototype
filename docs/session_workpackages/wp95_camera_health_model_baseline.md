# WP95 Camera Health Model Baseline

## Purpose

This work package defines the internal minimal `CameraHealth` derivation slice that follows the explicit surface-contract clarification from `WP94`.

Closure lane:

- Usable Camera Subsystem / Pre-Product Baseline

Slice role:

- internal derivation-model baseline

Scope level:

- current internal `CameraHealth` model only

Its purpose is to give the repository one explicit internal health model that can later support:

- `GetHealth` on the surface
- later runtime health events
- later orchestrator, logging, and safety consumers

without pulling those later consumers into the repo now.

This package should be read as:

- internal health-model clarification
- derivation-source narrowing
- semantic tightening beyond raw `last_error` and `can_*`

It should not be read as:

- a new transport contract
- a supervisor-policy package
- a global safety model
- an event-system package

## Branch

- current branch carrying the documentation sequence: `docs/camera-embedding-analysis`
- intended narrow execution branch if split later: `docs/wp95-camera-health-model-baseline`
- activation state: active

## Scope

Included:

- define one minimal internal `CameraHealth` model for the current repo phase
- identify which existing repo signals can feed that model
- define the minimal field set and its intended meanings
- define the first derivation boundaries between:
  - current state
  - current degradation
  - current fault
  - current capability impairment
- keep the model explicitly subordinate to the already documented `WP94` surface contract

Stable-now field target:

- `availability`
- `readiness`
- `degraded`
- `faulted`
- `last_error`
- `capabilities_available`
- optional only if cleanly derivable now: `recording_impaired`

Excluded:

- redesign of `GetHealth`
- transport, DTO, or API redesign
- incident history or audit-feed modeling
- runtime event delivery
- safety-supervisor policy

What this package does not close:

- full fault taxonomy
- full lifecycle-state model
- runtime-event semantics
- cross-module health correlation
- global safety decision logic

Minimal modeling rules:

- `faulted` = the current state prevents or breaks an essential function now
- `degraded` = the current state still permits function, but with impairment, reduced trust, or bounded risk
- `last_error` is only a context field, not the truth-anchor of health
- audit signals may influence health derivation, but `CameraHealth` is not an audit feed

## Session Goal

Leave the repository with one explicit, small internal `CameraHealth` model description that explains what the current health view is derived from, what it means, and what it intentionally does not model yet.

Expected concrete outputs:

- one active `WP95` session work package
- one repo-near note update that defines the internal `CameraHealth` baseline separately from the `WP94` surface contract
- one explicit stable-now / deferred-later split for health derivation

## Status

- active as the direct follow-up after the implemented `WP94` surface-contract slice

## Sub-Packages

### WP95.A Health Field Baseline

- status: planned
- purpose: define the minimal internal `CameraHealth` field set and semantic meaning

### WP95.B Derivation Source Mapping

- status: planned
- purpose: map current status, warning, and recording/capability signals into the internal health model

### WP95.C Deferred Fault And Safety Boundary

- status: planned
- purpose: keep the line explicit between this internal model and later safety, orchestrator, and runtime-event work

## Open Questions

- Which current repo signals are strong enough to derive `degraded` versus only a warning or note?
- Which current recording or capability failures should be treated as current health impairment versus historical incident only?
- How much of the current hardware-audit classification can be reused as derivation input without turning the health model into an audit mirror?

## Learned Constraints

- `WP95` must remain the internal derivation model, not a second surface-contract package.
- `CameraHealth` must not become a synonym for safety policy.
- the model must stay small enough to be explainable from current repo signals rather than aspirational architecture.
- runtime-event needs should inform naming, but must not drive the model into event-first design.
- `degraded` and `faulted` must be kept semantically separate from the start or the model will immediately blur.
- `last_error` may support explanation, but it must not replace state derivation.
- audit- and incident-related inputs must remain inputs only, not mirrored output channels.

## Execution Plan

1. Re-read:
   - `docs/STATUS.md`
   - `docs/WORKPACKAGES.md`
   - `docs/BiggerPictureNotes/camera_integration_surface_v0.1.md`
   - `docs/session_workpackages/wp94_health_and_capabilities_surface_contract.md`
2. Inspect the current status, warning, recording, capability, and audit-adjacent signals named in `WP94`.
3. Define one minimal internal `CameraHealth` field set and its meanings.
4. Record explicitly how `degraded` and `faulted` differ and how `last_error` remains contextual only.
5. Record which current repo signals feed each field and which semantics remain deferred.
6. Keep audit and incident traces as derivation inputs only, not as modeled output streams.
7. Update the central PM docs if the active-next wording changes later.

## Validation

- documentation consistency review against the current status, capability, recording, and audit-related repo structures
- confirm the package stays internal-model-focused rather than redoing `WP94`
- confirm the package does not absorb safety-policy or runtime-event design
- confirm the stable-now field set remains intentionally small
- confirm `degraded` and `faulted` are defined with non-overlapping meaning
- confirm audit remains derivation input only

## Documentation Updates

- `docs/BiggerPictureNotes/camera_integration_surface_v0.1.md` or a directly adjacent repo-near camera note if that becomes the clearest home
- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- this work-package file while active

## Expected Commit Shape

1. `docs: add wp95 camera health model baseline`
2. `docs: define internal camera health derivation baseline`

## Merge Gate

- `WP95` is visible from `docs/WORKPACKAGES.md` as the queued follow-up after `WP94`
- the note explicitly preserves `WP94 = surface contract` and `WP95 = internal derivation model`
- the package defines one minimal internal health model and its derivation sources
- the package keeps the stable-now field set intentionally small
- the package keeps `last_error` contextual and does not turn `CameraHealth` into an audit mirror
- safety-policy, transport, and runtime-event design remain deferred

## Recovery Note

To resume this package later:

1. read `docs/STATUS.md`
2. read `docs/WORKPACKAGES.md`
3. read `docs/session_workpackages/wp94_health_and_capabilities_surface_contract.md`
4. read `docs/BiggerPictureNotes/camera_integration_surface_v0.1.md`
5. continue only with the internal `CameraHealth` derivation model
