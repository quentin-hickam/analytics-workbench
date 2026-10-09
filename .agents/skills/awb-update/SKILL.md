---
name: awb-update
description: Update an existing analytics workbench to the installed awb-* skills - refresh copied package formats, project helpers, and project guides, retire files the skills no longer ship, and apply instruction migrations. Use when the user asks to update or upgrade a workbench or its package format, or after installing a newer skills release.
---

# Update a workbench

Bring a project made with earlier `awb-*` skills in line with the installed ones. An update replaces only what the skills shipped and the project left unchanged; customized files, investigation records, data, and deliveries change only as stated below. It never commits.

## Plan

Run the bundled helper from the project root the user names, otherwise the current directory, using this skill's actual directory to resolve its path:

```sh
python3 <skill-directory>/scripts/plan_update.py <project-root>
```

It is read-only without flags and emits compact JSON; execute it without reading its implementation. `workbench: false` means stop and suggest `awb-init`. It compares every file the skills copy verbatim into projects (shared package formats, project helpers under `src/`, and `workbench-guides/`) with the installed asset and with every version the skills have shipped:

- `current`: already matches; nothing to do.
- `earlier`: an unmodified copy of an earlier version; safe to replace.
- `customized`: matches no shipped version; the project changed it.
- `absent`: not installed; the owning skill installs it on first use. Leave it absent.

Under `retired`, it lists files the skills no longer ship that the project still holds, `unmodified` or `customized`. Under `old_format_drafts`, it lists package drafts in an earlier format, with reasons.

## Apply

1. Replace every `earlier` file: rerun the helper with `--apply`. The user's update request authorizes this; the replaced content was shipped, never written by the project.
2. For each `customized` file, show the user the difference against the installed asset (`git diff --no-index <project file> <asset>`, with `asset` from the plan) and ask, one file at a time, whether to replace it, keep it, or merge the update by hand. Replace the chosen ones in one call with `--replace <path> ...`; make a hand merge with ordinary edits, keeping the project's changes.
3. For `retired` files, ask once whether to remove the `unmodified` ones, then run `--remove-retired`. Report `customized` retired files and leave them; they are the project's code now.
4. Apply every migration below whose condition holds. These touch files the skills adapt rather than copy, so make the stated edit only and preserve everything else.

Combine flags in one call when the user's answers allow, and report the helper's final JSON rather than re-running it to confirm.

## Migrations

Newest first. Each applies when its condition holds, whatever the project's starting version.

### Charts move to the M365 handoff; the deck replaces Word and Excel

- **`AGENTS.md` names `awb-visualize`:** delete the line or bullet that routes charts, figures, diagrams, or results tables to `awb-visualize`, and remove any clause placing figure style or figure builders in `src/presentation/`.
- **`README.md` names `src/presentation/` or `awb-visualize`:** delete the line describing `src/presentation/` under **Where work belongs** and the `awb-visualize` request under **Asking for things**. Add `- \`awb-update\` brings the workbench up to date after installing newer skills: "Use awb-update to update this workbench."` under **Asking for things** when no `awb-update` line exists.
- **A customized `workbench-guides/analysis.md` places figure style in `src/presentation/`:** remove that clause.
- **`old_format_drafts` is not empty:** change nothing. Tell the user the next revision through `awb-package` rewrites each listed draft as a deck outline with chart files; numbered releases stay as delivered.

Investigation records, evidence files, and figures already saved under `investigations/` stay as they are: they are the record of past results, and `compare_evidence` reads evidence in both the earlier and current formats.

## Report

List what was replaced, kept, merged, or removed, each migration applied, the drafts awaiting a revision in the new format, and any file left for the user to decide. Suggest committing the update as one commit so it can be reviewed and reverted as a unit.
