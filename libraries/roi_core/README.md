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
- frame-clamped pixel-bounds helper for grid-based consumers
- rectangle and ellipse mask derivation for analysis consumers
- placeholder structure for freehand support

## Freehand Note

- freehand ROI support is not part of the current MVP baseline
- any future artifact- or metadata-level ROI serialization must be frozen in this module's documentation before downstream consumers rely on it
- the intended canonical text-oriented baseline for later reuse is:
  - `global`
  - `rectangle(x1,y1,x2,y2)`
  - `ellipse(x_c,y_c,x_corner,y_corner)`
  - `freehand(x1,y1,x2,y2,...,xn,yn)`
- when used later, these formats should stay canonical:
  - no extra whitespace
  - `rectangle(...)` uses two stored corner points in order
  - `ellipse(...)` uses center point followed by one corner/edge-defining point in order
  - `freehand(...)` point order must match the stored ROI point order
  - integer-valued coordinates should serialize without trailing `.0`
  - non-integer coordinates should use one compact stable decimal form

## Inputs / Outputs

- inputs: `RoiDefinition`
- outputs: derived ROI geometry helpers and cropped pixel-grid masks

## Control Rule

- ROI describes which image region a consumer wants to use
- without ROI, consumers operate on the full frame
- with ROI, consumers operate on the relevant image intersection or derived bounds
- ROI core provides geometry helpers such as bounds and centroid, while consumers decide when and why ROI is applied

## Dependencies

- `libraries/common_models`

## Implementation Location

- current implementation lives under `src/vision_platform/libraries/roi_core`
