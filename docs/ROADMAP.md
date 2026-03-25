# Roadmap

## Purpose

This roadmap reflects the actual implementation flow reconstructed from the current Python repository state.

It is intentionally different from the original idealized phase order.

The codebase progressed iteratively, with snapshot, preview, recording, simulation, host control, and validation overlapping in practice.

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

- not implemented yet
- suitable as the next optional Python-side extension after hardware evaluation or in parallel with local inspection needs

## Current Recommended Order

From the current repository state, the practical next steps are:

1. run the real hardware evaluation checklist
2. decide whether Phase 8 can be marked complete after that run
3. add optional OpenCV preview and grayscale-safe inspection if live visual inspection is needed
4. keep the Python core stable as the handover baseline for the later C# phase
