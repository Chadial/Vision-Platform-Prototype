# WP110 Local Shell Viewport Rendering Adapter Baseline

## Purpose

Move the wx shell's bitmap buffer lifecycle and viewport-image presentation glue out of the canvas widget into one bounded app-local adapter seam.

## Branch

- `refactor/wp110-local-shell-viewport-rendering-adapter`

## Closure Lane

- local shell display-boundary cleanup after landed `WP107` through `WP109`

## Slice Role

- baseline
- structure-only UI/display cleanup

## Scope

- extract the wx bitmap presentation lifecycle from `PreviewCanvas.update_view`
- keep the current viewport image conversion behavior unchanged
- keep overlay drawing, event translation, and shell status assembly in the current wx shell
- keep the adapter app-local rather than introducing a broader shared renderer framework

The new adapter owns only the bitmap/presentation bridge for the current wx canvas.

It must not own:

- overlay drawing
- mouse / keyboard / pointer event translation
- preview interaction state
- status formatting
- camera semantics
- runtime or transport semantics

The wx shell remains the caller that owns canvas painting and overlay composition.
The adapter only converts the already rendered viewport image into a wx-consumable bitmap lifecycle.

## Guardrails

- do not add a generic renderer abstraction
- do not introduce a new OpenCV path
- do not move preview interaction, status, or command semantics into the adapter
- do not redesign the image pipeline or the existing viewport mapping
- keep the slice app-local and bounded to the wx shell display path

## Out Of Scope

- no non-OpenCV frontend architecture redesign
- no shared presenter hierarchy
- no camera or recording behavior changes
- no overlay model changes
- no status model changes

## Affected Modules

- `apps/local_shell`
- local-shell preview tests

## Validation

- `.\.venv\Scripts\python.exe -m unittest tests.test_wx_preview_shell`

## Done Criteria

- the wx shell no longer owns the bitmap buffer lifecycle inline in `PreviewCanvas`
- the adapter takes a rendered viewport image and returns or maintains the wx bitmap presentation state for the canvas
- overlay drawing and interaction behavior remain unchanged
- the current viewport rendering output remains behaviorally identical

## Recommended Follow-Up

- only after this adapter baseline, decide whether any further renderer-facing cleanup is justified by a concrete residual rather than by cleanup momentum
- after `WP110`, do not derive additional local-shell display cleanup from the same refactor momentum alone
- any later non-OpenCV renderer or operator-control slice must be justified by a concrete residual, integration need, test failure, or user-observed workflow friction
