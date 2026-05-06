# Hardware Evaluation Checklist

## Purpose

This document defines how to validate the Python camera prototype against real hardware.

It is intended to answer:

- does the real camera initialize reliably
- do configuration changes actually take effect
- do snapshot, preview, and recording behave correctly on hardware
- which gaps remain between simulator-backed validation and real-device validation

For the tested device capability surface itself, use `docs/HARDWARE_CAPABILITIES.md` alongside this checklist.
For a machine-readable exported profile, see `docs/hardware_profiles/`.

This checklist should be used before treating the Python prototype as hardware-validated.

Current repository note:

- simulator-backed validation is already strong
- the optional OpenCV preview/save path is already implemented and simulator-tested
- neither of those facts closes Phase 8 or Phase 9 without at least one real-hardware validation pass

## Current Hardware Verdict

- current hardware baseline: prototype-level validated on the tested camera path `DEV_1AB22C046D81`
- residual observations: `vmbpyLog <VmbError.NotAvailable: -30>`, raw duplicate SDK visibility for the tested camera id, bounded interval jitter, and timing-sensitive back-to-back CLI reuse observations
- next likely hardware follow-up: only residual-driven narrowing such as remaining lifecycle timing observations or further diagnostics around host-visible device constraints, not broad new hardware exploration

## Current Verified Hardware Status

Current repository position after the March 27 and March 30, 2026 runs:

- the Python camera subsystem can now be treated as hardware-validated at prototype level for the tested camera path `DEV_1AB22C046D81`
- the current integrated baseline has real-device evidence for:
  - preview readiness
  - snapshot
  - bounded recording
  - interval capture
  - host-readable status / polling
  - traceability / recording-log output
  - offline reuse of hardware-generated `BMP` output
- the current hardware status should still be read as `acceptable with residual issues`, not as full hardware closure

The main residuals still under observation are:

- `vmbpyLog <VmbError.NotAvailable: -30>` during otherwise successful runs
- duplicate SDK-visible entries for `DEV_1AB22C046D81` at raw Vimba X enumeration level
- bounded but not perfectly stable interval timing
- remaining timing-sensitive device-reuse observations when separate real-device CLI invocations are fired back-to-back too aggressively

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
- output directory: historical `captures/hardware_smoke/run_003` (cleanup-pruned; later retained evidence lives under `wp26_*` and `wp04_*`)
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

- historical `run_004_duration`: combined hardware run with `Mono8`, `Exposure=10000`, `Gain=3.0`, `ROI=2000x1500`
- historical `run_005_target_fps`: hardware run with the same configuration and `target_frame_rate=5.0`
- historical `run_006_duration_only`: duration-only hardware run with the same configuration and `duration_seconds=1.5`
- historical `mono10_snapshot_test`: successful hardware snapshot with supported alternate pixel format `Mono10` saved as `.raw`

Observed result from the expanded matrix:

- `duration_seconds` is now validated on hardware without a simultaneous frame-limit stop condition
- `target_frame_rate` path executes successfully on hardware and writes the expected file sequence
- exposure, gain, and ROI size changes are reflected in the hardware-backed recording metadata
- this camera exposes `OffsetX` and `OffsetY` only at `0`, so ROI validation on this device is effectively width/height validation at zero offset
- `Mono10` is supported for hardware snapshot capture when saved as `.raw`
- `AcquisitionFrameRate` is read-only by default on this camera, but `AcquisitionFrameRateEnable` is writeable; enabling it makes the frame-rate feature writeable and allows reduced-rate control such as `5.0 -> 4.9991` fps read back from hardware

Documented hardware-side error checks on March 27, 2026:

Latest availability check on April 9, 2026 before `WP87 Hybrid Companion Hardware Workflow Revalidation`:

- attempted command: `.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli status --source hardware --camera-alias tested_camera`
- observed result:
  - failed with `No Camera with Id 'DEV_1AB22C046D81' available.`
  - direct VmbPy enumeration only exposed camera simulators `DEV_Cam1`, `DEV_Cam2`, and `DEV_Cam3`
- interpretation:
  - the documented tested real-hardware path was not attached locally in this session
  - no fresh real-device Hybrid Companion workflow evidence was collected on April 9, 2026
  - simulator-visible Vimba devices do not satisfy the current tested-hardware revalidation requirement

Latest tested-path revalidation on April 10, 2026:

- machine: current local development machine
- camera id: `DEV_1AB22C046D81`
- camera model: `Allied Vision 1800 U-1240m`
- output directories:
  - `captures/hardware_smoke/test_wp87_snapshot`
  - `captures/hardware_smoke/test_wp87_recording`
  - `captures/hardware_smoke/test_wp87_run_001`
- command paths:
  - `.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli status --source hardware --camera-alias tested_camera`
  - `.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli snapshot --source hardware --camera-alias tested_camera --configuration-profile default --base-directory .\captures\hardware_smoke\test_wp87_snapshot --file-extension .bmp`
  - `.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli recording --source hardware --camera-alias tested_camera --configuration-profile default --base-directory .\captures\hardware_smoke\test_wp87_recording --frame-limit 3`
  - `.\.venv\Scripts\python.exe .\scripts\launchers\run_hardware_command_flow.py --base-directory .\captures\hardware_smoke --run-name test_wp87_run_001 --camera-id DEV_1AB22C046D81 --pixel-format Mono8 --frame-limit 3 --interval-frame-count 3`

Observed result:

- hardware-backed `status` succeeded and reported the tested camera path as initialized
- hardware-backed `snapshot` succeeded and wrote `captures\hardware_smoke\test_wp87_snapshot\snapshot_000000.bmp`
- hardware-backed bounded `recording` succeeded and wrote 3 frames to `captures\hardware_smoke\test_wp87_recording`
- the integrated hardware command flow succeeded on the same camera path

Residual observations:

- `vmbpyLog <VmbError.NotAvailable: -30>` still appeared during otherwise successful runs
- the bounded recording path also emitted an `Unexpected access mode change` warning after completion, but the command still returned success

Latest wx camera-settings live-path rerun on May 6, 2026:

- machine: current local development machine
- camera id: `DEV_1AB22C046D81`
- camera model: `Allied Vision 1800 U-1240m`
- command paths:
  - `.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli status --source hardware --camera-alias tested_camera`
  - `.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell --source hardware --camera-alias tested_camera --configuration-profile default --snapshot-directory .\captures\hardware_smoke\wp103_wx_shell_snapshot`
  - `.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell control status`

Observed result:

- hardware-backed `status` succeeded with serial `067WH`, `capabilities_available=true`, and `capability_probe_error=null`
- the wx shell started on the tested hardware path, published live status, and kept preview running with `Mono10`, gain `3`, ROI `0,0,2000,1500`, and the configured save directory
- the real `Camera Settings...` menu path opened the modal dialog in the running shell
- confirming the dialog completed without `failure_reflection`, left preview running, and preserved the full effective configuration in the published status
- follow-up visual inspection in the same May 6, 2026 hardware session confirmed that status-only preview validation was insufficient: the original `Mono10` wx renderer produced an effectively black image because it downshifted all high-bit grayscale formats by 8 bits
- after the display-only high-bit scaling fix, a real wx window screenshot at `captures\hardware_smoke\visible_preview_shell\wx_shell_screenshot.png` showed visible camera content; sampled window pixels had mean brightness `62.31` with `2139/2992` sampled pixels above the visibility threshold

Implementation note from this rerun:

- the fixed exposure value in the shared `default` profile was removed because live capability probes showed state-dependent exposure increments where `10013.862` and `10031.291` can each be valid in different current camera states
- the `default` profile now keeps the stable `Mono10` / gain / ROI baseline and leaves exposure unset
- partial configuration updates now preserve previously known effective configuration fields in status
- `Mono10` / `Mono12` / `Mono14` / `Mono16` rendering now uses format-aware conversion plus display-only contrast stretching for the wx preview path; saved raw/snapshot data is not altered by that UI rendering step

Residual observations:

- `vmbpyLog <VmbError.NotAvailable: -30>` still appeared during otherwise successful hardware status/startup attempts and remains classified as the known non-blocking SDK/logging residual

- invalid camera id: explicit failure, `No Camera with Id 'DOES_NOT_EXIST' available.`
- unsupported pixel format: explicit failure when trying `Mono16`, with `No Entry associated with 'Mono16'`
- unsupported ROI combination: explicit failure for width `2001`, with device-side increment guidance `not a multiple of 8`

Latest bounded revalidation on March 30, 2026:

- machine: current local development machine
- camera id: `DEV_1AB22C046D81`
- camera model: `Allied Vision 1800 U-1240m`
- output directories:
  - `captures/hardware_smoke/wp26_run_001`
  - `captures/hardware_smoke/wp26_run_002`
  - `captures/hardware_smoke/wp26_run_003`
  - `captures/hardware_smoke/wp26_cli_snapshot`
  - `captures/hardware_smoke/wp26_cli_recording`

Bounded evidence covered:

- hardware-backed `status` command on the current CLI host surface
- integrated snapshot + preview + interval capture + bounded recording run through `run_hardware_command_flow.py`
- in-process active polling inspection during interval capture and bounded recording on the same subsystem instance
- second normal save run on the same subsystem instance without process restart
- traceability/logging inspection over generated hardware artifacts
- practical offline reuse by running the current postprocess focus-report path against a hardware-generated `BMP` snapshot
- hardware-backed CLI `snapshot` and bounded `recording` command-result envelopes

Observed result from the March 30, 2026 bounded rerun:

- preview readiness passed on the real device path
- snapshot save passed through both the integrated flow and the current CLI host surface
- bounded recording passed through both the integrated flow and the current CLI host surface
- interval capture passed on the integrated/in-process real-device path
- active host-readable polling was meaningful during real interval capture and real bounded recording, including `active_run` samples for both operation kinds
- traceability and recording-log outputs were written for the generated hardware artifact folders
- hardware-generated `BMP` output remained usable through the current offline focus-report path together with traceability joins
- a second normal save run on the same subsystem instance succeeded without process restart after preview, interval capture, and bounded recording had already completed

Residual observations from the March 30, 2026 bounded rerun:

- successful hardware-backed `status`, `snapshot`, and `recording` runs still emitted a `vmbpyLog <VmbError.NotAvailable: -30>` line during startup or teardown without failing the command
- hardware enumeration exposed duplicate entries for `DEV_1AB22C046D81`, one with serial `067WH` and one with serial `N/A`
- the in-process interval-capture rerun completed successfully but reported `skipped_intervals=1`, so interval timing on the real path should still be treated as boundedly acceptable rather than perfectly scheduler-stable

Latest WP29 startup-warning classification rerun on March 30, 2026:

- fresh serial CLI-host-surface proofs were rerun for:
  - `status`
  - `snapshot(.bmp)`
- both commands completed successfully on `DEV_1AB22C046D81`
- both commands still emitted `vmbpyLog <VmbError.NotAvailable: -30>` on stderr
- the successful `status` and `snapshot` envelopes still reported:
  - `capabilities_available = true`
  - `capability_probe_error = null`
  - `last_error = null`

Current interpretation after WP29:

- the current `NotAvailable: -30` line should be read as non-blocking SDK / logging residual on the successful tested path
- it is not currently evidenced as a capability-probe failure surfaced through the repository status model
- it should therefore remain documented as residual noise under observation, not as proof that startup is failing

Latest WP35 enumeration / startup residual rerun on March 30, 2026:

- raw Vimba X enumeration was rerun on `DEV_1AB22C046D81`
- the SDK still exposed two entries with the same camera id:
  - one entry with serial `067WH`
  - one entry with serial `N/A`
- direct CLI `status` rerun on the same hardware path remained successful and still emitted `vmbpyLog <VmbError.NotAvailable: -30>` on stderr
- an additional direct open-camera probe showed that the richer enumerated camera entry can degrade from serial `067WH` to `N/A` after the SDK camera object is opened

Implemented narrowing after WP35:

- the repository now resolves duplicate SDK-visible entries by camera id and prefers the richer identity candidate during hardware camera selection
- the hardware driver now preserves the richer pre-open identity for host-visible status fields when the opened camera object degrades identity fields such as `camera_serial`

Observed result after WP35:

- hardware-backed CLI `status` on `DEV_1AB22C046D81` now again reports the richer serial `067WH` through the repository status surface
- the duplicate SDK visibility remains a raw SDK-level residual under observation rather than a current host-surface identity defect
- the `NotAvailable: -30` line still remains non-blocking SDK / logging residual on the successful tested path

Latest WP30 interval timing and polling rerun on March 30, 2026:

- one bounded real-device interval-capture rerun with active polling was executed on `DEV_1AB22C046D81`
- configuration used:
  - `interval_seconds = 0.1`
  - `max_frame_count = 3`
  - output directory `captures/hardware_smoke/wp30_interval_capture`
- observed active polling result:
  - `skipped_intervals` rose during timing gaps
  - `last_error` surfaced non-fatal timing warnings during active work
  - the warning cleared again after successful writes
- observed completion result:
  - final status completed successfully with `frames_written = 3`
  - final status reported `skipped_intervals = 7`
  - final status carried the compact completion summary `Interval capture completed with skipped_intervals=7`

Current interpretation after WP30:

- the current interval-capture path should still be treated as boundedly acceptable rather than perfectly scheduler-stable
- however, the polling and completion surfaces are now explicit enough that timing skips no longer have to be inferred only from a bare counter

WP27 lifecycle follow-up on March 30, 2026:

- narrowed the most plausible shared lifecycle seam to capability probing during `CameraService.initialize()`: the real-hardware path previously opened the camera through `VimbaXCameraDriver` and then re-entered Vimba X again through `probe_camera_capabilities(...)`
- the current baseline now probes hardware capability data from the already opened driver camera instead of opening a second Vimba/camera context during initialization
- supporting unit coverage now exists for:
  - open-camera capability serialization
  - driver-side capability probing on the already opened camera
  - `CameraService` preference for driver-provided probe payloads with fallback to the older live-probe path

Observed result from the WP27 serial hardware proof:

- serial `status -> status` on `DEV_1AB22C046D81` succeeded without `camera already in use`
- serial `snapshot -> status` on the same camera id succeeded without `camera already in use`
- serial bounded `recording(frame_limit=5) -> status` on the same camera id also succeeded without `camera already in use`
- proof directories from that slice were later cleanup-pruned; keep this section as documented result rather than retained artifact inventory
- the residual `vmbpyLog <VmbError.NotAvailable: -30>` line was not the target of this slice and may still appear independently of the narrowed reuse result

WP28 capability-aware ROI reporting follow-up on March 30, 2026:

- the current CLI host surface now returns configuration failures during apply-configuration as `configuration_error` instead of only generic `command_error`
- capability-backed ROI width/offset failures now include:
  - requested value
  - camera feature name
  - allowed range
  - required increment and base
  - nearest valid values where practical

Observed result from the WP28 hardware spot-check:

- invalid width request on `DEV_1AB22C046D81`:
  - `roi_width=2001`
  - returned `configuration_error`
  - message included `Width`, range `8..4008`, increment `8`, base `8`, nearest valid values `2000, 2008`
- invalid offset request on `DEV_1AB22C046D81`:
  - `roi_offset_x=17`
  - returned `configuration_error`
  - message included `OffsetX`, range `0..2024`, increment `2`, base `0`, nearest valid values `16, 18`

Additional nuance from the WP28 spot-check:

- one immediately following second CLI invalid-configuration invocation briefly reproduced `camera already in use` before the same offset check was retried successfully after a short pause
- this should be read as a residual timing-sensitive reuse observation, not as a rollback of the WP27 improvement:
  - the targeted WP27 serial proofs still passed
  - the later offset retry produced the intended capability-aware `configuration_error`
  - continued observation is still warranted for tightly back-to-back separate hardware CLI processes

Additional camera-specific rerun on March 30, 2026 against `docs/HARDWARE_CAPABILITIES.md`:

- integrated `Mono8` command-flow rerun with `exposure_time_us=10031.291`, `gain=3.0`, `roi_width=2000`, `roi_height=1500`
- integrated bounded-recording rerun with the same configuration and `target_frame_rate=5.0`
- hardware-backed `Mono10` snapshot rerun to `.raw`
- explicit invalid-setting reruns for unsupported `Mono16` and invalid ROI width `2001`
- bounded CLI snapshot rerun with non-zero ROI offsets `roi_offset_x=16`, `roi_offset_y=4`

Observed result from the camera-specific rerun:

- the combined `Mono8` + exposure + gain + ROI-size path remained hardware-valid
- the bounded `target_frame_rate=5.0` path remained hardware-valid
- `Mono10` snapshot save to `.raw` remained hardware-valid
- unsupported `Mono16` still failed explicitly with `No Entry associated with 'Mono16'`
- invalid ROI width `2001` still failed explicitly against the width increment rule
- non-zero ROI offsets were now also confirmed on hardware through the CLI host path and traceability output, so the earlier assumption that this camera behaved strictly as a size-only ROI target should no longer be treated as current truth

## Current Pass / Fail Matrix

Current baseline for camera `DEV_1AB22C046D81` after the March 27 and March 30, 2026 runs:

| Area | Result | Notes |
| --- | --- | --- |
| Initialization / Shutdown | PASS with narrower reuse confidence | Integrated hardware runs completed cleanly, and the March 30 WP27 serial `status -> status`, `snapshot -> status`, and `recording -> status` proofs no longer reproduced `camera already in use`; successful commands may still emit a `vmbpyLog <VmbError.NotAvailable: -30>` line that remains under observation |
| Explicit Camera Selection | PASS with narrowed residual note | Hardware runs used explicit camera id `DEV_1AB22C046D81`; raw Vimba X enumeration still shows duplicate SDK-visible entries for that same id, but the repository now prefers the richer identity candidate and preserves serial `067WH` on the current host-visible status path |
| Configuration Application | PASS | Exposure, gain, ROI size, `Mono8`, and `Mono10` behaved plausibly; camera-side frame-rate control also works when `AcquisitionFrameRateEnable` is enabled first |
| Snapshot Save | PASS | `Mono8`, `Mono10`, and hardware-backed `BMP` snapshot paths produced plausible files |
| Preview Flow | PASS | Preview readiness succeeded in the integrated hardware flow and in the in-process bounded rerun; the April 7, 2026 bounded OpenCV hardware preview smoke after `WP50` and `WP51` also rendered 5 frames successfully at `2000x1500 Mono8` |
| Recording Flow | PASS | Frame-limit, duration-only, and target-frame-rate recording paths completed on hardware; March 30 also revalidated bounded recording plus active polling on the current host-oriented baseline |
| Interval Capture / Active Polling | PASS with clearer timing semantics | Interval capture completed on hardware, active polling now surfaces non-fatal timing warnings during skipped intervals, and the latest bounded rerun completed with `frames_written=3` and final summary `completed with skipped_intervals=7` |
| Traceability / Offline Reuse | PASS | Traceability logs, recording logs, run linkage, and offline BMP reuse behaved plausibly on hardware-generated output |
| Error / Boundary Checks | PASS | Invalid camera id, unsupported `Mono16`, and invalid ROI increment failures were explicit and recoverable |

Additional March 31, 2026 bounded follow-up:

- alias-backed hardware `snapshot` and bounded `recording` runs through `tested_camera -> DEV_1AB22C046D81` also wrote `camera_alias=tested_camera` into the folder-level stable traceability context while preserving the resolved `camera_id`
- alias-backed hardware `status`, `snapshot`, and bounded `recording` runs through `tested_camera -> DEV_1AB22C046D81` now also resolve and apply the repo-local `default` configuration profile, with traceability headers preserving `configuration_profile_id=default` and resolved `configuration_profile_camera_class=1800_u_1240m`
| Camera-Specific Capability Rerun | PASS with correction | March 30 reruns refreshed the documented `Mono8`, `Mono10`, acquisition-frame-rate, and ROI behavior for `DEV_1AB22C046D81`, and corrected the earlier assumption that ROI offsets were effectively fixed to `0` |

Additional April 7, 2026 bounded architecture revalidation:

- target: real-device confidence after `WP50` display-geometry extraction and `WP51` shared preview-interaction extraction
- serial hardware CLI `status` through `tested_camera -> DEV_1AB22C046D81` succeeded and still reported serial `067WH`
- hardware CLI `snapshot` through `tested_camera` plus profile `default` succeeded and wrote:
  - `captures\hardware_smoke\wp04_revalidation_snapshot\snapshot.bmp`
- integrated hardware command flow succeeded through:
  - `captures\hardware_smoke\wp04_revalidation_run_001`
- bounded OpenCV hardware preview smoke succeeded through:
  - `.\scripts\launchers\run_hardware_preview_demo.py --camera-id DEV_1AB22C046D81 --poll-interval-seconds 0.03 --frame-limit 5`
  - observed result: `Rendered 5 frames.` and final frame info `2000x1500 Mono8`
- `vmbpyLog <VmbError.NotAvailable: -30>` still appeared as non-blocking SDK/logging residual during successful runs
- a parallel start of multiple hardware processes reproduced `camera already in use`, so current hardware validation and CLI checks should continue to run serially on the tested device path

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
- `captures/hardware_smoke/wpXX_manual_block/`

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

At the current documented state, phrase the project as hardware-validated at bounded prototype level on the tested camera path, not as broadly hardware-validated across wider device, stress, or performance matrices. The remaining `VmbError.NotAvailable: -30` line should currently be described as non-blocking SDK/logging residual on the successful tested path unless later evidence shows real startup or capability failure behind it.
