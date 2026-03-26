# Stream Service

## Purpose

Owns live acquisition orchestration, preview buffering, and shared-frame distribution without binding to a UI framework.

## Responsibility

- preview start/stop orchestration
- latest-frame access for UI layers
- shared acquisition path for preview plus recording
- future stream fan-out to analysis and API modules

## Functions

- `PreviewService`
- `SharedFrameSource`
- `CameraStreamService`
- `FocusPreviewService`

## Inputs / Outputs

- inputs: camera drivers, polling configuration
- outputs: latest frame info, shared live frames, stream lifecycle state, preview-adjacent focus state

## Dependencies

- `integrations/camera`
- `services/recording_service`
- `libraries/common_models`
