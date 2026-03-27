# Roadmap

## Next

- move prototype-specific CLI parsing from legacy smoke modules into the app namespace
- add overlay-ready preview composition without embedding analysis logic in the window code
- define one canonical prototype launch command for preview, save, and simulated workflows
- validate the new focus-preview smoke path against simulated preview frames
- carry optional focus-state composition through the preview demo without moving analysis into the window code
- decide whether the new overlay-payload demo should stay console-oriented or feed a later optional adapter for OpenCV drawing
- extend the current viewport-oriented preview behavior from fit-to-window and zoom toward cursor-aware zoom and pan
- keep overlay drawing stable under display scaling and viewport transforms
- keep overflow clipping centered until explicit pan is implemented on top of the current viewport model
- continue hardening preview teardown so longer hardware sessions do not leave avoidable disconnect-style cleanup errors
- add a toggleable crosshair overlay for live preview inspection
- add coordinate readout for the current crosshair or cursor position in a dedicated bottom status bar area instead of drawing those values directly into the image content
- keep that bottom status band separate from the image viewport so inspection overlays and status text do not consume image pixels
- add mouse-wheel zoom for the preview viewport
- zoom around the cursor position when the cursor is inside the image viewport, and fall back to centered zoom when the cursor is outside the image area or no reliable cursor-to-image mapping is available
- keep fit-to-window available as an explicit reset action that can also use the current cursor position when meaningful viewport-local feedback is available
- add FPS reporting in the bottom status bar
- toggle the crosshair with the `x` key
- toggle focus-state display with the `y` key
- add rectangular ROI-mask creation with the `r` key
- add elliptical ROI-mask creation with the `e` key
- for rectangle ROI editing, support corner-handle interaction with click, hold, and drag
- for ellipse ROI editing, define the shape through the center point plus the upper-right corner of its rectangular bounding box, with that bounding box kept implicit or minimally hinted
- add snapshot saving through the `+` key
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
- add ROI overlay integration once ROI core advances
- support richer operator/developer demo modes
- separate operator-facing and developer-facing preview modes

## Deferred

- full desktop UI rewrite
- browser client work
