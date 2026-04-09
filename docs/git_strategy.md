# Git Strategy

## Purpose

This repository now follows a strict trunk-based workflow with short-lived branches. The goal is to keep `main` stable while making the migration from `camera_app` to the modular platform structure reviewable and reversible in small steps.

## Branch Rules

- `main` is the integration branch and should remain stable.
- Substantive work happens on short-lived branches only.
- One branch covers one coherent work package.
- Do not mix unrelated concerns in one branch.

## Branch Naming

Use one of these prefixes:

- `feature/`
- `fix/`
- `refactor/`
- `docs/`
- `test/`
- `chore/`

Examples:

- `refactor/platform-model-facades`
- `test/migrate-vision-platform-imports`
- `feature/focus-core-baseline`
- `fix/recording-stop-cleanup`
- `docs/reorg-status-sync`

## Required Scope Separation

Keep these concerns separate whenever possible:

- repository reorganization
- behavioral or runtime changes
- tests
- documentation
- hardware-specific integration changes

Good:

- one branch for import-surface migration
- one branch for ROI foundation
- one branch for real-hardware validation notes

Bad:

- one branch containing namespace migration, new ROI behavior, unrelated README rewrites, and formatting churn

## Commit Rules

Commits must be:

- small
- logically ordered
- reviewable without reconstructing the entire repository history

Preferred commit types:

- `feat:`
- `fix:`
- `refactor:`
- `test:`
- `docs:`
- `chore:`

Recommended format:

```text
<type>: <scope> <intent>
```

Examples:

- `refactor: expose control layer through vision_platform`
- `test: migrate command controller coverage to platform namespace`
- `docs: record repository git workflow`

## Git Execution Discipline

When git commands change repository state, execute them serially.

Do not run these in parallel:

- `git checkout` / `git switch`
- `git merge`
- `git rebase`
- `git commit`
- `git add`
- `git rm`
- branch deletion or rename commands

Reason:

- concurrent git mutations can create transient `index.lock` conflicts
- concurrent branch-changing and merge commands can produce misleading results such as a merge effectively running on the wrong checked-out branch
- this repository is used from Windows PowerShell where those race conditions are easy to trigger accidentally during automated sessions

Safe pattern:

1. run one state-changing git command
2. inspect the result with `git status --short`, `git branch --show-current`, or `git log --oneline -1` as needed
3. only then run the next state-changing git command

Apply the same pattern to merge cleanup:

1. merge one branch
2. inspect the result
3. only then merge the next branch or delete the merged topic branch

## Repository-State Documentation Discipline

Branch maintenance and general git maintenance are repository-state changes, not invisible housekeeping.

When those actions change what the repository currently is or how it should be read, update the durable docs in the same branch.

At minimum:

- re-check `docs/STATUS.md` whenever branch creation, branch switching, merge completion, branch deletion, backlog reassignment, or similar maintenance makes an existing status statement inaccurate
- keep the `Current Branch` section in `docs/STATUS.md` aligned with the actual checked-out branch when that section is meant to describe the active worktree state
- if a completed merge changes which branch now carries the integrated baseline, remove or rewrite stale topic-branch wording in `docs/STATUS.md`
- if git workflow policy changes, update this file in the same documentation slice instead of leaving the rule implicit in conversation only

The goal is not to log every transient git command.
The goal is to prevent durable project-state docs from drifting away from the actual repository state after git housekeeping.

## Expected Branch Flow

For a normal work package:

1. create branch from current `main`
2. implement one coherent change set
3. add or update tests for the touched scope
4. update docs if status, structure, or roadmap changed
5. run local validation
6. if the branch is internally consistent, continue through merge rather than stopping at a "ready" state
7. delete the local topic branch after merge unless there is a deliberate short-term reason to keep it

## Autonomous Merge Rule

Default behavior after a completed work package is:

1. validate the touched scope
2. confirm the worktree is clean on the topic branch
3. confirm the intended integration branch is clear
4. switch to the integration branch and re-check state
5. merge serially
6. re-check `git status --short` and `git log --oneline -1` after each merge
7. delete only those local topic branches that are now merged and not still needed for another immediate branch flow

Do not stop at "final commit" by default when the branch already satisfies its merge gate.

Ask for confirmation before merge only when one of these applies:

- the intended integration branch is unclear
- merge conflicts appear
- the branch includes unresolved mixed scope
- required validation is missing or failed
- there is an explicit review, release, or hold requirement for that branch

If none of those conditions apply, agents should proceed through the merge autonomously.

## Required Validation Before Merge

At minimum, run the relevant local checks for the touched scope.

Examples:

- namespace or service migration:
  - `.\.venv\Scripts\python.exe -m unittest`
- documentation-only branch:
  - verify linked paths and referenced commands still match the repository
- hardware-related branch:
  - document clearly whether validation is simulator-only or hardware-backed

## Rules For This Repository Specifically

- do not commit direct work on `main` except for trivial emergency fixes
- do not bundle module reorganization and new functional analysis features in one branch
- do not bundle broad rename churn without the corresponding tests
- use `docs/branch_backlog.md` to assign remaining worktree changes to future branches before committing mixed repository states
- when architecture changes touch module boundaries, update:
  - `docs/MODULE_INDEX.md`
  - relevant module `STATUS.md`
  - relevant module `ROADMAP.md`
  - `docs/STATUS.md` when roadmap position changed
- when branch maintenance or general git housekeeping changes durable repository-state truth, update `docs/STATUS.md` and any affected git workflow docs in the same branch
- periodically check which local branches are already merged into `main` and delete them before they become stale context
- if an old branch is clearly obsolete because the repository has moved on structurally or functionally, delete it explicitly rather than treating it as still-actionable work

## Recommended Next Branches

Based on the current repository state, there is no unconditional next branch.

Use these rules instead:

- if the documented tested camera path is attached again, prefer one narrow hardware-evidence branch such as `test/wp87-hardware-workflow-rerun`
- if hardware is still unavailable, derive the next smallest justified branch from current residuals, documentation drift, or an explicitly chosen later lane
- keep simulator-only confidence work, hardware revalidation, runtime behavior changes, and documentation hygiene on separate short-lived branches

## Immediate Execution Plan

The old branch-by-branch execution block below the current workflow-first chain is historical and should not be read as the default next action.

Current default:

1. read `docs/STATUS.md` and `docs/WORKPACKAGES.md`
2. confirm whether the next slice is:
   - conditional hardware evidence
   - non-hardware residual follow-up
   - documentation or git hygiene
3. create one short-lived branch that matches only that narrow scope
4. keep validation matched to the touched scope
5. merge and clean up locally merged topic branches when the merge gate is satisfied

If a new default lane is chosen later, this section should be rewritten to match that new lane explicitly rather than leaving stale branch plans here.
