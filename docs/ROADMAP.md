# Roadmap

## Purpose

This roadmap reflects the actual implementation flow reconstructed from the current Python repository state.

It is intentionally different from the original idealized phase order.

The codebase progressed iteratively, with snapshot, preview, recording, simulation, host control, validation, and repository reorganization overlapping in practice.

## Phase 0: Repository Reorganization Toward The Vision Platform

- align the repository with `docs/ProjectDescription.md` and `docs/ProjectAgents.md`
- create repository-level module workspaces for apps, integrations, services, and libraries
- add `README.md`, `STATUS.md`, and `ROADMAP.md` per key module
- introduce `src/vision_platform` as the platform-facing namespace while preserving `src/camera_app`

Status:

- completed for the first reorganization round
- physical code migration remains intentionally incremental

## Reconstructed Delivery Flow

## Phase 1: Foundation And Package Structure

- create package structure under `src/camera_app/`
- define core models for configuration, requests, frames, and status
- define the `CameraDriver` abstraction
- establish logging and file naming scaffolding
- keep storage, services, drivers, and control separated

Status:

- completed

## Phase 2: Real Camera Access Baseline

- implement `VimbaXCameraDriver`
- discover available cameras
- open camera by explicit id or first available camera
- expose `CameraStatus`
- shut down cleanly
- apply basic camera features defensively
- capture a single frame safely

Status:

- completed in Python prototype form
- still requires repeated real-hardware evaluation

## Phase 3: End-To-End Snapshot Baseline

- connect camera acquisition to `SnapshotService`
- save one image to an explicit target path
- support deterministic naming
- log snapshot attempts and results
- provide a small smoke-test entry point

Status:

- completed

## Phase 4: Preview Service

- maintain a latest-frame buffer
- expose preview frame metadata without binding to a UI toolkit
- keep preview independent from snapshot and recording
- support start/stop behavior suitable for polling-based preview

Status:

- completed at service level
- `CameraStreamService` now provides a host-friendly composition point for preview on a shared live acquisition
- no dedicated desktop or browser preview UI in the core repository

## Phase 5: Recording Pipeline

- implement producer/consumer acquisition pipeline
- add bounded queue
- add writer service
- support stop by count, duration, or explicit stop
- track recording status and error state
- write per-recording CSV metadata logs

Status:

- completed for simulator-backed validation
- preview and recording can now share one acquisition loop through a common frame source
- interval-based single-image capture from that shared live stream is now implemented in the Python prototype
- still missing trigger-based recording
- still needs repeated real-hardware validation

## Phase 6: Simulation And Demo Path

- add `SimulatedCameraDriver` separate from SDK-backed drivers
- support deterministic generated frames
- support sample-image sequences for demos
- keep services and command flow identical between simulated and real hardware
- provide runnable simulator demos when hardware is unavailable

Status:

- completed

## Phase 7: External Command And Host Control Layer

- implement `CommandController`
- support externally controlled save directory changes
- support typed external request models for configuration, snapshot, and recording
- expose a typed consolidated `SubsystemStatus`
- keep the contract host-neutral so it can survive the later C# handover

Status:

- completed for the current Python scope
- bootstrap helpers now provide a consistent Python composition root for host-facing service wiring

### Phase 7a: Optional Payload Contract

- optional only if a concrete transport or host interface is needed
- define transport-facing DTOs, payload shapes, or response envelopes
- keep this aligned with the later C# handover instead of forcing it into the Python core too early

Status:

- intentionally deferred

## Phase 8: Validation And Demo Coverage

- add tests for naming, validation, queue behavior, and state transitions
- add tests for external request model mapping
- add runnable simulated demos for service flow and command-controller flow
- validate both real-hardware and simulated-driver workflows where practical

Status:

- partially completed
- simulator-backed validation is strong
- real-hardware validation is still the key open item

## Phase 9: Real Hardware Evaluation

- validate initialization and shutdown on the target device
- validate explicit camera selection by id
- validate exposure, gain, pixel format, and ROI behavior on real hardware
- validate snapshot, preview, and recording on real hardware
- validate failure cases such as unsupported settings, timeouts, or disconnects
- document results using `docs/HARDWARE_EVALUATION.md`

Status:

- open

## Phase 10: Optional OpenCV Integration

OpenCV is not part of the core architecture by default.

It should only be introduced as an optional imaging and preview layer on top of the existing services.

### Phase 10a: Preview And Inspection

- add optional conversion from `CapturedFrame` into an OpenCV-friendly image representation
- add an optional preview demo that displays simulator or hardware frames with `cv2.imshow()`
- keep the display path separate from the driver and service core
- keep screen- and window-specific scaling logic in the preview/display layer instead of the camera core
- add viewport-oriented preview controls such as fit-to-window, zoom, pan, and overlay-stable display transforms in the optional UI-facing path

Use this for:

- live stream inspection
- quick visual confirmation of focus, ROI, and exposure
- local desktop debugging

### Phase 10b: Lossless Grayscale Save Path

- prefer lossless visible formats over `.raw` when inspection is needed
- keep measurement data in a grayscale-safe format
- avoid silent normalization, gamma adjustment, contrast stretching, or lossy compression
- keep display conversion separate from saved measurement data

Recommended direction:

- `Mono8` -> lossless `.png`
- higher bit depth grayscale -> 16-bit-capable `.png` or `.tiff`

Use this for:

- human inspection
- later DIC workflows that depend on preserved grayscale values

### Phase 10c: Architecture Rule For OpenCV

- do not move OpenCV into `CameraDriver`
- do not make OpenCV a required dependency for the core services
- do not let preview-specific conversions alter stored measurement data
- keep OpenCV in a separate adapter, imaging utility, or optional demo module

Status:

- partially completed at the Python level
- optional preview inspection and grayscale-safe save paths are implemented for simulator-backed use
- a first real-hardware OpenCV preview demo now exists for local inspection
- a first viewport-based preview path with fit-to-window and zoom controls now exists in the OpenCV prototype layer
- still requires real-hardware validation before treating the optional path as hardware-proven

## Current Recommended Order

From the current repository state, the practical next steps are:

1. run the real hardware evaluation checklist
2. decide whether Phase 8 can be marked complete after that run
3. validate the already implemented optional OpenCV path against real hardware frames if that inspection path is needed
4. structure the next OpenCV UI block around status bar, crosshair toggle, focus toggle, ROI tools, snapshot shortcut, and the operator-facing menu/control band
5. extend the viewport path toward pan and cursor-aware zoom behavior without moving those concerns into the core
6. keep the Python core stable as the handover baseline for the later C# phase
