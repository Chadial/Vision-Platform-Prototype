# Migration Plan

## Phase 1: Analysis

- read the binding root documents
- inspect the current `src/camera_app` layout and runnable entry points
- identify camera, stream, recording, and OpenCV prototype boundaries

## Phase 2: Structural Preparation

- create repository-level module workspaces
- add `README.md`, `STATUS.md`, and `ROADMAP.md` for each key module
- introduce `src/vision_platform` as the new platform namespace

## Phase 3: Controlled Migration Surface

- expose existing camera, stream, recording, and prototype entry points through the new namespace
- add app-level wrapper scripts inside `apps/opencv_prototype`
- keep legacy `camera_app` imports working to avoid breaking tests and demos

## Phase 4: Foundation Modules

- add shared frame, ROI, and focus contracts
- add minimal ROI and focus core helpers
- prepare tracking and API module areas without forcing premature implementation

## Phase 5: Consolidation

- update `docs/GlobalRoadmap.md` to a platform-wide master roadmap
- update module index and root documentation
- verify the simulator-backed baseline still runs through the preserved paths
- assign remaining mixed worktree changes into future branches through `docs/branch_backlog.md`

## Recommended Next Migration Round

- start moving new development to `vision_platform` imports first
- add tests that exercise the new namespace directly
- then decide which legacy `camera_app` modules should be physically relocated behind the already documented module boundaries
- keep branch execution aligned with `docs/git_strategy.md` and `docs/branch_backlog.md`
