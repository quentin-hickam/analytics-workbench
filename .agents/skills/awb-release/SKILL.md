---
name: awb-release
description: Preserve a numbered release of an analytics workbench delivery package's working draft, or record where released packages are kept and copy existing releases there. Use only when the user explicitly marks the package delivered, requests an equivalent delivery milestone, or asks to record or change the release storage location; drafting and revision never trigger it.
---

# Release a delivery package

Preserve one numbered release of an existing working draft at an explicit delivery milestone. A release is a frozen copy of the draft; it never drafts, revises, or reruns analysis. Draft layout, shared `package-format/` files, the manifest field list, and draft consistency rules belong to [awb-package](../awb-package/SKILL.md); apply them from there.

Resolve every repository path from the project root.

## Identify the draft

Identify the investigation and package being delivered. If the request could refer to more than one, ask which before reading or writing package files.

The draft lives at `deliveries/<investigation>/<package>/draft/`. If it does not exist, say so and direct the user to [awb-package](../awb-package/SKILL.md) to create it; a release never creates a draft.

## Record where releases are kept

`deliveries/` is excluded from Git, so a release exists only on this disk until it is copied elsewhere. The project README records the storage location on a line reading `Released packages are kept at: <location>`.

When that line is absent or reads `not yet recorded`, ask the user where released packages are kept before creating the release. Record the answer on that line, adding the line when absent after the README's `Active investigation` line and any `Landed data is kept at` line, and preserving every other line. If the user declines, record `none chosen` and warn plainly that the release will exist only in this checkout. A recorded `none chosen` is a decision: repeat the warning at each release and record a location whenever the user names one.

## Verify the draft

Check the draft against the structural consistency rules in **Assemble the draft** of [awb-package](../awb-package/SKILL.md): `findings.md` is self-contained for its audience and `check` from `src/packaging/findings.py`, run on it, returns no results; `methodology.md` is self-contained as the account of the analysis; the two agree in claims, numbers, qualifications, and caveats, and every `###` finding heading in `findings.md` has a section with the same heading text in `methodology.md`; the selected exports are present; and `verify` from `src/packaging/manifest.py`, run on the draft with the manifest's recorded `inventory`, returns no discrepancies. If `src/packaging/findings.py` is missing, copy [awb_findings.py](../awb-package/assets/awb_findings.py) there first; if `src/packaging/manifest.py` is missing, copy [awb_manifest.py](../awb-package/assets/awb_manifest.py) there first. Report each result `check` returns and each discrepancy `verify` returns as the helper returns it; a check or comparison made by hand does not substitute for the helper. Defer the caveat rule for findings awaiting revalidation to the re-verification in **Resolve revalidation flags**: a draft can predate a flag, and that gap is settled by a disposition, not reported here. When a structural rule fails, list each discrepancy and stop; repairs are package revisions made through awb-package, never reconstructed here.

## Resolve revalidation flags

Run this step after the structural verification passes. The draft can predate the current flags: a shared-data correction may flag findings in the investigation records after drafting, and record maintenance leaves the draft unchanged. Read the investigation's current `state.md` findings and revalidation flags, and the `foundation/quality.md` entries their reasons cite, then match each flagged finding to the conclusions the draft represents. A flag counts whether or not the draft mentions it. A disposition recorded in the draft manifest applies only while the finding and its evidence remain materially the same as when it was recorded; a flag raised or changed since then reopens it.

An affected conclusion includes every place the draft represents it: findings text, methodology text, a figure's caption and alt text in `findings.md`, and a dataset or dataset column in `findings.md`'s dataset description. For each represented finding currently flagged for revalidation that lacks an applicable recorded disposition, stop, list those places, and ask the user to choose one outcome. The user may give one answer for every listed place or a different answer per place:

1. revalidate it through a separate analytical step;
2. omit it from the package; or
3. release it with the caveat explicitly accepted.

Release is never authority to revalidate or rerun analysis. A revalidation choice pauses the release until separate analytical work updates the investigation and the draft; the user then requests the release again. For omission or an accepted caveat, revise the draft through [awb-package](../awb-package/SKILL.md) so each listed place omits the conclusion or carries the caveat beside it and the draft lists the finding as unresolved, and record each disposition in the draft manifest's `revalidation_flags`. An applicable disposition whose omission or caveat is missing from the draft also requires that revision before release. A recorded disposition stays applicable while the finding and its evidence remain materially the same.

Once every represented flag has an applicable disposition, re-verify the draft against all the consistency rules, the structural rules and the deferred caveat rule together, even when this release needed no new disposition. Run `verify` again on the draft as it now stands; never reuse the earlier result. When a rule fails, list each discrepancy and stop as in **Verify the draft**.

## Create the release

Number the release one greater than the highest existing numeric directory under `released/`, zero-padded to at least three digits; use `001` when none exists. Leave numbering gaps unfilled and existing releases untouched.

Copy the complete draft, including its exact exported datasets, to `deliveries/<investigation>/<package>/released/<NNN>/`; never re-export or regenerate results for a release. In the copy only, set the manifest's `status` to `release`, `release_number` to the number, `released_at` to the release time, and `prior_release` to the previous highest release or `none`; leave `revised_at` and `inventory` unchanged, since the inventory lists the manifest by path only. The draft stays the working location for later revisions and the next delivery.

## Copy to storage

When the recorded location is a filesystem path that exists and is reachable from this machine, copy the new release directory to `<location>/<investigation>/<package>/released/<NNN>/`, creating the intermediate directories as needed. Never overwrite: if that directory already exists, stop the copy and report the conflict. Run `compare_trees` from `src/packaging/manifest.py` with the local release as `local_dir` and the copy as `copy_dir`, copying the helper first as in **Verify the draft** if it is missing, and report each discrepancy it returns, or that it returned none. Never compare the trees by hand.

When the location is not reachable, such as a SharePoint or other URL, or a path that is absent or unmounted, tell the user exactly which local directory to copy and the destination path to copy it to. With `none chosen`, repeat the warning that this checkout holds the only copy.

## Record storage without releasing

When the user asks only to record or change where released packages are kept, record the location as above and create no release. Then, for each existing numbered release under `deliveries/`, apply **Copy to storage**, including its `compare_trees` check; a destination that already exists is skipped and reported, never overwritten. Report each copy with its comparison result, each skip, and each copy instruction.

## Report

Finish with:

- the release path and release number;
- the included datasets, or none;
- dispositions recorded during this release and those carried from earlier revisions;
- provenance gaps carried from the manifest;
- a warning naming each acquisition the manifest cites whose retained copy in `foundation/sources.md` is blank or `this checkout only`, since its landed original exists only in this checkout; and
- the storage result: the verified copy path, a conflict or a file-list or checksum mismatch, the exact copy instruction, or the only-copy warning.
