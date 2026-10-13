---
name: awb-status
description: Report the status of an analytics workbench and what to ask next. Use this skill when the user asks for the status or for what to do next.
---

# Report workbench status

Stay *read-only*: report what the records say. Turn every fix into a next request.

## Collect

Use the project that the user names. If the user names no project, use the current directory. Run the helper, but do not read it:

```sh
python3 <skill-directory>/scripts/collect_status.py <project-root>
```

If `workbench` is false, stop and suggest `awb-init`. Treat `null`, `unknown`, and each `uncertainties` entry as a targeted lookup: read only the named record or field. Report missing records as missing. If `git.available` is false, report its `reason`. Do not read the history, the source data, or the conclusions of other investigations.

## Report

Keep the report to one screen, in this order. Report the values of the collector as given. Use the words of the investigation in a shorter form. Do not include empty items.

- **Question and state.** `active.question` and `active.last_updated`, then `git.state_status`. For `out of date`, add `days_after_state` and `latest_change`. If `git.commit_comparison` is present, add it. Modification dates use the timezone of the host. Convert `latest_change.date` only when the timezone of the user is different and the conversion changes the date.
- **Findings.** `active.counts`, then every flagged finding in `active.findings` with its `reason`. Read a correction row in `foundation/quality.md` only when a reason cites a correction that needs an explanation.
- **Open work.** `unresolved_issues` and `next_steps`. Report an open decision only when the brief or the state records it as an open decision. List `material_unknowns` as unknowns.
- **Other investigations.** Each name and `last_updated`.
- **Packages.** For each package: `revised_at`, `latest_release` with `released_at`, and `draft_vs_release`. Then the items that block its next release:
  - `confirmed_without_disposition`: flags that the manifest records, whose disposition is still `none` or `revalidate`
  - `unmatched_flags`: flagged findings that the manifest does not record with the same finding and reason (awb-package resolves these)
  - `rerun_since_draft`: represented results that were rerun after the last revision of the draft. As a result, the package still shows their earlier run.
- **Storage.** `landed_data_storage` and `release_storage` by `availability`, and `acquisitions.without_retained_copy` as acquisitions held only in this checkout. When acquisitions or releases exist, `unrecorded` or `unreachable` is a risk. `none chosen` is the recorded decision of the user: report that this checkout holds the only copy. For `unknown`, check through the established access method of the project, or say "not verified".
- **Uncertainties** that the targeted lookups did not resolve.

## You can ask for

Finish with up to five requests whose state applies. Put the risk rows first, then the progress rows. Write each request as a sentence that the user can type. Put its handler in parentheses, so that hosts without a skill menu can still route it.

| State | Request | Handler | Kind |
| --- | --- | --- | --- |
| `active.counts` has `revalidation-needed` | "Rerun the flagged findings" | `python3 investigations/<name>/run.py` | risk |
| The `unmatched_flags` of a package is more than zero | "Revise the <package> draft to carry the new caveats" | `awb-package` | risk |
| The `rerun_since_draft` of a package lists results | "Revise the <package> draft to the rerun results" | `awb-package` | risk |
| A release exists and `release_storage` is `unrecorded` or `unreachable` | "Record where releases are kept" | `awb-release` | risk |
| Acquisitions exist and `landed_data_storage` is `unrecorded` or `unreachable`, or `reachable` with acquisitions held only in this checkout | "Record where landed data is kept" | AGENTS.md record maintenance | risk |
| `git.state_status` is `out of date` | "Update the investigation state" | `python3 src/awb.py state` | risk |
| An `uncertainties` entry names a missing standard record, or the user mentions newer workbench skills | "Bring the workbench up to date" | `awb-init` | risk |
| There is no active investigation | "Start an investigation into <question>" | `awb-init` | progress |
| The brief or state records an open scope or purpose decision | "Resolve the <topic> scope change" | `awb-init` | progress |
| A dataset that the investigation uses has no row in the quality record, or unresolved issues or next steps name data errors | "Clean the <dataset> data" | `awb-clean` | progress |
| There are no findings yet, or a next step calls for the exploration of a dataset | "Explore <dataset> for this investigation" | `awb-eda` | progress |
| There are supported findings and no draft | "Prepare a draft package" | `awb-package` | progress |
| `draft_vs_release` is `ahead`, or a draft has no release | "Mark the <package> package delivered" | `awb-release` | progress |
| Next steps call for preparation beyond the active question | "Prepare <source> more broadly" | analytical work under AGENTS.md | progress |
| `other_investigations` lists one or more investigations | "Checkpoint this investigation and switch to <name>" | AGENTS.md record maintenance | progress |
| `git.uncommitted_paths` is more than zero | "Commit the current work" | explicit commit request | progress |
| `next_steps` lists a step and no other progress row applies | "Continue: <first next step, shortened>" | analytical work under AGENTS.md | progress |
