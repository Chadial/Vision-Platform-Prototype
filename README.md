# Vision Platform Prototype

Python prototype with Allied Vision Vimba X integration.

## What This Repository Is

This repository is the Python prototype baseline for a modular vision platform.

Its purpose is to:

- validate camera, preview, snapshot, recording, ROI, and focus-related workflows in Python
- keep the architecture clean enough for later handover to a C#/.NET team
- preserve a simulator-backed development path when hardware is unavailable
- prepare a UI-agnostic core that can later support desktop, host-integrated, or web-capable frontends

This is not intended to be a finished end-user product yet. It is the working technical baseline and architecture reference for later phases.

## Where To Read Next

- For the shortest possible project overview, read [`docs/SESSION_START.md`](docs/SESSION_START.md).
- For the current verified implementation state, read [`docs/STATUS.md`](docs/STATUS.md).
- For the long-term product and architecture target, read [`docs/ProjectDescription.md`](docs/ProjectDescription.md).

The current goal is not to build a full UI, but to establish a maintainable application core with:

- Allied Vision / Vimba X camera integration
- camera driver isolation
- explicit command and status models
- snapshot and recording services
- future compatibility with external host control
- future portability to desktop UI and web UI

The repository is now also organized as the first step toward a broader modular vision platform. Legacy compatibility remains under `src/camera_app`, while the platform-facing implementation is being moved incrementally into `src/vision_platform` and the repository-level module workspaces for:

- camera integration
- stream/frame orchestration
- recording/persistence
- OpenCV prototype apps
- shared common models
- ROI and focus foundations
- UI/display-oriented preview experiments

## Current State

The repository is currently a simulator-validated Python prototype with:

- a core architecture built for Allied Vision / Vimba X while keeping SDK-specific code isolated in the driver layer
- clean driver/service/storage/control separation
- `CameraStreamService` as the intended orchestration point for shared live acquisition
- `camera_app.bootstrap` as the intended composition point for wiring the subsystem consistently
- working simulated preview, snapshot, interval capture, recording, and host-style command flow
- an optional shared-acquisition path so preview and recording can consume the same live frame stream
- `IntervalCaptureService` for timed single-image saving from the shared live stream
- optional OpenCV-based preview inspection and grayscale-safe export paths
- a first real-hardware OpenCV preview path with viewport-based `fit-to-window` and zoom controls
- ROI mask primitives for rectangle and ellipse selections
- a first manual-focus baseline with ROI-aware evaluation hooks
- UI-free overlay-payload composition for preview/snapshot-adjacent consumers

Real hardware is available again for targeted preview and smoke validation, but the repository should still not yet be treated as fully hardware-validated. For the verified implementation state and roadmap position, use [`docs/STATUS.md`](docs/STATUS.md) together with [`docs/ROADMAP.md`](docs/ROADMAP.md) and [`docs/GlobalRoadmap.md`](docs/GlobalRoadmap.md).

## Repository Layout

```text
apps/
camera_app/
captures/
configs/
docs/
integrations/
libraries/
services/
scripts/
  launchers/
src/
  camera_app/
  vision_platform/
tests/
tools/
```

Repository-level module workspaces now contain `README.md`, `STATUS.md`, and `ROADMAP.md` files so the platform can be evolved per module. Launcher-style helper scripts and the minimal Vimba SDK smoke test now live under `scripts/launchers/` instead of cluttering the repository root.

The root-level project guidance documents currently in active use are:

- [`docs/SESSION_START.md`](docs/SESSION_START.md)
- [`Agents.md`](Agents.md)
- [`docs/ProjectDescription.md`](docs/ProjectDescription.md)
- [`docs/ProjectAgents.md`](docs/ProjectAgents.md)
- [`docs/MODULE_INDEX.md`](docs/MODULE_INDEX.md)
- [`docs/GlobalRoadmap.md`](docs/GlobalRoadmap.md)

## Planned Architecture

- `models`: request, configuration, and status objects
- `drivers`: SDK-specific camera access only
- `services`: preview, snapshot, recording, and orchestration logic
- `storage`: file naming and frame writing
- `control`: host-facing command surface
- `logging`: central logging setup

The new platform-facing namespace mirrors that structure at a higher level:

- `vision_platform.integrations.camera`
- `vision_platform.services.stream_service`
- `vision_platform.services.recording_service`
- `vision_platform.apps.opencv_prototype`
- `vision_platform.libraries.common_models`
- `vision_platform.libraries.roi_core`
- `vision_platform.libraries.focus_core`

Current preview/display architecture rule:

- camera drivers and core services expose frames plus metadata
- viewport management such as fit-to-window, zoom, pan, and display-space overlay transforms belongs in the UI/display layer
- the OpenCV prototype is the current place for validating those operator-facing preview behaviors

## Setup

There are two different setup paths in this repository:

1. repository-only setup for simulator work
2. hardware setup with the full Allied Vision Vimba X environment

If you only want to work on simulator-backed flows, OpenCV demos, or documentation, you do not need the Vimba X SDK immediately.

If you want to access a real camera, you need both:

- the project installed into the virtual environment
- the Vimba X SDK installed on the machine
- the `vmbpy` wheel from that local Vimba X installation installed into the same virtual environment

1. Create and activate a virtual environment.
2. Install the camera SDK Python package that matches the target camera environment.
3. Install this project in editable mode when the package work begins.

Example:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

The repository keeps dependency setup minimal:

- `pip install -e .` for the core package
- `pip install -e .[opencv]` for the optional OpenCV path
- `.python-version`: preferred local Python version hint for tools such as `pyenv` and IDEs

Typical Windows setup:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

One-command Windows bootstrap:

```powershell
.\scripts\bootstrap.ps1
```

Optional variants:

```powershell
.\scripts\bootstrap.ps1 -IncludeOpenCv
.\scripts\bootstrap.ps1 -Dev
.\scripts\bootstrap.ps1 -RecreateVenv
.\scripts\bootstrap.ps1 -VmbPyWheel "C:\Path\To\vmbpy-X.Y.Z-py-none-any.whl"
.\scripts\bootstrap.ps1 -IncludeOpenCv -VmbPyWheel "C:\Path\To\vmbpy-X.Y.Z-py-none-any.whl"
```

## Vimba X Setup

This project uses **Allied Vision Vimba X** for camera access.

### What an external developer needs to know first

For real hardware, a plain repository checkout is not enough.

The hardware path depends on two separate things:

1. the Allied Vision Vimba X SDK installed on Windows
2. the Python binding `vmbpy` installed from the local wheel that comes with that SDK

In practice this means:

- `pip install -e .` installs this repository
- it does not install the Vimba X SDK
- it does not install camera drivers or transport layers
- it does not magically provide `vmbpy`

The usual and intended workflow is therefore:

1. install Vimba X on the machine
2. create the project virtual environment
3. install this repository
4. install `vmbpy` from the local wheel shipped with Vimba X into that same virtual environment
5. verify camera enumeration

You normally do not "generate" the wheel yourself. In the standard setup, the wheel is already included in the installed Vimba X SDK and only needs to be located and installed.

### Where to get Vimba X

Download the official SDK from the Allied Vision Vimba X download page.

Recommended Windows package:

- `VimbaX_Setup-2026-1-Win64.exe`

Vimba X includes:

- C, C++, .NET, and Python APIs
- Viewer
- Camera Simulator
- ImageTransform library
- examples

### Windows installation

1. Download and install **Vimba X** from the official Allied Vision website.
2. If you use an **Alvium USB** camera, connect it during installation if possible so the USB driver can be installed automatically.
3. After installation, useful locations are typically:
   - Viewer / Driver Installer: `Vimba X/bin`
   - Examples: `C:\Users\Public\Documents\Allied Vision\Vimba X`
   - Documentation: included in the SDK installation and also available online

After installation, locate the `vmbpy` wheel that ships with the SDK. The exact folder can vary by SDK version and installation layout, so do not hardcode a guessed path in the repository docs or scripts. Search inside the Vimba X installation directory for a file matching:

- `vmbpy-*.whl`

Typical places are under SDK-provided Python, API, wheel, or examples directories.

### Python requirements

- Python **3.10 or higher**
- 64-bit Python is recommended on 64-bit systems

Check your Python setup:

```powershell
python --version
python -m pip --version
```

### Install VmbPy into the project environment

`VmbPy` is provided as a local `.whl` file inside the Vimba X installation directory.

Use the **local wheel from the Vimba X installation**, not a guessed package name.

Recommended sequence:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
.\.venv\Scripts\python.exe -m pip install "C:\Path\To\vmbpy-X.Y.Z-py-none-any.whl"
```

Example:

```powershell
python -m pip install "C:\Path\To\vmbpy-X.Y.Z-py-none-any.whl"
```

Optional extras for NumPy and OpenCV:

```powershell
python -m pip install "C:\Path\To\vmbpy-X.Y.Z-py-none-any.whl[numpy,opencv]"
```

If you want to fold that into the project bootstrap, pass the wheel path directly:

```powershell
.\scripts\bootstrap.ps1 -VmbPyWheel "C:\Path\To\vmbpy-X.Y.Z-py-none-any.whl"
```

Or for the OpenCV-enabled path:

```powershell
.\scripts\bootstrap.ps1 -IncludeOpenCv -VmbPyWheel "C:\Path\To\vmbpy-X.Y.Z-py-none-any.whl"
```

### Why install from the local wheel?

The local Vimba X wheel is the recommended installation source for `VmbPy`.

Installing from PyPI alone does **not** include other essential Vimba X components such as:

- transport layers
- drivers

That is why repository setup and hardware setup are deliberately treated as separate steps in this project.

### Short checklist for external setup

Use this when onboarding a new machine:

1. install Vimba X
2. verify the camera is visible in the Vimba X Viewer or simulator tooling
3. create the project `.venv`
4. install this repository with `pip install -e .`
5. install `vmbpy` from the local Vimba X wheel into that same `.venv`
6. run the minimal SDK check
7. only then run project hardware smoke or preview commands

### First verification

After installation, verify that `vmbpy` works:

```python
from vmbpy import *

with VmbSystem.get_instance() as vmb:
    cams = vmb.get_all_cameras()
    print(cams)
```

If cameras are listed, the SDK and Python binding are working.

Repository-specific verification command:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\test_vimba.py
```

If this command lists cameras, the local SDK installation, Python binding, and project environment are aligned correctly.

### Notes

- This project is currently developed and tested on **Windows**.
- For USB cameras, a USB 3.0 or higher controller is required.
- Viewer and Camera Simulator are useful for initial testing before real hardware is available.

## OpenCV

OpenCV is currently optional.

Install the optional path only when local preview windows or lossless grayscale export beyond the standard-library PNG path are needed:

```powershell
pip install -e .[opencv]
```

Use it for:

- preview frame conversion for a UI
- `cv2.imshow()` based local stream inspection
- lossless grayscale `.png` / `.tiff` export for higher bit depth frames
- additional image processing

The core services still work without OpenCV. The standard writer keeps handling `Mono8`, `Rgb8`, and `Bgr8` PNG output without extra dependencies. The optional OpenCV adapter stays in a separate imaging layer on top of `PreviewService` and `FrameWriter`.

## How To Check A Repo Quickly

For this repository, the intended order is:

1. Read [`Agents.md`](Agents.md) for startup rules, git discipline, and the required document order.
2. Read [`docs/SESSION_START.md`](docs/SESSION_START.md) for the compact current baseline and task-based reading map.
3. Read [`docs/MODULE_INDEX.md`](docs/MODULE_INDEX.md) to locate the relevant module docs quickly.
4. Read [`docs/STATUS.md`](docs/STATUS.md) for the current verified implementation baseline.
5. Read [`docs/ROADMAP.md`](docs/ROADMAP.md) and [`docs/GlobalRoadmap.md`](docs/GlobalRoadmap.md) only when planning or architectural context is needed.
6. Read [pyproject.toml](pyproject.toml) for the supported Python version and dependency source of truth.
7. Use `.python-version` as the preferred interpreter hint.
8. Use [`scripts/bootstrap.ps1`](scripts/bootstrap.ps1) for fast Windows setup, or this README for the exact manual commands.

## Subsystem Bootstrap

For application code, prefer the Python-side bootstrap helpers instead of manually instantiating every service:

- `build_camera_subsystem(driver)` for a provided driver
- `build_simulated_camera_subsystem(...)` for the simulator-backed path

These helpers wire:

- `CameraService`
- `SnapshotService`
- `CameraStreamService`
- `RecordingService`
- `IntervalCaptureService`
- `CommandController`

from one consistent composition root.

## Next Implementation Steps

See [`docs/ROADMAP.md`](docs/ROADMAP.md).

For the repository reorganization state and target module layout, see:

- [`docs/project_overview.md`](docs/project_overview.md)
- [`docs/current_state.md`](docs/current_state.md)
- [`docs/target_structure.md`](docs/target_structure.md)
- [`docs/migration_plan.md`](docs/migration_plan.md)
- [`docs/git_strategy.md`](docs/git_strategy.md)
- [`docs/branch_backlog.md`](docs/branch_backlog.md)
- [`docs/MODULE_INDEX.md`](docs/MODULE_INDEX.md)

For host-facing command formulation and request examples, see [`docs/COMMANDS.md`](docs/COMMANDS.md).
For real-device validation steps, see [`docs/HARDWARE_EVALUATION.md`](docs/HARDWARE_EVALUATION.md).

## Verified Simulator Test Block

Run the current simulator-/service-focused verification block with:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_snapshot_service tests.test_frame_writer tests.test_snapshot_smoke tests.test_preview_service tests.test_file_naming tests.test_recording_service tests.test_interval_capture_service tests.test_camera_stream_service tests.test_bootstrap tests.test_simulated_camera_driver tests.test_simulated_demo tests.test_command_flow_demo tests.test_command_controller tests.test_request_models tests.test_opencv_adapter tests.test_opencv_preview tests.test_opencv_smoke_demos
```

## Smoke Test

Run the minimal end-to-end snapshot smoke test with an explicit camera id and output directory:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_snapshot_smoke.py --camera-id example_camera_id --save-directory .\captures\smoke --pixel-format Mono8
```

The command prints the saved snapshot path on success.

## Simulated Demo

Run the hardware-free simulation path with generated frames:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_simulated_demo.py --save-directory .\captures\simulated --file-stem demo
```

This demo performs snapshot saving, interval-based single-image saving from the shared preview stream, and a short recording in one run.

Example with explicit interval-capture settings:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_simulated_demo.py --save-directory .\captures\simulated --file-stem demo --interval-seconds 0.25 --interval-frame-count 5 --frame-limit 3
```

Optional sample images can be provided from a directory containing `.pgm` or `.ppm` files:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_simulated_demo.py --save-directory .\captures\simulated --sample-dir .\demo_samples
```

## Simulated Command Flow Demo

Run a host-style command sequence through the `CommandController` with the simulated driver:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_command_flow_demo.py --base-directory .\captures\commands --run-name run_001 --frame-limit 3 --target-frame-rate 10
```

This command-flow demo also exercises interval capture from the shared preview stream before starting the recording flow.

Example with explicit interval-capture settings:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_command_flow_demo.py --base-directory .\captures\commands --run-name run_001 --interval-seconds 0.5 --interval-frame-count 4 --frame-limit 3 --target-frame-rate 10
```

## Optional OpenCV Preview Demo

Run the optional OpenCV-backed preview window on top of the simulated preview service:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_opencv_preview_demo.py --frame-limit 100
```

To also compose focus state during preview rendering:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_opencv_preview_demo.py --frame-limit 100 --with-focus
```

Optional sample images can be loaded from a directory containing `.pgm` or `.ppm` files:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_opencv_preview_demo.py --sample-dir .\demo_samples
```

## Optional Hardware Preview Demo

Run the optional OpenCV-backed hardware preview window against a real Vimba X camera:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_hardware_preview_demo.py --camera-id DEV_1AB22C046D81
```

Current prototype controls:

- `i`: zoom in
- `o`: zoom out
- `f`: fit-to-window
- `q` / `Esc`: quit
- window `X`: quit

The next OpenCV prototype UI block is planned around:

- status bar / lower info band
- crosshair and focus-display toggles
- ROI tools for rectangle and ellipse masks
- cursor-aware zoom and later pan
- an operator-facing menu/control band for sensor geometry, shutter time, storage behavior, frame limits, and focus method selection

## Simulated Focus Preview Demo

Run the simulator-backed preview-to-focus smoke path without opening a full preview workflow:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_focus_preview_demo.py
```

This path exercises preview acquisition, focus evaluation, and overlay-anchor derivation on the simulator-backed route.

## Optional OpenCV Save Demo

Save one simulated grayscale frame through the optional OpenCV-backed lossless save path:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_opencv_save_demo.py --save-directory .\captures\opencv_save_demo
```

Example with explicit `Mono8` PNG output:

```powershell
.\.venv\Scripts\python.exe .\scripts\launchers\run_opencv_save_demo.py --save-directory .\captures\opencv_save_demo --pixel-format Mono8 --file-extension .png
```
