# Hardware Evaluation Checklist

## Purpose

This document defines how to validate the Python camera prototype against real hardware.

It is intended to answer:

- does the real camera initialize reliably
- do configuration changes actually take effect
- do snapshot, preview, and recording behave correctly on hardware
- which gaps remain between simulator-backed validation and real-device validation

This checklist should be used before treating the Python prototype as hardware-validated.

Current repository note:

- simulator-backed validation is already strong
- the optional OpenCV preview/save path is already implemented and simulator-tested
- neither of those facts closes Phase 8 or Phase 9 without at least one real-hardware validation pass

## Preconditions

Before starting:

- the target camera is physically connected
- the correct Vimba X environment is installed
- `vmbpy` is installed into the active project virtual environment from the local Vimba X wheel
- the project virtual environment is available
- the camera is visible to the SDK
- the intended camera id is known, for example `example_camera_id` or `device_camera_id`
- a writable output directory is available

Recommended Python executable:

```powershell
.\.venv\Scripts\python.exe
```

## Vimba X Installation Baseline

Use the official Allied Vision Vimba X SDK installation as the hardware access baseline.

Recommended Windows package:

- `VimbaX_Setup-2026-1-Win64.exe`

Typical useful locations after installation:

- Viewer / Driver Installer: `Vimba X/bin`
- Examples: `C:\Users\Public\Documents\Allied Vision\Vimba X`
- Documentation: included in the SDK installation and also available online

Install `VmbPy` from the local wheel that comes with the Vimba X installation:

```powershell
.\.venv\Scripts\python.exe -m pip install "C:\Path\To\vmbpy-X.Y.Z-py-none-any.whl"
```

If needed, optional extras can be installed from that same wheel:

```powershell
.\.venv\Scripts\python.exe -m pip install "C:\Path\To\vmbpy-X.Y.Z-py-none-any.whl[numpy,opencv]"
```

Equivalent project-bootstrap form:

```powershell
.\scripts\bootstrap.ps1 -VmbPyWheel "C:\Path\To\vmbpy-X.Y.Z-py-none-any.whl"
```

Or, if the OpenCV path is also required:

```powershell
.\scripts\bootstrap.ps1 -IncludeOpenCv -VmbPyWheel "C:\Path\To\vmbpy-X.Y.Z-py-none-any.whl"
```

Do not treat a plain PyPI install as sufficient for the full hardware path, because the full Vimba X environment also provides drivers and transport-layer components.

Practical note for new machines:

- the wheel is normally shipped with Vimba X already
- you usually do not build or generate it yourself
- you must install that local SDK-provided wheel into the same `.venv` that runs this repository
- if the wheel path is unclear, search the local Vimba X installation directory for `vmbpy-*.whl`

## First SDK Verification

Before running the checklist below, verify that the SDK can enumerate cameras:

```powershell
.\.venv\Scripts\python.exe -c "from vmbpy import *; \
with VmbSystem.get_instance() as vmb: \
    print(vmb.get_all_cameras())"
```

If cameras are listed, the Vimba X SDK and Python binding are available to the environment used by this project.

## What To Record

For each hardware validation run, record:

- date and operator
- machine name
- camera id
- camera model / serial
- SDK version if known
- test output directory
- tested configuration values
- pass / fail per checklist item
- notes about unexpected behavior

## Evaluation Areas

The minimum real-hardware evaluation should cover:

1. initialization and shutdown
2. camera selection by explicit id
3. configuration application
4. single-frame snapshot save
5. preview acquisition behavior
6. recording behavior
7. failure behavior and unsupported settings

## Recommended Integrated Run

Before or alongside the individual checks below, prefer one integrated hardware-backed command flow that exercises:

- initialize
- optional configuration
- save-directory resolution
- snapshot save
- preview start and first-frame readiness
- interval capture from the shared preview stream
- recording with explicit stop conditions
- shutdown

Recommended command:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_hardware_command_flow.py --base-directory .\captures\hardware_smoke --run-name run_001 --camera-id example_camera_id --pixel-format Mono8 --frame-limit 3 --interval-frame-count 3
```

This integrated run does not replace the checklist below, but it gives one reproducible Phase 9 baseline that can be repeated after code changes.

## Latest Documented Run

Latest integrated run on March 27, 2026:

- machine: current local development machine
- camera id: `DEV_1AB22C046D81`
- camera model: `Allied Vision 1800 U-1240m`
- command path: `.\scripts\launchers\run_hardware_command_flow.py`
- output directory: `captures/hardware_smoke/run_003`
- configuration used: `Mono8`, `frame_limit=3`, `interval_frame_count=3`

Observed result:

- snapshot save passed
- preview readiness passed
- interval capture from the shared preview stream passed
- recording with frame-limit stop passed
- output artifacts were written with plausible file sizes for `4024x3036 Mono8`
- the earlier cleanup-side Vimba X `Invalid Camera` errors seen during `run_001` and `run_002` no longer occurred after the shared-frame-source shutdown ordering and timeout hardening

Still not closed by this run:

- broader configuration matrix coverage
- duration-based hardware recording validation
- target-frame-rate hardware recording validation
- explicit invalid-setting and boundary-case checks

Expanded matrix on March 27, 2026 after that baseline:

- `run_004_duration`: combined hardware run with `Mono8`, `Exposure=10000`, `Gain=3.0`, `ROI=2000x1500`
- `run_005_target_fps`: hardware run with the same configuration and `target_frame_rate=5.0`
- `run_006_duration_only`: duration-only hardware run with the same configuration and `duration_seconds=1.5`
- `mono10_snapshot_test`: successful hardware snapshot with supported alternate pixel format `Mono10` saved as `.raw`

Observed result from the expanded matrix:

- `duration_seconds` is now validated on hardware without a simultaneous frame-limit stop condition
- `target_frame_rate` path executes successfully on hardware and writes the expected file sequence
- exposure, gain, and ROI size changes are reflected in the hardware-backed recording metadata
- this camera exposes `OffsetX` and `OffsetY` only at `0`, so ROI validation on this device is effectively width/height validation at zero offset
- `Mono10` is supported for hardware snapshot capture when saved as `.raw`
- `AcquisitionFrameRate` is present on this camera but not writeable in the tested mode, and the driver currently reports that clearly

Documented hardware-side error checks on March 27, 2026:

- invalid camera id: explicit failure, `No Camera with Id 'DOES_NOT_EXIST' available.`
- unsupported pixel format: explicit failure when trying `Mono16`, with `No Entry associated with 'Mono16'`
- unsupported ROI combination: explicit failure for width `2001`, with device-side increment guidance `not a multiple of 8`

## Current Pass / Fail Matrix

Current baseline for camera `DEV_1AB22C046D81` on March 27, 2026:

| Area | Result | Notes |
| --- | --- | --- |
| Initialization / Shutdown | PASS | Integrated hardware runs completed cleanly after shared-stream cleanup hardening |
| Explicit Camera Selection | PASS | Hardware runs used explicit camera id `DEV_1AB22C046D81` |
| Configuration Application | PASS with device constraint | Exposure, gain, ROI size, `Mono8`, and `Mono10` behaved plausibly; `AcquisitionFrameRate` was present but not writeable in the tested mode |
| Snapshot Save | PASS | `Mono8` and `Mono10` snapshot paths produced plausible files |
| Preview Flow | PASS | Preview readiness succeeded in the integrated hardware flow |
| Recording Flow | PASS | Frame-limit, duration-only, and target-frame-rate recording paths all completed on hardware |
| Error / Boundary Checks | PASS | Invalid camera id, unsupported pixel format, and invalid ROI increment failures were explicit and recoverable |

## 1. Initialization And Shutdown

Goal:

- verify that the real camera can be opened and released cleanly

Check:

- initialization succeeds with the intended camera id
- reported camera metadata is plausible
- shutdown completes without hanging or leaving the camera locked

Expected result:

- no exception during startup or shutdown
- `CameraStatus.is_initialized` becomes true during operation
- camera id, name, model, serial, and interface are populated

## 2. Explicit Camera Selection

Goal:

- verify that the correct device is opened when a specific id is given

Check:

- run the smoke path with an explicit camera id
- compare the returned metadata to the expected device

Recommended command:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_snapshot_smoke.py --camera-id example_camera_id --save-directory .\captures\hardware_smoke
```

Expected result:

- the selected camera is the requested device
- no fallback to a different device happens silently

## 3. Configuration Application

Goal:

- verify that hardware settings can be applied through the prototype contract

Check at least:

- exposure time
- gain if supported
- pixel format if supported
- acquisition frame rate if supported
- ROI offset and ROI size if supported

Recommended evaluation method:

- apply one setting at a time first
- then apply a combined configuration
- inspect logs and saved frames for plausibility

Expected result:

- supported features are applied without error
- unsupported features fail clearly and defensively
- ROI-related settings do not corrupt acquisition

## 4. Snapshot Validation

Goal:

- verify `initialize -> configure -> capture -> save -> shutdown` on real hardware

Check:

- snapshot file is created in the requested directory
- naming is deterministic
- saved image format matches the requested extension
- frame metadata is plausible

Recommended command:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_snapshot_smoke.py --camera-id example_camera_id --save-directory .\captures\hardware_smoke --pixel-format Mono8
```

Expected result:

- file exists after the run
- no timeout during normal operation
- image size and content look plausible

## 5. Preview Validation

Goal:

- verify that the real camera can provide a stable latest-frame stream for preview logic

Check:

- `PreviewService` starts without error
- repeated refreshes return frame metadata
- the latest-frame buffer updates over time
- preview start/stop does not lock the device

Expected result:

- frame ids or timestamps advance over time
- preview can be started and stopped repeatedly
- no stale permanent acquisition state remains after stop

## 6. Recording Validation

Goal:

- verify recording against real hardware instead of the simulator

Check:

- frame-limit stop condition
- duration-based stop condition
- target-frame-rate pacing
- output file sequence
- CSV log metadata
- ROI/exposure metadata presence in the log

Expected result:

- recording files are created in order
- stop conditions terminate the run cleanly
- CSV log is written and readable
- reported frame count is plausible

## 7. Error And Boundary Validation

Goal:

- verify how the prototype behaves under realistic hardware-side problems

Check where practical:

- invalid camera id
- unsupported pixel format
- unsupported ROI combination
- disconnected camera during operation
- frame timeout during snapshot

Expected result:

- errors are explicit
- failures do not silently corrupt state
- the camera can still be shut down cleanly afterwards

## Recommended Test Matrix

Minimum hardware matrix:

- one integrated hardware command-flow run
- one snapshot with default configuration
- one snapshot with explicit exposure and pixel format
- one snapshot with ROI if supported
- one short recording with `max_frame_count`
- one short recording with `duration_seconds`
- one recording with `target_frame_rate`
- one preview start/stop cycle

## Suggested Output Location

Use a repo-local ignored directory so files remain inspectable but untracked:

- `captures/hardware_smoke/`

If needed, create per-run subdirectories such as:

- `captures/hardware_smoke/run_001/`
- `captures/hardware_smoke/run_002/`

## Pass / Fail Rule

Treat hardware evaluation as passed only if:

- initialization and shutdown are stable
- snapshot works on real hardware
- preview acquisition works on real hardware
- recording works on real hardware
- configuration changes behave plausibly
- failures are understandable and recoverable

If any of these are missing, the Python prototype is still only simulator-validated.

## Result Template

Use this template for each run:

```text
Date:
Operator:
Machine:
Camera ID:
Camera Model:
Camera Serial:
Output Directory:

Initialization / Shutdown: PASS | FAIL
Explicit Camera Selection: PASS | FAIL
Configuration Application: PASS | FAIL
Snapshot Save: PASS | FAIL
Preview Flow: PASS | FAIL
Recording Flow: PASS | FAIL
Error / Boundary Checks: PASS | FAIL

Notes:
```

## Next Step After Successful Hardware Validation

If this checklist passes on real hardware, the Python repository can be treated as:

- architecturally validated
- simulator validated
- hardware validated at prototype level

That is the right point to freeze the Python baseline and use it as the handover reference for the later C# phase.

Until then, keep the project status phrased as simulator-validated rather than fully hardware-validated.
