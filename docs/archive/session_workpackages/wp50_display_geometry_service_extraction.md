# WP50 Display Geometry Service Extraction

## Purpose

This work package defines the first architecture-first slice for decoupling preview display behavior from the current OpenCV window implementation.

Closure lane:

- Post-Closure Python Baseline / selective expansion through architecture readiness

Slice role:

- structure-first extraction

Scope level:

- viewport geometry, coordinate transforms, zoom, and pan state only

This package exists to make preview geometry reusable before any new local UI shell or richer host/UI interaction layer is introduced.

## Branch

- intended branch: `refactor/display-geometry-service-extraction`
- activation state: current next

## Scope

Included:

- extract reusable viewport geometry logic from `src/vision_platform/imaging/opencv_preview.py`
- define one headless geometry model under `src/vision_platform/services/display_service`
- define one small zoom/pan state carrier reusable outside OpenCV
- move source-to-viewport and viewport-to-source mapping into the new service
- keep current OpenCV behavior by routing the existing preview window through the extracted service
- add focused tests for geometry and mapping behavior

Excluded:

- replacing the OpenCV preview shell
- introducing a new UI framework
- changing overlay rendering policy
- changing ROI interaction policy
- introducing host commands or transport changes
- audit/help/polish work

What this package does not close:

- the full UI migration
- the shared interaction command layer
- the overlay/status model cleanup
- the first non-OpenCV local UI shell

## Session Goal

Leave the repository with one testable geometry core so viewport math no longer lives implicitly inside `OpenCvPreviewWindow`.

## Current Context

The current preview implementation already proves the operator behaviors that matter:

- fit-to-window
- cursor-anchored zoom
- pan in zoom mode
- viewport cropping and padding
- source/viewport coordinate mapping for selection and ROI drawing

The architectural problem is ownership. Those rules currently sit inside one OpenCV class, which makes later UI migration and shared interaction work unnecessarily expensive.

## Target Extraction Seams

Current logic that should move out of `OpenCvPreviewWindow`:

- `_ViewportMapping`
- `_resolve_display_scale(...)`
- `_resolve_viewport_origin(...)`
- `_build_viewport_mapping(...)`
- `_map_viewport_point_to_source(...)`
- `_map_source_point_to_viewport(...)`
- `_build_cursor_anchored_origin(...)`
- zoom/pan state normalization currently spread across `_manual_zoom_scale`, `_viewport_origin_scaled`, and related helpers

Logic that should remain in `OpenCvPreviewWindow`:

- window lifecycle
- keyboard handling
- mouse event dispatch
- status-band text composition
- snapshot shortcut handling
- ROI mode toggles and draft-ROI interaction flow
- drawing calls into `OpenCvFrameAdapter`

## Proposed Output Shape

Preferred new implementation shape:

- `src/vision_platform/services/display_service/display_geometry_service.py`
- one immutable viewport-mapping dataclass
- one mutable but UI-neutral zoom/pan state dataclass
- one `DisplayGeometryService` with methods for:
  - fit-scale resolution
  - viewport origin clamping
  - mapping construction
  - viewport-to-source mapping
  - source-to-viewport mapping
  - cursor-anchored zoom-origin derivation

Keep the API portable and free of `cv2` or `numpy`.

## Execution Plan

1. Extract `_ViewportMapping` into a display-service-owned model.
2. Extract fit-scale, origin-clamp, and mapping creation into `DisplayGeometryService`.
3. Introduce a small UI-neutral zoom/pan state carrier consumed by `OpenCvPreviewWindow`.
4. Route `OpenCvPreviewWindow.render_latest_frame_and_get_key(...)` through the new geometry service.
5. Route mouse hit-testing and ROI drawing coordinate transforms through the same service.
6. Add dedicated geometry tests separate from the OpenCV window tests.
7. Keep existing OpenCV preview tests green with minimal behavior drift.

## Validation

Required automated validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_opencv_preview tests.test_opencv_smoke_demos
```

Recommended focused validation:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_opencv_adapter tests.test_bootstrap
```

Recommended new test target after extraction:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_display_geometry_service
```

## Documentation Updates

- `docs/WORKPACKAGES.md`
- `docs/STATUS.md`
- `services/display_service/STATUS.md`
- `apps/opencv_prototype/STATUS.md` if ownership wording changes materially

## Expected Commit Shape

1. `refactor: extract display geometry service`
2. `refactor: route opencv preview through display geometry`
3. `test: cover display geometry mapping`
4. `docs: record display geometry slice`

## Merge Gate

- viewport math is reusable without `OpenCvPreviewWindow`
- current preview behavior remains covered by tests
- no UI toolkit is added
- no audit/help/polish work is bundled into the branch
- geometry ownership is documented clearly enough to unblock `WP51`

## Recovery Note

If this package is resumed later:

1. inspect `src/vision_platform/imaging/opencv_preview.py`
2. inspect `tests/test_opencv_preview.py`
3. confirm the branch is still scoped to geometry extraction only
4. implement the headless service before touching any new UI shell work
