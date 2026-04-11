# WP54 wx Shell Hardware Enablement

## Purpose

This work package defines the missing real-device enablement slice for the newly landed wxPython local shell.

Closure lane:

- Post-Closure Python Baseline / selective expansion

Slice role:

- hardware enablement baseline

Scope level:

- one bounded real-hardware path for the existing wx shell only

Its purpose is to close the concrete gap exposed by the first manual hardware revalidation after `WP53`: the repository now has a bounded local wx shell, but that shell still runs only against the simulated subsystem path.

## Branch

- intended branch: `feature/wx-shell-hardware-enablement`
- activation state: implemented

## Scope

Included:

- add one bounded hardware-backed startup path for the existing wx shell
- reuse the existing real hardware driver/bootstrap/controller path instead of introducing UI-private hardware logic
- keep snapshot and basic status on the same controller-owned path already used by the CLI and current OpenCV hardware demos
- keep the current simulated wx shell path working
- add one minimal manual or bounded automated smoke path for wx-shell startup on real hardware if locally feasible

Excluded:

- broader wx-shell feature growth
- recording UI
- full camera-configuration UI
- hardware audit/history redesign
- CLI help/documentation polish

## Session Goal

Leave the repository with one bounded wxPython shell path that can run against real hardware on the tested device path, so the new local shell is no longer simulator-only.

## Current Context

The current hardware rerun established:

- CLI `status` succeeds on `tested_camera`
- CLI `snapshot` succeeds on `tested_camera`
- the integrated hardware command flow succeeds on `DEV_1AB22C046D81`
- the OpenCV hardware preview smoke succeeds on `DEV_1AB22C046D81`

The missing part is narrower:

- the wx shell itself has no real-hardware entry path yet
- the current wx shell is still wired to `build_simulated_camera_subsystem(...)`

## Narrow Decisions

- do not replace the simulated wx path; keep both simulated and hardware-backed startup paths
- do not bypass the existing subsystem/controller path just to get a picture on screen
- use the tested camera path and existing alias/profile conventions where practical
- prefer one bounded hardware shell path over broad wx-shell feature expansion

## Execution Plan

1. re-read the current wx shell code and the existing OpenCV hardware preview entry path
2. extract the smallest shared subsystem/startup seam needed so the wx shell can be fed by either:
   - simulated subsystem
   - hardware-backed subsystem
3. add one explicit hardware startup path for the wx shell
4. keep snapshot on the existing command-controller path
5. keep status/preview ownership on the already extracted display-service layers
6. add the narrowest viable validation:
   - simulator-backed test coverage where practical
   - bounded real-hardware smoke instructions or proof when hardware is attached
7. update status/work-package docs from the new capability

## Validation

Minimum local validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_wx_preview_shell tests.test_bootstrap tests.test_command_controller
```

Bounded hardware smoke target:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell --source hardware --camera-alias tested_camera
```

Or an equivalent explicit `--camera-id DEV_1AB22C046D81` path if the shell keeps direct-id startup simpler.

## Documentation Updates

- `docs/WORKPACKAGES.md`
- `docs/STATUS.md`
- `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md`
- `apps/local_shell/STATUS.md`
- `apps/local_shell/README.md`

## Expected Commit Shape

1. `feat: add hardware-backed startup path for wx shell`
2. `test: cover wx shell hardware startup seam`
3. `docs: record wx shell hardware enablement`

## Merge Gate

- the wx shell can start on real hardware without UI-private hardware bypasses
- the simulated wx path still works
- snapshot still runs through the shared controller path
- the shell remains a bounded optional frontend
- docs clearly distinguish simulator-first and hardware-backed startup options
