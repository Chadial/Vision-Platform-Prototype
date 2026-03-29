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

## Status

- current state: queued; prepared conceptually, but should wait until ROI and focus MVP boundaries are clearer

## Sub-Packages

1. choose the first narrow tracking or edge kernel
2. define input and result contracts
3. implement one baseline slice
4. add focused tests
5. document implemented versus aspirational tracking scope

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
