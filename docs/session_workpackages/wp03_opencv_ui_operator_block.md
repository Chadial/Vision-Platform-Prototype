# OpenCV UI Operator Block

## Purpose

This work package captures the next operator-facing OpenCV UI block after the hardware-validation branch closes.

It exists so the next branch can continue UI work without losing track of the UI baseline that is already implemented on the closing branch.

## Branch

- active branch: `feature/opencv-ui-operator-block`
- branch fit: this branch matches the intended scope of the current operator-facing OpenCV UI block and should continue to carry only UI/display-facing work for that package

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
  - at most a lightweight in-preview operator strip later if it still proves necessary

Excluded:

- new hardware validation work unless required only for a narrow UI check
- camera-core or recording-core redesign
- browser or full desktop UI replacement
- freehand ROI
- richer ROI editing such as drag handles, post-creation resize, or ROI move workflows; keep those for a non-MVP follow-up branch

## Session Goal

Continue the existing UI-focused branch from the already implemented preview baseline without redoing completed hardware-preview and point-selection work.

The first completed slice on this branch should make the preview feel more operator-facing by separating image content from status text and by formalizing the newly added point-selection workflow.

## Status

- current state: active lane; major MVP preview/operator slices are already implemented, with remaining work limited to bounded UI-facing follow-up

## Sub-Packages

1. preserve completed viewport and operator baseline
2. finish any remaining bounded viewport hardening
3. decide whether a lightweight in-preview operator strip still belongs on this branch
4. keep richer ROI editing explicitly out of MVP

## Open Questions

- does any remaining operator-strip work still belong on this branch or in a later package?
- which remaining zoom or pan edge cases are worth fixing before calling the branch stable enough?
- should any operator-facing warning paths also surface through richer host-visible status later?

## Learned Constraints

- UI work must remain in the OpenCV/display lane
- snapshot shortcuts require acquisition-safe wiring, not ad-hoc direct saves
- richer ROI editing remains intentionally outside MVP scope

## Current Baseline To Preserve

Treat the following as already implemented baseline, not as still-open work for this package:

- viewport-based fit-to-window preview
- zoom in/out and fit reset through the current OpenCV preview controls
- dedicated bottom status band that keeps preview status text out of the image viewport
- rolling FPS readout in that status band
- warning-only capability-probe hinting
- click-based single-point selection
- image-space coordinate readout for the selected point in the status band
- crosshair rendering for the selected point
- `x`-based crosshair visibility toggle
- focus-status display in the status band for focus-aware preview flows
- `y`-based focus-status visibility toggle
- `r`/`e`-based ROI entry modes for rectangle and ellipse
- first two-click ROI creation baseline for rectangle and ellipse
- cursor-anchored zoom in the viewport preview path
- top-left image anchoring with padding only to the right and bottom
- thin outline around the visible image area when padding is present
- coordinate copy through `c`
- preview-frame snapshot save through `+` when an explicit snapshot save directory is configured in the app/demo path
- mouse-wheel zoom through the same cursor-anchored viewport path as the keyboard zoom controls
- middle-drag pan for zoomed content in the viewport path
- concise operator-facing warning/error messages for common unavailable actions and for demo-start failures

This baseline is documented in:

- `apps/opencv_prototype/STATUS.md`
- `apps/opencv_prototype/ROADMAP.md`
- `docs/STATUS.md`

Any resumed session should first confirm that code changes still preserve those behaviors before extending the operator UI further.

## Status And Roadmap Alignment

This work package is not the source of truth for implementation status. Before and after each coherent slice, re-check:

- `apps/opencv_prototype/STATUS.md` for the implemented OpenCV prototype baseline and open gaps
- `apps/opencv_prototype/ROADMAP.md` for the intended next OpenCV preview/UI steps
- `docs/STATUS.md` for repository-level progress against both `docs/ROADMAP.md` and `docs/GlobalRoadmap.md`

Use those documents to keep the plan honest:

- if a capability is already listed as implemented in status, preserve it and avoid reopening it as roadmap work
- if a capability is listed as planned in roadmap but not yet implemented, it can stay in scope for this branch if it remains UI/display-facing
- when status and roadmap drift, update the permanent docs rather than expanding this work package into a second source of truth

## Collected Implementation Notes

- The snapshot shortcut is not just another preview keybinding. A clean implementation needs explicit service wiring from the OpenCV app/demo path into an existing snapshot-save path so the UI does not start owning file naming, save-directory policy, or ad-hoc storage behavior.
- A direct `SnapshotService` call from the running preview path would currently compete with the same camera driver that is already serving the shared live stream, so the eventual snapshot shortcut needs a deliberately chosen acquisition-safe path rather than a naive direct save call.
- Because of that wiring requirement, snapshot shortcut work should be treated as a small integration slice inside this branch rather than as an isolated one-line key handler patch.
- ROI entry points can land earlier than full ROI editing as long as the UI layer only owns mode selection and event capture while ROI state and geometry remain aligned with existing model/service boundaries.
- Full ROI editing is intentionally out of MVP scope for this branch. The current branch stops at ROI mode selection, live preview, and first creation so the operator baseline stays small and mergeable.
- In this OpenCV/HighGUI path, words like `menu` or `menu band` must not be read as a promise of real GUI widgets. At most, this branch may add a lightweight operator strip inside the composed preview/status area.
- Recent hardware check on the attached camera confirmed that `c` coordinate copy with paste verification, `x`, `r`, `e`, `q`, `Esc`, and window-close shutdown all behaved as expected in the live preview path.
- Recent hardware check also confirmed the latest viewport refinements: cursor-anchored zoom and the thin visible-image outline behaved as intended on the attached camera.
- The hardware preview demo now also accepts `--exposure-time-us`, which was needed on the current setup because ambient light was insufficient for comfortable manual UI validation.
- A later hardware pass on the same setup also confirmed that `+` saved preview snapshots successfully once `--snapshot-save-directory` was configured.
- In preview paths without a focus provider, `y` now reports `Focus display unavailable` and is omitted from the shortcut hint line so operators are not told to toggle a feature that is not actually wired.
- Manual hardware validation on March 28, 2026 also showed that the new wheel-based cursor zoom is acceptable for the current MVP, but very small zoom factors can still introduce visible anchor drift from integer viewport rounding; keep that as roadmap hardening, not as a blocker for this branch.
- The same hardware validation pass also confirmed that middle-drag pan is workable for the current MVP and that the added `view=x,y` status readout is useful when the live scene is too dark to make viewport motion obvious by eye.
- MVP quality on this branch also includes operator-readable warnings/errors. The branch should prefer short action-oriented messages in the status band or terminal over raw exception dumps whenever common preview/demo failure paths occur.

## Execution Plan

1. Confirm branch and worktree before each substantial edit:
   - branch should remain `feature/opencv-ui-operator-block`
   - run `git status --short`
   - if unrelated changes appear, stop and classify them against `docs/branch_backlog.md` before mixing work
2. Re-read the current OpenCV module docs before the first code edit of a resumed session:
   - `apps/opencv_prototype/README.md`
   - `apps/opencv_prototype/STATUS.md`
   - `apps/opencv_prototype/ROADMAP.md`
   - `docs/STATUS.md`
3. Preserve the already completed preview interaction as the starting baseline rather than treating it as still-open roadmap work.
4. Implement UI Slice 1: bottom status band baseline.
   - move coordinate, warning, and preview-state text out of the image overlay
   - keep image pixels free for inspection overlays
   - keep crosshair and point-selection behavior intact
5. Extend UI Slice 1 with stable status-band content.
   - current status: completed baseline for preview mode / zoom, selected point coordinates, warning display, and UI feedback messages
   - keep this baseline intact while extending the band further
6. Add the next planned status-band content:
   - selected point coordinates
   - preview mode / zoom
   - warning-only capability-probe error if present
   - FPS readout
   - current status: completed for all four items above
7. Implement UI Slice 2: operator-facing toggles.
   - `x` for crosshair visibility
   - `y` for focus visibility
   - keep `c` for coordinate copy
   - keep toggle state in the OpenCV/UI layer rather than in driver, stream, or recording code
   - current status: completed for crosshair visibility and focus-status visibility in the status band
8. Implement UI Slice 3: local operator snapshot shortcut.
   - add `+`-based snapshot entry if the current preview integration can call an existing save path cleanly
   - do not move file naming or storage policy into the UI layer
   - note: this slice requires additional service wiring in the app/demo path and should not be reduced to a standalone key handler change
   - current status: completed through an acquisition-safe preview-frame save path that is enabled only when an explicit snapshot save directory is configured for the app/demo path
9. Implement UI Slice 4: first ROI entry points.
   - add rectangle entry through `r`
   - add ellipse entry through `e`
   - avoid collapsing ROI ownership into the preview window; prefer existing model/service boundaries
   - current status: completed for key-based mode entry points plus a first two-click ROI creation baseline that mirrors active ROI state into `RoiStateService`
   - hardware note: rectangle and ellipse entry/creation were manually validated on the attached camera at the current baseline
10. If time remains after the above slices, continue with the next roadmap-consistent preview work without crossing module boundaries:
   - operator-facing warning/error coverage for common unavailable actions and startup failures
   - further zoom hardening for cursor-outside-image edge cases
   - current status: warning/error coverage baseline, mouse-wheel zoom, and a first middle-drag pan baseline are completed; additional zoom hardening remains open
11. After each coherent slice, update tests first, then update permanent docs, then reassess whether the next slice still belongs on this branch.

## Git Handling

Use the repository git rules strictly for this package:

- do not create a new branch unless this branch becomes a scope mismatch
- do not mix repository reorganization, hardware validation, or unrelated doc cleanup into this branch
- keep commits small and ordered by UI slice
- before commit, verify that touched files belong to this work package
- before any merge discussion, re-read `docs/git_strategy.md`

Preferred commit sequence:

1. `feat: add preview status band baseline`
2. `feat: add preview interaction toggles`
3. `feat: add preview snapshot shortcut`
4. `feat: add roi entry points to opencv preview`
5. `docs: update opencv ui status after operator block`

If a slice naturally splits into behavior and tests, keep the split reviewable, but do not create noisy micro-commits for trivial text changes.

## Validation

- `.\.venv\Scripts\python.exe -m unittest tests.test_opencv_preview tests.test_opencv_smoke_demos tests.test_bootstrap`
- extend targeted preview tests for any new key, mouse, or status-band behavior
- if hardware is connected again later, run a short manual preview check on the OpenCV hardware demo

Validation expectations by slice:

- status band:
  - cover the new status composition and any rendering/layout helpers that are testable without a GUI dependency
- toggles:
  - add or extend tests for `x`, `y`, and unchanged `c` handling
- snapshot shortcut:
  - cover the local key path and verify existing snapshot service boundaries are still respected
- ROI entry points:
  - cover mode-switch and event-entry behavior even if full ROI editing remains partial

If the full targeted test block cannot be run in the current session, record what was not run in the final branch summary or commit handoff note.

## Documentation Updates

Before the work package is considered complete, update:

- `apps/opencv_prototype/STATUS.md`
- `apps/opencv_prototype/ROADMAP.md`
- `docs/STATUS.md`
- `docs/SESSION_START.md` if the active recovery link changes

Documentation intent for this package:

- `apps/opencv_prototype/STATUS.md`
  - move finished operator-facing preview work from partial/planned into working-now or implemented status
  - keep remaining UI gaps explicit
- `apps/opencv_prototype/ROADMAP.md`
  - remove or reword completed preview/UI bullets
  - keep only genuinely remaining next steps
- `docs/STATUS.md`
  - state what changed against both the repository roadmap and the global roadmap
  - update the next recommended step after the operator block advances
- `docs/SESSION_START.md`
  - update only if another work package becomes the preferred recovery link after this one progresses or completes

## Expected Commit Shape

1. `feat: add preview status band baseline`
2. `feat: add preview interaction toggles`
3. `feat: add preview snapshot shortcut`
4. `feat: add roi entry points to opencv preview`
5. `docs: update opencv ui status after operator block`

## Merge Gate

- already completed preview UI baseline remains intact
- new UI work stays in the OpenCV/display-facing layer
- touched OpenCV tests pass locally
- docs clearly distinguish completed UI baseline from still-open operator work
- repository-level status and module-local status/roadmap are aligned well enough that a new agent does not need to infer the current truth from code diffs alone

## Recovery Note

To resume this work:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/MODULE_INDEX.md`
4. Read `apps/opencv_prototype/README.md`
5. Read `apps/opencv_prototype/STATUS.md`
6. Read `apps/opencv_prototype/ROADMAP.md`
7. Read `docs/STATUS.md`
8. Read `docs/git_strategy.md`
9. Run `git branch --show-current`
10. Run `git status --short`

Then resume from the first incomplete slice in this order:

1. remaining viewport interaction hardening that still fits this branch
2. lightweight in-preview operator strip work, only if it still belongs on this branch after review

Before editing code after a resume:

- verify the current branch still matches this work package
- verify permanent docs still describe the same baseline assumed here
- if docs and code no longer match, update the permanent docs or replace this work package rather than layering conflicting notes on top
