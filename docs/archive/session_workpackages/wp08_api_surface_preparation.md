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

## Execution Readiness Assessment

For a fresh agent, the package was directionally valid but not execution-ready enough:

- the first adapter-facing payload family was not yet chosen
- it was unclear whether the next slice should stay documentation-only or already add code
- the boundary between shared command contracts and future transport DTOs was still too implicit

The package is now refined around one narrow adapter payload family so later API work can build on a concrete mapping layer instead of improvising serialization directly at the transport edge.

## Status

- current state: completed; archive after queue/status sync

## Sub-Packages

### SP1 Status Payload Family Baseline

- Goal: define the first transport-neutral API-adapter DTO family above the shared command surface
- Scope:
  - add adapter-facing payload dataclasses for `SubsystemStatus` and its nested status/configuration shapes
  - add one mapper from host-neutral `SubsystemStatus` into those payloads
  - keep the mapping above the shared controller/models layer
- Non-Scope:
  - HTTP, IPC, or framework wiring
  - command execution DTOs beyond the first payload family
  - CLI replacement or duplication
- Validation:
  - targeted `tests.test_api_service`
  - regression coverage for command-controller / CLI only if the touched slice interacts with those paths
- Dependencies:
  - stabilized host-neutral status contract from `WP02`
- Exit Criterion:
  - the repository contains one explicit adapter-facing status payload family that stays separate from shared core models

### SP2 Adapter Serialization Boundary Tightening

- Goal: clarify where generic serialization belongs once adapter DTOs exist
- Scope:
  - decide whether existing CLI-facing serialization should remain local or reuse adapter-layer helpers
  - keep the change small and avoid transport or framework commitments
- Non-Scope:
  - full CLI refactor
  - API framework introduction
- Validation:
  - targeted `tests.test_camera_cli`
  - targeted adapter-layer tests if helpers move
- Dependencies:
  - SP1
- Exit Criterion:
  - serialization ownership between adapter DTOs and adapter output formatting is clearer than before

### SP3 API-Service Module Activation And Documentation

- Goal: move `api_service` from prepared-only to an explicit baseline-preparation module
- Scope:
  - update module and central docs to reflect the implemented DTO/mapping slice
  - record what remains deferred
- Non-Scope:
  - transport implementation
  - broader repository reprioritization
- Validation:
  - docs match the implemented adapter-preparation slice
- Dependencies:
  - SP1 and any SP2 outcome
- Exit Criterion:
  - a fresh agent can identify what `api_service` now contains and what still remains out of scope

### SP4 Deferred API Boundary Close-Out

- Goal: close the package without accidentally starting an API implementation lane
- Scope:
  - explicitly defer framework choice, frame/feed streaming, and broader command-result exposure if still open
  - record the next likely slice for later API work
- Non-Scope:
  - implementation of deferred API concerns
- Validation:
  - `WP08` remains a bounded preparation package
- Dependencies:
  - SP1 to SP3
- Exit Criterion:
  - no further API-preparation work remains inside this package without widening the intended scope

## Open Questions

- should the first API-preparation slice be code-backed or documentation-first?
- what belongs in adapter DTOs versus shared host-neutral contracts?
- is local API, IPC, or embedded host integration the most likely first adapter target?

## Learned Constraints

- do not create a second business-logic stack
- keep transport concerns out of the core until the shared control path is clearer
- API preparation should follow host-contract hardening, not precede it

## Current Progress

The repository already has:

- a host-neutral command/controller baseline
- typed request and result shapes for important command operations
- a prepared `services/api_service` module area

What remains open:

- the first adapter-facing payload family
- the first boundary between host-neutral core contracts and later transport-facing DTOs

Chosen first slice:

- `SP1 Status Payload Family Baseline`
- reason: status is the most stable and lowest-risk adapter-facing payload family, and it gives future API work a real mapping layer without pulling command execution or transport choices into scope

Implemented progress:

- `SP1` completed
- `api_service` now contains a first transport-neutral status payload family above the shared command/controller layer
- `SubsystemStatus` mapping now lands in adapter DTOs instead of assuming future transports should serialize shared core models directly

Remaining package focus:

- `SP2` completed through an explicit conservative boundary decision: existing CLI serialization stays local for now, while the new API-service DTO layer remains the transport-facing preparation path for later external adapters
- `SP3` completed through module activation and permanent doc updates
- `SP4` completed by explicitly deferring framework choice, feed/stream transport, and broader command-result DTO families until a real external adapter lane is opened

Package outcome:

- `api_service` is no longer only a prepared placeholder
- one explicit adapter-facing status payload family now exists above the shared command/controller layer
- shared core models remain business-logic contracts, while adapter DTOs are now an explicit separate concern
- CLI serialization intentionally remains local, so this package does not over-unify adapters prematurely
- framework choice, streaming feeds, and broader command-result DTO families remain deferred

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

Completed validation for `SP1`:

- `.\.venv\Scripts\python.exe -m unittest tests.test_api_service tests.test_command_controller tests.test_camera_cli`

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
