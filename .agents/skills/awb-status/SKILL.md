---
name: awb-status
description: Report where an analytics workbench stands and what to ask next. Use when the user asks for status or what to do next.
---

# Report workbench status

Stay *read-only*: report what the records say, and turn every fix into a next request.

## Collect

Use the user-named project, otherwise the current directory. Run the helper without reading it:

```sh
python3 <skill-directory>/scripts/collect_status.py <project-root>
```

When `workbench` is false, stop and suggest `awb-init`. Treat `null`, `unknown`, and each `uncertainties` entry as a targeted lookup: read only the named record or field, and inspect a custom-format manifest directly. Report missing records as missing. When `git.available` is false, report its `reason`. Leave history, source data, and other investigations' conclusions unread.

## Report

Keep the report to one screen, in this order. Report the collector's values as given, in the investigation's wording shortened, and omit empty items.

- **Question and state.** `active.question` and `active.last_updated`, then `git.state_status`; for `out of date`, add `days_after_state` and `latest_change`. Add `git.commit_comparison` when present. Modification dates use the host timezone: convert `latest_change.date` only when the user's timezone differs and the conversion moves the date.
- **Findings.** `active.counts`, then every flagged finding in `active.findings` with its `reason`. Read a `foundation/quality.md` correction row only when a reason cites one that needs explaining.
- **Open work.** `unresolved_issues` and `next_steps`. Report an open decision only when the brief or state records it as one; list `material_unknowns` as unknowns.
- **Other investigations.** Each name and `last_updated`.
- **Packages.** For each: `revised_at`, `latest_release` with `released_at`, and `draft_vs_release` (an estimate when `comparison_is_estimate` is true). Then the flagged findings that block its next release. A recorded disposition applies while its finding and reason match the current `state.md` row exactly; `confirmed_without_disposition` counts matched findings with any place still `none` or `revalidate`. For each `representation_review` entry, read `review_methodology` (it names finding identifiers) and decide whether the package represents that finding; a represented one was flagged since the draft and also lacks a disposition.
- **Storage.** `landed_data_storage` and `release_storage` by `availability`, and `acquisitions.without_retained_copy` as acquisitions held only in this checkout. `unrecorded` or `unreachable` is a risk once acquisitions or releases exist. `none chosen` is the user's recorded decision: report that this checkout holds the only copy. For `unknown`, check through the project's established access method or say "not verified".
- **Uncertainties** the targeted lookups left unresolved.

## You can ask for

Finish with up to five requests whose state applies, risk rows first, then progress. Phrase each as a sentence the user could type, with its handler in parentheses so hosts without a skill menu still route it.

| State | Request | Handler | Kind |
| --- | --- | --- | --- |
| `active.counts` has `revalidation-needed` | "Rerun the flagged findings" | `python3 investigations/<name>/run.py` | risk |
| A package represents a flagged finding that lacks a disposition | "Revise the <package> draft to carry the new caveats" | `awb-package` | risk |
| A release exists and `release_storage` is `unrecorded` or `unreachable` | "Record where releases are kept" | `awb-release` | risk |
| Acquisitions exist and `landed_data_storage` is `unrecorded` or `unreachable`, or `reachable` with acquisitions held only in this checkout | "Record where landed data is kept" | AGENTS.md record maintenance | risk |
| `git.state_status` is `out of date` | "Update the investigation state" | AGENTS.md record maintenance | risk |
| An `uncertainties` entry names a missing standard record, or the user mentions newer workbench skills | "Bring the workbench up to date" | `awb-init` | risk |
| No active investigation | "Start an investigation into <question>" | `awb-init` | progress |
| The brief or state records an open scope or purpose decision | "Resolve the <topic> scope change" | `awb-init` | progress |
| A dataset the investigation uses has no row in the quality record, or unresolved issues or next steps name data errors | "Clean the <dataset> data" | `awb-clean` | progress |
| No findings yet, or a next step calls for exploring a dataset | "Explore <dataset> for this investigation" | `awb-eda` | progress |
| Supported findings and no draft | "Prepare a draft package" | `awb-package` | progress |
| `draft_vs_release` is `ahead`, or a draft has no release | "Mark the <package> package delivered" | `awb-release` | progress |
| Next steps call for preparation beyond the active question | "Prepare <source> more broadly" | analytical work under AGENTS.md | progress |
| `other_investigations` lists any | "Checkpoint this investigation and switch to <name>" | AGENTS.md record maintenance | progress |
| `git.uncommitted_paths` is above zero | "Commit the current work" | explicit commit request | progress |
| `next_steps` lists a step and no other progress row applies | "Continue: <first next step, shortened>" | analytical work under AGENTS.md | progress |
