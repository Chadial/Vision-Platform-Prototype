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

## Execution Readiness Assessment

For a fresh agent, the package was directionally valid but not yet execution-ready enough:

- the first concrete slice was not explicit
- the repository already exposed multiple `FocusMethod` names, but the implementation still only had one real evaluator path
- it was unclear whether the next slice should add a second metric or only tighten method selection

The package is now refined so the next bounded slice can be chosen directly without reopening the broader focus roadmap.

## Status

- current state: completed; archive after queue/status sync

## Sub-Packages

### SP1 Tenengrad Method Baseline

- Goal: add one real second focus metric and make method selection explicit inside `focus_core`
- Scope:
  - implement a `tenengrad` evaluator path in `focus_core`
  - make `evaluate_focus(...)` honor `FocusRequest.method`
  - preserve the current Laplace baseline as the default path
- Non-Scope:
  - UI controls for method switching
  - broad metric bake-offs
  - host/API-facing focus configuration
- Validation:
  - targeted `tests.test_focus_core`
  - targeted preview/snapshot focus-consumer tests only if the new method path is exercised there
- Dependencies:
  - existing ROI workflow clarification from `WP05`
  - existing `FocusRequest.method` contract
- Exit Criterion:
  - `laplace` and `tenengrad` are both real, test-covered focus methods, and `evaluate_focus(...)` selects the requested one explicitly

### SP2 Method Selection Reuse In Consumers

- Goal: keep preview/snapshot consumers portable once more than one focus method exists
- Scope:
  - decide whether consumer services should continue injecting evaluators only or accept an explicit method selector path
  - keep any change local and avoid UI-heavy configuration
- Non-Scope:
  - broad host-surface contract work
  - OpenCV menu/control expansion
- Validation:
  - targeted `tests.test_focus_preview_service`
  - targeted `tests.test_snapshot_focus_service`
- Dependencies:
  - SP1
- Exit Criterion:
  - focus-consuming services have one explicit and documented way to stay compatible with multiple focus methods

### SP3 Baseline Comparison And Documentation

- Goal: make the baseline-versus-optional focus story reconstructible from permanent docs
- Scope:
  - record why `tenengrad` was selected as the next slice
  - distinguish current baseline, secondary method support, and deferred future metric families
- Non-Scope:
  - new metrics beyond the selected slice
  - roadmap reprioritization outside `WP06`
- Validation:
  - permanent docs match the implemented focus surface
- Dependencies:
  - SP1 and any SP2 outcome
- Exit Criterion:
  - a later agent can see which methods are implemented, which path is default, and what remains deferred

### SP4 Deferred Focus Expansion Boundary

- Goal: close the package without turning it into a broad focus-experiment lane
- Scope:
  - explicitly defer broader metric families, comparison tooling, and UI/host method switching if still open
  - record narrow follow-up notes for later analysis packages if needed
- Non-Scope:
  - tracking, autofocus, or postprocess expansion
- Validation:
  - `WP06` remains one bounded method-expansion package
- Dependencies:
  - SP1 to SP3
- Exit Criterion:
  - no additional focus-method work remains inside this package without expanding its intended boundary

## Open Questions

- is the next useful slice a new metric or a method-selection contract?
- which focus method best supports both preview and offline reuse?
- how much consumer-facing configurability is needed before API or richer host integration work?

## Learned Constraints

- avoid broad metric experiments in one branch
- keep focus-core changes portable and reusable across live, snapshot, and later offline flows
- tracking work must not be smuggled into focus work

## Current Progress

The repository already has:

- one implemented focus baseline
- ROI-aware focus integration points
- preview- and snapshot-adjacent focus consumers

What remains open:

- whether one additional focus method should become the next baseline extension
- how focus-method selection should be represented once more than one method matters

Chosen first slice:

- `SP1 Tenengrad Method Baseline`
- reason: it is the smallest end-to-end slice that converts the existing multi-method contract from placeholder naming into real implemented behavior without introducing UI or host-surface scope

Implemented progress:

- `SP1` completed
- `focus_core` now implements a real `tenengrad` evaluator path alongside the existing Laplace baseline
- `evaluate_focus(...)` now dispatches explicitly through `FocusRequest.method` instead of silently treating all requests as Laplace
- `laplace` remains the default method path when no explicit request is supplied
- preview-facing consumers remain compatible through the existing evaluator-injection boundary, and focused tests now exercise a Tenengrad-backed preview consumer path
- `SP2` completed
- `FocusPreviewService` and `SnapshotFocusService` now accept a small explicit `focus_method` selection path without requiring custom evaluator injection
- existing evaluator injection remains compatible, and the services infer `tenengrad` correctly when that evaluator is injected directly
- `CameraStreamService.create_focus_preview_service(...)` now exposes the same small method-selection path for preview-adjacent focus consumers

Remaining package focus:

- `SP3` completed through permanent focus-core and central status updates that distinguish Laplace default behavior, Tenengrad support, and deferred future metric families
- `SP4` completed by explicitly deferring broader metric families, comparison tooling, and UI/host method switching instead of stretching this package into a broader focus experimentation lane

Package outcome:

- `laplace` remains the default portable focus baseline
- `tenengrad` is now a real second implemented metric rather than a placeholder method name
- `evaluate_focus(...)` dispatches explicitly by requested method
- preview-/snapshot-adjacent consumers now have a small service-level method-selection path while preserving evaluator injection for local composition
- broader metric families, comparison tooling, and operator-/host-facing method controls remain deferred

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

Completed validation for `SP1`:

- `.\.venv\Scripts\python.exe -m unittest tests.test_focus_core tests.test_focus_preview_service tests.test_snapshot_focus_service tests.test_vision_platform_namespace`

Completed validation for `SP2`:

- `.\.venv\Scripts\python.exe -m unittest tests.test_focus_preview_service tests.test_snapshot_focus_service tests.test_camera_stream_service tests.test_focus_core`

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
