# Documentation Playbook

## Purpose

This document defines the practical documentation model for this repository.

It is intended to keep the documentation:

- easier to navigate
- cheaper to maintain
- less likely to drift
- useful for operation, handover, and current project steering

This playbook is intentionally lightweight.

It does not create:

- one giant manual
- a full documentation rewrite obligation
- a requirement to update every document after every change

## Documentation Model

The repository should use a layered documentation model.

### 1. Stable docs

Role:

- capture knowledge that should change rarely
- explain long-lived structure, boundaries, terminology, and stable contract intent

Typical content:

- architecture principles
- project description and target picture
- root category rules
- module responsibilities
- stable host/control surface boundaries
- stable metadata or traceability model boundaries

Current examples:

- `AGENTS.md`
- `docs/ProjectDescription.md`
- `docs/ARCHITECTURE_BASELINE.md`
- `docs/architecture_principles.md`
- `docs/root_category_audit.md`
- `docs/COMMANDS.md`
- `docs/HOST_CONTRACT_BASELINE.md`
- module `README.md`

Expected update frequency:

- low

### 2. Operational docs

Role:

- explain how to run, validate, operate, and troubleshoot the current working baseline
- capture known-good workflows and practical execution paths

Typical content:

- runbooks
- launch guidance
- hardware evaluation procedures
- known-good command paths
- troubleshooting notes

Current examples:

- `docs/MANUALS_INDEX.md`
- `docs/PYTHON_BASELINE_RUNBOOK.md`
- `docs/ENTRYPOINT_AND_LAUNCH_BASELINE.md`
- `docs/HARDWARE_EVALUATION.md`
- `docs/HARDWARE_CAPABILITIES.md`
- launcher or app usage sections in module docs

Expected update frequency:

- medium
- only when the validated workflow or operating assumptions change

### 3. Current-state docs

Role:

- capture what is currently true in the repository
- steer active PM sequencing
- record active residuals, landed work, and next recommendations

Typical content:

- implementation truth
- workpackage ordering
- active residuals and current gaps
- phase status

Current examples:

- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- `docs/ROADMAP.md`
- `docs/GlobalRoadmap.md`
- `docs/StatusHistory.md`
- `docs/StatusReport.md`
- active files under `docs/session_workpackages/`

Expected update frequency:

- higher than stable or operational docs
- only when project truth, PM order, or verified residuals actually change

Single-source rule inside this class:

- `docs/STATUS.md` is the only authoritative repository status document
- `docs/WORKPACKAGES.md` is the only authoritative repository work queue
- `docs/StatusHistory.md` is supporting history only, not the authoritative current-state carrier
- other current-state docs should be treated as derived, supporting, historical, or long-range views unless explicitly stated otherwise

### 4. Deferred and boundary docs

Role:

- make explicit what is stable now versus intentionally deferred
- reduce accidental over-promising
- support later handover and productization without forcing immediate expansion

Typical content:

- stable-now versus deferred-later boundaries
- current scope limits
- later-handover or later-productization notes

Current examples:

- `docs/HOST_CONTRACT_BASELINE.md`
- selected boundary sections in `docs/STATUS.md`
- workpackage scope and exclusion sections

Expected update frequency:

- low to medium
- only when the documented boundary actually changes

## Recommended Repo Layout

Keep the layout simple and repo-native.

### Central docs under `docs/`

Recommended grouping by role:

- stable project docs:
  - architecture, principles, category rules, command vocabulary, contract-baseline docs
- operational docs:
  - runbooks, hardware guidance, launch guidance
- current-state docs:
  - status, workpackages, roadmap, status report
- execution docs:
  - `docs/session_workpackages/`
  - `docs/archive/session_workpackages/`

This does not require moving all files into new folders immediately.

The practical rule is:

- keep existing useful files where they are
- make their role explicit
- add new documents only where they reduce confusion

### Module docs

Module docs should remain local to the module and stay small:

- `README.md`:
  - stable module purpose and boundaries
- `STATUS.md`:
  - current implemented reality for that module
- `ROADMAP.md`:
  - only local future intent when genuinely useful

Module docs are local context, not the main PM stack.

### Machine-readable formats

Default human-maintained format:

- Markdown `.md`

Use JSON or YAML only when machine-readable structure is genuinely useful, for example:

- hardware profiles
- exported structured capability snapshots

PDF should remain export-only if ever needed.

Do not use HTML, XML, or plain TXT as the primary maintained format without a strong reason.

## Documentation Update Rules

### Stable docs

Update only when:

- architecture changes
- stable contracts change
- persistent behavior guarantees change
- long-lived terminology changes
- module responsibilities or boundaries change

Do not update just because:

- one bug was fixed
- one residual changed
- one workpackage landed without changing stable structure

### Operational docs

Update only when:

- validated workflows change
- preferred run order changes
- hardware procedure changes
- launch instructions change
- expected outputs change
- troubleshooting guidance changes

Do not update just because:

- code changed internally but the operational path stayed the same
- a test changed without changing the run procedure

### Current-state docs

Update when:

- implementation truth changes
- PM ordering changes
- active residuals are resolved or newly discovered
- phase status changes
- a workpackage lands or is newly prepared

Do not update everything in this class automatically.

Update only the docs whose current-truth role is actually affected.

### Boundary and deferred docs

Update when:

- something previously deferred becomes stable now
- something previously treated as stable is narrowed
- a handover or productization boundary is clarified

Do not expand these docs into speculative future-roadmap prose.

## Agent Documentation Playbook

Future agents should use this decision order.

### 1. Identify the doc role before editing

Ask:

- is this stable knowledge
- is this an operational workflow
- is this current project truth
- is this a stable-now versus deferred-later boundary

Update the smallest matching doc set only.

### 2. Do not update every doc after every change

Default rule:

- update only the documents whose role was actually affected

Examples:

- a new landed workpackage:
  - usually update `docs/STATUS.md`, `docs/WORKPACKAGES.md`, and the active session workpackage file
- a changed launch command:
  - update the launch baseline and any directly linked runbook or module usage note
- a stable contract change:
  - update the stable contract doc and any affected current-state summary

### 3. Prefer additive precision over broad rewrites

When a doc needs improvement:

- add one clear section
- sharpen one boundary
- correct one stale statement

Avoid:

- rewriting large sections for style only
- moving many docs at once without a real need
- turning one local clarification into a repository-wide rewrite

### 4. Keep stable docs calm

Stable docs should not read like changelogs.

If a change only affects current truth:

- prefer `docs/STATUS.md`
- prefer `docs/WORKPACKAGES.md`
- prefer the active workpackage file

### 5. Keep operational docs executable

Operational docs should help someone run or validate the system with less rediscovery.

Prefer:

- exact commands
- clear preconditions
- known-good paths
- current residual notes only when operationally relevant

Avoid:

- large conceptual essays
- duplicate architecture prose

### 6. Keep current-state docs current

Current-state docs must reflect landed reality.

If implementation truth, PM order, phase state, or residual interpretation changes:

- update the relevant current-state doc in the same slice when practical

Priority order for avoiding drift:

1. update `docs/STATUS.md` if repository truth changed
2. update `docs/WORKPACKAGES.md` if the queue or completion state changed
3. update `docs/session_workpackages/...` only for the selected slice
4. update `docs/TARGET_MAP.md`, `docs/PRIORITIES.md`, or other compact views only if their derived summary would otherwise mislead

### 6a. Offload status history deliberately

When `docs/STATUS.md` starts accumulating too much landed chronology in its upper reading path:

- move older chronology into `docs/StatusHistory.md`
- preserve the moved wording there when practical
- keep `docs/STATUS.md` focused on current truth and the fast decision layer

Default history cadence:

1. append a history snapshot when the repository phase changes
2. append another history snapshot every 20 additional landed/completed work packages

### 7. Minor change rule

A change is usually too minor to justify doc edits when:

- it does not change user-visible behavior
- it does not change stable contracts
- it does not change validated run procedure
- it does not change current project truth in a meaningful way

In that case:

- do not force a doc edit just for symmetry

## Minimal Integration Recommendation

Introduce this model without a giant rewrite:

1. keep existing useful docs in place
2. add this playbook as the central maintenance reference
3. link it from startup and workflow docs
4. use it for future doc decisions
5. only refactor existing docs gradually when a real slice already touches them

Recommended immediate integration:

- `docs/SESSION_START.md`
- `docs/WORKFLOW.md`
- `docs/MODULE_INDEX.md`
- `docs/module_doc_audit.md`

Additional compact anchor docs now in use:

- `docs/MANUALS_INDEX.md`
- `docs/ARCHITECTURE_BASELINE.md`

This is enough to change behavior without forcing a large documentation migration.
