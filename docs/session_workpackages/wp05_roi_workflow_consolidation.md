# ROI Workflow Consolidation

## Purpose

This work package defines the first focused repository slice for making ROI usage consistent across preview, snapshot, and analysis consumers.

Its purpose is to clarify ROI ownership and reuse without leaking UI concerns into the core or forcing analysis logic into the preview layer.

## Branch

- intended branch: `feature/roi-workflow-consolidation`
- activation state: planned after the current command-surface and active OpenCV UI follow-up work are stable enough

## Scope

Included:

- clarify how ROI state is created, owned, and consumed across the current prototype
- define one explicit flow for ROI selection in preview-facing paths and ROI reuse in snapshot or analysis consumers
- tighten the contract between UI-owned ROI interaction and service-owned ROI consumption
- document what remains intentionally outside the first ROI workflow baseline

Excluded:

- freehand ROI implementation
- rich ROI editing workflows such as drag handles, move, resize, or multi-ROI management
- new tracking logic
- broad command-surface redesign outside ROI-related contract shaping

## Session Goal

Leave the repository with one explicit and documented ROI workflow that makes these boundaries clear:

- where ROI interaction starts
- where ROI state lives
- how preview consumers read it
- how snapshot or analysis consumers reuse it
- which parts are still deferred

## Status

- current state: queued; ready to activate after current host-control and active OpenCV UI stabilization work

## Sub-Packages

1. document current ROI data flow
2. choose the first ambiguity to resolve
3. harden one ROI handoff path
4. define explicit deferred ROI behavior
5. update docs to make ROI ownership obvious

## Open Questions

- where should active ROI ownership live long term?
- should snapshot-side consumers default from active ROI state or require explicit ROI input?
- do host-facing ROI commands belong in the command surface at all?

## Learned Constraints

- UI interaction and ROI analysis ownership must stay separate
- rectangle and ellipse are the current supported baseline; freehand remains deferred
- avoid turning ROI state into a UI-only concept or a stream-owned concept

## Current Progress

The repository already has:

- ROI models and rectangle/ellipse mask groundwork
- a first `RoiStateService`
- OpenCV-side rectangle and ellipse entry points
- analysis consumers that can already use ROI-aware paths

What remains unclear enough to justify this package:

- which layer is the intended owner of the active ROI state
- how ROI should move from UI interaction into reusable analysis input
- where future CLI or host-facing ROI commands should attach, if they belong at all

## Execution Plan

1. re-read:
   - `docs/STATUS.md`
   - `docs/GlobalRoadmap.md`
   - `docs/ProjectDescription.md`
   - `apps/opencv_prototype/STATUS.md`
   - `libraries/roi_core/STATUS.md`
2. inspect current ROI model, state-service, and preview integration points
3. document the current actual ROI data flow before changing behavior
4. identify the narrowest ambiguity that should be resolved first
5. implement one end-to-end contract clarification slice
6. update tests around ROI ownership or consumption if behavior becomes more explicit
7. update permanent docs after the workflow is clearer

## Validation

- targeted ROI-core tests
- targeted preview or focus-consumer tests for the touched handoff path
- simulator-backed validation where UI-side ROI creation and analysis-side consumption meet

## Documentation Updates

Before this work package is considered complete, update:

- `libraries/roi_core/STATUS.md`
- `apps/opencv_prototype/STATUS.md` if UI-side ROI behavior changes
- `docs/STATUS.md`

## Expected Commit Shape

1. `refactor: clarify roi workflow ownership`
2. `test: cover roi workflow handoff`
3. `docs: update roi workflow status`

## Merge Gate

- ROI ownership is clearer than before
- UI interaction remains separate from ROI analysis logic
- touched tests pass locally
- docs explicitly state what ROI behavior is implemented and what remains deferred

## Recovery Note

To activate this work package later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/STATUS.md`
4. Read `docs/GlobalRoadmap.md`
5. Read `docs/ProjectDescription.md`
6. Read `libraries/roi_core/STATUS.md`
7. Read `apps/opencv_prototype/STATUS.md`
