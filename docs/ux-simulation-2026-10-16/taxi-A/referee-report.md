# Referee report: taxi-A (variant A)

Variant A: Claude (Opus, headless `claude -p`) played the user, Dana Ortiz, a mobility policy analyst. Codex (`codex exec`, model `gpt-6.1-sol`, reasoning effort high) played the agent, with the awb skills installed.

## Run summary

| Item | Value |
|---|---|
| Relay started | 2026-10-16T19:16:52Z (pid 2705) |
| Conversation ended | 2026-10-16T20:16:22Z (user STATUS: DONE) |
| Relay finished (after feedback turns) | 2026-10-16T20:19:14Z |
| Wall-clock | 59.5 min conversation, 62.4 min total |
| User messages | 9 written; 8 delivered (each answered by an agent reply). Message 9 was the DONE line and, by design, was not relayed |
| Agent replies | 8 conversational replies, plus 1 feedback turn (`agent_turns` = 9 in `relay/state.json`) |
| Caps | Not reached (limits were 45 user messages and 8 hours) |
| Agent time | 57.0 min across the 8 replies (3.2, 9.6, 14.4, 1.7, 5.7, 16.6, 3.7, 2.1) |
| User time / cost | About 2.5 min of model time, $0.98 |
| Outcome | DONE. End point met |
| User satisfaction | **9/10** |
| Relay health | Clean: `relay/relay.log` is empty, with no crash and no restart |

When this referee started, `relay.py status` printed `DEAD` with an empty state `{}`. The run had not been started yet; status prints DEAD whenever no relay pid exists. The phase was empty, so I started the relay as the playbook says.

## End-point checklist (from `human/BRIEF.md`)

| Criterion | Met | Evidence |
|---|---|---|
| All five questions have specific answers the user accepts | Yes | Transcript msg 4: "I accept the answers to all five questions." `project/investigations/taxi-trip-patterns/questions.md` shows Q-001 to Q-005 as `answered`, each linked to a recorded result (`evidence/*.json`). `state.md` lists them as supported findings |
| User asked where things stand at least once | Yes | Msg 4: "Use awb-status — where are we?" Agent reply 4 is the status report |
| A deck package draft exists and the user reviewed it | Yes | Headline preview (reply 5, `deliveries/.../draft/preview-plan.md` at the time). User headline edits (msg 6). Full draft (reply 6). User opened `findings.md`, `methodology-note.md` and `START-HERE.md` (`relay/human-007.jsonl`) and asked for six corrections (msg 7). Changed slides were shown in reply 7 |
| Released as 001 and copied to the releases folder | Yes | Reply 8. `storage/releases/taxi-trip-patterns/board-decisions/001/` holds 13 files. `diff -r` against `project/deliveries/taxi-trip-patterns/board-decisions/released/001/` is identical. The release manifest has `status: release`, `release_number: 001` and `released_at: 2026-10-16T16:15:28-04:00`. The draft differs from the release only in the manifest's release fields |

Supporting checks:
- Originals were preserved byte for byte. SHA-256 of the three inbox files equals that of the copies under `storage/landed/data/raw/...`.
- The project git history has 12 commits, made as the user asked ("commit as you go", msg 3). The tree is clean.

## The five questions

All figures below were re-derived by the referee from `inbox/` with DuckDB. Scripts: `referee/spotcheck.py` and `referee/spotcheck_hours.py`. Output: `referee/spotcheck-output.txt`. I re-implemented the agreed primary rules independently: a nonpositive, nonfinite or null fare or distance; a missing pickup or dropoff time; a pickup outside the file's month; a duration under 1 minute or over 240 minutes; or a speed over 80 mph.

| Q | Agent's final answer | Recorded result | Referee spot-check |
|---|---|---|---|
| 1. Volume by weekday and hour | Eligible trips rose 3.59% (2,858,984 to 2,961,664). Tuesday +16.04%, Saturday −10.32%. The busiest pickup hour stayed 6–7 p.m. Holiday caveat added: Jan 1 and MLK Day fell on Mondays, July 4 on a Thursday; their effect was not tested | Yes: `trip-volume` (supported) | **Exact match.** Eligible counts 2,858,984 and 2,961,664. Tue +16.04%, Sat −10.32%. Peak hour 18 in both months (205,648 and 206,564 trips, which is 6,634 and 6,663 per day as the slide notes say) |
| 2. Airport share, fares, durations | Known-airport share 9.82% to 11.28%. Median airport fare $54.80 to $57.60, versus $12.10 to $12.80 for non-airport trips. Median duration 32.1 to 35.7 min, versus 10.8 to 11.8 | Yes: `airport-comparison` (supported) | **Exact match.** Airport trips (either endpoint in zone 1, 132 or 138) were 280,692 and 334,110. Unknown-endpoint trips were 19,815 and 19,990. Both medians and durations are identical |
| 3. Card tip % of fare, by hour and borough | Median 26.25% to 25.65% ("about a quarter" in both months). Zero-tip share 4.66% to 6.58%. Lowest near 5 a.m. (about 24%), highest early evening (27–28%). Manhattan 26.61% and 26.25%, Queens 23.13% and 22.81%. Bronx and Brooklyn medians are 0 because Vendor 1 code-99 card records are almost all zero-tip (27,081/27,081 and 39,858/39,859). Cash tips are not recorded. The question goes to TLC (Q-011) | Yes: `tipping-patterns`, `tip-reporting-check`, `tip-code-sensitivity` (supported) | **Exact match.** n = 2,293,396 and 2,226,310. Medians 26.25% and 25.65%. Zero shares 4.66% and 6.58%. Borough medians match. Code-99 counts match. Hour 5 is lowest (23.65% and 23.63%) and hour 18 highest (27.98% and 27.34%). Brooklyn zero shares 69.13% and 75.66% match the appendix's "about 69% then 76%" |
| 4. Invalid records, by vendor | Jan: 105,640 of 2,964,624 excluded (3.56%). Jul: 115,239 of 3,076,903 (3.75%). Vendor 1: 4.85% to 2.48%. Vendor 2: 3.14% to 4.13%. Vendor 6 (Jan only): 93 of 260 (35.77%). Reasons overlap and were counted once per record. Sensitivity check run | Yes: `quality-counts`, `quality-overlaps`, `sensitivity` (supported) | **Exact match** in every month × vendor cell and both totals |
| 5. Top 10 pickup zones by fare per occupied hour | Floor of at least 1,000 eligible trips per zone per month, proposed by the user. Long Island City/Hunters Point first in both months ($106.28 and $98.99; shown as $106 and $99). JFK, LaGuardia and East Elmhurst in the top five in both months. Fare_amount only | Yes: `zone-ranking`, `sensitivity-zone-ranks` (supported; the earlier ranking with no floor is marked superseded) | **Exact match** for all 20 ranked rows. Jan: LIC, JFK, LGA, East Elmhurst, Sunnyside, Battery Park City, FiDi North, Seaport, FiDi South, Yorkville East. Jul: LIC, Baisley Park, JFK, East Elmhurst, LGA, Sunnyside, Jackson Heights, East Williamsburg, Battery Park City, Yorkville East |

No answer was wrong or unsupported. Every number in chat, on the released slides and in the methods note that I checked traces to a recorded result and reproduces from the source files.

## Timeline

| Phase | Messages | Time (UTC) | Notes |
|---|---|---|---|
| Init | U1 → A1 | 19:17–19:20 (3.2 min) | Project created. The agent replaced the interpreter awb/setup chose (`<python-prefix>/bin/python3`, no duckdb) with a project `.venv` and reran the installer through the CLI. It read the TLC dictionary text with web tools; the direct PDF download returned HTTP 403 |
| Landing | A1 | same turn | All three originals landed and retained under `storage/landed/`, with matching hashes |
| Scoping | A1 (4 questions) → U2 → A2 | 19:20–19:30 | Four questions, each with a recommendation and an alternative. The user accepted all four and added fare-only revenue and a zero-tip share |
| Cleaning | A2 | 19:20–19:30 (9.6 min, 48 MCP calls) | Exclusions by month and vendor, overlaps, a sensitivity check and full row reconciliation. The agent flagged single-trip zones in the rankings but did not propose a floor |
| Follow-ups | U3 | 19:30 | User asked which question was "1 answered", what Vendor 6 is, set the 1,000-trip floor, and asked for commits as it goes |
| Exploring / answering | A3 | 19:30–19:45 (14.4 min, 30 MCP calls, 2 guard refusals) | No separate awb-explore pass: the agent read the skill and went straight to the defined results. It found the code-99 zero-tip concentration and added diagnostics. Vendor 6 was identified from a 2025 dictionary and the question was passed to TLC |
| Acceptance + status | U4 → A4 | 19:45–19:47 (1.7 min) | All five accepted. Holiday caveat added. awb-status report given |
| Package preview | U5 → A5 | 19:47–19:53 (5.7 min) | 8 main and 4 appendix headlines, a methods-note plan, preview-and-wait honored. The user pre-answered the dataset and methods-note questions |
| Full draft | U6 → A6 | 19:53–20:10 (16.6 min, the longest turn; 5 MCP "failures") | Headline edits applied. Chart export, check-draft repairs, two fresh reviews, review rules saved |
| Review | U7 → A7 | 20:10–20:14 (3.7 min) | Six corrections, including adding Q3's hour and borough detail, which had been in speaker notes only. Changed slides shown inline |
| Release | U8 → A8 | 20:14–20:16 (2.1 min) | Fresh release review, release 001 frozen, storage copy verified, exact path given |
| Done | U9 | 20:16:22 | DONE |

## Pain points observed by the referee

| # | Observation | Messages | Severity |
|---|---|---|---|
| 1 | In the first full draft, Q3's hour and borough answer appeared only in speaker notes. The draft still passed `check-draft` and an independent fresh review, and the user had to catch the gap. A less careful user would have shipped a slide that does not answer part of a required question | A6, U7 item 1 | major |
| 2 | The full-draft turn took 16.6 min, longer than the whole analysis turn. The 5.7-min preview produced eight headlines. Time went on long package instructions, six chart specifications, and check-draft misreading numbers: slash pairs such as `54.8/57.6`, `18:00`, the `264/265` identifiers and a tolerance value. Repairs were then followed by a second full review | A5, A6; `feedback/harness-log.md` | major |
| 3 | The agent linked and quoted skill files to the user three times: awb-init SKILL.md twice in A1 and awb-package SKILL.md in A5. The user ranked this as the top pain point. The agent's notes call the skill-quote explanation mandatory under init's report rules; the harness note does not ask for it | A1, A5 | major |
| 4 | awb/setup recorded the MCP server's own interpreter, which lacked duckdb, as the project interpreter and has no interpreter argument. Fixing it took a shell `venv` plus the installer CLI. That fallback works under Codex here, but a host that cannot auto-approve terminal calls would turn it into user prompts | A1 | major |
| 5 | Jargon remained in the audience package. The user had "with zero-record tolerance" removed from the methods note, but the same phrase is still on the released appendix slide "How we know" (`storage/releases/.../001/findings.md`). Review guidance asks for tolerance wording in verification claims | U7 item 6, A7, release 001 | minor |
| 6 | The agent saved four review rules without asking whether each correction was general. It also put commit hashes and rule IDs in chat | A3, A6, A7 | minor |
| 7 | Progress counts were opaque: "1 answered" without naming Q4, "nine findings" against five questions, and a sixth root question (Vendor 6) added mid-run | A2, A4 | minor |
| 8 | The agent's interim reports (`cleaning-report.md`, `analysis-report.md`) carry internal IDs and terms such as canonical views, Q-008, run.py and deadheading. The user was pointed to both files | A2, A3 | minor |
| 9 | The interim MCP "failures" in the harness log (2 in turn 3, 5 in turn 6, 1 in turn 7) are guard refusals and validation exits, not transport errors. In one of them, export wrote files and then exited 1 | A3, A6, A7 | minor |

No loops, stalls or protocol breaches occurred. Neither role broke its rules. No number given to the user was wrong.

## Isolation audit

Agent logs: `relay/agent-001…009.jsonl`, rendered with `logview.py --full` to `referee/agent-logs-full.txt`.
- None of these paths appear: `workbench-spec`, `workbench-design`, `CONTEXT.md`, a `docs/` folder, analytics-workbench repository paths, `SIMDIR/human`, `SIMDIR/relay`, `transcript.md`, or `/Users/`.
- Paths outside SIMDIR: `<python-prefix>/bin/python3` and its stdlib, which is the interpreter the harness registered the MCP server with and the shell's `python3`. Also `/var/folders/.../xcrun_db-*`, from Apple git cache warnings. Neither is a content read.
- Turn 1: an ancestor scan looked for AGENTS.md and CLAUDE.md files up the parent directories, which the awb-init routine calls for. It found none. **Did not matter.**
- Turn 9, the feedback turn after DONE: the agent read `feedback/harness-log.md` for timings. That file is not on the forbidden list, the read came after the conversation, and it **did not affect the run**.
- The agent edited project files under `project/src/` (`src/preparation/*.sql`, `src/exploration/audit.py`). These are project-owned producer files it wrote itself, not helper source.

User logs: `relay/human-001…010.jsonl`.
- The user read only `human/BRIEF.md`, `human/README.md` and its own `notes.md`. In the project it read `cleaning-report.md`, `analysis-report.md` and the draft's `findings.md`, `methodology-note.md` and `START-HERE.md`, each of which the agent had pointed to. It also globbed `storage/releases`.
- No reads of AGENTS.md, SKILL.md, `src/`, `.py` files, `workbench-guides/` or agent homes. **Clean.**

Study-design note: the user persona volunteered most of the "if it asks" facts in U1, following the README's first-message template, and pre-answered package questions in U5 ("To save you asking"). This thinned the scoping interview to a single round. It is a known limit of the study and is tagged harness.

## Satisfaction

**9/10** (`feedback/human.md`). The point was taken off for internal process and jargon leaking into the chat.

## Most important issues for the workbench maintainers, ranked

1. **The package check does not verify that every dimension of a required question appears on a visible slide.** Q3's hour and borough detail sat only in speaker notes. It passed `check-draft` and a fresh independent review, and the user had to catch it (taxi-A-01).
2. **check-draft misreads numbers.** It treats slash-separated pairs (`54.8/57.6`), clock times (`18:00`), identifier codes (`264/265`) and tolerances as unsupported quantities. This forced repeated failed preflights and a methodology rewrite in the longest turn (taxi-A-02).
3. **awb-package is heavy.** The instruction layers are long and overlap, there is no lightweight preview state, and each repair needs a full fresh review. The preview took 5.7 min and the full draft 16.6 min, more than the analysis (taxi-A-03, 04, 15).
4. **Skill files are linked and quoted to the user.** It happened three times; the user ranked it the top pain point (taxi-A-05).
5. **awb/setup accepts an interpreter that lacks duckdb and offers no way to choose another.** Recovery needed CLI calls outside MCP. On hosts that cannot auto-approve terminal calls, that is a real cost (taxi-A-06).
6. **Internal language reaches audience text and chat.** Examples: the tolerance phrase that review guidance pushes in (still on the released appendix slide), record IDs in interim reports, commit hashes and rule IDs in replies (taxi-A-07, 08, 10).
7. **Review rules are saved without asking whether a correction is general** (taxi-A-09).
8. **Footer and status counts are opaque.** They do not name the answered question, do not explain findings versus questions, and count added context roots alongside the original questions (taxi-A-11).
