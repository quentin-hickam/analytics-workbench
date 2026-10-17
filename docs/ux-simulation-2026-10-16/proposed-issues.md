# Issues from the 2026-10-16 re-run

The eleven issues below are filed as [#84](https://github.com/quentin-hickam/analytics-workbench/issues/84), [#85](https://github.com/quentin-hickam/analytics-workbench/issues/85), [#86](https://github.com/quentin-hickam/analytics-workbench/issues/86), [#87](https://github.com/quentin-hickam/analytics-workbench/issues/87), [#88](https://github.com/quentin-hickam/analytics-workbench/issues/88), [#89](https://github.com/quentin-hickam/analytics-workbench/issues/89), [#90](https://github.com/quentin-hickam/analytics-workbench/issues/90), [#91](https://github.com/quentin-hickam/analytics-workbench/issues/91), [#92](https://github.com/quentin-hickam/analytics-workbench/issues/92), [#93](https://github.com/quentin-hickam/analytics-workbench/issues/93), [#94](https://github.com/quentin-hickam/analytics-workbench/issues/94).

It turns the confirmed findings in the [comparison report](README.md) into PR-sized issues, the way the Oct 15 fix plan grouped its phases.
- **Included:** only findings that both skeptics confirmed as product defects. Where a skeptic narrowed a finding, the problem is stated in its narrower form.
- **Listed separately, not proposed:** contested findings, at the end under [Contested findings](#contested-findings-not-proposed-yet).
- **Left out:** rejected findings and harness findings. They are summarized in the report.

**Paths.** Release paths such as `awb-package/references/review.md:33` are relative to the release root. They match `.agents/skills/<skill>/` at `1db6084` line for line. `README.md:NN` refers to the release README, which drops the dist-excluded blocks. Evidence paths are written `SIMS/<run>/...`, where `SIMS` is the simulation folder that holds the report. In this repository the copied evidence is flattened: `SIMS/<run>/feedback/<file>` is `<run>/<file>`, `feedback/orchestrator-report.md` is `<run>/referee-report.md`, and `human/notes.md` is `<run>/human-notes.md`. Relay logs, project folders, storage and grading scripts were not copied; their figures are in `data.json`.

**IDs.** `C-NN` is a consolidated finding in `data.json`. Per-run IDs such as `taxi-B-01` are the IDs in each run's `findings.json`.

## Summary

| # | Issue | Severity | Closes | Runs |
|---|---|---|---|---|
| [1](https://github.com/quentin-hickam/analytics-workbench/issues/84) | Make the package review gate converge | major | C-01, C-15, C-17 | 6/6 |
| [2](https://github.com/quentin-hickam/analytics-workbench/issues/85) | Decide what the review checks: the brief, readability, tolerances and rules | major | C-06, C-10, C-11, C-33, C-70 | 6/6 |
| [3](https://github.com/quentin-hickam/analytics-workbench/issues/86) | Conversation: show answers before calling them answered, plain report rules, chat claims | major | C-02, C-04, C-18, C-30, C-45, C-58 | 6/6 |
| [4](https://github.com/quentin-hickam/analytics-workbench/issues/87) | Analysis discipline: reconciliation, thresholds, coverage, shared SQL, validation | major | C-07, C-14, C-20, C-41, C-53, C-56, C-62, C-75 | 5/6 |
| [5](https://github.com/quentin-hickam/analytics-workbench/issues/88) | check-draft reading and display values | major | C-09, C-22, C-23, C-24, C-34, C-39, C-55 | 6/6 |
| [6](https://github.com/quentin-hickam/analytics-workbench/issues/89) | Headline length limit and release-gate integrity | major | C-13, C-21 | 3/6 |
| [7](https://github.com/quentin-hickam/analytics-workbench/issues/90) | awb-package instructions, step order and package files | major | C-08, C-27, C-37, C-40, C-50, C-51, C-77, C-86 | 6/6 |
| [8](https://github.com/quentin-hickam/analytics-workbench/issues/91) | Setup interpreter, MCP routing and `awb sql` | major | C-03, C-05, C-16, C-43 | 6/6 |
| [9](https://github.com/quentin-hickam/analytics-workbench/issues/92) | Data landing, cleaning and source records | major | C-19, C-26, C-42, C-54, C-73, C-74, C-76, C-80 | 6/6 |
| [10](https://github.com/quentin-hickam/analytics-workbench/issues/93) | awb-status reports | minor | C-31, C-32, C-48, C-71, C-85 | 6/6 |
| [11](https://github.com/quentin-hickam/analytics-workbench/issues/94) | README | minor | C-25, C-72 | 6/6 |

All 58 confirmed findings are closed by exactly one issue.

## Conventions for every issue

- **One PR per issue,** reviewed by a fresh Codex reviewer and a fresh Opus reviewer before merge. Issue 11 is docs-only, so decide its review approach when it is opened rather than defaulting to that pair.
- **MCP reach.** Every changed helper argument or new command stays reachable over MCP through the existing `records`, `data`, `package`, `release` and `read` tools, with a case in `tests/test_awb_mcp.py`.
- **Design record.** A PR that changes accepted behavior updates the matching sentences of `docs/workbench-spec.md`, `docs/workbench-design.md` and `CONTEXT.md`, and adds a `CHANGELOG.md` fragment.
- **No migration.** No projects exist on any release yet.
- **Copilot.** Copilot was not used in this study. Where a fix rests on Copilot's approval model, cite its primary documentation and do not describe the behavior as tested.

---

## Issue 1: Make the package review gate converge ([#84](https://github.com/quentin-hickam/analytics-workbench/issues/84))

**Severity.** Major. It is the largest single cost in the study.

**Closes.** C-01, C-15, C-17.

**Problem.**
- **The loop does not end (C-01).** Four rules combine into a pass that must be rerun until it comes back clean:
  - any narrative problem blocks, and the user can accept only `warning` violations;
  - only a full review completes a request or a release, and a scoped re-review "never does";
  - any narrative edit makes the last review stale;
  - `awb-release` runs a fresh full review at every release request, even on a draft a clean review just passed.

  A fresh reviewer finds new wording items on each pass, so every repair restarts the cycle. Agents skip the scoped re-review because it can never finish anything.
- **Verdicts are not stable (C-17).** Rules with no pattern are "judged by reading", and the same reviewer brief gives different verdicts on unchanged text. The gate treats one clean pass as final, so it cannot tell a real problem from reviewer variance.
- **The user cannot settle it, and release repairs go out unseen (C-15).** A narrative problem on text the user approved cannot be waived with the user's consent. Repairs forced by the release review are made and frozen into the numbered release in the same turn. #64's show-the-changed-slides rule covers only revisions the user requested.

**Evidence.**
- **taxi-B:** 21 full reviews in total, 15 of them in reply 5 (58.5 minutes, $21.71, 61% of agent cost).
  - Logs: `SIMS/taxi-B/relay/agent-005.jsonl`; snapshots `SIMS/taxi-B/agent-home/scratch/review-1` to `review-17`; `taxi-B-01`.
  - In reply 7, the first release review raised R-rates-001 on a Newark line that the previous clean review had passed. The agent rewrote it, trimmed approved note lines to meet a word warning, and released (`SIMS/taxi-B/relay/agent-007.jsonl`; `SIMS/taxi-B/transcript.md`).
- **co2-B:** 38 full reviews across A4 to A8. A4 to A8 took 129.5 of 142.9 minutes and $44.12 of $48.38 (`co2-B-01`).
  - The A8 release review flagged "every country behind the rankings", which A7's final review had passed. It was changed and released in the same turn: compare `review-copy/findings.md:158` with `released/001/findings.md:160` under `SIMS/co2-B/project/deliveries/co2-cuts-growth-consumption/donor-briefing/`.
  - Six review-driven edits followed the user's request to stop unrelated wording changes (`co2-B-02`). Reviewers also gave contradictory guidance across passes (`co2-B-05`).
- **retail-B:** 15 full reviews; the drafting turn took 40.4 minutes and $11.86, 57% of agent cost (`retail-B-01`).
  - In `SIMS/retail-B/relay/agent-005.jsonl`, R-concentration-001 passed in four consecutive full reviews of the approved France/Australia headline, then failed in the next. The text was unchanged and the reviewer prompt was identical to the pass before.
- **retail-A:** four full reviews, including a release re-review of a candidate a clean review had passed (`retail-A-02`).
- **co2-A:** six full reviews: snapshots 001 to 004 in one turn (`co2-A-06`), 005 after the user's corrections, and `release-001` at release (`SIMS/co2-A/agent-home/.cache/awb-reviews/donor-roundtable/`).
- **taxi-A:** a `.tmp` snapshot for every review (`taxi-A-15`).

**Cause in the release.**
- `awb-package/references/review.md:33`: a review passes only with no narrative problem and every warning accepted; a scoped re-review "never does" complete a request or release.
- `awb-package/references/review.md:35`: a review goes stale after any narrative change and runs again.
- `awb-package/references/review.md:37`: a full review is still required before the final `check-draft`, and "awb-release always runs the full review".
- `awb-package/references/review.md:18` and `:21`: report every problem "in this one pass"; rules with no pattern are judged by reading.
- `awb-package/SKILL.md:74` and `:87`: Done requires a full review that passed and is not stale.
- `awb-package/SKILL.md:97`: changed slides are shown first only for "A revision requested with it".
- `awb-release/SKILL.md:18`: a full review at the start of every release request, never scoped, with no earlier report kept; a narrative problem stops the release and is repaired within the request.

**Fix direction.**
1. **Review receipt.** Record a clean full review as a receipt keyed by a hash of the narratives and the rules file. `awb-release` reuses a receipt that still matches instead of reviewing again. When the draft changed since the receipt, it reviews the changes.
2. **Let a scoped re-review complete a request** after one full review in that request, when it covers the diff, the prior report's problems and every rule added since, and comes back clean. This is the change #66 stopped short of.
3. **Cap the rounds.** After two full reviews in one request, stop and show the user the remaining narrative problems with a recommendation. The user may accept a narrative problem with a recorded reason, as they can a warning.
4. **Stable verdicts.** Pass the reviewer the prior report. A new problem on a line an earlier pass judged clean, with the line unchanged, needs a stated reason and goes to the user rather than restarting the loop. Ask for a pattern, or an explicit check list, when a rule is judged only by reading.
5. **Show release-time repairs.** Any repair made inside `awb-release` is shown to the user as changed slides before `release` runs, as #64 already does for requested revisions.

**Files.** `awb-package/references/review.md`; `awb-package/SKILL.md` (review step, Done, delivery milestone); `awb-release/SKILL.md` (step 2); `awb-package/assets/awb-package-reviewer.agent.md`; `awb-package/assets/awb_draft.py` (receipt write and verify, likely beside `review-rules check`); `awb-package/references/helpers.md`; tests.

**Acceptance checks.**
- `tests/test_awb_review.py`:
  - a receipt written after a clean review verifies against unchanged narratives and fails after an edit;
  - an accepted narrative problem is recorded with its reason.
- `tests/test_skill_surface.py`:
  - `awb-release/SKILL.md` reuses a matching receipt;
  - it shows release-time repairs before running `release`;
  - `review.md` no longer says a scoped re-review "never" completes a request.

**Depends on.** Nothing. Merge before Issues 2 and 7, which also edit `review.md` and `awb-package/SKILL.md`.

---

## Issue 2: Decide what the review checks: the brief, readability, tolerances and rules ([#85](https://github.com/quentin-hickam/analytics-workbench/issues/85))

**Severity.** Major.

**Closes.** C-06, C-10, C-11, C-33, C-70.

**Problem.**
- **The review never reads the brief (C-11).** Step 3 checks that the narratives agree, that claims are not too strong, that caveats are carried, and that "checked" sentences cite a check. It does not check that each part of each question is on a visible slide, that standing requirements in the brief are met, or that a claim about how a source is built is documented. `check-draft`'s `questions` check only confirms that `methodology.md` repeats each question.
- **"With its tolerance" pushes technical numbers into audience text (C-10).** Every "checked" sentence in `findings.md` and the note must state a tolerance. There is no exception for an exact check, or for a check with no tolerance set beforehand. The templates show "within 0.5%" on the slide, and the `state finding` warning suggests adding a tolerance after the fact.
- **Review rules are written on the agent's judgment alone (C-06).** The agent decides whether a correction becomes a rule, records it in the project-wide `foundation/review-rules.md` before repairing, and reports an ID. Nothing asks the user, nothing scopes a rule to one package, and nothing says which rule wins when two conflict. The rule's `Scope` field sets only how much text one violation covers.
- **No pass for readability (C-33).** Undefined terms, display precision beyond what the audience needs, and record or imperative wording pass both `check-draft` and the review. Step 4 tells the reviewer to report exactly the listed checks "and nothing else". Repairs made for consistency can spread a misleading label.
- **Methods-note length is never checked (C-70).** The template says "a page or two". Nothing compares the note with a length the brief records; the only length reported is the slide count.

**Evidence.**
- **C-11:**
  - taxi-A: Q3's hour and borough detail sat only in speaker notes, and the draft passed two full reviews (`SIMS/taxi-A/project/.tmp/package-review-2`; msg 7 correction 1; `taxi-A-01`).
  - taxi-B: the note grew from 770 to 867 words across 15 reviews against "one-page methodology note" in the brief. Base fare was defined as the meter's fare, though flat JFK fares drive key findings (`SIMS/taxi-B/agent-home/scratch/review-15/methodology-note.md`; `taxi-B-02`).
  - co2-B: a review accepted "the world total leaves out China's and India's emissions in them too", and `DQ-008` still carries it (`co2-B-04`).
- **C-10:**
  - taxi-A: "with zero-record tolerance" is on the released appendix slide after the user removed it from the note (`SIMS/taxi-A/storage/releases/taxi-trip-patterns/board-decisions/001/findings.md:127`; `taxi-A-08`).
  - co2-B: the agent invented a 0.15 Mt tolerance after observing a 0.13 Mt maximum gap. Its notes say it "had to invent a 0.15 tolerance", and it put the figure in a visible bullet after U5 asked for notes only (`co2-B-07`, `co2-B-08`).
  - retail-B: filter retention ratios (90%, 95%, 50%, 3%) appeared on the How we know slide until U6 (`retail-B-04`).
- **C-06:**
  - taxi-A: four rules were saved unasked, three of them beginning "For this board study" (`taxi-A-09`).
  - co2-A: four rules were saved unasked, and `R-consumption-001` hard-codes this deck's directions (`co2-A-09`).
  - taxi-B: `R-rates-001` and `R-methodology-note-001` collided on one line (`taxi-B-22`; `SIMS/taxi-B/project/foundation/review-rules.md`).
  - co2-B: `R-periods-001` forced a long combined Answer caveat (`co2-B-06`).
- **C-33:**
  - taxi-A msg 7, corrections 2 to 5: "other located trips", an unexplained "occupied hour", $106.28 labels, arrow headlines.
  - co2-A U5 item 2: "territorial" undefined.
  - retail-A U6 items 4 to 6: control-group wording, imperative bullets, an undefined repeat-buyer metric (`retail-A-12`).
  - retail-B: review repairs introduced "three largest buyers" and "count as one buyer" (`SIMS/retail-B/relay/agent-005.jsonl`; U6).
- **C-70:** taxi-B's report called an 867-word note "a one-page methodology note" (`SIMS/taxi-B/transcript.md`, reply 5).

**Cause in the release.**
- `awb-package/references/review.md:18-22`: the brief gives the reviewer the rules output, the narratives and `revalidation_flags`, never `brief.md`. Step 3 holds the agreement, claim-strength, tracing and check-citation items, ending with "the check in plain words, with its tolerance".
- `awb-package/references/package-contract.md:48`: the same tolerance rule for the writer.
- `awb-package/assets/package-format/findings-template.md:66` and `methodology-note-template.md:29`: "totals reconcile to the finance ledger within 0.5%".
- `awb-init/assets/workbench/workbench-guides/analysis.md:17`: the `state finding` warning's fix says to state the check "with its tolerance".
- `awb-package/references/review.md:39` and `awb-package/SKILL.md:22`: the agent decides and records a rule before repairing, with no user step.
- `awb-package/assets/awb_draft.py:3543-3546`: `Scope` sets violation granularity only.
- `awb-package/assets/package-format/findings-template.md:15`: overflow goes "into the notes".
- `awb-package/references/helpers.md:36`: the `questions` check matches `methodology.md` only.
- `awb-package/assets/awb_draft.py:2484`: "Known limits: this compares rendered text, not paraphrases or audience suitability."
- `awb-package/assets/package-format/methodology-note-template.md:7`: "Keep it to a page or two".
- `awb-package/SKILL.md:28`, `:52` and `:91`: a recorded length is reported as slide counts only.

**Fix direction.**
1. **Give the reviewer the brief.** Add three checks:
   - every part of each required question is on a visible slide, not only in notes;
   - the note meets a length the brief records;
   - a claim about how a source builds a series cites documentation or a recorded check.
2. **Narrow the tolerance rule.**
   - Ask for a tolerance only where the check had one set before the data was seen.
   - Accept "exactly" or "every row" for exact checks.
   - Keep tolerances in `methodology.md` and speaker notes, and drop "within 0.5%" from the slide and note examples.
   - Say that a tolerance chosen after seeing the result is not a tolerance.
3. **Make rules the user's.**
   - Ask the user before saving a correction as a standing rule.
   - Allow a package-scoped rule stored with the package.
   - Warn when a rule's text names this draft's figures or entities.
   - State precedence: an `error` rule wins over a `warning`, and a conflict the reviewer cannot settle goes to the user.
4. **A narrow readability item in step 3:** a term the glossary defines but the slide does not; precision finer than the audience's stated needs; record vocabulary or imperative voice in audience text. Each is quoted with its line.
5. **Note length.** Record a note length in the brief's Audience when the user gives one (for example "one page, about 500 words"). `check-draft` reports the note's word count against it as a warning row.

**Files.** `awb-package/references/review.md`, `package-contract.md`, `helpers.md`; `awb-package/assets/package-format/findings-template.md`, `methodology-note-template.md`; `awb-package/SKILL.md`; `awb-package/assets/awb_draft.py` (`review-rules add`, the note length row); `awb-init/assets/workbench/investigation/brief.md`; `awb-init/assets/workbench/workbench-guides/analysis.md`; `awb-init/assets/awb_provenance.py` (warning text); tests.

**Acceptance checks.**
- `tests/test_awb_draft.py`: a note over the recorded length yields a warning row; with no recorded length, no row.
- `tests/test_awb_review.py`: `review-rules add` without the user-confirmation flag refuses, or records the rule as unconfirmed; a package-scoped rule applies only to its package.
- `tests/test_skill_surface.py`:
  - `review.md` step 3 reads `brief.md`;
  - no template example puts a tolerance on a slide;
  - `review.md:39` asks the user before recording a rule.

**Depends on.** Issue 1, for the `review.md` edits.

---

## Issue 3: Conversation: show answers before calling them answered, plain report rules, chat claims ([#86](https://github.com/quentin-hickam/analytics-workbench/issues/86))

**Severity.** Major.

**Closes.** C-02, C-04, C-18, C-30, C-45, C-58.

**Problem.**
- **"Answered" before the user has seen the answer (C-04).** `run.py` marks a ledger question answered as soon as a result declares it, even while the finding is provisional or hangs on an open user decision. The footer counts that status. The headline checkpoint shows headlines, required questions and slide counts, but not the evidence. `AGENTS.md` says to summarize helper output. The result: "5 answered" and a request for headline approval while chat showed only leaders or summaries.
- **Report rules require internal IDs (C-02).**
  - `review.md` says "Report the new ID".
  - `awb-package` asks for each chart with the result it serializes.
  - `awb-clean` asks for the recorded issues with their quality IDs.
  - The provenance-gap rule drops a gap only "when it changes nothing the user decides", and its one example is "a project without Git", so agents report a packaging-commit gap for a Git repository with no commit in package and release reports.
  - `AGENTS.md:28` lets an ID "sit beside plain text".

  Commit hashes, shell-slip narration and agent-invented interim report files are agent habit. The plain-words rule exists but loses to these report checklists.
- **Untested explanations in chat (C-18).** The rule "offer an untested explanation as a question, not an answer" is one sentence among the analytical invariants. It is not repeated where chat answers, headline previews or cleaning proposals are written. `awb-clean` files `duplicate-rows` as "a row landed twice" and requires a proposed treatment, which invites "double-scanned, remove them".
- **Chat figures change base without notice (C-45).** Nothing asks the agent to name the denominator of a share in chat, or to say when a figure's base changes between replies.
- **Commit reminders repeat (C-30).** The guides carry "unless you already suggested a commit this session". The `awb-status` "Commit the current work" row and the package and release provenance reports do not.
- **The scoping cap bundles unrelated choices (C-58).** At most four decisions per round, plus "ask every open decision before writing the records", leads agents to nest unrelated method choices under one number.

**Evidence.**
- **C-04:**
  - co2-A A2 footer "5 answered with stated caveats", then U3 "I need the actual answers in chat" (`co2-A-03`).
  - retail-A A2 "5 answered · next: headline feedback", then U3 (`retail-A-01`).
  - taxi-B reply 3 "5 answered (provisional), with 2 decisions from you open", then msg 4 (`taxi-B-07`, `taxi-B-10`).
  - co2-B A2 figures for 3 of 20 Q1 countries (`co2-B-09`).
  - retail-B A2 without the 24 monthly figures (`retail-B-09`).
- **C-02:**
  - Replies with rule IDs and commit hashes: taxi-A replies 6 and 7 (`taxi-A-10`). Replies with rule IDs: co2-A replies 3 and 5 (`co2-A-08`).
  - retail-A reply 7 "No packaging Git commit exists; producing-file checksums are recorded" (`retail-A-15`).
  - retail-B commit hashes in A6 and A7, and narration in interim lines (`retail-B-07`).
  - taxi-A interim report files in record vocabulary (`taxi-A-07`); co2-B fingerprints (`co2-B-24`); taxi-B shell narration (`taxi-B-08`).
  - The taxi-B and retail-B interim narration is partly a harness effect (C-66 in the report).
- **C-18:**
  - retail-B A2: "probably Christmas-season buyers", growth "spread across many accounts", "double-scanned ... remove them".
  - retail-B A3: early cohorts "overstated".
  - retail-B A4: a preview headline asserting concentration "at home" (`retail-B-02`, `retail-B-10`).
  - taxi-B reply 2: code-0 totals "undercount", disproved in reply 3 (`taxi-B-11`).
- **C-45:**
  - taxi-B: code-0 share 6.9% of all records, then 4.02% and 8.85% of screened trips; 54 zones, then 53.
  - co2-B A2: "219 entities with a code, plus Kosovo" (218 plus Kosovo) (`co2-B-25`).
- **C-30:**
  - co2-B mentioned commits in A1, A2, A3, A4 and A8 (`co2-B-10`).
  - retail-B suggested a commit in A2, A3 and A5. Its A3 line came word for word from the status row, against the agent's own note "not repeating".
- **C-58:** co2-B A1 item 4 and retail-B A1 item 4 each bundled three unrelated thresholds or definitions (`SIMS/co2-B/feedback/agent-notes.md`; `SIMS/retail-B/feedback/agent-notes.md`).

**Cause in the release.**
- **C-04:** `awb-init/assets/workbench/AGENTS.md:32` (footer counts ledger roots); `awb-init/assets/awb_provenance.py:1551` and `:2253-2279` (`link_answers` marks declared questions answered on record); `awb_provenance.py:2089-2100` (only flagged or superseded findings change the displayed status); `awb-init/assets/workbench/workbench-guides/analysis.md:17` and `investigation/run.py:15-16`; `AGENTS.md:28`; `awb-package/SKILL.md:47-52`.
- **C-02:** `awb-package/references/review.md:39`; `awb-package/SKILL.md:91`; `awb-release/SKILL.md:55`; `awb-clean/SKILL.md:75`; `awb-package/assets/awb_draft.py:2895-2897` and `:3955` (an unknown packaging commit in a repository with no commit is reported as a gap); `AGENTS.md:28` and `:30`.
- **C-18:** `AGENTS.md:38` (the only statement of the rule); `README.md:83` (the promise to users); `awb-clean/SKILL.md:26` and `:31`.
- **C-45:** `AGENTS.md:26-32` (no rule on the base of a chat figure) and `:40`.
- **C-30:** `awb-status/SKILL.md:65`; `awb-package/SKILL.md:91`; `awb-release/SKILL.md:55`. The guard exists at `awb-init/assets/workbench/workbench-guides/data.md:11`, `:33` and `analysis.md:17`. The promise is at `README.md:109` and `AGENTS.md:48`.
- **C-58:** `awb-scope/SKILL.md:25` and `:42`; `awb-init/SKILL.md:46` and `:50`.

**Fix direction.**
1. **Answered means shown.**
   - The footer counts a question answered only once its figures have appeared in chat. Before that it says "results ready, not yet shown", or the turn shows them.
   - Alternatively, `run.py` records `answered (provisional)` until the finding is promoted, and the footer reports that status.
   - In preview-and-wait, the headline checkpoint shows the figures behind each headline when chat has not.
2. **Plain report rules.**
   - Replace "Report the new ID" with "say in plain words what later drafts will be checked for".
   - Report charts by what they show; report cleaning issues in plain words, with IDs kept in the files.
   - Treat a Git repository with no commit like a project without Git for the packaging-commit gap, or report it once as "no version saved yet".
   - Drop the `AGENTS.md:28` allowance for an ID beside plain text in user-facing replies.
3. **Move the claim rules to where chat is written.**
   - Add the untested-explanation rule, and "name the base of every share in chat and say when it changes", to the Conversation section.
   - Repeat the explanation rule at the headline checkpoint.
   - In `awb-clean`, describe `duplicate-rows` as a repeat to be explained, not "a row landed twice", and propose a treatment without asserting a cause.
4. **One commit reminder per session.** Add the same "unless you already suggested a commit this session" guard to the `awb-status` row and to the package and release reports.
5. **Scoping rounds.** Count a decision as one choice; do not nest unrelated choices under one number. Use a second round instead, or let the cap rise to five when every item has a recommendation.

**Files.** `awb-init/assets/workbench/AGENTS.md` (Conversation, footer); `awb-init/assets/awb_provenance.py` (`link_answers` status, if the provisional route is chosen); `awb-init/assets/workbench/investigation/run.py`; `awb-package/SKILL.md` (checkpoint, report); `awb-package/references/review.md:39`; `awb-release/SKILL.md` (report); `awb-clean/SKILL.md` (classes, report); `awb-status/SKILL.md` (commit row); `awb-scope/SKILL.md` (pacing); `awb-package/assets/awb_draft.py` (`provenance_gaps`); tests.

**Acceptance checks.**
- `tests/test_skill_surface.py`:
  - the Conversation section holds the untested-explanation and base rules;
  - no skill says "Report the new ID";
  - every commit suggestion in the skills carries the once-per-session guard.
- `tests/test_awb_draft.py`: a manifest with `packaging_commit {"unknown": "the checkout has no commit yet"}` in a repository with no commit yields no provenance gap, or one gap with the plain wording.
- `tests/test_awb_findings.py`: if the provisional route is chosen, a result that declares `answers` marks its question `answered (provisional)` until promoted.
- `tests/test_measure_instruction_load.py`: the always-loaded `AGENTS.md` grows by no more than the lines it drops.

**Depends on.** Issue 1 for `review.md` and the `awb-package/SKILL.md` report wording. Merge before Issue 8, which also edits `AGENTS.md`.

---

## Issue 4: Analysis discipline: reconciliation, thresholds, coverage, shared SQL, validation ([#87](https://github.com/quentin-hickam/analytics-workbench/issues/87))

**Severity.** Major.

**Closes.** C-07, C-14, C-20, C-41, C-53, C-56, C-62, C-75.

**Problem.**
- **Reconciliation surfaces only at packaging (C-07).**
  - Validation records any omitted spec key as "not assessed". The default producer measures nothing, and the guide lets an unassessed check stand with a caveat.
  - No standard reconciliation (input equals kept plus excluded) or coverage check is suggested when results are written.
  - #66's review then requires every "checked" or "reconciles" sentence to cite a result ID or evidence path, without saying whether a foundation quality record or an exploration query counts.
  - So agents add checks late, file them under questions they do not answer, rerun and re-export.
- **Thresholds after results (C-14).** The guide has no rule that a threshold, minimum or exclusion the brief does not settle is the user's decision, or that it should be fixed before looking at which rows lead. `awb-explore` lets the agent make question-specific exclusions itself and only "say so".
- **Per-entity coverage of summed series (C-20).** Exploration checks coverage for the whole dataset. Validation checks nulls only in the result frame, where `SUM()` hides missing years. Nothing requires a coverage shortfall the agent computed to become a caveat.
- **No investigation-local shared SQL (C-41).** Sessions load only `foundation/views`. Exploration copies every scope filter into each query, and `[eda] where` cannot read `$parameters`. A rerun is matched by exact SHA-256, so DuckDB's parallel float sums can change a table between runs. The guide also never shows how to import a helper module from the investigation folder.
- **`validate.py` crashes on an incomplete joins spec (C-53).** It reads `join["left_rows"]` unchecked and raises `KeyError` for each result. The settings template never says the key is required.
- **The `views` key accepts anything (C-75).** `run.py` passes `config.get("views")` straight to evidence recording. A logical view name is recorded as a missing file with a null checksum, so the run passes and only `stale` complains later.
- **Commit, rerun, commit (C-56).** A result run before the first commit records `producing_commit: "uncommitted"`, and it still counts as current after a commit. Nothing says that only a rerun after the commit records the commit, so provenance repair is found by reading the manifest.
- **Records drift from the release (C-62).** When review corrects a claim in the package, the skill sends only new facts to `history.md`. The finding text in `state.md` keeps the old claim, and a later revision starts from it.

**Evidence.**
- **C-07:**
  - taxi-B: all 17 `state.md` finding rows read "not assessed: row_counts, joins", the record-reconciliation result included. The methods note told the board counts and joins were not checked, and msg 6 asked for a reconciliation (`taxi-B-03`).
  - co2-B: the review refused an exploration-query citation (`SIMS/co2-B/relay/agent-004.jsonl`), and the agent built `world-reconciliation` and `q4-missing-years` under Q-004's question text (`co2-B-16`; `settings.toml:128-142`).
  - retail-B: commits `6fb0cc2`, `c18e2e7` and `c1e1393` came after acceptance; human.md: "I expected basic totals to have been reconciled already" (`retail-B-05`).
  - taxi-A: the first full review failed on two missing check citations (`SIMS/taxi-A/feedback/agent-notes.md`).
- **C-14:**
  - taxi-B reply 3: "With the current minimum of 1,000 trips". Msg 4: "I hadn't agreed to the 1,000-trip minimum". `history.md:131` admits it. Reply 3 also recommended a 10,000-trip minimum and dropping rate-code-99 trips after seeing them lead (`taxi-B-04`).
  - taxi-A: single-trip zones led a top ten until the user set a floor (`taxi-A-12`).
- **C-20:** co2-B: `years_with_data` of 118 and 156 of 175 were computed in A2 (`SIMS/co2-B/relay/agent-002.jsonl`) with no caveat. A5 then wrote "count as zero" from a reviewer's wording, and U6 challenged it (`co2-B-03`).
- **C-41:**
  - taxi-B: a 20-line screening CTE in 17 query files, with the same rules as literals in `[eda] where` (`taxi-B-13`).
  - retail-B: `sys.path.insert` added to five producers (`retail-B-18`).
  - taxi-A: `SET threads=1` was needed to keep float tails stable (`taxi-A-19`; `SIMS/taxi-A/feedback/agent-notes.md`).
- **C-53:** co2-B and retail-B tracebacks through `validate.py:124` (`co2-B-12`, `retail-B-17`).
- **C-75:** taxi-A: `views = ["yellow_trips","taxi_zones"]` passed the run, then `stale` reported a missing sha256 for all four results (`SIMS/taxi-A/relay/agent-002.jsonl`; `taxi-A-14`).
- **C-56:** co2-B release 001 records `producing_commit` "uncommitted" (`co2-B-11`). retail-B committed, reran all eight results for provenance, re-exported and committed again (`retail-B-16`).
- **C-62:** taxi-B `findings.json:66` and `:131`, `state.md` lines 13 and 17 (findings rows) and line 36 (an Unresolved issues bullet) still say "Monday to Wednesday", "one holiday" and "all record zero tips", where release 001 says otherwise (`taxi-B-05`).

**Cause in the release.**
- **C-07:**
  - `awb-init/assets/awb_validate.py:182-183` (an absent key is recorded as not assessed) and `:120` (only the last step's counts);
  - `awb-init/assets/workbench/investigation/run.py:52-54` (the default producer measures nothing);
  - `awb-init/assets/workbench/investigation/settings.toml:31-41`;
  - `awb-init/assets/workbench/workbench-guides/analysis.md:11`, `:13` and `:17`;
  - `awb-package/references/review.md:22` and `package-contract.md:48` (citation forms; foundation scans not mentioned).
- **C-14:** `analysis.md:9-17` ("Add a result" has no user-decision rule); `awb-explore/SKILL.md:49`. Compare `awb-clean/SKILL.md:31` and `awb-scope/SKILL.md:42`, which do have it.
- **C-20:** `awb-explore/SKILL.md:50`; `awb-explore/references/reading-the-scan.md:11-17`; `awb-explore/scripts/eda_scan.py:332-358` (coverage counted for the whole dataset); `awb-init/assets/awb_validate.py:140` (`_nulls` on the result frame).
- **C-41:** `run.py:37` and `:82-88`; `awb-init/assets/awb_landing.py:1156-1159` (only `foundation/views` loaded); `awb-explore/SKILL.md:41`; `eda_scan.py:108-131` (no parameter substitution in `[eda] where`); `awb-init/assets/awb_provenance.py:1436-1454` (exact-hash rerun match).
- **C-53:** `awb_validate.py:124`; `settings.toml:33`; `run.py:97-102`.
- **C-75:** `run.py:122-123`; `awb_provenance.py:633-690` (`result_problems` has no views check) and `:95-96` (a missing file is recorded with null bytes and checksum).
- **C-56:** `awb_provenance.py:779-781`, `:861` and `:941`; `awb-status/scripts/collect_status.py:847-849`.
- **C-62:** `awb-package/SKILL.md:64` (history only) and `:33` (later revisions read `state.md`).

**Fix direction.**
1. **Standard checks at analysis time.**
   - Ship a stock reconciliation helper that a producer can call (input rows, kept rows, excluded rows by rule) and that fills `row_counts`.
   - Have `analysis.md` suggest it for every filtered population, and suggest a per-entity coverage check for every series summed over a period.
   - Say in `review.md` which citations count for a "checked" sentence: a result ID, an evidence path, or a foundation quality ID with its scan.
   - Keep "not assessed" caveats out of audience text unless the user should act on them.
2. **Thresholds are the user's.** In `analysis.md` "Add a result": a threshold, minimum or exclusion the brief does not settle is proposed to the user before looking at which rows lead, and one proposed after seeing results says so. Align `awb-explore/SKILL.md:49` with that rule.
3. **Coverage shortfalls become caveats.** A computed coverage count below the period length is recorded as a caveat on the finding. `awb-explore`'s coverage step covers each entity in scope for summed measures.
4. **Shared SQL.**
   - Load `investigations/<name>/views/*.sql` after the foundation views, and count them as producing code for results that read them.
   - Let `[eda] where` read `$parameters`.
   - Show the import form for a helper in the investigation folder.
   - Pin DuckDB to one thread in result sessions, or compare floats at a stated tolerance on rerun.
5. **Clear validation errors.** `validate()` raises a `ValueError` naming the missing `joins` key. The settings template marks `left_rows` as required unless a producer supplies it.
6. **Validate `views`.** Each entry must be an existing file under `foundation/views/`. Document the key in the settings template.
7. **Say what a commit changes.** In `analysis.md` and `awb-package`: results run before the first commit stay "uncommitted" until rerun after it. `awb-status` lists results whose evidence predates the first commit. The package report says so in one plain line.
8. **Keep records in step.** When a review or the user corrects a claim that a finding's text states, reword the finding with `state finding --text` in the same revision, not only in `history.md`.

**Files.** `awb-init/assets/workbench/workbench-guides/analysis.md`, `data.md`; `awb-init/assets/workbench/investigation/run.py`, `settings.toml`; `awb-init/assets/awb_validate.py`, `awb_provenance.py`, `awb_landing.py` (session views); `awb-explore/SKILL.md`, `references/reading-the-scan.md`, `scripts/eda_scan.py`; `awb-package/SKILL.md` (records step, report); `awb-package/references/review.md` (citation forms); `awb-status/scripts/collect_status.py` (pre-commit evidence); `awb-init/references/validation.md`, `provenance.md`; tests.

**Acceptance checks.**
- `tests/test_awb_validate.py`:
  - a joins spec without `left_rows` raises a `ValueError` naming it;
  - the stock reconciliation helper fills `row_counts`.
- `tests/test_awb_provenance.py`:
  - a `views` entry that is not a file is refused at run time;
  - a file under `investigations/<name>/views/` counts as producing code for a result that reads it.
- `tests/test_awb_explore.py`: `[eda] where` with `$start` reads the settings parameter.
- `tests/test_awb_status.py`: a result produced before the first commit is listed as needing a rerun after a commit.
- `tests/test_skill_surface.py`: `analysis.md` "Add a result" states the threshold rule.

**Depends on.** Issue 2 for the `review.md` citation sentence. Otherwise independent.

---

## Issue 5: check-draft reading and display values ([#88](https://github.com/quentin-hickam/analytics-workbench/issues/88))

**Severity.** Major.

**Closes.** C-09, C-22, C-23, C-24, C-34, C-39, C-55.

**Problem.**
- **Ordinary notation reads as untraced numbers (C-09).** Slash pairs, clock times, identifier pairs, citation years and years followed by a word are reported as numbers that trace to nothing. The behavior is documented and fails safe. It still cost repeated failed preflights and rewording of sound prose. The year rule itself is consistent; an apparent inconsistency came from coincidental tracing.
- **Sentences that deny causation are refused (C-34).** The claims regex matches "causes", "caused", "effect on" and "attributable to" with no negation handling, and reads the note's Limitations section at full claim strength. One agent then told the user a rewritten caveat was "in your wording".
- **CO₂ labels fail chart checks (C-22).** The narrative is NFKC-normalized before the **Data:** fields are read, but the CSV headers are compared raw, so "CO₂" never matches.
- **No display-only unit rescale (C-23).** A number written in another unit than the recorded one cannot trace. The only route is a new column in a saved query, a rerun and a re-promotion.
- **Double rounding passes (C-24).** A share saved at 4 decimals is rounded again on export. The tracing window includes its edges, so 52.5% traces to 0.5245, and export's "unrounded" test treats a 4-place fraction as already rounded.
- **`display.toml` feedback gaps (C-55).** `label_warnings` repeats on every export with no way to record that a shared name was confirmed. A boolean value key (`true = "Yes"`) silently matches nothing, because pandas saves `True`.
- **Chart-spec wording (C-39).** "leave a blank line between them and the slide's next bullet" reads as "a blank line between fields". A blank line ends the fields, so check-draft counts the rest as slide bullets, and its message never mentions the chart.

**Evidence.**
- **C-09:**
  - taxi-A: the `numbers` rows for 264/265, 54.8/57.6, 18:00 and 18:59 in `SIMS/taxi-A/relay/agent-006.jsonl` (`taxi-A-02`).
  - retail-A: a `state finding` warning on "2011" and `check-draft` rows for "2012" and "368/53.5%" (`retail-A-03`).
  - retail-B: an `allowed_numbers` entry for "2011" (`retail-B-25`).
  - co2-B: "1907" (`co2-B-21`).
- **C-34:**
  - co2-A "attributable to" at `methodology-note.md:36` in review snapshots `SIMS/co2-A/agent-home/.cache/awb-reviews/donor-roundtable/001/` and `002/`, reworded before release (`co2-A-18`).
  - co2-B "does not test what caused them" (`co2-B-21`).
  - retail-B "the effect on repeat rates is unknown", rewritten and then called "in your wording" (`retail-B-15`).
  - taxi-B "not trends or causes", and "waiting and driving" (`SIMS/taxi-B/relay/agent-005.jsonl`).
- **C-22:** co2-A "chart-1.csv has no column 'Change in annual CO2 (Mt)'" for five charts (`SIMS/co2-A/relay/agent-004.jsonl`; `co2-A-04`). A skeptic reproduced it against the release helper.
- **C-23:** co2-A rows for "13.41 billion", "11.38 billion" and "2.32 billion". Gt columns were added to `ranking-groups` and `coal-share-change`, which were rerun and re-promoted (`co2-A-05`).
- **C-24:** retail-B: `round(x, 4)` in queries (`SIMS/retail-B/relay/agent-002.jsonl`). `check-draft` passed five times with 63.2% and 52.5%. A reviewer then flagged "63.2% comes from rounding the stored 0.6315 a second time", and the fix was `sed 's/, 4)/, 8)/g'` and a full rerun (`agent-005.jsonl`; `retail-B-03`).
- **C-55:** taxi-A: the same `source_month`/"Month" warning across five results on every export (`SIMS/taxi-A/relay/agent-006.jsonl`, `agent-007.jsonl`). co2-B: `[values.large] true = "Yes"` matched nothing (`co2-B-19`).
- **C-39:** taxi-B, co2-B and retail-B each got a "keep it to 5" bullet-count row on every finding slide ("10 bullets" in taxi-B and co2-B, "11 bullets" in retail-B-14) (`taxi-B-15`, `co2-B-17`, `retail-B-14`).

**Cause in the release.**
- **C-09:** `awb-package/assets/awb_draft.py:1319-1347` (year and time contexts) and `:1386-1396` (digits joined across `/` and `:`); `awb-package/references/helpers.md:39-44`.
- **C-34:** `awb_draft.py:1145-1150` (`_CAUSAL`), `:1286-1305` (the note read whole; `_wording` refuses every match below causal); `awb-package/references/package-contract.md:49`.
- **C-22:** `awb_draft.py:253` (NFKC in `_rendered`) against `:2199-2216` (raw CSV headers, exact match).
- **C-23:** `awb_draft.py:1404` (`_SCALES`, powers of ten only) and `:1574-1589` (`_traces`); `helpers.md:45` (no unit transform in `display.toml`); `awb-package/SKILL.md:85` (repair rule 4).
- **C-24:** `awb_draft.py:1569-1581` (`_within`'s inclusive comparison and the half-unit window), `:3104-3115` (`_display_cell` rounds saved text again); `awb-init/assets/workbench/workbench-guides/analysis.md:9-15` (no precision guidance).
- **C-55:** `awb_draft.py:3251-3265` (`label_collisions`, no confirmed state), `:3013-3016` (no key for a confirmation), `:3104-3107` and `:3224-3231` (exact label match; no report of unmatched keys); `awb-init/assets/workbench/investigation/run.py:120` (`to_csv` writes `True`).
- **C-39:** `awb-package/assets/package-format/findings-template.md:19`; `awb_draft.py:1853` (a blank line ends the fields) and `:2023` (the bullet-count message).

**Fix direction.**
1. **Numbers.**
   - Read `a/b` as two numbers when both sides are numbers, and trace each.
   - Skip 24-hour `HH:MM` times.
   - Skip a four-digit year after a month name or inside a citation `(YYYY)`.
   - Keep failing safe on everything else. Make the row name the rule that applied, and point to `allowed_numbers`.
2. **Claims.**
   - Skip a causal word inside a negated clause.
   - Exempt the note's Limitations section, as the deck's Limitations slide already is.
   - Add a line to the package skill: never tell the user a rewritten sentence is in their wording.
3. **NFKC.** Normalize CSV headers the same way before comparing, or compare raw text on both sides.
4. **Display unit scale.** A `[scale]` table in `display.toml` (for example `change_mt = { divide = 1000 }`), recorded in the manifest's chart entry. Export writes scaled values, and `numbers` traces a narrative figure against the recorded value divided by the scale.
5. **Rounding.**
   - `analysis.md` says to save full precision in result queries and round only for display.
   - Export warns when a fraction column holds exactly four decimals and a percent display would round it again.
   - Tracing treats the exact edge of a rounded recorded value as untraced.
6. **`display.toml`.**
   - A `[confirmed]` list of shared column names that silences their `label_warnings`.
   - A warning when a `[values]` key matches no cell.
   - A sentence that keys match the saved text exactly (`"True"`).
7. **Chart specs.** Reword `findings-template.md:19` to "no blank line between fields, and one blank line after the last field". When a field-shaped bullet is counted as a slide bullet, the outline row names the chart.

**Files.** `awb-package/assets/awb_draft.py`; `awb-package/references/helpers.md`, `package-contract.md`; `awb-package/assets/package-format/findings-template.md`; `awb-package/SKILL.md`; `awb-init/assets/workbench/workbench-guides/analysis.md`; tests.

**Acceptance checks.**
- `tests/test_awb_draft.py` (numbers):
  - "54.8/57.6" traces when both values are recorded;
  - "18:00" and "December 2011 is" are not rows;
  - an untraced figure still is.
- `tests/test_awb_draft.py` (claims): "does not test what caused them" is not a row; "drove the increase" still is.
- `tests/test_awb_charts.py`:
  - a "CO₂" header matches a "CO₂" **Data:** role;
  - a blank line inside a spec yields an outline row naming the chart.
- `tests/test_awb_draft.py` (export):
  - `[scale]` divides, is recorded, and a scaled narrative number traces;
  - a 4-decimal fraction shown as a percent warns;
  - an unmatched `[values]` key warns;
  - a `[confirmed]` name silences its label warning.

**Depends on.** Issue 2 for `package-contract.md`. Merge before Issues 6 and 7, which also edit `awb_draft.py`.

---

## Issue 6: Headline length limit and release-gate integrity ([#89](https://github.com/quentin-hickam/analytics-workbench/issues/89))

**Severity.** Major.

**Closes.** C-13, C-21.

**Problem.**
- **A hidden hard cap (C-13).** `HEADLINE_WORDS = 15` makes any longer headline an outline error. Outline rows block Done and `release`, and only review-rule warnings can be accepted. The limit is written only for the agent: the README says "one-sentence headline", and the headline checkpoint never mentions it. Agents trimmed headlines the user had approved and told the user only afterwards.
- **A locally altered gate can release (C-21).** To keep the user's 21-word headline, the co2-A agent edited the installed `src/packaging/draft.py` (the outline check and the START-HERE generator) and two templates, adding a `headline_length_exceptions` field. Release 001 then passed a gate that differs from what the installer wrote.
  - `AGENTS.md` and `helpers.md` allow adapting helpers, with no exception for checks that gate release and no rule to tell the user.
  - Only the installer reads `.awb-receipt.json`, and only on upgrade.
  - With no commits, `packaging_uncommitted_changes` lists every file as untracked, so the change is not singled out.

  On an interactive host the user would see the file edit, so "undisclosed" is softer there. Nothing in the release detects it.

**Evidence.**
- **C-13:**
  - co2-A: slashes in A3, a clause dropped in A4, then in A5 "Your exact headline exceeds the template's word limit" after the user restored their wording. The human feedback says "a template word limit I had never heard of" (`co2-A-01`; `SIMS/co2-A/feedback/human.md`).
  - co2-B A5: "To fit your wording within the 15-word headline limit, I dropped ..." (`SIMS/co2-B/transcript.md`).
  - taxi-B reply 5: "Headline wording was tightened from the version you approved" (weaker evidence).
- **C-21:** the SHA-256 of `SIMS/co2-A/project/src/packaging/draft.py`, `package-format/findings-template.md` and `manifest-template.md` differ from `.awb-receipt.json`. `draft.py:1980` reads `headline_length_exceptions`, and release 001's manifest carries the exception (`co2-A-02`).

**Cause in the release.**
- **C-13:** `awb-package/assets/awb_draft.py:1772`, `:2019-2020` (the error row), `:2624-2626` (`_structure_passed` needs no outline rows) and `:4072` (`release` refuses otherwise); `awb-package/references/review.md:33-35` (only warnings can be accepted); `awb-package/assets/package-format/findings-template.md:14`; `package-contract.md:45`; `helpers.md:28`; `README.md:11` and `:66-70`; `awb-package/SKILL.md:43-52`.
- **C-21:** `awb-init/assets/workbench/AGENTS.md:24` ("open one's source only to adapt or debug it"); `awb-package/references/helpers.md:3`; `awb-init/scripts/install_helpers.py:302-317` (the receipt is read only by the installer); `awb-package/assets/package-format/manifest-template.md:34`.

**Fix direction.**
1. **Make headline length acceptable by the user.**
   - Turn a headline over 15 words into a warning-severity outline row that the user can accept, recorded in the manifest with a reason, or keep 15 as a default the user can raise per package.
   - State the limit at the headline checkpoint, and say so before trimming a user's wording.
   - Add the limit to the README (Issue 11).
2. **Detect helper drift.**
   - `check-draft` and `release` compare every installed helper and package-format file with `.awb-receipt.json` and report a `helper_drift` row per changed file.
   - `awb-release` shows the rows and asks the user to confirm, and the manifest records the confirmation.
   - `AGENTS.md`: changing a helper or template that gates release needs the user's yes, asked in plain words.

**Files.** `awb-package/assets/awb_draft.py` (outline severity, drift check, release); `awb-package/SKILL.md` (checkpoint); `awb-package/references/helpers.md`, `package-contract.md`; `awb-package/assets/package-format/findings-template.md`, `manifest-template.md`; `awb-release/SKILL.md`; `awb-init/assets/workbench/AGENTS.md`; `awb-init/scripts/install_helpers.py` (a shared receipt reader); tests.

**Acceptance checks.**
- `tests/test_awb_outline.py`: a 21-word headline yields a warning row; an accepted one passes `check-draft` and `release`.
- `tests/test_awb_draft.py`: editing the project's `src/packaging/draft.py` yields a `helper_drift` row naming it, and `release` refuses until it is confirmed.
- `tests/test_skill_surface.py`: the headline checkpoint states the word limit.

**Depends on.** Issue 5, for `awb_draft.py`.

---

## Issue 7: awb-package instructions, step order and package files ([#90](https://github.com/quentin-hickam/analytics-workbench/issues/90))

**Severity.** Major (C-08); the rest minor.

**Closes.** C-08, C-27, C-37, C-40, C-50, C-51, C-77, C-86.

**Problem.**
- **Long, overlapping instructions (C-08).**
  - `awb-package`'s `SKILL.md`, package contract, review reference and helpers reference total about 11,700 words. The helpers reference alone is about 30 KB.
  - Step 4 opens with a single 3,089-character paragraph.
  - The preview-mode rules appear in several places.
  - The scoped re-review procedure is elaborate yet can never complete a request.

  Agents on both hosts found it too long. Most packaging time still went to the review loop (Issue 1), not to reading.
- **Export sits awkwardly in the step order (C-27).** Step 3 writes the narratives and asks for display names before writing, but only step 4's export prints the display stubs and the `methodology_lines` to paste. Run before the draft folder exists, export refuses with "no draft at ...; create it with awb-package", naming the skill the agent is already running.
- **Preview-and-wait has no defined file or state (C-37).** The skill says to "write the title slide and every slide headline ... show them", with no location. The draft inventory freezes every file in the folder, and START-HERE lists only known files. Status reports the expected missing manifest as a gap.
- **The default storyline and its upkeep (C-40).**
  - A finding slide ranks by the best question among all results its methodology section cites, supporting ones included.
  - Plain words that happen to be result IDs, such as "monthly", count as citations.
  - No command previews the derived order.
  - `presentation_order` keys on heading text, so it is hand-edited whenever a heading changes.
- **START-HERE contradicts itself (C-50).** Part 2 tells the builder to attach `methodology.md` and `deck-rules.md`; part 3 lists both as "Internal: keep these, and do not send them".
- **Release folders nest unexplained names (C-51).** The copy goes to `<location>/<investigation>/<package>/<n>/`. Nothing asks the user for, or tells them, the investigation slug. The package name appears only inside paths because step 7's report does not repeat step 1's "report it". The README explains the layout only under How it works.
- **Open questions membership is tied to `must` priority (C-77).** The slide lists exactly the unanswered `must` questions, and `must` means "the decision cannot be made without its answer". Showing a non-gating question the user asked for means marking it `must`.
- **"One `###` slide per finding" (C-86).** The README glossary calls a finding "a checked result", and `state.md` writes one row per result. The contract, however, expects a finding slide to rest on several results.

**Evidence.**
- **C-08:** `taxi-A-03` (headline preview 5.7 minutes, full draft 16.6 minutes), `co2-A-22`, `retail-B-24`, and `SIMS/taxi-B/feedback/agent.md` section 2 (snapshots "mostly wasted").
- **C-27:** the "no draft at" refusal in `SIMS/taxi-B/relay/agent-005.jsonl`, `SIMS/co2-B/relay/agent-004.jsonl` and `SIMS/retail-B/relay/agent-005.jsonl` (`taxi-B-16`, `co2-B-18`, `retail-B-13`). taxi-A and retail-A exported before writing the chart specs (`taxi-A-16`, `retail-A-27`).
- **C-37:** taxi-A `preview-plan.md` (`taxi-A-04`). co2-A `headline-preview.md`, with question and result IDs, inside `SIMS/co2-A/storage/releases/co2-country-priorities/donor-roundtable/001/` and its manifest inventory (`co2-A-12`). retail-A status reported "Draft lacks manifest.json" at the preview stage (`retail-A-23`).
- **C-40:** co2-A "move it to finding position 5" (`co2-A-17`). co2-B hand-edits to `presentation_order` in A4 to A7 (`co2-B-20`). retail-A expected order shifted by the plain words "monthly" and "concentration" (`retail-A-25`).
- **C-50:** both released START-HERE files (`co2-A-11`, `retail-A-19`). The co2-A user asked for a fix in U5 item 4.
- **C-51:** `co2-A-16`, `retail-A-18`. Only co2-B of six runs stated its package name in chat.
- **C-77:** taxi-A: `questions edit Q-009 --priority must` to put Vendor 6 on the slide, with `history.md:143` explaining it is not a funding gate (`SIMS/taxi-A/relay/agent-006.jsonl`).
- **C-86:** retail-B combined two results on one slide twice and doubted whether that was allowed (`SIMS/retail-B/feedback/agent-notes.md`, turn 4).

**Cause in the release.**
- **C-08:** `awb-package/SKILL.md:68` (step 4), `:45` with `awb-package/references/package-contract.md:39` (the checkpoint rules repeated), `awb-package/references/review.md:33` and `:37` (the scoped procedure).
- **C-27:** `awb-package/assets/awb_draft.py:3282-3284` and `:2645` (the refusal); `awb-package/SKILL.md:58` (names before writing) against `:68` (export output to paste); `package-contract.md:21`.
- **C-37:** `awb-package/SKILL.md:47`; `package-contract.md:7-19` (the draft layout); `awb_draft.py:1690-1694` (inventory of every file) and `:2580-2620` (START-HERE lists known files); `awb-status/scripts/collect_status.py:422-423`.
- **C-40:** `awb_draft.py:2390-2405` (ranking), `:702-709` and `:1186-1190` (plain-token citations); `package-contract.md:33-35`; `awb-package/assets/package-format/manifest-template.md:49`; `awb-package/SKILL.md:52`.
- **C-50:** `awb_draft.py:2596-2609`.
- **C-51:** `awb_draft.py:4045`; `awb-package/SKILL.md:22` and `:91`; `awb-scope/SKILL.md:55`; `README.md:29` against `:137`.
- **C-77:** `awb-package/assets/package-format/findings-template.md:82`; `awb_draft.py:2489-2492` and `:2536-2541`; `awb-scope/SKILL.md:38`.
- **C-86:** `findings-template.md:50`; `README.md:98`; `awb-init/assets/workbench/investigation/state.md:14`; `package-contract.md:49`.

**Fix direction.**
1. **Shorter instructions.**
   - Split step 4 into numbered sub-steps.
   - State the preview-mode rules once.
   - Move the evidence-restoring procedure in step 4 to `helpers.md`.
   - Delete the scoped re-review procedure if Issue 1 replaces it.
   - Set a word budget for `SKILL.md` and test it.
2. **Step order.**
   - Export creates the draft folder when it is missing.
   - Step 3 becomes a first pass, and the `methodology_lines` and display names are filled in after export, said in that order.
   - The refusal message names the missing step instead of the skill.
3. **A defined preview.** Preview headlines go in a named file outside the inventory (for example `draft/.preview/headlines.md`), which `check-draft` and `release` skip. Status reports "headline preview awaiting approval" instead of a missing manifest.
4. **Storyline.**
   - Rank a slide by its primary result only: the first result its methodology section cites, or a `Primary:` line. Supporting citations do not move it.
   - Count a result ID as cited only in backticks or a citation form.
   - Print the derived order in `check-draft` output.
   - Key `presentation_order` on a stable slide slug, so a reworded heading keeps its place.
5. **START-HERE.** List `methodology.md` and `deck-rules.md` once, as files for the builder only, and title part 3 "Internal: keep these; do not send them to the audience".
6. **Names and paths.**
   - `awb-scope`'s report names the investigation folder it created.
   - `awb-package` step 7 repeats the package name.
   - The release report prints the full storage path.
   - The README's What you get section names the layout (Issue 11).
7. **Open questions membership.** A ledger flag such as `show: true`, separate from priority, puts a non-gating question on the slide.
8. **Terms.** `findings-template.md:50` says one `###` slide per finding slide, which may present several recorded results. The README glossary separates a recorded finding from a finding slide.

**Files.** `awb-package/SKILL.md`; `awb-package/references/package-contract.md`, `helpers.md`, `review.md`; `awb-package/assets/package-format/findings-template.md`, `manifest-template.md`; `awb-package/assets/awb_draft.py` (export folder, inventory skip, storyline, START-HERE, release report); `awb-status/scripts/collect_status.py` (preview state); `awb-scope/SKILL.md` (report); `awb-init/assets/awb_provenance.py` (ledger flag); tests.

**Acceptance checks.**
- `tests/test_awb_draft.py`:
  - export with no draft folder creates it;
  - a file under `.preview/` is not inventoried;
  - START-HERE lists `methodology.md` once.
- `tests/test_awb_outline.py`:
  - a supporting citation does not move a slide in the derived order;
  - the bare word "monthly" in prose is not a citation of result `monthly`;
  - a reworded heading keeps its `presentation_order` slot.
- `tests/test_awb_questions.py`: a `should` question with `show: true` appears on Open questions.
- `tests/test_awb_status.py`: a preview-only draft reports the preview state, not a missing manifest.
- `tests/test_skill_surface.py`: `awb-package/SKILL.md` stays under its word budget.

**Depends on.** Issues 1 and 6, which edit the same skill text and `awb_draft.py`.

---

## Issue 8: Setup interpreter, MCP routing and `awb sql` ([#91](https://github.com/quentin-hickam/analytics-workbench/issues/91))

**Severity.** Major.

**Closes.** C-03, C-05, C-16, C-43.

**Problem.**
- **Setup records the MCP server's Python (C-03).**
  - The MCP `setup` tool takes no interpreter argument. On a fresh project, with no README line and no `.venv`, it runs the installer under the server's own interpreter, which the README tells admins to keep outside any project venv.
  - The installer records that interpreter as the Project interpreter. Once it is recorded, a run under a new `.venv` is refused until the README is edited by hand.
  - `awb-init` never says to create the project venv before setup, or that the MCP `setup` tool on a fresh project runs the installer under the server's own interpreter and records that one.
  - #65 fixed the Oct 15 bare-`python3` failures and the uv hint, but moved the trap into setup.
- **Helpers run through the terminal instead of MCP (C-05).**
  - `AGENTS.md:20` prefers MCP in one sentence. `AGENTS.md:24` then says "Run workbench helpers with `python3 src/awb.py <command>`".
  - The skills, guides and references spell about 85 commands in CLI form, `analysis.md:17` runs `run.py` directly, and `review.md` tells Claude Code reviewers to use Bash.
  - The Claude agents used MCP only where `AGENTS.md` maps a skill script to an MCP command.

  On a host that cannot auto-approve terminal calls, each CLI call needs approval. That is inferred from Copilot's documented approval model; it was not tested.
- **`awb sql` cannot bind parameters, and its refusal points the wrong way (C-16).**
  - `cli_sql` takes only `--limit`, `--out` and `--read-only`, and the MCP read tool always passes `--read-only` with no parameter input. A saved result query that uses settings `$parameters` cannot be tried.
  - Under `--read-only`, any EXPLAIN failure, including an ordinary binder error, is reported as "run it without --read-only". Dropping it fixes neither case.
  - A missing relative `.sql` path is parsed as SQL text.
- **Storage lines at setup (C-43).** The README tells users to name storage folders in the first message. `awb-init` never mentions the README's "Landed data is kept at" and "Released packages are kept at" lines. Only the data guide and `awb-release`, read later, say to record them, and no text gives the accepted forms.

**Evidence.**
- **C-03:**
  - All three Codex runs recorded `<python-prefix>/bin/python3`, which lacks duckdb, then built a venv and edited the README by hand. co2-A hit "README's Project interpreter is <python-prefix>/bin/python3, not this interpreter" (`SIMS/taxi-A/relay/agent-001.jsonl`; `taxi-A-06`, `co2-A-24`, `retail-A-21`).
  - All three Claude runs guessed the order or bypassed MCP setup (`taxi-B-23`, `retail-B-21`, `co2-B-22`).
- **C-05:** Bash helper calls against MCP calls (main thread, counting Bash calls that run `src/awb.py` or `run.py`): taxi-B 89 to 10, co2-B 83 to 32, retail-B 70 to 10 (`SIMS/<run>/relay/agent-*.jsonl`; `retail-B-28`). All three agents gave habit and output piping as reasons in `feedback/agent.md`. taxi-A (Codex) made about 126 MCP calls against about 11 CLI calls.
- **C-16:**
  - retail-A: "Values were not provided for the following prepared statement parameters: cohort_end, ...; run it without --read-only" (`SIMS/retail-A/feedback/agent-notes.md`; `retail-A-04`).
  - co2-A: an ambiguous `year` binder error got the same advice (`SIMS/co2-A/relay/agent-003.jsonl`; `co2-A-07`).
  - retail-B: `sql --help` shows no parameter option, and "syntax error at or near queries" came from a missing relative path (`retail-B-19`).
- **C-43:** all three Claude agents filled the lines by hand at init and noted the ownership was unclear (`SIMS/taxi-B/feedback/agent-notes.md`, `SIMS/retail-B/feedback/agent-notes.md`, `SIMS/co2-B/feedback/agent-notes.md`).

**Cause in the release.**
- **C-03:** `awb-init/assets/awb_mcp.py:191-205` (the setup schema has no interpreter key), `:318-319` (`_python` falls back to `sys.executable`) and `:399-405`; `awb-init/assets/awb_cli.py:161-174`; `awb-init/scripts/install_helpers.py:196-245` and `:209-212`; `awb-init/SKILL.md:32`; `README.md:176-179` and `:196`.
- **C-05:** `awb-init/assets/workbench/AGENTS.md:20` against `:24` (and `:7`); `awb-init/assets/workbench/workbench-guides/analysis.md:17`; `awb-package/SKILL.md:68` and `:78`; `awb-release/SKILL.md:22` and `:24`; `awb-status/SKILL.md:42-49`; `awb-package/references/review.md:9-10` and `:18`; `README.md:198`.
- **C-16:** `awb-init/assets/awb_landing.py:1287-1301` (the refusal), `:1519-1533` (`cli_sql` arguments) and `:1488-1497` (a missing path treated as SQL); `awb-init/assets/awb_mcp.py:345-351`; `awb-init/assets/workbench/investigation/run.py:46-49`; `AGENTS.md:24`.
- **C-43:** `awb-init/SKILL.md:26-37`; `awb-init/assets/workbench/README.md:9` and `:11`; `README.md:46` and `:64`; `awb-init/assets/workbench/workbench-guides/data.md:27`; `awb-release/SKILL.md:14` and `:47`; `awb_landing.py:853-878` (the unwritten form rule).

**Fix direction.**
1. **Interpreter.**
   - Add an `interpreter` argument to the MCP `setup` tool.
   - On a fresh project with no venv, `awb-init` step 3 creates a project `.venv` before setup, or asks once, and says which interpreter setup records.
   - When the interpreter setup would record lacks the required packages and sits outside the project, setup reports that and records nothing.
   - The refusal message names the one-line README edit.
2. **MCP first in practice.**
   - `AGENTS.md:24` says to run helpers through the awb MCP tools when the host offers them, with `python3 src/awb.py` as the fallback.
   - `analysis.md:17` routes `run.py` through `awb/run`.
   - Each skill's command block names its MCP tool and command beside the CLI form.
   - `review.md` lets Claude Code reviewers use the MCP read tool.
3. **`awb sql`.**
   - Add `--param name=value`, and `--settings <investigation>` to bind from settings `[parameters]`, to `cli_sql` and the MCP read `sql` input.
   - On an EXPLAIN failure, return the DuckDB error with the likely fix (bind the parameters, qualify the column), and never suggest dropping `--read-only`.
   - A path that ends in `.sql` and does not exist is reported as a missing file.
4. **Storage lines.** `awb-init` step 3 fills both README lines when the user names locations, and states the accepted forms (absolute, `~`, or relative to the project).

**Files.** `awb-init/assets/awb_mcp.py`, `awb_cli.py`, `awb_landing.py`; `awb-init/scripts/install_helpers.py`; `awb-init/SKILL.md`; `awb-init/assets/workbench/AGENTS.md`, `README.md`, `workbench-guides/analysis.md`, `data.md`; the command blocks in `awb-package`, `awb-release`, `awb-status`, `awb-clean`, `awb-explore`; `awb-package/references/review.md`; `README.md` (admin section); tests.

**Acceptance checks.**
- `tests/test_awb_mcp.py`:
  - `setup` with `interpreter` records that path;
  - `setup` on a fresh project whose server interpreter lacks duckdb records nothing and says why;
  - `read sql` binds `--param`.
- `tests/test_awb_landing.py`:
  - an unbound parameter under `--read-only` returns the binder message without "without --read-only";
  - a missing `.sql` path reports a missing file.
- `tests/test_awb_install.py`: a venv created after a recorded interpreter gets the README-edit hint.
- `tests/test_skill_surface.py`:
  - `AGENTS.md` makes MCP the first route for helpers;
  - `analysis.md` names `awb/run`.

**Depends on.** Issue 3, which also edits `AGENTS.md`.

---

## Issue 9: Data landing, cleaning and source records ([#92](https://github.com/quentin-hickam/analytics-workbench/issues/92))

**Severity.** Major (C-19); the rest minor.

**Closes.** C-19, C-26, C-42, C-54, C-73, C-74, C-76, C-80.

**Problem.**
- **Duplicates across sheets or extracts go unseen, and who decides is unclear (C-19).**
  - The duplicate-rows scan groups by every column, so lineage columns such as `sheet` and `sheet_row`, the natural key for an invoice-line workbook, make every row unique.
  - No step checks for overlapping sheets, files or partitions.
  - `awb-clean` lets the agent fix `duplicate-rows` "under a recorded grain", but leaves "whether repeated rows ... are errors and which row wins" to the user. An exact cross-sheet copy fits neither clearly.
- **`eda_scan.py` fails on an integer year (C-54).** `--start` and `--end` build `CAST(<column> AS DATE)`, which fails on an integer `year`. Only DATE and TIMESTAMP columns count as temporal, so panel data gets no coverage or trend output.
- **The quality writer cannot amend an observation (C-42).** A decision keyed by quality ID revises only judgment cells, and a `new` entry with corrected text adds a second row. A withdrawn claim stays in the observation. `awb-clean/SKILL.md:69` tells the agent to add a `findings` string even when no view changed.
- **The source register's reference grammar (C-26).** The template spends about 340 words on parser internals to describe two reference forms. `land` rewrites a hand-kept Status cell. Status lists a source with no reference without saying why.
- **`datasets.toml` shows only one-line inline tables (C-73).** TOML forbids line breaks inside an inline table. A long `types` table wrapped across lines fails with a raw parser message, and the subtable form is never shown.
- **The upstream probe cannot check sources without validators (C-74).** It needs an ETag or Last-Modified header, and the UCI server sends neither, so the source can never be checked. Status reports this honestly; it is a capability gap.
- **No form for documentation that cannot be retained (C-76).** The register accepts only a retained copy, or a location with a checksum. A dictionary that was read but could not be saved (HTTP 403) has no supported note. Neither does a dictionary revision later than the data.
- **A failed publish leaves a partial folder silently (C-80).** The refusal prints only the partial path, and a retry is refused while it exists. Only `landing.md`, which the CLI path never routes to, says to clear it.

**Evidence.**
- **C-19:**
  - retail-B scanned with `--key sheet,sheet_row`, and its baseline lists no duplicate issue (`SIMS/retail-B/project/foundation/scans/online_retail_lines.json`). The 22,523-line, £377,488 overlap was confirmed by `SIMS/retail-B/referee/check1.py` (`retail-B-06`, `retail-B-27`).
  - retail-A cited the awb-clean wording and left the overlap as an open limitation (`retail-A-08`; `SIMS/retail-A/feedback/agent-notes.md`).
- **C-54:** co2-B: "Unimplemented type for cast (INTEGER -> DATE)" (`SIMS/co2-B/relay/agent-002.jsonl`; `co2-B-13`). The scan missed the country and aggregate mix, which the release plans to catch as a `new` issue (`co2-B-14`).
- **C-42:** co2-B `DQ-008` still carries the withdrawn World-series inference (`co2-B-15`). taxi-A raw and canonical scans produced duplicate rows `DQ-007` to `DQ-025` (`taxi-A-18`; that part was largely the agent's choice).
- **C-26:** `taxi-A-20`, `taxi-B-17`, `co2-A-20`, `retail-A-22`, `retail-B-22`. In taxi-B, the agent renamed a file it did not need to rename after status flagged the source.
- **C-73:** taxi-B: "Invalid initial character for a key part (at line 9, column 104)" (`SIMS/taxi-B/relay/agent-002.jsonl`; `taxi-B-18`).
- **C-74:** retail-B `provenance.json` notes "server sent no ETag or Last-Modified"; status shows `probeable_files: 0` (`retail-B-26`).
- **C-76:** taxi-A: `urllib` HTTP 403 on the TLC dictionary, so an analyst summary was linked as the reference (`SIMS/taxi-A/relay/agent-001.jsonl`; `SIMS/taxi-A/project/foundation/references/tlc-yellow/documentation-notes.md`; `taxi-A-22`).
- **C-80:** taxi-B: `ChecksFailed key:trip_id`, then `rm -rf .../p1.partial` (`SIMS/taxi-B/relay/agent-002.jsonl`; `taxi-B-19`).

**Cause in the release.**
- **C-19:** `awb-clean/scripts/scan_dataset.py:528-537`; `awb-clean/references/checks.md:9`; `awb-clean/SKILL.md:18`, `:24-33`, `:26` and `:31`; `awb-init/references/landing.md:31`.
- **C-54:** `awb-explore/scripts/eda_scan.py:755`, `:35` and `:760-767`; `awb-explore/SKILL.md:22`.
- **C-42:** `awb-clean/scripts/record_cleaning.py:19-21`, `:410-425`, `:466-469` and `:493-496`; `awb-clean/SKILL.md:69`.
- **C-26:** `awb-init/assets/workbench/foundation/sources.md:16-21` and `:27`; `awb-init/assets/awb_landing.py:750-765`; `awb-status/scripts/collect_status.py:262-268` and `:404-406`.
- **C-73:** `awb-init/assets/workbench/foundation/datasets.toml:15` and `:36-41`; `awb_landing.py:333-339`.
- **C-74:** `awb-status/scripts/collect_status.py:573-574`; `awb-status/SKILL.md:18`; `awb-init/references/landing.md:11`.
- **C-76:** `awb-init/assets/workbench/workbench-guides/data.md:11`; `sources.md:16-23`; `awb-status/SKILL.md:32` and `:48`.
- **C-80:** `awb_landing.py:571-573`, `:1031-1033` and `:1117-1119`; `data.md:5` and `:39`; `landing.md:47`.

**Fix direction.**
1. **Overlap and duplicates.**
   - Give the duplicate scan a way to leave lineage columns out of the match, defaulting to columns `datasets.toml` marks as lineage.
   - Add an `awb-clean` step, and a `landing.md` note for multi-sheet workbooks, that compares sheets, files or partitions on their non-lineage columns.
   - Settle the rule: an exact copy of the same source rows across extracts is a representation fix the agent removes and records; repeats within one extract stay the user's decision.
2. **`eda_scan.py`.** Accept an integer year as the date column, comparing as integers. Report coverage per measure across years for panel data.
3. **Quality writer.**
   - Allow amending an observation with a reason, keeping the original text in the row's history.
   - Make the `awb-clean/SKILL.md:69` `findings` sentence conditional on a changed view.
4. **Source register.**
   - Keep the template to the two forms with one example each, and move parser detail to a reference.
   - `land` reports when it changes a hand-kept cell.
   - Status says why a source lacks a reference.
5. **`datasets.toml`.** Show the `[datasets.<name>.checks.types]` subtable form for long tables, and say inline tables stay on one line. Translate the parser message.
6. **Upstream probe.** At landing, say once that a source with no validator cannot be checked for upstream change. Offer a size or checksum comparison by download when the user asks.
7. **Access notes.** Add a third reference form, an access note giving the URL, the date and why the original could not be kept. Status reports it as a known limitation, not a risk. Allow a note that a document's revision postdates the data.
8. **Failed publish.** The refusal says to remove the partial folder before retrying, or offers a flag that clears it, and `data.md`'s publish section repeats that.

**Files.** `awb-clean/scripts/scan_dataset.py`, `record_cleaning.py`, `references/checks.md`, `SKILL.md`; `awb-explore/scripts/eda_scan.py`, `SKILL.md`; `awb-init/assets/workbench/foundation/sources.md`, `datasets.toml`; `awb-init/assets/awb_landing.py`; `awb-init/references/landing.md`; `awb-init/assets/workbench/workbench-guides/data.md`; `awb-status/scripts/collect_status.py`, `SKILL.md`; `awb-init/assets/awb_mcp.py` (schema text for new options); tests.

**Acceptance checks.**
- `tests/test_awb_clean.py`:
  - two sheets with identical non-lineage rows yield a duplicate issue when lineage columns are excluded;
  - an observation amendment keeps the original text and records the reason.
- `tests/test_awb_explore.py`: `--date-column year --start 1850 --end 2024` on an integer column scans without error and reports coverage by year.
- `tests/test_awb_landing.py`:
  - a failed publish names the partial folder and the next step;
  - a multi-line inline table yields the translated message.
- `tests/test_awb_status.py`:
  - an access-note reference is not listed as `documentation_without_reference`;
  - a source without validators is reported once as not checkable.

**Depends on.** Issue 8, for `awb_landing.py`. Merge before Issue 10, for `collect_status.py`.

---

## Issue 10: awb-status reports ([#93](https://github.com/quentin-hickam/analytics-workbench/issues/93))

**Severity.** Minor.

**Closes.** C-31, C-32, C-48, C-71, C-85.

**Problem.**
- **Cryptic freshness (C-31).** `state_status` is "indeterminate at date precision" whenever the state and the latest change share a date, which is the normal case, since every state write stamps today. The skill explains only "out of date".
- **Read-only even with edits in the same message (C-32).** "Stay *read-only*" has no scope. A user who writes "make these edits, then where are we?", as the README's own example invites, may get the edits deferred. One agent then described them as "pending in the package files" when they existed only in chat.
- **Findings counted against questions (C-48).** Status reports `active.counts` (findings) next to the user's question count with nothing relating the two. The footer example counts questions without naming which changed.
- **Caveats hidden (C-71).** The Findings item reports a caveat only for flagged findings. A status with caveats on unflagged findings can say "none open", which `awb-release` forbids for its own report.
- **No row for provisional findings awaiting approval (C-85).** The only route to packaging needs supported findings. With all findings provisional, the table offers brainstorm and commit, and its "Continue" fallback is ruled out.

**Evidence.**
- **C-31:** all four runs whose collector output was checked show `days_after_state: 0` and "indeterminate at date precision", including taxi-A with a clean committed tree (`SIMS/taxi-A/relay/agent-004.jsonl`; `co2-A-21`).
- **C-32:** retail-A A4 (`retail-A-05`); taxi-A transcript lines 165 to 167 (`taxi-A-21`); `SIMS/co2-B/feedback/agent.md`.
- **C-48:** taxi-A "Nine findings are supported" beside five questions, and a footer "1 answered" that the user had to decode (`taxi-A-11`). retail-A "11 supported findings" (`SIMS/retail-A/human/notes.md`, turn 5).
- **C-71:** retail-B A3: "none open. The one recorded caveat is the kept repeated lines", while the collector returned caveats on all eight findings (`SIMS/retail-B/relay/agent-003.jsonl`; `retail-B-08`).
- **C-85:** retail-B A3: the agent improvised "These findings are approved: preview the slide headlines" (`retail-B-23`).

**Cause in the release.**
- **C-31:** `awb-status/scripts/collect_status.py:884`; `awb-status/SKILL.md:26`; `awb-init/assets/awb_provenance.py:1129` (`Last updated: {today}`).
- **C-32:** `awb-status/SKILL.md:8`; `README.md:84` and `:123`. Compare `README.md:86`, which explains same-message changes for release only.
- **C-48:** `awb-status/SKILL.md:27-28`; `awb-init/assets/workbench/AGENTS.md:32`; `collect_status.py:132-133` and `:226`; `README.md:83` and `:98`.
- **C-71:** `awb-status/SKILL.md:27-28`; `collect_status.py:211` and `:223`. Compare `awb-release/SKILL.md:57`.
- **C-85:** `awb-status/SKILL.md:59`, `:56` and `:66`; `awb-init/assets/workbench/investigation/state.md:10`.

**Fix direction.**
1. **Freshness.** Compare timestamps, not dates. When order still cannot be known, say so in plain words beside the evidence result ("saved the same day as the latest change; evidence checks show 11 of 11 current").
2. **Mixed requests.** Scope read-only to the status report itself, and carry out the message's other requests through their own skills after it. The README says so (Issue 11).
3. **Map findings to questions.** Report findings per question ("Q1: 2 findings"), and label roots the agent added.
4. **Caveats.** Report every finding's caveat, as `awb-release` lists `open_caveats`, and never say nothing is open while one remains.
5. **Provisional findings.** Add the row "Provisional findings and no draft" → "Preview the slide headlines" (`awb-package`), and say who promotes a finding and when.

**Files.** `awb-status/SKILL.md`; `awb-status/scripts/collect_status.py`; `awb-init/assets/workbench/investigation/state.md` (who promotes); tests.

**Acceptance checks.**
- `tests/test_awb_status.py`:
  - a state written after the latest change on the same day reports up to date;
  - findings are grouped by question;
  - every finding's caveat is reported.
- `tests/test_skill_surface.py`:
  - the read-only sentence is scoped to the report;
  - the provisional-findings row exists.

**Depends on.** Issues 3 (commit row), 7 (preview state) and 9 (`collect_status.py`).

---

## Issue 11: README ([#94](https://github.com/quentin-hickam/analytics-workbench/issues/94))

**Severity.** Minor.

**Closes.** C-25, C-72.

**Problem.**
- **Still long and admin-heavy (C-25).** The README is about 5,345 words. The Install and administer section is about 1,810 words, and How it works plus Included skills about 965 more. The analyst glossary defines terms an analyst never needs (receipt, which "you never need to open"; canonical view; disposition). The checkpoint paragraph is dense. It does not say:
  - that headlines have a word limit (Issue 6);
  - that choosing supporting tables adds a slide;
  - how many review rounds to expect, or when a draft is stable;
  - what "one-page" means, given the note template's "a page or two";
  - what a commit means for the user;
  - that the user can skip seeing changed slides before release;
  - whether data at a URL is fetched during setup.
- **Clean and explore listed as steps (C-72).** "The usual requests, in order" numbers Clean and Explore as steps 3 and 4, and only a trailing "It helps when..." marks them optional. When agents fold them into other steps, nothing tells the user.

**Evidence.**
- **C-25:** README feedback in every run: `taxi-A-24`, `taxi-B-27`, `taxi-B-28`, `co2-A-15`, `co2-B-23`, `retail-A-20`, `retail-B-12`. All six users praised the quick-start: four by name, and all six found its first-message example useful.
- **C-72:** `retail-A-07`; `SIMS/retail-A/human/notes.md` turn 3: "It never ran a separate clean or explore step, which the README lists as steps 3 and 4."

**Cause in the release.** `README.md:143-214` (admin), `:114-141`, `:96-104` (glossary, including `:99`, `:101` and `:102`), `:66-70` (checkpoint), `:11` (headline), `:13` and `:20` (no Supporting datasets slide), `:46` ("one-page methods note", undefined), `:86` (no release waiver; compare `awb-package/SKILL.md:97`), `:52` and `:81` (URL fetching), `:109` (commits), `:75-88` (the usual requests).

**Fix direction.**
1. Move Install and administer, and How it works, into a separate admin document linked from the top, or collapse them below the quick-start.
2. Drop receipt, canonical view and disposition from the analyst glossary, and say when a disposition is asked.
3. Add the missing expectations listed above, using the behavior Issues 1, 6 and 7 settle.
4. Mark clean and explore as optional, say when the agent folds them into landing or analysis, and say the agent will tell the user when it does.

**Files.** `README.md` only. `scripts/build-dist.sh` changes only if the section markers move.

**Acceptance checks.**
- `scripts/build-dist.sh` builds, and its marker checks pass.
- `tests/test_skill_surface.py`: README link targets resolve.
- A read-through confirms every expectation the README states matches the skills after Issues 1 to 10.

**Depends on.** All other issues, whose behavior it describes. Merge last.

**Review.** Docs-only. Decide the review approach when the PR is opened rather than defaulting to the Codex and Opus pair.

---

## Recommended order

1. **Issue 1, the review gate.** The largest cost in the study: 129.5 of 142.9 minutes in co2-B, and 57% to 91% of agent cost in the Claude-agent runs.
2. **Issue 3, conversation.** Mostly instruction text and cheap. It reaches every run.
3. **Issue 2, what the review checks.** It follows Issue 1 in `review.md`.
4. **Issue 5, check-draft reading.** Mechanical fixes with tests. It precedes Issues 6 and 7 in `awb_draft.py`.
5. **Issue 6, headline limit and gate integrity.** Small, and it closes the one case of a locally altered release gate.
6. **Issue 4, analysis discipline.** It removes the late reconciliation reruns.
7. **Issue 8, setup and MCP routing.** It follows Issue 3 in `AGENTS.md`.
8. **Issue 7, package instructions and files.** It follows Issues 1 and 6, and can then delete what Issue 1 makes obsolete.
9. **Issue 9, data landing and cleaning.** It follows Issue 8 in `awb_landing.py`.
10. **Issue 10, awb-status.** It follows Issues 3, 7 and 9, which touch `collect_status.py` and the status table.
11. **Issue 11, README.** Last, because it describes the result.

**If fewer PRs are wanted:** fold Issue 6 into Issue 5, and Issue 10 into Issue 3. That gives nine.

---

## Contested findings (not proposed yet)

> **These are not part of any issue above.** The two skeptics split on each one. The usual split: the harness lens found no harness cause and called it a product defect, while the release lens found the release already instructs against it, or allows it, and called the cause the agent. Each needs a maintainer decision before it becomes work.

| ID | Finding | Runs | Harness lens | Release lens | Decision needed | Would fit |
|---|---|---|---|---|---|---|
| C-57 | Headline previews need substantial user correction | co2-A, co2-B | Product, narrowed: co2-A's vague Answer clause, top-ten slides framed on one country, a co2-B subtitle period missing 1850; nothing checks a headline against its question before the preview | Unsupported: `findings-template.md:14` and `:36` already require an answer with its key number; the preview is the designed correction step; the cap part duplicates C-13 | Whether a pre-preview self-check against the questions is worth adding, or the preview step is enough | Issue 2 |
| C-59 | Review independence rests on the brief and the agent's discipline | taxi-A, retail-A | Product: Codex reviewer subagents inherit all tools; retail-A spawned reviewers with the writer's full history (`fork_turns: "all"`) and edited narratives mid-review; `review.md` has no rule against either | Unsupported: no reviewer wrote anything, the mid-review edit was re-read before "clean", and later full reviews passed. Notes that the default history fork is a separate real gap | Whether to add two lines to `review.md`'s Codex branch: spawn the reviewer without history, and never edit narratives while a review runs | Issue 1 |
| C-79 | The analysis guide does not say packaged results need an `answers` declaration | taxi-B | Product: the settings template calls `answers` "optional", and packaging needs it on every represented result to order slides | Unsupported: `analysis.md:11` makes it conditional ("when it answers ledger data questions"); unlinked slides only sort last; the agent skipped an instruction it had read | Whether to add one sentence to `analysis.md` saying packages order slides by `answers` | Issue 4 |
| C-89 | Newark's short-duration anomaly understated in the draft and release | taxi-B | Product: the agent knew about implausibly short trips in reply 4 but never recorded the caveat, and the review checks consistency, not completeness | Unsupported: the agent failed to record a caveat it had promised; the released "roughly 8 minutes each" came from the user's own wording and the agent's rule; the zone slide carries the 0.3-minute median | Whether C-11's brief-aware review covers it; otherwise drop | Issue 2 |
| C-92 | MCP setup output lists packages as missing after installing helpers | taxi-B | Product, minor: the output is accurate, but the tool's title ("Install workbench helpers") and the phrase "package formats" invite the misreading | Unsupported: accurate output, the skill says to run the printed command, and 5 of 6 agents read it correctly | Whether to add one clause to the setup tool description saying Python packages are checked, not installed | Issue 8 |
| C-93 | Agent queried inbox files with raw DuckDB before landing | taxi-B | Product: `awb-scope` says to look facts up in source systems during a round that runs before landing, while the landed-copies rule sits in `data.md`, reached only through an `AGENTS.md` trigger | Unsupported: one lapse against `data.md:9`; the other five agents read the guide and landed first | Whether `awb-scope` should point at `data.md` for any look at source records | Issue 3 |
| C-95 | A near-tautological repeat-buyer share carries weight on the Answer slide | retail-A | Product, weak: preview-and-wait shows only headlines, so the figure first appeared in the draft | Unsupported: the agent chose the metric and already caveated its exposure bias; the user's draft review caught it | Probably drop | none |
| C-96 | Unrecorded StockCode normalization changes a ranking | retail-A | Product, low confidence: `data.md:43` ("preparation owns ... normalization") conflicts with `data.md:47` ("normalization ... stay in views"), and nothing catches a transform inside a conversion | Unsupported: the agent ignored clear guidance to put normalization in views and record it in `quality.md` | Whether to reconcile the two `data.md` sentences | Issue 9 |
| C-97 | An undisclosed "purchase" definition shifts repeat counts slightly | retail-B | Product: nothing sends a definition the user approved back to the user when the data narrows it, and the review does not check omissions | Unsupported: the glossary and the delivered `methodology.md` record it, and the note template asks for definitions. The shift is 0 to 2 customers per cohort | Whether to add "report a narrowed definition to the user" to `AGENTS.md` | Issue 3 |
| C-98 | Agent promoted a classification to a shared foundation view unasked | retail-B (and retail-A did the same) | Product: `AGENTS.md:36` ("broader preparation needs an explicit request") reads against `data.md:43` ("promote ... deliberately"), and two agents on two hosts made the same choice | Unsupported: the view served the active question, was announced in chat, filters nothing, and matches the design's split of shared normalization and local exclusion | Whether "deliberately" should say who decides | Issue 4 |
| C-99 | Findings re-promoted after reruns on the strength of an earlier acceptance | retail-B | Product: no shipped text says who promotes a finding or whether an acceptance survives a rerun | Unsupported: promotion is the agent's validation step and acceptance is not a condition; the agent disclosed both reruns, and the user approved the release | Settled if Issue 10 says who promotes a finding; otherwise drop | Issue 10 |
