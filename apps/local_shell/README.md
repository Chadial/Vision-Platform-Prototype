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
- fit/zoom, crosshair, and rectangle/ellipse ROI entry through the shared display-service layers
- reuse of the same alias, configuration-profile, and configuration-override semantics already used by the camera CLI

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
- it does not yet provide full configuration or recording UI
- the OpenCV prototype remains the fallback/reference frontend
