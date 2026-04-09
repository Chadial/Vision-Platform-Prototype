# WP87 Hybrid Companion Hardware Workflow Revalidation

## Purpose

Revalidate the landed Hybrid Companion workflows on the tested hardware path through the current host-plus-shell operating mode.

## Status

Conditional and currently blocked in this session.

`WP87` was activated after `WP86`, but the tested real-hardware path could not be revalidated on April 9, 2026 because the expected device `DEV_1AB22C046D81` was not available locally.

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

- status: blocked
- target:
  - Delamination Recording
  - Geometry Capture
  - Setup / Focus / ROI Adjustment
- intended mode:
  - running wx shell on hardware
  - host-visible status through the bounded open-shell control path

#### `WP87.C Hardware Evidence Capture`

- status: blocked
- target:
  - record fresh April 2026 evidence in the hardware docs once the tested device path is attached again

### Boundary Note

This package remains:

- hardware-dependent
- evidence-driven
- conditional on the tested real device being attached
- not satisfiable through simulator-only proof

### Reactivation Trigger

Reactivate `WP87` only when the tested real camera path is attached again and the bounded hardware command path resolves the documented device identity successfully.
