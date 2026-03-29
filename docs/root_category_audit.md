# Root Category Audit

## Purpose

This document records the current audit and clarification of the repository root categories:

- `apps/`
- `integrations/`
- `services/`
- `libraries/`

Its purpose is to make category usage understandable for fresh agents and to reduce ambiguity about where new modules or code slices belong.

## Problem Statement

The repository already uses these root categories, but their meaning was introduced early and was not yet strict enough for reliable fresh-agent use.

The key risk is not the existence of the categories themselves, but category drift:

- `services/` turning into a generic catch-all
- `libraries/` overlapping with `services/`
- UI-adjacent code drifting into services or libraries
- adapter code drifting out of `integrations/`

## Current Decision

Keep the four root categories.

Do not reorganize them away at this stage.

Instead, define them strictly and use those rules consistently in docs and later work-package decisions.

Current action outcome:

- no immediate physical module moves are recommended from this audit pass
- the current module fit is good enough to continue with clearer rules
- the main follow-up is disciplined future placement, not broad reclassification churn

## Category Definitions

### `apps/`

Meaning:

- runnable entry points
- operator-facing or developer-facing application shells
- thin app-layer composition around existing services, libraries, and integrations

Belongs here:

- CLI apps
- OpenCV prototype app
- later desktop app
- later postprocess tool

Does not belong here:

- reusable core analysis logic
- driver or SDK integration logic
- business logic that should be shared by multiple frontends

Rule of thumb:

- if the module is something a user or developer starts directly, it is likely an `app`

### `integrations/`

Meaning:

- adapters to external systems, SDKs, hardware, or infrastructure dependencies

Belongs here:

- camera SDK adapters
- simulator drivers that exist to stand in for the real external integration path
- later external actuator or hardware adapters

Does not belong here:

- generic domain logic
- orchestration across multiple modules
- UI-facing preview behavior

Rule of thumb:

- if the module's main reason to exist is “talk to something external”, it belongs in `integrations/`

### `services/`

Meaning:

- application-facing orchestration and workflow coordination
- modules that compose multiple lower-level parts into usable flows

Belongs here:

- preview orchestration
- shared acquisition coordination
- snapshot / recording workflows
- display-payload composition when it coordinates app-facing behavior above pure libraries

Does not belong here:

- pure reusable contracts or kernels
- direct SDK access
- startable app shells

Rule of thumb:

- if the module coordinates work across libraries and integrations to deliver a use case, it belongs in `services/`

### `libraries/`

Meaning:

- reusable core building blocks
- portable contracts, models, and analysis kernels
- logic that should be usable from multiple services, apps, or later external adapters

Belongs here:

- shared models
- ROI geometry and mask logic
- focus evaluation kernels
- later tracking kernels

Does not belong here:

- UI shells
- orchestration-heavy application workflows
- direct external-system adapters

Rule of thumb:

- if the module should remain reusable without caring which app, service, or adapter calls it, it belongs in `libraries/`

## Decision Matrix For Fresh Agents

Ask these questions in order:

1. Is this a directly runnable user/developer entry point?
   - yes: `apps/`
2. Is this primarily an adapter to hardware, SDK, filesystem-side dependency, or another outside system?
   - yes: `integrations/`
3. Is this mainly orchestrating a workflow or use case across other modules?
   - yes: `services/`
4. Is this mainly reusable domain or technical core logic?
   - yes: `libraries/`

If multiple answers appear true:

- prefer `integrations/` over `services/` when the external adapter role dominates
- prefer `libraries/` over `services/` when reuse and kernel logic dominate
- prefer `apps/` only when the module is actually a runnable shell or frontend surface

## Current Module Fit Assessment

### Strong Fit

These modules fit their current root category well:

- `apps/camera_cli`
- `apps/opencv_prototype`
- `integrations/camera`
- `libraries/common_models`
- `libraries/roi_core`
- `libraries/focus_core`
- `libraries/tracking_core`
- `services/stream_service`
- `services/recording_service`

### Acceptable But Watch Closely

- `services/display_service`
  - acceptable as a service because it currently coordinates display-facing payload composition above raw libraries
  - should stay out of UI shell behavior and out of camera/integration logic
- `services/api_service`
  - acceptable as a prepared service because it is intended as an adapter-facing service layer above the shared control path
  - should not become a second core business-logic stack
- `apps/postprocess_tool`
  - acceptable as an app because it is intended to be a user/developer-invoked offline tool
- `apps/desktop_app`
  - acceptable as an app because it is intended as a future frontend shell

## Immediate Category Outcome

From the current repository state:

- `services/display_service` stays in `services/`
  - reason: it currently coordinates application-facing display payload composition rather than exposing a purely generic kernel
- `services/api_service` stays in `services/`
  - reason: it is intended as an adapter-facing service boundary above the host-neutral control path, not as a low-level integration module
- `apps/postprocess_tool` stays in `apps/`
  - reason: it is intended as a user- or developer-invoked offline tool
- `apps/desktop_app` stays in `apps/`
  - reason: it is intended as a frontend shell, not as reusable core logic

No current module shows a strong enough mismatch to justify an immediate move.

If later work changes their role materially, re-run this audit before moving code.

## Known Category Traps

### `services/` vs `libraries/`

Common mistake:

- putting reusable kernels into `services/`

Counter-rule:

- if the logic should survive reuse by multiple services or later C# handover without app-specific workflow assumptions, prefer `libraries/`

### `apps/` vs `services/`

Common mistake:

- letting CLI or OpenCV app layers accumulate unique business logic

Counter-rule:

- `apps/` should compose and expose workflows, not become the only place where those workflows exist

### `integrations/` vs `services/`

Common mistake:

- mixing SDK-specific behavior with orchestration logic

Counter-rule:

- SDK or hardware specifics belong in `integrations/`
- orchestration across preview/recording/snapshot/status belongs in `services/`

## Non-Goals

This audit does not propose:

- renaming the root categories
- introducing new top-level buckets
- moving modules immediately just because the category language was previously unclear

The goal is first to stabilize understanding, then decide later whether any physical moves are still needed.
