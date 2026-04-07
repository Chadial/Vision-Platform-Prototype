# WP64 wx Menu And Settings Dialog Baseline

## Purpose

Add a bounded menu and settings-dialog surface to the wx shell so the current working frontend can expose save/configuration controls more clearly without turning into a broad desktop-product UI project.

## Closure lane

- Usable Camera Subsystem / Pre-Product Baseline

## Slice role

- bounded local usability extension

## Scope level

- first menu and popup-driven settings baseline

## Branch

- intended branch: `feature/wx-menu-settings-baseline`
- activation state: landed

## Scope

Included:

- a small menu bar with first practical entries
- popup-driven input for save-directory and bounded recording settings
- reuse of the shared controller/configuration path instead of UI-private settings logic

Excluded:

- broad docking or toolbar work
- full camera configuration workstation
- product-level desktop shell redesign
- remote control / live-sync transport changes

## Validation

- start the wx shell, open the bounded settings/menu path, change one save/configuration value, and confirm the shell reflects it through the shared status/controller path

## Implementation Status

Implemented on `feature/wx-menu-settings-baseline` as a bounded local-usability extension:

- wx menu bar with `File -> Set Save Directory...` and `Settings -> Recording Settings...`
- save-directory dialog wired to the existing controller path via `SetSaveDirectoryRequest(mode=\"append\")`
- recording-settings dialog for `file_stem`, `file_extension`, `max_frames`, and `recording_fps`
- `Start Recording` now reuses the configured recording settings values
- targeted wx-shell tests for recording-settings application and start-recording request wiring

Validation evidence:

- unit validation passed for wx-shell, snapshot-service, recording-service, and live-command-sync coverage
- manual hardware verification on April 7, 2026 confirmed:
  - `File` / `Settings` menu visibility
  - working save-directory dialog path
  - working recording-settings dialog path
  - visible `recording_fps` status update
  - bounded recording start/stop from menu-configured values
  - visible retained recording progress summary after auto stop
  - snapshot success after recording without shared trace-log permission failure
