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

When that line is absent or reads `not yet recorded`, ask the user where released packages are kept before creating the release. Record the answer on that line, adding the line after the README's `deliveries/` entry when absent and preserving every other line, including an older bullet that says to record the location once chosen. If the user declines, record `none chosen` and warn plainly that the release will exist only in this checkout. A recorded `none chosen` is a decision: repeat the warning at each release and record a location whenever the user names one.

## Verify the draft

Check the draft against the consistency rules in **Assemble the draft** of [awb-package](../awb-package/SKILL.md): it is self-contained, the journal and executive summary agree, its files match the manifest inventory exactly, and the selected exports are present. When it fails, list each discrepancy and stop; repairs are package revisions made through awb-package, never reconstructed here.

## Resolve revalidation flags

The draft can predate the current flags: a shared-data correction may flag findings in the investigation records after drafting, and record maintenance leaves the draft unchanged. Read the investigation's current `state.md` findings and revalidation flags, and the `foundation/quality.md` entries their reasons cite, then match each flagged finding to the conclusions the draft represents. A flag counts whether or not the draft mentions it. A disposition recorded in the draft manifest applies only while the finding and its evidence remain materially the same as when it was recorded; a flag raised or changed since then reopens it.

For each represented finding currently flagged for revalidation that lacks an applicable recorded disposition, stop and ask the user to choose one outcome per affected conclusion:

1. revalidate it through a separate analytical step;
2. omit it from the package; or
3. release it with the caveat explicitly accepted.

Release is never authority to revalidate or rerun analysis. A revalidation choice pauses the release until separate analytical work updates the investigation and the draft; the user then requests the release again. For omission or an accepted caveat, revise the draft through [awb-package](../awb-package/SKILL.md) so it omits the conclusion or carries the caveat beside it and lists the finding as unresolved, record the disposition in the draft manifest, and re-verify before continuing. An applicable disposition whose omission or caveat is missing from the draft also requires that revision before release. A recorded disposition stays applicable while the finding and its evidence remain materially the same.

## Create the release

Number the release one greater than the highest existing numeric directory under `released/`, zero-padded to at least three digits; use `001` when none exists. Leave numbering gaps unfilled and existing releases untouched.

Copy the complete draft, including its exact exported datasets, to `deliveries/<investigation>/<package>/released/<NNN>/`; never re-export or regenerate results for a release. In the copy only, mark the manifest status as a release with its number and release time. The draft stays the working location for later revisions and the next delivery.

## Copy to storage

When the recorded location is a filesystem path that exists and is reachable from this machine, copy the new release directory to `<location>/<investigation>/<package>/released/<NNN>/`, creating the intermediate directories as needed. Never overwrite: if that directory already exists, stop the copy and report the conflict. Compare the copy's recursive relative file list with the local release and report any difference.

When the location is not reachable, such as a SharePoint or other URL, or a path that is absent or unmounted, tell the user exactly which local directory to copy and the destination path to copy it to. With `none chosen`, repeat the warning that this checkout holds the only copy.

## Record storage without releasing

When the user asks only to record or change where released packages are kept, record the location as above and create no release. Then, for each existing numbered release under `deliveries/`, apply **Copy to storage**; a destination that already exists is skipped and reported, never overwritten. Report each copy, skip, or copy instruction.

## Report

Finish with:

- the release path and release number;
- the included datasets, or none;
- dispositions recorded during this release and those carried from earlier revisions;
- provenance gaps carried from the manifest; and
- the storage result: the verified copy path, a conflict or file-list mismatch, the exact copy instruction, or the only-copy warning.
