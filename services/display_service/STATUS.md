# Status

- maturity: active baseline module
- implemented: UI-free composition of preview focus, snapshot focus, and active ROI into one shared display payload
- working now: display consumers can reuse one payload shape without owning ROI or focus composition logic
- working now: a lightweight console-oriented overlay-payload demo consumes the shared payload without introducing a concrete renderer dependency
- partial: no window renderer or drawing adapter consumes the payload directly yet
- known issues: payload currently carries focus overlays and active ROI only, not future tracking or annotation layers
- technical debt: preview and snapshot focus states still reuse the preview-oriented `FocusPreviewState` name
- risk: future overlay growth may require a small layer model instead of flat fields only
