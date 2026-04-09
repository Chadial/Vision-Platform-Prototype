# WP82 Setup Focus ROI Workflow Narrowing

## Purpose

Make the confirmed `Setup / Focus / ROI Adjustment` workflow the third workflow-first package, so setup usability is treated as part of the current product direction rather than as scattered ROI/focus residual work.

## Branch

- intended narrow branch: `feature/wp82-setup-focus-roi-workflow`
- derive the exact implementation branch only when code work begins

## Closure Lane

- `Usable Camera Subsystem / Pre-Product Baseline`

## Slice Role

- workflow-first narrowing
- setup-path usability clarification

## Boundary Reading

This package should be read as a setup-workflow boundary definition first.

It exists to clarify:

- which setup actions are actually required in the current phase
- which settings, focus, and ROI state must be visible
- what must remain shell-local while the companion shell stays locally adjustable
- what must be host-visible in the current phase

It does not automatically authorize:

- full settings-UI expansion
- broad shell redesign
- focus-method expansion
- ROI-feature expansion
- freehand ROI expansion
- broad analysis or product breadth

Future implementation slices must still choose the smallest seam inside this workflow.

## Scope

In scope:

- preview
- only the settings visibility and setup actions required for the current phase
- ROI/focus
- focus value as status
- ROI-related state visibility
- optional control snapshot
- shell-local adjustability plus host-visible relevant state in the current phase
- workflow-boundary clarification for the current setup path before any larger feature slice is chosen

Out of scope:

- broad settings-menu work
- broad shell redesign
- focus-method expansion
- ROI-feature expansion beyond the current setup workflow need
- freehand ROI expansion
- broad analysis expansion
- tracking expansion
- product-breadth expansion

## Session Goal

Leave the repository with one execution-ready package for the current setup workflow after `WP81`, while keeping that workflow narrow enough that it does not become a hidden umbrella for remaining shell/setup wishes.

## Status

Prepared only. Queue directly after `WP81`.

## Execution Plan

1. define the workflow in product terms and technical terms
2. define the setup-workflow boundary for the current phase before selecting any implementation seam
3. pin the current setup expectations for shell-local and host-visible use
4. keep focus value explicitly framed as status rather than as a separate command surface
5. capture the smallest implementation seams that would need follow-up without turning this package into broad settings, shell, focus, or ROI expansion

## Validation

- verify consistency with the confirmed functional-workflow set
- verify the package stays inside current setup usability and does not broaden into broad settings, shell, focus, ROI, analysis, or product-expansion lanes

## Documentation Updates

- `docs/WORKPACKAGES.md` when the queue changes
- `docs/STATUS.md` when it becomes active or landed

## Expected Commit Shape

One PM/documentation commit is preferred.

## Merge Gate

- the package clearly follows `WP81`
- the current setup workflow is represented through the `Hybrid Companion` lens
- focus value remains status, not a newly widened command surface
- the package still reads as a narrow workflow-boundary definition rather than as a hidden umbrella for wider shell/setup work

## Recovery Note

Resume with:

1. `AGENTS.md`
2. `docs/SESSION_START.md`
3. `docs/MODULE_INDEX.md`
4. `docs/STATUS.md`
5. `docs/WORKPACKAGES.md`
6. this file
