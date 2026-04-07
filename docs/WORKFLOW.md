# Workflow

## Purpose

This document defines the operational execution flow for agents working in this repository.

Use it to turn broad requests into a consistent sequence of branch selection, work-package selection, implementation, validation, and documentation updates.

## Core Principle

Work from explicit work packages and central status, not from scattered local notes.

The default loop is:

1. bootstrap context
2. identify branch fit
3. select or derive one concrete work package
4. implement the smallest meaningful end-to-end slice
5. validate the touched scope
6. update central status and work-package tracking
7. state the next recommended slice

## Execution Flow

### 1. Bootstrap

Read in this order:

1. `AGENTS.md`
2. `docs/SESSION_START.md`
3. `docs/MODULE_INDEX.md`

Then read:

- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`

Read `docs/ROADMAP.md` and `docs/GlobalRoadmap.md` only when roadmap alignment is needed.

### 2. Check Repository State

Before substantive changes:

1. check current branch
2. inspect `git status --short`
3. decide whether the current branch matches the work
4. read `docs/git_strategy.md` for repository-state changes
5. use `docs/branch_backlog.md` if the worktree is dirty or mixed

### 3. Choose The Work Package

If the user gave a concrete implementation task, execute that task directly after confirming branch fit and module context.

If the user gave a broad goal:

1. use `docs/STATUS.md` as the current truth
2. use `docs/WORKPACKAGES.md` as the primary queue
3. select the package marked `current next` unless the user request or current branch scope clearly overrides it
4. if no package is marked `current next`, derive the next smallest justified post-closure slice from concrete residuals or the user's explicit direction
5. open the referenced detailed `docs/session_workpackages/wpXX_*.md` file for execution details when one exists
6. derive the next smallest verifiable slice inside that package if needed
7. restate it in implementation terms before editing

Selection priority:

1. unblock later work
2. align with current implementation reality
3. stay locally verifiable
4. stay inside existing module boundaries
5. minimize churn

### 3a. Package Precision Rule

When creating a new work package or materially refining an active one, keep lane-level intent and slice-level scope explicitly separated.

At minimum, the package should make these points explicit:

- `Closure Lane`: the broader tactical lane the package belongs to
- `Slice Role`: for example `baseline`, `patch`, `extension`, `producer`, `consumer`, or `validation`
- `Scope Level`: whether the package touches stable context, run/session, artifact/per-image scope, or only a subset of those levels
- `Producer / Consumer / Structure impact`: whether the package is mainly structure-only, producer-facing, consumer-facing, or one narrow stated combination
- what the package does not close inside the lane
- which policy questions remain open and still require later testing or definition

Additional precision rules:

- if the package touches traceability, logging, metadata, save artifacts, or offline reuse, explicitly distinguish stable-context, run/session, and artifact/per-image placement rather than leaving those levels implicit
- if the package only defines metadata shape, say so explicitly; if it only writes metadata, say so explicitly; if it only consumes metadata, say so explicitly
- if a field or policy is not finalized, record that explicitly under a short section such as `Open Policy Questions`, `Not Yet Frozen`, or `Requires Later Testing/Definition`
- if the package title is broader than the selected slice, explicitly state that the package is only one narrow slice and does not close the whole lane
- keep package text explicit about what larger concerns are intentionally deferred

### 4. Read Only The Needed Local Context

Before editing a module, read:

- that module's `README.md`
- that module's `STATUS.md`

Read the module's `ROADMAP.md` only if:

- the local module plan is directly relevant
- or the module is currently `prepared only` and this is first activation work there

If the task may create a new module or move logic across root categories, also read:

- `docs/root_category_audit.md`

If the task may create a new module:

1. classify it with the `root_category_audit` decision matrix first
2. only then decide its root folder and module docs

### 5. Implement In One Coherent Pass

Default behavior:

- do the work rather than stopping at analysis
- complete closely related sub-steps in one run
- keep changes inside one coherent work package
- avoid speculative side quests

Ask for confirmation only when public contracts, dependencies, repository structure, or major architecture choices are affected.

### 6. Validate

Run the relevant local tests, smoke paths, or manual checks for the touched scope.

If full validation is not possible:

- run the narrowest meaningful validation
- record what was not verified

### 7. Update Documentation

When the work changes repository state:

- use `docs/DOCUMENTATION_PLAYBOOK.md` first to identify whether the affected docs are stable, operational, current-state, or boundary docs
- update `docs/STATUS.md`
- update `docs/WORKPACKAGES.md`
- update the active detailed `docs/session_workpackages/wpXX_*.md` file with progress, sub-work-package decisions, and discoveries
- update relevant module `STATUS.md` when module reality changed
- update `docs/MODULE_INDEX.md` only if module visibility or purpose changed

Context-window checkpoint rule:

- if discussion or implementation detail becomes dense enough that future sessions could lose decisions, assumptions, architecture boundaries, or deferred-policy notes, trigger a documentation checkpoint immediately rather than continuing with only chat context
- checkpoint minimum:
  - `docs/STATUS.md`
  - `docs/WORKPACKAGES.md`
  - active `docs/session_workpackages/wpXX_*.md`
- if the checkpoint cannot be completed immediately, emit an explicit warning that context-risk is increasing and schedule the checkpoint as the next step before further broad work

Default discipline:

- do not update all docs after every change
- update only the smallest doc set whose role was actually affected
- prefer one sharp additive clarification over large prose rewrites

### 8. Close The Slice

At the end of the slice:

- summarize completed work
- record validation
- state assumptions
- name the next recommended work package

If the slice completed a coherent topic branch and the merge gate is already satisfied:

- continue into the git completion flow instead of stopping at a "ready to merge" summary
- switch to the intended integration branch
- re-check clean state
- merge serially
- re-check after each merge
- delete merged local topic branches when they are no longer needed

Only stop before merge if the integration target is unclear, validation failed, a conflict appears, or an explicit review/hold requirement exists.

## Work-Package Quality Bar

A work package is well formed when it includes:

- a concrete goal
- explicit included scope
- explicit out-of-scope
- affected modules
- validation
- done criteria
- follow-up recommendation

For future package generation and refinement, that quality bar also requires:

- explicit lane vs. slice wording
- explicit scope-level wording where metadata/logging/traceability is involved
- explicit producer vs. consumer vs. structure ownership
- explicit recording of unresolved policy choices instead of silently freezing or omitting them
- explicit wording that keeps narrow slices visibly narrower than their lane titles

If a planned item is too large to satisfy those points, split it first.
