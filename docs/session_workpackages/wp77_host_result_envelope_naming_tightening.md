# WP77 Host Result Envelope Naming Tightening

## Purpose

Normalize one concrete confusing host-facing result, status, or error field without reopening the broader command model or widening transport scope.

## Branch

- intended narrow branch: `feature/host-result-envelope-naming-tightening`
- derive the exact branch only when the concrete ambiguity is selected

## Scope

In scope:

- one specific confusing field, subset, or naming seam in the host-facing envelope family
- the minimum code and test updates needed to clarify it
- corresponding contract doc wording for the changed naming

Out of scope:

- new transport adapters
- broad command-surface redesign
- multiple simultaneous payload reshapes
- host workflow expansion beyond the selected ambiguity

## Session Goal

Resolve one host-facing naming ambiguity so an AMB-side caller can interpret the affected field without project-internal context.

## Status

Prepared only. Activate only when a concrete ambiguity is observed.

## Sub-Packages

1. select one ambiguous host-facing field or subset
2. implement the narrow naming or shaping clarification
3. update the matching tests and contract wording

## Open Questions

- is the next ambiguity in status payloads, command results, error shape, confirmed settings, or stop-result semantics?
- can the issue be solved by documentation only, or is a real payload/name change required?
- would renaming break existing local callers enough to require a compatibility seam?

## Learned Constraints

- the repository wants one host-neutral command/application surface
- host-side usability should tighten clarity before broad transport expansion
- this slice must stay small and should not reopen the full host contract

## Execution Plan

1. capture the exact ambiguous field and the current confusing behavior
2. inspect the controlling payload, controller, and contract-doc seams
3. implement the smallest coherent naming clarification
4. run the targeted tests or CLI checks for the affected payload path
5. update the contract wording and central docs if the package lands

## Validation

- targeted automated coverage for the affected payload/result path
- optionally one CLI command example if that is the clearest proof of the changed envelope

## Documentation Updates

- `docs/HOST_CONTRACT_BASELINE.md`
- `docs/STATUS.md` and `docs/WORKPACKAGES.md` when the package lands
- module status/docs only if the implemented surface changes materially

## Expected Commit Shape

One narrow contract/code/test slice is preferred.

## Merge Gate

- one concrete host-facing naming ambiguity is removed
- tests or CLI evidence cover the changed path
- the package does not widen transport scope or reopen the command model broadly

## Recovery Note

Resume with:

1. `AGENTS.md`
2. `docs/SESSION_START.md`
3. `docs/MODULE_INDEX.md`
4. `docs/STATUS.md`
5. `docs/WORKPACKAGES.md`
6. `docs/HOST_CONTRACT_BASELINE.md`
7. this file
