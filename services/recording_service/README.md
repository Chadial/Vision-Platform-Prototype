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

Traceability note:

- snapshot saving and bounded recording now both write into one folder-local appendable traceability log with stable context header, run/session blocks, and per-image rows
- per-image traceability rows now also support optional focus-summary aggregation metadata, with an explicit aggregation-basis field required when summary fields such as `focus_value_mean` or `focus_value_stddev` are stored
- the existing per-recording CSV path remains in place; the traceability log is an additional narrow baseline for host- and offline-readable experiment context

## Dependencies

- `services/stream_service`
- `integrations/camera`
- `libraries/common_models`

## Implementation Location

- current implementation is split between `src/vision_platform/services/recording_service` and remaining compatibility paths under `src/camera_app/services`
- naming and frame-writing paths already live under `src/vision_platform/services/recording_service`
