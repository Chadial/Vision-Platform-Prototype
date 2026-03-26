# Command Manual

## Purpose

This document defines how external control code should formulate commands for the camera subsystem.

The goal is:

- clear request names
- explicit parameters
- minimal hidden behavior
- easy portability from Python to C#

This is a command manual for the application core. It is not tied to a GUI, HTTP API, or any host-specific transport.

## General Rule

Formulate commands as typed request objects.

Prefer:

- one command = one action
- explicit field names
- required values always set by the caller
- optional values only when intentionally overridden

Avoid:

- free-text commands
- hidden defaults that are not visible to the caller
- mixing camera hardware settings with save-path settings in one request

Operational preconditions:

- camera-side commands require an initialized camera service
- snapshot, interval capture, and recording require either an explicit `save_directory` in the request or a previously configured default save directory
- an explicit request `save_directory` overrides the default save directory

## Command Terms

Use these request names for external control:

- `ApplyConfigurationRequest`
- `SetSaveDirectoryRequest`
- `SaveSnapshotRequest`
- `StartRecordingRequest`
- `StopRecordingRequest`
- `StartIntervalCaptureRequest`
- `StopIntervalCaptureRequest`
- `SubsystemStatus`

These names are intentionally neutral. They fit:

- direct Python calls
- a later C# host integration
- a later API or IPC layer

## Request Overview

### `ApplyConfigurationRequest`

Use this request for camera-side hardware settings.

Typical fields:

- `exposure_time_us`
- `gain`
- `pixel_format`
- `acquisition_frame_rate`
- `roi_offset_x`
- `roi_offset_y`
- `roi_width`
- `roi_height`

Use this for:

- shutter / exposure changes
- ROI changes
- camera-side acquisition configuration

Example:

```python
ApplyConfigurationRequest(
    exposure_time_us=2000.0,
    gain=1.5,
    pixel_format="Mono8",
    roi_offset_x=100,
    roi_offset_y=50,
    roi_width=640,
    roi_height=480,
)
```

### `SetSaveDirectoryRequest`

Use this request for storage target control.

Fields:

- `base_directory`
- `mode`
- `subdirectory_name`

Supported `mode` values:

- `"append"`: write directly into `base_directory`
- `"new_subdirectory"`: create or use `base_directory / subdirectory_name`

Use this for:

- externally controlled save paths
- per-run subdirectories
- separating experiments or recordings cleanly

Examples:

```python
SetSaveDirectoryRequest(
    base_directory=Path("captures"),
    mode="append",
)
```

```python
SetSaveDirectoryRequest(
    base_directory=Path("captures"),
    mode="new_subdirectory",
    subdirectory_name="run_001",
)
```

### `SaveSnapshotRequest`

Use this request to save one image.

Fields:

- `file_stem`
- `file_extension`
- `save_directory`
- `create_directories`
- `camera_id`

Notes:

- `save_directory` may be omitted if a default save directory was set earlier.
- `file_stem` should be deterministic and meaningful.

Example:

```python
SaveSnapshotRequest(
    file_stem="snapshot_001",
    file_extension=".png",
)
```

### `StartRecordingRequest`

Use this request to start image-series acquisition.

Fields:

- `file_stem`
- `file_extension`
- `save_directory`
- `max_frame_count`
- `duration_seconds`
- `target_frame_rate`
- `queue_size`
- `create_directories`
- `camera_id`

Stop conditions:

- `max_frame_count`
- `duration_seconds`
- explicit stop via `StopRecordingRequest`

Notes:

- At least one stop condition should be given.
- `target_frame_rate` is a pacing target for recording acquisition.
- `target_frame_rate` does not replace camera-side acquisition settings; it is part of recording control.
- `save_directory` may be omitted if a default save directory was set earlier.

Examples:

```python
StartRecordingRequest(
    file_stem="series_001",
    max_frame_count=300,
    target_frame_rate=25.0,
)
```

```python
StartRecordingRequest(
    file_stem="series_002",
    duration_seconds=10.0,
    target_frame_rate=12.5,
)
```

```python
StartRecordingRequest(
    file_stem="series_003",
    max_frame_count=500,
    duration_seconds=20.0,
    target_frame_rate=20.0,
)
```

### `StopRecordingRequest`

Use this request to stop an active recording explicitly.

Fields:

- `reason`

Example:

```python
StopRecordingRequest(
    reason="external_request",
)
```

### `StartIntervalCaptureRequest`

Use this request to save one frame at a fixed interval from a running live stream.

Fields:

- `file_stem`
- `interval_seconds`
- `file_extension`
- `save_directory`
- `max_frame_count`
- `duration_seconds`
- `create_directories`
- `camera_id`

Stop conditions:

- `max_frame_count`
- `duration_seconds`
- explicit stop via `StopIntervalCaptureRequest`

Notes:

- At least one stop condition should be given.
- `save_directory` may be omitted if a default save directory was set earlier.
- This command is intended for timed single-image capture, not full-rate recording.

Example:

```python
StartIntervalCaptureRequest(
    file_stem="interval",
    interval_seconds=1.0,
    max_frame_count=10,
)
```

### `StopIntervalCaptureRequest`

Use this request to stop an active interval capture explicitly.

Fields:

- `reason`

Example:

```python
StopIntervalCaptureRequest(
    reason="external_request",
)
```

## Recommended Command Sequence

Typical host control sequence:

1. Initialize the camera service.
2. Apply camera configuration.
3. Set or update the save directory.
4. Save a snapshot.
5. Optionally start interval capture when timed single-image saving from the live stream is needed.
6. Start a recording when a full-rate frame series is needed.
7. Poll `SubsystemStatus` when needed.
8. Stop recording or interval capture explicitly if the stop condition is not purely automatic.

Example sequence:

```python
controller.apply_configuration(
    ApplyConfigurationRequest(
        exposure_time_us=1500.0,
        roi_offset_x=0,
        roi_offset_y=0,
        roi_width=1280,
        roi_height=720,
    )
)

controller.set_save_directory(
    SetSaveDirectoryRequest(
        base_directory=Path("captures"),
        mode="new_subdirectory",
        subdirectory_name="test_run_007",
    )
)

controller.save_snapshot(
    SaveSnapshotRequest(
        file_stem="snapshot_before_recording",
    )
)

controller.start_interval_capture(
    StartIntervalCaptureRequest(
        file_stem="interval",
        interval_seconds=1.0,
        max_frame_count=10,
    )
)

controller.start_recording(
    StartRecordingRequest(
        file_stem="recording",
        max_frame_count=200,
        target_frame_rate=10.0,
    )
)
```

## Status Query

Use `SubsystemStatus` as the consolidated status model.

It currently provides:

- `camera`
- `configuration`
- `recording`
- `interval_capture`
- `default_save_directory`
- `can_apply_configuration`
- `can_save_snapshot`
- `can_start_recording`
- `can_stop_recording`
- `can_start_interval_capture`
- `can_stop_interval_capture`

This status model is intended for:

- host integration
- later C# handover
- later transport mapping into JSON, IPC, or API payloads

## Naming Guidance

Use deterministic names.

Prefer:

- `snapshot_001`
- `series_001`
- `run_20260325_001`
- `experiment_A_trial_03`

Avoid:

- `test`
- `image`
- `newfolder`
- names that depend on hidden runtime state

## Separation Rule

Keep these concerns separate:

- hardware configuration via `ApplyConfigurationRequest`
- storage routing via `SetSaveDirectoryRequest`
- one-shot image saving via `SaveSnapshotRequest`
- series acquisition via `StartRecordingRequest`
- stop control via `StopRecordingRequest`
- timed single-image capture via `StartIntervalCaptureRequest`
- interval-capture stop control via `StopIntervalCaptureRequest`

This separation should survive the later C# migration.

## Future Extension Rule

If a later host, API, or C# integration requires strict transport payloads, define them on top of these request terms instead of replacing them.

That means:

- current request classes remain the domain-facing contract
- later JSON or DTO shapes can be mapped from them
- the core service layer should stay transport-agnostic
