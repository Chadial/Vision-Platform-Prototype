# Tracking Core

Reusable tracking- and edge-analysis primitives kept separate from UI, stream orchestration, and transport-facing result shaping.

## Responsibility

- profile- or column-based edge analysis kernels
- later drift-indication and feature-anchor groundwork
- contracts that can be reused by preview, postprocess, or later API consumers

## Current Baseline

- directional edge-profile analysis over `FrameData` or `CapturedFrame`
- optional ROI-bounded analysis through existing ROI contracts
- transport-neutral request/result dataclasses for one dominant edge pass

## Not This Module

- UI overlays or operator interaction
- multi-frame tracking workflow ownership
- crack-tip heuristics as a first baseline
