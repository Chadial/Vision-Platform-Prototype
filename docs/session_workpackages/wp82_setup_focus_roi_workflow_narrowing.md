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

Landed. `WP82` is now complete as one sequence of small sub-packages under the same workflow-first lane rather than as one large setup umbrella.

Closure result:

- the setup workflow now has one explicit host-plus-shell baseline for focus visibility, ROI state, and setup-oriented configuration readability
- shell-visible and host-visible setup state are now readable enough for the current phase without widening settings UI, focus methods, or ROI features
- the workflow-first trilogy is now complete, so future work can be derived from concrete residual seams instead of from an unfinished workflow package

## Sub-Packages

### Landed

#### `WP82.A Setup State Reflection Tightening`

- status: landed
- purpose: make the current setup state readable in shell and published live status through focus visibility, focus summary, ROI state, and configuration summary
- scope:
  - setup-oriented shell prefix cues
  - published live-status reflection for setup state
  - no broad state-model redesign

#### `WP82.B Setup Messaging Tightening`

- status: landed
- purpose: make host-triggered setup changes read as setup work rather than as generic configuration side effects
- scope:
  - tighter setup-oriented apply-configuration messaging
  - no broad wording rewrite across the shell

#### `WP82.C Host-Control Smoke For Setup Path`

- status: landed
- purpose: prove one repeatable host-driven setup block against the current companion-shell baseline
- scope:
  - host applies bounded setup configuration
  - shell/live status reflect focus and ROI-related setup state
  - no new host-surface breadth

#### `WP82.D Setup Failure Reflection Narrowing`

- status: landed
- purpose: keep setup/configuration failures understandable enough in shell and published status without broadening into a new error platform
- scope:
  - configuration-application failure
  - setup-state visibility after failure
  - no retry workflow or broader diagnostics lane

### Ordering Note

Execution order used inside `WP82`:

1. `WP82.A Setup State Reflection Tightening`
2. `WP82.B Setup Messaging Tightening`
3. `WP82.C Host-Control Smoke For Setup Path`
4. `WP82.D Setup Failure Reflection Narrowing`

Landed implementation slices so far:

- the shell status prefix now keeps setup-oriented focus visibility and active ROI shape readable
- the published live shell status now exposes one explicit `setup_reflection` block with focus visibility, focus summary, ROI state, ROI bounds, and configuration summary
- host-triggered configuration changes now read through setup-oriented messaging instead of generic configuration wording
- one repeatable host-control smoke block now covers the current setup path through bounded configuration plus ROI/focus visibility against the wx-shell live-command session bridge

## Execution Plan

1. define the workflow in product terms and technical terms
2. define the setup-workflow boundary for the current phase before selecting any implementation seam
3. pin the current setup expectations for shell-local and host-visible use
4. keep focus value explicitly framed as status rather than as a separate command surface
5. capture the smallest implementation seams that would need follow-up without turning this package into broad settings, shell, focus, or ROI expansion
6. keep future implementation slices inside this workflow small and avoid broad settings, focus-method, or ROI-feature expansion

## Validation

- verify consistency with the confirmed functional-workflow set
- verify the package stays inside current setup usability and does not broaden into broad settings, shell, focus, ROI, analysis, or product-expansion lanes
- verify the final implementation slice leaves one coherent setup path with understandable shell-visible and host-visible focus, ROI, and configuration state

## Documentation Updates

- `docs/WORKPACKAGES.md` when the queue changes
- `docs/STATUS.md` when it becomes active or landed
- `apps/local_shell/STATUS.md` when shell-visible setup state changes materially

## Expected Commit Shape

Implementation, tests, and PM/documentation updates are expected together for the closure slice.

## Merge Gate

- the package clearly follows `WP81`
- the current setup workflow is represented through the `Hybrid Companion` lens
- focus value remains status, not a newly widened command surface
- the package closes with understandable setup-state reflection without becoming a hidden umbrella for wider shell/setup work

## Recovery Note

Resume with:

1. `AGENTS.md`
2. `docs/SESSION_START.md`
3. `docs/MODULE_INDEX.md`
4. `docs/STATUS.md`
5. `docs/WORKPACKAGES.md`
6. this file
