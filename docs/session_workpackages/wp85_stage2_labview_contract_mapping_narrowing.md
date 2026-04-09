# WP85 Stage-2 LabVIEW Contract Mapping Narrowing

## Purpose

Map the current bounded Stage-1 host surface into one LabVIEW-near reading so the next real host-integration step is explicit without widening transport scope.

## Status

Landed. `WP85` is now completed as one narrow Stage-2 mapping sequence behind the landed workflow, host-surface, and failure-reading baselines.

## Sub-Packages

### Landed

#### `WP85.A LabVIEW Mapping Shape Baseline`

- status: landed
- purpose: define one additive LabVIEW-near reading for the current status and command-result surfaces without changing the underlying command/runtime model
- scope:
  - current command name
  - current workflow phase/result cues
  - current save-path / file / stop-category cues where already present
  - no transport or IPC redesign

#### `WP85.B Test-Host Output Wiring`

- status: landed
- purpose: expose that LabVIEW-near reading through the current `local_shell control` path so Stage 1 remains the proving seam for Stage 2
- scope:
  - `status`
  - current command results
  - additive mapping only

#### `WP85.C Failed Command Mapping Preservation`

- status: landed
- purpose: keep one LabVIEW-near reading available even when the current command fails
- scope:
  - bounded command failure only
  - no broad recovery or retry lane

#### `WP85.D Stage-2 Reading Smoke`

- status: landed
- purpose: prove the additive Stage-2 mapping on the current bounded host path
- scope:
  - one status reading
  - one successful command reading
  - one failed command reading

### Boundary Note

This package should be read as:

- a mapping clarification and additive adapter slice
- not a new transport layer
- not a LabVIEW runtime integration implementation
- not a reason to widen the current host surface beyond the bounded phase-1 command set

### Outcome

- the current `local_shell control` test-host surface now exposes one additive `labview_mapping` block for published shell status reads
- successful command results now also expose one additive `labview_mapping` block with the current command name, workflow phase cues, save-path/file cues, stop category, and current failure ownership where relevant
- failed command reads now preserve the same additive `labview_mapping` block instead of collapsing to a plain error string only
- the mapping stays intentionally narrow and adapter-oriented:
  - no transport redesign
  - no new runtime layer
  - no widening of the bounded phase-1 command surface

### Implemented order inside `WP85`

1. `WP85.A LabVIEW Mapping Shape Baseline`
2. `WP85.B Test-Host Output Wiring`
3. `WP85.C Failed Command Mapping Preservation`
4. `WP85.D Stage-2 Reading Smoke`
