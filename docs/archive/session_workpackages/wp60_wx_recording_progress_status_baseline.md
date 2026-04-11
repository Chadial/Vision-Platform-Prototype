# WP60 wx Recording Progress Status Baseline

## Purpose

This work package defines the later bounded recording-progress follow-up for the wx shell.

Closure lane:

- Post-Closure Python Baseline / selective expansion

Slice role:

- status-surface baseline

Scope level:

- one bounded recording progress slice

Its purpose is to surface recording progress through the existing controller/status models so operators can see how many frames have been written without making the wx shell a new workflow owner.

The same slice also keeps the header honest about live cadence by showing the current camera acquisition FPS and the measured wx UI refresh FPS.

## Branch

- intended branch: `feature/wx-recording-progress-status`
- activation state: landed

## Scope

Included:

- show bounded recording progress through existing status models
- add start/stop recording controls with `Max Frames` and `Recording FPS` inputs
- render progress as `n/m` for bounded runs and `n/n` for unlimited runs
- keep the last recording summary visible after `Stop Recording` until the next `Start Recording`
- prefer status-line or light shell-surface presentation over new workflow logic

Excluded:

- interval capture controls
- detached recording redesign
- export/history UI

## Validation

Targeted controller/status tests plus bounded manual shell smoke during recording or interval capture.

## Result

- the wx shell now exposes start/stop recording controls, `Max Frames`, and `Recording FPS` on the same operator surface
- bounded progress stays visible in the shell status area, and the last recording summary remains visible after `Stop Recording` until the next `Start Recording`
- the shell header now shows the live camera acquisition FPS and the measured wx UI refresh FPS
- the current implementation stops short of append/resume semantics such as `n/n` progress for directory-level append runs; that remains a later storage/recording follow-up
