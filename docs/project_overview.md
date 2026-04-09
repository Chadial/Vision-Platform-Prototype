# Project Overview

## Purpose

This repository now operates from `Usable Camera Subsystem / Pre-Product Baseline` while preserving a modular vision-platform structure for later expansion and handover.

Use this document as a compact repository-level overview.

For architecture detail, use:

- `docs/ARCHITECTURE_BASELINE.md`

## Active Platform Modules

- `integrations/camera`: camera SDK adapters and simulation path
- `services/stream_service`: live acquisition, preview buffering, shared frame source
- `services/recording_service`: snapshot, interval capture, recording, deterministic persistence
- `apps/opencv_prototype`: current runnable prototype and smoke/demo entry points
- `libraries/common_models`: portable shared contracts for future cross-module and C# handover
- `libraries/roi_core`: ROI geometry helpers for overlays and analysis consumers
- `libraries/focus_core`: focus-analysis baseline with overlay-ready result mapping

## Active Supporting Modules

- `libraries/tracking_core`
- `services/api_service`
- `apps/postprocess_tool`

## Prepared Later Modules

- `apps/desktop_app`

## Code Mapping

- preferred platform-facing import surface: `src/vision_platform`
- compatibility bridge: `src/camera_app`
- repository-level module folders own local `README.md`, `STATUS.md`, and optional `ROADMAP.md`
- runnable app access remains available through package entry points and bounded launcher scripts

## Current Working Baseline

- host-steerable running `Vision App / wxShell` in `Hybrid Companion` form
- bounded host-oriented command surface
- snapshot, preview, bounded recording, and bounded interval capture
- traceability and recording-log output
- optional OpenCV prototype path for local preview/inspection
- bounded real-hardware validation on the tested camera path
- bounded offline follow-up through the current postprocess baseline

## Operating References

- `docs/MANUALS_INDEX.md`
- `docs/PYTHON_BASELINE_RUNBOOK.md`
- `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md`
- `docs/HOST_CONTRACT_BASELINE.md`

## Planning And Governance References

- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- `docs/ROADMAP.md`
- `docs/GlobalRoadmap.md`
- `docs/git_strategy.md`
