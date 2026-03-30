# Module Doc Audit

## Purpose

This document records the current audit of module-local `README.md`, `STATUS.md`, and `ROADMAP.md` files under:

- `apps/`
- `integrations/`
- `libraries/`
- `services/`

Its purpose is to make the role of module-local docs explicit for fresh agents and to prevent project-planning drift back into scattered module roadmaps.

## Audit Rule

The central project-control documents remain:

- `docs/WORKPACKAGES.md`
- `docs/STATUS.md`
- `docs/WORKFLOW.md`
- `docs/SESSION_START.md`

Module docs are local context, not primary PM control.

## Decision Categories

- `keep`: file is useful in its current role
- `shrink`: file should stay but remain strictly local and concise
- `merge later`: file is currently acceptable but may later be collapsed if the module remains inactive for a long time
- `drop later`: only if the content remains redundant after future cleanup

## Audit Summary

### Global Decision

Current recommendation:

- keep all module `README.md`
- keep all module `STATUS.md`
- keep all current module `ROADMAP.md`, but treat most of them as `shrink`

Reason:

- the repository is explicitly organized around module-level delegation
- fresh agents still benefit from local module context
- many prepared modules need a small future-intent file because they do not yet have richer implementation context
- the main problem is not file count alone, but unclear ownership and usage

No immediate deletion is recommended in this audit pass.

## Per-Module Decisions

| Module | README.md | STATUS.md | ROADMAP.md | Audit Note |
| --- | --- | --- | --- | --- |
| `apps/camera_cli` | keep | keep | shrink | active module; roadmap must stay local to CLI-only concerns |
| `apps/opencv_prototype` | keep | keep | keep | active UI lane; local roadmap remains useful because UI-specific follow-up is intentionally separate |
| `apps/desktop_app` | keep | keep | keep | prepared-only module; short placeholder docs are currently acceptable |
| `apps/postprocess_tool` | keep | keep | keep | prepared-only module; short placeholder docs are currently acceptable |
| `integrations/camera` | keep | keep | shrink | active core; roadmap should stay focused on integration-specific next steps only |
| `services/stream_service` | keep | keep | shrink | active core; avoid repeating global project order |
| `services/recording_service` | keep | keep | shrink | active core; keep only storage/recording-local future intent |
| `services/display_service` | keep | keep | shrink | active but narrow module; roadmap should stay renderer/display-local |
| `services/api_service` | keep | keep | keep | prepared-only module; local future intent remains useful |
| `libraries/common_models` | keep | keep | shrink | active foundation; roadmap should stay contract-local |
| `libraries/roi_core` | keep | keep | shrink | active foundation; roadmap should stay ROI-local and not become MVP control |
| `libraries/focus_core` | keep | keep | shrink | active baseline; roadmap should stay method-/contract-local |
| `libraries/tracking_core` | keep | keep | keep | prepared-only module; local future intent remains useful |

## Fresh-Agent Usage Rule

### Active Modules

For active modules, a fresh agent should:

1. read the module `README.md` before editing code there
2. read the module `STATUS.md` before editing code there
3. read the module `ROADMAP.md` only when:
   - the selected work package is explicitly expanding that module
   - the module's next local contract decision matters

### Prepared-Only Modules

For prepared-only modules, a fresh agent should:

1. read `README.md`
2. read `STATUS.md`
3. read `ROADMAP.md`

Reason:

- prepared modules often have little implemented code
- their local roadmap is part of their meaning until they become active

## Cleanup Direction

The next cleanup pass should focus on:

1. shrinking active-module `ROADMAP.md` files that mostly repeat central priorities
2. keeping prepared-only module docs short and explicit
3. removing cross-document ambiguity, not deleting files aggressively

## Explicit Non-Goal

This audit does not recommend turning module-local docs into another PM stack.

The intended model remains:

- central PM and status in `docs/`
- local reality and boundaries in module docs

Repo-wide documentation role split:

- `docs/DOCUMENTATION_PLAYBOOK.md` is the central reference for stable docs, operational docs, current-state docs, and deferred/boundary docs
- this audit remains focused specifically on module-local documentation, not on replacing that broader playbook
