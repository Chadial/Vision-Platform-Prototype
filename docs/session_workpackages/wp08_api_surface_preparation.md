# API Surface Preparation

## Purpose

This work package defines the first focused preparation step for an external API or feed adapter above the shared host-neutral control layer.

Its purpose is to avoid creating a second business-logic stack while still making later external integration easier to plan and execute.

## Branch

- intended branch: `feature/api-surface-preparation`
- activation state: planned after the host-neutral command surface is considered stable enough for an external adapter

## Scope

Included:

- identify the first external-adapter-ready contract slice
- keep API/feed work above the shared host-neutral control/application layer
- clarify what belongs in adapter payload shaping versus core request/result contracts
- document a small starting point for later API-service work

Excluded:

- full API-service implementation
- transport framework decisions beyond what is necessary for planning
- OpenCV or CLI-specific behavior
- unrelated business-logic duplication

## Session Goal

Leave the repository with one explicit first API-preparation slice that makes future adapter work easier without forcing premature transport commitments into the core.

## Current Progress

The repository already has:

- a host-neutral command/controller baseline
- typed request and result shapes for important command operations
- a prepared `services/api_service` module area

What remains open:

- the first adapter-facing payload family
- the first boundary between host-neutral core contracts and later transport-facing DTOs

## Execution Plan

1. re-read:
   - `docs/STATUS.md`
   - `docs/GlobalRoadmap.md`
   - `docs/ProjectDescription.md`
   - `services/api_service/README.md`
   - `services/api_service/STATUS.md`
   - `services/api_service/ROADMAP.md`
2. inspect the current host-neutral control surface and decide whether the next slice is planning-only or code-backed
3. choose one minimal adapter preparation step
4. keep the shared control/application layer as the source beneath the adapter
5. add or update tests only if behavior or contract code changes
6. update docs to capture what is now ready for later API work

## Validation

- targeted command-controller tests if shared control contracts change
- adapter-layer tests if a small DTO or mapping slice is added

## Documentation Updates

Before this work package is considered complete, update:

- `services/api_service/STATUS.md`
- `services/api_service/ROADMAP.md`
- `docs/STATUS.md`

## Expected Commit Shape

1. `feat: prepare api surface baseline`
2. `test: cover api surface preparation`
3. `docs: update api preparation status`

## Merge Gate

- the first API-preparation slice is clearer than before
- no duplicate business-logic path is introduced
- touched tests pass locally where relevant
- docs clearly describe what is prepared versus not yet exposed

## Recovery Note

To activate this work package later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/STATUS.md`
4. Read `services/api_service/STATUS.md`
5. Read `services/api_service/ROADMAP.md`
6. Confirm the host-neutral command surface is stable enough for the chosen slice
