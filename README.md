# Camera Subsystem Prototype

Python prototype for a camera subsystem that will later be handed over to a C#/.NET team.

The current goal is not to build a full UI, but to establish a maintainable application core with:

- camera driver isolation
- explicit command and status models
- snapshot and recording services
- future compatibility with external host control
- future portability to desktop UI and web UI

## Repository Layout

```text
src/
  camera_app/
    control/
    drivers/
    imaging/
    logging/
    models/
    services/
    storage/
tests/
docs/
test_vimba.py
```

`test_vimba.py` is kept as a minimal SDK smoke test and is not part of the planned application structure.

## Planned Architecture

- `models`: request, configuration, and status objects
- `drivers`: SDK-specific camera access only
- `services`: preview, snapshot, recording, and orchestration logic
- `storage`: file naming and frame writing
- `control`: host-facing command surface
- `logging`: central logging setup

## Setup

1. Create and activate a virtual environment.
2. Install the camera SDK Python package that matches the target camera environment.
3. Install this project in editable mode when the package work begins.

Example:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

Quick-install files are also available for users who prefer `pip install -r ...`:

- `requirements.txt`: core project install
- `requirements-opencv.txt`: core install plus optional OpenCV preview/grayscale path
- `requirements-dev.txt`: current developer baseline
- `.python-version`: preferred local Python version hint for tools such as `pyenv` and IDEs

Typical Windows setup:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
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

### First verification

After installation, verify that `vmbpy` works:

```python
from vmbpy import *

with VmbSystem.get_instance() as vmb:
    cams = vmb.get_all_cameras()
    print(cams)
```

If cameras are listed, the SDK and Python binding are working.

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

Or, with the convenience file:

```powershell
pip install -r requirements-opencv.txt
```

Use it for:

- preview frame conversion for a UI
- `cv2.imshow()` based local stream inspection
- lossless grayscale `.png` / `.tiff` export for higher bit depth frames
- additional image processing

The core services still work without OpenCV. The standard writer keeps handling `Mono8`, `Rgb8`, and `Bgr8` PNG output without extra dependencies. The optional OpenCV adapter stays in a separate imaging layer on top of `PreviewService` and `FrameWriter`.

## How To Check A Repo Quickly

For this repository, the intended order is:

1. Read [pyproject.toml](pyproject.toml) for the supported Python version and dependency source of truth.
2. Use `.python-version` as the preferred interpreter hint.
3. Pick one of the requirements files for the install path you need.
4. Use [`scripts/bootstrap.ps1`](scripts/bootstrap.ps1) for fast Windows setup, or this README for the exact manual commands.

## Next Implementation Steps

See [`docs/ROADMAP.md`](docs/ROADMAP.md).

For host-facing command formulation and request examples, see [`docs/COMMANDS.md`](docs/COMMANDS.md).
For real-device validation steps, see [`docs/HARDWARE_EVALUATION.md`](docs/HARDWARE_EVALUATION.md).

## Smoke Test

Run the minimal end-to-end snapshot smoke test with an explicit camera id and output directory:

```powershell
.\.venv\Scripts\python.exe .\run_snapshot_smoke.py --camera-id cam2 --save-directory .\captures\smoke --pixel-format Mono8
```

The command prints the saved snapshot path on success.

## Simulated Demo

Run the hardware-free simulation path with generated frames:

```powershell
.\.venv\Scripts\python.exe .\run_simulated_demo.py --save-directory .\captures\simulated --file-stem demo
```

Optional sample images can be provided from a directory containing `.pgm` or `.ppm` files:

```powershell
.\.venv\Scripts\python.exe .\run_simulated_demo.py --save-directory .\captures\simulated --sample-dir .\demo_samples
```

## Simulated Command Flow Demo

Run a host-style command sequence through the `CommandController` with the simulated driver:

```powershell
.\.venv\Scripts\python.exe .\run_command_flow_demo.py --base-directory .\captures\commands --run-name run_001 --frame-limit 3 --target-frame-rate 10
```

## Optional OpenCV Preview Demo

Run the optional OpenCV-backed preview window on top of the simulated preview service:

```powershell
.\.venv\Scripts\python.exe .\run_opencv_preview_demo.py --frame-limit 100
```

Optional sample images can be loaded from a directory containing `.pgm` or `.ppm` files:

```powershell
.\.venv\Scripts\python.exe .\run_opencv_preview_demo.py --sample-dir .\demo_samples
```
