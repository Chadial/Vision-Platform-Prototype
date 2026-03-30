# Module Documentation Audit And Shrink Pass

## Purpose

This work package defines one bounded meta-documentation slice for the post-closure Python baseline.

Closure lane:

- Post-Closure Python Baseline / Documentation Governance And Operational Readiness

Slice role:

- module-doc audit, shrink, and consistency pass

Scope level:

- module-local docs under `apps/`, `integrations/`, `services/`, and `libraries/`

Its purpose is to reduce ambiguity and drift in module-local `README.md`, `STATUS.md`, and `ROADMAP.md` files without turning the repository into a large documentation rewrite.

This package should be read as:

- a bounded documentation-governance cleanup slice
- not a repository-wide manual rewrite
- not central PM replanning

## Branch

- intended branch: `docs/module-doc-audit-shrink-pass`
- activation state: active lane

## Scope

Included:

- audit module-local `README.md`, `STATUS.md`, and `ROADMAP.md` files under:
  - `apps/`
  - `integrations/`
  - `services/`
  - `libraries/`
- identify active-module docs that still carry stale reorganization-phase or outdated next-step wording
- shrink active-module `ROADMAP.md` files when they mostly repeat central PM or old transition logic
- keep prepared-only modules short and explicit instead of broadening them
- update `docs/module_doc_audit.md` to reflect the post-pass state if the recommendations materially change

Excluded:

- broad rewrite of central docs
- end-user manual creation
- merging all module docs into one document
- changing module architecture or ownership

What this package does not close:

- all future module-doc upkeep
- the need for local module docs

## Session Goal

Leave the repository with module-local docs that are easier to trust and easier to read:

- `README.md` for purpose and boundaries
- `STATUS.md` for local implemented reality
- `ROADMAP.md` only where local future intent still adds value

## Execution Plan

1. Re-read:
   - `docs/DOCUMENTATION_PLAYBOOK.md`
   - `docs/module_doc_audit.md`
   - `docs/MODULE_INDEX.md`
2. Inventory current module-local docs under `apps/`, `integrations/`, `services/`, and `libraries/`.
3. For active modules:
   - remove stale reorganization or already-landed PM wording
   - keep `ROADMAP.md` only as narrow local future intent
4. For prepared-only modules:
   - keep docs short and explicit
   - avoid broad placeholder prose
5. Update `docs/module_doc_audit.md` if the keep/shrink guidance changes materially.
6. Update central status / workpackage docs only if the repository-wide reading of module-doc roles changes.

## Validation

- doc-only consistency review across active modules
- confirm that no module-local `ROADMAP.md` is treated as primary PM control
- confirm that active-module `STATUS.md` files no longer point at obviously outdated slices or phases

## Documentation Updates

Potentially affected:

- `docs/module_doc_audit.md`
- `docs/MODULE_INDEX.md`
- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- selected module-local `README.md`, `STATUS.md`, `ROADMAP.md`

## Expected Commit Shape

1. `docs: shrink and refresh module-local roadmaps`
2. `docs: align module status notes with post-closure baseline`
3. `docs: refresh module doc audit guidance`

## Merge Gate

- the slice remains module-doc-focused
- active-module docs are more current and less repetitive afterward
- prepared-only modules remain intentionally short
- no broad PM rewrite or architecture rewrite is bundled

## Recovery Note

To activate this work package later:

1. Read `AGENTS.md`
2. Read `docs/SESSION_START.md`
3. Read `docs/MODULE_INDEX.md`
4. Read `docs/DOCUMENTATION_PLAYBOOK.md`
5. Read `docs/module_doc_audit.md`
6. Read `docs/WORKPACKAGES.md`
7. Create the intended branch before substantive edits
