# C# Handover Hardening

## Purpose

This work package defines the first explicit repository slice aimed at making the current Python architecture easier to hand over or port to C#/.NET later.

Its purpose is not to start a C# implementation in this repository, but to harden the Python-side contracts, naming, and module boundaries that are most likely to survive direct translation.

## Branch

- intended branch: `feature/csharp-handover-hardening`
- activation state: planned after the current host-neutral control and analysis contracts are more stable

## Scope

Included:

- identify the contracts and modules that are strongest candidates for later C# ownership
- reduce Python-specific ambiguity in selected core interfaces
- document what is ready for porting versus still prototype-specific
- prefer small, high-value hardening slices over broad rewrites

Excluded:

- starting a parallel C# codebase
- UI framework migration
- broad stylistic rewrites with no contract payoff
- adapter-specific concerns that do not improve the core handover boundary

## Session Goal

Leave the repository with one clearer handover-oriented slice that makes future C# ownership easier to reason about.

## Execution Readiness Assessment

For a fresh agent, the package was directionally valid but not execution-ready enough:

- the strongest current handover candidate surface was not yet narrowed beyond broad module categories
- the package did not separate low-risk contract-explicitness work from broader portability cleanup
- exit criteria for a first slice were still too abstract

The package is now refined around the adapter/core request boundary first, because that surface is already implemented, test-covered, and likely to survive a direct C# port without pulling in transport or UI decisions.

## Status

- current state: completed; archive after queue/status sync

## Sub-Packages

### SP1 Request DTO Symmetry Hardening

- Goal: make the current adapter-facing request DTOs explicitly map both to and from the underlying core request/configuration contracts
- Scope:
  - add `from_*` classmethods to the existing external request DTOs that already expose `to_*` mapping methods
  - keep field naming translation explicit where adapter DTO names differ from core names
  - cover the new mapping symmetry with targeted request-model tests
- Non-Scope:
  - command-controller signature changes
  - transport serialization helpers
  - new DTO families
- Validation:
  - `tests.test_request_models`
- Dependencies:
  - existing request DTO baseline from CLI/host-neutral command work
- Exit Criterion:
  - request DTOs no longer encode a one-way Python-only mapping assumption

### SP2 Command Result Construction Tightening

- Goal: reduce ad-hoc command-result construction at controller call sites
- Scope:
  - decide whether the typed command-result models should expose small named constructors for common result shapes
  - keep the change local to the command/result boundary
- Non-Scope:
  - broader controller redesign
  - API payload shaping
- Validation:
  - `tests.test_command_controller`
- Dependencies:
  - SP1 not required, but the same handover boundary rationale applies
- Exit Criterion:
  - controller/result construction is more explicit than raw field assembly where that improves portability

### SP3 Handover Candidate Documentation Tightening

- Goal: document which currently implemented contracts look most stable for direct C# ownership
- Scope:
  - update central status and this work package with explicit handover-ready versus still prototype-specific surfaces
  - keep the note bounded to touched contracts
- Non-Scope:
  - new implementation lanes
  - broad roadmap rewrite
- Validation:
  - docs match the implemented hardening slice
- Dependencies:
  - at least one implemented hardening slice
- Exit Criterion:
  - a fresh agent can identify what became more portable in this package

### SP4 Deferred Prototype-Specific Boundary Close-Out

- Goal: close the package without drifting into full portability cleanup
- Scope:
  - explicitly defer remaining Python-specific concerns that would require broader rewrites
  - record the next likely handover-hardening follow-up if more than one slice remains
- Non-Scope:
  - wide refactors across services or frontends
- Validation:
  - `WP09` remains bounded to one coherent portability step or one small cluster of directly related steps
- Dependencies:
  - SP1 to SP3
- Exit Criterion:
  - no further work remains in this package unless the scope intentionally widens

## Open Questions

- which modules are the strongest current handover candidates?
- where are the most expensive remaining implicit Python behaviors?
- should a small handover-readiness checklist be added for selected modules?

## Learned Constraints

- this is not a C# implementation branch
- prefer contract clarity over broad rewrites
- only touch slices with clear later handover value

## Current Progress

The repository already has:

- modular boundaries that roughly align with later C# service and model concerns
- typed request, result, and status models in important areas
- a growing `vision_platform` namespace as the preferred future surface

What remains open:

- which modules are the best early handover candidates
- which implicit Python behaviors should be made more explicit first

Chosen first slice:

- `SP1 Request DTO Symmetry Hardening`
- reason: the request DTO boundary already exists, it is locally test-covered, and explicit bidirectional mapping improves portability without changing the host-neutral controller surface

Implemented progress:

- `SP1` completed
- adapter-facing request DTOs now expose explicit `from_*` classmethods in addition to their existing `to_*` mapping methods
- field-name translation between external request DTOs and the underlying core request/configuration types is now centralized in one bidirectional mapping surface instead of being expressed only in the DTO-to-core direction

Remaining package focus:

- `SP2` completed: typed command-result models now expose named constructors for their common result shapes, and the controller uses those constructors instead of assembling result fields inline
- `SP3` completed through central status/work-package updates that mark the request/result boundary as the currently strongest direct-port handover candidate in this package
- `SP4` completed by explicitly deferring wider portability cleanup, transport concerns, and broad service rewrites beyond this request/result contract cluster

Package outcome:

- the adapter-facing request DTO boundary is now explicit in both directions
- the typed command-result boundary is now constructed through named result factories instead of scattered controller-side field assembly
- the handover-oriented hardening stayed inside the existing host-neutral command boundary without starting a parallel C# lane or widening into transport work
- broader Python-specific concerns remain intentionally deferred because they would require wider rewrites than this package was meant to carry

## Execution Plan

1. re-read:
   - `docs/GlobalRoadmap.md`
   - `docs/ProjectDescription.md`
   - `docs/STATUS.md`
2. identify the current best handover candidates, likely among:
   - common models
   - command surface
   - ROI/focus core contracts
3. choose one narrow hardening slice
4. implement only the smallest change that improves later port clarity
5. add or update tests if contracts or behavior become more explicit
6. record the handover implication in docs

## Validation

- targeted tests for the touched core contract or service surface
- manual review that the selected slice is genuinely more explicit and portable than before

Completed validation for `SP1` and `SP2`:

- `.\.venv\Scripts\python.exe -m unittest tests.test_request_models tests.test_command_results tests.test_command_controller`

## Documentation Updates

Before this work package is considered complete, update:

- `docs/STATUS.md`
- any touched module `STATUS.md`
- this work package with newly learned handover notes if more slices are expected

## Expected Commit Shape

1. `refactor: harden csharp handover contract`
2. `test: cover handover hardening slice`
3. `docs: record csharp handover readiness update`

## Merge Gate

- the touched contract or module is more explicit and portable than before
- no unrelated platform expansion is bundled in
- touched tests pass locally
- docs explain the handover value of the slice clearly

## Recovery Note

To activate this work package later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/STATUS.md`
4. Read `docs/GlobalRoadmap.md`
5. Read `docs/ProjectDescription.md`
6. Identify the narrowest high-value handover contract before creating the branch
