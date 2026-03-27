# Project Overview

## Purpose

This repository is being reorganized from a camera-subsystem prototype into a modular vision platform. The existing Python prototype remains the executable baseline, but the repository structure now reflects broader platform modules defined in `docs/ProjectDescription.md`.

## Active Platform Modules

- `integrations/camera`: camera SDK adapters and simulation path
- `services/stream_service`: live acquisition, preview buffering, shared frame source
- `services/recording_service`: snapshot, interval capture, recording, deterministic persistence
- `apps/opencv_prototype`: current runnable prototype and smoke/demo entry points
- `libraries/common_models`: portable shared contracts for future cross-module and C# handover
- `libraries/roi_core`: ROI geometry helpers for overlays and analysis consumers
- `libraries/focus_core`: focus-analysis baseline with overlay-ready result mapping

## Prepared Platform Modules

- `libraries/tracking_core`
- `services/api_service`
- `apps/postprocess_tool`
- `apps/desktop_app`

## Code Mapping In This Reorganization Round

- stable implementation remains in `src/camera_app`
- new platform-facing import surface is introduced in `src/vision_platform`
- repository-level module folders now own roadmap/status/readme documents
- runnable app access remains available through the existing root scripts and new `apps/opencv_prototype` wrappers

## Operational Governance

- `docs/git_strategy.md` defines the required branch and commit discipline
- `docs/branch_backlog.md` assigns unfinished worktree changes to future branches
- repository reorganization work should use those two documents before new commits are created from mixed local states

## Architectural Direction

- keep hardware access isolated
- keep stream and recording orchestration separate
- avoid UI-coupled core logic
- introduce shared, portable models before analysis and API expansion
- keep focus consumer-driven and ROI geometry reusable across consumers
- retain Python pragmatism while preparing a later C# handover
