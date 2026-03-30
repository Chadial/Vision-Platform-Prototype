# Hardware Lifecycle And Camera Release Hardening

## Purpose

This work package defines the next execution-ready follow-up after the landed `WP26` bounded hardware confidence rerun.

Closure lane:

- Experiment Reliability Closure

Slice role:

- narrow hardware-lifecycle hardening

Scope level:

- deterministic camera release, cleanup, and process-to-process reuse on the current real-device path

Its purpose is to narrow the remaining operationally relevant real-device gap exposed during the March 30, 2026 hardware work: successful runs generally work, but repeated serial hardware work can still encounter `camera already in use` conditions that point to non-deterministic lifecycle or lingering-handle behavior.

This package should be read as:

- cleanup / release hardening
- not a broad hardware exploration package
- not a broad runtime redesign

## Branch

- intended branch: `fix/hardware-camera-lifecycle-cleanup`
- activation state: landed on March 30, 2026 as the narrow lifecycle follow-up after `WP26`

## Scope

Included:

- inspect real-device initialization and shutdown paths in the current Vimba X driver, service, and shared-stream lifecycle
- reproduce and narrow the remaining `camera already in use` path under serial real-device execution
- identify whether the observed problem is:
  - one lingering process / handle problem
  - one incomplete shutdown path
  - one preview/shared-stream cleanup ordering issue
  - one capability-probe or command-entry-point lifecycle issue
- implement the narrowest deterministic cleanup improvement that makes serial real-device reuse more reliable
- add the smallest practical validation path that proves a second hardware process can reuse the same camera after a completed prior run

Excluded:

- broad hardware capability expansion
- camera matrix testing
- transport or API redesign
- large driver rewrite
- performance benchmarking

What this package does not close:

- all remaining hardware quirks
- all SDK/logging anomalies such as every `NotAvailable` log line
- broad reliability closure across every failure class

## Session Goal

Leave the repository with one narrower and more deterministic real-device lifecycle baseline so completed hardware runs do not leave the next serial hardware process in an ambiguous `camera already in use` state.

## Current Context

The March 30, 2026 bounded hardware reruns showed:

- the core hardware baseline works
- repeated hardware work is operationally slowed by occasional `camera already in use` failures
- at least one real instance was caused by a lingering Python process that still held the camera

The unresolved question is:

- does the current integrated Python baseline release the camera deterministically enough across real-world serial execution paths?

Implemented narrowing result:

- the most plausible shared lifecycle seam was the capability-probe path during `CameraService.initialize()`
- the real-hardware path previously opened the camera through `VimbaXCameraDriver` and then immediately re-entered Vimba X through `probe_camera_capabilities(...)`
- this slice now probes capability data from the already opened driver camera instead of opening a second Vimba/camera context during initialization
- the March 30, 2026 serial hardware proofs on `DEV_1AB22C046D81` (`status -> status`, `snapshot -> status`, `recording -> status`) no longer reproduced `camera already in use`
- this slice does not close the residual `vmbpyLog <VmbError.NotAvailable: -30>` observation or the duplicate SDK enumeration note

## Narrow Decisions

- this package is about lifecycle determinism, not capability expansion
- successful real-device flows already exist, so the target is cleanup confidence rather than new functional breadth
- any fix should stay as local as practical to driver/service/entry-point cleanup behavior
- any new validation should be hardware-backed and serial, not parallel

## Execution Plan

1. Re-read:
   - `docs/HARDWARE_EVALUATION.md`
   - `docs/HARDWARE_CAPABILITIES.md`
   - `services/recording_service/STATUS.md`
2. Inspect the hardware lifecycle boundaries in:
   - `vision_platform.integrations.camera.vimbax_camera_driver`
   - shared preview / stream shutdown
   - snapshot, recording, CLI, and capability-probe entry paths
3. Reproduce one minimal serial camera-reuse failure path.
4. Tighten cleanup ordering or teardown handling at the narrowest shared seam.
5. Re-run one serial hardware proof such as:
   - process A: `status` or `snapshot`
   - process B immediately afterwards on the same camera id
6. Update hardware docs with the narrowed result.

## Validation

Required hardware-backed validation:

- one serial `status -> status` or `snapshot -> snapshot` reuse proof on `DEV_1AB22C046D81`
- one serial `recording -> status` or `recording -> snapshot` reuse proof on the same camera id

Recommended supporting local validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_command_controller tests.test_bootstrap tests.test_recording_service
```

## Documentation Updates

- `docs/HARDWARE_EVALUATION.md`
- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- relevant module `STATUS.md` if cleanup behavior changes materially

## Expected Commit Shape

1. `fix: harden hardware camera release lifecycle`
2. `test: cover serial hardware reuse path`
3. `docs: record hardware lifecycle hardening`

## Merge Gate

- the slice remains narrowly focused on camera release and cleanup determinism
- at least one previously flaky serial hardware reuse path is now reliable enough to document
- no broad hardware exploration or transport work is bundled
- hardware-backed evidence is recorded explicitly

## Completion Note

Landed evidence for this slice:

- unit validation:
  - `.\.venv\Scripts\python.exe -m unittest tests.test_camera_service tests.test_capability_probe tests.test_vimbax_camera_driver`
- serial real-device proofs on `DEV_1AB22C046D81`:
  - `status -> status`
  - `snapshot(.bmp) -> status`
  - bounded `recording(frame_limit=5) -> status`
- artifact folders:
  - `captures/hardware_smoke/wp27_reuse_check`
  - `captures/hardware_smoke/wp27_recording_reuse_check`

## Recovery Note

To activate this work package later:

1. confirm the camera is attached
2. confirm no stale hardware test processes still hold the device
3. read `docs/HARDWARE_EVALUATION.md`
4. read `docs/HARDWARE_CAPABILITIES.md`
5. read `services/recording_service/STATUS.md`
6. create the intended branch before substantive edits
