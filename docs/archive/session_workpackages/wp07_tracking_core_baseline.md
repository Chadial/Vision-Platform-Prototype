# Tracking Core Baseline

## Purpose

This work package defines the first deliberate tracking or edge-analysis foundation slice for the platform.

Its purpose is to create a narrow, reusable baseline in `tracking_core` without prematurely committing to a full crack-tip workflow, live UI-heavy tracking path, or transport-facing result surface.

## Branch

- intended branch: `feature/tracking-core-baseline`
- activation state: planned after ROI and focus MVP boundaries are clearer

## Scope

Included:

- define the first reusable tracking or edge-analysis kernel
- keep contracts aligned with existing ROI, focus, and overlay-ready model boundaries
- favor a library-first baseline over a UI-driven experiment when possible
- document what problem the first tracking slice does and does not solve

Excluded:

- full crack-tip detection
- broad live tracking UI workflows
- automation or actuator feedback logic
- premature API/feed result envelopes

## Session Goal

Leave the repository with one explicit first tracking-core capability or at least one implementation-ready contract baseline that future preview, postprocess, or API consumers can build on.

## Execution Readiness Assessment

For a fresh agent, the package was directionally clear but not execution-ready enough:

- the first concrete kernel was not yet selected
- input/result contracts were still unspecified
- the line between reusable library baseline and later tracking workflow was too open

The package is now refined around one narrow, profile-based edge kernel so later work can build on a real analytical baseline instead of a purely prepared module.

## Status

- current state: completed; archive after queue/status sync

## Sub-Packages

### SP1 Edge Profile Kernel Baseline

- Goal: establish one reusable, ROI-aware edge/profile kernel in `tracking_core`
- Scope:
  - define a small request/result contract for one directional edge-profile pass
  - implement dominant edge extraction along a horizontal or vertical profile
  - keep the kernel library-only and transport-neutral
- Non-Scope:
  - drift logic
  - crack-tip heuristics
  - multi-frame tracking
  - UI overlays or rendering
- Validation:
  - targeted `tests.test_tracking_core`
  - targeted namespace/import coverage if the new library surface is exported
- Dependencies:
  - existing frame and ROI contracts
- Exit Criterion:
  - `tracking_core` contains one real, test-covered edge/profile kernel with stable request/result dataclasses

### SP2 Module Activation And Documentation

- Goal: move `tracking_core` from prepared-only to active baseline documentation status
- Scope:
  - update module docs and central status to reflect the implemented kernel
  - record what this first kernel does and does not solve
- Non-Scope:
  - broader tracking roadmap reprioritization
  - drift, crack-tip, or postprocess implementation
- Validation:
  - docs match the implemented kernel and module state
- Dependencies:
  - SP1
- Exit Criterion:
  - a fresh agent can tell from docs that `tracking_core` now contains an implemented profile-based edge baseline

### SP3 Deferred Tracking Boundary Close-Out

- Goal: explicitly bound what remains out of scope after the first kernel lands
- Scope:
  - defer multi-frame tracking, drift indication, crack-tip heuristics, and UI-facing workflows
  - record the next likely follow-up package boundary
- Non-Scope:
  - implementation of deferred tracking logic
- Validation:
  - `WP07` remains a narrow baseline package instead of expanding into a full tracking lane
- Dependencies:
  - SP1 and SP2
- Exit Criterion:
  - no further tracking work remains inside this package without widening its intended scope

## Open Questions

- should tracking start from edge extraction, drift indication, or feature-anchor tracking?
- should the first slice be library-only or preview-adjacent?
- what is the smallest tracking result shape that survives later API and overlay use?

## Learned Constraints

- avoid committing to full crack-tip workflows too early
- prefer library-owned kernels over UI-driven experiments for the first slice
- keep contracts aligned with existing ROI and focus boundaries

## Current Progress

The repository already has:

- prepared `tracking_core` module space
- ROI, focus, and overlay-related groundwork that tracking should later align with

What remains open:

- the first concrete tracking or edge kernel
- the first stable tracking input and result contract

Chosen first slice:

- `SP1 Edge Profile Kernel Baseline`
- reason: it is the narrowest library-owned kernel that matches the documented profile-/column-scan direction without prematurely committing to drift logic, crack-tip heuristics, or UI workflows

Implemented progress:

- `SP1` completed
- `tracking_core` now exposes one transport-neutral edge-profile request/result contract together with dominant-edge extraction for horizontal and vertical profiles
- the baseline works on `FrameData` or `CapturedFrame` and can optionally limit analysis to an existing ROI
- `SP2` completed through module activation and permanent doc updates
- `SP3` completed by explicitly deferring drift logic, crack-tip heuristics, multi-frame tracking, and UI workflows

Package outcome:

- `tracking_core` is no longer only a prepared module placeholder
- the first baseline is library-only, ROI-aware, and reusable by later preview, postprocess, or API consumers
- the package does not yet claim drift indication, crack-tip estimation, or multi-frame tracking

## Execution Plan

1. re-read:
   - `docs/GlobalRoadmap.md`
   - `docs/ProjectDescription.md`
   - `libraries/tracking_core/README.md`
   - `libraries/tracking_core/STATUS.md`
   - `libraries/tracking_core/ROADMAP.md`
2. choose the narrowest first kernel that adds real analytical value
3. define input and result contracts before writing heavier logic
4. implement the first baseline slice
5. add focused tests
6. update docs to show what is foundation versus still aspirational

## Validation

- targeted tracking-core unit tests
- optional simulator-backed fixture data if the selected slice benefits from it

Completed validation:

- `.\.venv\Scripts\python.exe -m unittest tests.test_tracking_core tests.test_vision_platform_namespace`

## Documentation Updates

Before this work package is considered complete, update:

- `libraries/tracking_core/STATUS.md`
- `libraries/tracking_core/ROADMAP.md`
- `docs/STATUS.md`

## Expected Commit Shape

1. `feat: add tracking core baseline`
2. `test: cover tracking core baseline`
3. `docs: update tracking core status`

## Merge Gate

- the first tracking slice is explicit and reviewable
- contracts remain compatible with existing ROI and focus boundaries
- touched tests pass locally
- docs clearly separate prepared tracking direction from implemented tracking behavior

## Recovery Note

To activate this work package later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/STATUS.md`
4. Read `docs/GlobalRoadmap.md`
5. Read `docs/ProjectDescription.md`
6. Read `libraries/tracking_core/STATUS.md`
