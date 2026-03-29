# Operator Surface Template

## Purpose

This document captures a lightweight structure/template for a future operator-facing camera surface.

It is intentionally not tied to a specific GUI toolkit.
For the current OpenCV prototype, it should be read only as a layout and responsibility guide, not as a commitment to implement real widgets in HighGUI.

## Scope Boundary

What this template is for:

- preserving the intended operator-facing information architecture
- keeping future desktop or host-embedded UI work aligned with the current prototype
- separating MVP preview interaction from later comfort/UI work

What this template is not:

- not a commitment to build a real menu UI in the current OpenCV branch
- not a replacement for module `STATUS.md` or `ROADMAP.md`
- not a commitment to any specific toolkit such as Tkinter, Qt, WPF, or web UI

## Design Principles

- keep camera, stream, recording, and storage logic outside the UI layer
- keep UI state separate from camera-driver state
- prefer status visibility and operator clarity over decorative UI
- treat OpenCV/HighGUI as a temporary operator prototype, not as the long-term desktop UI
- preserve a later migration path to a C#/.NET operator surface

## Surface Zones

### 1. Preview Viewport

Purpose:

- show the current live image
- preserve aspect ratio
- support zoom/pan/fit behavior
- host lightweight overlays such as crosshair and ROI outlines

Current OpenCV baseline:

- fit-to-window
- keyboard zoom
- wheel zoom
- middle-drag pan
- top-left anchoring
- visible image-bound outline when padding is present
- point selection
- ROI creation baseline

### 2. Status Band

Purpose:

- hold operator feedback that should not cover image pixels
- make transient actions and warnings visible

Current OpenCV baseline:

- preview mode
- zoom factor
- viewport origin in zoom mode
- FPS
- selected point coordinates
- warning messages
- transient action messages
- focus-state line when available
- ROI-mode/ROI-preview status

### 3. Optional Operator Strip

Purpose:

- provide a future place for a small set of operator-facing controls or summarized settings
- stay lightweight in the OpenCV prototype if ever added there

Important constraint:

- in the current OpenCV path this means, at most, an extra composed strip or text-guided control area
- this does not mean real GUI widgets inside HighGUI

Potential control groups:

- acquisition:
  - exposure time
  - frame limit
  - snapshot action
- storage:
  - save directory
  - append vs. new subfolder
- tools:
  - crosshair toggle
  - ROI mode
  - focus overlay toggle
- geometry:
  - width
  - height
  - offset X
  - offset Y

## Suggested Information Hierarchy

Priority 1:

- live image
- warnings/errors
- current operator action feedback

Priority 2:

- zoom state
- viewport state
- selected point / ROI state
- focus status

Priority 3:

- editable configuration controls
- save-path choices
- more advanced analysis toggles

## Suggested Operator Grouping

For this project, prefer operator-facing groups over generic desktop menu names such as `File`, `View`, and `Settings`.

Recommended top-level grouping:

- `Capture`
- `View`
- `ROI`
- `Camera`
- `Storage`
- `Analysis`

Rationale:

- these labels match the actual operator tasks better than a generic desktop-app menu model
- they map more cleanly to the current CLI/service boundaries
- they will still translate well into a later C#/.NET UI

### Capture

Purpose:

- actions that trigger acquisition or saving behavior

Potential entries:

- snapshot
- start recording
- stop recording
- frame limit
- run/session behavior

### View

Purpose:

- controls that only affect visual inspection and viewport behavior

Potential entries:

- fit to window
- zoom in
- zoom out
- reset view
- toggle crosshair
- toggle focus status
- show/hide helper overlays

Suggested shortcut presentation:

```text
View
- Zoom In                I
- Zoom Out               O
- Fit To Window          F
- Toggle Crosshair       X
- Toggle Focus Status    Y
```

### ROI

Purpose:

- ROI tool selection and ROI-related actions

Potential entries:

- rectangle ROI
- ellipse ROI
- clear ROI
- later non-MVP ROI editing actions

Shortcut keys should be shown directly in the menu/strip text for ROI actions.

Suggested shortcut presentation:

```text
ROI
- Rectangle ROI          R
- Ellipse ROI            E
- Clear ROI              Del
```

### Camera

Purpose:

- camera-side acquisition parameters and geometry

Potential entries:

- exposure time
- gain
- pixel format
- sensor width
- sensor height
- offset X
- offset Y
- camera selection / camera id

### Storage

Purpose:

- save-path and file-output behavior

Potential entries:

- save directory
- append vs. new subfolder
- file stem / naming scheme
- snapshot format

### Analysis

Purpose:

- focus and later analysis behavior

Potential entries:

- focus method
- focus overlay/status
- later analysis modes

## UI vs. CLI/API Mapping

These operator groups should not be treated as UI-only ideas.
Where useful, they should map to the same service/controller capabilities that a later CLI or API can expose.

### Good candidates for shared UI + CLI/API capabilities

- `Capture`
- `Camera`
- `Storage`
- `Analysis`
- parts of `ROI`

Examples:

- `Capture`
  - UI: snapshot button or operator-strip action
  - CLI/API: save snapshot, start recording, stop recording
- `Camera`
  - UI: exposure, gain, pixel format, geometry fields
  - CLI/API: apply configuration request
- `Storage`
  - UI: save directory and naming behavior
  - CLI/API: set save directory, naming/file-format options
- `Analysis`
  - UI: focus method selection, focus visibility
  - CLI/API: analysis-method selection where host-facing use is justified
- `ROI`
  - UI: create/clear ROI visually
  - CLI/API: set ROI / clear ROI through explicit coordinates or ROI definitions

### Mostly UI-local groups

- `View`

Examples:

- fit to window
- zoom in/out
- reset view
- pan
- viewport-local helper overlays

These are normally preview-surface concerns, not host-control concerns.

## Shared Capability Principle

If an action belongs to camera operation, storage policy, capture flow, ROI definition, or analysis configuration, prefer defining it so that:

- a future UI can call it
- a future CLI can call it
- a future API/host can call it

If an action belongs only to local viewing behavior, keep it UI-local.

## OpenCV Interpretation

If this structure is used in the current OpenCV prototype, interpret it only as:

- a design template
- a possible lightweight operator strip
- a shortcut/help grouping model

Do not interpret it as a promise of a real native-style menu bar inside HighGUI.

## MVP vs. Non-MVP

MVP for the current OpenCV operator path:

- preview viewport
- status band
- point selection
- crosshair toggle
- focus visibility toggle behavior
- ROI mode entry and first ROI creation
- keyboard and wheel zoom
- pan baseline
- preview-frame snapshot shortcut

Non-MVP follow-up:

- richer ROI editing
- real menu widgets
- full configuration forms
- directory pickers
- structured settings panels
- operator/developer mode switching UI

## Text Layout Sketch

Example future surface, independent of toolkit:

```text
+--------------------------------------------------------------+
| Operator strip / summary controls (optional, lightweight)    |
+--------------------------------------------------------------+
|                                                              |
|                       Preview viewport                        |
|          image, crosshair, ROI, focus/overlay hints          |
|                                                              |
+--------------------------------------------------------------+
| mode | zoom | view origin | fps | point | roi | warnings     |
| focus state / transient operator feedback                    |
| shortcuts / operator hint line                               |
+--------------------------------------------------------------+
```

## Portability Notes

- the same surface structure should be representable in a later C# desktop UI
- host integration should treat preview, status, and controls as separate concerns
- save-path policy, camera configuration, and recording logic should remain service-driven, not UI-owned

## Recovery Use

If a later agent or developer resumes UI work:

1. read this template together with:
   - `apps/opencv_prototype/STATUS.md`
   - `apps/opencv_prototype/ROADMAP.md`
- `docs/session_workpackages/wp03_opencv_ui_operator_block.md`
2. confirm which parts are MVP baseline vs. non-MVP follow-up
3. decide whether the next step still belongs in OpenCV or should wait for a real UI frontend
