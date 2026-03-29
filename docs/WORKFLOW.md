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
4. open the referenced detailed `docs/session_workpackages/wpXX_*.md` file for execution details
5. derive the next smallest verifiable slice inside that package if needed
6. restate it in implementation terms before editing

Selection priority:

1. unblock later work
2. align with current implementation reality
3. stay locally verifiable
4. stay inside existing module boundaries
5. minimize churn

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

- update `docs/STATUS.md`
- update `docs/WORKPACKAGES.md`
- update the active detailed `docs/session_workpackages/wpXX_*.md` file with progress, sub-work-package decisions, and discoveries
- update relevant module `STATUS.md` when module reality changed
- update `docs/MODULE_INDEX.md` only if module visibility or purpose changed

### 8. Close The Slice

At the end of the slice:

- summarize completed work
- record validation
- state assumptions
- name the next recommended work package

## Work-Package Quality Bar

A work package is well formed when it includes:

- a concrete goal
- explicit included scope
- explicit out-of-scope
- affected modules
- validation
- done criteria
- follow-up recommendation

If a planned item is too large to satisfy those points, split it first.
