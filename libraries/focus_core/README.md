# Focus Core

## Purpose

Prepares the reusable focus-analysis boundary so live, snapshot, and postprocess workflows can share one contract.

## Responsibility

- focus request/result contracts
- evaluation entry points separate from UI and camera drivers
- future support for global and ROI-local focus scoring

## Functions

- portable focus request/result models
- Laplace-based focus evaluation for manual focus guidance
- evaluator boundary that stays separate from UI and camera drivers
- read-only overlay-data builder for preview and display consumers

## Inputs / Outputs

- inputs: `FrameData` or `CapturedFrame`, optional focus request
- outputs: one numeric focus score plus validity/result metadata

## Dependencies

- `libraries/common_models`
