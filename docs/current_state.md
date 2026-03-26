# Current State

## Existing Implementation Baseline

The repository already contains a service-oriented Python prototype under `src/camera_app` with:

- `drivers` for `VimbaXCameraDriver` and `SimulatedCameraDriver`
- `services` for camera initialization, preview, shared streaming, recording, interval capture, and snapshot saving
- `storage` helpers for deterministic file naming and frame writing
- `imaging` helpers for optional OpenCV preview and grayscale-safe export
- `control` with a host-style `CommandController`
- `smoke` entry points used by the root helper scripts
- automated tests covering most simulator-backed flows

During the current reorganization, parts of that implementation have already started to move physically into `src/vision_platform`. At this point, `control`, optional `imaging`, stream-service internals, camera drivers, prototype app entry points, ROI helpers, and the first focus-analysis baseline are implemented there, while `camera_app` keeps compatibility shims for the still-bridged areas.

## Tight Couplings

- the implementation is technically layered, but organizationally concentrated under `src/camera_app`
- root helper scripts now target `vision_platform.apps.opencv_prototype`, while `camera_app.smoke` remains as a compatibility layer
- shared models for future ROI/focus/tracking work did not exist as separate reusable libraries
- repository-level module ownership was missing, so roadmap and status tracking remained mostly global
- root-level status documents still need active synchronization so new platform behavior is not only implied by tests and package structure

## What Already Works

- camera initialization through a real or simulated driver
- preview buffering and shared acquisition
- snapshot saving to explicit paths
- interval capture and bounded-queue recording
- host-style command flow with explicit request objects
- optional OpenCV preview/save path
- baseline Laplace focus scoring with ROI-aware overlay anchors
- preview- and app-level focus consumers on top of the simulator-backed path
- simulator-backed tests and smoke demos

## Main Risks Before Reorganization

- future ROI/focus/tracking work would likely accumulate inside `camera_app`
- module responsibilities were clearer in code than in repository layout
- root documentation did not yet show a platform-wide target structure
- a later C# team handover would need extra effort to infer module boundaries from package internals alone
