---
name: awb-package
description: "Draft or revise an analytics workbench delivery package: deck outline, charts, and selected datasets. Use only for requests such as \"make me slides\", \"prepare a deck\", or \"revise the package draft\"."
---

# Draft a delivery package

Run this skill's commands through the `awb` MCP tools when the host offers them, as the project's `AGENTS.md` **Commands** maps them; the command lines below are the fallback.

Packaging **serializes** recorded results: it reuses recorded evidence, exports, and provenance, and changed results come only from separately authorized analysis. Read the [package contract](references/package-contract.md) first: the layout, consistency rules, and commands. Bundled asset paths are relative to this `SKILL.md`.

## Sequence

1. **Establish** the investigation, package name, dataset selection, and Audience.
2. **Gather** the record on the read path the change needs.
3. **Write** a first pass of `findings.md` with its chart specifications, `methodology.md`, and any `methodology-note.md`, passing the headline checkpoint in its mode.
4. **Export the files and provenance** with `export` on every revision, which creates the draft folder; then fill in the display names and paste the `methodology_lines`, in that order, and review the flags.
5. **Review** the narratives with a read-only reviewer against every review rule.
6. **Check** last with `check-draft`, until done.
7. **Report.**

## 1. Establish

Identify the investigation and package. When the request corrects a draft in a way later drafts could repeat, first ask the user whether later drafts should be checked for it, saying in plain words what would be checked, and record it as a review rule only on their yes, as [references/review.md](references/review.md) says under **After the review**. When the request could refer to more than one investigation, ask which before changing package files. Use the package name the user gives, else the existing package's, else derive a short, stable one from the investigation and a purpose word and report it. Keep one package per investigation unless another has an independent scope or delivery schedule.

From the project root, install the missing shared formats with README's `Project interpreter`: `python3 <awb-init skill directory>/scripts/install_helpers.py . --package-formats`, which preserves existing files and records what it installs in `.awb-receipt.json`.

For a new package, ask which audience-facing datasets to include and explicitly offer **none**; there is no default export set. A revision keeps the current manifest's selection unless the user changes it or it no longer fits the package scope; when it no longer fits, explain why and ask for another before exporting.

Read the **Audience** section of the investigation's `brief.md`: who will see or present the deck, what they know, the decision they own, their terms, and any deck length or checkpoint mode. When it is missing or blank, ask the user, then record the answer there (after **Purpose** when absent) as record maintenance, as you do a deck length (such as about 8 slides), a precision, a methods note length in the template's `Methods note length: about <n> words` form, or a checkpoint mode the user states. When it or the request mentions a methods note, ask whether the audience needs `methodology-note.md`.

## 2. Gather the record

- **New draft or changed analytical scope or results:** read the investigation's `brief.md`, `state.md`, `history.md`, settings, `run.py`, and `producers/`; the relevant portions of `foundation/sources.md`, `catalog.md`, `quality.md`, and `glossary.md`; and any draft manifest and latest release.
- **Bounded narrative revision, including an omission or accepted caveat:** start with the current draft and manifest, the brief's **Audience**, current findings and flags in `state.md`, the requested change and the evidence, history, and foundation entries relevant to it, plus the latest release parts and date the changes slide needs. Expand to the other records above wherever scope, evidence, provenance, or consistency is missing or conflicting.

Recover the business question, intended decision or exploratory purpose, audience, usefulness criteria, and evidence the contract needs, with the data limitations and errors affecting interpretation.

Read the ledger with `python3 src/awb.py questions list --all` and each represented result's recorded settings `answers` to derive the storyline under the contract's **Ledger storyline** rules (pass `--investigation <name>` to commands for another investigation).

When a brief section names a ledger question ID, resolve it with that list. An `answered` question, `answered (provisional)` included, supplies its recorded text or linked result's value; `answered (awaiting recheck)` or `answered (provisional, awaiting recheck)` leaves it unsettled, as does any other status, missing ID, or failed lookup. The list prints each linked finding's status. When unsettled, ask only if the question is open and its answerer is `user`, recording the answer with `python3 src/awb.py questions answer Q-NNN --text "<answer>" --by "<the user>"` before writing; otherwise carry the unsettled element, including any usefulness criterion, in both narratives: in `findings.md` in the audience's words, naming its owner; its ID only in `methodology.md`'s **What makes the answer useful:** (or matching) line. Never present it as settled.

## 3. Write the draft

### The headline checkpoint

For each required question whose text is not in the audience's words, set audience wording with `python3 src/awb.py questions edit Q-NNN --audience "<wording>"`, leaving its text unchanged. A question the user wants on the **Open questions** slide that the decision does not need takes `--show`, leaving its priority. A new draft, or a changed storyline, passes the checkpoint in the first of these modes that applies: the mode the request states; **draft-then-review** when the request supplies the storyline or asks for the full draft; the mode the brief's **Audience** section records; **preview-and-wait**.

- **preview-and-wait**: write the title slide and every slide headline in storyline order, the conditional **Open questions** slide included, to `.preview/headlines.md` in the draft folder, which no check reads and no release copies; show them with the figures behind each headline that chat has not shown, and write the full slides once the user approves or reorders them.
- **draft-then-review**: write the full draft and finish the steps below; step 7 reports its headlines.

In either mode a consequential open choice, such as audience wording the user has not approved or an unsettled usefulness criterion, stops the draft before its full slides and is asked with the headlines. Offer an untested explanation as a question, never as a headline's claim. Promote each provisional finding behind an approved headline with `python3 src/awb.py state finding <result-id> --status supported --reason "<why>"`.

With the headlines, show the required questions as the slide words them, and say in one sentence that the deck opens with a title slide, then the answer slide, and that a headline holds at most 15 words. Before trimming a headline the user wrote or approved, ask: offer the shorter wording, or keeping theirs, recorded with their reason in the manifest's `accepted_long_headlines`. Report the main slides, title included, and appendix slides against any recorded length, proposing which move to the appendix when the main slides exceed it. Propose the ledger-derived finding order; record an order the user approves instead as the manifest's `presentation_order` once `export` has written it, leaving ledger priority and parent unchanged. A revision that keeps the storyline skips the checkpoint, but new audience wording needs the user's approval.

### Write the full slides

Write the draft at the contract's paths, or revise the same files: a first pass, which step 4 finishes. A draft in an earlier format is rewritten whole in the current format on its next revision; releases stay frozen.

- `findings.md` is the deck outline under the slide rules and translation rule in `package-format/findings-template.md`; its **Answer** slide is the executive summary.
- Order finding slides by `presentation_order`, the slide slugs `ledger_order` lists, when the manifest records one, otherwise under the contract's **Ledger storyline** rules, which also govern **Open questions**; slides the user agreed to move go under `## Appendix`. Report every finding with no linked ledger question.
- `methodology.md` follows `package-format/methodology-template.md` in the workbench's own vocabulary.
- When the audience needs one, `methodology-note.md` follows `package-format/methodology-note-template.md`.
- Copy `package-format/deck-rules.md` and `package-format/assembly/m365.md` unchanged to the same paths under the draft.
- Record facts a revision brings in that the investigation records lack, such as a limitation the user supplies, in its `history.md` as record maintenance, so no narrative states more than the records. When a review or the user corrects a claim a finding's text states, also reword that finding with `python3 src/awb.py state finding <id> --text "<corrected text>"` in the same revision.

## 4. Export the files and provenance

1. Run `python3 src/awb.py export <investigation> <package> --chart <result>[:<columns>][@first=<n>|@where=<column>=<value>,...] ... --dataset <name>=<result>[:<columns>] ... (or --no-datasets) --result <id> ...`, passing every represented result: one `--chart` per **Chart N.** specification, in order, exactly the user-selected datasets, and each other represented result as `--result`, which is recorded without the export check, so a flagged finding can be represented with its caveat. Choose columns so each file holds exactly what its chart plots, with interval bounds as their own columns, and select its rows in the `--chart`, such as `@first=10` for a top ten, rather than recording a new result. Display choices, such as the highlight or baseline, go in the specification.
2. Give each listed column without a display name one from the glossary: fill its `display_stub` under `[columns]` in `foundation/display.toml`, and paste its `round_stub` under `[round]`, replacing each `""` with the places the slide's number format shows, unquoted, such as `"share" = 1`. List fractions the slide shows as percents in `[percent]`'s `columns = [...]`, and name a column that means something else in another result under `[results."<id>".columns]`; a result whose column of that name already holds percents lists its own percent columns, even none, under `[results."<id>".percent]`. Fix any blank name or places it reports in place, and rerun. For each `label_warnings` column, confirm its name suits every result it labels, or name it for one result. **Data:** lines and dataset headers use these names.
3. Paste its `methodology_lines` into `methodology.md`, and repeat each of its `questions` verbatim in the methodology section of the finding that result supports.
4. For a revision that only adds caveats and keeps the exported files, pass only `--result`, once for every represented result; omit `--chart`, `--dataset`, and `--no-datasets`. A `check-draft` `charts` row that asks to rerun export needs the full export, with every `--chart`.
5. When `export` reports `exports_blocked`, stop and report it. When it reports missing evidence it writes nothing; stop, or rerun and restore, as **Missing evidence** in [helpers](references/helpers.md) says. Commit nothing on the user's behalf to make provenance look clean.

`export` records each flag's finding and reason and lists `flags_pending`. Review every flag's `represented_in` against the revised draft and fill pending places per the contract; then for any represented flag whose disposition is still `none`, ask the user to revalidate, omit, or release with the caveat, and record the answer, or leave it `none`.

## 5. Review

Once the narratives and flags are complete, run the review in [references/review.md](references/review.md): a fresh subagent, limited to read tools, checks the draft against the brief, every rule in `foundation/review-rules.md`, and what `check-draft` cannot check, and reports without fixing; that file's **Launch** says how each host starts it, right after `review-receipt start`. Record and act on its report as that file's **After the review** says; the first review of a draft is full, and later ones are scoped against the recorded one.

## 6. Check

Once every other draft file is final, run `python3 src/awb.py check-draft <investigation> <package>`. Repair the draft and rerun it; a long-headline `warning` row is asked about as the headline checkpoint says, never trimmed unasked. When a repair rewrites a sentence the user wrote, show them the new wording, and never call it their wording unless it is word for word theirs. A `note_length` row is a methods note over the brief's length: shorten it, or report its word count against that length.

A `numbers` row is a number no represented result records; its `problem` names the rule that applied. A `numbers` row on a `methodology.md` **Claim strength:** line the `claims` check refuses clears once that row is repaired: repair it first, never listing its numbers in `allowed_numbers`. Repair any other `numbers` row by the first of these that fits:

1. It comes from a recorded result the draft relies on but `export` was not given: rerun `export` passing that result too. `allowed_numbers` never stands in for representing a result.
2. A represented result records it at another value or precision: rewrite it from the recorded value. In another unit than its chart or dataset column, such as gigatonnes for megatonnes, it traces once that column has a `[scale]` divisor in `foundation/display.toml` and `export` reruns.
3. It is not a quantity, such as a date, a comparison year, a chart number, or a tool version: the check reports any number whose context leaves it in doubt, so reword where a context [helpers](references/helpers.md) lists would mark it, such as a comma after a date or year; otherwise, or when the records support it from elsewhere, such as an earlier release, a `history.md` entry, or a result's question `methodology.md` repeats, list it in the manifest's `allowed_numbers` as `package-format/manifest-template.md` describes.
4. It is computed from results that none records: only separately authorized analysis records it; until then, leave it out.

**Done** when `check-draft` prints `passed: true` on the final files and its `review` row is `current`, a passed review, full or scoped, of these files, which checks what `check-draft` cannot. Any edit after `check-draft` reruns it. Report its outcome.

## 7. Report

Report the review's outcome and any problems the user accepted, the package name, the draft path, the audience `findings.md` is written for, the main and appendix slide counts from `check-draft`'s `slides` against any recorded length, the included datasets, each chart by what it shows, unresolved caveats, and the check's `unlinked_findings`. Report a provenance gap, a manifest value recorded as `{"unknown": "<reason>"}` or a requirements line in a result's `unread_requirements`, as what went unrecorded, such as "one result's package versions were not recorded", or not at all when it changes nothing the user decides, such as an unrecorded packaging commit in a project without Git or without a commit yet. Suggest no commit in this report when you already suggested a commit this session. When `open_questions_count` exceeds five, report the count. In draft-then-review, list the slide headlines, marked provisional, with what the headline checkpoint shows beside them, and ask the user to approve or reorder them. Call `methodology.md` the internal methodology reference, and offer a `methodology-note.md` when the draft has none. Say it is a working copy the next revision overwrites; marking it delivered freezes it as a numbered release. When a represented flagged finding lacks an applicable disposition, say `awb-release` will ask for one before releasing.

Point the user to the draft's `START-HERE.md`: what to send the audience, what builds the deck in a Microsoft 365 Copilot app chat with the PowerPoint agent, and what stays internal.

## Delivery milestone

When the user marks the package delivered, invoke [`awb-release`](../awb-release/SKILL.md). A revision requested with it comes first: finish it, show the user the changed slides, and wait for their yes before invoking `awb-release`, unless they said to release without seeing it.
