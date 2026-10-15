---
name: awb-status
description: "Report where an analytics workbench stands and suggest next requests. Use for \"what's left?\", \"where are we?\", \"what should we do next?\", or \"have the landed sources changed upstream?\"."
---

# Report workbench status

Stay *read-only*: report what the records say, and turn every fix into a next request.

## Collect

Use the user-named project, otherwise the current directory. Run the helper without reading it:

```sh
python3 <skill-directory>/scripts/collect_status.py <project-root>
```

Add `--probe-upstream` only when the user asks whether landed sources changed upstream. It sends HEAD requests only, one per landed file whose `provenance.json` records an HTTP URL with an ETag or Last-Modified, skipping a file when a later acquisition of the same source records the same URL (later by `completed_at`, then by acquisition ID for the same second), and none to a host and port, directly or by redirect, after one request to it times out (10 s). It follows a redirect only to an http(s) URL and changes nothing.

When `workbench` is false, stop and suggest `awb-init`. Treat `null`, `unknown`, and each `uncertainties` entry as a targeted lookup: read only the named record or field. Report missing records as missing. When `git.available` is false, report its `reason`. Leave history, source data, and other investigations' conclusions unread.

## Report

Keep the report to one screen, in this order. Summarize outcomes in plain words, preserving the collector's values and the investigation's meaning; omit empty items and keep helper keys in tool results.

- **Question and state.** `active.question` and `active.last_updated`, then `git.state_status`; for `out of date`, add `days_after_state` and `latest_change`. Add `git.commit_comparison` when present. Modification dates use the host timezone: convert `latest_change.date` only when the user's timezone differs and the conversion moves the date. When `active.question` is a ledger ID, report the ID with its `questions.open` or `questions.awaiting_recheck` entry, falling back to its line from `python3 <project-root>/src/awb.py questions list --all`. A missing ID or failed lookup leaves the question unsettled; report the uncertainty.
- **Findings.** `active.counts`, then every flagged finding in `active.findings` with its `reason`. Read a `foundation/quality.md` correction row only when a reason cites one that needs explaining.
- **Open work.** `unresolved_issues` and `next_steps`. Report an open decision only when the brief or state records it as one. From `questions`: its `counts` using the displayed statuses, each `open` question grouped by answerer, and each `awaiting_recheck` entry as `answered (awaiting recheck)`: an answered data question with at least one flagged or superseded answering finding. The stored status remains `answered`; even another settled answering finding does not remove the recheck. A null `questions` with an `uncertainties` entry for the ledger means it could not be read: report that entry. Otherwise a null `questions` means the investigation has no ledger yet; then list `material_unknowns` as unknowns.
- **Other investigations.** Each name and `last_updated`.
- **Packages.** For each: `revised_at`, `latest_release` with `released_at`, and `draft_vs_release`. Then what blocks its next release: `confirmed_without_disposition`, flags the manifest records whose disposition is still `none` or `revalidate`; `unmatched_flags`, flagged findings the manifest does not record with the same finding and reason, which awb-package resolves; and `rerun_since_draft`, represented results rerun after the draft was last revised, so the package still shows their earlier run.
- **Storage.** `landed_data_storage` and `release_storage` by `availability`, and `acquisitions.without_retained_copy` as acquisitions held only in this checkout. `unrecorded` or `unreachable` is a risk once acquisitions or releases exist. `none chosen` is the user's recorded decision: report that this checkout holds the only copy. For `unknown`, check through the project's established access method or say "not verified".
- **Sources.** `sources.documentation_without_reference`: sources assessed from documentation whose Notes record no reference in one of the two forms `foundation/sources.md` states; that file gives their exact grammar. The check reads syntax only and errs toward listing: any other spelling is listed, including Markdown that renders as a link (a title, brackets in the link text), a location without backticks, and a clause inside code, HTML, emphasis, strikethrough or brackets. A placeholder written in a valid form, such as `[none](none)`, counts, and no link, location or checksum is opened or verified.
- **Upstream**, only when probed. Each `upstream.files` entry whose `result` is `changed` as "<path>: upstream changed since acquisition <acquisition_id>", then each `unknown` with its `reason` and no lookup, then the count unchanged. Name `not_probeable` files with their reasons and the `without_upstream` count as not checked. `superseded` counts files whose URL a later acquisition records, which is the one checked; report it only when the user asks about older acquisitions. A null `probeable_files` means an acquisition could not be read: name the directories and provenance files listed under uncertainties as not checked. An ETag is the server's opaque value, so a change is only as reliable as the server.
- **Uncertainties** the targeted lookups left unresolved.

## You can ask for

Finish with up to five requests whose state applies, risk rows first, then progress. Phrase each as a sentence the user could type, with its handler in parentheses so hosts without a skill menu still route it.

| State | Request | Handler | Kind |
| --- | --- | --- | --- |
| `active.counts` has `revalidation-needed` | "Rerun the flagged findings" | `python3 investigations/<name>/run.py` | risk |
| A package's `unmatched_flags` is above zero | "Revise the <package> draft to carry the new caveats" | `awb-package` | risk |
| A package's `rerun_since_draft` lists results | "Revise the <package> draft to the rerun results" | `awb-package` | risk |
| A release exists and `release_storage` is `unrecorded` or `unreachable` | "Record where releases are kept" | `awb-release` | risk |
| Acquisitions exist and `landed_data_storage` is `unrecorded` or `unreachable`, or `reachable` with acquisitions held only in this checkout | "Record where landed data is kept" | AGENTS.md record maintenance | risk |
| `sources.documentation_without_reference` lists a source | "Keep the documentation behind the <source> assessment" | `workbench-guides/data.md` | risk |
| `git.state_status` is `out of date` | "Update the investigation state" | `python3 src/awb.py state` | risk |
| An `uncertainties` entry names a missing standard record, or the user mentions newer workbench skills | "Bring the workbench up to date" | `awb-init` | risk |
| No active investigation | "Start an investigation into <question>" | `awb-scope` | progress |
| The brief or state records an open scope or purpose decision | "Resolve the <topic> scope change" | `awb-scope` | progress |
| `questions` is null for the active investigation and no `uncertainties` entry names its ledger | "Start the question ledger for <investigation>" | `awb-scope` | progress |
| `questions.open_by_answerer` counts `user` or `stakeholder` questions | "Work through the open questions" | `awb-scope` | progress |
| `questions.open_by_answerer` counts `data` questions | "Explore <dataset> to answer <question in plain words>" | `awb-explore` | progress |
| `questions.counts` has answered questions and at most two open ones | "What else should we ask?" | `awb-brainstorm` | progress |
| A dataset the investigation uses has no row in the quality record, or unresolved issues or next steps name data errors | "Clean the <dataset> data" | `awb-clean` | progress |
| No findings yet, or a next step calls for exploring a dataset | "Explore <dataset> for this investigation" | `awb-explore` | progress |
| Supported findings and no draft | "Prepare a draft package" | `awb-package` | progress |
| `draft_vs_release` is `ahead`, or a draft has no release | "Mark the <package> package delivered" | `awb-release` | progress |
| Next steps call for preparation beyond the active question | "Prepare <source> more broadly" | analytical work under AGENTS.md | progress |
| `upstream.files` has a `changed` entry | "Land <source> again as a new acquisition" | `src/preparation/fetch_<source>.py` with a new acquisition ID | progress |
| `upstream.probeable_files` is above zero and the probe has not run | "Check whether the landed sources changed upstream" | `awb-status` | progress |
| `other_investigations` lists any | "Checkpoint this investigation and switch to <name>" | AGENTS.md record maintenance | progress |
| `git.uncommitted_paths` is above zero | "Commit the current work" | explicit commit request | progress |
| `next_steps` lists a step and no progress row other than the upstream check applies | "Continue: <first next step, shortened>" | analytical work under AGENTS.md | progress |
