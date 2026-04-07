# AGENTS.md

## Purpose

This repository is a Python-first camera and vision-platform prototype that is expected to evolve into a maintainable C#/.NET-ready solution.

The software must support:

- live preview on desktop
- single-image snapshot saving
- image-series or video-like acquisition
- externally controlled save paths and filenames
- camera configuration from an external control software
- future migration toward a web-capable architecture

The project is intended to be embeddable into a larger host application. It must not assume it is the top-level application.

---

## Working Model

This repository now uses a more centralized operating model:

- `AGENTS.md` defines durable agent behavior and decision rules
- `docs/SESSION_START.md` is the compact session bootstrap
- `docs/WORKFLOW.md` defines the operational execution flow
- `docs/WORKPACKAGES.md` is the central work-package queue and prioritization surface
- `docs/STATUS.md` is the central implementation truth
- `docs/ROADMAP.md` is the repository delivery sequence
- `docs/GlobalRoadmap.md` is the platform-wide direction
- module-local docs are supporting context, not the primary planning source

Do not treat scattered module `ROADMAP.md` files as the main project-planning mechanism. Project prioritization and active sequencing belong in the centralized docs above.

---

## Mandatory Startup Read Order

Read these in order at the start of every new session:

1. `AGENTS.md`
2. `docs/SESSION_START.md`
3. `docs/MODULE_INDEX.md`

Then continue based on task type:

- implementation or validation work:
  - `docs/STATUS.md`
  - `docs/WORKPACKAGES.md`
- planning or next-step derivation:
  - `docs/STATUS.md`
  - `docs/WORKPACKAGES.md`
  - `docs/ROADMAP.md`
  - `docs/GlobalRoadmap.md`
- repository-state changes:
  - `docs/git_strategy.md`
- dirty or mixed worktree:
  - `docs/branch_backlog.md`
- module-specific implementation:
  - that module's `README.md`
  - that module's `STATUS.md`
  - only read that module's `ROADMAP.md` if a local module plan is directly needed

---

## Mandatory Startup Checks

Before substantive changes:

1. check the current branch
2. inspect `git status --short`
3. verify whether the task belongs on the current branch or a new branch
4. identify the relevant module documentation before editing code
5. re-read `docs/git_strategy.md` if the task changes repository state

If the current branch scope does not match the requested work, create a new branch first.

Do not start substantive work on `main`. If the current branch is `main` and the task is not a trivial emergency fix, create the correct branch before continuing.

If `git status --short` is not clean, use `docs/branch_backlog.md` to decide whether the existing changes belong to the current task or must stay isolated.

---

## Autonomy Rule

Default to autonomous execution inside the approved repository scope.

That means:

- derive the next concrete work package when the user gives a broad goal
- make the smallest reasonable assumption when details are missing
- implement the full smallest meaningful slice in one pass when practical
- update central status and work-package docs when the work changes project state
- summarize decisions and assumptions after implementation instead of pausing early

Do not ask for confirmation unless one of these is true:

- a public or externally consumed contract must change
- a new dependency is needed
- the task requires edits outside the obvious scope
- build, packaging, CI, installer, or repository structure must change materially
- destructive or hard-to-revert actions would be taken
- multiple architecture options are plausible and the choice would affect future work materially

If none of those conditions apply, continue.

---

## Work-Package Rule

Do not derive implementation work directly from broad architectural prose alone.

When the user request is not already a narrowly scoped coding task:

1. read `docs/STATUS.md`
2. read `docs/WORKPACKAGES.md`
3. read `docs/ROADMAP.md` only if roadmap alignment is needed
4. read `docs/GlobalRoadmap.md` only if long-range direction matters
5. select the highest-value unfinished work package that is:
   - consistent with current repository status
   - small enough to complete in one coherent pass
   - locally verifiable, or at least clearly checkable
   - within the current branch scope, or suitable for a new branch
6. restate that work package in concrete implementation terms
7. implement it
8. update `docs/STATUS.md` and `docs/WORKPACKAGES.md`

When roadmap items are too large, split them into the smallest end-to-end slice first.

---

## Work-Package Selection Priority

If multiple unfinished work packages are available, prefer the one that best satisfies this order:

1. unblocks later work
2. is closest to current implementation reality
3. is verifiable locally
4. stays within existing module boundaries
5. minimizes architectural churn

Prefer one completed slice over multiple partial starts.

---

## Project-Management Rule

Treat the repository as a sequence of explicit work packages, not as an open-ended pool of ideas.

Every non-trivial work package should have:

- goal
- scope
- out-of-scope
- affected modules
- validation
- done criteria
- recommended follow-up

Use `docs/WORKPACKAGES.md` as the central queue for current and next work.

Use `docs/session_workpackages/` as the detailed execution layer once a package has been selected from `docs/WORKPACKAGES.md`.

Do not use `docs/session_workpackages/` as the primary prioritization system.

---

## Documentation Governance

Prefer centralized project guidance over repeated local planning text.

Use document roles strictly:

- `AGENTS.md`: durable agent behavior, repository rules, autonomy limits
- `docs/SESSION_START.md`: compact startup flow and reading map
- `docs/WORKFLOW.md`: execution flow from request to validation to doc updates
- `docs/WORKPACKAGES.md`: active queue, work-package definitions, selection order
- `docs/STATUS.md`: current verified implementation state and next recommendation
- `docs/ROADMAP.md`: repository-level delivery phases
- `docs/GlobalRoadmap.md`: platform-wide master direction
- `docs/MODULE_INDEX.md`: fast module lookup

For module-local docs:

- `README.md` should remain and describe purpose, boundaries, interfaces, and dependencies
- `STATUS.md` should exist for active or risky modules and describe current implemented state
- `ROADMAP.md` should only carry module-local future intent when that local plan is genuinely useful

Fresh-agent usage rule:

- active modules:
  - read `README.md` and `STATUS.md` before edits
  - read `ROADMAP.md` only when the selected work package is expanding that module's local future path
- prepared-only modules:
  - read `README.md`, `STATUS.md`, and `ROADMAP.md` before first activation work

Use `docs/module_doc_audit.md` as the current governance reference for keep/shrink decisions and module-doc usage.

Avoid duplicating central priorities across many module `ROADMAP.md` files.

If central docs and module docs disagree, central project docs win for prioritization, while module `STATUS.md` wins for that module's implemented reality.

---

## Context Window Discipline

Treat conversational context as finite and non-authoritative.

When implementation, planning, or architecture discussion accumulates enough detail that later sessions could lose decisions, assumptions, or boundaries, trigger a short mandatory documentation checkpoint before continuing broad changes.

At minimum, record the current truth in:

- `docs/STATUS.md` for verified state and active residuals
- `docs/WORKPACKAGES.md` for current-next selection and ordering impact
- the active `docs/session_workpackages/wpXX_*.md` file for slice-specific policy decisions and deferred items

If this checkpoint is skipped, warn explicitly that context compression risk is increasing and request/perform the documentation step next.

---

## High-Level Priorities

Always optimize for the following, in order:

1. correctness and reliability
2. simple, understandable architecture
3. clean separation of concerns
4. future portability to C#/.NET
5. future compatibility with a browser/web UI
6. performance optimization only when needed

Do not prematurely introduce heavy frameworks, unnecessary abstractions, or distributed architecture.

---

## Architecture Rules

Keep camera logic, recording logic, configuration, and UI separate.

Prefer this split:

- models:
  configuration objects, request objects, status objects
- driver layer:
  camera SDK specific code only
- application/service layer:
  snapshot, recording, preview, logging, command handling
- UI/display layer:
  desktop preview, operator controls, overlays, future web UI, or host integration adapters

Use the same separation for real hardware and simulated sources:

- real camera access belongs in SDK-specific driver implementations
- simulated behavior belongs in separate driver implementations
- services must work against the same `CameraDriver` abstraction

Do not mix SDK calls directly into UI code unless explicitly requested for a throwaway prototype.

Repository category rule:

- `apps/`: runnable application or frontend shells
- `integrations/`: external SDK, hardware, or system adapters
- `services/`: workflow and orchestration modules above libraries and integrations
- `libraries/`: reusable core contracts, kernels, and technical/domain building blocks

When category fit is unclear, use `docs/root_category_audit.md` before creating or moving modules.

---

## Preferred Domain Model

When introducing or refactoring code, prefer names close to:

- `CameraConfiguration`
- `SnapshotRequest`
- `RecordingRequest`
- `RecordingStatus`
- `CameraStatus`
- `PreviewFrameInfo`
- `CameraDriver`
- `PreviewService`
- `RecordingService`
- `LogService`

---

## Command Model

Assume the external control software will eventually need commands similar to:

- `ApplyConfiguration(config)`
- `SetSaveDirectory(path)`
- `SaveSnapshot(request)`
- `StartRecording(request)`
- `StopRecording()`
- `GetStatus()`

Keep one host-neutral command/application surface as the primary control layer.

CLI is a thin local adapter for development and smoke tests.

Future API or feed work must reuse the same command/application surface rather than duplicate business logic.

---

## Preview And Recording Rules

Treat preview and recording as separate concerns.

Preferred behavior:

- preview should remain responsive
- recording must not block acquisition
- saving to disk must not block acquisition
- the latest frame may be used for preview
- recording selection may be time-based, trigger-based, or count-based

Prefer patterns such as:

- producer/consumer
- bounded queues
- latest-frame buffer for preview
- writer thread or service for saving
- explicit stop conditions

Do not assume that preview frame rate and recording frame rate are the same.

When hardware is unavailable, prefer a simulated camera driver instead of bypassing the architecture.

---

## File, Logging, And Python Rules

Always make save paths explicit and configurable.

When saving images or sequences:

- never hardcode final output directories
- allow external control of save location
- keep naming deterministic
- keep logging aligned with saved files
- avoid hidden side effects

At minimum, log:

- camera initialization
- configuration application
- preview start/stop
- snapshot save attempts/results
- recording start/stop
- save path used
- frame count if relevant
- warnings and failures

Write Python as a prototype that is still easy to port to C#:

- small modules
- explicit classes where they clarify responsibility
- dataclasses for lightweight models
- type hints where useful
- simple control flow
- clear public docstrings

Avoid:

- magic globals
- deeply implicit state
- giant script files
- UI code mixed with camera SDK code
- clever one-liners that reduce readability

---

## Dependency, Refactoring, And Completion Rules

Before adding a dependency:

1. check whether the standard library is enough
2. check whether an existing dependency already solves it
3. prefer smaller, stable dependencies
4. explain why it is needed

When refactoring:

- preserve behavior unless asked otherwise
- reduce coupling
- improve naming
- avoid wide-scope rewrites unless necessary

When implementing a task, finish the smallest meaningful end-to-end slice:

- code change
- directly related tests or validation
- minimal status/work-package updates if affected

Do not stop after a partial code edit if the adjacent validation and documentation can still be completed in the same scope.

---

## Git Strategy

Use a simple trunk-based workflow.

- keep `main` stable
- use short-lived branches for coherent work packages
- keep commits focused and reviewable
- separate structural refactors, behavior changes, tests, and docs when practical
- merge only after relevant local validation
- after a work-package branch is complete, validated, and scope-clean, continue through the merge flow by default instead of stopping at "ready to merge"
- do not treat "committed" as the default stopping point when the merge gate is already satisfied

Branch names must describe scope, for example:

- `feature/roi-foundation`
- `fix/recording-cleanup-state`
- `docs/centralize-workflow-governance`

When git commands change repository state, run them serially and re-check branch or worktree state before the next state-changing command.

Autonomous merge rule:

- once a coherent work-package branch has:
  - passed the relevant local validation
  - updated the required permanent docs
  - shown no unrelated worktree changes
  - and introduced no unresolved scope conflict with the intended integration branch
- agents should by default:
  1. switch to the intended integration branch
  2. re-check branch and clean worktree state
  3. merge serially
  4. re-check state after each merge
  5. delete only those local topic branches that are now merged and no longer needed
- stop for confirmation only if a merge conflict, validation failure, unclear integration target, or policy-sensitive risk appears

Use `docs/git_strategy.md` as the operational source for branch, commit, and merge constraints.

---

## Documentation Update Rule

Update documentation when the implementation or operating model changes.

At minimum, update:

- `docs/STATUS.md` when verified implementation state changes
- `docs/WORKPACKAGES.md` when work-package priority or completion changes
- `docs/MODULE_INDEX.md` when module visibility or meaning changes
- relevant module `STATUS.md` when a module's implemented state changes materially

When updating `docs/STATUS.md`, relate the current state to:

- `docs/ROADMAP.md`
- `docs/GlobalRoadmap.md`

---

## Default Implementation Bias

Unless instructed otherwise, prefer this path:

- Python prototype first
- clear service-oriented internal structure
- no hard dependency on a GUI framework
- ready for later C# reimplementation or gradual replacement
- future web UI enabled by separation, not by overbuilding now
