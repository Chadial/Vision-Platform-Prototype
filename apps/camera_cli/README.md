# Camera CLI

## Purpose

Provides a camera-oriented command-line app surface for exercising the existing platform services without depending on the OpenCV preview path.

## Responsibility

- expose one coherent CLI entry command for camera operations
- reuse command-controller and service-layer contracts instead of ad-hoc script logic
- keep storage, camera configuration, and bounded capture options explicit
- keep CLI concerns separate from preview/UI-specific prototype behavior
- remain a thin local adapter above the shared host-neutral control layer rather than becoming a second business-logic path

## Functions

- consolidated `status` command
- consolidated `snapshot` command
- consolidated bounded `recording` command
- consolidated bounded `interval-capture` command
- simulator-backed and hardware-backed source selection

## Inputs / Outputs

- inputs: CLI arguments for camera source, camera id, configuration, save-directory behavior, and bounded capture options
- outputs: saved image or recording artifacts plus JSON command summaries on stdout

## Dependencies

- `integrations/camera`
- `services/stream_service`
- `services/recording_service`
- `src/vision_platform/control`

## Usage

Prefer the package entry point:

- `python -m vision_platform.apps.camera_cli`

Or use the launcher:

- `scripts/launchers/run_camera_cli.py`

## Implementation Location

- app entry points currently live under `src/vision_platform/apps/camera_cli`
