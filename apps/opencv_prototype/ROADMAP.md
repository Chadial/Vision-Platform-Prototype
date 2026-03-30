# Roadmap

## Next

- keep overlay drawing stable under display scaling and viewport transforms
- continue hardening preview teardown so longer hardware sessions do not leave avoidable disconnect-style cleanup errors
- harden cursor-anchored zoom behavior further for cases where the cursor is outside the visible image area or no reliable cursor-to-image mapping is available
- reduce low-zoom cursor-anchor drift caused by integer viewport rounding so repeated wheel zoom steps hold the same image point more precisely
- refine pan ergonomics on top of the new middle-drag baseline, including any desired status feedback and behavior at viewport edges
- keep the `+` snapshot shortcut on the current preview-frame save path and extend it only where clearer operator feedback is still needed
- decide whether hardware preview flows should eventually expose a real focus-state provider so `y` can become meaningful there instead of remaining explicitly unavailable
- keep any later operator strip explicitly lightweight and UI-only if it is ever reopened

## Later

- add snapshot-analysis mode
- extend ROI overlay interaction from the current creation baseline into editable rectangle and ellipse tools
- support richer operator/developer demo modes
- separate operator-facing and developer-facing preview modes

## Deferred

- full desktop UI rewrite
- browser client work
