# Status

## Source References

This status document should always be read and updated in relation to:

- `docs/ROADMAP.md` for the repository-specific implementation phases
- `GlobalRoadmap.md` for the broader Python -> C# -> web-capable target path

Each status update should state progress and gaps against both roadmaps.

## Current Branch

- `main`

## Roadmap Position

- Against `docs/ROADMAP.md`: Foundation, Camera Access, Snapshot Flow, Preview Flow, Recording Flow, Simulation, Host Integration, and the Python-side optional OpenCV path are functionally implemented. Phase 8 Validation remains partially completed because simulator-backed coverage is strong but real-hardware validation is still open. Phase 9 Real Hardware Evaluation remains open.
- Against `GlobalRoadmap.md`: the Python structuring phase and the simulation path are functionally complete, including the host-neutral command/status contract and the optional Phase 3c OpenCV inspection path. The next mandatory milestone against the global roadmap remains Phase 3b real-hardware evaluation before the Python baseline can be treated as hardware-validated.

## Current Summary

The repository currently provides a structured Python prototype for the camera subsystem with:

- package layout under `src/camera_app/`
- request, configuration, and status models
- `CameraDriver` abstraction
- `VimbaXCameraDriver` initialization, camera selection, configuration, and single-frame capture
- snapshot save flow with explicit target path
- preview service with latest-frame buffering and polling loop
- optional OpenCV imaging adapter for preview-window display and grayscale-safe export
- recording base flow with bounded queue, writer loop, and frame-limit stop condition
- command-controller support for default save-directory resolution and consolidated subsystem status
- `CameraStreamService` as a small orchestration layer for shared live acquisition across preview and recording
- `IntervalCaptureService` for deterministic timed single-image capture from the shared live stream
- `camera_app.bootstrap` as a small composition root for consistently wiring driver, services, stream orchestration, and command controller
- explicit `SubsystemStatus` model with host-facing command readiness flags
- camera status metadata that identifies hardware vs. simulation source kind and active driver name
- external request models for configuration, save-directory changes, snapshot save, and recording start/stop
- camera configuration now models ROI offsets and ROI size in addition to exposure, gain, pixel format, and acquisition frame rate
- recording requests can now carry a target frame rate and log it alongside ROI metadata
- smoke-test entry point for explicit camera id usage such as `example_camera_id`
- command-flow demo for host-style external control using the simulated driver
- a clear architectural basis for separating real hardware drivers from future simulation/demo drivers
- a working simulated driver for hardware-free preview, snapshot, and recording flows
- a shared frame-source path that lets preview and recording consume one acquisition loop together
- optional OpenCV preview demo on top of the simulated preview service
- optional OpenCV-backed lossless grayscale path for `.png` and `.tiff`
- additional service hardening so preview/recording cleanup resets internal state defensively even when acquisition stop fails during recovery

## Completed Work

### Foundation

- package structure created
- core domain models added
- logging setup scaffold added
- file naming scaffold added
- command controller skeleton added

### Camera Access

- camera discovery and initialization implemented
- explicit camera selection by id implemented
- clean shutdown implemented
- configuration application implemented
- single-frame acquisition implemented
- frame metadata model added through `CapturedFrame`
- real hardware currently runs through `VimbaXCameraDriver`
- hardware-free development now runs through `SimulatedCameraDriver`

### Snapshot Flow

- snapshot request to target-path flow implemented
- frame writer added for `.png`, `.raw`, and `.bin`
- frame writer can now use an optional OpenCV adapter for higher-bit grayscale `.png` and `.tiff`
- snapshot logging added
- snapshot smoke-test flow added

### Preview Flow

- preview service start/stop implemented
- latest-frame buffer implemented
- polling-based preview refresh implemented
- preview frame metadata exposure implemented
- optional OpenCV preview window adapter implemented above `PreviewService`

### Recording Flow

- basic producer/consumer pipeline implemented
- bounded queue implemented
- sequential recording file naming implemented
- per-recording CSV log file implemented
- recording log header includes session metadata such as start signal time, stop conditions, save path, and known camera settings
- frame-limit stop condition implemented
- duration-based stop condition implemented
- target-frame-rate pacing implemented for recording requests
- recording state and error tracking implemented

## Partially Implemented

### Recording

- `frame_limit` stop condition is implemented
- `duration_seconds` stop condition is implemented
- both stop conditions can be combined
- `target_frame_rate` can now be provided to pace acquisition in the recording producer loop
- each recording writes a CSV log with image name, frame id, camera timestamp, and system UTC timestamp
- each recording log starts with metadata header lines for start signal time, save path, stop conditions, continuation flag, and known camera settings
- ROI fields in the log header are populated when ROI is present in `CameraConfiguration`
- no trigger-based recording yet
- no hardware-backed continuous acquisition validation yet

### Interval Capture

- `IntervalCaptureService` now supports timed single-image saving from a running shared acquisition
- interval capture uses explicit stop conditions via `max_frame_count`, `duration_seconds`, or explicit stop
- interval capture writes deterministic sequential filenames and can run in parallel with preview on the simulator-backed path
- interval capture is now exposed through bootstrap wiring and the host-facing command controller
- hardware-backed validation is still open

### Host Integration

- command surface exists
- default save directory can now be resolved into snapshot and recording requests
- controller now exposes a typed `SubsystemStatus` model instead of an untyped dictionary
- subsystem status now includes command readiness flags for configuration, snapshot, recording start, and recording stop
- subsystem status now also includes interval-capture status together with start/stop readiness flags
- camera status now exposes whether the active source is `hardware` or `simulation` together with the driver name
- external request types now exist for `ApplyConfigurationRequest`, `SetSaveDirectoryRequest`, `SaveSnapshotRequest`, `StartRecordingRequest`, `StopRecordingRequest`, `StartIntervalCaptureRequest`, and `StopIntervalCaptureRequest`
- save-directory requests now support append-to-directory or create-new-subdirectory behavior
- host-style command flow now covers interval capture from the shared stream in addition to snapshot and recording
- deeper host-specific payload shaping is still open

### Validation

- unit coverage exists for naming, preview, recording, driver integration, and command-controller behavior
- dedicated tests now cover the external request model mappings and save-directory resolution rules
- a simulated command-flow demo now validates a host-style `configure -> set save directory -> snapshot -> interval capture -> recording -> status` sequence
- the direct simulated demo now also validates interval-based single-image saving from the shared stream before recording
- runnable demo entry points exist for both the direct simulated service flow and the command-controller flow
- dedicated tests now cover the optional OpenCV adapter, preview-window bridge, and Mono16 simulated frames
- request and path validation is now hardened for snapshot, recording, file naming, and save-directory commands
- additional tests now cover invalid file stems, unsupported extension shapes, and invalid save-directory subpaths
- preview and recording services now handle repeated stop calls and startup failures more defensively
- additional tests now cover cleanup and stable state recovery when preview thread setup or recording startup fails
- command-controller calls now reject uninitialized camera operations before delegating into snapshot or recording services
- snapshot smoke execution now rejects partially injected service dependencies to avoid inconsistent test and demo wiring
- simulated demo and command-flow demo now return a shared typed result model instead of loosely shaped dictionaries
- frame output validation now rejects unsupported pixel-format and file-extension combinations such as RGB-to-TIFF before writing
- dedicated OpenCV smoke-demo tests now verify the preview and save demo entry points against the simulator-backed path
- preview and recording cleanup now preserve stable service state even when `stop_acquisition()` itself fails during shutdown or recovery
- additional tests now verify that startup failures keep their original exception even if cleanup also fails afterwards
- real hardware validation is still pending separately from the simulator-backed validation

### Preview

- service layer exists and is test-covered
- preview can now run against an optional shared frame source instead of starting an independent acquisition loop
- `CameraStreamService` now exposes that shared-acquisition path as the preferred composition point for live preview plus concurrent recording
- `CameraStreamService` can now also create `IntervalCaptureService` for preview plus timed single-image saving from the same stream
- an optional OpenCV preview window now exists above the service layer
- no browser preview or non-OpenCV UI layer yet
- hardware validation is currently blocked because the camera is not available
- simulated preview exists through `SimulatedCameraDriver`

### Simulation vs. Real Hardware

- architecture now explicitly expects separate real-hardware and simulated driver implementations
- `SimulatedCameraDriver` is implemented for generated frames and `.pgm`/`.ppm` sample image sequences
- a simulated demo entry point exists for preview, snapshot, and recording without hardware
- simulator-backed tests now verify that preview and recording can share one acquisition loop without fighting over the driver
- simulator-backed tests now also verify preview plus timed interval capture from the same shared stream
- simulated generation now also covers `Mono16` frames for grayscale-save-path validation
- sample-image demo support is limited to `.pgm` and `.ppm` files for now
- real hardware validation is still required separately from simulation

### Optional OpenCV Integration

- optional `camera_app.imaging` layer now contains `OpenCvFrameAdapter` and `OpenCvPreviewWindow`
- OpenCV remains outside `CameraDriver` and outside the mandatory core dependency set
- preview display can now run through `cv2.imshow()` on top of `PreviewService`
- lossless grayscale save now supports `.png` and `.tiff` through the optional adapter for `Mono8` and unpacked higher-bit grayscale formats such as `Mono16`
- the standard-library writer remains the default for dependency-free `Mono8`, `Rgb8`, and `Bgr8` PNG output
- packed grayscale formats are still not decoded automatically and should be transformed explicitly before using the OpenCV save path if required
- simulator-backed validation for the optional path is complete, but hardware-backed validation is still pending

## Known Constraints

- hardware is currently not available for live preview validation
- the terminal default `python` points to Python 3.6 on this machine
- project tests should be run with `.\.venv\Scripts\python.exe`

## Verified Test Commands

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_snapshot_service tests.test_frame_writer tests.test_snapshot_smoke tests.test_preview_service tests.test_file_naming tests.test_recording_service tests.test_interval_capture_service tests.test_camera_stream_service tests.test_bootstrap tests.test_simulated_camera_driver tests.test_simulated_demo tests.test_command_flow_demo tests.test_command_controller tests.test_request_models tests.test_opencv_adapter tests.test_opencv_preview tests.test_opencv_smoke_demos
```

## Next Recommended Steps

1. Run a real hardware smoke test again when the target camera is available.
2. Validate the optional OpenCV path with real hardware frames, especially any higher-bit grayscale formats delivered by Vimba X.
3. Decide whether `docs/ROADMAP.md` Phase 8 can be declared complete after one real-hardware validation pass and whether the optional OpenCV path can then be treated as hardware-validated.
4. Define a stricter payload mapping only if the later C# or host integration really needs it.
5. Extend simulation support if needed beyond `.pgm` and `.ppm` sample sequences.
6. Keep the Python core stable as the handover baseline for the later C# phase.
