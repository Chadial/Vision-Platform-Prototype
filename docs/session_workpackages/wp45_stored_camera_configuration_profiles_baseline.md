# Stored Camera Configuration Profiles Baseline

## Purpose

This work package defines one bounded post-closure configuration-profile slice above the current host-neutral camera-configuration baseline.

Closure lane:

- Post-Closure Python Baseline / operational readiness with a narrow selective-expansion seam

Slice role:

- configuration-profile baseline

Scope level:

- named profile loading and application over the current `CameraConfiguration` path

Producer / Consumer / Structure impact:

- consumer-facing and structure-facing

Its purpose is to make the current Python baseline easier to reuse on known camera classes by introducing one small profile model centered on named `CameraConfiguration` bundles rather than ad-hoc repeated CLI arguments or SDK-property storage.

The narrow goal is to support camera-class-first configuration profiles, starting with one `default` profile per camera class where justified, without turning the repository into a generic property store, broad preset-management system, or camera-alias framework.

## Branch

- intended branch: `feature/stored-camera-configuration-profiles-baseline`
- activation state: current next

## Scope

Included:

- one repo-local profile storage shape under a bounded config location such as `configs/`
- named configuration profiles keyed first by `camera_class`
- support for a `default` profile per camera class as the baseline entry
- loading and applying those profiles through the current host-neutral configuration/application path
- continued capability-aware validation when a loaded profile is applied
- focused docs for profile purpose, boundaries, and expected usage

Excluded:

- camera alias resolution
- camera-id-specific override layers
- SDK-property-level persistence
- profile editing UI
- last-used profile persistence
- broad profile management commands beyond the smallest useful baseline

What this package does not close:

- a full camera preset-management system
- operator-facing profile discovery or editing workflows
- per-camera override hierarchies
- detached hardware-state persistence

Which policy questions remain open:

- whether camera-id or camera-alias overrides should ever exist above `camera_class`
- whether profile listing/inspection commands are justified later
- whether profile files should remain repository-local only or gain user-local overrides later

## Session Goal

Leave the repository with one bounded configuration-profile baseline that reduces repeated manual configuration for known camera classes while keeping the current host-neutral configuration contract as the single application path.

Target outcome for implementation:

- one small profile file format maps `camera_class` plus `profile_id` to a partial or full `CameraConfiguration` bundle
- the first justified entry point can resolve and apply a `default` profile for a known camera class
- loaded profile data still passes through the current request/configuration validation path instead of bypassing capability-aware checks
- no property-store abstraction, alias system, or profile-management surface is introduced incidentally

## Execution Plan

1. Re-read:
   - `docs/STATUS.md`
   - `docs/WORKPACKAGES.md`
   - `docs/HOST_CONTRACT_BASELINE.md`
   - relevant configuration / controller module docs
2. Identify the smallest current host-neutral application seam for profile loading.
3. Freeze one minimal repository-local profile file shape centered on `camera_class` and `profile_id`.
4. Implement one narrow load-and-apply path with focused validation coverage.
5. Document what profile support means now and what remains deferred.

## Validation

- focused tests for profile file parsing / loading
- focused tests for applying a loaded profile through the current validation path
- at least one bounded CLI or controller-level proof that a named profile can be resolved and applied without bypassing existing configuration rules

## Documentation Updates

- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- `docs/HOST_CONTRACT_BASELINE.md` if the stable-now host surface changes
- relevant module `STATUS.md` files for the touched configuration / control path

## Expected Commit Shape

1. `feat: add stored camera configuration profile baseline`
2. `test: cover stored camera configuration profiles`
3. `docs: record stored camera configuration profile baseline`

## Merge Gate

- the slice remains profile-oriented and `camera_class`-first
- the current host-neutral configuration path remains the single apply path
- no alias system, property-store model, or broad profile-management surface is bundled
- capability-aware validation remains in force for loaded profile data

## Recovery Note

To activate this work package later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/MODULE_INDEX.md`
4. Read `docs/WORKPACKAGES.md`
5. Read `docs/STATUS.md`
6. Create the intended branch before substantive edits
