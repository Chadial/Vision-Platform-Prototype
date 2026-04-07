# WP53 Local Working UI Shell Baseline

## Purpose

This work package records the first intended non-OpenCV local shell once geometry, interaction, and status ownership are separated.

Closure lane:

- Post-Closure Python Baseline / selective expansion

Slice role:

- local frontend baseline

Scope level:

- one pragmatic local operator shell only

Its purpose is to create a better daily-use frontend without dragging framework choices into the core architecture too early.

## Branch

- intended branch: `feature/local-working-ui-shell-baseline`
- activation state: queued

## Scope

Included:

- add one local working UI shell above the extracted geometry, interaction, and status layers
- keep the shell as an adapter over shared platform logic
- preserve the existing OpenCV prototype as a fallback/reference path while the new shell proves itself

Excluded:

- browser/web work
- broad host/API transport work
- hardware audit/help polish

## Activation Condition

Activate only after `WP50`, `WP51`, and `WP52` are in place, or when there is a concrete operator need that justifies the shell immediately.
