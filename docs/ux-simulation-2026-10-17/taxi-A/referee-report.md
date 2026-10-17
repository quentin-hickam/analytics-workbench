# Referee report: taxi-A (variant A)

Variant A: Claude (Opus, headless) played the user, Dana Ortiz, a mobility policy analyst. Codex (`codex exec`) played the agent with the awb skills and MCP server. Dataset: NYC yellow-taxi trips for January and July 2024, plus the zone lookup.

Paths below use `SIMS` for the simulations root, so the run folder is `SIMS/taxi-A`.

## Run summary

| Item | Value |
|---|---|
| Relay started | 2026-10-17T11:17:42Z |
| Conversation ended | 2026-10-17T12:20:17Z (DONE) |
| Relay finished (feedback collected) | 2026-10-17T12:23:45Z |
| Wall-clock | 62.6 min conversation, 66.0 min total |
| User messages | 10. Nine were answered; the final DONE message is not relayed, by design. |
| Agent replies | 9 in the conversation, plus 1 feedback turn (10 agent turns) |
| User-role cost | $0.94 |
| Agent reply time | 59.9 min summed (2.7, 2.2, 7.5, 11.0, 9.2, 8.5, 14.7, 3.3, 0.8) |
| Outcome | End point reached; release 001 copied to storage |
| User satisfaction | **8/10** |

Sources: `SIMS/taxi-A/relay/state.json`, `SIMS/taxi-A/transcript.md` and `SIMS/taxi-A/feedback/harness-log.md`.

## End-point checklist (from `SIMS/taxi-A/human/BRIEF.md`)

| Criterion | Met | Evidence |
|---|---|---|
| All five questions answered and accepted | Yes | Q2 and Q4 were accepted at msg 5. Q1, Q2, Q4 and Q5 were accepted at msg 6. Q3 was accepted after the verification in reply 6 (msg 7 moves on to the headlines). Every root question is `answered` in `project/investigations/trip-pattern-comparison/questions.md`, with recorded results. |
| Asked where things stand (`awb-status`) | Yes | msg 8 asks "use awb-status — where are we?", and reply 8 answers it. |
| Package draft exists and was reviewed | Yes | Headline preview at reply 6, with four corrections from the user at msg 7. Full draft at reply 7, which the user read (findings.md, methodology-note.md, START-HERE.md). Three more corrections at msg 8, changed slides shown at reply 8, approval at msg 9. |
| Released as 001 and copied to the releases folder | Yes | Reply 9. `project/deliveries/trip-pattern-comparison/board-brief/released/001/` and `SIMS/taxi-A/storage/releases/trip-pattern-comparison/board-brief/001/` are byte-identical (checked with `diff -r`; 12 files). |

Other checks: the landed originals are in `SIMS/taxi-A/storage/landed/data/raw/...`, each with a provenance.json. The released findings.md contains no 24-hour times, so the 12-hour rule from msg 8 holds. The methodology note is 521 words.

## Answers and spot-checks

I ran an independent read-only DuckDB recomputation on the landed parquet and CSV files: `SIMS/taxi-A/referee/spotcheck.py`, `spotcheck2.py` and `spotcheck3.py`, run with `uv run --with duckdb python -I`. Screens applied as approved: fare > 0, distance > 0, duration > 0 and ≤ 4 h, speed ≤ 80 mph, pickup in the file's month.

| Q | Agent's final answer | Recorded result | Referee spot-check |
|---|---|---|---|
| 1 | Eligible trips rose from 2,866,703 (Jan) to 2,970,872 (Jul), +3.6%. Both months peak at 6 p.m. July Thursdays average 99,947 including July 4 and 113,478 excluding it, against January's 103,961. | q1-volume, q1-thursday (supported) | **Matched**: 2,866,703 and 2,970,872 eligible trips; July 4 = 59,353 trips. |
| 2 | Airport share rose from 9.84% to 11.32% (282,212 → 336,439 trips). Median airport fare was $54.80 → $57.60, against $12.10 → $12.80 for other trips. Median airport duration was 32.0 → 35.5 min, against 10.8 → 11.7 min. | q2-airports, board-airports (supported) | **Matched**: 282,212 and 336,439 trips; 9.84% and 11.32%; medians $54.80 and $57.60; durations 32.0 and 35.5 min. |
| 3 | Median standard-rate card tip was 26.61% (Jan) and 26.25% (Jul). Hourly medians ran 25.63–28.21% in January and 25.37–27.65% in July. Cash tips are unrecorded. In the Bronx, 95.1% and 91.8% of card trips have unknown rate code 99 with a zero tip. | q3-standard, q3-verification (supported); q3-tips kept as a provisional reference | **Matched**: 2,174,074 and 2,074,295 standard-rate card trips, medians 26.61% and 26.25%. Bronx and Brooklyn code-99 shares and standard-rate medians (15.06/21.84, 23.36/23.07) match. Small inconsistency: the chat in reply 5 said Bronx July code 99 was 91.85%, but the exact value is 91.844997%, which rounds to 91.84%. The release shows 91.8%. |
| 4 | Excluded 97,921 (3.30%) in January and 106,031 (3.45%) in July. Vendor 1 went from 4.77% to 2.41%, vendor 2 from 2.82% to 3.76%. Vendor 6 excluded 35.38% (January only, 260 records). | q4-quality (supported) | **Matched exactly**, including each vendor's raw and excluded counts. |
| 5 | With a 300-trip floor, January's #1 is Flushing Meadows-Corona Park at $180.93/occupied hour (454 trips). July's #1 is Outside of NYC at $253.15 (681), then Flushing Meadows-Corona Park at $162.26. Every named zone in both top-10s is in Queens. | q5-supported, board-rankings (supported); q5-zones kept as a provisional reference | **Matched**: both top-10 lists, their rates and trip counts, and the all-Queens claim. Caveat: January's #10, Briarwood/Jamaica Hills ($93.4973/h, 371 trips), beats LaGuardia Airport ($93.4970/h, 87,625 trips) by less than a tenth of a cent. The slide does not flag this tie. |

Every final number I checked reproduces from the source files.

## Package review loop (from `SIMS/kit/reviewloop.py`)

| Request | Turn | Review rounds | Outcome | User waited |
|---|---|---|---|---|
| Q3 verification and headline preview (msg 6) | agent-006 | 0 (by design, a preview is not reviewed) | preview shown | 8.5 min |
| Full draft after headline edits (msg 7) | agent-007 | **2**: a full review at 12.1 min found 3 narrative problems; a scoped re-review at 14.3 min was clean | passed | **14.7 min**. Review tail (first review start to turn end) was 4.3 min. |
| awb-status plus 3 corrections, changed slides shown (msg 8) | agent-008 | **1** scoped review, clean at 2.6 min | passed | 3.3 min (tail 1.7 min) |
| Release (msg 9) | agent-009 | **0**: reused the current receipt, 1 read-only check-draft | released 001 | 0.8 min |

Packaging turns 006–009 took 27.3 min, 46% of agent reply time. The tool reports 30 min (48%) because it also counts the post-session feedback turn. Time from first review start to turn end totals about 6 min (10%).

**Verdict: no perfectionism loop in this run.** No request went past two review rounds, every second round was scoped and clean, and the release reused a current receipt without another review. Two costs remain, and the most critical is the first:
- One of the three first-round findings was audience-irrelevant: "put the no-mix-up verification on the visible tipping slide". The user rejected it at msg 8. Undoing it took a correction, a recorded user-override exception and another scoped review.
- Most of the 14.7-min draft turn came *before* the review, not inside it: two new projection results built just to select chart rows, numbers-check rewrites, and an export that deleted all charts and had to be redone (agent notes, reply 7).

## Timeline

| Phase | Messages | Time (UTC) | Notes |
|---|---|---|---|
| Init | msg 1 → reply 1 | 11:18–11:20:42 | awb-init. Landed the 3 files to storage with hash checks. Fetched the TLC dictionary over the web, after curl got a 403. Asked 2 scoping questions. |
| Scoping | msg 2 → reply 2 | –11:23:03 | awb-scope. Created investigation `trip-pattern-comparison` with 5 root questions and 5 child questions. |
| Landing, publishing, cleaning proposal | msg 3 → reply 3 | 11:23:12–11:30:42 | Published 6,041,527 trips and 265 zones. Proposed screens with counts (3.30% / 3.45%) and held them for signoff. |
| Cleaning applied and answering | msg 4 → reply 4 | 11:31:00–11:41:59 | Applied the approved screens and answered all five questions (35 validation checks). Sensitivity check on the 127 review-flagged records. |
| Exploring | (none as a separate phase) | — | awb-explore was never invoked. Profiling happened inside awb-clean (reply 3) and as diagnostics (reply 4). |
| Refinements | msg 5 → reply 5 | 11:42:16–11:51:29 | Q5 300-trip floor, Q3 code 99 = unknown, Q1 July 4 sensitivity, Newark pickup caveat. |
| Q3 verification and headline preview | msg 6 → reply 6 | 11:51:44–12:00:13 | awb-package preview: 8 headlines. |
| Full draft and review | msg 7 → reply 7 | 12:00:35–12:15:17 | 2 review rounds. Export failure and recovery. |
| Status and corrections | msg 8 → reply 8 | 12:15:44–12:19:04 | awb-status. 12-hour times saved as a standing rule. Changed slides shown. |
| Release | msg 9 → reply 9 | 12:19:15–12:20:00 | Release 001, storage copy verified. msg 10 DONE at 12:20:17. |

## Pain points observed by the referee

| # | Observation | Messages | Severity |
|---|---|---|---|
| 1 | The first-pass Q5 ranking had no support floor and was led by zones with 1–13 trips (Rikers Island on 1 trip). The agent's own scoping records said to propose small-group thresholds before viewing leaders, yet it proposed none during the threshold signoff at reply 3. The user had to ask. | reply 3, reply 4, msg 5 | major |
| 2 | The first-pass Q3 led with 0% medians for the Bronx and Brooklyn and cited "rate-code 99" without defining it. Not board-safe until the user pushed. | reply 4, msg 5 | major |
| 3 | The package reviewer, applying the contract that every represented question gets visible content, pushed an internal QA bullet onto an audience slide. The user had it removed. | reply 7, msg 8 | major |
| 4 | The first-pass Q1 reported a July Thursday decline without checking the July 4 holiday. The user raised it. | reply 4, msg 5 | minor |
| 5 | The agent linked and quoted its own SKILL.md files to the user to justify pausing. | reply 1, reply 8 | minor |
| 6 | awb-status came back as prose paragraphs, not the per-question screen with suggested next requests. It said "nine supported findings and two provisional reference calculations", which the user could not map to 5 questions. | reply 8 | minor |
| 7 | User-facing previews were saved in a hidden `.preview/` folder. | reply 6, reply 8 | minor |
| 8 | Deck times defaulted to 24-hour format for a lay board. | reply 7, msg 8 | minor |
| 9 | `package export` with `--no-datasets` and no `--chart` deleted all five chart exports (2 failed MCP calls), and a full re-export recovered them. | reply 7 (agent-007) | minor |
| 10 | The January rank-10 tie in Q5 was not flagged: the gap is less than $0.001/h, between a 371-trip zone and an 87,625-trip airport. | reply 5, chart-4.csv | minor |
| 11 | A typo in the release slipped past the format checks: "27.65% at 6–7 p.m.." has a double period. | release 001 findings.md, tipping slide | minor |
| 12 | Reply 5's interim messages contradicted each other: first "will wait for your signoff" on the 300-trip floor, then it applied the floor. | reply 5 | minor |
| 13 | MCP failures: `records` once (evidence-string grammar), `read` once (review-rules called before the narratives existed), `package` twice (item 9). All were recovered. | replies 3 and 7 | minor |

No stalls or loops. Every user message was answered in under 15 minutes.

## Isolation audit

- **Agent** (`SIMS/taxi-A/relay/agent-*.jsonl`, through `logview.py --full`): file reads were confined to the released skills under the agent's own home (allowed) and the project. MCP SQL reads named only project-relative files. Web access went only to TLC and NYC311 pages. There were **no hits** for workbench-spec, workbench-design, CONTEXT.md, a docs folder, the source repository, `SIMS/taxi-A/human`, `SIMS/taxi-A/relay`, the transcript, or `SIMS/kit`. One audit limit: the fresh reviewer subagents in agent-007 and agent-008 appear in the Codex event stream only as a single collab `wait` event, so their own tool calls cannot be audited. Their reports are recorded as review receipts in `project/deliveries/.../review/`.
- **User** (`SIMS/taxi-A/relay/human-*.jsonl`): it read BRIEF.md and README.md, `quality-proposal.md` (which the agent pointed to), the draft's findings.md, methodology-note.md and START-HERE.md, and a glob of `storage/releases`. It made no reads of AGENTS.md, SKILL.md, `src/`, `.py` files, `workbench-guides/` or agent homes, and hit no permission denials. The agent twice linked a SKILL.md path in chat; the user declined to open it and logged it as friction.
- **Verdict: clean.** No breach affected the outcome.

## Identity check

- `git log --all` in the project returns no commits. The repository was initialized, nothing was committed, so there are no author or committer identities. The agent's simulated home sets a placeholder git name with `analyst@example.com`.
- The project and storage contain no real home-directory paths and no email other than `analyst@example.com`. Two regex false positives sit inside a retained NYC311 HTML page: an OData attribute and an image filename.
- The OS account name, which spells the operator's personal name, is part of the harness scratch-directory path. The persona brief gave that path as the landed and release storage locations, and the agent wrote it, as an absolute path, into `project/README.md`, `project/foundation/sources.md` and the package review snapshot's `sources.md`. It does not appear in the release 001 files or in the landed provenance files. This leak comes from the harness, not the product.

## Most important issues for maintainers (ranked)

1. **Ranking questions need a support floor before leaders are shown.** awb-clean or the analysis guide should prompt for a minimum group size during the threshold signoff whenever a question asks for a top-N by rate. The README promises this; this run broke that promise (taxi-A-01).
2. **Codes in first-pass answers need defining, and a cleaner population should be offered when an unknown code dominates a subgroup.** Leading with "0%" medians that come from code-99 records was not board-usable (taxi-A-02).
3. **Separate audience questions from internal verification in the package contract.** The reviewer's rule that "every represented question is visible" created audience noise. The user had to reverse it, which cost an extra correction and review (taxi-A-03).
4. **Packaging assembly cost sits before the review, not in it.** The draft took 14.7 minutes: chart-row selection needed new recorded projections, numbers-check false positives needed rewrites, and the export footgun deleted all charts. The review loop itself is now bounded (2 rounds at most, 4.3 min). Fix the export semantics and the chart-selection grammar first (taxi-A-11, 12, 13, 14).
5. **awb-status output and the finding-role model.** Status should be the promised per-question screen. A reference-only role would stop valid reference calculations from showing up as "provisional" and confusing the user (taxi-A-05, 10).
6. **Small user-facing defaults:** 12-hour times for lay audiences, previews in a visible folder rather than `.preview/`, no skill-file links in chat, and plain language in review files (taxi-A-04, 06, 07, 08).
