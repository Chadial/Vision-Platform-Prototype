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
- defer any lightweight operator info/control strip unless a later dedicated OpenCV slice shows that the remaining operator need cannot be met by the current status-band and shortcut model
- if such a strip is ever reopened later, keep it explicitly lightweight and treat it as a UI-only convenience layer rather than a baseline requirement for the prototype

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
