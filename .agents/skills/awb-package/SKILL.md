---
name: awb-package
description: "Draft or revise an analytics workbench delivery package: deck outline, charts, and selected datasets. Use only for requests such as \"make me slides\", \"prepare a deck\", or \"revise the package draft\"."
---

# Draft a delivery package

Packaging **serializes** recorded results: it reuses recorded evidence, exports, and provenance, and changed results come only from separately authorized analysis. Read the [package contract](references/package-contract.md) first; it holds the layout, the consistency rules, and the commands. Bundled asset paths are relative to this `SKILL.md`.

## Sequence

1. **Establish** the investigation, package name, dataset selection, and Audience.
2. **Gather** the record on the read path the change needs.
3. **Write** `findings.md`, with every **Chart N.** specification, `methodology.md`, and any `methodology-note.md` from the project's templates, and copy the deck rules and assembly files, passing the headline checkpoint in its mode; a revision that keeps the storyline skips it.
4. **Export the files and provenance** with `export` on every revision, then review the flags.
5. **Review** the narratives with a read-only reviewer against every review rule.
6. **Check** last with `check-draft`, until done.
7. **Report.**

## 1. Establish

Identify the investigation and package. When the request corrects a draft the user is reviewing, record the correction as a review rule first when later drafts could repeat it, as [references/review.md](references/review.md) says under **After the review**. When the request could refer to more than one investigation, ask which before changing package files. Use the package name the user gives; otherwise reuse the existing package's name, or derive a short, stable one from the investigation and a purpose word and report it. Keep one package per investigation unless another has an independent scope or delivery schedule.

From the project root, install the missing shared formats with `python3 <awb-init skill directory>/scripts/install_helpers.py . --package-formats`, which preserves existing files and records what it installs in `.awb-receipt.json`.

For a new package, ask which audience-facing datasets to include and explicitly offer **none**; there is no default export set. A revision inherits the selection in the current manifest unless the user changes it or it no longer fits the package scope; when it no longer fits, explain why and ask for a new selection before exporting.

Read the **Audience** section of the investigation's `brief.md`: who will see or present the deck, what they already know, the decision they own, the terms they use, and any deck length or checkpoint mode. When it is missing or blank, ask the user, then record the answer there (adding the section after **Purpose** when absent) as record maintenance, as you do a length (such as about 8 slides) or checkpoint mode the user states. When it or the request mentions a methods note, ask whether the audience needs `methodology-note.md`.

## 2. Gather the record

- **New draft or changed analytical scope or results:** read the investigation's `brief.md`, `state.md`, `history.md`, settings, `run.py`, and `producers/`; the relevant portions of `foundation/sources.md`, `catalog.md`, `quality.md`, and `glossary.md`; and the existing draft manifest and latest release, when present. Changed results need recorded evidence from separately authorized analytical work before packaging.
- **Bounded narrative revision, including an omission or accepted caveat:** start with the current draft and manifest, the brief's **Audience**, current findings and flags in `state.md`, the requested change, and the evidence, history entries, and foundation entries relevant to it, plus the latest release portions and release date the changes slide needs. Expand to the rest of the brief, settings, `run.py` and `producers/`, earlier history, and foundation records wherever scope, evidence, provenance, or consistency is missing or conflicting.

Recover the business question, intended decision or exploratory purpose, audience, usefulness criteria, and evidence the contract needs, with the data limitations and errors that affect interpretation.

Read the ledger with `python3 src/awb.py questions list --all` and each represented result's recorded settings `answers` to derive the storyline under the contract's **Ledger storyline** rules (pass `--investigation <name>` to commands for another investigation).

When a brief section names a ledger question ID, resolve it with that list. An `answered` question supplies its recorded text or linked result's value; `answered (awaiting recheck)` leaves it unsettled, as does any other status, missing ID, or failed lookup. The list prints each linked finding's status. When unsettled, ask only if the question is open and its answerer is `user`, recording the answer with `python3 src/awb.py questions answer Q-NNN --text "<answer>" --by "<the user>"` before writing; otherwise carry the unsettled element, including any usefulness criterion, in both narratives: in `findings.md` in the audience's words, naming its owner; its ID only in `methodology.md`'s **What makes the answer useful:** (or matching) line. Never present it as settled.

## 3. Write the draft

### The headline checkpoint

For each required question whose text is not in the audience's words, set audience wording with `python3 src/awb.py questions edit Q-NNN --audience "<wording>"`, leaving its text unchanged. A new draft, or a changed storyline, passes the checkpoint in the first of these modes that applies: the mode the request states; **draft-then-review** when the request supplies the storyline or asks for the full draft; the mode the brief's **Audience** section records; **preview-and-wait**.

- **preview-and-wait**: write the title slide and every slide headline in storyline order, the conditional **Open questions** slide included, show them, and write the full slides once the user approves or reorders them.
- **draft-then-review**: write the full draft and finish the steps below; the step 7 report shows its headlines, marked provisional, for the user to approve or reorder.

In either mode a consequential open choice, such as audience wording the user has not approved or an unsettled usefulness criterion, stops the draft before its full slides and is asked in the same message as the headlines.

With the headlines, show the required questions as the slide words them, and say in one sentence that the deck opens with a title slide and then the answer slide. Report the main slides, title included, and the appendix slides against any recorded length, and when the main slides exceed it, propose which move to the appendix. Propose the ledger-derived finding order; record an order the user approves instead as the manifest's `presentation_order` once `export` has written the manifest, leaving ledger priority and parent unchanged. A revision that keeps the storyline skips the checkpoint, but new audience wording still needs the user's approval.

### Write the full slides

Create the draft at the contract's paths, or revise the same files. A draft in an earlier format is rewritten whole in the current format on its next revision; releases stay frozen.

- Before writing, give each column a chart or dataset will export a display name from the glossary in `foundation/display.toml`, e.g. `[columns]` then `return_rate = "Return rate"`, and the decimal places its slide shows under `[round]`; list fractions the slide shows as percents in `[percent]`'s `columns = [...]`, and name a column that means something else in another result under `[results."<id>".columns]`; a result whose column of that name already holds percents lists its own percent columns, even none, under `[results."<id>".percent]`. **Data:** lines and dataset headers use these names.
- `findings.md` is the deck outline under the slide rules and translation rule in `package-format/findings-template.md`; its **Answer** slide is the executive summary.
- Order finding slides by `presentation_order` when the manifest records one, otherwise under the contract's **Ledger storyline** rules, which also govern **Open questions**; slides the user agreed to move go under `## Appendix`. Report every finding with no linked ledger question, even though, without a `presentation_order`, its placement last passes the check.
- `methodology.md` follows `package-format/methodology-template.md` in the workbench's own vocabulary.
- When the audience needs one, `methodology-note.md` follows `package-format/methodology-note-template.md`.
- Copy `package-format/deck-rules.md` and `package-format/assembly/m365.md` into the draft unchanged, at the same paths under it.
- When a revision brings in facts the investigation records lack, such as a limitation the user supplies, record them in the investigation's `history.md` as record maintenance with the revision, so no narrative states more than the records.

## 4. Export the files and provenance

Run `python3 src/awb.py export <investigation> <package> --chart <result>[:<columns>][@first=<n>|@where=<column>=<value>,...] ... --dataset <name>=<result>[:<columns>] ... (or --no-datasets) --result <id> ...`, passing every represented result: one `--chart` per **Chart N.** specification, in order, exactly the user-selected datasets, and each other represented result as `--result`; a `--result` is recorded without the export check, so a flagged finding can be represented with its caveat. Choose columns so each file holds exactly what its chart plots, with interval bounds as their own columns, and select the rows it plots in the `--chart`, such as `@first=10` for a top ten, rather than recording a new result. Display choices such as the highlight or the baseline go in the specification. When it lists display-name or rounding gaps, fill its `display_stub` under `[columns]`, and paste its `round_stub` under `[round]`, replacing each `""` with the places the slide's number format shows, unquoted, such as `"share" = 1`; fix any blank name or places it reports in place, and rerun. For each `label_warnings` column, confirm its name suits every result it labels, or name it for one result. Paste its `methodology_lines` into `methodology.md`, and repeat each of its `questions` verbatim in the methodology section of the finding that result supports. For a revision that only adds caveats and keeps the exported files, pass only `--result`, once for every represented result; omit `--chart`, `--dataset`, and `--no-datasets`. A `check-draft` `charts` row that asks to rerun export needs the full export, with every `--chart`. When `export` reports `exports_blocked`, stop and report it. When it reports missing evidence it writes nothing, so the draft and its manifest stay as they were. If a result without evidence is serialized by a `--chart` or `--dataset`, or has an entry in the manifest's `export_checks` (`export` records one for every result a chart or dataset file serializes and keeps it while the result is represented), or if no `--result` in a `--result`-only run has evidence, stop and report it as for `exports_blocked`: only separately authorized analytical work restores the evidence, and dropping a chart, a dataset, or a recorded export check is the user's decision. Otherwise rerun it without those results. For each, the rerun drops only its `results` entry and its share of the producing state (the fields under **Producing state** in `package-format/manifest-template.md`); add both back by hand: the `results` entry with the `evidence` path `export` named, the `question` from the result's settings table, and its `runtime` copied from an earlier manifest's `results` entry, or `{"unknown": "evidence missing"}` when none records it, never read from the current interpreter; and the producing state from investigation records or an earlier manifest, never from the current checkout. While their evidence is missing, every later `export` run drops them again, so restore them after each. Commit nothing on the user's behalf to make provenance look clean.

`export` records each flag's finding and reason and lists `flags_pending`. Review every flag's `represented_in` against the revised draft and fill pending places per the contract; then for any represented flag whose disposition is still `none`, ask the user to revalidate, omit, or release with the caveat, and record the answer; without one it stays `none`.

## 5. Review

Once the narratives and flags are complete, run the review in [references/review.md](references/review.md): a fresh subagent, limited to read tools, checks the draft against every rule in `foundation/review-rules.md` and what `check-draft` cannot check, and reports without fixing; that file's **Launch** says how each host starts it. Act on its report as that file's **After the review** says. A review after repairs may be the scoped re-review that file describes, but the last review before the final `check-draft` is a full one.

## 6. Check

Once every other draft file is final, run `python3 src/awb.py check-draft <investigation> <package>`. Repair the draft and rerun it.

A `numbers` row is a number no represented result records. A `numbers` row on a `methodology.md` **Claim strength:** line that the `claims` check refuses clears once that `claims` row is repaired, so repair that row first and never list its numbers in `allowed_numbers`. Repair any other `numbers` row by the first of these that fits:

1. It comes from a recorded result the draft relies on but `export` was not given: rerun `export` as step 4 says, passing that result too. `allowed_numbers` never stands in for representing a result.
2. A represented result records it at another value or precision: rewrite it from the recorded value.
3. It is not a quantity, such as a date, a comparison year, a chart number, a tool version, or a week number: the check reports any number whose context leaves it in doubt, so reword where a context [helpers](references/helpers.md) lists would mark it, such as a comma after a date or year; otherwise, or when the records support it from elsewhere, such as a figure from an earlier release, a fact the user supplied that `history.md` records, or a number inside a result's question that `methodology.md` must repeat, list it in the manifest's `allowed_numbers` as `package-format/manifest-template.md` describes.
4. It is computed from results that none records: only separately authorized analysis records it; until then, leave it out.

**Done** when `check-draft` prints `passed: true` on the final files and the last review is a full review, passed and not stale, as [references/review.md](references/review.md) defines under **After the review**; that review confirms what `check-draft` cannot check, since `check-draft` proves only that each number is recorded somewhere. Any edit after `check-draft` reruns it. Report its outcome.

## 7. Report

Report the review's outcome and any accepted `warning` violations, the draft path, the audience `findings.md` is written for, the main and appendix slide counts from `check-draft`'s `slides` against any recorded length, the included datasets, each chart with the result it serializes, unresolved caveats, and the check's `unlinked_findings`. Report a provenance gap, a manifest value recorded as `{"unknown": "<reason>"}` or a requirements line in a result's `unread_requirements`, as what went unrecorded, such as "the Python version for one result was not recorded" or "one result's package versions were not recorded", or not at all when it changes nothing the user decides, such as an unrecorded packaging commit in a project without Git. When `open_questions_count` exceeds five, report the count so the audience can review the longer slide. In draft-then-review, list the slide headlines, marked provisional, with what the headline checkpoint shows beside them, and ask the user to approve or reorder them. Call `methodology.md` the internal methodology reference, and offer a `methodology-note.md` when the draft has none. Say it is a working copy the next revision overwrites; marking it delivered freezes it as a numbered release. When a represented flagged finding lacks an applicable disposition, say `awb-release` will ask for one before releasing.

Point the user to the draft's `START-HERE.md`: what to send the audience, the files to attach and the prompt that builds the deck in a Microsoft 365 Copilot app chat with the PowerPoint agent, and what stays internal.

## Delivery milestone

When the user marks the package delivered, invoke the sibling [`awb-release`](../awb-release/SKILL.md). A revision requested with it comes first: finish it, show the user the changed slides, and wait for their yes before invoking `awb-release`, unless they said to release without seeing it.
