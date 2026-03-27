# Roadmap

## Next

- move prototype-specific CLI parsing from legacy smoke modules into the app namespace
- add overlay-ready preview composition without embedding analysis logic in the window code
- define one canonical prototype launch command for preview, save, and simulated workflows
- validate the new focus-preview smoke path against simulated preview frames
- carry optional focus-state composition through the preview demo without moving analysis into the window code
- decide whether the new overlay-payload demo should stay console-oriented or feed a later optional adapter for OpenCV drawing
- add viewport-oriented preview behavior for large hardware frames, starting with fit-to-window
- add interactive zoom and pan in the prototype preview path
- keep overlay drawing stable under display scaling and viewport transforms

## Later

- add snapshot-analysis mode
- add ROI overlay integration once ROI core advances
- support richer operator/developer demo modes
- separate operator-facing and developer-facing preview modes

## Deferred

- full desktop UI rewrite
- browser client work
