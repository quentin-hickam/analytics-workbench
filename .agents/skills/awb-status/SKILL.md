---
name: awb-status
description: Report where an analytics workbench stands (active investigation, findings by status, revalidation flags, open issues, package and release state, landed data and release storage) and the requests that fit right now. Use when the user asks where things stand, what is active or flagged, or what they can do next. Read-only; it changes nothing.
---

# Report workbench status

Give the analyst a read-only snapshot of the project and a short menu of what they can ask for next. Many workbench capabilities run only on an explicit request, and this report is where the analyst learns which of those requests apply now.

This skill is an observer. Read files and run `git rev-parse`, `git status`, and `git log`; change no file, run no analysis, refresh no cache, query no source, and make no commit. When the report reveals something to fix, name it under **You can ask for** and leave the fix to the user's next request.

## Confirm the workbench

Use the project root the user names, otherwise the current directory. It is a workbench when its `README.md` has an `Active investigation` line or the root holds `foundation/` or `investigations/`. Otherwise say so, stop, and suggest `awb-init` to create one there.

## Read the minimum

Read only these, in the project root:

- `README.md`: the `Active investigation` line and any `Landed data is kept at:` and `Released packages are kept at:` lines.
- The active investigation's `state.md` (its `Last updated` date, findings table, unresolved issues, next steps) and `brief.md` (business question and material unknowns). Skip `history.md`.
- The other directories under `investigations/`: each name and its `state.md` `Last updated` date. Leave their findings and conclusions unread; the project instructions forbid reading another investigation's conclusions unprompted.
- `foundation/quality.md` correction rows, only to explain a revalidation flag whose state-file reason points to a correction.
- For each package under `deliveries/<active-investigation>/`: whether `draft/` exists, its manifest's `revised_at` and `revalidation_flags` with dispositions, and the highest numeric `released/NNN` with that manifest's `released_at`. Read the draft `journal.md` only to tell whether it represents a finding `state.md` flags that the manifest does not list with its current reason.
- The Acquisitions table in `foundation/sources.md`: how many acquisitions are recorded and how many have a blank retained copy or `this checkout only`.
- `git rev-parse --verify -q HEAD`, then `git log -1 --format=%cs -- investigations/<slug>/ ':!investigations/<slug>/state.md'` and `git status --short`, for staleness and uncommitted work. When `HEAD` does not resolve, the repository has no commits: skip `git log`.

A record that does not exist is a fact to report, such as "no packages yet", not a gap to fill.

## Assess

- **Flagged findings**: a finding is flagged when its status begins with `revalidation-needed`, as in `revalidation-needed (was supported)`. Count it under needs revalidation, not under its prior status.
- **Staleness**: state is stale when a commit, or an uncommitted change by its file modification date, in the investigation directory is newer than `state.md`'s `Last updated` date. Say which is newer and by how much. With no commits, report "no commits yet; all work uncommitted" in place of the commit comparison. When the newest commit or uncommitted change falls on the `Last updated` date itself, say staleness cannot be determined at date precision.
- **Draft ahead of release**: compare the draft manifest's `revised_at` with the latest release manifest's `released_at`. Only when a manifest lacks the field, compare file modification times and label the result an estimate.
- **Flags the release will ask about**: count the flagged findings in `state.md` that the draft represents and that lack an applicable disposition: the manifest's `revalidation_flags` has no entry for the finding with its current reason, or the entry has a place with disposition `none`. A flagged finding with no entry at its current reason was flagged since the draft was revised. Report both counts on the package line.
- **Open decisions**: a decision is open only when the brief or state says one is needed. A recorded material unknown is not an open decision by itself.
- **Landed data storage risk**: an acquisition is recorded and the README records no location or `none chosen`, the recorded location is not reachable from here, or any acquisition's retained copy is blank or `this checkout only`.
- **Release storage risk**: a release exists and the README records no storage location, or the recorded location is not reachable from here.

## Report

Keep the report to one screen. Use the investigation's own wording for findings, shortened; give every revalidation-needed finding its reason. Omit a section that has nothing to say. Follow this shape:

```text
Active: churn-q3: Why did Q3 enterprise churn rise? (state updated 2026-10-02; 3 commits since, stale)
Findings: 2 supported, 1 provisional, 1 superseded, 1 needs revalidation
  - Revalidate: "Renewal lag drives churn": account-merge correction Q-004 changed the account count
Open issues: contract-end dates missing for 6% of accounts; scope of reseller accounts undecided
Next steps: profile reseller accounts; compare lag by region
Other investigations: pricing-test (updated 2026-07-02)
Package churn-review: draft revised 2026-09-30, newer than release 002 (2026-09-12); 1 flagged finding without disposition, flagged since the draft was revised
Landed data storage: /Volumes/analytics/workbench (risk: 1 of 4 acquisitions exists only in this checkout)
Release storage: /Volumes/analytics/releases

You can ask for:
  - "Rerun the flagged findings" (analytical work under AGENTS.md)
  - "Revise the churn-review draft to carry the new caveats" (awb-package)
  - "Record where landed data is kept" (AGENTS.md record maintenance)
  - "Update the investigation state" (AGENTS.md record maintenance)
  - "Resolve the reseller scope change" (awb-init)
```

## You can ask for

End with the handful of requests the current state makes relevant, each phrased as a sentence the user could type, with its handler in parentheses so hosts without a skill menu still route it. Choose from this map and offer nothing else:

| State | Request | Handler | Kind |
| --- | --- | --- | --- |
| No active investigation | "Start an investigation into <question>" | `awb-init` | progress |
| A consequential scope or purpose decision is open in the brief or state | "Resolve the <topic> scope change" | `awb-init` | progress |
| Findings flagged for revalidation | "Rerun the flagged findings" | analytical work under AGENTS.md | risk |
| A draft or release represents a finding flagged since the draft was revised | "Revise the <package> draft to carry the new caveats" | `awb-package` | risk |
| Supported findings and no draft | "Prepare a draft package" | `awb-package` | progress |
| Draft ahead of the latest release, or never released | "Mark the <package> package delivered" | `awb-release` | progress |
| A release exists and storage is unrecorded or unreachable | "Record where releases are kept" | `awb-release` | risk |
| An acquisition is recorded and landed data storage is unrecorded, `none chosen`, or unreachable, or an acquisition has no retained copy | "Record where landed data is kept" | AGENTS.md record maintenance | risk |
| Next steps call for preparation beyond the active question | "Prepare <source> more broadly" | analytical work under AGENTS.md | progress |
| Other investigations exist | "Checkpoint this investigation and switch to <name>" | AGENTS.md record maintenance | progress |
| Uncommitted analytical code or records | "Commit the current work" | explicit commit request | progress |
| State is stale | "Update the investigation state" | AGENTS.md record maintenance | risk |
| `state.md` lists next steps and no other progress row applies | "Continue: <first next step, shortened>" | analytical work under AGENTS.md | progress |

Limit the list to the four or five requests that matter most, ordered by risk first (revalidation, storage, staleness), then progress.
