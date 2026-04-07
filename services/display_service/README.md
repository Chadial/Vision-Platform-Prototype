# Display Service

## Purpose

Composes UI-free display payloads and owns headless preview-geometry logic without binding the platform to a concrete window toolkit.

## Responsibility

- compose display-ready payloads from preview focus, snapshot focus, and active ROI
- own reusable viewport geometry, zoom, pan, and coordinate mapping rules outside concrete preview windows
- keep display composition separate from UI rendering classes
- reuse existing overlay-ready focus payloads instead of duplicating focus logic

## Functions

- `DisplayGeometryService`
- `OverlayCompositionService`
- `PreviewInteractionService`

## Inputs / Outputs

- inputs: frame size, viewport size, zoom/pan state, preview interaction commands/state, preview focus state, snapshot focus state or capture, active ROI or ROI state service
- outputs: viewport mappings and coordinate transforms, interaction state transitions, plus shared display payload with active ROI and focus overlays

## Dependencies

- `libraries/common_models`
- `libraries/roi_core`
- `services/stream_service`
- `services/recording_service`

## Implementation Location

- current implementation lives under `src/vision_platform/services/display_service`
- current lightweight payload consumer lives under `src/vision_platform/apps/opencv_prototype/overlay_payload_demo.py`
