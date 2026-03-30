# Architecture Baseline

## Purpose

This document is the compact architecture reference for the current post-closure Python baseline.

Use it to answer:

- what the current system layers are
- which responsibilities belong where
- how `src/vision_platform` and `src/camera_app` relate today
- which boundaries are stable now versus still intentionally deferred

This is a compact architecture note.

It does not replace:

- `docs/STATUS.md` for current implementation truth
- `docs/WORKPACKAGES.md` for PM sequencing
- module `README.md` and `STATUS.md` for local detail

## Current Architecture Verdict

- current baseline: one usable Python working reference baseline with bounded real-hardware evidence on the tested camera path
- preferred implementation surface: `src/vision_platform/...`
- compatibility surface: `src/camera_app/...`
- control model: one host-neutral command/controller layer with thin CLI and optional adapter surfaces above it
- UI model: OpenCV remains an optional frontend/prototype path, not the platform core

## Layered Model

### Libraries

Role:

- reusable contracts, kernels, and technical/domain building blocks

Examples:

- `libraries/common_models`
- `libraries/roi_core`
- `libraries/focus_core`
- `libraries/tracking_core`

Rules:

- no direct SDK ownership
- no app-shell ownership
- no transport-specific policy unless the module is explicitly about shared contracts

### Integrations

Role:

- external SDK, hardware, and system adapters

Examples:

- `integrations/camera`

Rules:

- real hardware and simulation stay behind the same driver abstraction
- SDK-specific behavior belongs here, not in services or apps

### Services

Role:

- workflow orchestration above libraries and integrations

Examples:

- `services/stream_service`
- `services/recording_service`
- `services/display_service`
- `services/api_service`

Rules:

- services own runtime orchestration, not UI presentation
- services should remain reusable across CLI, OpenCV, and later transport/frontends

### Apps

Role:

- runnable shells and adapter-facing entry points

Examples:

- `apps/camera_cli`
- `apps/opencv_prototype`
- `apps/postprocess_tool`
- `apps/desktop_app`

Rules:

- apps assemble and expose existing platform behavior
- apps should stay thin over services and shared contracts

## Current Control Path

The current bounded control path is:

1. request models and shared contracts
2. command/controller layer
3. camera/stream/recording services
4. driver implementations for hardware or simulation
5. thin adapters such as CLI or later API/frontend shells

Practical meaning:

- business logic should not live in CLI wrappers
- later API or IPC work should reuse the same command/application surface
- current host-oriented behavior is intentionally bounded, not a broad transport contract

Use these docs for the current boundary:

- `docs/HOST_CONTRACT_BASELINE.md`
- `docs/COMMANDS.md`
- `docs/RECORDING_LIFECYCLE_BOUNDARY.md`

## Current Runtime Baseline

The current Python baseline already covers:

- camera initialization on hardware or simulation
- preview/shared acquisition
- snapshot saving
- bounded recording
- bounded interval capture
- traceability and recording-log output
- bounded host polling and confirmed-settings reporting
- offline focus-report reuse of current saved artifacts

This baseline should be read as:

- working and reusable
- intentionally bounded
- still open to selective hardening and selective expansion

## Namespace Mapping

Current practical rule:

- prefer `src/vision_platform/...` for platform-facing implementation and imports
- keep `src/camera_app/...` as compatibility surface while physical relocation remains incremental

Do not read the remaining `camera_app` presence as proof that the architecture is still undefined.

It is a compatibility bridge, not the preferred future-facing namespace.

## Stable Now

The current stable architectural boundaries are:

- one host-neutral control layer remains the primary control surface
- real hardware and simulation stay behind the same driver abstraction
- preview, recording, and saving remain separate concerns
- OpenCV remains optional and frontend-owned
- ROI and focus logic stay reusable outside UI shells
- saved-artifact traceability and bounded offline reuse are part of the current baseline

## Current Intentional Compatibility Bridges

The preferred import and ownership surface is now `src/vision_platform`, but some compatibility bridges remain intentional:

- `src/camera_app.bootstrap`, `src/camera_app.control`, `src/camera_app.imaging`, and `src/camera_app.storage` remain as legacy compatibility shims
- `vision_platform.models` still re-exports a number of model owners that physically remain under `camera_app.models`
- selected `vision_platform` implementation modules still depend on `camera_app` services, validation helpers, or logging helpers where the physical owner has not yet moved
- selected OpenCV prototype app entry points still use the legacy logging helper while now owning their local `DemoRunResult` type inside `vision_platform.apps.opencv_prototype`

These bridges should be read as explicit compatibility seams, not as uncertainty about the preferred namespace.

## Intentionally Deferred

The following are intentionally deferred rather than missing by accident:

- broad transport/API product surface
- detached cross-process recording lifecycle control
- broad frontend expansion beyond the current bounded shells
- larger offline workstation behavior
- broad hardware matrix and stress validation
- C# implementation itself

## Reading Map

Use these adjacent docs by role:

- current truth: `docs/STATUS.md`
- PM queue: `docs/WORKPACKAGES.md`
- operating manual: `docs/PYTHON_BASELINE_RUNBOOK.md`
- launch manual: `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md`
- host boundary: `docs/HOST_CONTRACT_BASELINE.md`
- command vocabulary: `docs/COMMANDS.md`
- module lookup: `docs/MODULE_INDEX.md`
