# wx Shell Feature Inventory

## Purpose

This document records the current implemented surface of the bounded wxPython local shell and the boundary between shared headless core logic and UI-local behavior.

## Implemented Functions

- simulated or hardware-backed preview window with image area
- snapshot trigger through the existing command-controller path
- shared status-line display derived from the extracted preview-status model
- focus status visibility and toggle using the shared focus-preview service
- visible in-image focus marker / label above the shared focus-preview output
- fit/zoom, crosshair, and rectangle/ellipse ROI entry through the shared display-service layers
- visible point and ROI corner anchors with bounded hover and first drag behavior
- ROI body panning with `Shift` dominant-axis projection and `Esc` cancel-to-start behavior
- `Ctrl+C` point-copy behavior aligned with the current OpenCV operator path
- recording start/stop controls with `Max Frames` and `Recording FPS`
- recording progress and the latest recording summary in the shell status area
- camera and UI cadence readouts in the shell header
- reuse of the same alias, configuration-profile, and configuration-override semantics already used by the camera CLI

## Shared Core Ownership

These responsibilities stay in the shared headless core:

- bootstrap and startup wiring
- command controller
- live stream acquisition and preview buffering
- display geometry and coordinate mapping
- preview interaction state and command transitions
- preview-status model creation
- focus evaluation and focus overlay data
- recording and snapshot semantics

## UI-Local Ownership

These responsibilities stay in the wx shell:

- wx window layout and button arrangement
- bitmap rendering and canvas repainting
- event translation from wx events into shared interaction commands
- status text presentation and layout
- clipboard integration
- local menu / shortcut affordances
- transient operator feedback for the running shell

## Current Boundaries

- the shell should render and route input, but it should not own camera or recording semantics
- the shell should reuse shared models rather than building a parallel status model
- the shell may expose controls, but the control actions should continue to flow through the shared controller surface
- live command sync remains out of scope for this inventory and is deferred to a later slice

## Known Gaps

- full configuration UI is still deferred
- menu-driven settings flows are still deferred
- live CLI/API sync for an already open shell is still deferred
- non-OpenCV renderer abstraction is still deferred

