# Next Session Order

## Purpose

This document is retained as a legacy quick-reference.

Use `docs/WORKPACKAGES.md` as the primary current source for what agents should work on next.

This file should only remain as a lightweight compatibility pointer until any remaining references are removed.

## Current Rule

When the next task is not already explicit:

1. read `AGENTS.md`
2. read `docs/SESSION_START.md`
3. read `docs/MODULE_INDEX.md`
4. read `docs/WORKPACKAGES.md`
5. use `docs/STATUS.md` if implementation reality needs to be confirmed

## Interpretation Rules

### CLI

- `apps/camera_cli` is a local adapter for shell usage, smoke tests, and developer/operator command execution
- it must stay thin over the shared control/application layer
- it must not accumulate unique business logic that later API or host integrations would need to duplicate

### Host Integration

- the host-neutral command/controller surface is the real long-term control path
- this is the layer that should be made clearer for later C# embedding, desktop integration, and future external adapters
- prefer explicit request, result, and status models over ad-hoc output shapes

### API

- `services/api_service` is not the next primary architecture step
- it should come after the host-neutral command surface is clarified
- it should reuse the shared control/application layer instead of creating a second business-logic stack

### OpenCV

- keep OpenCV work in the UI/display lane
- viewport behavior, operator controls, overlays, and preview ergonomics stay there
- do not use OpenCV work to define the platform's primary command architecture

## Current Default Recommendation

If no stronger user direction is given, the next recommended path is:

1. execute the package marked `current next` in `docs/WORKPACKAGES.md`
2. if no package is marked `current next`, derive the next smallest justified post-closure slice from concrete residuals or the user's explicit direction
3. then open that package's detailed `docs/session_workpackages/wpXX_*.md` file for actual execution and progress tracking
4. use session work-package files as the detailed execution layer, not as the primary prioritization surface
5. only consult `docs/ROADMAP.md` or `docs/GlobalRoadmap.md` when higher-level sequencing needs clarification
