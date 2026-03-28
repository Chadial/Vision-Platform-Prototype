# Next Session Order

## Purpose

This document is the short decision guide for what agents should normally work on next.

Use it when a new session starts and the next task is not already explicitly assigned by the user.

It is intentionally narrower than `docs/ROADMAP.md` and more directive than `docs/STATUS.md`.

## Core Rule

Prefer the next unfinished item in this order unless the user explicitly redirects the session.

Do not skip ahead to later adapter or frontend work just because it is interesting.

## Default Work Order

1. Finish and narrow the active `feature/camera-cli` work to a small, stable CLI baseline.
2. After the CLI baseline is stable, define and implement one host-integration work package that hardens the shared host-neutral command surface.
3. Only after that, prepare `services/api_service` as an external adapter over the same host-neutral control layer.
4. Keep the OpenCV prototype work separate as UI/display work; do not let it become the main control architecture.
5. Revisit broader hardware validation when the camera is available again.

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

## Session Startup Instruction

When a new session begins and the user asks generally what to do next:

1. read `AGENTS.md`
2. read `docs/SESSION_START.md`
3. read `docs/MODULE_INDEX.md`
4. read this file
5. propose the highest-priority unfinished item from this order before asking broad open-ended planning questions

## Current Default Recommendation

If no stronger user direction is given, the next recommended path is:

1. treat the CLI baseline as intentionally narrow and stable unless a clear defect appears
2. use `docs/session_workpackages/host_integration_command_surface.md` to execute the next dedicated host-integration work package
3. only then move toward API/feed adapter work
