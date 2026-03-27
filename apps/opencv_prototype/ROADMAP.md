# Roadmap

## Next

- move prototype-specific CLI parsing from legacy smoke modules into the app namespace
- define one canonical prototype launch command for preview, save, and simulated workflows
- decide whether the new overlay-payload demo should stay console-oriented or feed a later optional adapter for OpenCV drawing
- extend the current viewport-oriented preview behavior from fit-to-window and zoom toward cursor-aware zoom and pan
- keep overlay drawing stable under display scaling and viewport transforms
- keep overflow clipping centered until explicit pan is implemented on top of the current viewport model
- continue hardening preview teardown so longer hardware sessions do not leave avoidable disconnect-style cleanup errors
- build on the now-implemented point-selection baseline of click-selected crosshair, coordinate readout, and `c`-based coordinate copy
- add mouse-wheel zoom for the preview viewport
- zoom around the cursor position when the cursor is inside the image viewport, and fall back to centered zoom when the cursor is outside the image area or no reliable cursor-to-image mapping is available
- keep fit-to-window available as an explicit reset action that can also use the current cursor position when meaningful viewport-local feedback is available
- for rectangle ROI editing, support corner-handle interaction with click, hold, and drag
- for ellipse ROI editing, define the shape through the center point plus the upper-right corner of its rectangular bounding box, with that bounding box kept implicit or minimally hinted
- add snapshot saving through the `+` key
  - keep this tied to an existing snapshot service path instead of introducing UI-owned save logic
- add a top menu or control band for operator-facing preview settings
- allow sensor-array configuration through that menu, including width, height, and X/Y offsets
- allow shutter time configuration in floating-point milliseconds through that menu
- allow save-directory selection with either append-to-existing-run or create-new-subfolder behavior
- allow frame-limit configuration for capture and recording workflows, with `0` or empty meaning unlimited
- allow selection of the focus-calculation method through the same operator-facing control area
- structure that operator-facing top control band into:
  - sensor geometry: width, height, offset X, offset Y
  - acquisition: shutter time in float milliseconds, frame limit, snapshot action
  - storage: base directory plus append-vs-new-subfolder behavior
  - analysis: focus-method selection and focus overlay toggle
  - tools: crosshair toggle plus ROI mode selection for rectangle and ellipse

## Later

- add snapshot-analysis mode
- extend ROI overlay interaction from the current payload baseline into editable rectangle and ellipse tools
- support richer operator/developer demo modes
- separate operator-facing and developer-facing preview modes

## Deferred

- full desktop UI rewrite
- browser client work
