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

- `src/camera_app/drivers`
- `libraries/common_models`

## Usage

The new namespace is `vision_platform.integrations.camera`, currently backed by the stable `camera_app.drivers` implementation.
