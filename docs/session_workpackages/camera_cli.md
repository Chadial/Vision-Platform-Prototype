# Camera CLI

## Purpose

This work package reserves the next focused branch for a camera-oriented CLI surface that can exercise the existing platform services without depending on the OpenCV operator preview path.

It exists early so the next branch can start from a named scope instead of improvising a second active track while the current OpenCV UI block is still being finished.

## Branch

- intended future branch: `feature/camera-cli`
- activation state: planned only, not active while `feature/opencv-ui-operator-block` remains the current work package

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

Create a focused CLI work package that can become the next coherent branch after the OpenCV operator block reaches a stable stopping point.

The first completed slice on that future branch should establish one clear entry command and argument structure for the most important camera operations instead of leaving behavior scattered across multiple prototype scripts.

## Precondition

Do not activate this work package until the current OpenCV UI block has reached a deliberate stop point.

Reason:

- the user explicitly wants one active focus at a time
- the current branch still has unfinished OpenCV preview work
- repository context stays clearer when CLI work starts as a fresh branch with a clean handoff

## Execution Plan

1. Re-check `docs/STATUS.md`, `docs/ROADMAP.md`, and `docs/GlobalRoadmap.md` before activating this package.
2. Re-read `docs/git_strategy.md` and confirm the current branch should change before starting CLI work.
3. Create `feature/camera-cli` from the correct stable base once the OpenCV branch is paused or merged.
4. Inventory the current prototype commands under `src/vision_platform/apps/opencv_prototype` and identify overlap, gaps, and inconsistent arguments.
5. Decide whether the CLI should wrap:
   - existing demo entry points directly
   - the command-controller path
   - or a thin new app-layer command surface above the existing services
6. Define one consistent argument model for:
   - camera id
   - exposure/gain/pixel format
   - save directory
   - frame limits or durations where relevant
   - simulator versus hardware selection where needed
7. Implement the first coherent CLI slice with targeted tests.
8. Update module and repository docs once the CLI scope is real rather than only planned.

## Validation

- use targeted CLI and bootstrap tests for the touched entry points
- prefer simulator-backed validation first
- only add hardware-backed CLI checks once the hardware path being exercised is explicit and reproducible

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
