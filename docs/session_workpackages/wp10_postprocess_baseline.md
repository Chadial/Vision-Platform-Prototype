# Postprocess Baseline

## Purpose

This work package defines the first explicit offline or postprocess-oriented path for the platform.

Its purpose is to make stored images and later analysis results reusable outside the live camera loop without prematurely building a large secondary application.

## Branch

- intended branch: `feature/postprocess-baseline`
- activation state: planned after storage and analysis contracts are stable enough to reuse offline

## Scope

Included:

- identify one useful offline evaluation slice over stored images or image series
- keep the path aligned with existing storage, ROI, and focus contracts where possible
- clarify what belongs in a future postprocess tool versus what remains a shared library concern

Excluded:

- broad desktop UI work
- full analytics workstation behavior
- duplicate storage pipelines unrelated to current core contracts
- unrelated live-preview feature work

## Session Goal

Leave the repository with one explicit postprocess baseline or one implementation-ready contract slice for offline evaluation.

## Current Progress

The repository already has:

- stored image and metadata paths
- focus and ROI foundations that should later be reusable offline
- a prepared `apps/postprocess_tool` module area

What remains open:

- the first concrete offline use case
- the first thin entry point for offline evaluation

## Execution Plan

1. re-read:
   - `docs/ProjectDescription.md`
   - `docs/STATUS.md`
   - `apps/postprocess_tool/README.md`
   - `apps/postprocess_tool/STATUS.md`
   - `apps/postprocess_tool/ROADMAP.md`
2. choose one small offline use case that already fits the current core
3. keep shared logic in libraries or services where possible
4. add a thin app or tool layer only if needed for the selected slice
5. add focused tests or smoke coverage
6. update docs once the baseline is real

## Validation

- targeted tests for the shared analysis or storage path being reused
- smoke validation for a thin postprocess entry point if one is added

## Documentation Updates

Before this work package is considered complete, update:

- `apps/postprocess_tool/STATUS.md`
- `apps/postprocess_tool/ROADMAP.md`
- `docs/STATUS.md`

## Expected Commit Shape

1. `feat: add postprocess baseline`
2. `test: cover postprocess baseline`
3. `docs: update postprocess baseline status`

## Merge Gate

- the offline path reuses current shared contracts rather than inventing a second core
- touched tests pass locally where relevant
- docs explain what postprocess behavior is now available and what remains prepared only

## Recovery Note

To activate this work package later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/STATUS.md`
4. Read `apps/postprocess_tool/STATUS.md`
5. Read `apps/postprocess_tool/ROADMAP.md`
6. Confirm that the selected offline slice can reuse current storage and analysis contracts cleanly
