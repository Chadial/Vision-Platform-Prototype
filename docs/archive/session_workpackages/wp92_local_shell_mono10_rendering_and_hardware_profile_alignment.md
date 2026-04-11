# WP92 Local Shell Mono10 Rendering And Hardware Profile Alignment

## Goal

Keep the wx shell usable on the tested hardware path when the camera profile resolves to `Mono10`, by making the local preview renderer accept high-bit grayscale frames and by aligning the stored default exposure to a valid hardware increment.

## Status

Completed after implementation and live hardware verification.

## Scope

- render `Mono10` preview frames in the local shell instead of crashing the UI timer loop
- keep the shell usable for `Mono12`, `Mono14`, and `Mono16` grayscale frames through the same conversion path
- correct the stored camera-class default exposure to a value accepted by the tested hardware increment grid
- make snapshot and bounded recording fall back to a hardware-safe output extension when BMP is invalid for the current pixel format

## Out Of Scope

- changing the camera SDK driver
- redesigning preview geometry or overlays
- broad file-format expansion beyond the current shell fallback rules

## Affected Areas

- `src/vision_platform/apps/local_shell/preview_shell_state.py`
- `src/vision_platform/apps/local_shell/wx_preview_shell.py`
- `src/vision_platform/apps/local_shell/control_cli.py`
- `src/vision_platform/apps/local_shell/output_format_policy.py`
- `configs/camera_configuration_profiles.json`
- `tests/test_camera_cli.py`
- `tests/test_local_shell_control_cli.py`
- `tests/test_local_shell_camera_settings_service.py`
- `tests/test_wx_preview_shell.py`

## Validation

- `tests.test_local_shell_camera_settings_service`
- `tests.test_camera_cli`
- `tests.test_local_shell_control_cli`
- `tests.test_wx_preview_shell`
- live hardware shell status, snapshot, and bounded recording on `DEV_1AB22C046D81`

## Done Criteria

- `Mono10` no longer crashes local-shell preview rendering
- the hardware-backed shell starts and stays visible on the tested camera path
- snapshot falls back to a hardware-safe format when BMP would be invalid
- bounded recording completes on the open hardware shell
- the hardware profile defaults are valid for the tested camera increment grid
