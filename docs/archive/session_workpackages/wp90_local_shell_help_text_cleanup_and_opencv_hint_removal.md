# WP90 Local Shell Help Text Cleanup And OpenCV Hint Removal

## Goal

Replace the old OpenCV-flavored shortcut help with a shorter wx-shell-oriented reference that reflects the current menu and accelerator map and removes the obsolete OpenCV hint entirely.

## Status

Completed after implementation.

## Scope

- shorten the keyboard-shortcut help text
- remove the obsolete OpenCV-specific framing
- keep the current accelerator map readable and accurate
- make the help content visually cleaner and easier to scan

## Out Of Scope

- changing the actual shortcut bindings
- redesigning the menu structure
- adding a new help dialog system

## Affected Areas

- `src/vision_platform/apps/local_shell/wx_preview_shell.py`
- `tests/test_wx_preview_shell.py`

## Validation

- `tests.test_wx_preview_shell`

## Done Criteria

- help text no longer references OpenCV styling
- help text reflects the current local shell bindings only
- accelerator text remains consistent with the visible shell
- the help dialog is compact enough to be usable instead of noisy
