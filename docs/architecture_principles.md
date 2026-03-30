# Architecture Principles

This file captures the durable architecture rules for the repository.

For the compact current architecture map and stable-now boundaries, use:

- `docs/ARCHITECTURE_BASELINE.md`

## Core Principles

- preserve the working Python baseline while introducing clearer platform boundaries
- keep one host-neutral control/application surface as the primary control layer
- separate repository module ownership from temporary physical source-file placement
- keep hardware integration, application services, reusable libraries, and UI/app entry points distinct
- prefer typed request/result objects over ad-hoc dictionaries
- keep reusable analysis foundations independent of OpenCV and UI concerns
- introduce portable contracts early so later C# migration does not depend on Python-specific internals
- treat simulation as a first-class path, not a test-only shortcut
- treat focus evaluation as consumer-driven: stream layers expose frames, while dedicated consumers decide when focus is computed
- treat ROI as reusable geometry and selection data: ROI helpers provide bounds and centroid, while consuming services decide whether to use full-frame or ROI-limited evaluation
- treat viewport fitting, zoom, pan, window sizing, and display-space overlay transforms as UI/display concerns rather than camera-core responsibilities

## Category Rule

- `apps/`: runnable shells and operator/developer entry points
- `integrations/`: external SDK and hardware adapters
- `services/`: orchestration and workflow logic above libraries and integrations
- `libraries/`: reusable contracts, kernels, and technical/domain building blocks

## Boundary Rule

- do not let OpenCV become a core-platform dependency
- do not mix SDK calls into UI code
- do not let CLI, transport, or UI adapters duplicate business logic that belongs in services/control
