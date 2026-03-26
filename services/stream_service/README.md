# Stream Service

## Purpose

Owns live acquisition orchestration, preview buffering, and shared-frame distribution without binding to a UI framework.

## Responsibility

- preview start/stop orchestration
- latest-frame access for UI layers
- shared acquisition path for preview plus recording
- future stream fan-out to analysis and API modules
- provide frame access to analysis consumers without forcing analysis decisions into the stream layer

## Functions

- `PreviewService`
- `SharedFrameSource`
- `CameraStreamService`
- `FocusPreviewService`
- `RoiStateService`

## Inputs / Outputs

- inputs: camera drivers, polling configuration
- outputs: latest frame info, shared live frames, stream lifecycle state, shared active-ROI state, preview-adjacent focus state via `CameraStreamService` or `FocusPreviewService`

## Analysis Boundary

- `PreviewService` and `CameraStreamService` expose frames and stream lifecycle
- analysis consumers such as `FocusPreviewService` decide when to evaluate a frame
- ROI selection state can be stored in `RoiStateService` and consumed by preview-adjacent analysis without moving ROI ownership into the stream loop or a window class
- ROI and focus logic stay outside the window/rendering classes and outside the core stream loop itself

## Dependencies

- `integrations/camera`
- `services/recording_service`
- `libraries/common_models`
