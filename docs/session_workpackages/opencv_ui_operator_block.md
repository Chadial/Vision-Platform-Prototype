# OpenCV UI Operator Block

## Purpose

This work package captures the next operator-facing OpenCV UI block after the hardware-validation branch closes.

It exists so the next branch can continue UI work without losing track of the UI baseline that is already implemented on the closing branch.

## Branch

- intended next branch: `feature/opencv-ui-operator-block`

## Scope

Included:

- continue the OpenCV prototype as the current operator-facing UI surface
- build on the already implemented preview UI baseline:
  - fit-to-window preview
  - zoom in/out and fit reset
  - warning-only capability-probe hinting
  - click-based point selection
  - crosshair drawing for the selected point
  - coordinate readout in the preview overlay
  - coordinate copy with `c`
- move toward richer operator-facing preview interaction:
  - dedicated bottom status band
  - crosshair toggle
  - FPS/status readout
  - focus visibility toggle
  - ROI drawing entry points for rectangle and ellipse
  - snapshot shortcut
  - later control/menu band preparation

Excluded:

- new hardware validation work unless required only for a narrow UI check
- camera-core or recording-core redesign
- browser or full desktop UI replacement
- freehand ROI

## Session Goal

Create the next UI-focused branch and continue from the existing preview baseline without redoing already completed UI work.

The first completed slice on that branch should make the preview feel more operator-facing by separating image content from status text and by formalizing the newly added point-selection workflow.

## Execution Plan

1. Create the new branch from the merge-ready closeout of `feature/hardware-validation-phase-9`.
2. Preserve the already completed preview interaction as the starting baseline rather than treating it as still-open roadmap work.
3. Move coordinate, warning, and preview-state text out of the image overlay and into a dedicated bottom status band in the OpenCV prototype.
4. Add stable operator toggles:
   - `x` for crosshair visibility
   - `y` for focus visibility
   - keep `c` for coordinate copy
5. Add status-band content for:
   - selected point coordinates
   - preview mode / zoom
   - warning-only capability-probe error if present
   - FPS readout
6. Add the first ROI interaction entry points for rectangle and ellipse without collapsing ROI ownership into the preview window.
7. Add snapshot shortcut handling for local operator use.
8. Update module and repository docs after each coherent UI slice.

## Validation

- `.\.venv\Scripts\python.exe -m unittest tests.test_opencv_preview tests.test_opencv_smoke_demos tests.test_bootstrap`
- extend targeted preview tests for any new key, mouse, or status-band behavior
- if hardware is connected again later, run a short manual preview check on the OpenCV hardware demo

## Documentation Updates

Before the work package is considered complete, update:

- `apps/opencv_prototype/STATUS.md`
- `apps/opencv_prototype/ROADMAP.md`
- `docs/STATUS.md`
- `docs/SESSION_START.md` if the active recovery link changes

## Expected Commit Shape

1. `feat: add preview status band baseline`
2. `feat: add preview interaction toggles`
3. `feat: add roi entry points to opencv preview`
4. `docs: update opencv ui status after operator block`

## Merge Gate

- already completed preview UI baseline remains intact
- new UI work stays in the OpenCV/display-facing layer
- touched OpenCV tests pass locally
- docs clearly distinguish completed UI baseline from still-open operator work

## Recovery Note

To resume this work:

1. Read `Agents.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/MODULE_INDEX.md`
4. Read `apps/opencv_prototype/README.md`
5. Read `apps/opencv_prototype/STATUS.md`
6. Read `apps/opencv_prototype/ROADMAP.md`
7. Read `docs/STATUS.md`
