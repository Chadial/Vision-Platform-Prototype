# OpenCV Prototype

## Purpose

Provides the current runnable prototype entry points for local preview inspection, snapshot/save checks, and simulator-backed workflow validation.

## Responsibility

- expose a lightweight app layer above the existing service core
- keep OpenCV-specific behavior out of hardware drivers and core services
- preserve a startable prototype while the repository becomes more modular

## Functions

- OpenCV preview demo
- OpenCV save demo
- simulated end-to-end demo
- host-style command flow demo

## Inputs / Outputs

- inputs: simulator frames or camera-backed frames, CLI arguments, explicit save paths
- outputs: preview windows, saved image files, capture folders, console summaries

## Dependencies

- `src/camera_app/smoke`
- `src/camera_app/imaging`
- `services/stream_service`
- `services/recording_service`

## Usage

Prefer the package entry points under `python -m vision_platform.apps.opencv_prototype...` or the existing root helper scripts.
