# Session Work Packages

## Purpose

This folder holds temporary, session-oriented work-package documents that make it easy to resume an interrupted effort without reconstructing the full context from scratch.

Use this folder for:

- active work-package handoff notes
- temporary execution plans tied to one branch or one validation effort
- short recovery references linked from `docs/SESSION_START.md` or `docs/STATUS.md`

Do not use this folder as the primary source for project prioritization. Central project-level work selection belongs in `docs/WORKPACKAGES.md`.

## Lifecycle

- keep active or in-progress work packages in this folder
- move finished work packages into `docs/archive/session_workpackages/`
- when archiving a finished work package, remove or update any recovery link from `docs/SESSION_START.md` and `docs/STATUS.md`

## Naming

Prefer descriptive lowercase filenames, for example:

- `wp04_hardware_validation_phase_9.md`
- `wp03_opencv_ui_operator_block.md`

## Recommended Structure

Use this structure unless there is a clear reason to keep the note smaller:

1. `Purpose`
2. `Branch`
3. `Scope`
4. `Session Goal`
5. `Execution Plan`
6. `Validation`
7. `Documentation Updates`
8. `Expected Commit Shape`
9. `Merge Gate`
10. `Recovery Note`

Practical guidance for each section:

- `Purpose`: why this work package exists and what interruption it protects against
- `Branch`: the intended branch name for the work
- `Scope`: explicit included and excluded concerns
- `Session Goal`: the concrete done-state for the current work package
- `Execution Plan`: ordered steps to carry the work
- `Validation`: tests, smoke runs, or manual checks that must be performed
- `Documentation Updates`: permanent docs that must be updated before the work is considered complete
- `Expected Commit Shape`: intended commit sequence when the work is large enough to benefit from it
- `Merge Gate`: what must be true before the work package is considered complete or merge-ready
- `Recovery Note`: the minimum read order for resuming the interrupted work

## Completion Rule

A session work package is ready to leave this folder when all of the following are true:

1. the stated session goal is achieved or explicitly closed out
2. required validation has been run for the touched scope
3. required permanent docs have been updated
4. any recovery links in `docs/SESSION_START.md` and `docs/STATUS.md` are no longer needed or have been updated
5. the remaining state is understandable without treating the work package as the active source of truth

When those conditions are met:

- move the file to `docs/archive/session_workpackages/`
- optionally add a short final outcome note near the top of the archived file
