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

## Dependencies

- `services/stream_service`
- `integrations/camera`
- `libraries/common_models`
