---
name: awb-package
description: Create or revise the working draft of an analytics workbench delivery package. Use only when the user explicitly requests package work; routine analysis, record maintenance, and revalidation flags never trigger it. Marking a package delivered belongs to awb-release.
---

# Draft a delivery package

Package one investigation only after the user explicitly requests package work. Routine analysis, record maintenance, and revalidation flags never trigger packaging.

Resolve every repository path from the project root and every bundled asset path relative to this `SKILL.md`. Keep the workflow portable: use repository conventions and available tools rather than assuming a language, backend, or global skill installation.

## Establish the package

Identify the investigation, package name, and requested action: create or revise the working draft, and whether the user also marks the package delivered. If the request could refer to multiple investigations, ask which one before changing package files.

Use the package name the user gives. Otherwise reuse the existing package's name, or for a new package derive a short, stable name from the investigation, such as its name plus a purpose word, and report it.

Use one stable package per investigation by default. Add another only for an independent scope or delivery schedule. Keep all revisions at:

```text
deliveries/<investigation>/<package>/draft/
```

Preserved releases live at `released/001`, `released/002`, and so on. Treat existing numbered releases as immutable; read them, never change them.

If any of these shared files is missing, copy only the missing file from this skill's `assets/package-format/` directory into the project's root `package-format/` directory:

- [journal-template.md](assets/package-format/journal-template.md)
- [executive-summary-template.md](assets/package-format/executive-summary-template.md)
- [m365-assembly.md](assets/package-format/m365-assembly.md)
- [manifest-template.md](assets/package-format/manifest-template.md)

Preserve every existing shared format file. The root `package-format/` applies across investigations; keep it shared rather than forking it for a package.

For a new package, ask which audience-facing datasets to include and explicitly offer **none**. There is no default export set. For a revision, inherit the selection recorded in the current manifest unless the user changes it or it no longer fits the package scope. If it no longer fits, explain why and ask for a new selection before exporting data.

## Gather the record

Read the investigation's `brief.md`, `state.md`, `history.md`, analytical settings, and composition entry. Read the portions of `foundation/sources.md`, `catalog.md`, `quality.md`, and `glossary.md` relevant to this investigation, its inputs, and its selected exports. Also inspect the current draft manifest and latest numbered release when they exist.

Use these records to recover the business question, scope, intended decision or exploratory purpose, usefulness criteria, methods, settings, findings, contrary evidence, source quality, limitations, and unresolved revalidation flags. Include data limitations and errors that affect interpretation. The journal follows the same inclusion rule as `history.md`: a methodological mistake that changed a finding or explains why an earlier conclusion was wrong belongs in the account; routine debugging, coding mistakes, and abandoned execution attempts that changed no understanding stay in code history.

Capture provenance for every field in `package-format/manifest-template.md`, covering both the represented analytical results and the packaging operation. A commit identifies code, not data. Recover the result-producing state from recorded result provenance, the investigation records, or an earlier package manifest; the current `HEAD` describes the packaging checkout, not the results. If the producing state included uncommitted changes, say that its SHA does not fully identify the producing code and record the changed paths or other available state evidence. If no commit existed and the evidence records `uncommitted` with the checksums of the producing files, record that value and those checksums as the producing commit, and say that no commit identifies the producing code. A package built from a dirty or uncommitted producing state is never described as reproducible. If a provenance field is unavailable, record it as unknown with the reason. Commit nothing on the user's behalf to make provenance look clean.

## Assemble the draft

Create the draft lazily and update the same paths on each revision:

```text
draft/
├── journal.md
├── executive-summary.md
├── m365-assembly.md
├── manifest.<project-format>
├── figures/                     # only when the narrative cites figures
└── datasets/                    # only when datasets were selected
```

Use the shared templates as structure, adapting them to the investigation rather than copying placeholder text. The journal is the authoritative account of the analysis represented by this package. When a prior release exists, add a concise **Changes since previous release** section measured against the latest numbered release, without replacing the complete narrative. Derive the executive summary from that complete journal. Copy the shared `m365-assembly.md` into the draft, fill its **Files in this package** list, and adjust only concrete package details such as included filenames. Create the manifest from the shared field list with its field names, in the project's existing manifest format, keeping any additional fields an established schema has. Set `created_at` once, `revised_at` on every revision, and `status` to `draft`.

Export exactly the user-selected datasets through existing code in `src/packaging/` or the analytical modules where available. These are audience-facing outputs, not intermediate handoffs; convenience extracts, temporary query dumps, and full database snapshots are out of scope. An explicit selection of none produces no dataset exports. Write each export in the project's established export format; when none exists, use CSV with a header row. A caveat on a dataset or column goes in the journal's description of that dataset, never into its values.

An export may run a neutral operation at the packaging checkout only to serialize a result already recorded in the investigation. Before running it, run `compare_evidence` from the project's `src/provenance.py` against the result's evidence file, first copying [awb_provenance.py](../awb-init/assets/awb_provenance.py) to `src/provenance.py` if the project lacks it. It compares the current state with the complete producing state recorded with the result, code and data alike: committed producing paths against the producing commit with `git diff`; uncommitted producing paths against their recorded checksums, or every producing file when the producing commit is `uncommitted`; view definitions against their recorded checksums and the publications they read; input publication and acquisition files against the checksums in their publication and provenance files; and resolved settings against the recorded settings. Record its output unchanged, each comparison with its paths and outcome, under the manifest's `export_checks`; a comparison made by hand does not substitute for it. When any comparison fails, when the result has no evidence file, or when the helper reports missing evidence, export nothing, then stop and report: the export would not serialize the represented result, and changed results need separate analytical work.

Copy each figure the narrative cites into `figures/`, reusing the investigation's evidence figure unless separate analytical work changed the result; figures follow [awb-visualize](../awb-visualize/SKILL.md). When a reused figure needs a caveat it does not carry, put the caveat in the figure's caption text in the journal and in its alt text; leave the PNG unchanged. Exact-rerun inputs or database snapshots are included only when the user explicitly chooses them.

For a narrative-only revision, reuse the existing result evidence, exports, and producing provenance. Update the narrative and package metadata without rerunning or reconstructing analysis. Run analytical code only when the user separately requests changed results. When a revision brings in facts not yet in the investigation records, such as a limitation or context the user supplies, record them in the investigation's `history.md` as record maintenance before or with the revision, so the journal never states more than the records.

Findings awaiting revalidation may remain in the draft under the caveat rule below. List each represented finding currently flagged in `state.md` under the manifest's `revalidation_flags`, with its current reason and every place the draft represents an affected conclusion, and disposition `none` until the user chooses. Preserve the user's recorded revalidate, omit, or release-with-caveat disposition across revisions while the finding and evidence remain materially the same; when the flag's reason changes, record the new reason and reset its dispositions to `none`. Packaging never reruns analysis on its own; an export under the check above is not a rerun.

Every revision leaves the draft consistent:

- The journal is self-contained: it explains enough scope, sources, method, settings, findings, evidence, contrary results, limitations, and caveats to stand without earlier releases or M365 edits.
- The executive summary agrees with the journal in claims, numbers, qualifications, and recommendations.
- The manifest `inventory` matches the draft directory exactly: the same files, each with matching byte size and SHA-256, and the manifest listed by path only.
- The `datasets/` directory and the manifest match the recorded dataset selection.
- Every place the draft represents an affected conclusion of a finding awaiting revalidation carries a nearby caveat, unless a recorded disposition omits it: journal and summary text beside the claim, a figure in its journal caption and alt text, and a dataset or column in the journal's description of it. The draft lists that finding as unresolved.

## Delivery milestone

When the user marks the package delivered or requests an equivalent delivery milestone, finish any draft revision requested with it, then invoke the sibling [`awb-release`](../awb-release/SKILL.md). That skill verifies the draft's structure, settles revalidation dispositions, re-verifies the draft in full, and preserves the numbered release; this skill never creates a `released/` directory.

## M365 boundary

The package narrative and datasets are authoritative upstream. M365 may turn the supplied Markdown and selected datasets into polished Word and Excel files using the included assembly instructions. Make substantive revisions in the upstream draft and send the refreshed package forward again. Word or Excel edits are never reconciled back into the workbench.

Finish by reporting the draft path, included datasets, provenance gaps, and unresolved caveats. Tell the user it is a working copy that the next revision overwrites; only marking it delivered preserves it as a numbered release. When a represented finding is flagged for revalidation without an applicable recorded disposition, note that `awb-release` will ask for a disposition for each before releasing.
