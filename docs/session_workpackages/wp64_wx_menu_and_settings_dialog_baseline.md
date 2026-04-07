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
- activation state: current next

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
