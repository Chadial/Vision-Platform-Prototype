# Focus Method Expansion

## Purpose

This work package defines the next focused step for moving the current focus baseline beyond one initial method.

Its purpose is to add one stronger or alternative focus-method slice without turning the focus module into a broad experimentation branch all at once.

## Branch

- intended branch: `feature/focus-method-expansion`
- activation state: planned after ROI workflow ownership is clearer

## Scope

Included:

- identify one useful next focus-method or focus-selection enhancement
- keep the change compatible with current preview, snapshot, and later postprocess usage
- preserve the current focus module boundaries and ROI integration path
- document the method choice and why it was selected over broader experimentation

Excluded:

- broad metric bake-offs across many methods in one branch
- tracking or edge-analysis work disguised as focus work
- UI-heavy focus controls beyond what current consumers need
- freehand ROI implementation

## Session Goal

Add one reviewable focus-method slice that improves the current baseline while keeping the focus module portable and easy to hand over later.

## Current Progress

The repository already has:

- one implemented focus baseline
- ROI-aware focus integration points
- preview- and snapshot-adjacent focus consumers

What remains open:

- whether one additional focus method should become the next baseline extension
- how focus-method selection should be represented once more than one method matters

## Execution Plan

1. re-read:
   - `docs/STATUS.md`
   - `docs/GlobalRoadmap.md`
   - `docs/ProjectDescription.md`
   - `libraries/focus_core/STATUS.md`
   - `libraries/focus_core/ROADMAP.md`
2. inspect the current focus evaluator and tests
3. choose one additional method or one explicit method-selection improvement
4. implement the change behind the existing focus-core boundaries
5. add targeted tests and compare outputs where useful
6. update docs to distinguish baseline method from prepared future directions

## Validation

- targeted focus-core tests
- simulator-backed preview or snapshot focus tests if the selected slice affects consumers

## Documentation Updates

Before this work package is considered complete, update:

- `libraries/focus_core/STATUS.md`
- `libraries/focus_core/ROADMAP.md`
- `docs/STATUS.md`

## Expected Commit Shape

1. `feat: add next focus method slice`
2. `test: cover focus method expansion`
3. `docs: update focus method status`

## Merge Gate

- one additional focus-method slice is clearly implemented or selected
- current focus consumers remain understandable
- touched tests pass locally
- docs state what is now baseline, optional, or still deferred

## Recovery Note

To activate this work package later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/STATUS.md`
4. Read `libraries/focus_core/STATUS.md`
5. Read `libraries/focus_core/ROADMAP.md`
6. Re-check the current ROI workflow decision before selecting the slice
