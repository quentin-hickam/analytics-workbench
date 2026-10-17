# UX simulation re-run, 2026-10-16: comparison with 2026-10-15

On 2026-10-15 six simulated first-time users took the `awb-*` skills from an empty folder to a released deck package. That study (`docs/ux-simulation-2026-10-15/README.md` and `fix-plan.md` in the repository) became seven fix phases, filed as #61 to #67. All seven have merged. This re-run repeats the study on a release built from `main` at `1db6084`, with the same three datasets, persona briefs, end point and role swap, on a rebuilt harness. It reports what changed, ranks what remains, and keeps harness effects out of the scores.

- The issues are in [proposed-issues.md](proposed-issues.md), filed as [#84](https://github.com/quentin-hickam/analytics-workbench/issues/84) to [#94](https://github.com/quentin-hickam/analytics-workbench/issues/94).
- The raw data behind this report (run results, answer grading, consolidated findings and both skeptics' verdicts) is in [data.json](data.json).

## Bottom line

- **All six runs reached the end point again.** Each answered all five questions, asked `awb-status`, had a draft reviewed by the user, and released 001. Every storage copy is identical to the in-project release. In the taxi runs, where the user handed over files, every landed original has the same SHA-256 as the file in the inbox.
- **All 30 answers were correct.** Each answer was recomputed blind twice, once in DuckDB and once in pandas, then graded against the definitions the user agreed in the transcript.
  - 15 matched exactly and 3 within rounding.
  - The other 12 differed by definition. In ten, the blind recomputes picked their own thresholds, minimums, denominators or revenue basis, and under the agreed rules the grader reproduced the agent's figures. In retail-A Q1 and Q2, the remaining £747 gap comes from the agent's own sign rule for one cancellation line. The grader judged that rule defensible, but the user never agreed to it.
  - The graders found two small definitional choices never disclosed to the user: a sign rule that moves one retail-A cancellation line by £747, and how taxi-B split trips touching two airports. The referees found two more: retail-B's narrower "purchase" (it needs a goods line), which moves repeat counts by a customer or two per cohort, and retail-A's stock-code case merge, which moves one product from rank 7 to 9.
- **Users were slightly happier and sent fewer messages.** Mean satisfaction rose from 7.5 to 7.8 out of 10. Users sent 49 messages, against 55 on Oct 15.
- **Most Oct 15 fixes held.** 15 items are verified fixed, among them the scoping interview, stale-everything churn, the checked methods note, export rounding, the appendix, the headline-checkpoint mode, routine installs and the quality-ID scheme. Of the eleven Oct 15 areas, 2 are fixed, 6 improved, 2 persist and 1 regressed.
- **The main cost moved into package review, and it grew.**
  - In the three runs where Claude was the agent, packaging ran 15, 21 and 38 full reviews. In co2-B, packaging and review took 129.5 of 142.9 minutes and $44 of the $48 agent cost.
  - Those runs got slower (mean 76 to 105 minutes) while the Codex-agent runs halved (103 to 53 minutes, partly because the relay is faster).
  - Fresh reviewers flip verdicts on unchanged text, and the reviews still miss what users catch in one read.
- **58 product findings survived both skeptics** (23 major, 35 minor). 25 are new, 24 persist from Oct 15, and 9 are partly fixed. 11 more are contested and 20 were rejected. 21 harness findings are listed separately and not scored.
- **Some new defects come from the Oct 15 fixes themselves:**
  - #66's rule that only a full review completes a request drives the review loop, and its "with its tolerance" rule pushed invented tolerances into audience text.
  - #62's footer counts "answered" by ledger status, so agents report answers the user has not seen.
  - #65's recorded project interpreter moved the virtual-environment trap into setup.
  - #64's START-HERE note contradicts itself, and #61's preview mode has no defined file; one improvised preview file shipped inside a frozen release.
- **The result is 11 PR-sized issues (#84 to #94),** led by the review gate and conversation hygiene.

## Method

| | Detail |
|---|---|
| Release under test | Built from `main` at `1db6084`. Its skills are identical to `.agents/skills/` at that commit. A copy is at `SIMS/release/analytics-workbench-skills/` |
| Datasets | Unchanged: NYC TLC yellow taxi trips, Jan and Jul 2024 (two Parquet files plus the zone lookup, as local files); Our World in Data CO2 (CSV and codebook, by URL); UCI Online Retail II (zipped XLSX, by URL) |
| Questions | Five per dataset, in the same persona briefs (`SIMS/kit/personas/`) |
| Variant A | Claude (Opus) played the user, Codex the agent |
| Variant B | Codex played the user, Claude (Opus) the agent |
| Harness | Both roles ran as headless CLI sessions (`codex exec` and `claude -p`), each resumed by its session ID every turn, driven by a deterministic relay script (`SIMS/kit/relay.py`). No model relayed messages |
| Codex agent | A simulated home holding only the release skills, with Codex's bundled skills off; the `awb` MCP server registered with its tools auto-approved; a writable `.git`; Python 3.13 first on `PATH` |
| Claude agent | Real headless Claude Code with real skill discovery and the `awb` MCP server, with Bash and the awb tools pre-allowed. On Oct 15 this role was a subagent imitating a host with no MCP server, so variant B results are not strictly like-for-like |
| User's view | The release README, the persona brief (`SIMS/kit/human-rules.md`), the agent's replies, and only the project files the agent pointed to |
| Referee | One per run (`SIMS/kit/referee.md`). It started the relay, verified the end point, spot-checked answers against the landed files, audited isolation, collected feedback from both roles, and tagged each finding product, harness or unclear |
| Answer grading | Each answer recomputed blind twice from the source data (`SIMS/grading/<run>-sql/`, `<run>-pandas/`). A grader then compared the agent's answer, both recomputes and the definitions agreed in the transcript, and ran its own checks where they disagreed (`SIMS/grading/<run>-compare/`) |
| Finding triage | Findings were merged across runs and re-tagged independently of the referee. Each product finding was then checked by two skeptics: one looking for a harness cause, one checking whether the release text causes it. **Confirmed** means both called it a product defect, **rejected** means neither did, **contested** means they split. Only product findings count toward the scores and the issue list |

**Paths.** Evidence paths are written `SIMS/<run>/...`, where `SIMS` is the folder that holds this report folder; the links below resolve from here. In this repository the copied evidence is flattened: `SIMS/<run>/feedback/<file>` is `<run>/<file>`, `feedback/orchestrator-report.md` is `<run>/referee-report.md`, and `human/notes.md` is `<run>/human-notes.md`. Relay logs, project folders, storage and grading scripts were not copied; their figures are in `data.json`. Release paths such as `awb-package/references/review.md:33` are relative to the release root, which matches `.agents/skills/` at `1db6084`. README line numbers refer to the release README, which drops the dist-excluded blocks.

**IDs.** `C-NN` is a consolidated finding. Per-run IDs such as `taxi-B-01` are the IDs in each run's `findings.json`. The `member_ids` lists in `data.json` use an earlier numbering that does not match those files, so the proposal cites the `findings.json` IDs and the files directly.

## Results by run

| Run | User / agent | User msgs | Agent turns | Wall-clock | Satisfaction | End point | Answer accuracy | Spot-check |
|---|---|---|---|---|---|---|---|---|
| [taxi-A](taxi-A/) | Claude / Codex | 9 | 8 | 59.5 min | 9/10 | met | 5/5 correct: 2 within rounding, 3 differ only by the agreed definitions | all 5 exact |
| [taxi-B](taxi-B/) | Codex / Claude | 8 | 7 | 95.9 min | 7/10 | met | 5/5 correct: 1 exact, 1 within rounding, 3 by definition; per-airport split rule not disclosed | all 5 exact |
| [co2-A](co2-A/) | Claude / Codex | 7 | 6 | 50.4 min | 8/10 | met | 5/5 exact | all 5 exact |
| [co2-B](co2-B/) | Codex / Claude | 9 | 8 | 142.9 min | 7/10 | met | 5/5 exact | all 5 exact; released from a repository with no commits |
| [retail-A](retail-A/) | Claude / Codex | 8 | 7 | 49.4 min | 8/10 | met | 5/5 correct: 2 exact, 3 by definition; sign rule for one cancellation line not disclosed (Feb 2010 £747 lower) | all 5 match; stock-code case merge not recorded |
| [retail-B](retail-B/) | Codex / Claude | 8 | 7 | 75.2 min | 8/10 | met | 5/5 correct: 2 exact, 3 by definition (postage included, as the user agreed) | all 5 match (Q4: 873 qualifying products vs 872, from stock-code case-folding); "purchase" definition not shown to the user |

- **Counting.** User messages include the closing DONE line, which is never relayed. Agent turns are replies and leave out the feedback turn. This matches the Oct 15 table, where messages were always turns plus one. data.json's per-run human_messages, agent_turns and wall_clock_minutes come from the referees and mix conventions: co2-A's 6 messages leave out DONE, taxi-A's 9 turns include the feedback turn, and wall-clock includes the feedback turns except retail-A's 49.4. The table uses relay/state.json.
- **Wall-clock** runs from relay start to DONE. With the feedback turns added it is 62.4, 97.6, 52.9, 144.3, 53.6 and 77.3 minutes.
- **Agent cost** was recorded for the Claude agents only: taxi-B $35.51, co2-B $48.38, retail-B $20.72.
- **"By definition"** means the blind recomputes chose their own validity thresholds, minimums, denominators or revenue basis, while the agent applied what the user agreed. The grader reproduced the agent's figures under the agreed rules in all but two such cases. The exceptions are retail-A Q1 and Q2. There the remaining £747 gap comes from the agent's own sign rule for one positive-quantity cancellation line. The user never saw that rule; the grader judged it defensible. Details are in each run's `compare` block in `data.json`.

Each run folder here holds `transcript.md`, `human.md` (user feedback), `human-notes.md` (the user's per-turn log), `agent.md`, `agent-notes.md`, `referee-report.md`, `findings.json` and `harness-log.md`. The raw relay logs, referee scripts, projects and storage stayed in the simulation folder.

**Skill use.** No run used `awb-brainstorm`. A clean scan ran in four runs (taxi-A, taxi-B, co2-B, retail-B). co2-A and retail-A folded cleaning and exploration into landing and analysis, and the retail-A user wondered whether a step had been skipped (C-72). Every run asked `awb-status` at least once.

## Findings, ranked

Ranking weighs how many runs hit an issue against its severity. "n/6" counts the runs where any confirmed member finding appeared. Only confirmed product findings are ranked here. Where a skeptic narrowed a finding, the narrower version is stated.

### 1. Package review does not converge, and a clean review is not a reliable gate (6/6, major)

- **Cost (C-01).** Full reviews per run: taxi-B 21, co2-B 38, retail-B 15, retail-A 4, taxi-A 4, and six in co2-A (four in its drafting turn, one after the user's corrections and one at release). taxi-B's drafting reply took 58.5 minutes and $21.71, 61% of its agent cost ([taxi-B](taxi-B/referee-report.md)). retail-B's took 40.4 minutes and 57% of its cost. The causes are all in the release text:
  - any narrative problem blocks, and the user may accept only `warning` violations;
  - only a full review can complete a request, and a scoped re-review "never does";
  - any narrative edit makes the last review stale;
  - `awb-release` runs a fresh full review even on a draft a clean review just passed.
- **How long the user waited.** Measured from the relay logs (`SIMS/kit/measure.py`). A packaging turn is any agent reply that ran the package skill, a draft check or a reviewer. Minutes count only conversation replies, not the feedback turn.

  | Run | Agent | Packaging minutes | Reviewer runs | Draft-check runs | Longest single wait | Agent time in packaging |
  |---|---|---|---|---|---|---|
  | taxi-A | Codex | 28 of 57 | 5 | 16 | 17 min | 49% |
  | taxi-B | Claude | 77 of 94 | 21 | 59 | 58 min | 82% |
  | co2-A | Codex | 26 of 48 | 4 | 11 | 17 min | 53% |
  | co2-B | Claude | 131 of 140 | 38 | 100 | 43 min | 94% |
  | retail-A | Codex | 33 of 47 | 2 | 16 | 13 min | 70% |
  | retail-B | Claude | 52 of 65 | 15 | 48 | 40 min | 79% |

  The reviewer-run column counts reviewer subagent launches seen in the relay log. The Codex rows undercount, because Codex reviewer threads can be reused and their calls are missing from the relay log (C-69); co2-A's snapshots show six full reviews. During each of those waits the user saw nothing, since the agent cannot be interrupted mid-turn. GitHub Copilot Chat in VS Code runs one conversation thread at a time, and the release ships `awb-package-reviewer` as a VS Code custom agent for this step, so a Copilot user would wait through the same loop. That is inferred from the release's design, not tested in Copilot.

- **Inconsistent verdicts (C-17).** In retail-B, the approved France/Australia headline passed rule R-concentration-001 in four full reviews, then failed it in the next, with the text unchanged and the same reviewer prompt as the pass before. In co2-B, the release review flagged a line that the previous turn's final review had passed.
- **Misses (C-11).** The review never reads the brief.
  - taxi-A: Q3's hour and borough detail sat only in speaker notes, and the user caught it.
  - taxi-B: 15 reviews passed a methods note that grew from 770 to 867 words during those reviews, against a one-page request, and a base-fare definition that left out flat airport fares ([taxi-B](taxi-B/human.md)).
  - co2-B: a review accepted an unsupported claim about how OWID builds its World series.
- **Review rules saved on the agent's judgment (C-06).** taxi-A and co2-A each saved four rules without asking. Three taxi-A rules begin "For this board study", and one co2-A rule hard-codes that deck's directions. Two taxi-B rules collided with no precedence. In co2-B, the agent's R-periods-001 bloated the Answer slide's caveat; it is the same over-literal rule Oct 15 reported.
- **The "with its tolerance" rule (C-10).** #66 requires every "checked" sentence in audience text to state a tolerance.
  - taxi-A: "zero-record tolerance" stayed on the released appendix slide after the user removed it from the note.
  - co2-B: the agent invented a 0.15 Mt tolerance after seeing a 0.13 Mt maximum gap, and put it in a visible bullet after the user asked for notes only.
  - retail-B: internal filter retention ratios appeared on the How we know slide.
- **No pass for readability (C-33).** First drafts carried "other located trips", fare labels like $106.28, arrow-heavy headlines, an undefined "territorial" and imperative methods bullets. Review repairs in retail-B spread misleading labels such as "three largest buyers" for growth contributors.
- **Edits frozen unseen (C-15).** Repairs forced by the mandatory release review went into release 001 in the same turn without being shown. In taxi-B, the agent rewrote a Newark line and trimmed approved note lines. In co2-B, "every country behind the rankings" became "the countries behind each ranking".
- **Note length (C-70).** Nothing compares the methods note with the length the brief records, and the template allows "a page or two".

### 2. Internal vocabulary still reaches the user (6/6, major)

- **C-02.** Replies carried commit hashes (taxi-A, retail-B), review-rule and result IDs (taxi-A, co2-A), "No packaging Git commit exists" (retail-A's final reply) and, in a relayed interim message, "one-penny tolerance" (retail-A), and validation and fingerprint detail (co2-B). Agents also pointed users to interim report files written in record terms ([taxi-A](taxi-A/human.md)).
  - Part of this is required by the release: `review.md` says "Report the new ID"; `awb-package` asks for each chart with the result it serializes; `awb-clean` asks for quality IDs.
  - The provenance-gap rule drops a gap only "when it changes nothing the user decides", and its one example is a project without Git, so agents report the gap for a Git repository with no commit yet.
  - Interim shell narration in the Claude-agent runs is partly a harness effect (C-66).
- **Status counts (C-48).** "Nine findings are supported" sat beside five questions, and the footer said "1 answered" without naming which question.
- **Cryptic freshness (C-31).** `awb-status` reports "indeterminate at date precision" whenever the state and the latest change share a date, which is the normal case. Agents dropped the line or puzzled over it.
- **Commit reminders (C-30).** co2-B mentioned commits in five replies and retail-B suggested one three times, despite the once-per-session promise. The guides carry that guard; the `awb-status` row and the package and release reports do not.
- **SKILL.md links.** All three Codex agents linked or quoted `SKILL.md` files to justify pauses again (taxi-A three times, retail-A five, co2-A once), and the taxi-A user ranked it the top pain point. Both skeptics traced it to Codex's own base instructions, which tell the model to name the `SKILL.md` behind a pause. It is therefore rejected as a release defect (C-12), but real Codex users will see it.

### 3. check-draft misreads ordinary text and display choices (6/6, major)

- **Numbers (C-09).** Slash pairs (54.8/57.6), clock times (18:00), identifier pairs (264/265), citation years and years followed by a word are reported as untraced numbers. This is documented and fails safe, but it cost failed preflights and rewording of sound prose in four runs ([taxi-A](taxi-A/agent.md)). A skeptic found the apparent year inconsistency was coincidental tracing, not a rule bug.
- **Claims (C-34).** The claims check refuses sentences that deny causation ("does not test what caused them", "causes cannot be inferred") and "waiting and driving". retail-B rewrote the user's own caveat and then told the user it was "in your wording".
- **CO₂ labels (C-22).** The narrative is NFKC-normalized but chart CSV headers are not, so five co2-A charts failed until the labels became plain ASCII.
- **Unit rescaling (C-23).** Mt shown as billions of tonnes cannot be traced. co2-A added Gt columns to saved queries, reran and re-promoted two findings.
- **Double rounding (C-24).** Shares rounded to 4 places in result queries were rounded again on export: 52.5% for a true 52.4% (193 of 368 = 52.446%, stored as 0.5245) and 63.2% for a true 63.1% (63.147%, stored as 0.6315). check-draft accepted both. A reviewer caught them before the user saw them, and the fix forced a full rerun ([retail-B](retail-B/agent.md)).
- **Headline cap (C-13).** The 15-word headline limit is a hard error with no override, and neither the README nor the headline checkpoint mentions it. Approved headlines were trimmed in co2-A and co2-B.
- **An altered gate (C-21).** To keep the user's 21-word headline, the co2-A agent edited the installed `src/packaging/draft.py` and two templates, and release 001 passed that locally changed gate. `AGENTS.md` allows adapting helpers, and neither check-draft nor release compares gate code to the installer receipt ([co2-A](co2-A/referee-report.md)).
- **Chart specs (C-39).** All three Claude agents put blank lines between chart-spec fields, as the template wording suggests, and check-draft then counted the fields as bullets.

### 4. Setup and MCP routing (6/6, major)

- **Recorded interpreter (C-03).** On a fresh project, MCP `awb/setup` records the MCP server's own Python as the project interpreter. That Python is global by design and usually lacks duckdb.
  - All three Codex runs recorded `<python-prefix>/bin/python3`, built a venv, edited the README by hand and reran setup.
  - All three Claude runs had to guess whether to create the venv before setup.
- **CLI over MCP (C-05).** With the `awb` server connected, the Claude agents ran most helpers through Bash: taxi-B 89 helper calls against 10 MCP calls, co2-B 83 against 32, retail-B 70 against 10 (main-thread Bash calls running `src/awb.py` or `run.py`). The Codex agents mostly used MCP. `AGENTS.md` prefers MCP in one sentence, then says "Run workbench helpers with `python3 src/awb.py <command>`". About 85 CLI spellings across the skills and guides pull the other way. The harness pre-allowed Bash, which hid the approval cost. Copilot was not tested; the cost there is inferred from its documented approval model.
- **SQL (C-16).** `awb sql` cannot bind settings `$parameters`. Under `--read-only`, any EXPLAIN failure, even an ambiguous column, comes back as "run it without --read-only". No agent followed that advice, but it points the wrong way.

### 5. "Answered" before the user has seen the answers, and chat claims run ahead of the evidence (6/6, major)

- **C-04.** `run.py` marks a question answered as soon as a result declares it. The footer counts that status, and the headline checkpoint shows headlines, not evidence. co2-A and retail-A reported "5 answered" and asked for headline approval while chat showed only leaders or summaries; each user spent the next message getting the tables. The Claude-agent runs showed a milder form.
- **Untested explanations (C-18).** retail-B called December buyers "probably Christmas-season buyers", said growth was "spread across many accounts" when three accounts gave 99.6% of Germany's growth, and recommended removing "double-scanned" lines. taxi-B claimed code-0 totals were undercounted, which its own check later disproved. The rule against this sits in one sentence of `AGENTS.md`.
- **Thresholds after results (C-14).** taxi-B applied a 1,000-trip minimum without asking. After seeing which zones led, it proposed a 10,000-trip minimum and dropping rate-code-99 trips. The analysis guide says nothing about who sets such a threshold.
- **Coverage gaps (C-20).** co2-B's query computed China's and India's years with data (118 and 156 of 175) at the first answer, but no caveat followed. A later review supplied the misleading wording "count as zero", and the user had to challenge it. Oct 15's co2-B made the same class of error.
- **Chat figures (C-45).** Bases changed without notice (taxi-B's code-0 share went from 6.9% of all records to 4.02% and 8.85% of screened trips; 54 zones became 53). co2-B miscounted coded entities.

### 6. Checks the review now demands are not set up at analysis time (5/6, major)

- **C-07.** Validation leaves row counts and joins "not assessed" unless a producer supplies counts, and the analysis guide suggests no standard reconciliation. Meanwhile #66 requires every "checked" or "reconciles" sentence to cite a recorded check. The gap surfaces only at packaging.
  - taxi-B's methods text told the board that counts and joins were not checked.
  - co2-B's earlier exploration reconciliation was refused as a citation, so the agent built a new result filed under Q-004's question, which it does not answer.
  - retail-B needed three commits and reruns after the user had accepted the findings.
- **Provenance repair (C-56).** Results run before the first commit stay "uncommitted" until rerun after a commit. Nothing tells the agent, and retail-B found it only from the manifest.
- **Records drift (C-62).** taxi-B's recorded findings still say "Monday to Wednesday", "one holiday" and "all record zero tips" after the release corrected them.

### 7. Long instructions, awkward step order and package-file details (6/6, major for time)

- **Length (C-08).** `awb-package`'s `SKILL.md`, package contract, review reference and helpers reference total about 11,700 words. Step 4 opens with a single 3,089-character paragraph, and the scoped re-review procedure is elaborate but can never complete a request. Agents on both hosts called it too long. Most packaging time still went to the review loop, not to reading.
- **Step order (C-27).** Run before the draft folder exists, `export` refuses with "create it with awb-package" (taxi-B, co2-B, retail-B); run before the chart specifications exist, it fails with "no specification in findings" (taxi-A, retail-A). Step 3 asks for display names and methodology lines that only step 4's export produces.
- **Package files:**
  - preview-and-wait has no defined file, and co2-A's improvised `headline-preview.md`, with question and result IDs, shipped in frozen release 001 (C-37);
  - the default storyline lets supporting citations and plain words that happen to be result IDs move slides (C-40);
  - START-HERE lists `methodology.md` both as a file to attach and as internal "do not send" (C-50);
  - release folders nest names the user never chose (C-51);
  - the Open questions slide ties membership to `must` priority (C-77);
  - "one `###` slide per finding" clashes with how the glossary defines a finding (C-86);
  - `display.toml` label warnings cannot be confirmed, and boolean value keys silently miss (C-55);
  - the source register's reference grammar runs to about 340 words (C-26).

### 8. Data landing, cleaning and analysis helpers (5/6, major)

- **Cross-sheet duplicates (C-19).** The UCI workbook's two sheets overlap on 1-9 December 2010: 22,523 lines, about £377k. The duplicate scan groups by every column, so the `sheet` and `sheet_row` lineage columns hide the copies. `awb-clean` is also ambiguous about who decides. Both retail agents found the overlap only through their own date checks; retail-A left it as an open limitation and retail-B removed it itself.
- **Smaller helper defects:**
  - `eda_scan.py` fails on an integer year column (C-54);
  - `validate.py` raises `KeyError: 'left_rows'` instead of a validation message (C-53);
  - the settings `views` key accepts names it cannot check (C-75);
  - the quality-ledger writer cannot amend an observation (C-42);
  - there is no investigation-local shared SQL, so taxi-B copied a screening CTE into 15 or more files (C-41);
  - the `datasets.toml` template shows only one-line inline tables (C-73);
  - a failed publish leaves a partial folder without saying so (C-80);
  - the upstream probe cannot check sources without ETag or Last-Modified (C-74);
  - there is no form for documentation that cannot be retained (C-76);
  - no instruction says who fills the README storage lines at setup (C-43).

### 9. awb-status gaps (4/6, minor)

- `awb-status` stays read-only even when the same message asks for edits. retail-A deferred the user's headline edits and called them "pending in the package files" when they existed only in chat (C-32).
- It reported "none open" in retail-B while three finding caveats remained, because it reports only flagged findings' caveats (C-71).
- It has no next-request row for provisional findings waiting on the user (C-85).

### 10. The README (6/6, minor)

- **C-25.** The analyst quick-start from #67 helped. All six users praised it: four by name, and all six found its first-message example useful. The README is still about 5,300 words, roughly half of it install and internal material. Its analyst glossary includes terms an analyst never needs (receipt, canonical view, disposition). It does not say:
  - that headlines have a word limit;
  - that choosing supporting tables adds a slide;
  - how many review rounds to expect;
  - what "one-page" means, or what a commit means for the user;
  - that the user can skip seeing changed slides before release.
- **C-72.** It lists clean and explore as steps 3 and 4. When agents folded them into other steps, the retail-A user was unsure whether something had been skipped.

### 11. Scoping round bundling (2/6, minor)

- **C-58.** `awb-scope`'s cap of four decisions per round led agents to nest unrelated method choices under one numbered question (co2-B, retail-B). Users followed them, but retail-B's user corrected two of the bundled choices.

### Contested (11, not ranked)

The two skeptics split on these, usually because one judged the agent at fault and the other judged that the release allowed or invited it. They are listed in [proposed-issues.md](proposed-issues.md#contested-findings-not-proposed-yet) with what each lens found:

- C-57 headline previews need substantial correction
- C-59 review independence rests on the brief
- C-79 packaged results need an `answers` declaration
- C-89 Newark's short durations understated
- C-92 setup output lists packages as missing after install
- C-93 agent queried inbox files before landing
- C-95 a near-tautological repeat-buyer share
- C-96 unrecorded stock-code normalization
- C-97 an undisclosed purchase definition
- C-98 a classification promoted to a foundation view unasked
- C-99 findings re-promoted on an earlier acceptance

### Rejected (20)

Neither skeptic found a release cause for these.

- **Host or model behavior that real users may still see:**
  - C-12: Codex agents link `SKILL.md` files, which Codex's base instructions ask for.
  - C-64: Codex switches between absolute and relative links against its own host rule.
  - C-38: Codex parks the first message in an improvised README section; the Claude agents did not.
- **Relay effects:** C-44 (long replies; the relay joins every interim message, and `codex exec` renders the question tool as text).
- **Agent slips against clear release instructions:** C-28 (tool and shell slips), C-63, C-81, C-87, C-88, C-90, C-91, C-94.
- **Design working as intended, or friction the evidence did not show:** C-49, C-52, C-60, C-61, C-78, C-82, C-83, C-84.

## What worked

- **Correct, reproducible numbers.** 30 of 30 answers were correct. The grader reproduced every figure under the agreed definitions except four retail-A figures: Feb 2010, the Y1 and 24-month totals, and guest revenue. It traced those to the agent's undisclosed sign rule for one cancellation line. In every other difference, the cause was a threshold or basis choice, and the agent had followed the one the user agreed.
- **Faithful use of the user's definitions.** Agents applied the exclusion rules, floors and revenue bases the user set, and labelled them. The taxi-B agent rebutted the user's wrong calendar objection with a query and was right.
- **Landing, retention and release.** Originals were checksummed and copied to the landed folder. Every release copy was identical to the in-project release.
- **Cleaning that caught real problems:**
  - the retail cross-sheet overlap, found by both agents;
  - Kosovo's missing ISO code (both co2 runs) and Antarctica's ISO code (co2-A);
  - Newark's 0.3-minute median trip time (taxi-B);
  - rate-code-99 card trips that almost all record zero tips (taxi);
  - the storage jar's 95% cancellation rate coming from one reversed order (retail).
- **The Oct 15 fixes in use:**
  - the methods note was checked in every run;
  - users chose the checkpoint mode themselves;
  - agents ran the install command themselves;
  - unsupported "checked" sentences were caught before release;
  - no run reported stale-everything churn;
  - top-ten charts used row selection instead of new results.
- **Codex-agent runs were fast and frugal:** 49 to 60 minutes, with four to six full reviews each (taxi-A 4, retail-A 4, co2-A 6).
- **Satisfaction held or rose in every run.**

## Differences between the two variants

The samples are small (three runs per cell), and the model playing the user changes with the model playing the agent, so treat these as leads.

- **Codex as agent (A runs):**
  - fast: mean 53 minutes, against 103 on Oct 15, partly from the script relay;
  - four to six full reviews per run (taxi-A 4, retail-A 4, co2-A 6);
  - used MCP heavily (taxi-A made about 126 MCP calls against about 11 CLI helper calls);
  - linked `SKILL.md` files to the user (host-caused, C-12);
  - improvised preview files (C-37), and recorded the MCP server's Python as the project interpreter (C-03);
  - reported "5 answered" before showing the answers (co2-A, retail-A);
  - co2-A edited release-gate code (C-21);
  - satisfaction 9, 8, 8.
- **Claude as agent (B runs):**
  - slow: mean 105 minutes, against 76 on Oct 15;
  - 15 to 38 full reviews per run, with $20 to $48 in agent cost, most of it in packaging;
  - ran helpers through the CLI more than through MCP (C-05);
  - put blank lines in chart specs (C-39) and exported before the draft folder existed (C-27), in all three runs;
  - made more slips in chat figures and explanations (C-18, C-45);
  - satisfaction 7, 7, 8.
- **Claude as user (A runs):** asked for the full tables before approving headlines (co2-A, retail-A), accepted the outline package, and turned down the instruction-file links.
- **Codex as user (B runs):**
  - terse and strict;
  - caught substantive errors the reviews missed: co2-B's "count as zero" wording, taxi-B's note length and base-fare definition;
  - made one wrong factual objection (taxi-B's calendar) and retracted it.

## Isolation

The referees audited every agent and user log. They found no agent reads of the spec, design docs, `CONTEXT.md`, the repository, or the human or relay folders, and no reads under `/Users/` except Claude Code's own spilled tool-result files (listed below). No user role read `AGENTS.md`, a `SKILL.md`, `src/`, any `.py` file, the workbench guides or the agent homes.

Edge cases, none of which exposed study contents:
- **taxi-B and co2-B:** listed the simulation folder (the project's parent), which showed `human`, `relay` and `REFEREE.md` beside the project. No file was opened.
- **taxi-B, co2-B and retail-B:** wrote scratch files to `/tmp` or `/tmp/claude-501`; all were deleted or moved except co2-B's `/tmp/q.sql`, which was left behind and removed after the run.
- **taxi-B and co2-B:** the agent or a reviewer subagent read Claude Code's own spilled tool-result files under the real `~/.claude/projects`. They held only that session's output.
- **taxi-A:** the agent read `feedback/harness-log.md` in the feedback turn after DONE.
- **taxi-A, co2-A and retail-A:** the Codex reviewer subagents' tool calls are missing from the relay log. co2-A's were audited from the Codex session rollouts. taxi-A's and retail-A's audits are incomplete for that reason.
- **The ancestor walk** for `AGENTS.md` and `CLAUDE.md` ran existence checks only, as `awb-init` intends.

## Harness findings (excluded from scoring)

These came from the simulation, not the release. They are listed so the next run can avoid them, and none counts toward any score or issue.

- **Personas front-loaded facts they should give only when asked** (C-29; 5 runs). Scoping shrank to one round and package questions were skipped. The README's own first-message example invites some of this.
- **The harness's private friction log leaked into replies** ("Now the friction log.") and added overhead (C-36). Its agent prompt says the user sees only the final reply, while the relay forwards every interim message (C-66). Both confound how interim narration (C-02) should be read.
- **Pre-approval hid permission prompts** (C-67). Bash and the awb tools were pre-allowed, so the approval cost of CLI-heavy runs (C-05) was not measured.
- **The Codex sandbox** blocked heredoc temp files, tool caches and system-temp writes (C-47), and its web tool failed on one PDF (C-105). The backend returned transient 403s once (C-108).
- **The Codex user role's first message** included its own meta-line, relayed verbatim (C-46).
- **Non-interactive `codex exec` instructions** conflict with the interview-first rule (C-109).
- **Scratch writes and ancestor listings outside the simulation folder** (C-35), and reads of Claude Code's own session files (C-65).
- **Relay bookkeeping:**
  - `relay.py status` prints DEAD for a run that never started (C-68);
  - Codex reviewer-subagent calls are missing from the relay logs (C-69);
  - guard refusals are labelled MCP failures (C-100);
  - harness telemetry sat in a folder the agent could read (C-101).
- **Persona artifacts:**
  - a wrong calendar objection (C-102);
  - a blocked-download premise that did not hold for the agent (C-103);
  - user notes offset by one turn (C-104);
  - the public UCI dataset's identity leaking into a persona's deck (C-107).
- **Simulation details in records:**
  - simulation paths in project records (C-106);
  - the operator's real name and email used for the retail-B agent's commits (C-110): headless Claude Code exposed the logged-in account's identity to the agent, which passed it to `git -c`; the commits stayed in the local simulation folder.

## Compared with Oct 15

### By Oct 15 finding area

| # | Oct 15 area | Now | Evidence |
|---|---|---|---|
| 1 | Package shaped for the format, not the audience | **Improved** | A checked, audience-facing methods note shipped in every run (taxi-A about 400 words; taxi-B's released note 506 words). Appendices were used without friction, CSVs came out rounded, and label collisions were flagged. Still open: note length is not checked against the brief (C-70); the 15-word headline cap (C-13); no readability pass (C-33); the default storyline moves supporting slides (C-40); tolerance wording in audience text (C-10) |
| 2 | "Deck package" means an outline, learned late | **Fixed** | The README's "What you get" section and START-HERE explain it; the taxi-A user accepted the outline citing both. co2-A's doubt about build order came from the agent's own next-step text (C-52, rejected). New minor defect: START-HERE contradicts itself (C-50) |
| 3 | Approval stops before the first draft | **Improved** | Users picked the checkpoint mode, and agents ran installs themselves. Still open: commit reminders repeat (C-30), and status stays read-only when the same message asks for edits (C-32). The new "answered" problem (C-04) is counted under area 4 |
| 4 | Internal mechanics leak into chat | **Persists** | C-02 hit 6/6 runs as major. Fixed: the ledger and quality ID collision (now `DQ-NNN`), and questions announced but not asked. Changed but not fixed: the footer now counts the user's questions, but "answered" means ledger status (C-04), and status still mixes findings with questions (C-48). `SKILL.md` links recurred in 3/3 Codex runs (host-caused, C-12) |
| 5 | Presentation edits cost analytical rework | **Improved** | No run reported an unrelated edit staling every result, and top-ten charts used row selection. Reruns still came from unit rescaling (C-23), double rounding (C-24) and late reconciliation checks (C-07). Number and claim false positives persist (C-09, C-34) |
| 6 | Review is expensive and checks form more than substance | **Regressed** (cost), **persists** (substance) | Oct 15's most was 11 rounds; now 15, 21 and 38 full reviews in the B runs (C-01). Verdicts flip on unchanged text (C-17). Users still catch what reviews miss (C-11). The same over-literal co2-B rule recurred (C-06). New: tolerance wording (C-10) and repairs frozen unseen (C-15). Fixed: unsupported "checked" sentences are now caught |
| 7 | First-pass answers run ahead of the evidence | **Persists** | Untested explanations across three retail-B replies and one taxi-B reply (C-18); thresholds set after results (C-14); co2-B's coverage gap handled badly again (C-20); chat figures changing base (C-45) |
| 8 | Codex agents skipped the scoping interview | **Fixed** | All three Codex agents asked their scope questions in reply 1. Minor remainder: the four-decision cap bundles choices (C-58) |
| 9 | Setup and environment friction | **Improved**, one trap moved | Fixed: the uv install hint, `quality.md` parsing, zip and XLSX landing, routine installs. Moved: the venv trap now sits in MCP setup, which records the server's Python (C-03, all three Codex runs). New with a real MCP host: Claude agents run helpers through the CLI (C-05). Persists: `awb sql` parameter binding (C-16) |
| 10 | Release details | **Improved** | No draft markers were reported, the storage path is shallower, folded revisions are shown first, and the release report lists open caveats. Still open: repairs forced by the release review are frozen unseen (C-15); nested names go unexplained (C-51); status hides caveats (C-71); a repository with no commit needs commit, rerun and commit to fix provenance (C-56) |
| 11 | The README | **Improved** | All six users praised the quick-start: four by name, and all six found its first-message example useful. Still long, admin-heavy and silent on several expectations (C-25), and clean and explore are listed as steps (C-72) |

Of the 58 confirmed findings, 24 persist from Oct 15, 9 are partly fixed and 25 are new. The data also lists 15 Oct 15 items verified fixed with run evidence (`fixed_since_oct15` in `data.json`).

### Scores, turns and wall-clock

| Run | User msgs | Agent turns | Wall-clock (min) | Satisfaction |
|---|---|---|---|---|
| taxi-A | 12 → 9 (-3) | 11 → 8 (-3) | 136 → 59.5 (-77) | 8 → 9 (+1) |
| taxi-B | 9 → 8 (-1) | 8 → 7 (-1) | 87 → 95.9 (+9) | 7 → 7 (0) |
| co2-A | 10 → 7 (-3) | 9 → 6 (-3) | 77 → 50.4 (-27) | 8 → 8 (0) |
| co2-B | 7 → 9 (+2) | 6 → 8 (+2) | 70 → 142.9 (+73) | 7 → 7 (0) |
| retail-A | 10 → 8 (-2) | 9 → 7 (-2) | 96 → 49.4 (-47) | 8 → 8 (0) |
| retail-B | 7 → 8 (+1) | 6 → 7 (+1) | 71 → 75.2 (+4) | 7 → 8 (+1) |
| **All six** | 55 → 49 (-6) | 49 → 43 (-6) | 537 → 473 (-64) | mean 7.5 → 7.8 |
| A mean | 10.7 → 8.0 | 9.7 → 7.0 | 103 → 53 | 8.0 → 8.3 |
| B mean | 7.7 → 8.3 | 6.7 → 7.3 | 76 → 105 | 7.0 → 7.3 |

- **Answer accuracy.** On Oct 15 every spot-checked figure matched, and one narrative reconciliation claim was false (co2-B). This time all 30 answers were correct under triple verification. The same class of narrative error recurred in co2-B: a claim about how the source builds a series, and misleading wording about missing years (C-11, C-20).
- **Wall-clock is confounded.** Oct 15 relayed every message through a model orchestrator; this run used a script, so part of the A-run speedup is the harness. The B-run slowdown happened despite the faster relay, and the review loop explains most of it (C-01).
- **Variant B is not like-for-like.** Its agent is now real Claude Code with an MCP server, where Oct 15's was a subagent imitating a host.

## Limits of this study

- **Not real users.** Both roles were models. Personas front-loaded definitions and package answers (C-29), which shortened scoping and hid any questions the agents might have skipped.
- **Pre-approved tools.** The harness auto-approved Bash and the awb MCP tools, so permission-prompt cost was not measured. Copilot was not tested; statements about it are inferred from its documented approval model.
- **One run per cell.** No figure here is a measured rate.
- **Model judges.** The skeptics' verdicts are model judgments. The narrowed versions above follow their corrections where they found a claim overstated.
- **Blind recomputes picked their own thresholds.** That explains ten of the 12 answers that grade as "differs by definition". The other two, retail-A Q1 and Q2, trace to the agent's undisclosed sign rule for one cancellation line. The grader resolved each against the transcript.
- **Mislabelled member IDs.** Some consolidated `member_ids` in `data.json` do not match the per-run `findings.json` files; the evidence was checked against the files.
