# Camera Prototype

Python prototype for a camera subsystem that will later be handed over to a C#/.NET team.

The current goal is not to build a full UI, but to establish a maintainable application core with:

- camera driver isolation
- explicit command and status models
- snapshot and recording services
- future compatibility with AMB host control
- future portability to desktop UI and web UI

## Repository Layout

```text
src/
  camera_app/
    control/
    drivers/
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

## OpenCV

OpenCV is currently optional.

Use it later only if one of these becomes necessary:

- preview frame conversion for a UI
- image encoding convenience
- additional image processing

For the first prototype stage, keep the dependency surface small and start with the SDK plus standard library where possible.

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
