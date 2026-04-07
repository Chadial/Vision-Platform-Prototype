# WP69 wx Camera Settings Menu And Shortcut Baseline

## Purpose

Expose the existing host-neutral camera configuration surface from the bounded wx shell through a real camera-settings menu path, and define the local GUI shortcut map so the shell remains aligned with the current OpenCV reference interactions and the host seam can reuse the same properties later.

## Closure lane

- Usable Camera Subsystem / Pre-Product Baseline

## Slice role

- bounded local UI / host-seam alignment baseline

## Scope level

- one narrow wx-shell menu and shortcut slice over the existing configuration request surface

## Branch

- intended branch: `feature/wx-camera-menu-shortcuts`
- activation state: landed

## Result

- implemented and merged as the wx camera-settings menu and shortcut baseline
- the bounded wx shell now exposes the camera settings dialog, shortcut map, and camera configuration summary through the existing controller path

## Scope

Included:

- add a camera-settings menu entry in the wx shell
- expose the existing camera configuration fields through a bounded dialog
- apply those values through the existing `ApplyConfigurationRequest` / controller path
- add menu entries and shortcut definitions for the already supported local shell features
- keep the OpenCV preview shortcut set as the behavioral reference for the core preview actions
- surface the current camera configuration compactly in the wx shell status so host-seam properties stay visible

Excluded:

- new camera core logic
- new transport/API layer
- large frontend redesign
- capability discovery UX beyond the existing host/core request model

## Validation

- camera-settings dialog opens from the wx shell
- edited values are applied through the existing controller path
- status updates reflect the current camera configuration summary
- menu items and shortcut labels cover the currently supported shell actions
- local unit tests cover the dialog parsing and the status summary
