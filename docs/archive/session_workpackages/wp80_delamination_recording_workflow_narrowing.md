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

Landed. `WP80` is now complete as one sequence of small sub-packages under the same workflow-first lane rather than as one large recording umbrella.

Closure result:

- the delamination workflow is now represented through one complete host-plus-shell baseline for `start -> run -> stop`
- `max frames` remains available as one practical stop parameter when relevant, but it is not the conceptual center of the workflow
- the remaining queue can now move to `WP81` without leaving delamination-recording reflection, save-path understanding, smoke coverage, or failure-state visibility half-defined

## Sub-Packages

### Landed

#### `WP80.A Host Start Uses Visible Shell Recording Defaults`

- status: landed
- purpose: keep host-driven `start-recording` aligned with the visible shell recording settings when optional host overrides are omitted
- result:
  - external `start-recording` now reuses shell-visible recording settings by default
  - the host overrides only the fields it explicitly supplies

#### `WP80.B Recording Reflection In Shell Status`

- status: landed
- purpose: make the running or last delamination recording run more explicitly readable in the companion shell and published shell status
- result:
  - the wx-shell live status snapshot now exposes one explicit recording-reflection block with run phase, summary, file stem, save directory, stop reason, and frames written
  - the visible shell status prefix now also keeps the current or last recording file stem readable

#### `WP80.C Stop-Reason Reflection Tightening`

- status: landed
- purpose: distinguish host stop, practical `max_frames_reached`, and failure termination more clearly in the delamination workflow
- scope:
  - visible stop reason in shell-facing reflection
  - same stop reason in published live status
  - no new stop-rule architecture

### Closure Slices

#### `WP80.D Save-Path Reflection Tightening`

- status: landed
- purpose: make the active or last recording target path easier to understand during and after the run
- scope:
  - align shell-visible save-path cues with published live status
  - keep recording target-path reading understandable without opening broader storage work

#### `WP80.E Run-State Messaging Tightening`

- status: landed
- purpose: make the shell wording read more clearly as a delamination run lifecycle instead of generic bounded-recording mechanics
- scope:
  - tighten start / running / stopped messaging
  - avoid broad shell copy or UI redesign

#### `WP80.F Host-Control Smoke For Delamination Path`

- status: landed
- purpose: prove one repeatable host-start / run / stop delamination-path block against the current companion shell baseline
- scope:
  - host starts recording
  - shell reflects running state
  - host stops or `max frames` ends the run practically
  - resulting status remains understandable

#### `WP80.G Failure Reflection Narrowing`

- status: landed
- purpose: make delamination-relevant recording failures understandable enough in shell and published status without opening a broad error-platform lane
- scope:
  - recording start failure
  - recording stop failure
  - save-path or write failure reflection

### Ordering Note

Execution order used inside `WP80`:

1. `WP80.D Save-Path Reflection Tightening`
2. `WP80.E Run-State Messaging Tightening`
3. `WP80.F Host-Control Smoke For Delamination Path`
4. `WP80.G Failure Reflection Narrowing`

Landed implementation slices so far:

- external `start-recording` now reuses shell-visible recording settings by default and applies only explicitly supplied host overrides
- the wx-shell live status snapshot now exposes one explicit recording-reflection block with run phase, summary, file stem, save directory, stop reason, and frames written, while the visible shell status prefix also keeps the current or last recording file stem readable
- the wx-shell recording reflection now also categorizes stop causes for the delamination path, so host stop, `max_frames_reached`, and failure-oriented termination are more clearly distinguished in shell-facing and published status
- the visible shell status prefix now also keeps the active or last recording save directory readable so path understanding remains aligned between shell and live status
- recording lifecycle messages now read more clearly as a host-driven delamination run, including path-aware start/stop wording instead of only generic bounded-recording wording
- one repeatable host-control smoke block now covers the current host `start -> run -> stop` path against the wx-shell live-command session bridge
- failure reflection now keeps `phase=failed` plus `last_error` visible in published status for start/stop and write-path failures without widening the command architecture

## Execution Plan

1. restate the workflow in product terms and in concrete technical terms
2. make the host-driven `start -> run -> stop` reading explicit before naming the supporting technical controls
3. define the exact host expectations for this workflow in the current phase
4. define the exact shell-reflection and shell-settings expectations for this workflow in the current phase
5. capture the smallest likely implementation seams without widening scope
6. close the package once save-path, run-state, smoke, and failure seams are tightened enough for the current delamination path

## Validation

- verify the package aligns with `docs/STATUS.md` and `docs/WORKPACKAGES.md`
- verify the package does not reopen broad residual or architecture lanes
- verify the package stays consistent with the current functional-workflow framing
- verify the package does not implicitly redefine the workflow as merely a bounded-recording refinement
- verify the final implementation slice leaves one coherent delamination path with understandable start, run, stop, save target, and failure reflection

## Documentation Updates

- `docs/WORKPACKAGES.md`
- `docs/STATUS.md`
- `apps/local_shell/STATUS.md`
- derived views only if the active queue summary later needs them

## Expected Commit Shape

Implementation, tests, and PM/documentation updates are expected together for the closure slice.

## Merge Gate

- the workflow is expressed through the current `Hybrid Companion` product lens
- the workflow is centered on host-driven delamination recording rather than on bounded-recording terminology
- the package closes with understandable host-plus-shell reflection for start, run, stop, save target, and failure state
- the package stays narrow and does not turn into a broad refactor plan
- older residual packages remain visible but no longer dominate next-step selection

## Recovery Note

Resume with:

1. `AGENTS.md`
2. `docs/SESSION_START.md`
3. `docs/MODULE_INDEX.md`
4. `docs/STATUS.md`
5. `docs/WORKPACKAGES.md`
6. this file
