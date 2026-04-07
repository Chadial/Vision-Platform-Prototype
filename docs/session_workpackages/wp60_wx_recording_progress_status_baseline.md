# WP60 wx Recording Progress Status Baseline

## Purpose

This work package defines the later bounded recording-progress follow-up for the wx shell.

Closure lane:

- Post-Closure Python Baseline / selective expansion

Slice role:

- status-surface baseline

Scope level:

- one bounded recording/interval progress status slice

Its purpose is to surface recording or interval progress through the existing controller/status models so operators can see how many frames have been written without making the wx shell a new workflow owner.

## Branch

- intended branch: `feature/wx-recording-progress-status`
- activation state: queued

## Scope

Included:

- show bounded recording and interval-capture progress through existing status models
- prefer status-line or light shell-surface presentation over new workflow logic

Excluded:

- full recording control panel
- detached recording redesign
- export/history UI

## Validation

Targeted controller/status tests plus bounded manual shell smoke during recording or interval capture.
