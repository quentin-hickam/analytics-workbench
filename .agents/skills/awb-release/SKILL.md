---
name: awb-release
description: "Release an analytics workbench package: a numbered, frozen copy of its draft. Use this skill only when the user marks a package as delivered, or sets the location where releases are kept."
---

# Release a delivery package

A release is a *frozen* copy of the existing draft. Changes to the draft go through [awb-package](../awb-package/SKILL.md). Changes to analysis go through analytical work that has a separate authorization. If a request is only to record or change where releases are kept, go directly to **Record storage without releasing**.

## 1. Identify the draft

Identify the investigation and the package to deliver. If the request can refer to more than one, ask which. The draft is at `deliveries/<investigation>/<package>/draft/`. If the draft is not there, say so and tell the user to use awb-package to create it.

If the `Released packages are kept at` line of the README is missing, blank, or `not yet recorded`, do these steps before you release:

1. Ask where releases are kept.
2. Record the location as in step 4. Then `release` copies the release there.

## 2. Release

Run `python3 src/awb.py release <investigation> <package>`. Its gate is `check-draft --verify-only`. A pass of this gate runs every mechanical check again. It also verifies every file, except the manifest, against the recorded inventory. For this reason, you do not need to read the narratives and the contract again. The command can refuse in two ways, and then it creates nothing:

- `check-draft --verify-only does not pass`: report the `check` rows verbatim and stop. Repairs are package revisions through awb-package.
- `flagged findings without a release disposition`: settle them under **3. Resolve flags**. Then run `release` again.

The step is done when the command exits with `released: true`. Report a `verify` row on the local copy verbatim.

## 3. Resolve flags

`unmatched_flags` lists the findings that `state.md` flags but that the manifest does not record with the same finding and reason. `dispositions` lists the recorded flags that are still `none` or `revalidate`. An unmatched flag needs a package revision. Send it through awb-package, which records the flag and its caveats. Then run `release` again.

For each recorded flag, list its `represented_in` places from the draft manifest. Then ask the user to choose one outcome:

1. Revalidate it through analytical work that has a separate authorization. This work pauses the release until the work updates the investigation and the draft. Then the user asks for the release again.
2. Omit it from the package. Revise the draft through awb-package so that no place represents it. Then run `release` again.
3. Release it with the caveat explicitly accepted. Write `release_with_caveat` as the `disposition` of that flag in the `manifest.json` of the draft. Then run `release` again.

Read `foundation/quality.md` only when the reason of a flag cites a correction that you must explain to the user.

## 4. Copy to storage

Report the `storage` row verbatim. If its status is `unrecorded`, do these steps:

1. Ask where released packages are kept.
2. Record the storage line as the next paragraph says.
3. Run `python3 src/awb.py copy-releases <investigation> <package>`.
4. Report its rows verbatim also.

If the status is `none chosen`, warn that this checkout holds the only copy.

The storage line is `Released packages are kept at: <location>` in the project README. To record the storage line, write the answer of the user on that line. If the line is not there, add it after the `Active investigation` line of the README and after the `Landed data is kept at` line, if that line exists. Keep every other line as it is. If the user declines, record `none chosen` and warn that releases will exist only in this checkout. Record a location each time the user names one.

## Record storage without releasing

When the user asks only to record or change where released packages are kept, record the storage line as above. Do not create a release. Then run `python3 src/awb.py copy-releases <investigation>` one time for each investigation that has releases. Report the `storage` row of each release as in **4. Copy to storage**.

## Report

Report these items from the `release` output:

- `release` and `release_number`
- `datasets`, or none
- `dispositions`. Keep the dispositions marked `new` (not in the manifest of the prior release) separate from the dispositions carried forward.
- `provenance_gaps`
- each `checkout_only_acquisitions` entry, as an acquisition held only in this checkout
- the storage result
