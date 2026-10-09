---
name: awb-package
description: "Draft or revise an analytics workbench delivery package (deck outline, charts, datasets). Use only when the user asks for a package or deck, or a change to its draft."
---

# Draft a delivery package

Packaging **serializes** recorded results: it reuses recorded evidence, exports, and provenance, and changed results come only from separately authorized analysis. Read the [package contract](references/package-contract.md) first; it holds the layout, the consistency rules, and the commands. Bundled asset paths are relative to this `SKILL.md`.

## Sequence

1. **Establish** the investigation, package name, dataset selection, and Audience.
2. **Gather** the record on the read path the change needs.
3. **Write** `findings.md`, with every **Chart N.** specification, `methodology.md`, and `m365-assembly.md` from the project's templates. This creates the draft.
4. **Export** the chart and dataset files. Skip it when a revision reuses every export.
5. **Provenance**: run `draft-provenance`, then fill the remaining manifest fields.
6. **Check** last with `check-draft`, until done.
7. **Report.**

## 1. Establish

Identify the investigation and package. When the request could refer to more than one investigation, ask which before changing package files. Use the package name the user gives; otherwise reuse the existing package's name, or derive a short, stable one from the investigation and a purpose word and report it. Keep one package per investigation unless another has an independent scope or delivery schedule.

From the project root, copy the missing shared formats with one `mkdir -p package-format && cp -n <skill-directory>/assets/package-format/*.md package-format/`, which preserves existing files.

For a new package, ask which audience-facing datasets to include and explicitly offer **none**; there is no default export set. A revision inherits the selection in the current manifest unless the user changes it or it no longer fits the package scope; then explain why and ask for a new selection before exporting.

Read the **Audience** section of the investigation's `brief.md`: who will see or present the deck, what they already know, the decision they own, and the terms they use. When it is missing or blank, ask the user, then record the answer there (adding the section after **Purpose** when absent) as record maintenance.

## 2. Gather the record

- **New draft or changed analytical scope or results:** read the investigation's `brief.md`, `state.md`, `history.md`, settings, and `run.py`; the relevant portions of `foundation/sources.md`, `catalog.md`, `quality.md`, and `glossary.md`; and the existing draft manifest and latest release, when present. Changed results need recorded evidence from separately authorized analytical work before packaging.
- **Bounded narrative revision, including an omission or accepted caveat:** start with the current draft and manifest, the brief's **Audience**, current findings and flags in `state.md`, the requested change, and the evidence, history entries, and foundation entries relevant to it, plus the latest release portions and release date both changes sections need. Expand to the rest of the brief, settings, `run.py`, earlier history, and foundation records wherever scope, evidence, provenance, or consistency is missing or conflicting.

Recover the business question, intended decision or exploratory purpose, audience, usefulness criteria, and evidence the contract needs, with the data limitations and errors that affect interpretation.

## 3. Write the draft

Create the draft at the contract's paths, or revise the same files. A draft in an earlier format (a `figures/` directory, a narrative `findings.md`, or a journal and executive summary) is rewritten whole in the current format on its next revision, whatever the change; releases stay frozen.

- `findings.md` is the deck outline under the slide rules and translation rule in `package-format/findings-template.md`; its **Answer** slide is the executive summary.
- `methodology.md` follows `package-format/methodology-template.md` in the workbench's own vocabulary.
- Copy `package-format/m365-assembly.md`, fill **Files in this package** and **Audience** from the draft and the brief, and adjust only concrete package details.
- When a revision brings in facts the investigation records lack, such as a limitation the user supplies, record them in the investigation's `history.md` as record maintenance with the revision, so neither narrative states more than the records.

## 4. Export

Export exactly the user-selected datasets and one `--chart` per **Chart N.** specification, in order, with one call: `python3 src/awb.py export <investigation> <package> --chart <result>[:<columns>] ... --dataset <name>=<result>[:<columns>] ...` (or `--no-datasets`). Choose columns so each file holds exactly what its chart plots, with interval bounds as their own columns. Display choices such as the highlight or the baseline go in the specification. When it lists display-name gaps, add them to `foundation/display.toml` from the glossary and rerun. Paste its `methodology_lines` into `methodology.md`. When `export` reports `exports_blocked`, stop and report it. A project with an established non-CSV format exports by hand as [helpers](references/helpers.md) describes.

## 5. Provenance

Run `python3 src/awb.py draft-provenance <investigation> <package> <result-id>...`, naming every represented result. When it reports missing evidence it writes nothing: rerun it with the results that have evidence, and record the missing results' producing state by hand from the investigation records or an earlier manifest, never from the current `HEAD`, under the template's producing-state rules. Commit nothing on the user's behalf to make provenance look clean.

Fill `scope` and the remaining fields under `package-format/manifest-template.md`; set `created_at` once, `revised_at` on every revision, and `status` to `draft`, and preserve additional fields of an established schema. Record every finding `state.md` flags under `revalidation_flags`, with its finding and reason exactly as the row writes them, each represented place with disposition `none` until the user chooses, or `represented_in: none`. A recorded disposition applies while its finding and reason match the current `state.md` row exactly; a new or changed reason reopens it. Exact-rerun inputs or snapshots go in only when the user chooses them.

## 6. Check

Once every other draft file is final, run `python3 src/awb.py check-draft <investigation> <package>`. Repair the draft and rerun it.

**Done** when `check-draft` prints `passed: true` on the final files and you have confirmed what it cannot check: both narratives carry the same numbers, qualifications, and caveats; every `revalidation_flags` place carries its caveat or omission; every claim in `findings.md` traces to `methodology.md`. Any edit after `check-draft` reruns it. Report its rows verbatim.

## 7. Report

Report the draft path, the audience `findings.md` is written for, the included datasets, each chart with the result it serializes, provenance gaps, and unresolved caveats. Say it is a working copy the next revision overwrites; marking it delivered freezes it as a numbered release. When a represented flagged finding lacks an applicable disposition, say `awb-release` will ask for one before releasing.

Tell the user how to build the deck: in a Microsoft 365 Copilot app chat, add the PowerPoint agent, attach `findings.md`, every file in `charts/`, `methodology.md`, and `m365-assembly.md`, and ask for a deck built under those instructions. Datasets travel beside the deck and are not attached.

## Delivery milestone

When the user marks the package delivered, finish any revision requested with it, then invoke the sibling [`awb-release`](../awb-release/SKILL.md).
