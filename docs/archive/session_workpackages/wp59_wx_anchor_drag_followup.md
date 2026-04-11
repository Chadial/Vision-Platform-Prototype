# WP59 wx Anchor Drag Follow-Up

## Purpose

This work package defines the later bounded interaction follow-up for visible ROI and point anchors in the wx shell.

Closure lane:

- Post-Closure Python Baseline / selective expansion

Slice role:

- interaction follow-up

Scope level:

- one bounded anchor hover/drag slice for the wx shell only

Its purpose is to add anchor affordances only after focus visibility and clipboard semantics are stable, so draggable anchors do not land on top of already ambiguous point and focus behavior.

## Branch

- intended branch: `feature/wx-anchor-drag-followup`
- activation state: queued

## Scope

Included:

- visible anchor affordances for active ROI geometry and fixed point selection
- bounded hover/highlight state
- first drag behavior for supported anchors

Excluded:

- full vector-editing toolset
- arbitrary ROI reshaping
- recording controls
- generalized desktop tool framework

## Validation

Targeted local validation plus manual wx-shell smoke over ROI and point dragging.
