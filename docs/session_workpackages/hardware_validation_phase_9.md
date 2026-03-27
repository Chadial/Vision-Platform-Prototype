# Phase 9 Hardware Validation Work Package

## Purpose

This temporary work package captures the current execution plan for making the real-hardware validation path complete enough to move the repository from simulator-validated toward prototype-level hardware-validated.

Use this file as the first recovery point if a session ends before the hardware-validation work is finished.

## Branch

- `feature/hardware-validation-phase-9`

## Scope

Included in this work package:

- real-hardware validation planning and execution for Phase 9
- minimal code hardening needed to make hardware smoke runs reproducible
- hardware-specific diagnostics, logging, and launcher refinements when justified
- documentation of pass/fail results
- status updates tied to hardware-backed evidence

Excluded from this work package:

- ROI drawing tools
- additional focus methods
- broader OpenCV UI feature work
- repository reorganization unrelated to hardware validation

## Session Goal

Reach a documented and reviewable hardware-validation state for:

1. initialization and shutdown
2. explicit camera selection
3. configuration application
4. snapshot save
5. preview flow
6. recording flow
7. error and boundary behavior

## Current Progress

State as of March 27, 2026:

- session-recovery and archive structure is in place
- a dedicated integrated hardware runner now exists at `scripts/launchers/run_hardware_command_flow.py`
- a first hardware-backed baseline run was completed against camera `DEV_1AB22C046D81` (`Allied Vision 1800 U-1240m`)
- the first two integrated runs exposed cleanup-side Vimba X `Invalid Camera` errors during shared-stream shutdown
- shared-frame-source cleanup ordering and timeout handling were hardened afterwards
- the follow-up `run_003` pass completed without those cleanup-side Vimba X errors
- the validated hardware-backed baseline now covers snapshot save, preview readiness, interval capture from the shared preview stream, and frame-limit recording
- additional hardware runs now cover duration-only recording, target-frame-rate recording, supported `Mono10` snapshot capture as `.raw`, and explicit failures for invalid camera id, unsupported pixel format `Mono16`, and invalid ROI width increments
- the tested camera exposes `AcquisitionFrameRate` but rejects writes in the exercised mode, which is now documented as a device-specific constraint
- the remaining open points are now mainly timeout/disconnect edge cases and any contract decision around capability-aware handling of non-writeable camera features

## Execution Plan

### 1. Prepare the run context

- confirm the active branch is `feature/hardware-validation-phase-9`
- use `.\.venv\Scripts\python.exe`
- confirm the target camera is connected
- confirm Vimba X and `vmbpy` are available to the project environment
- define a concrete output path such as `captures/hardware_smoke/run_001`
- record camera id, machine name, operator, and date

### 2. Inspect the current hardware entry points

- review the current launchers and smoke paths used for hardware access
- identify whether small code adjustments are needed for:
  - explicit CLI inputs
  - stable output paths
  - clearer failure messages
  - recoverable shutdown behavior
  - structured run notes

### 3. Apply only minimal code hardening

Allowed changes:

- improve logging around initialize, configure, preview, snapshot, and recording
- improve hardware-path diagnostics
- harden error handling for unsupported settings or cleanup failures
- add small launcher or helper refinements that make runs reproducible

Do not:

- start unrelated feature work
- mix UI expansion into this branch
- broaden scope beyond Phase 9 validation needs

### 4. Run the hardware checklist

Execute and document:

- initialization and shutdown
- explicit camera selection by id
- configuration application:
  - exposure
  - gain if supported
  - pixel format if supported
  - frame rate if supported
  - ROI if supported
- snapshot validation:
  - default snapshot
  - explicit pixel-format snapshot
  - ROI snapshot if supported
- preview validation:
  - start/stop cycle
  - repeated frame refresh behavior
- recording validation:
  - `max_frame_count`
  - `duration_seconds`
  - `target_frame_rate`
- error and boundary checks:
  - invalid camera id
  - unsupported pixel format
  - unsupported ROI combination
  - additional timeout/disconnect checks only if practical

Recommended integrated run command:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_hardware_command_flow.py --base-directory .\captures\hardware_smoke --run-name run_001 --camera-id example_camera_id --pixel-format Mono8 --frame-limit 3 --interval-frame-count 3
```

### 5. Run relevant validation after any code changes

At minimum, run the test modules that cover the touched scope.

If the hardware launchers or driver-facing behavior changes, prefer running the known core regression block from `docs/STATUS.md` in addition to the real-hardware smoke runs.

### 6. Update documentation from evidence

Update:

- `docs/HARDWARE_EVALUATION.md`
- `docs/STATUS.md`

Update `docs/ROADMAP.md` only if the Phase 9 status genuinely changes.

Record:

- pass/fail per checklist area
- what was verified on real hardware
- what still remains simulator-only
- concrete follow-up items if any hardware gaps remain

## Expected Commit Shape

1. `chore: add hardware validation run scaffolding`
2. `fix: harden hardware smoke paths and diagnostics`
3. `test: add hardware-oriented validation coverage where feasible`
4. `docs: record phase-9 hardware validation status`

## Merge Gate

Do not treat this work package as complete unless:

- the hardware run is documented with real results
- any touched tests pass locally
- docs reflect the actual validation boundary
- the branch remains focused on hardware validation only

## Recovery Note

If a later session resumes this work, start with:

1. `Agents.md`
2. `docs/SESSION_START.md`
3. this file
4. `docs/HARDWARE_EVALUATION.md`
5. `docs/STATUS.md`
