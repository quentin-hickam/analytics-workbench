---
name: awb-release
description: "Release an analytics workbench package: a numbered, frozen copy of its draft. Use only when the user marks a package delivered or sets where releases are kept."
---

# Release a delivery package

A release is a *frozen* copy of the existing draft. Changes to the draft go through [awb-package](../awb-package/SKILL.md), and changes to analysis go through separately authorized analytical work. A request only to record or change where releases are kept goes directly to **Record storage without releasing**.

## 1. Identify the draft

Identify the investigation and package being delivered; when the request could refer to more than one, ask which. The draft lives at `deliveries/<investigation>/<package>/draft/`. When it is absent, say so and direct the user to awb-package to create it.

## 2. Release

Run `python3 src/awb.py release <investigation> <package>`. Its gate is `check-draft --verify-only`: a pass means the draft is byte-identical to the one awb-package checked, so the draft's narratives and the contract need no rereading. It refuses, creating nothing, in two ways:

- `check-draft --verify-only does not pass`: report the `check` rows verbatim and stop; repairs are package revisions through awb-package.
- `flagged findings without a release disposition`: settle them under **3. Resolve flags**, then run `release` again.

The step is done when it exits with `released: true`; a `verify` row on the local copy is reported verbatim.

## 3. Resolve flags

`unmatched_flags` lists findings `state.md` flags that the manifest does not record with the same finding and reason; `dispositions` lists recorded places still `none` or `revalidate`. For each unmatched flag, read the draft's `methodology.md` to find every place the draft represents its conclusion: findings text, methodology text, a chart's specification in `findings.md` with its **Caveat:** and **Alt text:** lines, and a dataset or column description under **Supporting datasets**; or that it represents none. Read `foundation/quality.md` only when a flag's reason cites a correction you must explain to the user.

List each represented flag's places and ask the user to choose one outcome, as one answer for every place or one per place:

1. revalidate it through separately authorized analytical work;
2. omit it from the package; or
3. release it with the caveat explicitly accepted.

A recorded disposition applies while its finding and reason match the current `state.md` row exactly; a new or changed reason reopens it. A revalidation choice pauses the release until analytical work updates the investigation and the draft; the user then asks for the release again. For omission or an accepted caveat, revise the draft through awb-package under the package contract's **Revalidation caveats**: each place omits the conclusion or carries the caveat beside it, and the manifest records the flag with each disposition and its `disposition_recorded_at`. A flag the draft represents nowhere needs no choice; that revision records it with `represented_in: none`. Then run `release` again.

## 4. Copy to storage

`deliveries/` is excluded from Git, so a release exists only in this checkout until it is copied. The project README's storage line reads `Released packages are kept at: <location>`, and `release` copies to that location. Report its `storage` result by `status`:

- `copied` or `already copied`: the copy path, with its empty `compare_trees` rows.
- `mismatch`, `conflict`, or `copy failed`: each `compare_trees` row or `problem` verbatim.
- `unreachable`: its `instruction`, for the user to carry out.
- `none chosen`: the user's decision; warn that this checkout holds the only copy.
- `unrecorded`: ask the user where released packages are kept, record the storage line as below, then run `python3 src/awb.py copy-releases <investigation> <package>` and report its rows the same way.

To record the storage line, write the user's answer on that line, adding the line when absent after the README's `Active investigation` line and any `Landed data is kept at` line, and preserving every other line. When the user declines, record `none chosen` and warn that releases will exist only in this checkout. Record a location whenever the user names one.

## Record storage without releasing

When the user asks only to record or change where released packages are kept, record the storage line as above and create no release. Then run `python3 src/awb.py copy-releases <investigation>` once per investigation with releases, and report each release's `storage` row as in **4. Copy to storage**.

## Report

Report from the `release` output: `release` and `release_number`; `datasets`, or none; `dispositions`, separating those marked `new` (recorded since the prior release) from those carried forward; `provenance_gaps`; each `checkout_only_acquisitions` entry as an acquisition held only in this checkout; and the storage result.
