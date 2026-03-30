# Camera Alias And ID Resolution Baseline

## Purpose

This work package defines one bounded camera-selection convenience slice above the current explicit `camera_id` baseline.

Closure lane:

- Post-Closure Python Baseline / operational readiness with a narrow host-facing convenience seam

Slice role:

- camera-selection resolution baseline

Scope level:

- repo-local alias resolution into the current camera-selection path

Producer / Consumer / Structure impact:

- consumer-facing and structure-facing

Its purpose is to reduce repeated long hardware camera identifiers in the current CLI and host-oriented baseline by introducing one small alias-resolution layer that still ends in the same explicit camera-id-driven driver selection path.

The narrow goal is to support bounded repo-local camera aliases for known camera paths without turning the repository into a discovery system, inventory database, or broad device-management surface.

## Branch

- intended branch: `feature/camera-alias-and-id-resolution`
- activation state: landed

## Scope

Included:

- one small repo-local alias storage shape under a bounded config location such as `configs/`
- alias resolution from a stable alias key to one explicit `camera_id`
- continued support for direct explicit `camera_id` input without alias use
- one narrow CLI or controller-level path that can accept an alias and resolve it before driver selection
- focused docs for alias purpose, boundaries, and fallback rules

Excluded:

- hardware discovery or enumeration UI
- alias auto-generation from attached cameras
- camera-class-specific profile loading
- inventory metadata beyond the smallest useful alias mapping
- remote or user-home alias stores

What this package does not close:

- full camera inventory management
- automatic device discovery workflows
- camera-class configuration profiles
- per-camera operational metadata stores

Which policy questions remain open:

- whether aliases should later coexist with camera-class-specific default profiles from `WP45`
- whether user-local or machine-local alias overrides are ever justified
- whether any future alias listing/show command is justified

## Session Goal

Leave the repository with one bounded alias-resolution baseline that makes the tested camera path easier to address while preserving explicit `camera_id` support and the existing driver-selection contract.

Target outcome for implementation:

- one small alias file format maps `camera_alias` to explicit `camera_id`
- the first touched entry path can accept either a direct camera id or a configured alias
- unresolved aliases fail clearly and host-readably
- no discovery, inventory, or profile-management scope is introduced incidentally

Landed outcome:

- the camera CLI now accepts `--camera-alias` in addition to direct `--camera-id`
- repo-local alias resolution lives in `configs/camera_aliases.json`
- the current tested example alias `tested_camera` resolves to `DEV_1AB22C046D81`
- alias resolution happens before the unchanged `camera_service.initialize(camera_id=...)` path
- unknown aliases and conflicting `--camera-id` plus `--camera-alias` input now return one bounded `camera_selection_error` envelope
- March 30, 2026 hardware validation succeeded through the alias path for `status` and `snapshot(.bmp)` on the attached tested camera

## Execution Plan

1. Re-read:
   - `docs/STATUS.md`
   - `docs/WORKPACKAGES.md`
   - `docs/HOST_CONTRACT_BASELINE.md`
   - relevant CLI / control module docs
2. Identify the smallest current camera-selection seam for alias resolution.
3. Freeze one minimal repository-local alias file shape.
4. Implement one narrow resolve-and-pass-through path with focused validation coverage.
5. Document alias purpose, direct-id fallback, and what remains deferred.

## Validation

- focused tests for alias file parsing / loading
- focused tests for alias resolution success and unknown-alias failures
- at least one bounded CLI or controller-level proof that a resolved alias reaches the unchanged camera-selection path

## Documentation Updates

- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- `docs/HOST_CONTRACT_BASELINE.md` if the stable-now host surface changes
- relevant module `STATUS.md` files for the touched CLI / control path

## Expected Commit Shape

1. `feat: add camera alias resolution baseline`
2. `test: cover camera alias resolution`
3. `docs: record camera alias resolution baseline`

## Merge Gate

- the slice remains alias-oriented and bounded
- direct explicit `camera_id` use remains supported
- no discovery system, inventory model, or profile-management surface is bundled
- the existing camera-selection path remains the single driver-selection path

## Recovery Note

To activate this work package later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/MODULE_INDEX.md`
4. Read `docs/WORKPACKAGES.md`
5. Read `docs/STATUS.md`
6. Create the intended branch before substantive edits
