# WP56 CLI Help And Command Documentation

## Purpose

This work package keeps CLI help/documentation polish queued behind the current architecture-first work.

Closure lane:

- Post-Closure Python Baseline / operational readiness

Slice role:

- help and documentation polish

Scope level:

- argparse help text and generated command reference only

## Branch

- intended branch: `docs/cli-help-and-command-documentation`
- activation state: landed

## Scope

Included:

- refine current CLI help strings
- add one compact human-readable command reference to the command manual
- keep documentation aligned with the existing host-neutral command surface

Excluded:

- broad command-surface redesign
- new transport/API runtime
- preview/UI architecture work

## Result

- `src/vision_platform/apps/camera_cli/camera_cli.py` now has clearer top-level and subcommand help text
- `docs/COMMANDS.md` now includes a concise camera CLI quick reference
- the bounded current CLI surface remains unchanged; this slice only improves discoverability

## Activation Condition

Activate after the current architecture chain, or earlier only if a concrete usability defect in CLI discoverability blocks real use.
