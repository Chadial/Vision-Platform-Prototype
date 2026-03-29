# Additional Frontends

## Purpose

This work package captures the later preparation of additional frontend paths beyond the current OpenCV prototype.

Its purpose is to keep desktop and future web-capable directions visible without letting them outrun the core command, storage, ROI, focus, and analysis contracts.

## Branch

- intended branch: `feature/additional-frontends`
- activation state: planned for later, after the current core and adapter boundaries are more stable

## Scope

Included:

- identify the next non-OpenCV frontend preparation slice
- keep frontend work above the shared host-neutral control and analysis paths
- document which frontend behavior can already be reused from the current core
- distinguish frontend preparation from premature frontend implementation sprawl

Excluded:

- large new GUI framework commitments without a strong reason
- moving UI concerns into camera or analysis core modules
- broad web/API work that should first land through clearer core contracts

## Session Goal

Leave the repository with one explicit later-frontend preparation slice or one implementation-ready plan for the next frontend-facing branch.

## Status

- current state: queued; later package that should not outrun command, display, and analysis contract stabilization

## Sub-Packages

1. choose the next non-OpenCV frontend preparation target
2. identify the minimum reusable frontend-facing contract slice
3. avoid premature framework lock-in
4. document prepared versus implemented frontend scope

## Open Questions

- is desktop the next real frontend, or should later browser-capable preparation come first conceptually?
- which display or command contracts still need to settle before another frontend is worth starting?
- should the next slice be docs-first or code-backed?

## Learned Constraints

- frontend work must remain downstream of stable core contracts
- do not force a framework choice too early
- OpenCV remains the active prototype path until a stronger successor is justified

## Current Progress

The repository already has:

- the OpenCV prototype as the current active frontend path
- prepared `apps/desktop_app` module space
- early display payload groundwork that later frontends may consume

What remains open:

- the next concrete frontend beyond OpenCV
- the first stable frontend-facing contract slice above the current core

## Execution Plan

1. re-read:
   - `docs/GlobalRoadmap.md`
   - `docs/ProjectDescription.md`
   - `docs/STATUS.md`
   - `apps/desktop_app/STATUS.md`
   - `apps/desktop_app/ROADMAP.md`
2. choose the narrowest frontend preparation slice that does not force premature framework lock-in
3. keep the work above existing command, display, and analysis boundaries
4. implement only if the selected slice is small and justified
5. update docs to keep prepared versus implemented frontend scope explicit

## Validation

- targeted tests if shared adapter or contract code changes
- manual consistency review if the slice remains documentation-first

## Documentation Updates

Before this work package is considered complete, update:

- `apps/desktop_app/STATUS.md`
- `apps/desktop_app/ROADMAP.md`
- `docs/STATUS.md`

## Expected Commit Shape

1. `docs: define next frontend preparation slice`
2. `feat: add frontend preparation baseline`
3. `docs: update frontend preparation status`

## Merge Gate

- frontend planning remains subordinate to stable core contracts
- no premature framework-heavy direction is forced into the repository
- touched tests pass locally where relevant
- docs clearly state what frontend path is prepared versus still deferred

## Recovery Note

To activate this work package later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/STATUS.md`
4. Read `docs/GlobalRoadmap.md`
5. Read `docs/ProjectDescription.md`
6. Read `apps/desktop_app/STATUS.md`
