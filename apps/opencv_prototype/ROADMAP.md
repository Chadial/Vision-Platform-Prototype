# Roadmap

## Next

- move prototype-specific CLI parsing from legacy smoke modules into the app namespace
- define one canonical prototype launch command for preview, save, and simulated workflows
- decide whether the new overlay-payload demo should stay console-oriented or feed a later optional adapter for OpenCV drawing
- keep overlay drawing stable under display scaling and viewport transforms
- build on the current top-left-anchored viewport behavior toward explicit pan when zoomed content exceeds the visible preview area
- continue hardening preview teardown so longer hardware sessions do not leave avoidable disconnect-style cleanup errors
- build on the now-implemented point-selection baseline of click-selected crosshair, coordinate readout, and `c`-based coordinate copy
- harden cursor-anchored zoom behavior further for cases where the cursor is outside the visible image area or no reliable cursor-to-image mapping is available
- reduce low-zoom cursor-anchor drift caused by integer viewport rounding so repeated wheel zoom steps hold the same image point more precisely
- decide whether wheel events outside the visible image bounds should stay ignored with status feedback or later fall back to a viewport-center zoom policy
- keep fit-to-window available as an explicit reset action on top of the current top-left-anchored viewport model
- refine pan ergonomics on top of the new middle-drag baseline, including any desired status feedback and behavior at viewport edges
- keep the `+` snapshot shortcut on the current preview-frame save path and extend it only where clearer operator feedback or host-driven path control is still needed
- decide whether any remaining operator-facing error feedback should also be mirrored into structured logs or host-visible status objects beyond the current terminal/status-band coverage
- decide whether hardware preview flows should eventually expose a real focus-state provider so `y` can become meaningful there instead of remaining explicitly unavailable
- decide whether the OpenCV prototype should get only a lightweight operator info/control strip inside the preview composition rather than any "real" menu UI
- if that strip is added, allow sensor-array configuration through that lightweight operator area, including width, height, and X/Y offsets
- if that strip is added, allow shutter time configuration in floating-point milliseconds through that lightweight operator area
- allow save-directory selection with either append-to-existing-run or create-new-subfolder behavior
- allow frame-limit configuration for capture and recording workflows, with `0` or empty meaning unlimited
- allow selection of the focus-calculation method through the same lightweight operator area if it is still justified in OpenCV
- structure that lightweight operator area, if added at all, into:
  - sensor geometry: width, height, offset X, offset Y
  - acquisition: shutter time in float milliseconds, frame limit, snapshot action
  - storage: base directory plus append-vs-new-subfolder behavior
  - analysis: focus-method selection and focus overlay toggle
  - tools: crosshair toggle plus ROI mode selection for rectangle and ellipse

## Later

- add snapshot-analysis mode
- extend ROI overlay interaction from the current creation baseline into editable rectangle and ellipse tools; treat this as non-MVP operator comfort work rather than a baseline preview requirement
- for rectangle ROI editing, support corner-handle interaction with click, hold, and drag
- for ellipse ROI editing, define the shape through the center point plus the upper-right corner of its rectangular bounding box, with that bounding box kept implicit or minimally hinted
- extend ROI overlay interaction from the current payload baseline into editable rectangle and ellipse tools
- support richer operator/developer demo modes
- separate operator-facing and developer-facing preview modes

## Deferred

- full desktop UI rewrite
- browser client work
