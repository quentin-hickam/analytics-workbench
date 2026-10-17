# UX simulation re-run, 2026-10-17: comparison with 2026-10-16

The Oct 16 study (`docs/ux-simulation-2026-10-16/README.md` and `proposed-issues.md` in the repository) became issues #84 to #94. PRs #95 to #105 fixed them and merged as #106. This re-run repeats the study on a release built from `main` at `1677d19`. It keeps the same three datasets, persona briefs, end point and role swap, and the same harness apart from three changes listed under Method. It answers the maintainer's main question first, then reports what changed since Oct 16.

- The finding list for the maintainer, grouped into PR-sized proposed issues, is in [findings.md](findings.md). Nothing is filed.
- The raw data behind this report (run results, answer grading, the review-loop analysis, consolidated findings, both skeptics' verdicts on every finding and every claim) is in [data.json](data.json).

## Bottom line: is the package review still stuck in a perfectionism loop?

**No. The loop is bounded in all six runs.** Every run had exactly one full review, no request ran a third review, and every run's last review passed. The bound comes partly from a hard cap rather than from reviews converging, and part of the old cost now lands on the user as decisions.

| Run | Agent | Reviews (full + scoped) | Reviews per review request | Review and repairs, share of agent time | First review start to turn end | Longest wait | Later rounds | Two-review cap | Open problems handed to the user |
|---|---|---|---|---|---|---|---|---|---|
| taxi-A | Codex | 3 (1 + 2) | 2, 1; release reused the receipt | 4.9 of 59.8 min (8.2%) | 10.1% | 14.7 min (full draft) | Clean. Round 1 found 2 brief gaps the user later called real, and 1 rule-driven false positive | Never triggered | None |
| taxi-B | Claude | 4 (1 + 3) | 2, 2; release reused the receipt | 10.1 of 40.4 min (25%) | 27% | 13.4 min (full draft) | Round 2 of the draft found 2 wording problems that round 1's repair had created | Triggered once (reply 5); agent stopped | 2 wording problems with a recommended repair; settled in the user's next message |
| co2-A | Codex | 3 (1 + 2) | 2, 1; release reused the receipt | 3.1 of 37.0 min (8.4%) | 16.5% | 10.4 min (full draft) | Clean after round 1 (1 tolerance-placement problem) | Never triggered | None |
| co2-B | Claude | 5 (1 + 4) | 2, 2, 1 | 8.1 of 29.1 min (28%) | 34% | 10.2 min (full draft) | Round 2 of the draft found 7 problems: 1 new substantive, 2 repeats the agent had held back for the user, 4 wording items (2 caused by the agent's own repair) | Triggered once (reply 4); agent stopped | 7 problems as 3 decisions; the user approved all three in the next message |
| retail-A | Codex | 4 (1 + 3) | 2, 1, 1 | 4.0 of 61.1 min (6.5%) | 9.7% | 17.5 min (analysis turn); 8.7 min longest packaging wait | Clean after round 1 (3 problems, all in builder-only text) | Never triggered | None |
| retail-B | Claude | 5 (1 + 4) | 2, 2, 1 | 8.7 of 35.2 min (25%) | 30% | 11.7 min (full draft) | Round 2 of the corrections request found only the one citation problem held back for the user | Stop condition met once (reply 6); the agent cited the unchanged-problem rule | 1 citation fix in internal `methodology.md`; the user approved and said such fixes need no decision |

"Review and repairs" runs from each request's first review start to its last recorded review, including the repairs between rounds. Neither share column counts the feedback turn. Figures come from the review-loop analysts in `data.json` (`runs[].review_loop`) and `SIMS/kit/reviewloop.py`, checked by the skeptics on W-03 and W-04.

- **Compared with Oct 16.** In the three runs where Claude was the agent, Oct 16 ran 21, 38 and 15 full reviews. This run recorded 4, 5 and 5 reviews in total, one full in each (W-01, upheld). Oct 16's packaging turns took 82%, 94% and 79% of agent time in those runs. On the same `measure.py` they now take 57.5%, 68.1% and 67.6% (W-03). Oct 16 did not time review rounds separately (there were no per-line timestamps), so its 79-94% is the share of whole packaging turns, which were mostly review. Review and repairs now take 25%, 28% and 25% of agent time. The Codex-agent runs did not loop on Oct 16 either (4, 6 and 4 full reviews then; 3, 3 and 4 reviews now), so the Claude-agent runs carry most of the evidence that the convergence fix works (W-02).
- **The cap held, and it did part of the work.** No request started a third review. Three requests, all in Claude-agent runs, ended on a second review that still reported problems: taxi-B reply 5 (2 problems), co2-B reply 4 (7) and retail-B reply 6 (1). Each time the agent stopped and took the problems to the user with a recommended repair. In retail-B the agent named the unchanged-problem rule, not the cap, as its reason (W-08).
- **Later rounds found less each time, but the reviewer is strict about form.** In every request the second review found fewer problems than the first, or none. The second rounds that still failed found problems the first repair had created or items the agent had held back for the user, plus one new substantive gap in co2-B. Across the Claude-agent runs the reviewers reported 68 problems (taxi-B 27, co2-B 22, retail-B 19). By line-level reading, roughly 30 to 50 of them were about form: how a check is cited, "exactly" and approximate-match wording, record words and style rules (U-01). Reviewers still raised new problems on lines an earlier full review had read and passed: three "cut" lines in co2-B and a wrong citation in retail-B (U-02). The Codex-agent reviews reported 7 problems in 10 reviews, all from the first full review of each draft (W-09).
- **Drafts and releases.** No release turn ran a full review, and every release 001 manifest records the review as scoped with nothing accepted. taxi-A, taxi-B and co2-A released on a current receipt with no review. co2-B, retail-A and retail-B each ran one scoped review at release, clean on its first pass. In co2-B and retail-A, a review rule added at release made the receipt stale, and in retail-B the review followed a one-line citation fix the user had approved. No release review found a problem, so the new rule that a repair is shown to the user before release was never exercised (W-07).
- **Waits and cost.** The longest single waits in the Claude-agent runs fell from 58, 43 and 40 minutes to 13.4, 10.2 and 11.7 minutes, each now the full-draft turn (W-05, upheld). The waits shrank mainly because the slowest Oct 16 turns ran 15, 12 and 14 reviewers, against 2 each now, at a similar time per reviewer. Claude-agent cost fell 63%, from $104.61 to $39.08 (W-17, upheld). The drop is in packaging: packaging turns fell from about $90 to about $23, and reviewer runs from 74 to 14.
- **Where the cost went.** Several confirmed defects come from the review fixes themselves. The stop rules hand trivial or self-made problems to the user (C-04). The tolerance and citation rules make repairs delete true context (C-03). The brief-coverage check pushes internal verification questions onto slides (C-12). Adding a review rule makes the passed review stale and forces another one (C-24). The imperative rule flags builder instructions and requested recommendations (C-51). The co2-B user ranked "Review became an extended editorial approval process" a major pain point. The retail-B user called the citation question "the clearest unnecessary gate" and rated it minor, and the taxi-B user called it a small approval loop. No Codex-agent run hit a review stop (R-01).

## The rest of the bottom line

- **All six runs reached the end point again** (U-11, upheld). Each user accepted all five answers (taxi-A's Q3 implicitly), asked for `awb-status`, reviewed the draft, and saw release 001 made. Every storage copy is byte-identical to the in-project release.
- **All 30 answers were correct.** No grader found a mismatch, and all 30 referee spot-checks reproduced the agent's figures under the agent's definitions (U-09).
  - 13 were graded as matches and 17 as differing by definition, against 15 exact, 3 within rounding and 12 by definition on Oct 16. The shift says nothing about the release: graders labelled similar cases differently, the blind recomputes chose different thresholds, and users agreed different definitions.
  - In most of the 17, the blind recomputes picked their own thresholds or revenue basis while the agent applied the agreed ones. Graders flagged an undisclosed choice by the agent in four answers: retail-B Q3 (a purchase needs a goods line; January's cohort is 368 against 383 on an any-line basis, the same table as Oct 16), retail-A Q3 (postage-only invoices count as repeats; +0.3 points), retail-B Q4 (case-sensitive stock codes; 1,720 products against 1,715) and taxi-A Q2 (a comparison group the user never explicitly agreed; 11.73 against 11.75 minutes). None changes a headline.
- **Wall-clock fell 41%, all of it in the Claude-agent runs.** Conversation time fell from 473.3 to 277.1 minutes. The Claude-agent runs fell from 314.0 to 111.8 minutes. The Codex-agent runs rose slightly, from 159.3 to 165.3 (W-12). One run per cell; part of co2-B's drop comes from a shorter user path.
- **Messages and satisfaction barely moved.** Users sent 52 messages against 49. The Codex-agent runs rose by 5 and the Claude-agent runs fell by 2 (R-07, W-14). Mean satisfaction was 7.83 out of 10 in both studies. Only taxi-A (9 to 8) and co2-B (7 to 8) moved, which is within run-to-run noise (U-08).
- **47 product findings survived both skeptics** (11 major, 36 minor). 17 more are contested and 4 were rejected. 11 harness findings are listed separately and not scored. The fall from Oct 16's 58 is not like-for-like: raw referee findings fell only 13% (190 to 166), the consolidator merged more coarsely, and the skeptics judged some recurring issues differently. Confirmed major findings fell from 23 to 11, which is the firmer signal (W-18).
- **Oct 16's eleven issue areas.** #84 is bounded as a cost problem, though the gate is not yet reliable. #85, #88, #91 and #92 improved. #89 and #90 improved in parts. #86, #87, #93 and #94 persist in part. No area regressed overall, but Oct 16 C-08 (instruction length) grew by its own measure, from 11,749 to 14,727 words. The fixes introduced at least nine confirmed product defects (W-35).
- **The result is 11 PR-sized proposed issues** in [findings.md](findings.md), led by the review brief and the review stop rules. None is filed.

## Method

Everything not listed here is unchanged from the Oct 16 study; see its Method section (`docs/ux-simulation-2026-10-16/README.md`, copied at `SIMS/oct16-ref/README.md`).

| | Detail |
|---|---|
| Release under test | Built from `main` at `1677d19`, which includes #106 (PRs #95 to #105). A copy is at `SIMS/release/analytics-workbench-skills/` |
| Datasets, questions, end point | Unchanged: NYC TLC yellow taxi trips (Jan and Jul 2024, local files), Our World in Data CO2 (by URL), UCI Online Retail II (by URL); five questions each in the same persona briefs (`SIMS/kit/personas/`, byte-identical to Oct 16) |
| Variants | Unchanged. A: Claude (Opus) played the user and Codex the agent. B: Codex played the user and Claude (Opus) the agent. Same model and CLI versions as Oct 16 (claude-opus-5-5 on Claude Code 2.1.301; gpt-6.1-sol on codex-cli 0.159.3) |
| Harness | Unchanged apart from three changes: (1) each agent's git identity is pinned to the simulated identity through environment variables plus one prompt line, because on Oct 16 a Claude agent passed the logged-in account's identity to git; (2) every relay log line gets a wall-clock timestamp (`agent-NNN.ts`) so review rounds can be timed; (3) a new review-loop analyzer, `SIMS/kit/reviewloop.py` |
| Referees | One per run. Each verified the end point, spot-checked answers against the landed data, audited isolation and identity, and wrote `SIMS/<run>/feedback/orchestrator-report.md` and `findings.json` |
| Review-loop analysis | One analyst per run timed every review round from the relay logs and `.ts` stamps, read every recorded report (`SIMS/<run>/review-reports/`), and classed each problem as substantive, cosmetic or false positive |
| Answer grading | Each answer recomputed blind twice, in DuckDB and in pandas (`SIMS/grade/grading/<run>-sql/`, `<run>-pandas/`), then graded against the definitions the user agreed in the transcript (`<run>-compare/`) |
| Finding triage | Findings were tagged product or harness twice, merged across runs, and each product finding faced two skeptics: one looking for a harness cause, one checking whether the release text causes it. **Confirmed** means both called it a product defect, **rejected** means neither did, **contested** means they split |
| Claims | Every win, regression or unchanged result claimed against Oct 16 faced two skeptics: one re-deriving the evidence, one looking for confounds. 5 claims were upheld, 78 weakened and 1 contested. This report states weakened claims in their corrected wording |

**Paths.** Evidence paths are written `SIMS/<run>/...`, where `SIMS` is the simulation folder that holds `grade/report/`. Release paths such as `awb-package/references/review.md:43` are relative to the release root. `README.md:NN` refers to the release README.

In this repository the copied evidence is flattened, as on Oct 16: `SIMS/<run>/feedback/<file>` is `<run>/<file>`, `feedback/orchestrator-report.md` is `<run>/referee-report.md`, `human/notes.md` is `<run>/human-notes.md`, and `<run>/review-loop.txt` is the output of `kit/reviewloop.py` for that run. The kit is in `kit/`. Relay logs, `.ts` stamps, recorded review reports, project folders, storage and grading scripts were not copied; their figures are in `data.json`. Absolute paths, the operator's identity and third-party contact details in copied files are replaced by placeholders such as `SIMS`, `<user>` and `<email>`.

**IDs.** `C-NN` is a consolidated finding in this study (`consolidated` in `data.json`). These numbers collide with Oct 16 IDs of other meanings, so Oct 16 findings are always written "Oct 16 C-NN". `W-NN`, `R-NN` and `U-NN` are claims (wins, regressions, unchanged) in `claims` in `data.json`. Per-run IDs such as `taxi-B-04` come from each run's `findings.json`. Skeptics noted that some cited member IDs do not match those files; the evidence was checked against the files.

## Results by run

| Run | User / agent | User msgs | Agent turns | Wall-clock | Satisfaction | End point | Answer accuracy | Spot-check | Reviews | Review share |
|---|---|---|---|---|---|---|---|---|---|---|
| taxi-A | Claude / Codex | 10 | 9 | 62.6 min | 8/10 | met | 5/5 correct, all by definition; undisclosed: Q1 holiday Mondays kept with only a generic caveat (July's Monday gain is +10.1% without them, not +13.3%), Q2 comparison group | all 5 match; one chat rounding slip (91.85% for 91.84%), release correct | 3 | 8.2% |
| taxi-B | Codex / Claude | 8 | 7 | 42.9 min | 7/10 | met | 5/5 correct, all by definition; no material undisclosed choice | all 5 match | 4 | 25% |
| co2-A | Claude / Codex | 9 | 8 | 39.2 min | 8/10 | met | 5/5 match; Antarctica counted in the 216-country cohort without being named (no ranking changes) | all 5 exact | 3 | 8.4% |
| co2-B | Codex / Claude | 7 | 6 | 31.2 min | 8/10 | met | 5/5 match | all 5 exact | 5 | 28% |
| retail-A | Claude / Codex | 10 | 9 | 63.5 min | 8/10 | met | 5/5 correct, all by definition; undisclosed: Q3 postage-only repeats, Q4 case-sensitive codes | all 5 match | 4 | 6.5% |
| retail-B | Codex / Claude | 8 | 7 | 37.7 min | 8/10 | met | 5/5 correct: 3 match, 2 by definition; undisclosed: Q3 goods-line purchase rule, Q4 case-sensitive codes | all 5 match | 5 | 25% |

- **Counting.** User messages include the closing DONE line, which is never relayed. Agent turns are replies and leave out the feedback turn. Wall-clock runs from relay start to DONE (`SIMS/<run>/relay/state.json`). This matches the Oct 16 table.
- **Agent cost** was recorded for the Claude agents only: taxi-B $14.15, co2-B $11.67, retail-B $13.26.
- **"By definition"** means the blind recomputes chose their own thresholds or basis while the agent applied what the user agreed; the grader reproduced the agent's figures under the agreed rules. The undisclosed choices listed are those the graders found the user never saw. Details are in each run's `compare` block in `data.json`.
- **retail-A Q4.** The grader counted 2,482 eligible products against the agent's 2,483. Product 20619 sums to exactly £1,000.00; float summation puts it on either side of the threshold, and an exact decimal sum includes it, as the agent did (W-16).

## The review loop in detail

### Per run

- **taxi-A (Codex agent).** The full draft (reply 7, 14.7 min) ran one full review and one scoped review. The full review found three problems. Two were brief gaps the user later called real: the airport slide gave medians but no fare spread, and the ranking table lacked occupied hours and active dates. The third came from the brief-coverage rule: an internal no-mix-up check answered only in speaker notes had to move onto a slide, and the user had it removed in the next message (C-12). The scoped re-review was clean in 32 seconds. The corrections request (reply 8) ran one clean scoped review; the release (reply 9) reused the receipt. Most of the draft turn's cost came before the review: new projection results built only to select chart rows, numbers-check rewrites, and an export that deleted every chart. Review plus repairs took about 3.9 of the 14.7 minutes.
- **taxi-B (Claude agent).** The full draft (reply 5, 13.4 min) drew 21 problems in the full review. The analyst classed 8 as substantive (an untested claim that the limitations change nothing, a July tip peak that is really a tie, a Newark fare near $90 where the July median is $82.52) and 13 as citation and house-rule items. Repairing them took 0.65 minutes. The scoped review then found two wording problems that the repair itself had created. The agent stopped, started no third review, and asked the user to choose "lack a passenger count". The corrections request (reply 6) found one rule violation and three narrative problems, including a real contradiction between the user's new flat-fare wording and the project's own source record; the second review was clean. The release reused the receipt. The user still caught three wording errors no review flagged (C-06).
- **co2-A (Codex agent).** The full draft (reply 6, 10.4 min) drew one problem: a tolerance phrase in the donor note. The repair dropped the true statement that the EU totals agreed, because the rules allow no tolerance wording in the note, even a pre-recorded one (C-03). The scoped re-review was clean. The rounding request (reply 7) ran one clean scoped review, after the agent built a new recorded result only so "about 8.6 billion tonnes" would trace (C-08). The release reused the receipt.
- **co2-B (Claude agent).** The full draft (reply 4, 10.2 min) drew 9 problems, 4 substantive, including a "largest shares" overclaim and an unsupported claim that no limitation changes the rankings. The agent held back two of them, the word "cut" in headlines the user had approved, for the user. The scoped review found 7 problems: one new substantive (no comparison group for Greece's coal fall), the two held-back items, and four citation items, two caused by the agent's own repair. The cap stopped repairs, and the user approved three decisions in the next message. The corrections request (reply 5) found 3 violations and 3 narrative problems, including three more "cut" lines that earlier passes had missed; the agent repaired those itself, against the rule that sends them to the user. The second review was clean. At release, adding a rule made the receipt stale and forced one clean scoped review.
- **retail-A (Codex agent).** The full draft (reply 7, 8.7 min) drew three problems, all in builder-only text: an uncited "verified", an uncited "every result passed", and a chart-axis instruction flagged as an imperative (C-51). Repairs took 0.15 minutes; the scoped re-review was clean. The corrections request ran one clean scoped review. At release, two new review rules made the receipt stale and forced a 12-second scoped review. The run's longest wait, 17.5 minutes, was the analysis turn.
- **retail-B (Claude agent).** The full draft (reply 5, 11.7 min) drew 15 problems; the analyst classed 9 as substantive. Four of them were one root cause: an "exactly" revenue match where the recorded gap is -4.38e-06 pounds. Others included the 22.5% figure on the wrong base and an uncited claim of no transactions over Christmas. The scoped re-review was clean, though it missed a wrong citation in a line it had in scope. The corrections request found three problems, then one: that same citation, marked "unchanged since the prior review", which the rules sent to the user. The user approved and said routine citation fixes need no decision. The release ran one clean scoped review.

### Across runs

- **Rounds per request.** At most two in every request, full first and scoped after, in every run.
- **First-round problem counts depend on the reviewer model.** Claude reviewers raised 21, 9 and 15 problems on first full review; Codex reviewers raised 3, 1 and 3, and every Codex second review was clean. The stop rule therefore fired only in the Claude-agent runs, and the Codex-agent runs are not a control for it (R-01).
- **Reviewer independence still depends on the agent.** All three co2-A reviewers and retail-A's two drafting-turn reviewers were Codex forks with `fork_turns: "all"`. They opened with the session's user and agent messages, but not the writer's tool calls, against `review.md`'s "Start a fresh subagent". taxi-A's reviewers used `"none"`. The release never says what "fresh" means for Codex (U-04).
- **Time before the first review.** In the drafting turn, the time before the first review started was 62-71% of the turn for the Codex agents (10.4 of 14.7, 7.3 of 10.4, 5.4 of 8.7 min) and 47-53% for the Claude agents (7.2 of 13.4, 5.0 of 10.2, 5.5 of 11.7 min). That time went mostly to drafting, exports, check-draft repairs and record updates, not to reading instructions (U-05). This reverses Oct 16, when most packaging time went to the review loop.
- **What users saw.** During each wait the user saw nothing, since the agent cannot be interrupted mid-turn. Claude agents' progress lines arrived inside the final reply. No user complained about wait time, but all three Codex-played users said they could not judge elapsed time. The co2-B user called review "an extended editorial approval process" (major). The retail-B and taxi-B users called the escalations minor approval gates. The taxi-A user credited the reviewer with real catches and complained about the slide bullet it forced.
- **Copilot.** No run used GitHub Copilot. The release ships `awb-package-reviewer` as a VS Code custom agent with only file read, search and `awb/read` tools (`awb-package/assets/awb-package-reviewer.agent.md`). How the bounded loop behaves there is inferred from the release design, not tested.

## Compared with Oct 16

### By issue area

Only claims marked upheld or weakened are used, in their corrected wording. The status labels follow W-35 and the per-area claims.

| Issue | Oct 16 area | Now | Evidence |
|---|---|---|---|
| #84 | Package review gate converges (Oct 16 C-01, C-15, C-17) | **Improved: the loop is bounded; the gate is not yet reliable** | Claude-agent runs went from 21, 38 and 15 full reviews to 4, 5 and 5 reviews, one full each, at most two per request (W-01, upheld). The new stop rule partly enforces the bound: three requests ended with problems sent to the user (W-08, W-19). The Codex runs did not loop on either date (W-02). Later reviews still flagged unchanged lines an earlier full review had passed, though these are not the same-scope flips of Oct 16 C-17 (U-02). No release review found a problem, so the show-before-release guard (Oct 16 C-15) was never exercised (W-07). New cost: C-04 (R-01) |
| #85 | What the review checks (Oct 16 C-06, C-10, C-11, C-33, C-70) | **Improved, with side effects** | Fixed: review rules are now added only after the user says yes, 10 rules in 5 runs (W-21); the methods note now holds to the recorded length without the user stepping in (W-23); no tolerance appeared in a visible slide bullet or methods note, though co2-A's phrase stays in speaker notes (W-22). Partly fixed: the review reads the brief and caught real gaps in taxi-A (W-11), but still misses meaning errors (U-03); display precision is checked only when the user states one, and the closed readability list lets technical prose and typos through (U-12, U-13). Side effects of the fix: C-03, C-12, C-24, C-51 (R-02 to R-05) |
| #86 | Conversation (Oct 16 C-02, C-04, C-18, C-30, C-45, C-58) | **Persists in part** | Internal vocabulary reached the user in 6/6 runs, all rated minor now against major on Oct 16 (U-15). Untested explanations recurred in taxi-B and retail-B (U-16). Footers now mark answers provisional; the co2-A and retail-A users saw full answers before the headline preview, but both had asked for the analysis as its own step, a path that also avoided the problem on Oct 16 (W-24). All three Claude-agent first reports gave highlights, not full tables (U-17). The once-a-session commit guard was not shown working (U-19). Chat figures: one 0.01-point rounding slip (U-21). Unrelated choices are no longer bundled under one number in co2-B and retail-B (taxi-B still bundled them), but the four-decision cap defers simple choices to a second round (U-14) |
| #87 | Analysis discipline (Oct 16 C-07, C-14, C-20, C-41, C-53, C-56, C-62, C-75) | **Persists in part** | Investigation views were used in 3/6 runs; retail-A and co2-A still copied screening CTEs into 16 and 10 query files (W-25). The C-53 and C-75 fixes shipped but were not exercised. Joins read "not assessed" on 24 of 25 Claude-agent results (U-25). A threshold left out until after results clearly recurred only in taxi-A (U-23). co2-B's coverage gaps were disclosed at the first answer but worded as zero, partly fixed (U-24). Agents chose commit-and-rerun cycles that export does not require (U-26). New: C-65; C-61's rerun demotion was already part of Oct 16 C-07 (U-22, U-26) |
| #88 | check-draft reading (Oct 16 C-09, C-22, C-23, C-24, C-34, C-39, C-55) | **Improved, unevenly** | Fixed: co2-A's CO₂ chart headers passed (Oct 16 C-22). Did not recur: blank lines in chart specs (Oct 16 C-39) and double rounding (Oct 16 C-24, most likely because of #87's full-precision guidance). Partly fixed: number false positives still hit 5/6 runs in new forms (U-27). Persists in part: co2-A still recorded a new result for a rescaled figure, though check-draft did not strictly require it (U-28). New false alarms: `precision_warnings` on a genuine 0.1875, and export's own `[scale]` divisor text (W-26, W-27) |
| #89 | Headline limit and gate integrity (Oct 16 C-13, C-21) | **Improved in part** | No run edited a helper or package-format file, and no manifest carries `helper_drift_confirmed`, but the pressure behind Oct 16 C-21 did not recur, so the gate-integrity half was not exercised (W-28). The limit is disclosed and a long headline is a warning the user can accept. retail-B used that path cleanly; retail-A wrote the acceptance itself without telling the user. The preview still counts no words (U-29) |
| #90 | Package instructions, step order, files (Oct 16 C-08, C-27, C-37, C-40, C-50, C-51, C-77, C-86) | **Improved, unevenly; one item regressed** | Fixed: START-HERE lists `methodology.md` once (Oct 16 C-50). Fixed for location and release exclusion: the preview file (Oct 16 C-37). Not exercised: export's draft-folder fix (Oct 16 C-27), because every run created the folder for the preview first, and `--show` (Oct 16 C-77). Partly fixed: storyline linkage (Oct 16 C-40). Regressed by Oct 16's own measure: the four package instruction files grew from 11,749 to 14,727 words (Oct 16 C-08) (W-29, W-30, U-05, U-31) |
| #91 | Setup, MCP routing, `awb sql` (Oct 16 C-03, C-05, C-16, C-43) | **Improved** | All six agents created `.venv` first and passed the new `interpreter` argument; setup recorded `.venv/bin/python` on the first try (W-31). Claude agents' main-thread Bash-to-MCP helper calls went from 89:10, 83:32 and 70:10 to 6:94, 13:57 and 43:40; retail-B still ran about 60% of helper invocations through the CLI (W-32). `sql` now binds settings; `profile` does not (U-32) |
| #92 | Data landing and cleaning (Oct 16 C-19, C-26, C-42, C-54, C-73, C-74, C-76, C-80) | **Improved** | co2-B reran the exact Oct 16 integer-year scan without error (Oct 16 C-54). retail-A told the user at landing that UCI sends no version headers, though upstream changes still cannot be detected (Oct 16 C-74). taxi-A recorded access notes for the TLC pages that returned 403 (Oct 16 C-76) (W-33). Both retail scans found the cross-sheet overlap; retail-A asked before removing it, in a turn where the user had asked to review treatments first (W-34); retail-B removed it before asking again (U-33, C-11). The EDA scan still floods a wide panel (U-34, C-70) |
| #93 | awb-status (Oct 16 C-31, C-32, C-48, C-71, C-85) | **Persists in part** | The "indeterminate at date precision" wording appears in no run (U-36). Users still could not map finding counts to their questions in taxi-A and retail-A, and no run produced the per-question screen with suggested requests (U-35, C-30). A history entry stamped a second after the state gave one false "out of date" (C-67) |
| #94 | README (Oct 16 C-25, C-72) | **Persists in part** | Shorter: 4,718 words against about 5,345. In 4 of 6 runs users called it long, and 5 of 6 wanted the install material moved out (U-37, C-14) |

### Scores, turns, wall-clock and cost

| Run | User msgs | Agent turns | Wall-clock (min) | Satisfaction | Agent cost |
|---|---|---|---|---|---|
| taxi-A | 9 → 10 | 8 → 9 | 59.5 → 62.6 | 9 → 8 | not recorded |
| taxi-B | 8 → 8 | 7 → 7 | 95.9 → 42.9 | 7 → 7 | $35.51 → $14.15 |
| co2-A | 7 → 9 | 6 → 8 | 50.4 → 39.2 | 8 → 8 | not recorded |
| co2-B | 9 → 7 | 8 → 6 | 142.9 → 31.2 | 7 → 8 | $48.38 → $11.67 |
| retail-A | 8 → 10 | 7 → 9 | 49.4 → 63.5 | 8 → 8 | not recorded |
| retail-B | 8 → 8 | 7 → 7 | 75.2 → 37.7 | 8 → 8 | $20.72 → $13.26 |
| **All six** | 49 → 52 | 43 → 46 | 473.3 → 277.1 | mean 7.83 → 7.83 | $104.61 → $39.08 |
| A mean | 8.0 → 9.7 | 7.0 → 8.7 | 53.1 → 55.1 | 8.33 → 8.0 | |
| B mean | 8.3 → 7.7 | 7.3 → 6.7 | 104.7 → 37.3 | 7.33 → 7.67 | |

- **Same measures, same models.** Both studies count messages and wall-clock the same way, with the same `measure.py`, models, CLI versions, personas and user rules.
- **The variant gap reversed** (W-13, upheld). The Claude-agent runs now average 37.3 minutes against 55.1 for the Codex-agent runs. Nearly all of the change is the Claude-agent runs' packaging time falling to about the Codex level.
- **Codex-agent runs.** The mean barely moved. co2-A fell 11.2 minutes; taxi-A rose 3.1 and retail-A 14.1. These moves follow how much work each user asked for, and the Codex backend was about 14% faster per output token on Oct 17, so flat wall-clock does not show the release left Codex time unchanged (U-07). retail-A's slowdown sits in intake and analysis, partly from extra user requests; strict packaging time was about flat, so it is not a demonstrated regression (R-06).
- **Messages.** The Codex-agent runs' five extra rounds came mostly before any answer was shown, from separate landing and cleaning sign-off stops (R-07).
- **Satisfaction.** Scores track which model plays the user (Claude users 8 to 9, Codex users 7 to 8) and barely register the large drop in Claude-agent wait time (U-08). taxi-A's drop from 9 to 8 cites the same issues Oct 16's user raised when scoring 9 (R-08).

### Fixed since Oct 16 (consolidator's list)

The consolidator listed 17 Oct 16 items as fixed, with run evidence (`fixed_since_oct16` in `data.json`). No skeptic reviewed this list, and it overlaps the partly-fixed group: Oct 16 C-01 and C-10 appear here and also behind confirmed findings that are only partly fixed (W-18). The items with direct run evidence: the review loop's length (Oct 16 C-01), release repairs not frozen unseen (C-15, not exercised), the recorded project interpreter (C-03), rules saved only on the user's yes (C-06), tolerances out of audience text (C-10), the gate code left unedited (C-21), CO₂ chart headers (C-22), no double rounding (C-24), export creating the draft folder (C-27), a defined preview file (C-37), no chart-spec blank-line rows (C-39), investigation-local shared SQL (C-41), README storage lines (C-43, though they were present on Oct 16 too), a single START-HERE listing (C-50), methods note length (C-70), the upstream-check notice (C-74) and documentation access notes (C-76).

### Claims not counted

- **Contested: W-10.** The claim that no review reversed an earlier finding, and that no review-driven edit followed a user's request to stop wording changes. The evidence skeptic weakened it; the confound skeptic refuted it. Later reviews did flag unchanged text that an earlier full review had passed (co2-B, retail-B), and no user in any run asked to stop wording changes, so the second half was never tested.
- **No claim was refuted outright**, but skeptics refuted parts of weakened claims. The main ones:
  - co2-A's "the same ten countries" was accurate, not a misstatement (U-21).
  - "No tolerance reached any released audience text" is false for co2-A's speaker notes (W-22).
  - Oct 16 taxi-B did not ship an 867-word note; that was a draft, and the release was 506 words (W-23).
  - taxi-B's "(provisional)" footer is not new; it appeared on Oct 16 (W-24).
  - The retail-B and co2-A cases do not show thresholds set after the leaders were seen (U-23).
  - retail-B's undisclosed purchase rule did not grow; its cohort table is identical to Oct 16's (U-10).
  - Oct 16's commit-less releases were 4 of 6, not 2 (U-38).
  - The 17 "fixed" items are the consolidator's unreviewed assertion, not a verified list (W-18).
  - Commits do not carry "only" the simulated identity: 24 Claude-agent commits also carry a vendor co-author trailer (W-36).

## Findings, ranked

Ranking weighs how many runs hit a problem against its severity. "n/6" counts runs where a confirmed member appeared. Only confirmed product findings are ranked. Where a skeptic narrowed a finding, the narrower version is stated. Each group matches a proposed issue in [findings.md](findings.md).

### 1. The review brief checks form strictly and meaning loosely (6/6, major)

- **Citation and tolerance wording (C-03; taxi-B, co2-B, co2-A, retail-B).** `review.md:26-28` rejects a data-quality row that cites a saved query, which the release's own `awb-clean` creates. It allows no wording for a true match that is near-exact or within a tolerance recorded only in a judgment detail, and it bans plain words such as "flagged". Agents cleared these by deleting true statements: co2-B dropped its within-1-Mt world reconciliation, retail-B its revenue reconciliation, taxi-B its cash-tip observation (and cut code-0's missing fields to passenger count only), and co2-A moved "within source rounding" out of the donor note. The same reviews also caught real errors, and retail-B's "exactly" really was false against a -4.38e-06 gap.
- **Meaning errors pass (C-06; taxi-B, co2-B, retail-B).** The review's closed checklist (`review.md:22-29`) never compares the narratives' definitions with the brief's agreed definitions, and its source-build check accepts any cited check (one skeptic judged this part weak). taxi-B's trip-time rule narrowed to "zero", base fare was called the meter's fare next to a $70 JFK median, and a count-check sentence read as adding overlapping counts. co2-B's "energy mix" passed both drafting reviews. retail-B's narrower cohort definition went undisclosed in the note. Suggested severity: moderate.
- **Brief coverage forces internal checks onto slides (C-12; taxi-A).** A sanity check the user asked for in chat becomes a represented result whose question is the user's words, and `review.md:27` then demands a visible answer. The user had the bullet removed. The extra scoped review that followed was needed anyway for the user's other corrections.
- **Closed readability list (C-50; retail-A, taxi-A).** retail-A's How we know slide passed a full review with "signed quantity", "grouping keys" and "permitted repeated line occurrences", although the brief said to avoid technical detail. taxi-A's release carries double periods ("6 p.m..") from the agent's time-format regex; the review has no proofreading step.
- **Imperative rule (C-51; retail-A, retail-B).** It flagged a chart-axis instruction no audience sees, and pushed the recommendation the user asked for on the Answer slide into a gerund headline that shipped. A declarative "We recommend" would have passed.

### 2. The review stop rules hand small or self-made problems to the user (5/6, major)

- **C-04 (taxi-B, co2-B, retail-B; retail-A as the no-loop control).** `review.md:35` marks a problem "unchanged since the prior review" by whether the line changed, so it cannot tell a missed problem from one a repair elsewhere created. `review.md:43` sends marked problems to the user and stops after a second failing review. taxi-B got a two-word narrowing its own repair caused; retail-B a citation fix in internal `methodology.md`; co2-B a problem its repair created, bundled into the decision list. co2-B's question about the user's approved "cut" came from the agent's own judgment, not the stop rules. Two of three users rated the escalations minor.
- **Rule workflow (C-24; co2-B, retail-A, retail-B, taxi-B).** `review.md:45` says to ask about a rule and record it before repairing. Corrections arrive with "go ahead", so all four agents repaired first and asked afterwards, and rules arrived a turn late. Adding a rule makes the passed review stale (`review.md:39`), which forced an extra scoped review at release in co2-B and retail-A (under a minute each from start to record). Rules can cover one package or all, not one investigation.
- **The receipt does not check report shape (C-72; co2-A, and reports in taxi-B and co2-B).** `review-receipt record` checks only the last line and row counts, not the `problems` and `errors` lines Brief step 4 asks for. 10 of 24 recorded reports omit them. Every omitted list was empty, so nothing was lost.

### 3. Conversation: untested explanations, undefined codes, incomplete first answers (6/6, major)

- **Untested explanations (C-05; taxi-B, retail-B, retail-A).** taxi-B stated "timing errors", "Long Island or Westchester", code 0 "is" Flex Fare, and a vendor headline that hid vendor 6's 35%. retail-B stated "not product demand" and "Christmas closure". retail-A's released How we know slide turned the user's "plausible" into "confirmed by the e-commerce lead", though the user's own suggested wording had already said "genuine". The rule exists in `AGENTS.md` (line 30) and at the headline checkpoint, but nothing checks the preview, and check-draft's causal regex covers only causal verbs on finding slides.
- **Undefined codes (C-09; taxi-A).** taxi-A's first tipping answer led with 0% Bronx and Brooklyn medians and an undefined "rate-code 99". The scanner treats any column ending in "ID" as a key (`awb-clean/scripts/scan_dataset.py:65`) and skips the placeholder check, so code 99 never reached the cleaning sign-off. The taxi-B half was a harness effect: the simulation's URL rule kept the dictionary from the agent until turn 3.
- **Workbench vocabulary (C-13; 6/6, minor).** Required lines put internals in chat: the recorded interpreter path, the upstream-check notice, finding counts by status. The plain-words rule covers chat only, so files handed to the user (headline previews, a quality proposal) carry result IDs. Claude agents' interim narration is partly a harness effect.
- **Incomplete first reports (C-33; taxi-B, co2-B, retail-B).** No rule says the first results report must show every item a question asks for. taxi-B named 4 of 10 zones; retail-B gave ranges instead of 24 months and 12 cohorts. The request for full tables rode along in a message the user sent anyway.
- **Status line (C-22).** The footer counts only root questions, so taxi-B reported "0 open" while a must-answer decision was pending.
- **SKILL.md links (C-34; 3/3 Codex runs).** Codex's own model instructions ask it to name and quote the SKILL.md behind a pause. The release's counter at `AGENTS.md:32` was in context and lost every time.
- **Commit reminders at release (C-48).** The release report has no item for uncommitted producing or packaging code, and the once-a-session cap blocks a reminder, so retail-A froze release 001 with untracked producer and package-format files unmentioned. co2-B's repeated suggestion was an agent deviation.

### 4. awb-package instructions, preview checkpoint and slide linkage (6/6, major)

- **Instruction load (C-01).** About 13,500 words must be read before `helpers.md` adds 7,011 more. On Codex, reads truncate under the agent's own output caps and repeat after compaction (1 to 5 minutes per packaging turn). Several rules that drive first-review problems live only in the reviewer brief, which the writer reads after drafting: in retail-B, 4 of 15 first-review problems came from rules found only in `review.md`.
- **Required slides (C-23).** The default storyline comes to 9 slides against the persona's "about 8". The README never says the title counts. Each user approved the trade-off.
- **Linkage (C-31).** A missing methodology heading produced four check-draft rows, one with the wrong fix (retail-B). Citing a result first silently changed a slide's primary result (taxi-A).
- **Preview checkpoint (C-49, C-56).** Nothing counts preview words, so retail-B's approved 16-word headline came back at check-draft. No step carries chart forms agreed at the preview into the draft, so retail-B's promised reconciliation table became a bar chart.
- **Priority (C-62).** `awb-scope` sets priorities without asking, and the slide order sorts by them, so taxi-B proposed moving "your two 'should' questions" to the appendix. The user approved.

### 5. Display precision, units and number checks (6/6, major)

- **No audience defaults (C-07; co2-A, taxi-A, co2-B).** Precision is recorded and reviewed only when the user states one. co2-A's donor draft carried 8,645.2 million tonnes and 23.57%, which cost a correction round. Clock format and rounding notes depend on the agent model. Suggested severity: moderate.
- **Rescaled figures (C-08; co2-A).** `[scale]` is per column and rescales the chart too, and rounding works by decimal places only. co2-A recorded a unit-only result for "about 8.6 billion tonnes". Suggested severity: moderate.
- **Number and name checks (C-20; 5 runs).** The reader drops the first value's percent sign in "a%/b%", flags slash-joined time lists, rejects export's own "divided by 1000000000" line, flags a hyphenated result ID used as prose, and pulls the "2" out of "CO2" in rule warnings.
- **Chart rows and roles (C-43).** `@where` takes one column; bar charts have no annotation role.
- **Precision warning (C-69).** It fired on every retail-B export for a genuine 0.1875, with no way to confirm it.

### 6. Data landing and cleaning (5/6, major)

- **Cross-sheet copies (C-11; retail-B).** The example "such as overlapping periods" in `awb-clean/SKILL.md:33` let the agent remove 22,523 copies before asking. The rows were true copies and the user approved afterwards; the harm is process. The scan also reports cross-part copies and within-part repeats as one issue.
- **Scope against data rules (C-39; taxi-B).** `awb-scope` says to test definitions against source data before any landing, while `data.md:9` allows records only from landed copies; taxi-B queried unlanded inbox files.
- **Landing grammar, EDA flood, helper quirks (C-40, C-70, C-71).** `landing.md` mixes the `land()` signature with credential rules and the source-reference grammar, and never covers a fetched archive. The EDA scan reported 142 anomalies on co2-B's panel. A rescan prints `issues: []` while baseline issues stay unrecorded, and `profile` shows DECIMAL columns as float64.

### 7. Analysis validation (4/6, major)

- **Coverage wording (C-10; co2-B).** The coverage rule sets no wording, so unreported early years became "count as zero"; the agent also called a scenario a "ceiling", which one skeptic judged the agent's own choice. The third co2 run in a row. Suggested severity: moderate.
- **Joins (C-36).** No not-applicable form for joins, so 24 of 25 Claude-agent results carry a repeated "not assessed: joins" caveat. The Codex agents bypassed it with trivial specs.
- **Rerun demotion (C-61), reconcile wording (C-65), cut-line ties (C-58).** Recording a check by rerunning demotes a supported finding (taxi-B). `reconcile()` wording reads as summing overlapping counts (taxi-B). Nothing checks the margin at a top-N cut: taxi-A's January #10 and #11 differ by $0.0003 an hour.

### 8. MCP tool surface (6/6, minor)

- **Output size (C-18).** The MCP server cuts results at 16,000 characters; status and state regularly exceed it, the overflow file ends with "exit status 0", and `collect_status.py` repeats every finding under caveats.
- **CLI over MCP (C-35).** The tools take one command per call, so Claude agents batch through Bash (retail-B about 39 CLI against 40 MCP calls). The reviewer brief itself names the CLI form. On a default Claude Code host each such call needs approval; on Copilot the cost is inferred, not tested.
- **Profile settings (C-66).** `profile` cannot load an investigation's views or settings.

### 9. Records, templates and instruction gaps (6/6, minor)

C-21 (seven small conflicts and gaps agents resolved alone), C-26 (no place for a full first brief before the investigation exists), C-37 (one question per call), C-41 (a source registered at setup cannot meet the basis rule), C-63 (no step retires finished next steps after release).

### 10. awb-status (3/6, minor)

C-30 (counts per calculation that users cannot map; supporting checks stay provisional; the per-question screen was skipped in all six runs) and C-67 (a hand-written history entry a second after the state reads as "out of date").

### 11. README (6/6, minor)

C-14. Still 4,718 words with admin material in the same file; no definition of an investigation; items 6 and 7 explain mechanisms rather than effects; nothing says how small an issue triggers the review stop or that a new rule forces another review.

### Contested (17, not ranked)

The skeptics split on these, usually because one judged the agent at fault and the other judged that the release allowed or invited it. Each is in [findings.md](findings.md#contested-findings) with what each skeptic said: C-02 thresholds after results, C-25 scoping pace, C-27 check-draft lifecycle signals, C-32 chat figure slips, C-38 commit-rerun cycles, C-42 release report details, C-52 builder kit not a deck, C-53 relative links, C-57 holiday checks, C-59 export deleting charts, C-60 child questions left open, C-64 status reference check, C-68 methods-note length line, C-73 hard-coded row counts, C-74 a question without a fallback, C-75 a third party's email in a retained page, C-76 "changed on disk" re-shows.

### Rejected (4)

- C-15: agents' own command and coding slips, none caused by the release.
- C-19: the hidden `.preview` folder; the headlines are shown in chat by design.
- C-44: Codex narration then summary; a relay effect.
- C-54: TLC's 403 for curl, handled as designed; one agent spoofed a browser user agent.

## What worked

- **The review loop ends.** At most two reviews per request in every run, a passed scoped review completes a request, and three of six releases reused a current receipt with no review.
- **Correct answers.** 30 of 30, reproduced under the agreed definitions.
- **The user decides rules.** Every review rule followed an explicit yes; co2-A's user declined and none was added.
- **Setup.** Every run recorded `.venv/bin/python` on the first setup call.
- **Fixes that held in use:** CO₂ chart headers passed; the integer-year scan ran; both retail scans found the cross-sheet overlap; the methods note stayed within the recorded length; START-HERE lists each file once; no run edited gate code.
- **Cost.** Claude-agent cost fell 63%, and the longest Claude-agent waits fell by more than two thirds.

## Differences between the two variants

Three runs per cell, and the user model changes with the agent model, so treat these as leads.

- **Codex as agent (A runs):**
  - first full reviews raised 3, 1 and 3 problems; every second review was clean, and no stop rule fired;
  - 5 of 10 reviewers were full-history forks, against the fresh-subagent rule (U-04);
  - linked and quoted SKILL.md files in all three runs (C-34);
  - first answers came as full tables, but all three users had asked for the analysis as its own step;
  - most of each drafting turn came before the first review (62-71%), with truncated instruction reads;
  - wall-clock 55.1 minutes on average, about flat; satisfaction 8, 8, 8.
- **Claude as agent (B runs):**
  - first full reviews raised 21, 9 and 15 problems; the stop rule fired once in each run;
  - first reports gave highlights, not full tables (C-33); untested explanations in taxi-B and retail-B (C-05);
  - still batched helpers through the CLI, retail-B heavily (C-35);
  - wall-clock 37.3 minutes on average, down from 104.7; cost $11.67 to $14.15 per run; satisfaction 7, 8, 8.
- **Codex as user (B runs):** strict; caught meaning errors no review flagged (taxi-B's three wording errors, co2-B's "energy mix"); called the escalations approval gates.
- **Claude as user (A runs):** two of three asked for numbers in chat up front, spent a round on display precision (co2-A), asked for 12-hour times alongside other edits (taxi-A), and never opened the SKILL.md links, which the harness forbade.

## Isolation and identity audit

**Isolation stayed clean in all six runs.** No agent, including the ten Codex reviewer subagents audited from their session rollouts under `SIMS/<run>/agent-home/.codex/sessions/`, read the spec, the design docs, `CONTEXT.md`, the repository, or the human or relay folders. No user read `AGENTS.md`, a `SKILL.md`, `src/` or any `.py` file. The edge cases were the same kind as Oct 16's:

- taxi-B and retail-B listed the simulation folder, which showed the names `human/`, `relay/` and `transcript.md`; nothing was opened.
- co2-B's and retail-B's listings of `feedback/` showed the `harness-log.md` file name; it was never opened.
- A retail-B review subagent read its own Claude Code spill file under the real home folder.
- co2-B wrote a fetched OWID script to system `/tmp`, then moved it into the project.
- In all three Codex-agent runs, reviewer subagents appear in the relay log only as collab "wait" events; their rollouts show only clean reads.
- The ancestor walks for `AGENTS.md` and `CLAUDE.md` were existence checks with empty results.

**Identity.**
- All 27 commits (taxi-B 14, retail-B 10, retail-A 3; the other three runs made none) have the simulated author and committer identity. The operator's full name and email appear in no commit and in no relay log. The 24 Claude-agent commits also carry a vendor co-author trailer. The pinned identity is a harness fix, not a product result, and no agent tried to override it (W-36).
- In all six runs the storage paths the persona supplied sit under a scratchpad path that encodes the host account name, and agents wrote them into project `README.md` and `foundation/sources.md` (harness finding C-17). The released packages and storage copies are clean.
- retail-A's provenance text names the public dataset's creator, and both retail runs committed a retained UCI page whose embedded data includes an editor's public email (C-75, contested). No other real person's name or email appears in project files.

## Harness findings (excluded from scoring)

These came from the simulation, not the release, and none counts toward any score or issue.

- **Personas front-loaded facts** they should give only when asked (C-16; 6/6). Scoping shrank to one or two rounds.
- **The scratchpad path** encoding the host account name was written into project records (C-17; 6/6). The evidence must be sanitized before it is committed.
- **Measurement gaps** (C-28): `codex exec --json` logs reviewer subagents only as "wait" items, so `reviewloop.py` reports reviewers=0 for every Codex turn; it also counts a false review start in two feedback turns; harness-log mislabels expected check-draft exits as failures. Two counting bugs in `reviewloop.py` were fixed while the runs were going: it missed review calls made through the MCP `package` tool (fixed before any analyst ran), and it counted `help` lookups as review starts (fixed after the co2-B, retail-B, co2-A and taxi-B analysts ran, but none of those runs made such a lookup; only retail-A did). The report check used the fixed script.
- **The Codex user's preamble line** was relayed as the user's words in all three B runs, and the Claude user's pre-tool narration ("Let me open the files.") twice in retail-A (C-29).
- **The Codex sandbox** blocked heredoc temp files and tool caches (C-45).
- **Pre-approved tools** hid permission-prompt cost; no prompt was logged in any run (C-46).
- **Simulation boundaries:** the agent prompt's URL rule delayed taxi-B's dictionary read, and the read boundary limited `awb-init`'s parent-folder check (C-47).
- **Isolation edge cases** listed above (C-55).
- **The agent prompt tells Claude agents the user sees only the final reply**, while the relay forwards every interim message (C-77). This confounds the narration part of C-13.
- **The public dataset's identity** appeared as the source in retail-A's deck, because the simulation presents a public download as company data (C-78).
- **A persona miscounted headline words** in its private notes (C-79).

## Limits

- **Not real users.** Both roles were models. Personas front-loaded definitions and package answers, which shortened scoping.
- **Pre-approved tools.** The harness auto-approved Bash and the awb MCP tools for Claude agents, and Codex ran with approvals off, so approval cost was not measured.
- **Copilot was not tested.** Every statement about GitHub Copilot is inferred from the release design and Copilot's primary documentation.
- **One run per cell.** No figure here is a measured rate. Several "fixed" labels rest on triggers that did not recur, and those are marked "not exercised".
- **Model judges.** Referees, analysts, graders and skeptics are models. 78 of 84 claims were weakened; this report uses the corrected wording, and where the two skeptics disagreed it follows the narrower one.
- **Review timing.** Codex reviewer subagents are invisible in the relay log; their rounds were timed from receipts and rollouts. The problem classes (substantive, cosmetic, false positive) are analyst judgments.
- **Comparisons with Oct 16.** Oct 16 had no per-line timestamps, so review share has no Oct 16 baseline; its 79-94% is the share of whole packaging turns.
