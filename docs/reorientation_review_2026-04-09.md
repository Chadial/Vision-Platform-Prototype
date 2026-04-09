# Reorientation Review Report

Date: 2026-04-09
Branch: `docs/hybrid-companion-direction`

## Scope

This review checked the repository against the confirmed reorientation toward:

- a host-steerable running `Vision App / wxShell`
- `Hybrid Companion` product form
- current phase `Usable Camera Subsystem / Pre-Product Baseline`
- three confirmed functional workflows:
  - `Delamination Recording`
  - `Geometry Capture`
  - `Setup / Focus / ROI Adjustment`

The review focused on PM, orientation, bootstrap, and adjacent repo-guidance docs.
It did not review runtime code behavior.

## Overall Verdict

The central PM surfaces are now largely aligned with the confirmed direction.

Aligned central surfaces:

- `docs/STATUS.md`
- `docs/WORKPACKAGES.md`
- `docs/TARGET_MAP.md`
- `docs/GlobalRoadmap.md`
- `docs/PRIORITIES.md`
- `docs/HOST_CONTRACT_BASELINE.md`
- `docs/SESSION_START.md`

However, the repo is not yet fully reoriented end to end.
There are still several non-archived documents that either:

- present the old `post-closure` framing as the active reading
- describe the current goal too generically
- retain the older `local usability + host usability + reference scenarios` phrasing
- or act like shadow state surfaces despite the single-source rule

## Findings

### High: Root README still presents the old product reading

Files:

- `README.md:16`
- `README.md:25`
- `README.md:46`

Evidence:

- `README.md:16` says the repository is not intended to be a finished end-user product yet and describes it mainly as a technical baseline.
- `README.md:25` says the current goal is not to build a full UI.
- `README.md:46` still describes the repo as a `post-closure Python working baseline`.

Why this matters:

- The root README is still one of the first orientation surfaces for humans.
- It underplays the confirmed first product goal: a running host-steerable `Vision App / wxShell`.
- It can mislead future work away from the intended `Hybrid Companion` shell-plus-host balance.

Recommended action:

- Rewrite the top-level repo summary so it matches the current first product goal, current product form, and current workflow framing.

### High: `docs/StatusReport.md` is stale and behaves like a shadow status surface

Files:

- `docs/StatusReport.md:5`
- `docs/StatusReport.md:24`
- `docs/StatusReport.md:38`

Evidence:

- The file has visible encoding breakage (`hA lt`, `anschlieA ender`, etc.).
- `docs/StatusReport.md:24` still says the project should be read as `geschlossene Extended-MVP-Phase mit anschliessender stabiler Post-Closure-Python-Baseline`.
- `docs/StatusReport.md:38` still defines the phase through `Hardening`, `Operational Readiness`, `Selective Expansion`, and `Later Product / Handover Preparation`.

Why this matters:

- The filename strongly suggests current truth, even though `docs/STATUS.md` is supposed to be authoritative.
- The content is stale relative to the confirmed `Hybrid Companion` direction.
- The encoding defect further reduces trust and makes the doc look abandoned.

Recommended action:

- Either retire this file, or explicitly demote/rewrite it so it no longer competes with `docs/STATUS.md`.

### Medium: Operational agent docs still derive `post-closure` slices

Files:

- `docs/NEXT_SESSION_ORDER.md:52`
- `docs/WORKFLOW.md:59`

Evidence:

- `docs/NEXT_SESSION_ORDER.md:52` still says to derive the next smallest justified `post-closure` slice.
- `docs/WORKFLOW.md:59` uses the same derivation rule.

Why this matters:

- These are operational steering docs.
- They still point agents toward the older phase vocabulary instead of the current `Usable Camera Subsystem / Pre-Product Baseline` and `Hybrid Companion` selection lens.
- The mismatch is small, but it directly affects future work derivation language.

Recommended action:

- Replace `post-closure slice` wording with `Hybrid Companion residual`, `usable-subsystem slice`, or equivalent current-phase wording.

### Medium: `docs/current_state.md` remains a stale state summary outside the single-source model

Files:

- `docs/current_state.md:15`
- `docs/current_state.md:20`

Evidence:

- `docs/current_state.md:15` still says the repo operates from a `post-closure Python working baseline`.
- The file summarizes current repo state without the current product direction, workflows, host/shell role split, or usable definition.

Why this matters:

- It is another state-like surface beside `docs/STATUS.md`.
- It is easy to open accidentally because the name sounds authoritative.
- It does not reflect the now-confirmed direction.

Recommended action:

- Either retire it, or reduce it to a clearly secondary pointer with no independent repo-state summary.

### Medium: Supporting long-range docs still use the older current-focus phrasing

Files:

- `docs/ProjectDescription.md:18`
- `docs/ProjectDescription.md:682`
- `docs/ProjectAgents.md:9`

Evidence:

- `docs/ProjectDescription.md:18-23` is partially aligned, but the closing summary at `docs/ProjectDescription.md:684-686` still says `jetzt: lokale Nutzbarkeit, Host-Nutzbarkeit und kleine offizielle Referenzszenarien`.
- `docs/ProjectAgents.md:11-15` still describes the current focus through `praktische lokale Nutzbarkeit`, `praktische Host-Nutzbarkeit`, and `kleine offizielle Referenzszenarien`.

Why this matters:

- These docs are no longer primary planning sources, but they are still referenced from central planning sources and the root README.
- Their current-focus wording predates the more explicit functional-workflow and `Hybrid Companion` framing.

Recommended action:

- Update the current-focus sections so they point to:
  - host-steerable `Vision App / wxShell`
  - `Hybrid Companion`
  - the three confirmed functional workflows
  - headless as the next structural step, not the current implementation lane

## Non-Findings

The following are acceptable as-is for now:

- archived session work packages that still use older `reference scenario` wording
- historical `Extended MVP` closure material when it is clearly labeled as historical context
- operational docs that still use `post-closure` as historical shorthand but do not directly steer current work selection

## Recommended Next Actions

1. Align `README.md` with the confirmed first product goal and current phase summary.
2. Retire, replace, or sharply demote `docs/StatusReport.md`.
3. Update `docs/WORKFLOW.md` and `docs/NEXT_SESSION_ORDER.md` so broad-task derivation uses the current phase lens.
4. Retire or shrink `docs/current_state.md` to avoid state-surface duplication.
5. Align the current-focus sections in `docs/ProjectDescription.md` and `docs/ProjectAgents.md`.

## Review Method

- Checked current branch and worktree state.
- Reviewed the already patched central PM/orientation docs.
- Searched non-archived repo docs for stale current-phase wording and conflicting orientation signals.
- Compared remaining wording against the confirmed reorientation target.

## Validation Note

This was a documentation review only.
No runtime tests were executed.
