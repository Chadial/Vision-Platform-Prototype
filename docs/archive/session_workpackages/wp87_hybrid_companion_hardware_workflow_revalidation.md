# WP87 Hybrid Companion Hardware Workflow Revalidation

## Purpose

Revalidate the landed Hybrid Companion workflows on the tested hardware path through the current host-plus-shell operating mode.

## Status

Completed for the current tested-path revalidation.

`WP87` was activated after `WP86`. The tested real-hardware path initially missed on April 9, 2026 because `DEV_1AB22C046D81` was not available locally, then succeeded on April 10, 2026 once the device was attached again.

## Sub-Packages

### Executed In This Session

#### `WP87.A Tested-Hardware Availability Check`

- status: executed
- purpose: confirm whether the documented tested device path is actually available before attempting workflow revalidation
- observed result:
  - `python -m vision_platform.apps.camera_cli status --source hardware --camera-alias tested_camera` failed with `No Camera with Id 'DEV_1AB22C046D81' available.`
  - direct VmbPy enumeration only exposed camera simulators:
    - `DEV_Cam1` `Camera Simulator (G1-030_VSWIR)`
    - `DEV_Cam2` `Camera Simulator (G5-1240m)`
    - `DEV_Cam3` `Camera Simulator (G1-510c)`

### Deferred Until Hardware Is Attached

#### `WP87.B Hybrid Companion Workflow Rerun`

- status: executed
- target:
  - Delamination Recording
  - Geometry Capture
  - Setup / Focus / ROI Adjustment
- intended mode:
  - running wx shell on hardware
  - host-visible status through the bounded open-shell control path
- observed result:
  - `camera_cli status --source hardware --camera-alias tested_camera` succeeded on `DEV_1AB22C046D81`
  - `camera_cli snapshot --source hardware --camera-alias tested_camera --configuration-profile default --base-directory .\\captures\\hardware_smoke\\test_wp87_snapshot --file-extension .bmp` succeeded and wrote `snapshot_000000.bmp`
  - `camera_cli recording --source hardware --camera-alias tested_camera --configuration-profile default --base-directory .\\captures\\hardware_smoke\\test_wp87_recording --frame-limit 3` succeeded and wrote 3 frames
  - `run_hardware_command_flow.py --base-directory .\\captures\\hardware_smoke --run-name test_wp87_run_001 --camera-id DEV_1AB22C046D81 --pixel-format Mono8 --frame-limit 3 --interval-frame-count 3` succeeded

#### `WP87.C Hardware Evidence Capture`

- status: executed
- target:
  - record fresh April 2026 evidence in the hardware docs once the tested device path is attached again
- observed result:
  - fresh April 10, 2026 evidence was captured in `docs/HARDWARE_EVALUATION.md` and `docs/STATUS.md`

### Boundary Note

This package remains:

- hardware-dependent
- evidence-driven
- now complete for the current tested-path revalidation
- still repeatable later whenever the tested real device is attached again

### Reactivation Trigger

Re-run `WP87` later when fresh hardware evidence is needed on the tested real camera path.
