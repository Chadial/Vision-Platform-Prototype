# ROI Core

## Purpose

Prepares reusable ROI concepts for live overlay, focus analysis, tracking, and postprocess workflows.

## Responsibility

- ROI geometry contracts
- future ROI-mask derivation
- future reuse across UI and analysis modules
- keep ROI as reusable geometry and selection data, not as a UI-owned or preview-owned concern

## Functions

- bounding-box helper for portable ROI definitions
- centroid helper for display-anchor coordinates
- placeholder structure for rectangle, ellipse, and freehand support

## Inputs / Outputs

- inputs: `RoiDefinition`
- outputs: derived ROI geometry helpers

## Control Rule

- ROI describes which image region a consumer wants to use
- without ROI, consumers operate on the full frame
- with ROI, consumers operate on the relevant image intersection or derived bounds
- ROI core provides geometry helpers such as bounds and centroid, while consumers decide when and why ROI is applied

## Dependencies

- `libraries/common_models`
