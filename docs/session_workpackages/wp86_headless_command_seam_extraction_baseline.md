# WP86 Headless Command Seam Extraction Baseline

## Purpose

Extract one small shell-independent command/status seam from the current bounded wx-shell bridge as the first real headless-preparation slice.

## Status

Landed. `WP86` is now completed as one narrow headless-preparation sequence after the landed workflow, host-surface, failure-reading, and LabVIEW-near mapping baselines.

## Sub-Packages

### Landed

#### `WP86.A Companion Payload Contract Extraction`

- status: landed
- purpose: move the current command-result and status-snapshot payload assembly into one shell-independent seam
- scope:
  - successful command-result payload shape
  - failed command-result placeholder shape
  - published status-snapshot payload shape
  - no transport/runtime redesign

#### `WP86.B wx Bridge Reuse`

- status: landed
- purpose: make the existing wx-shell bridge consume that extracted seam instead of owning the payload assembly directly
- scope:
  - same current payload meaning
  - additive structural extraction only

#### `WP86.C Headless Seam Coverage`

- status: landed
- purpose: add focused tests for the extracted seam and keep existing wx-shell/live-sync tests green
- scope:
  - seam payload tests
  - no new integration harness

### Boundary Note

This package should be read as:

- a first shell-independent contract extraction
- not a detached headless runtime
- not a transport rewrite
- not a replacement of the current bounded wx-shell live-sync bridge

### Outcome

- the current companion command-result payload shape now has one shell-independent home in `vision_platform.services.companion_contract_service`
- the current published companion status-snapshot payload shape now also has one shell-independent home in that same service
- the wx-shell live-sync bridge now consumes those builders instead of owning the payload assembly directly
- the extraction stays intentionally narrow:
  - no new transport
  - no detached runtime
  - no replacement of the current bounded file-backed session bridge

### Implemented order inside `WP86`

1. `WP86.A Companion Payload Contract Extraction`
2. `WP86.B wx Bridge Reuse`
3. `WP86.C Headless Seam Coverage`
