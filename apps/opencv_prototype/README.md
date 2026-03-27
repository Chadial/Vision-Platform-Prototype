# OpenCV Prototype

## Purpose

Provides the current runnable prototype entry points for local preview inspection, snapshot/save checks, simulator-backed workflow validation, and the first viewport-based hardware preview path.

## Responsibility

- expose a lightweight app layer above the existing service core
- keep OpenCV-specific behavior out of hardware drivers and core services
- preserve a startable prototype while the repository becomes more modular

## Functions

- OpenCV preview demo
- OpenCV preview demo with optional focus-state composition
- hardware preview demo with fit-to-window and zoom controls
- overlay-payload demo that composes active ROI plus preview/snapshot focus and prints a console summary
- OpenCV save demo
- simulated end-to-end demo
- simulated preview-to-focus smoke demo
- host-style command flow demo

## Inputs / Outputs

- inputs: simulator frames or camera-backed frames, CLI arguments, explicit save paths
- outputs: preview windows, viewport-based preview rendering, saved image files, capture folders, console summaries

## Dependencies

- `src/camera_app/smoke`
- `src/camera_app/imaging`
- `services/stream_service`
- `services/recording_service`

## Usage

Prefer the package entry points under `python -m vision_platform.apps.opencv_prototype...` or the existing root helper scripts such as `run_focus_preview_demo.py` and `run_hardware_preview_demo.py`.
