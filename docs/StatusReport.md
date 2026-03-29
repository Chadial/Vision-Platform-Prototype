# Status Report

## Purpose

This document provides a compact MVP-oriented status view of the repository:

- what the project can already do
- what is only partially available
- what is still missing

It is a reader-friendly summary derived from:

- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- archived session work packages under `docs/archive/session_workpackages/`

For the detailed verified implementation truth, `docs/STATUS.md` remains authoritative.

## Current MVP Summary

The current MVP is a Python-first vision-platform prototype with:

- a stable shared camera/control core
- simulator-backed and hardware-capable acquisition paths
- a host-neutral command surface
- a thin CLI for core camera operations
- an OpenCV-based prototype frontend for local preview/operator work
- first reusable analysis kernels for ROI, focus, and tracking
- first preparation slices for API and offline postprocess reuse

This is an architectural and workflow MVP, not a production-ready end-user product.

## Implemented And Usable Today

### Camera And Acquisition

- camera initialization and camera selection by id
- camera configuration for exposure, gain, pixel format, frame rate, and ROI geometry
- single-image snapshot saving
- bounded recording with frame-limit and duration stop conditions
- bounded interval capture from the shared preview/acquisition path
- explicit save-directory handling and deterministic file naming
- simulator-backed camera driver for hardware-free development
- historically validated real-hardware path for the tested Allied Vision camera baseline

### Shared Command And Control Surface

- one host-neutral command/controller surface
- typed request, result, and status models
- consolidated `SubsystemStatus` with readiness flags
- typed command outcomes for configuration, save-directory, snapshot, recording, and interval capture
- capability-aware configuration validation with soft fallback when hardware probing is unavailable

### CLI Baseline

- unified CLI under `vision_platform.apps.camera_cli`
- subcommands:
  - `status`
  - `snapshot`
  - `recording`
  - `interval-capture`
- simulator-first JSON output suitable for developer/operator shell use
- deliberate MVP boundary limited to `Capture`, `Camera`, and `Storage`

### OpenCV Prototype Frontend

- live preview over the shared preview path
- fit-to-window and zoom
- pan and cursor-anchored zoom
- bottom status band and FPS display
- point selection and coordinate copy
- first operator-facing ROI creation baseline for rectangle and ellipse
- preview-frame snapshot shortcut through explicit save-directory configuration
- capability-aware shortcut hints

### Analysis Foundations

- ROI bounds, centroid, pixel bounds, rectangle/ellipse masks
- Laplace focus metric
- Tenengrad focus metric
- preview- and snapshot-side focus consumers
- overlay payload composition without binding to a concrete UI renderer
- first tracking-core baseline through edge/profile analysis

### API And Offline Preparation

- first transport-neutral API status payload family above `SubsystemStatus`
- first offline postprocess baseline through stored-image focus reporting for `.pgm` / `.ppm`

## Partially Implemented Or Intentionally Narrow

### Hardware

- hardware validation exists for the earlier tested camera baseline
- fresh hardware revalidation is still pending for the latest integrated repository state
- current development assumptions should remain simulator-first until the camera is explicitly retested

### CLI

- the CLI is intentionally narrow
- no ROI command group
- no analysis command group
- no preview/view concerns

### API

- no HTTP, IPC, or feed transport
- no full external adapter implementation
- only the first DTO/mapping preparation slice exists

### Postprocess

- only one small offline focus-report path exists
- no broad workstation behavior
- no richer export pipeline
- no metadata-join or batch analysis framework

### Tracking

- only the first edge/profile baseline exists
- no drift tracking or richer temporal tracking behavior yet

### Handover Hardening

- important request/result boundaries are now more explicit for later C# porting
- there is still no actual C# implementation in this repository

## Missing For A Larger Product Scope

- production-ready API surface
- broader offline/postprocess application
- additional desktop or web-capable frontend shells
- richer ROI editing such as freehand ROI
- more advanced focus/analysis orchestration
- richer tracking/drift behavior
- broader real-hardware regression coverage
- packaging, release, CI, installer, and deployment hardening
- actual C#/.NET codebase or parallel implementation

## Suggested MVP Test Paths

The current MVP can be checked through these kinds of entry points:

- CLI baseline:
  - `python -m vision_platform.apps.camera_cli status`
  - `python -m vision_platform.apps.camera_cli snapshot ...`
- OpenCV prototype:
  - preview and operator demos under `src/vision_platform/apps/opencv_prototype`
- offline postprocess baseline:
  - `python -m vision_platform.apps.postprocess_tool <sample_dir>`

And through the already verified local regression blocks:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_camera_cli tests.test_command_controller tests.test_bootstrap
.\.venv\Scripts\python.exe -m unittest tests.test_focus_core tests.test_tracking_core tests.test_postprocess_tool tests.test_vision_platform_namespace
.\.venv\Scripts\python.exe -m unittest tests.test_opencv_preview tests.test_opencv_smoke_demos
```

## Practical Conclusion

The project already has a credible technical MVP for:

- camera control and acquisition
- thin external control through one shared command surface
- local CLI execution of core operations
- local operator-facing OpenCV preview experiments
- first reusable analysis kernels
- first API and offline reuse preparation

The project does not yet have a production-ready integration platform, full offline workstation, or expanded frontend ecosystem.
