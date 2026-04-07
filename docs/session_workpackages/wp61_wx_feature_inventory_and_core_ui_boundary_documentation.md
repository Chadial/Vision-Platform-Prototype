# WP61 wx Feature Inventory And Core/UI Boundary Documentation

## Purpose

Document the implemented wx shell surface and make the boundary between the shared headless core and UI-local behavior explicit.

## Closure lane

- Post-Closure Python Baseline / operational readiness

## Slice role

- documentation and boundary clarification

## Scope level

- documentation only

## Branch

- intended branch: `docs/wx-shell-feature-inventory`
- activation state: current next

## Scope

Included:

- enumerate the implemented wx shell functions and controls
- separate shared-core responsibilities from UI-local responsibilities
- record which UI behaviors intentionally reuse the shared headless services
- update the module docs and central status / queue docs to reflect the current shell reality

Excluded:

- new wx behavior
- command sync or IPC
- menu redesign
- renderer refactors

## Validation

- cross-check the inventory against the current code and shell help/status text
- confirm the documented boundary matches the implemented shell responsibilities

