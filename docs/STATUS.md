# Status

## Source References

This status document should always be read and updated in relation to:

- `docs/ROADMAP.md` for the repository-specific implementation phases
- `docs/GlobalRoadmap.md` for the broader Python -> C# -> web-capable target path

Each status update should state progress and gaps against both roadmaps.

## Current Branch

- `main` as the latest integrated baseline

## Roadmap Position

- Against `docs/ROADMAP.md`: Phase 0 repository reorganization is now completed for its first round, and Foundation, Camera Access, Snapshot Flow, Preview Flow, Recording Flow, Simulation, Host Integration, and the Python-side optional OpenCV path remain functionally implemented. Validation remains partially completed because simulator-backed coverage is strong but real-hardware validation is still open. Real Hardware Evaluation remains open. The focus baseline now also exists as a first implemented analysis capability on top of that reorganized platform surface, and ROI groundwork has advanced from geometry-only helpers to analysis-consumable mask derivation for rectangle and ellipse shapes.
- Against `docs/GlobalRoadmap.md`: the platform-reorganization phase is now established alongside the existing Python prototype baseline. Camera integration, stream/recording services, host-neutral command flow, the optional OpenCV prototype path, ROI geometry groundwork, ROI mask primitives, and a first manual-focus baseline are in place. A first real-hardware OpenCV preview path is now available for local inspection, and the OpenCV prototype now also provides a first viewport-based preview baseline with fit-to-window plus zoom controls while keeping those concerns explicitly in the UI/display layer. The shared contract layer under `libraries/common_models` now also intentionally exposes some target-facing surface ahead of full implementation, with feature readiness expected to be marked in module-local status docs. Tracking/API modules and full real-hardware validation remain open. The next mandatory milestones against the global roadmap are broader hardware validation and the next operator-facing preview/UI block.

## Merge Note

- `feature/roi-core-mask-baseline` has been merged into `main`.
- The merged ROI/focus/overlay baseline was revalidated on `main` with the targeted simulator-backed regression block before continuing.

## Current Summary

The repository currently provides a structured Python prototype for the vision platform with:

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
- `RoiStateService` as a small service-layer holder for one active ROI selection that preview-adjacent consumers can reuse
- `SnapshotFocusService` as a separate snapshot-analysis consumer that can reuse the same active ROI state path without mixing focus logic into snapshot saving
- `OverlayCompositionService` as a UI-free display composition layer that can merge active ROI plus preview/snapshot focus overlays into one shared payload
- simulator-backed overlay-payload demo that consumes the shared payload and prints a simple console summary without committing to a concrete renderer
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
- optional OpenCV hardware preview demo for local live inspection with an explicit camera id
- optional OpenCV-backed lossless grayscale path for `.png` and `.tiff`
- viewport-based OpenCV preview controls for fit-to-window and zoom on large hardware frames
- additional service hardening so preview/recording cleanup resets internal state defensively even when acquisition stop fails during recovery
- new repository-level module workspaces for apps, integrations, services, and libraries
- new `src/vision_platform` namespace that exposes the current platform shape without breaking legacy `camera_app` imports
- new shared foundation modules for common models, ROI groundwork, and focus groundwork
- common model contracts now intentionally allow some future-facing surface to appear before full downstream implementation, with readiness expected to be marked in module-local docs
- physical migration of control and imaging implementation into `src/vision_platform`, with `camera_app` retained as a compatibility shim for those areas
- physical migration of file naming and frame writing into `src/vision_platform.services.recording_service`, with `camera_app.storage` retained as a compatibility shim
- physical migration of stream-service internals, camera drivers, and prototype demo entry points into `src/vision_platform`, with legacy `camera_app` modules retained as compatibility shims
- first implemented focus baseline with Laplace scoring, ROI-aware overlay anchors, and preview-consumer integration
- ROI core now also provides frame-clamped pixel bounds and rectangle/ellipse mask derivation so analysis consumers can apply ROI selection without reimplementing ROI math
- freehand ROI remains a target contract direction only and is not yet implemented through ROI-core mask derivation or downstream analysis consumers
- stream services now expose a small ROI state path so active ROI selection can be shared with preview-adjacent analysis without moving ROI ownership into UI or stream internals
- snapshot-side focus analysis can now also consume the same ROI state path while staying separate from snapshot persistence
- preview- and snapshot-side focus overlays can now be composed together with the active ROI into one shared display payload without introducing a concrete UI dependency
- the OpenCV prototype app layer now includes a simulator-backed payload demo that exercises this shared display payload through a lightweight console-facing adapter path
- viewport management concerns such as fit-to-window, zoom, pan, and display-space overlay transforms are now explicitly treated as UI/display-layer responsibilities instead of camera-core responsibilities
- the first integrated viewport implementation now preserves aspect ratio and uses black padding/cropping in the OpenCV prototype instead of naive display stretching

## Completed Work

### Foundation

- package structure created
- core domain models added
- logging setup scaffold added
- file naming scaffold added
- command controller skeleton added
- portable focus/ROI model extensions now include overlay-ready focus payloads and ROI centroid support
- ROI helper primitives now also include frame-clamped pixel bounds plus rectangle/ellipse mask derivation for analysis consumers
- common models now also include a shared display overlay payload for later preview, snapshot, or host consumers

### Camera Access

- camera discovery and initialization implemented
- explicit camera selection by id implemented
- clean shutdown implemented
- configuration application implemented
- single-frame acquisition implemented
- frame metadata model added through `CapturedFrame`
- real hardware currently runs through `VimbaXCameraDriver`
- hardware-free development now runs through `SimulatedCameraDriver`
- platform-owned driver implementations now live in `vision_platform.integrations.camera`

### Snapshot Flow

- snapshot request to target-path flow implemented
- frame writer added for `.png`, `.raw`, and `.bin`
- `FrameWriter` implementation now lives in `vision_platform.services.recording_service`
- frame writer can now use an optional OpenCV adapter for higher-bit grayscale `.png` and `.tiff`
- snapshot logging added
- snapshot smoke-test flow added
- snapshot smoke entry point now lives in `vision_platform.apps.opencv_prototype`
- `SnapshotFocusService` now provides a separate snapshot-analysis path for focus evaluation without coupling that behavior into `SnapshotService`
- `overlay_payload_demo` now validates a demo path that consumes the shared display payload without forcing a concrete window implementation

### Preview Flow

- preview service start/stop implemented
- latest-frame buffer implemented
- polling-based preview refresh implemented
- preview frame metadata exposure implemented
- optional OpenCV preview window adapter implemented above `PreviewService`
- optional OpenCV hardware preview demo implemented above `PreviewService` and `VimbaXCameraDriver`
- viewport-based fit-to-window and zoom controls now implemented in the OpenCV prototype preview path
- `PreviewService`, `SharedFrameSource`, and `CameraStreamService` now live in `vision_platform.services.stream_service`
- `FocusPreviewService` now derives focus state from preview frames without embedding analysis logic into the stream loop or window layer
- `RoiStateService` now lets preview-adjacent consumers reuse one active ROI selection without making ROI a stream-owned concern

### Recording Flow

- basic producer/consumer pipeline implemented
- bounded queue implemented
- sequential recording file naming implemented
- recording naming helpers now live in `vision_platform.services.recording_service`
- per-recording CSV log file implemented
- recording log header includes session metadata such as start signal time, stop conditions, save path, and known camera settings
- frame-limit stop condition implemented
- duration-based stop condition implemented
- target-frame-rate pacing implemented for recording requests
- recording state and error tracking implemented

### Focus And ROI Foundations

- portable ROI definitions now expose bounds and centroid helpers for later overlay consumers
- portable ROI definitions now also expose frame-clamped pixel bounds and rectangle/ellipse mask derivation for analysis consumers
- `common_models` may now expose some target-facing contract surface ahead of end-to-end implementation, with readiness expected to be marked in module status docs
- ROI remains a reusable geometry/selection input instead of a UI-owned concern
- `focus_core` now provides a baseline Laplace evaluator for manual focus decisions
- focus evaluation remains consumer-driven, so stream layers expose frames while preview-facing consumers decide when focus is computed
- overlay-ready focus payloads now exist for preview and display consumers without coupling UI code into the analysis layer
- focus evaluation now consumes ROI mask helpers from `roi_core` instead of keeping ROI pixel-window logic private inside `focus_core`
- preview-adjacent consumers can now read an active ROI through `RoiStateService`, while explicit per-call ROI still remains possible
- snapshot-side focus consumers can now reuse the same ROI state path or override it explicitly per call
- overlay composition is now a separate service-layer concern that can merge active ROI plus preview/snapshot focus states into one UI-free payload
- live preview-adjacent consumers now derive focus state from preview frames, while richer metric selection and operator-facing overlay controls remain open

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
- `CommandController` implementation now lives in `vision_platform.control`, while `camera_app.control` remains as a compatibility import
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
- additional tests now cover baseline focus scoring, ROI-centroid geometry, ROI pixel bounds, rectangle/ellipse mask derivation, ROI-state-driven preview-focus consumption, snapshot-side focus capture, UI-free overlay composition, overlay-payload demo consumption, stream-level focus integration, and the simulated focus-preview smoke/demo path
- real hardware validation is still pending separately from the simulator-backed validation

### Preview

- service layer exists and is test-covered
- preview can now run against an optional shared frame source instead of starting an independent acquisition loop
- `CameraStreamService` now exposes that shared-acquisition path as the preferred composition point for live preview plus concurrent recording
- `CameraStreamService` can now also create `IntervalCaptureService` for preview plus timed single-image saving from the same stream
- `CameraStreamService` can now also create `FocusPreviewService` so focus state can be derived from the same preview path
- an optional OpenCV preview window now exists above the service layer
- a first real-hardware preview demo now exists on top of the optional OpenCV layer for local desktop inspection
- the preview demo can now optionally compose focus state while keeping the window class itself free of focus logic
- fit-to-window and zoom are now implemented in the OpenCV prototype UI layer; pan, cursor-aware zoom anchoring, status bar, and menu-band controls remain for the next UI/display-facing step
- no browser preview or non-OpenCV UI layer yet
- hardware-backed preview inspection is now possible again because a connected camera has been verified locally
- simulated preview exists through `SimulatedCameraDriver`

### Simulation vs. Real Hardware

- architecture now explicitly expects separate real-hardware and simulated driver implementations
- `SimulatedCameraDriver` is implemented for generated frames and `.pgm`/`.ppm` sample image sequences
- a simulated demo entry point exists for preview, snapshot, and recording without hardware
- a simulated focus-preview smoke/demo path now exists for preview-to-focus validation without hardware
- the simulated and Vimba X drivers now live physically in `vision_platform.integrations.camera`
- simulator-backed tests now verify that preview and recording can share one acquisition loop without fighting over the driver
- simulator-backed tests now also verify preview plus timed interval capture from the same shared stream
- simulated generation now also covers `Mono16` frames for grayscale-save-path validation
- sample-image demo support is limited to `.pgm` and `.ppm` files for now
- real hardware validation is still required separately from simulation

### Optional OpenCV Integration

- optional OpenCV implementation now lives in `vision_platform.imaging`
- `camera_app.imaging` remains as a compatibility shim for legacy imports
- the app-facing OpenCV demos now live in `vision_platform.apps.opencv_prototype`
- OpenCV remains outside `CameraDriver` and outside the mandatory core dependency set
- preview display can now run through `cv2.imshow()` on top of `PreviewService`
- preview display can now also run against a real Vimba X camera through the optional OpenCV prototype path
- the preview demo can now optionally carry focus state alongside the rendered preview path without moving analysis into the OpenCV window class
- fit-to-window and zoom are now implemented as frontend/display concerns rather than core-service concerns
- pan, cursor-aware zoom anchoring, status bar widgets, ROI drawing tools, and menu-band controls remain planned in that same frontend/display layer
- lossless grayscale save now supports `.png` and `.tiff` through the optional adapter for `Mono8` and unpacked higher-bit grayscale formats such as `Mono16`
- the standard-library writer remains the default for dependency-free `Mono8`, `Rgb8`, and `Bgr8` PNG output
- packed grayscale formats are still not decoded automatically and should be transformed explicitly before using the OpenCV save path if required
- simulator-backed validation for the optional path is complete, but hardware-backed validation is still pending

## Known Constraints

- real hardware is available again for targeted preview validation, but broader hardware validation is still incomplete
- the terminal default `python` may differ from the project interpreter on this machine
- the project virtual environment currently uses Python 3.14.3 at `.\.venv\Scripts\python.exe`
- project tests should be run with `.\.venv\Scripts\python.exe`

## Verified Test Commands

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_snapshot_service tests.test_frame_writer tests.test_snapshot_smoke tests.test_preview_service tests.test_file_naming tests.test_recording_service tests.test_interval_capture_service tests.test_camera_stream_service tests.test_bootstrap tests.test_simulated_camera_driver tests.test_simulated_demo tests.test_command_flow_demo tests.test_command_controller tests.test_request_models tests.test_opencv_adapter tests.test_opencv_preview tests.test_opencv_smoke_demos tests.test_focus_core tests.test_focus_preview_service tests.test_focus_preview_demo tests.test_vision_platform_namespace
```

## Next Recommended Steps

0. If the current task is to complete real-hardware validation, resume from `docs/session_workpackages/hardware_validation_phase_9.md` before running or editing hardware-related paths.
1. Run a real hardware smoke test again when the target camera is available.
2. Validate the optional OpenCV path with real hardware frames, especially any higher-bit grayscale formats delivered by Vimba X.
3. Structure the next operator-facing OpenCV UI block around status bar, crosshair toggle, focus toggle, ROI tools, snapshot shortcut, and the menu/control band.
4. Extend the viewport path toward pan, cursor-aware zoom anchoring, and overlay-safe viewport transforms without leaking screen concerns into the core.
5. Decide whether future overlay composition should stay on fixed preview/snapshot fields or move to a more generic layer model when tracking overlays arrive.
6. Define a stricter payload mapping only if the later C# or host integration really needs it.
7. Keep the Python core stable as the handover baseline for the later C# phase.
