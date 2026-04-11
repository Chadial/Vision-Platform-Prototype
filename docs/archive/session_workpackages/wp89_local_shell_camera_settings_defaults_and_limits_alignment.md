# WP89 Local Shell Camera Settings Defaults And Limits Alignment

## Goal

Align the wx shell camera-settings dialog with the camera-class default JSON and the current camera capability limits so the dialog opens with sensible defaults, including corrected width/height and pixel-format defaults for the tested hardware path.

## Status

Completed after implementation.

## Scope

- preload camera-class defaults from `configs/camera_configuration_profiles.json`
- use the current capability profile to expose limits and step guidance in the dialog
- clamp or normalize entered values to the allowed hardware increment/range before apply
- keep the shell menu dialog reachable even when apply availability changes
- correct the tested hardware baseline where the original dialog showed stale width/height and pixel-format values

## Out Of Scope

- new profile-editing UI
- broad camera-configuration management
- a new settings persistence format

## Affected Areas

- `src/vision_platform/apps/local_shell/camera_settings_service.py`
- `src/vision_platform/apps/local_shell/wx_preview_shell.py`
- `configs/camera_configuration_profiles.json`
- `tests/test_local_shell_camera_settings_service.py`
- `tests/test_wx_preview_shell.py`

## Validation

- `tests.test_local_shell_camera_settings_service`
- `tests.test_wx_preview_shell`

## Done Criteria

- dialog opens with camera-class defaults
- limits are visible in the dialog hints
- width/height and ROI offsets respect camera increments
- unsupported values are corrected before apply
- pixel format matches the intended hardware default instead of a stale fallback
