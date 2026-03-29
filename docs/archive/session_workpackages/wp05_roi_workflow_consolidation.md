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

## Execution Readiness Assessment

For a fresh agent, the package was directionally clear but not execution-ready enough:

- the intended first slice was not explicit enough
- ROI ownership between OpenCV draft interaction and committed active ROI remained underspecified
- the existing sub-package list was too coarse to act as a direct next-step queue

The package is now refined into ordered sub-packages so a later agent can choose the next bounded slice without re-deriving the workflow.

## Status

- current state: completed; archive after queue/status sync

## Sub-Packages

### SP1 Committed Active ROI Ownership

- Goal: make the committed active ROI read from one service-owned path while keeping OpenCV interaction state limited to draft selection concerns
- Scope:
  - clarify that `RoiStateService` is the committed active ROI source when present
  - keep OpenCV-local state only for in-progress ROI entry interaction
  - ensure preview rendering/status reads the same committed ROI that analysis consumers read
- Non-Scope:
  - richer ROI editing
  - host-facing ROI commands
  - ROI serialization or persistence
- Validation:
  - targeted `tests.test_opencv_preview`
  - targeted `tests.test_focus_preview_service`
- Dependencies:
  - existing `RoiStateService`
  - existing OpenCV preview ROI entry baseline
- Exit Criterion:
  - active ROI display in the OpenCV path reflects the shared ROI state instead of a parallel window-owned committed copy

### SP2 ROI Consumer Precedence Clarification

- Goal: make explicit when consumers use explicit per-call ROI versus the shared active ROI state
- Scope:
  - tighten and document precedence rules for preview-focus, snapshot-focus, and overlay-composition consumers
  - keep full-frame fallback explicit when no ROI is active
- Non-Scope:
  - new analysis methods
  - ROI command-controller work
- Validation:
  - targeted `tests.test_focus_preview_service`
  - targeted `tests.test_snapshot_focus_service`
  - targeted `tests.test_overlay_composition_service`
- Dependencies:
  - SP1 ownership clarification
- Exit Criterion:
  - the repository has one explicit "explicit ROI overrides shared active ROI; otherwise shared active ROI applies; otherwise full frame" rule documented and test-covered

### SP3 ROI Workflow Documentation Tightening

- Goal: make the implemented ROI workflow reconstructible from permanent docs without rereading code
- Scope:
  - update ROI-core, OpenCV prototype, and central status docs with the implemented ownership and fallback rules
  - record what is deliberately deferred
- Non-Scope:
  - roadmap reprioritization
  - new module structure
- Validation:
  - docs align with implemented behavior and current tests
- Dependencies:
  - SP1 and SP2 outcomes
- Exit Criterion:
  - a fresh agent can identify ROI owner, consumer precedence, and deferred items from permanent docs alone

### SP4 Deferred ROI Boundary Close-Out

- Goal: close the package by explicitly bounding what does not belong in the first ROI workflow baseline
- Scope:
  - confirm deferral of host/CLI ROI command surface, multi-ROI management, and rich edit interactions
  - record any narrow follow-up note for `WP06`/later packages when discovered
- Non-Scope:
  - implementation of deferred capabilities
  - tracking or API preparation
- Validation:
  - `wp05` close-out notes stay within current PM order
- Dependencies:
  - SP1 to SP3
- Exit Criterion:
  - no further ROI-workflow ambiguity remains inside this package without expanding scope

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

Chosen first slice:

- `SP1 Committed Active ROI Ownership`
- reason: it is the smallest end-to-end ambiguity that affects both UI rendering and downstream analysis reuse while staying fully local and simulator-verifiable

Implemented progress:

- `SP1` completed
- OpenCV preview now treats `RoiStateService` as the committed active ROI source when the service is wired in
- OpenCV-local ROI state is now only the fallback path when no shared ROI state service is present
- in-progress ROI entry remains local to the OpenCV window through the existing anchor/preview draft state
- preview status rendering and ROI overlay drawing now read the same committed ROI path that preview-focus, snapshot-focus, and overlay-composition consumers already use
- `SP2` completed
- `RoiStateService` now exposes one explicit `resolve_active_roi(...)` rule used by preview-focus, snapshot-focus, and overlay-composition consumers
- the consumer precedence is now explicit and shared: explicit ROI overrides shared active ROI; otherwise shared active ROI applies; otherwise consumers fall back to full frame
- `SP3` completed through permanent doc updates in ROI-core, OpenCV prototype, and central status docs
- `SP4` completed by explicitly deferring host/CLI ROI commands, multi-ROI management, and rich ROI editing to later packages instead of stretching this package beyond the MVP boundary

Package outcome:

- ROI interaction starts in the OpenCV UI layer as local draft state
- committed active ROI lives in `RoiStateService` when that shared service is present
- preview rendering, preview-focus, snapshot-focus, and overlay-composition now align on that same committed ROI source
- explicit per-call ROI still remains available and intentionally overrides shared state
- later ROI producers, host-surface attachment, and richer editing remain deferred

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

Completed validation for `SP1`:

- `.\.venv\Scripts\python.exe -m unittest tests.test_opencv_preview tests.test_focus_preview_service tests.test_snapshot_focus_service tests.test_overlay_composition_service`

Completed validation for `SP2` and package close-out:

- `.\.venv\Scripts\python.exe -m unittest tests.test_roi_state_service tests.test_opencv_preview tests.test_focus_preview_service tests.test_snapshot_focus_service tests.test_overlay_composition_service`

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
