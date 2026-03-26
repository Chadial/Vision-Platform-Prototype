# Display Service

## Purpose

Composes UI-free display payloads from existing preview, snapshot, focus, and ROI state without binding the platform to a concrete window toolkit.

## Responsibility

- compose display-ready payloads from preview focus, snapshot focus, and active ROI
- keep display composition separate from UI rendering classes
- reuse existing overlay-ready focus payloads instead of duplicating focus logic

## Functions

- `OverlayCompositionService`

## Inputs / Outputs

- inputs: preview focus state, snapshot focus state or capture, active ROI or ROI state service
- outputs: shared display payload with active ROI plus preview and snapshot focus overlays

## Dependencies

- `libraries/common_models`
- `libraries/roi_core`
- `services/stream_service`
- `services/recording_service`
