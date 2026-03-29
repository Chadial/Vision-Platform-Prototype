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

## Status

- current state: queued; medium-term package that should follow clearer stabilization of core contracts

## Sub-Packages

1. identify the best handover candidate surface
2. choose one narrow explicitness/portability improvement
3. harden the selected contract or service surface
4. record what became more portable and what remains prototype-specific

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
