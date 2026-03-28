# AGENTS.md

## Purpose

This repository is for a camera software project that starts as a Python prototype and is expected to evolve into a team-maintainable C#/.NET solution later.

The software must support:

- live preview on desktop
- single-image snapshot saving
- image-series or “video-like” acquisition
- externally controlled save paths and filenames
- camera configuration from an external control software
- future migration toward a web-capable architecture

The camera project is intended to be embeddable into a larger host application.  
It should not assume it is the top-level application.

---

## Session Bootstrap

At the start of every new session, do not assume prior context. Build working context from the repository documents in the smallest useful steps.

Use this file for durable repository rules.  
Use `docs/SESSION_START.md` for the operational startup flow, current baseline, and task-based reading map.

### Mandatory startup read order

1. `AGENTS.md`
2. `docs/SESSION_START.md`
3. `docs/MODULE_INDEX.md`

Then follow the task-based reads listed in `docs/SESSION_START.md`.

### Mandatory startup checks

Before making substantive changes:

1. check the current branch
2. inspect `git status --short`
3. verify whether the task belongs on the current branch or a new branch
4. identify the relevant module documentation before editing code
5. re-read `docs/git_strategy.md` for branch, commit, and merge constraints if the task changes repository state

If the current branch scope does not match the requested work, create a new branch before continuing.

Do not start substantive work on `main`. If the current branch is `main` and the task is not a trivial emergency fix, create the correct branch first.

If `git status --short` is not clean, use `docs/branch_backlog.md` to decide whether the existing worktree changes belong to the current task or must stay isolated.

### Local shell constraints

Assume the local shell environment is Windows PowerShell unless verified otherwise.

- `rg` may not be installed on this machine. If `rg` is unavailable, immediately fall back to PowerShell-native file and text search instead of retrying.
- PowerShell in this environment does not accept `&&` as a command separator. Run sequential commands as separate tool calls or use PowerShell-compatible structure instead of emitting `&&` and then recovering from the parser error.
- Prefer avoiding preventable shell retries that only rediscover these environment constraints.

### Working assumptions for new sessions

- `docs/SESSION_START.md` is the compact repository-entry document for new sessions
- `docs/STATUS.md` is the current implementation truth for what is already verified
- `docs/ROADMAP.md` is the repository delivery sequence
- `docs/GlobalRoadmap.md` is the platform-wide direction
- `docs/ProjectDescription.md` is the product and architecture intent reference
- `docs/ProjectAgents.md` is the repository reorganization and modularization operating guide
- root module docs under `apps/`, `integrations/`, `services/`, and `libraries/` describe module purpose and status, while implementation usually lives under `src/vision_platform/...` with some compatibility paths still under `src/camera_app/...`

Do not use `docs/archive/StartPrompt.md` as the primary startup document. It is retained only as historical reference material.

---

## Work package derivation rule

Do not derive implementation work directly from broad architectural prose alone.

When a user request is not already a narrowly scoped coding task, derive the next work package in this order:

1. Read `docs/SESSION_START.md`
2. Read `docs/STATUS.md`
3. Read `docs/ROADMAP.md`
4. Read `docs/GlobalRoadmap.md`
5. Identify the next highest-value unfinished work package that is:
   - consistent with current repository status
   - small enough to implement in one coherent pass
   - testable or at least locally verifiable
   - within the current branch scope, or suitable for a new branch if needed
6. Restate that work package in concrete implementation terms before editing code
7. Implement the work package
8. Update `docs/STATUS.md` to reflect what was completed and what remains next

When roadmap items are too large, split them into the smallest meaningful end-to-end slice before implementation.

Do not stop just because a roadmap item is broad.  
Convert broad roadmap intent into a concrete repository-scoped task and proceed unless an escalation condition applies.

---

## Work package selection rule

If multiple unfinished roadmap items are possible, prefer the item that best satisfies this order:

1. unblocks later work
2. is closest to current implementation reality
3. is verifiable locally
4. stays within existing module boundaries
5. minimizes architectural churn

Prefer the smallest end-to-end slice over broad partial rewrites.  
Prefer completing one coherent slice over starting multiple incomplete slices.

---

## High-level priorities

Always optimize for the following, in this order:

1. **Correctness and reliability**
2. **Simple, understandable architecture**
3. **Clean separation of concerns**
4. **Future portability to C#/.NET**
5. **Future compatibility with a browser/web UI**
6. **Performance optimizations only when needed**

Do not prematurely introduce heavy frameworks, unnecessary abstractions, or distributed architecture.

---

## Project stage assumptions

Assume the current stage is:

- Python-first
- prototyping in PyCharm
- local execution on Windows
- Allied Vision / Vimba X context is likely
- later handover to a C# software team is expected
- long-term architecture should remain UI-agnostic
- real camera hardware may be temporarily unavailable during development

When making implementation decisions, prefer patterns that are easy to port from Python to C#.

---

## Non-goals

Avoid pushing the project toward any of the following unless explicitly requested:

- Qt / PyQt based GUI
- overengineered microservice architecture
- cloud-first architecture
- Docker/Kubernetes as a default
- unnecessary external dependencies
- framework-heavy solutions for simple local tasks
- experimental architecture that makes later team handover harder

---

## Core architectural rule

Keep **camera logic**, **recording logic**, **configuration**, and **UI** separate.

Prefer this conceptual split:

- **models**  
  configuration objects, request objects, status objects

- **driver layer**  
  camera SDK specific code only

- **application/service layer**  
  snapshot, recording, preview, logging, command handling

- **UI layer**  
  desktop preview, future web UI, or host integration

Do not mix SDK calls directly into UI code unless explicitly asked for a quick throwaway prototype.

Use the same separation for **real hardware** and **simulated sources**:

- real camera access belongs in SDK-specific driver implementations
- simulated or demo behavior belongs in separate driver implementations
- services should work against the same `CameraDriver` abstraction for both paths

This keeps testing and demos possible even when hardware is unavailable.

---

## Preferred domain model

When introducing or refactoring code, try to align naming with these concepts:

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

If you propose alternatives, keep them close to these names unless there is a strong reason not to.

---

## Command model

Assume the external control software will eventually need to issue commands similar to:

- `ApplyConfiguration(config)`
- `SetSaveDirectory(path)`
- `SaveSnapshot(request)`
- `StartRecording(request)`
- `StopRecording()`
- `GetStatus()`

Design code so these commands can later be called:

- directly from C# host code
- from a local desktop UI
- or from a future web/API layer

Architectural intent for command surfaces:

- keep one host-neutral command/application surface as the primary control layer
- treat CLI as a thin local adapter for development, smoke tests, and operator/developer shell usage
- treat API/feed exposure as a separate external adapter that should reuse the same command/application surface
- do not duplicate business logic across CLI, API, desktop UI, or web-facing layers

---

## Preview and recording rules

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
- writer thread/service for saving
- explicit stop conditions

Do not assume that preview frame rate and recording frame rate are the same.

When hardware is unavailable, prefer a **simulated camera driver** over bypassing the architecture.  
For demo scenarios, simulated drivers may use deterministic generated frames or real sample image sequences, as long as that behavior remains explicit and separate from SDK code.

---

## File and storage rules

Always make save paths explicit and configurable.

When saving images or sequences:

- never hardcode final output directories
- allow external control of save location
- keep naming deterministic
- keep logging aligned with saved files
- avoid hidden side effects

If a file naming scheme is needed, propose one clearly before spreading it across the codebase.

---

## Logging rules

Logging is important.

Prefer structured, useful logging over noisy logging.

At minimum, log:

- camera initialization
- configuration application
- preview start/stop
- snapshot save attempts/results
- recording start/stop
- save path used
- frame count if relevant
- warnings and failures

When frame-level logging is needed, keep it practical and not excessively verbose.

---

## Python coding guidelines

Use Python as a prototyping and validation language, but write it as if a later C# port is likely.

Prefer:

- small modules
- explicit classes where they clarify responsibilities
- dataclasses for lightweight data models
- type hints where useful
- simple, readable control flow
- clear docstrings on public classes and functions

Avoid:

- magic globals
- deeply implicit state
- giant script files
- UI code mixed with camera SDK code
- clever one-liners that reduce readability

If writing a quick prototype, keep it easy to refactor into services later.

---

## C# portability rule

When writing Python, prefer structures that translate well into C#:

Good candidates:

- explicit request objects
- service classes
- interface-like separation by responsibility
- clear state transitions
- configuration objects with validation

Avoid Python-specific patterns that would make a C# port awkward unless explicitly justified.

---

## WebUI future rule

The system may later gain a browser-based UI for desktop, tablet, or phone.

Therefore:

- do not bind core logic to a specific desktop UI toolkit
- keep commands and status exchange clean
- assume a future transport layer may exist
- keep preview generation separable from UI rendering

This does **not** mean building a web app now.  
It means avoiding design choices that would block one later.

---

## Dependency policy

Before adding a new dependency:

1. check whether the standard library is enough
2. check whether an existing project dependency already solves it
3. prefer smaller, stable dependencies
4. explain why the dependency is needed

Do not add large frameworks for narrow tasks without justification.

---

## Refactoring policy

When refactoring:

- preserve behavior unless asked otherwise
- explain structural changes briefly
- reduce coupling
- improve naming
- avoid wide-scope rewrites unless necessary

If a larger rewrite seems justified, propose it first in a short plan.

---

## Default execution behavior

Within the approved repository scope, execute the next complete and reasonable implementation step without stopping for confirmation.

Default behavior:
- do the work, not only the analysis
- prefer one coherent implementation pass over many tiny confirmation cycles
- complete closely related sub-steps in one run when they are clearly part of the same task
- after implementation, provide a concise summary of:
  - files changed
  - checks/tests run
  - assumptions made
  - any remaining open issues

Do not ask for confirmation for:
- small or medium refactors inside the active module scope
- local naming cleanups that follow existing repository conventions
- adding internal helper functions or classes
- updating tests that directly belong to the changed code
- updating nearby documentation that reflects the implemented change
- creating small supporting files already implied by the task
- choosing between obvious local implementation details when repository conventions already suggest the better option

Ask for confirmation only if one of these is true:
- public API or externally consumed contract must change
- a new dependency is needed
- the task requires edits outside the agreed or obvious scope
- build, packaging, CI, installer, or repository structure must change materially
- destructive or hard-to-revert actions would be taken
- multiple architecture options are plausible and the choice would affect future work significantly

If the task is reasonably clear, implement first and summarize after.  
Do not stop merely to restate the plan unless the task is genuinely ambiguous.

---

## Planning behavior

For small tasks:
- implement directly

For medium or large tasks:
- give a short plan only when it improves clarity
- then proceed directly with implementation in reviewable chunks
- do not pause after planning unless an actual escalation condition is met

For uncertain requirements:
- make the smallest reasonable assumption
- state the assumption clearly
- continue unless the assumption would change public behavior, architecture, or scope materially

---

## Task completion rule

When implementing a task, aim to finish the smallest meaningful end-to-end slice, not just a fragment.

A task slice is preferred when it includes, where applicable:
- code change
- directly related test adjustment or validation
- minimal documentation/status update if affected

Do not stop after only partial code edits if the directly related validation or nearby cleanup can be completed within the same scope.

---

## Git strategy

Use a simple trunk-based workflow.

- keep `main` stable and understandable
- use short-lived feature branches for coherent work packages
- prefer one branch per phase or sub-phase when practical
- keep commits small and reviewable
- separate structural refactors from SDK integration work
- merge only after the affected scope has been validated locally

Operational rules from now on:

- never develop directly on `main` for substantive changes
- create one branch per coherent work package, not per day and not per tiny edit
- branch names must describe scope, for example:
  - `feature/reorg-platform-imports`
  - `feature/roi-foundation`
  - `fix/recording-cleanup-state`
  - `docs/module-roadmaps`
- one branch must not mix unrelated concerns, especially not:
  - architecture reorganization and feature work
  - functional changes and broad formatting churn
  - hardware integration changes and documentation-only edits
- commits must stay focused and ordered so they can be reviewed independently
- before merge, run the relevant local validation for the touched scope
- merge to `main` only when the branch is in a stable, documented, test-backed state
- for mixed or partially completed repository states, use `docs/branch_backlog.md` as the required file-to-branch assignment before staging or committing

Branch choice should not block progress unnecessarily.  
If the requested work clearly fits the current non-main branch scope, continue directly.  
Only stop to branch-switch or create a new branch when the mismatch is substantive.

Preferred commit structure:

- commit 1: structural move or namespace prep
- commit 2: behavioral adaptation
- commit 3: tests
- commit 4: docs/status/roadmap updates

Commit message format:

- `<type>: <scope> <intent>`
- preferred types:
  - `feat:`
  - `fix:`
  - `refactor:`
  - `test:`
  - `docs:`
  - `chore:`

Examples:

- `refactor: move platform-facing imports to vision_platform`
- `test: migrate service tests to vision_platform namespace`
- `docs: update module roadmap after namespace migration`

Definition of ready to merge:

- relevant tests pass locally
- affected docs are updated if structure, status, or roadmap changed
- no unrelated file churn is bundled in the branch
- the branch leaves the repository in a runnable or at least internally consistent state

Branch cleanup expectation:

- after a branch is merged into `main`, delete the local branch promptly unless there is a specific short-term reason to keep it
- when a branch has become obsolete because the repository structure or product scope moved on, delete it explicitly instead of keeping it as an unreviewed historical side branch
- before starting new work, prefer a quick check of merged vs. unmerged local branches so stale topic branches do not accumulate and confuse branch selection

Preferred branch examples:

- `feature/phase-2a-driver-init`
- `feature/phase-2b-camera-config`
- `feature/phase-2c-single-frame`
- `feature/phase-2d-snapshot-save`

Commit messages should describe concrete technical intent clearly enough that a later C# team can follow the system evolution.

---

## Testing expectations

For logic-heavy code, prefer adding lightweight tests where practical.

Focus especially on:

- configuration validation
- path/naming logic
- recording stop conditions
- queue/buffer behavior
- state transitions

Do not create a large test harness unless the project is ready for it.

---

## Documentation expectations

When creating or updating code, also improve local clarity through:

- concise module docstrings where useful
- comments on non-obvious behavior
- short README notes for setup or run steps if needed

Avoid comment noise.  
Comment intent, constraints, and edge cases — not trivial syntax.

---

## Documentation source of truth

Use the following project documents together and keep their roles distinct:

- `AGENTS.md`  
  working rules, architecture constraints, implementation behavior, and repository conventions

- `docs/SESSION_START.md`  
  compact session bootstrap, current baseline, and task-based reading map

- `docs/ROADMAP.md`  
  implementation roadmap for the repository-specific phased delivery plan

- `docs/GlobalRoadmap.md`  
  higher-level long-term roadmap from Python prototype to C# handover and later web-capable architecture

- `docs/STATUS.md`  
  current implementation status, known gaps, verified progress, and next recommended steps

- `docs/git_strategy.md`  
  operational git workflow, branch structure, commit discipline, and merge rules

- `docs/branch_backlog.md`  
  assignment of still-open worktree changes to future branches so unfinished work does not leak into `main`

- `docs/archive/StartPrompt.md`  
  archived historical prompt material only; not the primary startup source for new sessions

When updating `docs/STATUS.md`, always relate the current state to both:

- `docs/ROADMAP.md`
- `docs/GlobalRoadmap.md`

This means status updates should explicitly state:

- what is complete against the repository roadmap
- what is complete or still missing against the global roadmap
- which next step is recommended in that context

For module-local documentation, keep these meanings strict:

- `README.md` describes module purpose, boundaries, and intended contract surface
- `ROADMAP.md` may include target-facing or planned contract surface that is not fully implemented yet, as long as that future intent is explicit
- `STATUS.md` must describe the current implemented state, current gaps, current next step, and any exposed-but-not-yet-implemented contract elements
- when a model, enum, request field, or shape is intentionally exposed ahead of implementation, `STATUS.md` must mark that feature as prepared, partial, deferred, or otherwise not yet supported end-to-end
- if a failed or rejected approach would help prevent repeated dead-end work, record that outcome briefly in the relevant module `STATUS.md` or `ROADMAP.md`
- keep module-local `STATUS.md` and `ROADMAP.md` aligned so target intent and current reality do not drift apart

---

## Preferred output style for this repository

When proposing code changes:

- be concrete
- keep code readable
- prefer maintainability over cleverness
- make assumptions explicit
- note portability implications when relevant

When proposing architecture:

- separate “prototype choice” from “long-term choice”
- identify what is temporary and what should survive migration
- keep the handover path to C# visible

---

## Default implementation bias

Unless instructed otherwise, prefer this path:

- Python prototype first
- clear service-oriented internal structure
- no hard dependency on a GUI framework
- ready for later C# reimplementation or gradual replacement
- future web UI enabled by separation, not by overbuilding now