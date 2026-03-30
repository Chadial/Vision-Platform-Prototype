# Reference Scenarios

## Purpose

This document defines three official bounded reference scenarios for the current Python baseline.

Use them as:

- practical usage anchors
- confidence scenarios after changes
- small handover recipes
- bounded operational examples

These scenarios are not a new test framework.
They are command-centered reference runs over the current baseline.

## General Rule

- use repo-local output under `captures/`
- use the preferred entry path:
  - `.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli`
- use simulator-backed commands by default for reproducibility
- substitute `--source hardware --camera-id DEV_1AB22C046D81` only when a real-device confidence rerun is the actual goal
- when the repo-local alias file is present, `--camera-alias tested_camera` is the current bounded convenience form for the tested hardware path
- when the repo-local profile file is present, `--configuration-profile default` is the current bounded convenience form for the tested hardware profile baseline

## 1. Snapshot Reference Scenario

### Purpose

Verify the smallest useful end-to-end capture path:

- initialize through the bounded host-oriented command surface
- save one visible artifact
- confirm the artifact landed
- confirm traceability exists
- optionally confirm the current offline path can reuse the result

### When To Run

- after changes around snapshot, save-path handling, traceability, or host-envelope behavior
- when you need one smallest practical confidence scenario
- when onboarding someone into the current baseline

### What It Proves

- the current command entry point works
- snapshot saving works end to end
- repo-local save-path handling works
- snapshot traceability is written
- a `.bmp` artifact can be reused through the current offline focus-report path

### What It Does Not Prove

- recording behavior
- interval-capture behavior
- broad hardware reliability
- broad offline tooling

### Commands

Preferred bounded reference run:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli status --source simulated
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli snapshot --source simulated --base-directory .\captures\reference_snapshot --file-stem reference_snapshot --file-extension .bmp
.\.venv\Scripts\python.exe -m vision_platform.apps.postprocess_tool .\captures\reference_snapshot
```

Real-device substitution when explicitly needed:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli snapshot --source hardware --camera-alias tested_camera --configuration-profile default --base-directory .\captures\reference_snapshot --file-stem reference_snapshot --file-extension .bmp
```

### Expected Output Directory

- `captures/reference_snapshot/`

### Expected Artifacts

- `reference_snapshot.bmp`
- folder-local traceability log for the snapshot folder
- no recording CSV log, because this is not a recording flow

### Expected Host / Log / Traceability Behavior

- `status` returns a successful bounded host envelope
- `snapshot` returns a successful bounded host envelope with saved path and confirmed settings
- the snapshot folder contains traceability output in the current baseline format
- the offline focus-report command succeeds on the saved `BMP`

### What Counts As Success

- the snapshot command succeeds
- the `.bmp` file exists under `captures/reference_snapshot/`
- traceability exists for the folder
- the offline focus-report command produces one valid report line for the saved file

## 2. Bounded Recording Reference Scenario

### Purpose

Verify the current bounded image-series baseline:

- initialize through the bounded command surface
- run one short bounded recording
- confirm artifacts, run/log behavior, and traceability
- confirm the subsystem returns to idle usable state afterwards

### When To Run

- after changes around recording, writer behavior, save-directory handling, run identity, or traceability
- after bounded recording lifecycle fixes
- when you need one practical image-series confidence scenario

### What It Proves

- bounded recording works through the current command surface
- a recording run produces artifacts, a recording log, and traceability
- confirmed-settings and final status remain plausible
- the system returns to a usable non-recording state after completion

### What It Does Not Prove

- detached recording lifecycle control
- trigger-based recording
- long-duration stability
- broad transport/API behavior

### Commands

Preferred bounded reference run:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli status --source simulated
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli recording --source simulated --base-directory .\captures\reference_recording --file-stem reference_recording --file-extension .bmp --frame-limit 3
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli status --source simulated
```

Real-device substitution when explicitly needed:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli recording --source hardware --camera-alias tested_camera --configuration-profile default --base-directory .\captures\reference_recording --file-stem reference_recording --file-extension .bmp --frame-limit 5
```

### Expected Output Directory

- `captures/reference_recording/`

### Expected Artifacts

- bounded image series such as `reference_recording_000000.bmp`
- one recording CSV log such as `reference_recording_recording_log.csv`
- folder-local traceability output for the recording folder

### Expected Host / Log / Traceability Behavior

- the recording command returns a successful bounded host envelope
- the result contains `frames_written`, `stop_reason`, bounded recording limits, and current confirmed settings
- traceability is present for the recording folder
- a follow-up `status` call reports an idle non-recording state

### What Counts As Success

- the recording command succeeds
- at least the expected bounded number of artifacts exists in `captures/reference_recording/`
- the recording CSV log exists
- traceability exists for the folder
- a follow-up `status` run is successful and shows no active recording

## 3. Interval Capture Reference Scenario

### Purpose

Verify the current periodic capture baseline from the shared preview/stream path:

- initialize through the bounded command surface
- run one bounded interval capture
- verify active bounded capture behavior and final artifact output
- confirm the system returns to a usable state afterwards

### When To Run

- after changes around interval capture, polling, timing interpretation, or shared-stream behavior
- when you need one bounded periodic-capture confidence scenario

### What It Proves

- the current interval-capture path works through the bounded command surface
- bounded interval capture writes deterministic artifacts into the requested folder
- the final bounded result and final status remain plausible
- saved `BMP` artifacts remain reusable by the current offline path when the visible output variant is chosen

### What It Does Not Prove

- perfect scheduler stability
- traceability for interval capture
- recording lifecycle behavior
- broad hardware timing validation

### Commands

Preferred bounded reference run:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli status --source simulated
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli interval-capture --source simulated --base-directory .\captures\reference_interval --file-stem reference_interval --file-extension .bmp --interval-seconds 0.10 --frame-limit 3
.\.venv\Scripts\python.exe -m vision_platform.apps.postprocess_tool .\captures\reference_interval
```

Real-device substitution when explicitly needed:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.camera_cli interval-capture --source hardware --camera-alias tested_camera --base-directory .\captures\reference_interval --file-stem reference_interval --file-extension .bmp --interval-seconds 0.25 --frame-limit 3
```

### Expected Output Directory

- `captures/reference_interval/`

### Expected Artifacts

- bounded image series such as `reference_interval_000000.bmp`
- no recording CSV log, because this is not the recording path
- no snapshot/recording traceability guarantee in the current baseline for interval capture

### Expected Host / Log / Traceability Behavior

- the interval-capture command returns a successful bounded host envelope
- the result contains `frames_written`, `stop_reason`, accepted interval bounds, and confirmed settings
- final status shows no active interval capture
- the offline focus-report command succeeds on the saved `BMP` series

### What Counts As Success

- the interval-capture command succeeds
- the expected bounded number of artifacts exists in `captures/reference_interval/`
- the final result reports the expected frame count and bounded stop reason
- the offline focus-report command succeeds on the output directory
