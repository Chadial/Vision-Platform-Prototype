# WP81 Geometry Capture Workflow Narrowing

## Purpose

Make the confirmed `Geometry Capture` workflow the second workflow-first package, so snapshot-oriented host-plus-shell use is selected through a concrete product workflow instead of through generic technical leftovers.

## Branch

- intended narrow branch: `feature/wp81-geometry-capture-workflow`
- derive the exact implementation branch only when code work begins

## Closure Lane

- `Usable Camera Subsystem / Pre-Product Baseline`

## Slice Role

- workflow-first narrowing
- snapshot-path usability clarification

## Scope

In scope:

- operator-guided overlapping-image acquisition as the workflow reading
- preview
- settings
- snapshot as the technical capture mode used for that workflow
- save-path clarity
- shell reflection of snapshot outcome and current relevant state
- host-side expectations for geometry-capture use in the current phase

Out of scope:

- broad offline measurement tooling
- broad gallery or browser tooling
- broad host-contract expansion
- recording-workflow redesign

## Session Goal

Leave the repository with one execution-ready package for the current `Geometry Capture` workflow after `WP80`.

## Status

Prepared only. Queue directly after `WP80`.

## Execution Plan

1. define the workflow in product terms and technical terms
2. keep geometry capture framed as an operator-guided overlapping-image workflow rather than as generic snapshot work
3. pin the current host-side snapshot expectations
4. pin the current shell reflection and settings expectations
5. capture the smallest implementation seams that would need follow-up

## Validation

- verify consistency with the confirmed functional-workflow set
- verify the package remains narrower than a broad snapshot or offline lane

## Documentation Updates

- `docs/WORKPACKAGES.md` when the queue changes
- `docs/STATUS.md` when it becomes active or landed

## Expected Commit Shape

One PM/documentation commit is preferred.

## Merge Gate

- the package clearly follows `WP80`
- the workflow remains inside the current `Hybrid Companion` phase reading
- no broad measurement or offline scope is reactivated accidentally

## Recovery Note

Resume with:

1. `AGENTS.md`
2. `docs/SESSION_START.md`
3. `docs/MODULE_INDEX.md`
4. `docs/STATUS.md`
5. `docs/WORKPACKAGES.md`
6. this file
