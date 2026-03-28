# Camera CLI

## Purpose

This work package reserves the next focused branch for a camera-oriented CLI surface that can exercise the existing platform services without depending on the OpenCV operator preview path.

It exists early so the next branch can start from a named scope instead of improvising a second active track while the current OpenCV UI block is still being finished.

## Branch

- active preparation branch: `feature/camera-cli`
- activation state: active for CLI workpackage preparation and scope definition; implementation can now continue on this branch because the OpenCV operator MVP baseline has been merged to `main`

## Scope

Included:

- define one coherent CLI surface for camera-oriented prototype operations
- favor service/controller-backed commands over ad-hoc script behavior
- keep CLI concerns separate from the OpenCV operator preview surface
- expose explicit arguments for camera selection, configuration, save paths, and bounded operations where that can be done on top of existing services
- clarify which commands are simulator-safe versus hardware-oriented

Excluded:

- finishing the current OpenCV operator block
- broad host/API work
- desktop UI or browser UI work
- unrelated refactors outside the CLI-facing app/demo surface

## Session Goal

Turn the already reserved CLI idea into a concrete, execution-ready work package with one clear command surface, one capability list, and one documented MVP slice for the next implementation steps.

The first completed implementation slice on this branch should establish one clear entry command and argument structure for the most important camera operations instead of leaving behavior scattered across multiple prototype scripts.

## Precondition

This precondition is now satisfied.

Reason:

- the user explicitly wants one active focus at a time
- the OpenCV operator MVP baseline has now been merged and documented
- repository context stays clearer when CLI work starts from that documented baseline instead of overlapping with unfinished preview work

## CLI Role

The CLI is not meant to reproduce local preview-only controls.

It should expose camera-facing, storage-facing, capture-facing, ROI-facing, and analysis-facing actions that already make sense as service/controller capabilities.

It should not treat viewport-only concerns such as zoom, pan, or fit-to-window as first-class CLI responsibilities unless a later host use case requires that explicitly.

## Recommended Command Shape

Prefer one coherent root command over many unrelated demo scripts.

Recommended direction:

- one root command for the camera prototype surface
- a small set of explicit subcommands grouped by capability

Example shape:

```text
camera-cli capture snapshot
camera-cli capture start-recording
camera-cli capture stop-recording
camera-cli camera apply
camera-cli storage set-directory
camera-cli roi set-rectangle
camera-cli roi set-ellipse
camera-cli roi clear
camera-cli analysis set-focus-method
camera-cli status show
```

The exact executable/module name can still be chosen later, but the work package should keep the subcommand grouping stable even if the final launch wrapper changes.

## Shared Capability Groups

The CLI capability list should align with the operator grouping already documented in `docs/ui/operator_surface_template.md`.

Initial shared groups:

- `Capture`
- `Camera`
- `Storage`
- `ROI`
- `Analysis`

Explicitly exclude from the initial CLI MVP:

- `View`
  - zoom
  - pan
  - fit-to-window
  - crosshair display position
  - other viewport-local concerns

Reason:

- those are local preview-surface behaviors, not host-control fundamentals

## Initial CLI MVP

The first CLI MVP should stay deliberately small.

Recommended initial commands:

- `capture snapshot`
  - explicit save directory
  - file stem / extension where already supported
- `capture start-recording`
  - frame limit and/or duration
- `capture stop-recording`
- `camera apply`
  - camera id
  - exposure
  - gain if already meaningful on the selected path
  - pixel format
  - ROI geometry fields if they already map cleanly
- `storage set-directory`
  - base directory
  - append vs. new subfolder behavior
- `roi set-rectangle`
- `roi set-ellipse`
- `roi clear`
- `status show`

Good MVP rule:

- if a capability already exists through service/controller requests, it is a good CLI candidate
- if a capability is only a local OpenCV window behavior, it is not part of the initial CLI MVP

## Command/Service Mapping

The branch should make the mapping explicit before implementing flags.

Target examples:

- `camera apply`
  - maps to configuration models / controller configuration path
- `storage set-directory`
  - maps to save-directory request path
- `capture snapshot`
  - maps to snapshot request path
- `capture start-recording`
  - maps to start-recording request path
- `capture stop-recording`
  - maps to stop-recording request path
- `roi set-*`
  - maps to ROI model/state path
- `status show`
  - maps to status/controller summary path

## Simulator vs. Hardware

The CLI should make the execution context explicit.

Recommended baseline:

- simulator-safe by default where practical
- hardware path enabled explicitly through camera selection or a source-mode argument

Document clearly for each subcommand:

- simulator-supported
- hardware-supported
- hardware-only

## Execution Plan

1. Re-check `docs/STATUS.md`, `docs/ROADMAP.md`, and `docs/GlobalRoadmap.md` before implementation starts on this branch.
2. Re-read `docs/git_strategy.md` and keep CLI scope separate from unrelated UI work.
3. Inventory the current prototype commands under `src/vision_platform/apps/opencv_prototype` and identify overlap, gaps, and inconsistent arguments.
4. Decide whether the CLI should wrap:
   - existing demo entry points directly
   - the command-controller path
   - or a thin new app-layer command surface above the existing services
5. Define one consistent argument model for:
   - camera id
   - exposure/gain/pixel format
   - save directory
   - frame limits or durations where relevant
   - simulator versus hardware selection where needed
6. Derive the CLI capability list from the shared operator grouping rather than from ad-hoc script flags.
   - `Capture`: snapshot, recording start/stop, bounded capture/recording arguments
   - `Camera`: exposure, gain, pixel format, geometry, camera selection
   - `Storage`: save directory, append/new-subfolder behavior, naming/format options
   - `Analysis`: focus-method or similar analysis configuration where already backed by services
   - `ROI`: explicit set/clear ROI commands where they map cleanly to existing models
   - exclude `View` from the initial CLI baseline unless a specific host use case requires it, because zoom/pan/fit are usually local preview concerns
7. Freeze one recommended command shape and subcommand tree before implementing flags.
8. Implement the first coherent CLI slice with targeted tests.
9. Update module and repository docs once the CLI scope is real rather than only planned.

## Initial Deliverables

The branch should leave behind at least:

- one documented root command shape
- one explicit capability matrix
- one small implemented CLI baseline or, if implementation is deferred, one implementation-ready argument contract
- targeted tests for the implemented command slice
- updated docs that explain what the CLI is for and what it still does not cover

## Validation

- use targeted CLI and bootstrap tests for the touched entry points
- prefer simulator-backed validation first
- only add hardware-backed CLI checks once the hardware path being exercised is explicit and reproducible

Suggested first validation block once implementation starts:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_command_controller tests.test_bootstrap
```

## Documentation Updates

Before this work package is considered complete, update:

- the relevant app/module `STATUS.md`
- the relevant app/module `ROADMAP.md`
- `docs/STATUS.md`
- `docs/SESSION_START.md` if the preferred next recovery link changes

## Expected Commit Shape

1. `feat: add camera cli baseline command surface`
2. `test: add camera cli coverage`
3. `docs: update camera cli workpackage status`

## Merge Gate

- CLI scope stays separate from OpenCV operator preview work
- touched tests pass locally
- docs explain the intended operator/developer role of the CLI clearly
- no unrelated UI churn is bundled into the branch

## Recovery Note

To activate this planned work later:

1. Read `Agents.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/MODULE_INDEX.md`
4. Read `docs/STATUS.md`
5. Read `docs/ROADMAP.md`
6. Read `docs/git_strategy.md`
7. Confirm the OpenCV operator block is paused, merged, or intentionally left at a stable checkpoint
8. Create the correct branch before any substantive CLI edits
