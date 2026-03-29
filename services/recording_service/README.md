# Recording Service

## Purpose

Handles snapshot saving, interval capture, recording, and deterministic file output without blocking acquisition.

## Responsibility

- snapshot flow
- interval-based single-image capture
- bounded-queue recording pipeline
- file naming and frame writing
- recording status and metadata logs

## Functions

- `SnapshotService`
- `SnapshotFocusService`
- `RecordingService`
- `IntervalCaptureService`
- file naming and frame writing helpers

## Inputs / Outputs

- inputs: requests, save paths, frames, optional camera configuration
- outputs: saved files, recording logs, status objects, optional snapshot-side focus state

Visible output note:

- dependency-free frame writing now covers `.png` and `.bmp` for `Mono8`, `Rgb8`, and `Bgr8`
- optional OpenCV-backed lossless grayscale output remains the path for higher-bit `.png` and `.tiff`
- raw acquisition-oriented export remains available through `.raw` and `.bin`

## Dependencies

- `services/stream_service`
- `integrations/camera`
- `libraries/common_models`

## Implementation Location

- current implementation is split between `src/vision_platform/services/recording_service` and remaining compatibility paths under `src/camera_app/services`
- naming and frame-writing paths already live under `src/vision_platform/services/recording_service`
