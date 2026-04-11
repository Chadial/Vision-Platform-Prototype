# WP83 Host Result And Status Surface Consistency Narrowing

## Purpose

Make the current Stage-1 host surface easier to consume by tightening one concrete inconsistency between live command results and published shell status, without widening the transport or redesigning the host contract.

## Branch

- intended narrow branch: `feature/wp83-host-status-surface-consistency`
- derive the exact implementation branch only when code work begins

## Closure Lane

- `Usable Camera Subsystem / Pre-Product Baseline`

## Slice Role

- host-surface consistency narrowing
- command-result readability clarification

## Scope

In scope:

- one narrow consistency seam between live command results and published shell status
- result readability for the current host-triggered `apply_configuration`, `save_snapshot`, `start_recording`, and `stop_recording` path
- reflection-aligned result shaping without widening transport scope
- one small smoke/proof block for the tightened result reading

Out of scope:

- broad transport redesign
- broad host-envelope redesign
- LabVIEW-specific transport work
- new runtime/session architecture
- broad naming churn outside the selected seam

## Session Goal

Leave the repository with one execution-ready package that makes the current host command results read through the same reflection model the shell already publishes in status.

## Status

Landed. `WP83` is now complete as one sequence of small sub-packages under the same post-workflow-first host-surface lane.

## Sub-Packages

### Landed

#### `WP83.A Reflection-Aligned Command Result Envelope`

- status: landed
- purpose: return one reflection-aligned subset in live command results so the host does not need to infer current state from unrelated raw result shapes
- scope:
  - `apply_configuration`
  - `save_snapshot`
  - `start_recording`
  - `stop_recording`

#### `WP83.B Save-Directory Result Consistency`

- status: landed
- purpose: keep `set_save_directory` readable through the same command-result lens instead of as a special ad-hoc result
- scope:
  - selected save directory
  - no storage-policy redesign

#### `WP83.C Host-Control Smoke For Result Reading`

- status: landed
- purpose: prove one repeatable host path where command results and published status agree on the same reflection reading
- scope:
  - command result
  - status snapshot
  - no broad integration harness

#### `WP83.D Failure Result Consistency Narrowing`

- status: landed
- purpose: keep command failures readable enough through the same host-result lens without broadening into a new error platform
- scope:
  - current failure ownership only
  - no retry or transport changes

### Ordering Note

Execution order used inside `WP83`:

1. `WP83.A Reflection-Aligned Command Result Envelope`
2. `WP83.B Save-Directory Result Consistency`
3. `WP83.C Host-Control Smoke For Result Reading`
4. `WP83.D Failure Result Consistency Narrowing`

Landed implementation slices so far:

- live command results now expose one additive `reflection_kind` plus `reflection` subset aligned with the existing published status reflections
- `set_save_directory` now follows the same result-reading pattern through one explicit save-directory reflection
- one repeatable host smoke block now proves that command result and published status can be read through the same reflection model
- failed command-result files now also keep one minimal command/result placeholder shape instead of collapsing to a bare error string only

## Execution Plan

1. identify the smallest concrete inconsistency between command results and published shell status
2. tighten that inconsistency through one reflection-aligned result subset
3. keep the current host surface additive and backward-compatible where practical
4. prove the new reading through one small host-control smoke block
5. avoid widening into broad contract redesign

## Validation

- verify the package stays inside one narrow host-surface consistency seam
- verify command results and published status can now be read through the same reflection model for the touched commands
- verify the package remains additive and does not widen transport/runtime scope

## Documentation Updates

- `docs/WORKPACKAGES.md` when the queue changes
- `docs/STATUS.md` when it becomes active or landed
- `apps/local_shell/STATUS.md` when host-surface behavior changes materially

## Expected Commit Shape

Implementation, tests, and PM/documentation updates are expected together for the closure slice.

## Merge Gate

- the package stays inside one narrow host-result consistency seam
- the touched command results now expose one reflection-aligned reading
- the package remains additive and does not become a broad host-contract redesign

## Recovery Note

Resume with:

1. `AGENTS.md`
2. `docs/SESSION_START.md`
3. `docs/MODULE_INDEX.md`
4. `docs/STATUS.md`
5. `docs/WORKPACKAGES.md`
6. this file
