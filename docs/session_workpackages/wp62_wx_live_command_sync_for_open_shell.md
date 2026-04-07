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
- activation state: queued

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

- polling vs event/IPC observer
- in-process shared state vs session bridge
- how much menu state is dynamically enabled or disabled

## Validation

- two-process smoke or equivalent local observation test
- issue a CLI/API command while the wx shell is open and confirm the UI updates without restart

