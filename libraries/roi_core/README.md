# ROI Core

## Purpose

Prepares reusable ROI concepts for live overlay, focus analysis, tracking, and postprocess workflows.

## Responsibility

- ROI geometry contracts
- future ROI-mask derivation
- future reuse across UI and analysis modules

## Functions

- bounding-box helper for portable ROI definitions
- centroid helper for display-anchor coordinates
- placeholder structure for rectangle, ellipse, and freehand support

## Inputs / Outputs

- inputs: `RoiDefinition`
- outputs: derived ROI geometry helpers

## Dependencies

- `libraries/common_models`
