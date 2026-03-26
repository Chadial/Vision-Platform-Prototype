# Focus Core

## Purpose

Prepares the reusable focus-analysis boundary so live, snapshot, and postprocess workflows can share one contract.

## Responsibility

- focus request/result contracts
- evaluation entry points separate from UI and camera drivers
- future support for global and ROI-local focus scoring

## Functions

- portable focus request/result models
- placeholder evaluator-availability helper

## Inputs / Outputs

- inputs: frame data, focus request
- outputs: focus availability or later focus scores/results

## Dependencies

- `libraries/common_models`
