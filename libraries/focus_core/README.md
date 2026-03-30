# Focus Core

## Purpose

Prepares the reusable focus-analysis boundary so live, snapshot, and postprocess workflows can share one contract.

## Responsibility

- focus request/result contracts
- evaluation entry points separate from UI and camera drivers
- future support for global and ROI-local focus scoring
- keep focus evaluation consumer-driven instead of embedding it into preview, stream, or window classes

## Functions

- portable focus request/result models
- Laplace-based focus evaluation for manual focus guidance
- evaluator boundary that stays separate from UI and camera drivers
- read-only overlay-data builder for preview and display consumers

## Artifact Metadata Note

- `focus_core` defines focus-evaluation meaning, not traceability/log ownership
- if later artifact-level metadata reuses focus results, this module should remain the source of truth for the semantic shape of those values
- the narrow reusable artifact-facing baseline should stay aligned with fields such as:
  - `focus_method`
  - `focus_score_frame_interval`
  - `focus_value_mean`
  - `focus_value_stddev`
  - `focus_roi_type`
  - `focus_roi_data`
- `focus_value_mean` and `focus_value_stddev` should not be treated as free-floating values; if used for artifact metadata, they should describe a moving window over frame-level focus scores
- the intended narrow baseline for that window is:
  - field: `focus_score_frame_interval`
  - default: `7`
  - minimum: `3`
  - maximum: `17`
- focus-related artifact metadata should remain analysis metadata for saved artifacts, not stable acquisition-header identity by default
- ROI text forms used with focus metadata should stay aligned with the canonical ROI serialization documented in `libraries/roi_core`

## Inputs / Outputs

- inputs: `FrameData` or `CapturedFrame`, optional focus request
- outputs: one numeric focus score plus validity/result metadata

## Control Rule

- `focus_core` does not fetch frames on its own
- a caller such as `FocusPreviewService` decides when the latest frame should be evaluated
- preview and window layers may consume focus state, but they should not own focus-analysis logic

## Dependencies

- `libraries/common_models`

## Implementation Location

- current implementation lives under `src/vision_platform/libraries/focus_core`
