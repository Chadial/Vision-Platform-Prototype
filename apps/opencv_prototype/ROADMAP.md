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
- replace the current resize-based zoom attempt with a viewport renderer that preserves aspect ratio and treats zoom as display-space scaling plus cropping
- pad unused display regions with black instead of stretching or distorting the image
- keep overflow clipping centered first, then add explicit pan on top of that viewport model
- add a visible on-screen display mode or zoom-state indicator so shortcut effects are immediately confirmable during operator testing
- harden preview teardown so closing the window does not leave the shared acquisition path logging avoidable disconnect-style cleanup errors

## Later

- add snapshot-analysis mode
- add ROI overlay integration once ROI core advances
- support richer operator/developer demo modes
- separate operator-facing and developer-facing preview modes

## Deferred

- full desktop UI rewrite
- browser client work
