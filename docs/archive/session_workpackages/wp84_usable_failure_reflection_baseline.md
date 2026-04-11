# WP84 Usable Failure Reflection Baseline

## Purpose

Make current host-plus-shell failures readable enough across setup, snapshot, and recording without introducing a broad new error platform.

## Status

Landed. `WP84` is now completed as one sequence of small failure-reading sub-packages under the same Hybrid Companion lane.

## Sub-Packages

### Landed

#### `WP84.A Shared Failure Reflection Baseline`

- status: landed
- purpose: expose one common failure-reading shape in published status and command-result paths for current setup, snapshot, and recording failures
- scope:
  - current failure source
  - current failed action
  - readable message
  - no retry or recovery orchestration

#### `WP84.B Setup Failure Reflection Tightening`

- status: landed
- purpose: make current setup/configuration failures visible enough in the same shared failure-reading model
- scope:
  - external `apply_configuration`
  - external `set_save_directory`
  - bounded local setup failures where already surfaced by the shell

#### `WP84.C Failure Smoke For Host-Visible Reading`

- status: landed
- purpose: prove one repeatable host path where a failure is readable through both command result and published shell status
- scope:
  - one current failure case only
  - no broad fault-injection harness

#### `WP84.D Failure Reset/Overwrite Narrowing`

- status: landed
- purpose: keep failure state understandable when a later success or newer failure occurs, without building a full incident history
- scope:
  - latest failure ownership only
  - no event log browser

### Outcome

- shell status, published live status, and failed live-command result files now share one explicit `failure_reflection` baseline
- the current failure-reading shape is intentionally small:
  - `phase`
  - `source`
  - `action`
  - `message`
  - `external`
- current setup failures are now covered for both local shell actions and external live commands
- the visible shell status prefix now exposes the current failure owner as `failure=...`
- later success in the same workflow lane clears the current failure owner, and a newer failure overwrites the older one without adding incident-history scope

### Ordering Note

Implemented order inside `WP84`:

1. `WP84.A Shared Failure Reflection Baseline`
2. `WP84.B Setup Failure Reflection Tightening`
3. `WP84.C Failure Smoke For Host-Visible Reading`
4. `WP84.D Failure Reset/Overwrite Narrowing`
