---
name: awb-package
description: "Draft or revise an analytics workbench delivery package: deck outline, charts, and selected datasets. Use only for requests such as \"make me slides\", \"prepare a deck\", or \"revise the package draft\"."
---

# Draft a delivery package

Packaging **serializes** recorded results: it reuses recorded evidence, exports, and provenance, and changed results come only from separately authorized analysis. Read the [package contract](references/package-contract.md) first; it holds the layout, the consistency rules, and the commands. Bundled asset paths are relative to this `SKILL.md`.

## Sequence

1. **Establish** the investigation, package name, dataset selection, and Audience.
2. **Gather** the record on the read path the change needs.
3. **Review the headlines, then write** `findings.md`, with every **Chart N.** specification, and `methodology.md` from the project's templates, and copy the deck rules and assembly files. Review headlines before a new draft's full slides; skip the checkpoint for a revision that keeps the storyline.
4. **Export the files and provenance** with `export` on every revision, then review the flags.
5. **Review** the narratives with a read-only reviewer against every review rule.
6. **Check** last with `check-draft`, until done.
7. **Report.**

## 1. Establish

Identify the investigation and package. When the request corrects a draft the user is reviewing, record the correction as a review rule first when later drafts could repeat it, as [references/review.md](references/review.md) says under **After the review**. When the request could refer to more than one investigation, ask which before changing package files. Use the package name the user gives; otherwise reuse the existing package's name, or derive a short, stable one from the investigation and a purpose word and report it. Keep one package per investigation unless another has an independent scope or delivery schedule.

From the project root, install the missing shared formats with `python3 <awb-init skill directory>/scripts/install_helpers.py . --package-formats`, which preserves existing files and records what it installs in `.awb-receipt.json`.

For a new package, ask which audience-facing datasets to include and explicitly offer **none**; there is no default export set. A revision inherits the selection in the current manifest unless the user changes it or it no longer fits the package scope; when it no longer fits, explain why and ask for a new selection before exporting.

Read the **Audience** section of the investigation's `brief.md`: who will see or present the deck, what they already know, the decision they own, and the terms they use. When it is missing or blank, ask the user, then record the answer there (adding the section after **Purpose** when absent) as record maintenance.

## 2. Gather the record

- **New draft or changed analytical scope or results:** read the investigation's `brief.md`, `state.md`, `history.md`, settings, and `run.py`; the relevant portions of `foundation/sources.md`, `catalog.md`, `quality.md`, and `glossary.md`; and the existing draft manifest and latest release, when present. Changed results need recorded evidence from separately authorized analytical work before packaging.
- **Bounded narrative revision, including an omission or accepted caveat:** start with the current draft and manifest, the brief's **Audience**, current findings and flags in `state.md`, the requested change, and the evidence, history entries, and foundation entries relevant to it, plus the latest release portions and release date the changes slide needs. Expand to the rest of the brief, settings, `run.py`, earlier history, and foundation records wherever scope, evidence, provenance, or consistency is missing or conflicting.

Recover the business question, intended decision or exploratory purpose, audience, usefulness criteria, and evidence the contract needs, with the data limitations and errors that affect interpretation.

Read the ledger with `python3 src/awb.py questions list --all` and each represented result's recorded settings `answers` to derive the storyline under the contract's **Ledger storyline** rules (pass `--investigation <name>` to commands for another investigation).

When a brief section names a ledger question ID, resolve it with that list. An `answered` question supplies its recorded text or linked result's value; `answered (awaiting recheck)` leaves it unsettled, as does any other status, missing ID, or failed lookup. The list prints each linked finding's status. When unsettled, ask only if the question is open and its answerer is `user`, recording the answer with `python3 src/awb.py questions answer Q-NNN --text "<answer>" --by "<the user>"` before writing; otherwise carry the unsettled element, including any usefulness criterion, in both narratives: in `findings.md` in the audience's words, naming its owner; its ID only in `methodology.md`'s **What makes the answer useful:** (or matching) line. Never present it as settled.

## 3. Write the draft

### Review the headlines

For each required question whose text is not in the audience's words, set audience wording with `python3 src/awb.py questions edit Q-NNN --audience "<wording>"`, leaving its text unchanged. For a new draft, write the title slide and every slide headline in storyline order, including the conditional **Open questions** slide, before writing the full slide bodies. Show these headlines, and the required questions as the slide words them, to the user and ask them to approve or reorder them; wait for their answer before expanding the slides. Apply an approved reorder through the ledger's parent and priority fields; when they cannot express it without changing what they mean, tell the user and keep the derived order. A revision that keeps the storyline skips this step, but new audience wording still needs the user's approval. A changed storyline returns here before full slides are rewritten.

### Write the full slides

Create the draft at the contract's paths, or revise the same files. A draft in an earlier format is rewritten whole in the current format on its next revision; releases stay frozen.

- Before writing, give each column a chart or dataset will export a display name from the glossary in `foundation/display.toml`, e.g. `[columns]` then `return_rate = "Return rate"`; **Data:** lines and dataset headers use these names.
- `findings.md` is the deck outline under the slide rules and translation rule in `package-format/findings-template.md`; its **Answer** slide is the executive summary.
- Order finding slides and include **Open questions** under the contract's **Ledger storyline** rules. Report every finding with no linked ledger question, even though its placement last passes the check.
- `methodology.md` follows `package-format/methodology-template.md` in the workbench's own vocabulary.
- Copy `package-format/deck-rules.md` and `package-format/assembly/m365.md` into the draft unchanged, at the same paths under it.
- When a revision brings in facts the investigation records lack, such as a limitation the user supplies, record them in the investigation's `history.md` as record maintenance with the revision, so neither narrative states more than the records.

## 4. Export the files and provenance

Run `python3 src/awb.py export <investigation> <package> --chart <result>[:<columns>] ... --dataset <name>=<result>[:<columns>] ... (or --no-datasets) --result <id> ...`, passing every represented result: one `--chart` per **Chart N.** specification, in order, exactly the user-selected datasets, and each other represented result as `--result`; a `--result` is recorded without the export check, so a flagged finding can be represented with its caveat. Choose columns so each file holds exactly what its chart plots, with interval bounds as their own columns. Display choices such as the highlight or the baseline go in the specification. When it lists display-name gaps, fill its `display_stub` under `[columns]`, fix any blank name it reports in place, and rerun. Paste its `methodology_lines` into `methodology.md`, and repeat each of its `questions` verbatim in the methodology section of the finding that result supports. For a revision that only adds caveats and keeps the exported files, pass only `--result`, once for every represented result; omit `--chart`, `--dataset`, and `--no-datasets`. When `export` reports `exports_blocked`, stop and report it. When it reports missing evidence it writes nothing, so the draft and its manifest stay as they were. If a result without evidence is serialized by a `--chart` or `--dataset`, or has an entry in the manifest's `export_checks` (`export` records one for every result a chart or dataset file serializes and keeps it while the result is represented), or if no `--result` in a `--result`-only run has evidence, stop and report it as for `exports_blocked`: only separately authorized analytical work restores the evidence, and dropping a chart, a dataset, or a recorded export check is the user's decision. Otherwise rerun it without those results. For each, the rerun drops only its `results` entry and its share of the producing state (the fields under **Producing state** in `package-format/manifest-template.md`); add both back by hand: the `results` entry with the `evidence` path `export` named, the `question` from the result's settings table, and its `runtime` copied from an earlier manifest's `results` entry, or `{"unknown": "evidence missing"}` when none records it, never read from the current interpreter; and the producing state from investigation records or an earlier manifest, never from the current checkout. While their evidence is missing, every later `export` run drops them again, so restore them after each. Commit nothing on the user's behalf to make provenance look clean.

`export` records each flag's finding and reason and lists `flags_pending`. Review every flag's `represented_in` against the revised draft and fill pending places per the contract; then for any represented flag whose disposition is still `none`, ask the user to revalidate, omit, or release with the caveat, and record the answer; without one it stays `none`.

## 5. Review

Once the narratives and flags are complete, run the review in [references/review.md](references/review.md): a fresh subagent, limited to read tools, checks the draft against every rule in `foundation/review-rules.md` and what `check-draft` cannot check, and reports without fixing; that file's **Launch** says how each host starts it. Act on its report as that file's **After the review** says.

## 6. Check

Once every other draft file is final, run `python3 src/awb.py check-draft <investigation> <package>`. Repair the draft and rerun it.

A `numbers` row is a number no represented result records. Repair it by the first of these that fits:

1. It comes from a recorded result the draft relies on but `export` was not given: rerun `export` as step 4 says, passing that result too. `allowed_numbers` never stands in for representing a result.
2. A represented result records it at another value or precision: rewrite it from the recorded value.
3. It is not a quantity, such as a date, a comparison year, a chart number, a tool version, or a week number: the check reports any number whose context leaves it in doubt, so reword where a context [helpers](references/helpers.md) lists would mark it, such as a comma after a date or year; otherwise, or when the records support it from elsewhere, such as a figure from an earlier release, a fact the user supplied that `history.md` records, or a number inside a result's question that `methodology.md` must repeat, list it in the manifest's `allowed_numbers` as `package-format/manifest-template.md` describes.
4. It is computed from results that none records: only separately authorized analysis records it; until then, leave it out.

**Done** when `check-draft` prints `passed: true` on the final files and the last review is passed and not stale, as [references/review.md](references/review.md) defines under **After the review**; that review confirms what `check-draft` cannot check, since `check-draft` proves only that each number is recorded somewhere. Any edit after `check-draft` reruns it. Report its outcome.

## 7. Report

Report the review's outcome and any accepted `warning` violations, the draft path, the audience `findings.md` is written for, the included datasets, each chart with the result it serializes, provenance gaps, unresolved caveats, and the check's `unlinked_findings`. When `open_questions_count` exceeds five, report the count so the audience can review the longer slide. Say it is a working copy the next revision overwrites; marking it delivered freezes it as a numbered release. When a represented flagged finding lacks an applicable disposition, say `awb-release` will ask for one before releasing.

Tell the user how to build the deck: in a Microsoft 365 Copilot app chat, add the PowerPoint agent, attach `findings.md`, every file in `charts/`, `methodology.md`, `deck-rules.md`, and `assembly/m365.md`, and ask for a deck built under those instructions. Datasets travel beside the deck and are not attached.

## Delivery milestone

When the user marks the package delivered, finish any revision requested with it, then invoke the sibling [`awb-release`](../awb-release/SKILL.md).
