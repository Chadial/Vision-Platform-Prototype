# Local Shell

## Purpose

Provides one bounded local wxPython working shell above the existing platform core.

It exists to offer a more practical daily-use local frontend than the current OpenCV window path without turning frontend work into a new platform core.

## Responsibility

- expose one optional wxPython desktop shell for the current Python baseline
- reuse the existing bootstrap, command-controller, stream, geometry, interaction, and preview-status layers
- keep the shell aligned with the proven OpenCV preview path for the first feature cut

## Functions

- simulated or hardware-backed preview window with image area
- snapshot trigger through the existing command-controller path
- shared status-line display derived from the extracted preview-status model
- focus status visibility and toggle using the shared focus-preview service
- visible in-image focus marker / label above the shared focus-preview output
- fit/zoom, crosshair, and rectangle/ellipse ROI entry through the shared display-service layers
- visible point and ROI corner anchors with bounded hover and first drag behavior
- `Ctrl+C` point-copy behavior aligned with the current OpenCV operator path
- reuse of the same alias, configuration-profile, and configuration-override semantics already used by the camera CLI

## Implemented Surface

- preview rendering through a bounded wx canvas over the shared preview stream
- snapshot trigger through the existing command-controller path
- focus visibility, focus marker, and focus-score reporting through the shared focus-preview service
- crosshair visibility plus point-copy behavior aligned with the current OpenCV baseline
- rectangle and ellipse ROI entry, hover emphasis, corner anchors, and bounded drag interaction
- ROI body panning with `Shift` dominant-axis projection and `Esc` cancel-to-start behavior
- recording start/stop controls with `Max Frames` and `Recording FPS`
- recording progress and the latest recording summary in the shell status area
- camera and UI cadence readouts in the shell header

See [`FEATURES.md`](FEATURES.md) for the full implemented wx shell inventory.

## Core vs UI

- shared headless core responsibilities: bootstrap, command controller, stream service, display geometry, preview interaction, preview-status models, and focus preview evaluation
- UI-local responsibilities: wx windowing, button layout, bitmap rendering, event translation, status text presentation, clipboard integration, and menu/shortcut affordances
- the shell is allowed to decide how to draw and route input, but it should not own camera semantics, recording semantics, or duplicate shared status models
- future live command sync should observe shared state instead of pushing new camera logic into the UI layer

## Dependencies

- `vision_platform.bootstrap`
- `vision_platform.services.stream_service`
- `vision_platform.services.display_service`
- optional `wxPython`

## Usage

Install the optional shell dependency in the project environment:

```powershell
.\.venv\Scripts\python.exe -m pip install wxPython
```

Preferred start path:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell
```

Current example:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell --snapshot-directory .\captures\wx_shell_snapshot
```

Bounded hardware-backed example on the tested path:

```powershell
.\.venv\Scripts\python.exe -m vision_platform.apps.local_shell --source hardware --camera-alias tested_camera --configuration-profile default --snapshot-directory .\captures\wx_shell_snapshot
```

## Boundaries

- this shell is optional and local-only
- it does not replace the host-neutral controller/core
- it now reuses the same headless startup semantics as the CLI for `source`, alias resolution, configuration profiles, and explicit configuration overrides
- current point-copy and focus-visibility behavior intentionally follow the already proven OpenCV prototype semantics where practical
- current anchor rendering and drag behavior are intentionally bounded to fixed-point movement and ROI corner updates, not full desktop vector editing
- it does not yet provide full configuration or recording UI
- the OpenCV prototype remains the fallback/reference frontend
- the documented wx feature surface intentionally stays narrower than the full future desktop-product direction
