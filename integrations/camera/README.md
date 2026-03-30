# Camera Integration

## Purpose

Contains camera-SDK-facing integration concerns and isolates real hardware access from the rest of the platform.

## Responsibility

- driver abstractions
- Allied Vision / Vimba X integration
- simulated camera path for hardware-free development

## Functions

- initialize and shut down cameras
- apply camera configuration
- acquire frames
- distinguish hardware and simulation sources

## Inputs / Outputs

- inputs: camera ids, configuration objects, SDK handles
- outputs: captured frames, camera status, initialization failures

## Dependencies

- `src/vision_platform/integrations/camera`
- `libraries/common_models`

## Usage

Prefer the `vision_platform.integrations.camera` namespace.

## Implementation Location

- current platform-owned driver implementations live under `src/vision_platform/integrations/camera`
- legacy compatibility imports may still bridge through `src/camera_app` in some paths
