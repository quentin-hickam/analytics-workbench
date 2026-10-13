---
name: awb-package
description: "Draft or revise an analytics workbench delivery package (deck outline, charts, datasets). Use only when the user asks for a package or deck, or a change to its draft."
---

# Draft a delivery package

Packaging **serializes** recorded results. It uses the recorded evidence, exports, and provenance again. Changed results come only from analysis that has a separate authorization. First, read the [package contract](references/package-contract.md). It holds the layout, the consistency rules, and the commands. Bundled asset paths are relative to this `SKILL.md`.

## Sequence

1. **Establish** the investigation, package name, dataset selection, and Audience.
2. **Gather** the record on the read path that the change needs.
3. **Write** `findings.md` (with every **Chart N.** specification) and `methodology.md` from the project's templates. Copy `m365-assembly.md`. This creates the draft.
4. **Export the files and provenance** with `export` on every revision. Then review the flags.
5. **Check** with `check-draft` as the last step, until the draft is done.
6. **Report.**

## 1. Establish

Identify the investigation and package. If the request can refer to more than one investigation, ask which one. Do this before you change package files. Use the package name that the user gives. If the user gives no name, do one of these:

- Use the name of the existing package again.
- Make a short, stable name from the investigation and a purpose word, and report this name.

Keep one package for each investigation, unless another package has an independent scope or delivery schedule.

From the project root, install the missing shared formats with `python3 <awb-init skill directory>/scripts/install_helpers.py . --package-formats`. This command keeps existing files and records what it installs in `.awb-receipt.json`.

For a new package, ask which audience-facing datasets to include. Explicitly offer **none** as a choice. There is no default export set. A revision keeps the selection in the current manifest, unless the user changes it or it no longer fits the package scope. In that case, explain why and ask for a new selection before you export.

Read the **Audience** section of the investigation's `brief.md`. It gives:

- Who will see or present the deck.
- What they already know.
- The decision that they own.
- The terms that they use.

If this section is missing or blank, ask the user. Then record the answer in that section as record maintenance. If the section is absent, add it after **Purpose**.

## 2. Gather the record

- **New draft or changed analytical scope or results:** read these items:
  - The investigation's `brief.md`, `state.md`, `history.md`, settings, and `run.py`.
  - The relevant parts of `foundation/sources.md`, `catalog.md`, `quality.md`, and `glossary.md`.
  - The existing draft manifest and the latest release, if they are present.

  Before packaging, changed results must have recorded evidence from analytical work that has a separate authorization.
- **Bounded narrative revision (this includes an omission or an accepted caveat):** start with these items:
  - The current draft and manifest.
  - The brief's **Audience**.
  - The current findings and flags in `state.md`.
  - The requested change.
  - The evidence, history entries, and foundation entries that are relevant to the change.
  - The parts of the latest release and the release date that the changes slide needs.

  If scope, evidence, provenance, or consistency is missing or in conflict, also read the rest of the brief, the settings, `run.py`, earlier history, and foundation records.

Recover these items:

- The business question.
- The intended decision or the exploratory purpose.
- The audience.
- The usefulness criteria.
- The evidence that the contract needs.
- The data limitations and errors that affect interpretation.

## 3. Write the draft

Create the draft at the paths in the contract, or revise the same files. On its next revision, a draft in an earlier format is rewritten completely in the current format. Releases stay frozen.

- Before you write, give each column that a chart or dataset will export a display name from the glossary in `foundation/display.toml`. For example, `[columns]` then `return_rate = "Return rate"`. **Data:** lines and dataset headers use these names.
- `findings.md` is the deck outline. It follows the slide rules and the translation rule in `package-format/findings-template.md`. Its **Answer** slide is the executive summary.
- `methodology.md` follows `package-format/methodology-template.md` and uses the workbench's own vocabulary.
- Copy `package-format/m365-assembly.md` into the draft. Do not change it.
- If a revision brings in facts that the investigation records do not have, record these facts in the investigation's `history.md`. An example is a limitation that the user supplies. Record them as record maintenance with the revision, so that neither narrative states more than the records.

## 4. Export the files and provenance

Run `python3 src/awb.py export <investigation> <package> --chart <result>[:<columns>] ... --dataset <name>=<result>[:<columns>] ... (or --no-datasets) --result <id> ...`. Pass every represented result with evidence, as follows:

- One `--chart` for each **Chart N.** specification, in order.
- Exactly the datasets that the user selected.
- Each other represented result as `--result`.

The command records a `--result` without the export check. This lets you represent a flagged finding with its caveat. Choose columns so that each file holds exactly what its chart plots. Put interval bounds in their own columns. Put display choices (for example, the highlight or the baseline) in the specification.

If `export` lists display-name gaps, do these steps:

1. Fill its `display_stub` under `[columns]`.
2. Fix in place any blank name that it reports.
3. Run it again.

Paste its `methodology_lines` into `methodology.md`. For a revision that only adds caveats and keeps the exported files, pass every represented result with `--result` only. Do not use `--chart`, `--dataset`, or `--no-datasets`. If `export` reports `exports_blocked`, stop and report it.

If `export` reports missing evidence, it writes nothing. In that case, run it again without those results, and record the producing state of those results by hand. Get this state from investigation records or an earlier manifest, and never from the current checkout. Do not commit anything on behalf of the user to make provenance look clean.

`export` records the finding and reason of each flag, and lists `flags_pending`. Compare the `represented_in` of every flag with the revised draft. Fill the pending places as the contract specifies. Then, for each represented flag whose disposition is still `none`, ask the user to revalidate, omit, or release with the caveat. Record the answer. If there is no answer, the disposition stays `none`.

## 5. Check

When every other draft file is final, run `python3 src/awb.py check-draft <investigation> <package>`. Repair the draft and run the command again.

**Done** when these conditions are true:

- `check-draft` prints `passed: true` on the final files.
- You confirmed the items that it cannot check:
  - Both narratives carry the same numbers, qualifications, and caveats.
  - Every `revalidation_flags` place carries its caveat or omission.
  - Every claim in `findings.md` traces to `methodology.md`.

If you make an edit after `check-draft`, run `check-draft` again. Report its rows verbatim.

## 6. Report

Report these items:

- The draft path.
- The audience for which `findings.md` is written.
- The included datasets.
- Each chart, with the result that it serializes.
- Provenance gaps.
- Unresolved caveats.

Say that the draft is a working copy that the next revision overwrites. When it is marked delivered, it is frozen as a numbered release. If a represented flagged finding does not have an applicable disposition, say that `awb-release` will ask for one before it releases.

Tell the user how to build the deck:

1. In a Microsoft 365 Copilot app chat, add the PowerPoint agent.
2. Attach `findings.md`, every file in `charts/`, `methodology.md`, and `m365-assembly.md`.
3. Ask for a deck built under those instructions.

Datasets travel beside the deck and are not attached.

## Delivery milestone

When the user marks the package delivered, finish any revision requested with it. Then invoke the sibling [`awb-release`](../awb-release/SKILL.md).
