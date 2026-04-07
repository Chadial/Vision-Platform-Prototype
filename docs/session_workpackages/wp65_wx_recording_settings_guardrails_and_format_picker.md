# WP65 wx Recording Settings Guardrails And Format Picker

## Purpose

Tighten the bounded wx recording-settings dialog so common recording-output choices are guided instead of relying on free-form extension typing.

## Closure lane

- Usable Camera Subsystem / Pre-Product Baseline

## Slice role

- bounded local usability follow-up

## Scope level

- one small dialog/input hardening follow-up

## Branch

- intended branch: `feature/wx-recording-settings-guardrails`
- activation state: current next

## Scope

Included:

- replace the free-form recording file-extension text field with a bounded picker
- expose only the currently supported / intended recording output extensions for the wx shell
- keep `file_stem`, `max_frames`, and `recording_fps` in the same bounded dialog
- keep the start-recording path on the existing controller/request surface

Excluded:

- broad recording-format capability discovery
- full settings workstation
- host/API configuration expansion
- per-camera dynamic format policy UI

## Validation

- open the wx recording-settings dialog and confirm the file-extension field is a picker instead of free text
- select one valid format, start recording, and confirm the chosen format is used
- confirm invalid-extension typing is no longer needed for the common path

## Headless Follow-Up Note

- this slice is UI-local guardrail work only
- recording-format policy still belongs in shared request validation and save-path behavior, not in wx-only logic
