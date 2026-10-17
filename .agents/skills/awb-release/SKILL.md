---
name: awb-release
description: "Preserve a numbered, frozen copy of an analytics workbench package draft. Use only when the user says \"mark this package delivered\", \"release this draft\", or \"record where releases are kept\"."
---

# Release a delivery package

A release is a *frozen* copy of the existing draft. Changes to the draft go through [awb-package](../awb-package/SKILL.md), and changes to analysis go through separately authorized analytical work. A request only to record or change where releases are kept goes directly to **Record storage without releasing**.

## 1. Identify the draft

Identify the investigation and package being delivered; when the request could refer to more than one investigation or package, ask which. The draft lives at `deliveries/<investigation>/<package>/draft/`. When it is absent, say so and direct the user to awb-package to create it.

When README's `Released packages are kept at` line is missing, blank, or `not yet recorded`, ask where releases are kept and record it as in step 5 before releasing, so `release` copies it.

## 2. Review

Read `review-receipt` through the `read` tool, or run `python3 src/awb.py review-receipt show <investigation> <package>`. A matching receipt, `current`, needs no review. When it is `stale` or `failed`, run the scoped read-only review in [awb-package's references/review.md](../awb-package/references/review.md) against it, or the full one when it is `none`, then record it and settle its report as that file's **After the review** says, releasing only once a review is passed. Its **Launch** runs `review-receipt start` right before the reviewer starts, and `record` refuses a report once the draft changed after that. A repair it needs is a package revision through awb-package; after it, show the user the changed slides and wait for their yes before running `release`, unless they said to release without seeing it. Recording `release_with_caveat` under **4. Resolve flags** leaves the review current.

## 3. Release

First run `python3 src/awb.py check-draft <investigation> <package> --verify-only`, which writes nothing. A release copies the draft byte for byte, so when `draft_markers` lists wording such as DRAFT or working copy in the deck's title, subtitle, headings, or title notes, show each row and ask the user to confirm it or revise it through awb-package, and release only once they confirm.

`helper_drift` lists each helper or package format that changed, or went missing, since the installer recorded it; these files decide whether a release passes. For each row whose `confirmed` is false, name its file and what it does in plain words, and ask the user whether to release with that change. On their yes, add `{file, sha256, reason}` to the draft manifest's `helper_drift_confirmed`, `file` and `sha256` copied from the row and their reason in `reason`. Otherwise put the file back, then run `check-draft --verify-only` again: a `src/` helper, or a `changed` package format, through awb-init repair, which asks whether to replace each customized file; a `missing` package format with the installer command in awb-package's **1. Establish**, which reinstalls it; `.awb-receipt.json` from Git.

Then run `python3 src/awb.py release <investigation> <package>`. Its gate is `check-draft --verify-only`: a pass reruns every mechanical check and verifies every file but the manifest against the recorded inventory, so the contract needs no rereading and only the review reads the narratives. It refuses, creating nothing, in four ways:

- `helpers or package formats differ from the install receipt without the user's confirmation`: ask about its `helper_drift` rows as above, then run `release` again.
- `check-draft --verify-only does not pass`: report the `check` rows verbatim and stop; repairs are package revisions through awb-package. A `claims` row also follows a claim strength or causal design basis changed in `state.md` since packaging: the released methodology must state each finding's current Claim.
- `flagged findings without a release disposition`: settle them under **4. Resolve flags**, then run `release` again.
- `no passed review of this draft`: review it as **2. Review** says, then run `release` again.

The step is done when it exits with `released: true`; report whether the local copy verified.

## 4. Resolve flags

`unmatched_flags` lists findings `state.md` flags that the manifest does not record with the same finding and reason; `dispositions` lists recorded flags still `none` or `revalidate`. An unmatched flag needs a package revision: send it through awb-package, which records it and its caveats, then run `release` again.

For each recorded flag, list its `represented_in` places from the draft manifest and ask the user to choose one outcome:

1. revalidate it through separately authorized analytical work, which pauses the release until that work updates the investigation and the draft; the user then asks for the release again;
2. omit it from the package: revise the draft through awb-package so no place represents it, then run `release` again; or
3. release it with the caveat explicitly accepted: write `release_with_caveat` as that flag's `disposition` in the draft's `manifest.json` and run `release` again.

Read `foundation/quality.md` only when a flag's reason cites a correction you must explain to the user.

## 5. Copy to storage

Report the `storage` row: where the release was copied and whether the copy verified; for `unreachable`, tell the user in plain words what to copy and where, from its `instruction` (`<location>/<investigation>/<package>/<n>/`). When its status is `unrecorded`, ask where released packages are kept, record the storage line as below, run `python3 src/awb.py copy-releases <investigation> <package>`, and report its rows the same way; when `none chosen`, warn that this checkout holds the only copy.

To record the storage line, `Released packages are kept at: <location>` in the project README, write the user's answer on that line, adding the line when absent after the README's `Active investigation` line and any `Landed data is kept at` line, and preserving every other line. When the user declines, record `none chosen` and warn that releases will exist only in this checkout. Record a location whenever the user names one.

## Record storage without releasing

When the user asks only to record or change where released packages are kept, record the storage line as above and create no release. Then run `python3 src/awb.py copy-releases <investigation>` once per investigation with releases, and report each release's `storage` row as in **5. Copy to storage**, copy instruction included.

## Report

Report the review's outcome and each problem its `review` lists as accepted, then from the `release` output: `release` and `release_number`; `datasets`, or none; `dispositions`, separating those marked `new` (absent from the prior release's manifest) from those carried forward; each `provenance_gaps` entry as what went unrecorded, from its `field` and `reason`, such as "the Python version for one result was not recorded" for an unknown runtime or "one result's package versions were not recorded" for a requirements line it could not read, or not at all when it changes nothing the user decides, such as an unrecorded packaging commit in a project without Git; each `checkout_only_acquisitions` entry as an acquisition held only in this checkout; and the storage result as in **5. Copy to storage**, copy instruction included.

List every `open_caveats` entry, those carried forward included: the headline and bullets of the deck's **Limitations and open caveats** and **Open questions** slides, then each flag released with its caveat. While one remains, never call the release clean or say nothing is outstanding.
