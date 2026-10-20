---
name: awb-status
description: "Report where an analytics workbench stands and suggest next requests. Use for \"what's left?\", \"where are we?\", \"what should we do next?\", or \"have the landed sources changed upstream?\"."
---

# Report workbench status

Run this skill's commands through the `awb` MCP tools when the host offers them, as the project's `AGENTS.md` **Commands** maps them; the command lines below are the fallback.

The status report is *read-only*: report what the records say, and turn every fix it finds into a next request. Carry out the message's other requests, such as edits, through their own skills after the report.

## Collect

Use the user-named project, otherwise the current directory. Run the helper without reading it:

```sh
python3 <skill-directory>/scripts/collect_status.py <project-root>
```

Add `--probe-upstream` only when the user asks whether landed sources changed upstream.

When `workbench` is false, stop and suggest `awb-init`. Treat `null`, `unknown`, and each `uncertainties` entry as a targeted lookup: read only the named record or field. Report missing records as missing. When `git.available` is false, report its `reason` with what it means for the user: status cannot tell what is uncommitted or whether the state is out of date, and evidence records file checksums instead of a commit SHA; say whether they must act, such as by installing Git or putting the project in a repository. Leave history, source data, and other investigations' conclusions unread.

## Report

Keep the report to one screen, in this order. Report the collector's values without its keys or their question and result IDs, in the investigation's wording shortened, and omit empty items.

- **Question and state.** `active.question` and `active.last_updated`, then `git.state_status`: for `out of date`, add `latest_change`, with `days_after_state` when above zero; for any other status but `up to date` and `no newer dated change found`, run `read` command `stale` for the investigation (`python3 <project-root>/src/awb.py stale --investigation <name>`) and give the status in plain words beside how many checked results it finds current, as "saved the same day as the latest change; evidence checks show 11 of 11 current". Add `git.commit_comparison` when present. When `git.uncommitted_evidence` lists results, say in one plain line that they were run before the first commit, so their evidence names no commit until they are rerun. When `active.question` is a ledger ID, report that question's text and status from its `questions.open`, `questions.awaiting_recheck` or `questions.provisional` entry, falling back to its line from `python3 <project-root>/src/awb.py questions list --all`. A missing ID or failed lookup leaves the question unsettled; report the uncertainty.
- **Findings.** `active.counts`, then each `questions.by_question` entry, one of the user's questions, by its text with its findings by status, as "Which zones grew fastest: 2 findings, 1 supported", labelling one whose `origin` is `brainstorm`, `eda`, or `analysis` as added while brainstorming, exploring, or analysing; then `findings_without_question` as findings no question names. Then every finding's `reason`, flagged findings first; while one remains, never say nothing is open. Read a `foundation/quality.md` correction row only when a caveat cites one that needs explaining.
- **Open work.** `unresolved_issues` and `next_steps`. Report an open decision only when the brief or state records it as one. From `questions`, lead with `roots`, the questions the user asked, in the user's terms: how many are answered, `answered (awaiting recheck)` included, of those not superseded ("Your five questions: 5 of 5 answered"), and how many await recheck, are open, parked, or declined. Count `answered (provisional)` and `answered (provisional, awaiting recheck)`, an answered data question none of whose answering findings is promoted yet, as provisional, not answered, and list each `provisional` question by its text. Then `must_subquestions`, the questions under them the decision cannot be made without, the same way. Then each `open` question grouped by answerer, and each `awaiting_recheck` entry by its status: an answered data question with at least one flagged or superseded answering finding. The stored status remains `answered`; even another settled answering finding does not remove the recheck. Report `questions.counts`, the totals with every sub-question, only on request. A null `questions` with an `uncertainties` entry for the ledger means it could not be read: report that entry. Otherwise a null `questions` means the investigation has no ledger yet; then list `material_unknowns` as unknowns.
- **Other investigations.** Each name and `last_updated`.
- **Packages.** For each whose `draft_stage` is set, that stage alone, such as "headline preview written, not yet exported". For each other: `revised_at`, `latest_release` with `released_at`, `draft_vs_release`, and `latest_release_in_storage`, whether release storage holds that release: null when release storage is not a reachable path or no release exists, which the **Storage** line and `latest_release` already report; only otherwise is its null a targeted lookup. Then what blocks its next release: `confirmed_without_disposition`, flags the manifest records whose disposition is still `none` or `revalidate`; `unmatched_flags`, flagged findings the manifest does not record with the same finding and reason, which awb-package resolves; and `rerun_since_draft`, represented results rerun after the draft was last revised, so the package still shows their earlier run.
- **Storage.** `landed_data_storage` and `release_storage` by `availability`, and `acquisitions.without_retained_copy` as acquisitions held only in this checkout. `unrecorded` or `unreachable` is a risk once acquisitions or releases exist. `none chosen` is the user's recorded decision: report that this checkout holds the only copy. For `unknown`, check through the project's established access method or say "not verified".
- **Sources.** Each `sources.documentation_without_reference` entry with its `reason`: a source assessed from documentation whose Notes record no reference in a form `foundation/sources.md` states; the `awb-init` skill's `references/landing.md` (**Source references**) gives their exact grammar. Report `sources.documentation_access_notes` and `upstream.not_checkable` once each, as known limitations, not risks: documentation that was read but could not be kept, and sources whose server sends no ETag or Last-Modified, so an upstream change cannot be detected.
- **Upstream**, only when probed. Each `upstream.files` entry whose `result` is `changed` as "<path>: upstream changed since acquisition <acquisition_id>", then each `unknown` with its `reason` and no lookup, then the count unchanged. Name `not_probeable` files with their reasons and the `without_upstream` count as not checked. A null `probeable_files` means an acquisition could not be read: name the directories and provenance files listed under uncertainties as not checked.
- **Uncertainties** the targeted lookups left unresolved.

## You can ask for

Finish with up to five requests whose state applies, risk rows first, then progress. Phrase each as a sentence the user could type, with its handler in parentheses so hosts without a skill menu still route it.

| State | Request | Handler | Kind |
| --- | --- | --- | --- |
| `active.counts` has `revalidation-needed` | "Recheck the findings awaiting recheck" | `python3 investigations/<name>/run.py` | risk |
| A package's `unmatched_flags` is above zero | "Revise the <package> draft to carry the new caveats" | `awb-package` | risk |
| A package's `rerun_since_draft` lists results | "Revise the <package> draft to the rerun results" | `awb-package` | risk |
| A release exists and `release_storage` is `unrecorded` or `unreachable` | "Record where releases are kept" | `awb-release` | risk |
| A package's `latest_release_in_storage` is false | "Copy the <package> releases to storage" | `python3 src/awb.py copy-releases <investigation> <package>` | risk |
| Acquisitions exist and `landed_data_storage` is `unrecorded` or `unreachable`, or `reachable` with acquisitions held only in this checkout | "Record where landed data is kept" | AGENTS.md record maintenance | risk |
| `sources.documentation_without_reference` lists a source | "Keep the documentation behind the <source> assessment" | `workbench-guides/data.md` | risk |
| `git.state_status` is `out of date` | "Update the investigation state" | `python3 src/awb.py state` | risk |
| An `uncertainties` entry names a missing standard record, or the user mentions newer workbench skills | "Bring the workbench up to date" | `awb-init` | risk |
| No active investigation | "Start an investigation into <question>" | `awb-scope` | progress |
| The brief or state records an open scope or purpose decision | "Resolve the <topic> scope change" | `awb-scope` | progress |
| `questions` is null for the active investigation and no `uncertainties` entry names its ledger | "Start tracking open questions for <investigation>" | `awb-scope` | progress |
| `questions.open_by_answerer` counts `user` or `stakeholder` questions | "Work through the open questions" | `awb-scope` | progress |
| `questions.open_by_answerer` counts `data` questions | "Explore <dataset> to answer <question in plain words>" | `awb-explore` | progress |
| `questions.counts` has answered questions and at most two open ones | "What else should we ask?" | `awb-brainstorm` | progress |
| A dataset the investigation uses has no row in the quality record, or unresolved issues or next steps name data errors | "Clean the <dataset> data" | `awb-clean` | progress |
| No findings yet, or a next step calls for exploring a dataset | "Explore <dataset> for this investigation" | `awb-explore` | progress |
| Provisional findings and no draft | "Preview the slide headlines" | `awb-package` | progress |
| Supported findings and no draft | "Prepare a draft package" | `awb-package` | progress |
| `draft_vs_release` is `ahead`, or a draft has no release | "Mark the <package> package delivered" | `awb-release` | progress |
| Next steps call for preparation beyond the active question | "Prepare <source> more broadly" | analytical work under AGENTS.md | progress |
| `upstream.files` has a `changed` entry | "Land <source> again as a new acquisition" | `src/preparation/fetch_<source>.py` with a new acquisition ID | progress |
| `upstream.probeable_files` is above zero and the probe has not run | "Check whether the landed sources changed upstream" | `awb-status` | progress |
| `other_investigations` lists any | "Checkpoint this investigation and switch to <name>" | AGENTS.md record maintenance | progress |
| `git.uncommitted_paths` is above zero, unless you already suggested a commit this session | "Commit the current work" | explicit commit request | progress |
| `git.uncommitted_evidence` lists results | "Rerun <results> so their evidence records the commit" | `python3 investigations/<name>/run.py <result-id> ...` | progress |
| `next_steps` lists a step and no progress row other than the upstream check applies | "Continue: <first next step, shortened>" | analytical work under AGENTS.md | progress |
