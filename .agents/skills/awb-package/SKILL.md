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

- [findings-template.md](assets/package-format/findings-template.md)
- [methodology-template.md](assets/package-format/methodology-template.md)
- [m365-assembly.md](assets/package-format/m365-assembly.md)
- [manifest-template.md](assets/package-format/manifest-template.md)

Preserve every existing shared format file. The root `package-format/` applies across investigations; keep it shared rather than forking it for a package.

If `src/packaging/manifest.py` is missing, copy [awb_manifest.py](assets/awb_manifest.py) there; it builds and checks the manifest `inventory`. If `src/packaging/findings.py` is missing, copy [awb_findings.py](assets/awb_findings.py) there; it finds internal names left in `findings.md`. Keep existing copies, and import both from `src/packaging/`, never from the skill folder.

For a new package, ask which audience-facing datasets to include and explicitly offer **none**. There is no default export set. For a revision, inherit the selection recorded in the current manifest unless the user changes it or it no longer fits the package scope. If it no longer fits, explain why and ask for a new selection before exporting data.

Read the **Audience** section of the investigation's `brief.md`: who will read the delivered documents, what they already know, the decision they own, and the terms they use. `findings.md` is written for that audience. When the section is missing or blank, ask the user before drafting, and record the answer in the brief's **Audience** section, adding the section after **Purpose** when absent, as record maintenance.

## Gather the record

Read the investigation's `brief.md`, `state.md`, `history.md`, analytical settings, and composition entry. Read the portions of `foundation/sources.md`, `catalog.md`, `quality.md`, and `glossary.md` relevant to this investigation, its inputs, and its selected exports. Also inspect the current draft manifest and latest numbered release when they exist.

Use these records to recover the business question, scope, intended decision or exploratory purpose, audience, usefulness criteria, methods, settings, findings, contrary evidence, source quality, limitations, and unresolved revalidation flags. Include data limitations and errors that affect interpretation. `methodology.md` follows the same inclusion rule as `history.md`: a methodological mistake that changed a finding or explains why an earlier conclusion was wrong belongs in the account; routine debugging, coding mistakes, and abandoned execution attempts that changed no understanding stay in code history.

The records are written in internal vocabulary: view, table, and column names, settings keys, result IDs, and paths. `methodology.md` keeps that vocabulary. `findings.md` translates it for the audience under the translation rule in `package-format/findings-template.md`: glossary business terms in place of internal names, sources described by owner, content, and period, and exclusions and choices described by their effect.

Capture provenance for every field in `package-format/manifest-template.md`, covering both the represented analytical results and the packaging operation. A commit identifies code, not data. Recover the result-producing state from recorded result provenance, the investigation records, or an earlier package manifest; the current `HEAD` describes the packaging checkout, not the results. If the producing state included uncommitted changes, say that its SHA does not fully identify the producing code and record the changed paths or other available state evidence. If no commit existed and the evidence records `uncommitted` with the checksums of the producing files, record that value and those checksums as the producing commit, and say that no commit identifies the producing code. A package built from a dirty or uncommitted producing state is never described as reproducible. If a provenance field is unavailable, record it as unknown with the reason. Commit nothing on the user's behalf to make provenance look clean.

## Assemble the draft

Create the draft lazily and update the same paths on each revision:

```text
draft/
├── findings.md                  # audience-facing; the only source of document content
├── methodology.md               # internal reference; never rendered into documents
├── m365-assembly.md
├── manifest.<project-format>
├── figures/                     # only when findings.md cites figures
└── datasets/                    # only when datasets were selected
```

Use the shared templates as structure, adapting them to the investigation rather than copying placeholder text. `methodology.md` is the authoritative account of the analysis represented by this package, in internal vocabulary. `findings.md` derives from it for the audience and is the only source of content for the delivered documents; it states nothing `methodology.md` does not support. No executive summary is written in the workbench: M365 distills it from `findings.md` under the guidelines in `m365-assembly.md`. When a prior release exists, measure a concise changes section in each file against the latest numbered release, without replacing the complete narrative: `findings.md`'s **What changed since the last version** refers to that release by the date in its manifest's `released_at`, and `methodology.md`'s **Changes since previous release** by its release number. Copy the shared `m365-assembly.md` into the draft, fill its **Files in this package** list and its **Audience** section from the brief, and adjust only concrete package details such as included filenames. Create the manifest from the shared field list with its field names, in the project's existing manifest format, keeping any additional fields an established schema has. Set `created_at` once, `revised_at` on every revision, and `status` to `draft`.

Export exactly the user-selected datasets through existing code in `src/packaging/` or the analytical modules where available. These are audience-facing outputs, not intermediate handoffs; convenience extracts, temporary query dumps, and full database snapshots are out of scope. An explicit selection of none produces no dataset exports. Write each export in the project's established export format; when none exists, use CSV with a header row. Name each column with its display name from the glossary, in the audience's terms, never the view or column name; renaming headers serializes the same values and is not an analytical change. Record each display header with the source column it came from in `methodology.md`. A caveat on a dataset or column goes in the description of that dataset under **Supporting datasets** in `findings.md`, never into its values.

An export may run a neutral operation at the packaging checkout only to serialize a result already recorded in the investigation. Before running it, run `compare_evidence` from the project's `src/provenance.py` against the result's evidence file, first copying [awb_provenance.py](../awb-init/assets/awb_provenance.py) to `src/provenance.py` if the project lacks it. It compares the current state with the complete producing state recorded with the result, code and data alike: committed producing paths against the producing commit with `git diff`; uncommitted producing paths against their recorded checksums, or every producing file when the producing commit is `uncommitted`; view definitions against their recorded checksums and the publications they read; input publication and acquisition files against the checksums in their publication and provenance files; and resolved settings against the recorded settings. Record its output unchanged, each comparison with its paths and outcome, under the manifest's `export_checks`; a comparison made by hand does not substitute for it. When any comparison fails, when the result has no evidence file, or when the helper reports missing evidence, export nothing, then stop and report: the export would not serialize the represented result, and changed results need separate analytical work.

Copy each figure `findings.md` cites into `figures/`; figures follow [awb-visualize](../awb-visualize/SKILL.md). Unless separate analytical work changed the result, reuse the investigation's evidence figure when it passes `check_text` from the project's `src/presentation/style.py` and draws no caption in the image; a reused PNG stays unchanged. `save_figure` runs `check_text` before writing, so a figure it saved under the current rules passes; inspect the image to confirm plain labels and no drawn caption, since a PNG saved earlier cannot be rechecked by the helper. An evidence figure made under the earlier rules, with a caption drawn in the image or raw names in its labels, is re-rendered for presentation from the plotted numbers recorded with it, the Markdown table that accompanies the figure, without running analytical code; save it with `save_figure` and record `Comment: presentation re-render of <evidence path>` in its provenance metadata. When those numbers are not recorded, never reconstruct them: leave the figure out, state its finding in text, and report the gap. Embed each figure in `findings.md` in the form `findings-template.md` gives; the italic `*Figure N. ...*` line after the image is the figure's caption, and nothing is drawn in the image. A caveat the figure needs goes in that caption and in its alt text, never into the PNG. Exact-rerun inputs or database snapshots are included only when the user explicitly chooses them.

For a narrative-only revision, reuse the existing result evidence, exports, and producing provenance. Update the narrative and package metadata without rerunning or reconstructing analysis. Run analytical code only when the user separately requests changed results. When a revision brings in facts not yet in the investigation records, such as a limitation or context the user supplies, record them in the investigation's `history.md` as record maintenance before or with the revision, so neither `findings.md` nor `methodology.md` states more than the records.

Findings awaiting revalidation may remain in the draft under the caveat rule below. List each represented finding currently flagged in `state.md` under the manifest's `revalidation_flags`, with its current reason and every place the draft represents an affected conclusion, and disposition `none` until the user chooses. Preserve the user's recorded revalidate, omit, or release-with-caveat disposition across revisions while the finding and evidence remain materially the same; when the flag's reason changes, record the new reason and reset its dispositions to `none`. Packaging never reruns analysis on its own; an export under the check above is not a rerun.

Every revision leaves the draft consistent:

- `findings.md` is self-contained for its audience: it gives enough context, answer, findings with their evidence and contrary results, plain-language method, limitations, and caveats to stand without earlier releases, `methodology.md`, or M365 edits. After its narrative is final, run `check` from `src/packaging/findings.py` on it, passing as `names` the investigation and package names, the view and table names the investigation reads, the keys of its settings file, and the result IDs its records cite, and repair `findings.md` until `check` returns `[]`. A check made by hand does not substitute for the helper.
- `methodology.md` is self-contained as the account of the analysis: it explains enough scope, sources, method, settings, validation, findings, evidence, contrary results, limitations, and caveats to stand without earlier releases or the investigation records.
- `findings.md` and `methodology.md` agree in claims, numbers, qualifications, and caveats, and every `###` finding heading in `findings.md` has a section with the same heading text in `methodology.md`.
- The manifest `inventory` matches the draft directory exactly: the same files, each with matching byte size and SHA-256, and the manifest listed by path only. After every other draft file is final, run `inventory` from `src/packaging/manifest.py` on the draft, serialize its rows in order into the manifest's `inventory` field, then run `verify` and repair the draft until it returns no discrepancies. A listing, hash, or comparison made by hand does not substitute for the helper.
- The `datasets/` directory and the manifest match the recorded dataset selection.
- Every place the draft represents an affected conclusion of a finding awaiting revalidation carries a nearby caveat, unless a recorded disposition omits it: findings text and methodology text beside the claim, a figure in its caption line and alt text in `findings.md`, and a dataset or column in its description under **Supporting datasets** in `findings.md`. The draft lists that finding as unresolved, under **Limitations and open caveats** in `findings.md` and **Revalidation status** in `methodology.md`.

## Delivery milestone

When the user marks the package delivered or requests an equivalent delivery milestone, finish any draft revision requested with it, then invoke the sibling [`awb-release`](../awb-release/SKILL.md). That skill verifies the draft's structure, settles revalidation dispositions, re-verifies the draft in full, and preserves the numbered release; this skill never creates a `released/` directory.

## M365 boundary

`findings.md`, `methodology.md`, and the datasets are authoritative upstream. M365 may turn `findings.md` and the selected datasets into polished Word and Excel files using the included assembly instructions, and distills the executive summary from `findings.md`; it may consult `methodology.md` for the reasoning behind a decision only, never as document content. Make substantive revisions in the upstream draft and send the refreshed package forward again. Word or Excel edits are never reconciled back into the workbench.

Finish by reporting the draft path, the audience `findings.md` is written for, included datasets, figures re-rendered for presentation or left out for missing plotted numbers, provenance gaps, and unresolved caveats. Tell the user it is a working copy that the next revision overwrites; only marking it delivered preserves it as a numbered release. When a represented finding is flagged for revalidation without an applicable recorded disposition, note that `awb-release` will ask for a disposition for each before releasing.
