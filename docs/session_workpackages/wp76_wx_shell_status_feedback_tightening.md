# WP76 wx Shell Status Feedback Tightening

## Purpose

Improve one concrete wx-shell feedback seam so operators can more reliably understand what just happened and what state the shell is currently in.

## Branch

- intended narrow branch: `feature/wx-shell-status-feedback-tightening`
- derive the exact branch only when the concrete friction point is chosen

## Scope

In scope:

- one concrete observed status or feedback problem in the wx shell
- the smallest UI/local-shell change that makes that feedback clearer
- bounded smoke verification on the local shell path

Out of scope:

- broad wx-shell usability redesign
- unrelated ROI or rendering work
- host contract changes
- new transport or session architecture

## Session Goal

Resolve one specific wx-shell feedback ambiguity, with a clear before/after description and one bounded validation path.

## Status

Prepared only. Do not activate until a concrete friction point is chosen.

## Sub-Packages

1. capture the concrete feedback problem
2. choose the smallest feedback/UI change that resolves it
3. verify the shell behavior through a bounded smoke path

## Open Questions

- is the next friction point about transient status, recording feedback, startup errors, snapshot confirmation, or live command sync?
- should the fix live in the shell presentation only, or does it expose a missing shared display/status model?
- is there already an existing shell status pattern that should be reused instead of inventing a new one?

## Learned Constraints

- the wx shell should remain a bounded frontend over shared controller/preview/display layers
- status ownership for camera semantics should not move into UI-private logic
- activation must be driven by concrete observed operator friction, not generic polish ambition

## Execution Plan

1. identify the exact shell feedback ambiguity from real usage or a concrete user report
2. inspect the existing shell and shared display/status seams involved
3. implement the smallest fix that improves operator readability
4. run a bounded shell smoke or targeted test for the touched path
5. update central docs only if the implemented shell surface materially changes

## Validation

- one bounded local-shell smoke path reproducing the fixed feedback
- targeted automated coverage if the touched seam already has test ownership

## Documentation Updates

- `apps/local_shell/STATUS.md` if the shell surface changes materially
- `docs/STATUS.md` and `docs/WORKPACKAGES.md` only when the package is actually landed

## Expected Commit Shape

One narrow UI/feedback commit is preferred.

## Merge Gate

- one concrete shell feedback ambiguity is resolved
- the change stays within bounded local-shell scope
- no broad UI redesign or host-surface expansion is pulled in

## Recovery Note

Resume with:

1. `AGENTS.md`
2. `docs/SESSION_START.md`
3. `docs/MODULE_INDEX.md`
4. `docs/STATUS.md`
5. `docs/WORKPACKAGES.md`
6. `apps/local_shell/README.md`
7. `apps/local_shell/STATUS.md`
8. this file
