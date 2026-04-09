# WP81 Geometry Capture Workflow Narrowing

## Purpose

Make the confirmed `Geometry Capture` workflow the second workflow-first package, so snapshot-oriented host-plus-shell use is selected through a concrete product workflow instead of through generic technical leftovers.

## Branch

- intended narrow branch: `feature/wp81-geometry-capture-workflow`
- derive the exact implementation branch only when code work begins

## Closure Lane

- `Usable Camera Subsystem / Pre-Product Baseline`

## Slice Role

- workflow-first narrowing
- snapshot-path usability clarification

## Scope

In scope:

- operator-guided overlapping-image acquisition as the workflow reading
- preview
- settings
- snapshot as the technical capture mode used for that workflow
- save-path clarity
- shell reflection of snapshot outcome and current relevant state
- host-side expectations for geometry-capture use in the current phase

Out of scope:

- broad offline measurement tooling
- broad gallery or browser tooling
- broad host-contract expansion
- recording-workflow redesign

## Session Goal

Leave the repository with one execution-ready package for the current `Geometry Capture` workflow after `WP80`.

## Status

Landed. `WP81` is now complete as one sequence of small sub-packages under the same workflow-first lane rather than as one large snapshot umbrella.

Closure result:

- geometry capture now has one explicit host-plus-shell baseline for operator-guided overlapping-image acquisition through preview, settings context, and snapshot
- the shell and published live status now keep the last snapshot result readable enough for the current phase without widening into gallery or offline lanes
- the remaining queue can now move to `WP82` without leaving geometry-capture save-path, shell reflection, host smoke coverage, or failure-state visibility half-defined

## Sub-Packages

### Landed

#### `WP81.A Snapshot Save-Path Reflection Tightening`

- status: landed
- purpose: make the active or last geometry-capture snapshot target easier to read in shell and published live status
- scope:
  - shell-visible snapshot file/save cues
  - published live-status reflection for the last snapshot result
  - no broader save-browser or artifact-management work

#### `WP81.B Snapshot Run-State Messaging Tightening`

- status: landed
- purpose: make snapshot feedback read as geometry-capture progress rather than as a bare technical side effect
- scope:
  - tighten local and external snapshot success wording
  - keep wording path-aware where useful
  - no broad shell-copy rewrite

#### `WP81.C Host-Control Smoke For Geometry Capture Path`

- status: landed
- purpose: prove one repeatable host-triggered snapshot block against the current companion-shell session baseline
- scope:
  - host requests snapshot
  - shell reflects the resulting snapshot state
  - live status publishes understandable snapshot outcome and save target

#### `WP81.D Snapshot Failure Reflection Narrowing`

- status: landed
- purpose: keep snapshot failures understandable enough in shell and published status without opening a broad error-platform lane
- scope:
  - snapshot save failure
  - save-path failure reflection
  - no broader retry or queue design

### Ordering Note

Execution order used inside `WP81`:

1. `WP81.A Snapshot Save-Path Reflection Tightening`
2. `WP81.B Snapshot Run-State Messaging Tightening`
3. `WP81.C Host-Control Smoke For Geometry Capture Path`
4. `WP81.D Snapshot Failure Reflection Narrowing`

Landed implementation slices so far:

- the shell status prefix now keeps the current or last geometry-capture snapshot file and save directory readable
- the published live shell status now exposes one explicit `snapshot_reflection` block with phase, file name, file stem, save directory, and last error
- local and external snapshot success/failure messages now read through the geometry-capture path and keep the save target visible
- one repeatable host-control smoke block now covers the current host-triggered snapshot path against the wx-shell live-command session bridge

## Execution Plan

1. define the workflow in product terms and technical terms
2. keep geometry capture framed as an operator-guided overlapping-image workflow rather than as generic snapshot work
3. pin the current host-side snapshot expectations
4. pin the current shell reflection and settings expectations
5. capture the smallest implementation seams that would need follow-up
6. keep future implementation slices inside this workflow small and avoid broad snapshot/offline expansion

## Validation

- verify consistency with the confirmed functional-workflow set
- verify the package remains narrower than a broad snapshot or offline lane
- verify the final implementation slice leaves one coherent geometry-capture path with understandable snapshot outcome, save target, and failure reflection

## Documentation Updates

- `docs/WORKPACKAGES.md` when the queue changes
- `docs/STATUS.md` when it becomes active or landed
- `apps/local_shell/STATUS.md` when the shell-visible snapshot baseline changes

## Expected Commit Shape

Implementation, tests, and PM/documentation updates are expected together for the closure slice.

## Merge Gate

- the package clearly follows `WP80`
- the workflow remains inside the current `Hybrid Companion` phase reading
- the package closes with understandable host-plus-shell reflection for geometry-capture snapshot outcome and save target
- no broad measurement or offline scope is reactivated accidentally

## Recovery Note

Resume with:

1. `AGENTS.md`
2. `docs/SESSION_START.md`
3. `docs/MODULE_INDEX.md`
4. `docs/STATUS.md`
5. `docs/WORKPACKAGES.md`
6. this file
