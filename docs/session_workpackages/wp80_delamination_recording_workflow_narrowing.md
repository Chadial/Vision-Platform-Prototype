# WP80 Delamination Recording Workflow Narrowing

## Purpose

Turn the confirmed `Delamination Recording` workflow into the first explicit workflow-first `Hybrid Companion` package, so future implementation work is selected through one practical end-to-end product slice instead of through older residual buckets.

## Branch

- intended narrow branch: `feature/wp80-delamination-recording-workflow`
- derive the exact implementation branch only when code work begins

## Closure Lane

- `Usable Camera Subsystem / Pre-Product Baseline`

## Slice Role

- workflow-first narrowing
- product-direction anchoring
- host-plus-shell usability clarification

## Workflow Reading

Functional workflow meaning:

- record specimen behavior during the delamination test

Current technical execution model:

- preview
- settings
- recording start
- recording stop
- save path
- optional `max frames` stop behavior when relevant

Interpretation rule:

- read this package through the host-driven `start -> run -> stop` delamination-use path first
- treat `max frames` as one practical stop parameter in the current phase, not as the conceptual definition of the workflow
- bounded-recording terminology remains useful at the service level, but this workflow package should be read through the host-driven delamination-use path first

## Scope Level

- one confirmed functional workflow
- no broad architecture rewrite
- no broad host-contract expansion

## Producer / Consumer / Structure Impact

- producer-facing: host command flow and shell state reflection for recording
- consumer-facing: shell operator readability and practical workflow execution
- structure impact: none required beyond clarifying the selected seams

## What This Package Does Not Close

- the full current phase
- the geometry-capture workflow
- the setup/focus/ROI workflow
- broad headless-kernel preparation
- broad compatibility-shim retirement

## Policy Questions Still Open

- whether the next blocker inside this workflow is mainly shell feedback, host naming, or a direct workflow seam
- whether `max frames` needs only shell reflection tightening or also small host/shell wording clarification without becoming the center of the workflow
- whether any remaining recording-status gap belongs inside `WP80` or should become a reactivated `WP76`

## Scope

In scope:

- define the current `Delamination Recording` workflow as the default next product slice
- define the workflow first through host-driven recording during the real delamination run:
  - host starts recording
  - recording runs during the test
  - host stops recording
- map that workflow to the current phase-appropriate technical execution model:
  - preview
  - settings
  - recording start
  - recording stop
  - save path
  - practical `max frames reached` stop behavior when relevant
- make the required host-plus-shell expectations explicit for this workflow:
  - host controls `start`, `stop`, `max frames`, `recording fps`, `save path`, and core settings
  - shell remains visible, locally adjustable, and reflective of recording state and outcomes
- keep the package from collapsing into a generic bounded-recording refinement slice
- identify the smallest code-facing seams that would need implementation next for this workflow to be practical
- keep later follow-up selection aligned with `Hybrid Companion` rather than with old closure logic

Out of scope:

- implementing the next recording feature directly in this package
- redesigning the command surface
- broad wx-shell UX work
- broad hardware reruns
- broad offline, MCP, packaging, or C# lanes

## Session Goal

Leave the repository with one execution-ready workflow package that makes `Delamination Recording` the concrete default next implementation slice for the current product direction.

## Status

Prepared and selected as `current next` at the PM level.

## Execution Plan

1. restate the workflow in product terms and in concrete technical terms
2. make the host-driven `start -> run -> stop` reading explicit before naming the supporting technical controls
3. define the exact host expectations for this workflow in the current phase
4. define the exact shell-reflection and shell-settings expectations for this workflow in the current phase
5. capture the smallest likely implementation seams without widening scope
6. point follow-up activation either to direct implementation or, only if justified later, to a reactivated narrow seam package such as `WP76`

## Validation

- verify the package aligns with `docs/STATUS.md` and `docs/WORKPACKAGES.md`
- verify the package does not reopen broad residual or architecture lanes
- verify the package stays consistent with the current functional-workflow framing
- verify the package does not implicitly redefine the workflow as merely a bounded-recording refinement

## Documentation Updates

- `docs/WORKPACKAGES.md`
- `docs/STATUS.md`
- derived views only if the active queue summary later needs them

## Expected Commit Shape

One PM/documentation commit is preferred.

## Merge Gate

- `WP80` is clearly the `current next`
- the workflow is expressed through the current `Hybrid Companion` product lens
- the workflow is centered on host-driven delamination recording rather than on bounded-recording terminology
- the package stays implementation-ready without turning into a broad refactor plan
- older residual packages remain visible but no longer dominate next-step selection

## Recovery Note

Resume with:

1. `AGENTS.md`
2. `docs/SESSION_START.md`
3. `docs/MODULE_INDEX.md`
4. `docs/STATUS.md`
5. `docs/WORKPACKAGES.md`
6. this file
