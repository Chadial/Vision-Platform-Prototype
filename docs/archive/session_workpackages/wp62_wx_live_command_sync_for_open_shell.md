# WP62 wx Live Command Sync For Open Shell

## Purpose

Let an already open wx shell observe CLI/API-driven configuration and recording changes without moving command ownership into the UI.

## Closure lane

- Post-Closure Python Baseline / selective expansion

## Slice role

- bounded live sync baseline

## Scope level

- one bounded live command observation/sync path

## Branch

- intended branch: `feature/wx-live-command-sync`
- activation state: implemented

## Scope

Included:

- reflect external start/stop/configuration changes in an open wx shell
- keep the UI responsive by observing shared state instead of duplicating command logic
- adjust status, controls, and menu affordances based on current core state

Excluded:

- new transport framework
- cross-machine service hosting
- broad menu redesign
- UI-private command execution that bypasses the core

## Open policy choices

- resolved for this slice:
  - local file-backed session bridge
  - polling from the already running shell timer
  - command execution continues through the in-process `CommandController`
- deferred:
  - broader event/IPC transport
  - richer menu-state sync once a real menu surface exists

## Validation

- two-process smoke or equivalent local observation test
- issue a CLI/API command while the wx shell is open and confirm the UI updates without restart

## Landed Result

- the wx shell now publishes one active local session under `captures/wx_shell_sessions/`
- external control commands can now be sent through `python -m vision_platform.apps.local_shell control ...`
- the open shell consumes those commands and updates its visible status/controls without restart

## Headless Follow-Up Note

- this slice intentionally lands the session bridge under the wx-shell app boundary as a bounded local-working solution
- it should not be treated as the final host-neutral command/runtime model
- when the later headless-kernel preparation starts, the session/command-observation concept should be revisited and lifted into a host-neutral service or protocol surface that can serve UI, host control, and automation flows equally

