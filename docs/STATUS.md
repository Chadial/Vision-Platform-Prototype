# Status

## Source References

This status document should always be read and updated in relation to:

- `docs/ROADMAP.md` for the repository-specific implementation phases
- `GlobalRoadmap.md` for the broader Python -> C# -> web-capable target path

Each status update should state progress and gaps against both roadmaps.

## Current Branch

- `feature/phase-2e-snapshot-smoke`

## Roadmap Position

- Against `docs/ROADMAP.md`: Foundation, Camera Access, Snapshot Flow, Preview Flow, Recording Flow, and the Simulation/Demo path are functionally implemented; Host Integration is partially implemented.
- Against `GlobalRoadmap.md`: the Python structuring phase is functionally complete, including the separated real/simulated driver paths; the next major step is the AMB-facing command/status phase plus real-hardware validation.

## Current Summary

The repository currently provides a structured Python prototype for the camera subsystem with:

- package layout under `src/camera_app/`
- request, configuration, and status models
- `CameraDriver` abstraction
- `VimbaXCameraDriver` initialization, camera selection, configuration, and single-frame capture
- snapshot save flow with explicit target path
- preview service with latest-frame buffering and polling loop
- recording base flow with bounded queue, writer loop, and frame-limit stop condition
- command-controller support for default save-directory resolution and consolidated subsystem status
- smoke-test entry point for explicit camera id usage such as `cam2`
- a clear architectural basis for separating real hardware drivers from future simulation/demo drivers
- a working simulated driver for hardware-free preview, snapshot, and recording flows

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
- snapshot logging added
- snapshot smoke-test flow added

### Preview Flow

- preview service start/stop implemented
- latest-frame buffer implemented
- polling-based preview refresh implemented
- preview frame metadata exposure implemented

### Recording Flow

- basic producer/consumer pipeline implemented
- bounded queue implemented
- sequential recording file naming implemented
- per-recording CSV log file implemented
- recording log header includes session metadata such as start signal time, stop conditions, save path, and known camera settings
- frame-limit stop condition implemented
- duration-based stop condition implemented
- recording state and error tracking implemented

## Partially Implemented

### Recording

- `frame_limit` stop condition is implemented
- `duration_seconds` stop condition is implemented
- both stop conditions can be combined
- each recording writes a CSV log with image name, frame id, camera timestamp, and system UTC timestamp
- each recording log starts with metadata header lines for start signal time, save path, stop conditions, continuation flag, and known camera settings
- ROI fields are reserved in the log header but not populated yet because ROI is not modeled in `CameraConfiguration`
- no trigger-based recording yet
- no hardware-backed continuous acquisition validation yet

### Host Integration

- command surface exists
- default save directory can now be resolved into snapshot and recording requests
- controller now exposes consolidated camera, configuration, recording, and save-directory status
- deeper AMB-specific command/status shaping is still open

### Preview

- service layer exists and is test-covered
- no actual UI preview window or browser preview yet
- hardware validation is currently blocked because the camera is not available
- no simulated preview/image source exists yet

### Simulation vs. Real Hardware

- architecture now explicitly expects separate real-hardware and simulated driver implementations
- `SimulatedCameraDriver` is implemented for generated frames and `.pgm`/`.ppm` sample image sequences
- a simulated demo entry point exists for preview, snapshot, and recording without hardware
- sample-image demo support is limited to `.pgm` and `.ppm` files for now
- real hardware validation is still required separately from simulation

## Known Constraints

- hardware is currently not available for live preview validation
- the terminal default `python` points to Python 3.6 on this machine
- project tests should be run with `.\.venv\Scripts\python.exe`

## Verified Test Commands

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_vimbax_camera_driver
.\.venv\Scripts\python.exe -m unittest tests.test_snapshot_service
.\.venv\Scripts\python.exe -m unittest tests.test_frame_writer
.\.venv\Scripts\python.exe -m unittest tests.test_snapshot_smoke
.\.venv\Scripts\python.exe -m unittest tests.test_preview_service
.\.venv\Scripts\python.exe -m unittest tests.test_file_naming
.\.venv\Scripts\python.exe -m unittest tests.test_recording_service
.\.venv\Scripts\python.exe -m unittest tests.test_simulated_camera_driver
.\.venv\Scripts\python.exe -m unittest tests.test_simulated_demo
.\.venv\Scripts\python.exe -m unittest tests.test_command_controller
```

## Next Recommended Steps

1. Run a real hardware smoke test again when `cam2` is available.
2. Shape the controller/status model further for AMB-facing integration needs.
3. Extend simulation support if needed beyond `.pgm` and `.ppm` sample sequences.
4. Model ROI and additional camera settings if they are needed for the next integration step.
5. Merge to `main` after the current Phase-2 branch is reviewed and accepted.
