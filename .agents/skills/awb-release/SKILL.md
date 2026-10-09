---
name: awb-release
description: "Release an analytics workbench package: a numbered, frozen copy of its draft. Use only when the user marks a package delivered or sets where releases are kept."
---

# Release a delivery package

A release is a *frozen* copy of the existing draft. Changes to the draft go through [awb-package](../awb-package/SKILL.md), and changes to analysis go through separately authorized analytical work. A request only to record or change where releases are kept goes directly to **Record storage without releasing**.

## 1. Identify the draft

Identify the investigation and package being delivered; when the request could refer to more than one, ask which. The draft lives at `deliveries/<investigation>/<package>/draft/`. When it is absent, say so and direct the user to awb-package to create it.

## 2. Release

Run `python3 src/awb.py release <investigation> <package>`. Its gate is `check-draft --verify-only`: a pass reruns every mechanical check and verifies every file but the manifest against the recorded inventory, so the narratives and the contract need no rereading. It refuses, creating nothing, in two ways:

- `check-draft --verify-only does not pass`: report the `check` rows verbatim and stop; repairs are package revisions through awb-package.
- `flagged findings without a release disposition`: settle them under **3. Resolve flags**, then run `release` again.

The step is done when it exits with `released: true`; a `verify` row on the local copy is reported verbatim.

## 3. Resolve flags

`unmatched_flags` lists findings `state.md` flags that the manifest does not record with the same finding and reason; `dispositions` lists recorded flags still `none` or `revalidate`. An unmatched flag needs a package revision: send it through awb-package, which records it and its caveats, then run `release` again.

For each recorded flag, list its `represented_in` places from the draft manifest and ask the user to choose one outcome:

1. revalidate it through separately authorized analytical work, which pauses the release until that work updates the investigation and the draft; the user then asks for the release again;
2. omit it from the package: revise the draft through awb-package so no place represents it, then run `release` again; or
3. release it with the caveat explicitly accepted: write `release_with_caveat` as that flag's `disposition` in the draft's `manifest.json` and run `release` again.

Read `foundation/quality.md` only when a flag's reason cites a correction you must explain to the user.

## 4. Copy to storage

Report the `storage` row verbatim. When its status is `unrecorded`, ask where released packages are kept, record the storage line as below, run `python3 src/awb.py copy-releases <investigation> <package>`, and report its rows the same way; when `none chosen`, warn that this checkout holds the only copy.

To record the storage line, `Released packages are kept at: <location>` in the project README, write the user's answer on that line, adding the line when absent after the README's `Active investigation` line and any `Landed data is kept at` line, and preserving every other line. When the user declines, record `none chosen` and warn that releases will exist only in this checkout. Record a location whenever the user names one.

## Record storage without releasing

When the user asks only to record or change where released packages are kept, record the storage line as above and create no release. Then run `python3 src/awb.py copy-releases <investigation>` once per investigation with releases, and report each release's `storage` row as in **4. Copy to storage**.

## Report

Report from the `release` output: `release` and `release_number`; `datasets`, or none; `dispositions`, separating those marked `new` (absent from the prior release's manifest) from those carried forward; `provenance_gaps`; each `checkout_only_acquisitions` entry as an acquisition held only in this checkout; and the storage result.
