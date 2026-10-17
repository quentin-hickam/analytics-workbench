# Referee report: retail-A (variant A)

## Run

- **Simulation:** retail-A, dataset "Online Retail II" (UCI, standing in for the persona's own export).
- **Variant A:** Claude (Opus, headless `claude -p`) played the user, Priya Natarajan, head of e-commerce. Codex (`codex exec`) played the agent.
- **Relay:** started by this referee at 2026-10-16T19:16:55Z. `relay.py status` returned DEAD with an empty state, which meant it had never been started.
- **Conversation:** 19:16:55Z to 20:06:19Z, 49.4 minutes.
- **Feedback collection:** finished at 20:10:29Z, 53.6 minutes in total.
- **Outcome:** DONE, well inside the caps (45 user messages, 8 hours).

### Counts

From `relay/state.json` and `transcript.md`:

- **User messages:** 8 in total. Seven were delivered and answered (U1–U7). U8 was the DONE message, which by design is never relayed.
- **Agent replies:** 7 (A1–A7). `state.json` reports 8 agent turns and 9 user turns because each role had one extra turn for feedback.
- **Agent time:** about 47.2 minutes across the seven reply turns: 2.9, 11.8, 9.5, 1.9, 13.3, 5.2 and 2.6 minutes.
- **User time:** about 2.2 minutes across all turns. The user model cost $0.84.
- **Satisfaction:** 8/10 (`feedback/human.md`). The user would use it again.

## End-point checklist (`human/BRIEF.md`, "The path to the end point")

| Criterion | Met | Evidence |
|---|---|---|
| All five questions answered and accepted | Yes | U4: "I accept all five answers." Ledger `project/investigations/marketing-investment/questions.md`: Q-001 to Q-005 are answered, each backed by evidence files, along with child questions Q-006 to Q-015. |
| `awb-status` (where are we) asked at least once | Yes | U4: "use awb-status — where are we?" A4 gave the read-only status report. |
| Package draft exists and the user reviewed it | Yes | A5 pointed to `draft/findings.md`, `methodology-note.md` and `START-HERE.md`. The user's log `relay/human-006.jsonl` shows all three were read. U6 asked for six corrections. A6 showed the changed passages, and U7 confirmed them. |
| Released as 001 | Yes | `project/deliveries/marketing-investment/leadership-budget/released/001/`. `release-record-001.json` shows `released: true`, `release_number: 001`, empty `verify`, and `datasets: none`. |
| Copied to `SIMDIR/storage/releases/` | Yes | `storage/releases/marketing-investment/leadership-budget/001/` contains 12 files: findings, methodology-note, methodology, START-HERE, deck-rules, assembly/m365, manifest, and chart-1 to chart-5. `diff -r` against the local release folder is identical. |

Supporting records:

- **Landed originals:** the ZIP and the workbook are in `storage/landed/data/raw/uci-online-retail-ii/2026-10-16-original/`, with sha256 values in `provenance.json`.
- **Project state:** `state.md` lists 12 supported descriptive findings, and its next step is to use release 001.
- **Git:** the project has no commits; the user never asked for any.

## The five questions

Spot-check method: I converted the landed workbook (`storage/landed/.../extracted/online_retail_II.xlsx`) to my own parquet at `referee/lines.parquet`, using `referee/load.py`. I then ran DuckDB queries in `referee/spot.py` and `referee/spot2.py`, with outputs in `referee/spot.out` and `referee/spot2.out`.

- **Overlap:** the two sheets overlap exactly for 1–9 December 2010, 22,523 lines in each, so I used the same split as the agent. Sheet 1 covers dates before 2010-12-01 and sheet 2 covers dates from then on.
- **Line values:** Quantity × Price, with C-invoice lines signed negative.
- **Non-products:** I used the same code list as the agent's classification view, matched case-insensitively.

| Q | Agent's final answer | Recorded result | Referee spot-check |
|---|---|---|---|
| 1. Monthly net revenue, seasonality | 24-month table. Dec 2009–Nov 2010 £9,161,249.04, Dec 2010–Nov 2011 £9,314,079.92 (+1.7%). November peaks at £1,422,654.64 and £1,461,756.25, which is 2.67× and 2.96× the quietest month (Feb 2010, Apr 2011). Sep–Nov is 36.3% and 38.1% of each year. Full-period total £18,475,328.97. | Yes: `monthly`, `seasonality-comparison`, `revenue-summary` | **Match.** All 24 months agree to the penny, as do both annual totals, the Sep–Nov shares and the full-period total (£18,475,328.97). |
| 2. Top-10% share; no-ID revenue | 592 of 5,914 identified IDs (top tenth rounded up). £10,176,511.65 is 63.60% of identified and 55.08% of total net revenue. Guest/no-ID £2,474,184.31 (13.39%). | Yes: `concentration` | **Exact match** on every figure. |
| 3. 90-day repeat rate by 2010 first-purchase month | 43.0% overall (1,448 of 3,364). Monthly cohorts Jan–Nov range from 34.7% to 53.5%. December is 15.8% (12 of 76). All cohorts have a full 90-day window. | Yes: `cohorts` (Q-003, Q-013) | **Exact match** on all 12 cohort sizes and repeat counts. Definition used: first positive merchandise invoice ever observed, and a later distinct invoice within 90 days. |
| 4. Highest cancellation rate by value (≥ £10k sales) | The storage jar (95.1%) comes entirely from one order that was fully reversed: invoice 541431 / C541433, £77,183.60. With both sides removed it falls below the threshold. Revised ranking: White Cherry Lights 35.6% (£6,421.10 / £18,048.72), Pink Cherry Lights 29.2%, Fairy Cake Flannel 26.1%, Two Door Curio Cabinet 22.8%, Vintage Red Kitchen Cabinet 18.1%. | Yes: `products`, `jar-order-check`, `products-without-reversal` | **Match, with one undocumented difference.** The jar figures match (£81,448.21 sales, £77,479.64 cancellations before removal). The top six, rank 8 and rank 10 match exactly. The agent's published data upper-cases stock codes, which merges 47566b (£1,761.26 of sales) into 47566B. That moves Tea Time Party Bunting from 17.4% (rank 7 on raw codes) to 16.3% (rank 9). The merge is defensible, but no catalog, publication or methodology file mentions it. |
| 5. Non-UK countries with the largest net-revenue growth | Australia +£107,642.62 (+365.7%). France +£65,848.44 (+52.9%). Norway +£32,085.31, which is 10,971% on a £292 net base, footnoted. Japan +£31,136.07. Germany +£23,073.89. Australia's largest account is 90.3% of its later revenue and 96.8% of its growth. | Yes: `countries`, `australia-growth` (Q-005, Q-010, Q-015) | **Exact match** on the top ten (UK and Unspecified excluded). I did not independently recompute the Australia single-account decomposition. |

All five answers come from recorded, validated results, and my independent queries reproduce them. The only gap is the undocumented stock-code case merge in Q4, which changes one product's rank but not the headline.

## Timeline

| Phase | Messages | Time (UTC) | What happened |
|---|---|---|---|
| Init | U1 → A1 | 19:17–19:20 | The user's first message was very complete: question, audience, five questions, data URL, storage paths and preview-and-wait. The agent ran awb-init (scaffold, Git init, a project venv plus DuckDB after setup first targeted the base interpreter, source documentation retained). It parked the intake in the README because an investigation cannot be created before the scope interview. It asked four scope questions, each with a recommendation. |
| Scoping | U2 | 19:20 | The user answered all four. They also raised, unprompted: non-product codes (asking for a recommendation), December 2011 being incomplete, guest lines, and the leadership hypothesis that retention pays better. |
| Landing | A2 | 19:20–19:32 | The ZIP and workbook were landed to `storage/landed/` with provenance and hashes. The data was published to canonical parquet, with 25 checks passing. |
| Cleaning | A2 (inline) | | Found the exact 1–9 Dec 2010 overlap between sheets (22,523 lines) and handled it with a per-investigation sheet split rather than an awb-clean pass. Classified non-product codes. No separate cleaning step was run. |
| Exploring | A2 (inline) | | Exploration SQL (scope counts, overlap, non-product codes, large jar lines). No separate explore step. One `awb/read` SQL failure on unbound parameters. |
| Answering | A2, U3 → A3, U4 | 19:32–19:42 | A2 reported "5 answered" with only headline-level numbers and a headline preview. In U3 the user asked for the numbers behind every headline. A3 supplied full tables, checked the jar reversal and added child questions Q-011 to Q-014. In U4 the user accepted all five answers and sent headline edits. |
| Status | U4 → A4 | 19:44 | A read-only awb-status report. It correctly flagged two wording risks (the Jan–Nov range versus December; 90% of revenue versus 90% of growth). The user's headline edits were not recorded in this turn because status is read-only. |
| Packaging | U5 → A5 | 19:44–19:57 | The full draft: 8 main slides plus a caveats appendix, a methodology note, five chart CSVs and START-HERE. Q-015 confirmed the Australian account supplies 96.8% of growth. Two independent reviewer subagents ran. There were two `awb/package` failures (export before chart specs; storyline and number checks) and three Codex backend reconnects (403). This was the slowest turn, at 13.3 minutes. |
| Review | U6 → A6 | 19:58–20:03 | The user made six corrections: company identity, chart source line, singular "key account", plainer control-group wording, declarative "How we know" bullets, and the repeat-buyer definition. The agent recorded them as review rules, ran a fresh full review and wrote a before/after change preview. It then waited for confirmation. |
| Release | U7 → A7, U8 | 20:03–20:06 | Release 001 was frozen, a fresh review ran, and the local and stored copies were verified. The agent reported the exact path and the caveats. U8 was DONE. |

## Pain points observed by the referee

| # | Pain point | Messages | Severity |
|---|---|---|---|
| 1 | "5 answered" was reported, and headline approval requested, before the user had seen the numbers behind four of the five answers. Q2 was given only on the identified-revenue denominator, and guest revenue only as a percentage. This cost one full exchange (U3/A3). | A2, U3 | major |
| 2 | Packaging and release overhead: a large contract plus templates, four full independent reviews across A5–A7 (including a re-review at release with no content change), and the slowest turns of the run (A5 13.3 min, A2 11.8 min). | A5–A7, `feedback/agent.md` §1.1 | major |
| 3 | The draft number checker rejected dates, a citation year and compact pairs such as "368/53.5%". The agent rewrote sound prose to get past it. | A5, `feedback/agent-notes.md` | major |
| 4 | The `awb/read` SQL error for unbound prepared-statement parameters advised running "without --read-only". That steers agents toward write mode for what is a binding problem. The agent did not follow it. | A2 | major |
| 5 | Because awb-status is read-only, the edits the user sent in the same message waited for a separate "Use awb-package" request. | U4, A4, U5 | minor |
| 6 | The agent linked and quoted internal SKILL.md files to the user three times. The user declined to open them and logged it as friction. | A1, A4, A6 | minor |
| 7 | The first full draft needed six audience corrections. Two (company identity, source label) trace to the public dataset standing in for the company's data. The others (technical control-group wording, imperative "How we know" bullets even after the slide-8 headline was corrected in A3, a missing metric definition) are draft-quality issues. | U6 | minor |
| 8 | The clean and explore steps from the README were folded into answering. The user was unsure whether something had been skipped. The agent avoided awb-clean because it would have required a user choice even for a proven exact overlap. | A2, U3 notes | minor |
| 9 | Undocumented stock-code case merge in the published data (47566b → 47566B). It shifts one product's cancellation rank (spot-check). | Q4 spot-check | minor |
| 10 | Jargon and duplication in replies. Examples: "signed financial lines", "one-penny tolerance", "No packaging Git commit exists; producing-file checksums are recorded". Scope questions were listed twice, and "confirm" was asked twice. | A1, A2, A6, A7 | minor |
| 11 | Agent execution slips, corrected within the turn: pip installed into the user site after the venv symlink was resolved to the base interpreter; an export ran before chart specs existed; a JavaScript quoting error. A reviewer subagent also passed an unsupported CLI `--project` flag. | A1, A3, A5 | minor |
| 12 | Harness: three Codex backend 403 reconnects in A5 (recovered). Sandbox heredoc and xcrun cache-file failures (worked around). | A1, A5 | minor |

There were no loops, no stalls, no wrong numbers, and no protocol or isolation breaches.

## Isolation audit

- **Agent logs** (`relay/agent-001..008.jsonl`, viewed with `logview.py --full` and rendered to `referee/logs/`):
  - **No forbidden reads:** nothing from `workbench-spec`, `workbench-design`, `CONTEXT.md`, any `docs/` folder, the analytics-workbench repository, `SIMDIR/human`, `SIMDIR/relay` or `transcript.md`.
  - **No real-home paths:** no `/Users/` paths at all; the fake HOME held.
  - **What it did read:** the release's skills under `agent-home/.agents/skills/` and the project files.
  - **Outside SIMDIR:** only `<python-prefix>/bin/python3` (the interpreter setup first picked) and a macOS `/var/folders` xcrun cache warning. Neither matters.
  - **Audit limit:** the reviewer subagents spawned in A5–A7 do not have their tool calls in the parent Codex log. Their saved reports in `project/investigations/marketing-investment/package-reviews/` and the agent's notes point only to project files and the awb read tool, but their reads cannot be fully audited.
- **User logs** (`relay/human-001..009.jsonl`):
  - **What it read:** `human/BRIEF.md` and `human/README.md`; Globs of `inbox/` and `storage/releases/`; and only the draft files the agent pointed to (`headline-preview.md` in A2; `findings.md`, `methodology-note.md` and `START-HERE.md` in A5).
  - **No forbidden reads:** no `AGENTS.md`, SKILL.md, `src/`, `.py`, `workbench-guides/` or agent homes.
  - **Clean.**
- **Known study limit (persona front-loading):** the user put essentially all of its context into U1 and U2, including facts the brief says to give only if asked. That thinned the scoping interview to a single round. This is the known limit, kept for comparability with Oct 15.

## User satisfaction

**8/10.** The user deducted points for communication, not correctness. They praised the overlap and jar-reversal catches, the pushback on their own wording, and the change preview and release.

## Most important issues for the maintainers, ranked

1. **Answered should mean answered to the user.** The headline preview and the status line ("5 answered") should come with a compact table of results per question, using the denominators the user asked for, so that headlines are never approved blind. This cost a turn here, and a less careful user would have approved without the numbers. (Product, major.)
2. **Packaging cost.** Consolidate the package and review instructions into one checklist, and reuse a clean review receipt when the candidate and the rules are byte-identical (A7 re-reviewed unchanged content). Packaging took about 21 of the 47 agent minutes. (Product, major.)
3. **Number checker false positives.** Distinguish dates, citation years, count/rate pairs and source counts recorded in checks from analytic quantities. Report the location and the expected evidence. (Product, major.)
4. **The read-only SQL error gives unsafe advice.** Diagnose unbound parameters before the plan-safety check, offer settings binding, and never suggest dropping `--read-only` for a binding error. (Product, major.)
5. **Mixed-intent status requests.** Either let status hand approved edits to the next step durably, or have it state plainly that edits sent with a status request will not be applied. The README should say so too. (Product, minor.)
6. **Clean/explore positioning and exact-duplicate handling.** The README lists clean and explore as steps, but this run skipped them for good reason. Say when they fold into analysis, and give proven exact cross-file overlaps an audited default instead of a forced user choice. (Product, minor.)
7. **Surface data normalisations.** Record any case or whitespace normalisation of keys in the publication record and the catalog (here, stock-code upper-casing). (Unclear, minor.)
8. **Let agents talk about instruction files without exposing them.** Agents should say "I'll wait for your OK" rather than linking SKILL.md paths. If a skill asks the agent to cite its rule when pausing, that request should be dropped. (Unclear, minor.)
9. **Scope the audience-facing identity.** Add a question about how to describe the company and the data source to the audience, and prompt for declarative methods bullets in the template. (Product/unclear, minor.)
10. **Smaller fixes.**
    - The init/scope ordering forces the intake into the README.
    - The 8-slide request became 8 main slides plus an appendix.
    - The README is dense: the checkpoint paragraph, the install material, and the release path nesting.
    - START-HERE lists methodology.md as both a file to attach and an internal file.
    - The CLI and MCP take different `--project` arguments.
    - Helper output is verbose.
    - Lifecycle text was stale (README said no release was authorized after the release).
