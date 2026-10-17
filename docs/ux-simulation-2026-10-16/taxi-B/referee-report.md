# Referee report: taxi-B (variant B)

Variant B: Codex (`codex exec`) played the user, Dana Ortiz (mobility policy analyst, NYC taxi Jan/Jul 2024 board deck). Claude (Opus, headless `claude -p`, real skill discovery) played the agent with the awb skills and the awb MCP server.

## Run summary

| Item | Value |
|---|---|
| Relay started | 2026-10-16T19:16:54Z (fresh start; state was empty) |
| Conversation ended | 2026-10-16T20:52:49Z, outcome **DONE** |
| Relay finished | 2026-10-16T20:54:31Z, phase `finished` (no crash, no restart) |
| Wall-clock | 95.9 min conversation, 97.6 min total including feedback |
| User messages | 8 sent; 7 delivered and answered by the agent; message 8 (DONE) not relayed, by design |
| Agent replies | 7 in conversation; 8 agent turns including the feedback turn |
| Agent cost | $35.51 (reply 5 alone: $21.71, 58.5 min) |
| Permission prompts | 0 (`relay/permission-prompts.jsonl` was never created) |
| Caps | not reached (45 messages / 8 h) |
| User satisfaction | **7/10** (`feedback/human.md`) |

## End-point checklist (BRIEF.md, "The path to the end point")

| Criterion | Met | Evidence |
|---|---|---|
| All five questions have specific answers the user accepts | Yes | Msg 5: "I accept the five descriptive answers with the caveats"; msgs 7-8 accept the package. Ledger `project/investigations/airport-trips-and-tipping/questions.md`: Q-001 to Q-005 `answered`, each linked to recorded results; `findings.json`: all 17 findings `supported`. |
| `awb-status` (or "where are we") asked at least once | Yes | Msg 4: "Use awb-status — where are we…". Agent loaded the `awb-status` skill and called MCP `read status` twice (`relay/agent-004.jsonl`); reply 4 opens with "Where we are". |
| Package draft exists and the user reviewed it | Yes | Draft at `project/deliveries/airport-trips-and-tipping/board-briefing/draft/`. User log `relay/human-006.jsonl` shows `cat` of START-HERE.md, findings.md, methodology-note.md; msg 6 asks for four corrections, msg 7 reviews the revised text. |
| Released as 001 and copied to the releases folder | Yes | `project/deliveries/.../released/001/` and `storage/releases/airport-trips-and-tipping/board-briefing/001/` (22 files). Referee `diff -rq` of the two trees: identical. User `ls` of the stored folder in `relay/human-008.jsonl`. |

Landed originals: `storage/landed/data/raw/tlc-yellow-trips/2024-01-and-07/` and `tlc-taxi-zones/2026-10-16/`. Referee SHA-256 matches the inbox files exactly.

## The five questions

Screening rules as stated to the user: pickup outside the file's month, drop-off not after pickup, over 6 h, distance 0 or over 100 mi, base fare ≤ $0 or over $500, over 60 mph, or a paid trip with a negative charge. Zones 264/265 are treated as unknown. The referee's scripts are `referee/spotcheck.py` and `referee/spotcheck2.py`, with outputs in `referee/spotcheck-output.txt` and `spotcheck2-output.txt`. They ran in the project's `.venv` (duckdb 1.5.6) on the landed files, written independently of the agent's queries.

| Q | Agent's final answer | Recorded? | Referee spot-check |
|---|---|---|---|
| 1 Volume by weekday/hour | Trips per weekday occurrence, Jan → Jul: Mon 78,548 → 89,031 (+13%), Tue 89,737 → 104,148 (+16%), Wed 96,069 → 106,635 (+11%), Thu 103,958 → 99,943 (−4%), Fri 99,001 → 91,619 (−7%), Sat 101,685 → 91,244 (−10%), Sun 81,564 → 85,103 (+4%). Both months peak at 18:00 (206,089 / 207,146); July higher late evening (22:00: 138,090 → 159,045). Full 336-row weekday × hour table supplied. | Yes: `volume-by-weekday`, `volume-by-hour`, `volume-by-weekday-hour` (supported) | **Exact match** on all 14 weekday cells. Calendar check confirms both months have 5 Mon–Wed and 4 Thu–Sun (the user's objection in msg 4 was wrong; the agent was right). |
| 2 Airport share, fares, durations | 9.91% (Jan, 282,179) → 11.4% (Jul, 336,396) of classifiable screened-in trips. JFK 5.65 → 6.68%, LGA 4.04 → 4.46%, EWR 0.23 → 0.26%. Median base fare $54.80 / $57.60 vs $12.10 / $12.80 for other trips; median duration 32.0 / 35.5 vs 10.8 / 11.7 min; median total paid $77.04 / $78.25 vs $19.20 / $19.80. | Yes: `airport-share`, `airport-fares-durations` | **Exact match** when "classifiable" means known zones at both ends *or* an airport at either end (the agent's definition, stated on the chart source line). Other defensible denominators move the share: both ends known gives 9.67% / 11.06%, all screened-in trips 9.84% / 11.32%. The difference matters only at the third digit; the definition is disclosed. |
| 3 Card tip % by hour and borough | Median card tip (zeros included) 26.3% Jan / 25.6% Jul; no-tip 4.67% / 6.6%. Hourly 23.6% (5 a.m.) to 28.0% / 27.3% (6 p.m.). Manhattan 26.6 / 26.3%, Queens 23.1 / 22.8%. Brooklyn and Bronx 0.0%, driven by vendor 1 rate-code-99 card trips that record $0 tips (sensitivity excluding them: Brooklyn 23.2 / 22.9%, Bronx 12.1 / 21.0%). Cash tips not recorded (TLC dictionary plus data: ≤0.01% of cash trips show a tip). | Yes: `tips-by-hour`, `tips-by-borough`, `payment-mix` | **Exact match**: unrounded medians are 26.25% and 25.65% overall, and 26.61% and 26.25% for Manhattan. Brooklyn and Bronx medians are 0.0 with no-tip shares of 68.93 / 75.5% and 96.7 / 93.91%. Queens no-tip 8.29 / 9.25%. |
| 4 Invalid records by vendor | Screening set aside 3.31% Jan (98,032 of 2,964,624) and 3.45% Jul (106,199 of 3,076,903). Vendor 1: 4.78% → 2.41% (mostly distance); vendor 2: 2.82% → 3.77% (mostly fare ≤ $0); vendor 6: 260 Jan records, 35.38%. Counts reconcile (input = screened-in + set aside; zone joins preserve trips). | Yes: `screening-by-vendor`, `screening-by-rule`, `record-reconciliation` | **Exact match** on every month and vendor count and share. |
| 5 Top 10 zones by fare per trip-hour | No minimum, Jan + Jul combined: Newark Airport 131 trips, 17.42 trip-hours, $564.64 (median recorded duration 0.3 min, flagged); Mariners Harbor $218.64; Charleston/Tottenville $191.76; …; Kew Gardens $128.87. Zones with 10,000+ trips (53): JFK $95.53 (308,913 trips), East Elmhurst $91.48, LGA $91.39, Battery Park City $77.00 … Lower East Side $72.40. Labelled "not driver earnings". | Yes: `top-zones-revenue-per-hour`, `top-zones-10000-trips`, `newark-pickup-durations`, `zone-count-check`, `top-zones-keeping-high-fares` | **Exact match** on all 10 rows of both rankings (trips, trip-hours, rates) and on the Newark diagnostics (8.0 mean min, 0.32 median, 77.9% under 5 min). |

All five answers reproduce from the source data. None is unsupported.

## Timeline

| Phase | Messages | Time (UTC) | Notes |
|---|---|---|---|
| Init + scoping round 1 | msg 1 → reply 1 | 19:17–19:19 (1.8 min) | `awb-init`, MCP `setup` check + install, `.venv` created with uv; `awb-scope` asks four bundled decisions with recommendations. Agent peeked at inbox parquet with raw DuckDB before landing. |
| Scoping records, landing, publishing, cleaning scan | msg 2 → reply 2 | 19:19–19:24 (4.4 min) | Investigation created; files landed to user storage and verified; TLC dictionary fetched; publish failed twice (TOML inline table; regex matched directory name and the declared key check caught it); `awb-clean` scan; four cleaning decisions put to the user. |
| Cleaning decisions, exploring, answering (provisional) | msg 3 → reply 3 | 19:24–19:31 (7.6 min) | `clean-record`, `awb-explore` eda-scan, 12–13 `run.py` results; code-0 totals checked per the user's correction. Agent applied an unapproved 1,000-trip minimum and proposed dropping rc99 zero tips. |
| Corrections + status | msg 4 → reply 4 | 19:31–19:35 (3.2 min) | `awb-status` surfaced two record errors of the agent's own; agent correctly rebutted the user's calendar claim; full tables and corrected headlines. |
| Packaging | msg 5 → reply 5 | 19:35–20:34 (58.5 min, $21.71) | `awb-package`: draft written, then **15 full reviewer subagent runs** before a clean pass. The user was told "thirteenth review". |
| Package review and revision | msg 6 → reply 6 | 20:34–20:43 (8.9 min) | User found four substantive problems that 15 reviews missed (note length, base-fare definition, Newark durations, unchecked row counts and joins). Corrections recorded as review rules; reconciliation result added; 2 reviews. |
| Release | msg 7 → reply 7 | 20:43–20:52 (9.3 min) | `awb-release`: 4 release reviews (one found an issue a prior clean review passed; a fix then broke the ~500-word rule); release 001 frozen and copied; compare clean. |
| Done | msg 8 | 20:52:49 | User confirmed the stored copy with `ls`. |

Analysis (init through answers) took about 17 minutes. Packaging, review and release took about 77 minutes, 80% of the conversation and about 85% of the agent cost.

## Pain points observed by the referee

| # | Severity | Observation | Where |
|---|---|---|---|
| 1 | major | The package review loop does not converge: 15 full reviews in reply 5, 2 in reply 6 and 4 in reply 7, 21 reviewer subagents in all. Reviewers drifted (one wanted counts on a slide, the next called it too dense). A release review flagged an R-rates-001 violation that the previous "clean" review had passed. | reply 5–7; `relay/agent-005.jsonl`, `agent-007.jsonl`; `feedback/harness-log.md` |
| 2 | major | The 15 reviews fixed wording nits but missed four problems the user caught in one read: the methods note was far over one page, base fare was defined as meter time-and-distance despite flat-fare findings, Newark's short durations were missing from the main caveat, and the methods text said row counts and joins were not checked. | msg 6 |
| 3 | major | Validation leaves `row_counts, joins` "not assessed" by default. Every finding carries that boilerplate, including `record-reconciliation`, whose result is itself the check. Reconciliation happened only because the user asked. | `state.md` caveat column; msg 6; reply 6 |
| 4 | major | Method choice made after seeing results: the agent applied an unapproved 1,000-trip zone minimum, then recommended 10,000. It also proposed excluding rc99 zero-tip trips because they made the borough medians 0%. Both contradicted or went beyond agreed scope; the user had to intervene. | reply 3; msg 4 |
| 5 | minor | Records drift from the released package. The `volume-by-weekday` finding still says "each includes one holiday (New Year's Day, Independence Day)" and "Monday to Wednesday"; the package says January also has MLK Day and "Sunday to Wednesday". `tips-by-borough` says rc99 trips "all record zero tips"; the package says "almost all". | `investigations/.../findings.json` vs `storage/releases/.../001/findings.md` |
| 6 | minor | The user-facing review count understated the work: messages counted to "Thirteenth review", but 15 reviewer runs happened (the first review's result was never announced). | reply 5 vs `agent-005.jsonl` |
| 7 | minor | The status and ledger count questions as "answered" on first `run.py` while their answers hung on open user decisions (Q-003, Q-005). | reply 3 ("5 answered (provisional)") |
| 8 | minor | Internal mechanics were narrated to a non-technical user: "private notes file", helpers, "zsh word-splitting slip", "the script ignored the extra arguments". | replies 1, 6 |
| 9 | minor | The agent asked again about code-0 treatment after the user had specified it. | reply 2 vs msg 2 |
| 10 | minor | Zone 265 ("Outside of NYC") is treated as unknown together with 264. It is a known location class. Effect on the airport share is negligible (9.90% vs 9.91%), but the methods text calls it "unknown". | referee check, `spotcheck2-output.txt` |
| 11 | minor | Tooling errors along the way, all recovered: TOML multi-line inline table, `p1.partial` left after a failed publish, `export` refusing before the draft folder exists, chart-spec blank-line ambiguity, `check-draft` claim-word false positives, `check-draft` not flagging methodology citations of unrepresented results, MCP `setup` reporting pre-install state. | `feedback/agent.md` §3 |
| 12 | minor (isolation) | Agent read 8 of its own spilled tool-result files under the real `~/.claude/projects/...` (turns 5, 7). In turn 1 it listed directory names of SIMDIR's parent and `/private/tmp/claude-501`, and checked for CLAUDE.md/AGENTS.md up the tree. In turn 5 it wrote a temp script to `/tmp`. None of this exposed outside knowledge. | `referee/agent-005.view.txt` lines 9, 11, 248, 291, 293, 318, 464; `agent-007.view.txt` 52; `agent-001.view.txt` 3, 55 |

Positive evidence: zero permission prompts. Landing copied and verified the originals. The declared key check caught a real bug. `awb-status` found two genuine record errors. The `check-draft` numbers rule forced every narrative number back to a recorded result, which produced the zone-count-check and reconciliation results. The agent rebutted a wrong user claim with evidence. All numbers reproduce exactly.

## Isolation audit

**Agent** (`relay/agent-001…008.jsonl` via `logview.py --full`):
- No reads of `workbench-spec`, `workbench-design`, `CONTEXT.md`, any `docs/` folder, the analytics-workbench repository, `SIMDIR/human`, `SIMDIR/relay` or `transcript.md`.
- No awb MCP `read`/`data` SQL touched files outside the project. MCP calls were `setup` ×2, `read` ×3 (help, status ×2), `records` ×3 (clean-record) and `data` ×2 (clean-scan, eda-scan). SQL `read_parquet`/`read_csv` targets were all project-relative or the inbox.
- Hits under the real home (`/Users/`): 8 Reads of `~/.claude/projects/<sim-project-key>/<session>/tool-results/*.txt`, at turn 5 (2 main, 5 subagent) and turn 7 (1 subagent). These are Claude Code's own spill files for oversized tool outputs. The model is told to read them back, and they contain only the agent's own command output. **Did not matter.** Cause: Claude Code's session storage is not redirected to the simulated home (harness).
- Turn 1: `ls -la project/..` (names of SIMDIR entries, including `human`, `relay`), `ls <scratch>` (names only), and existence checks for CLAUDE.md/AGENTS.md up to `/`. No contents read. **Did not matter.**
- Turn 5: wrote `/tmp/awb-export-board.sh`, later moved it into `agent-home/scratch/`. Write outside bounds; **did not matter.**
- Turn 2: `curl` of the TLC data dictionary from nyc.gov, a URL the user gave in the brief and the README. Allowed. Note that the persona premise ("the site blocked the download") did not hold for the agent.

**User** (`relay/human-001…009.jsonl`): commands were `cat BRIEF.md README.md`, `cat README.md`, `cat` of the three draft files the agent pointed to (START-HERE.md, findings.md, methodology-note.md), and `ls` of the stored release folder. No reads of `AGENTS.md`, `SKILL.md`, `src/`, `.py` files, `workbench-guides/` or agent homes. Clean.

## Harness events

- Pre-start `relay.py status` printed `DEAD {}` because there was no state yet; the relay was then started fresh. It finished normally, with no DEAD or crash and no restart.
- User message 1 began with a Codex meta-line, "I'll read BRIEF.md and README.md, then follow the simulation's response format.", which the relay passed to the agent verbatim. The agent ignored it.
- The agent's system note says "The user sees only your final reply each turn", but the relay passes interim messages by design. Interim implementation narration therefore reached the user and drew complaints.
- Persona front-loading: msg 1 gave storage paths, the exclusion policy, the dictionary doubt and the headline-preview request up front. This is the known study limit, and it thinned the scoping interview to one round plus cleaning decisions.
- The persona made a factually wrong calendar objection (msg 4) and retracted it in msg 5.
- The user's private notes are offset by one turn (note N describes agent reply N−1).
- Reply 5 ran as a single 58.5-minute agent turn; no timeout was hit.
- Both feedback files were written: `feedback/agent.md` (agent-008) and `feedback/human.md` (human-009).

## Most important issues for the workbench maintainers (ranked)

1. **Make package review converge** (`awb-package` review reference). Use a fixed checklist with severities so minor style findings do not block, allow a scoped re-review to complete small diffs, and stop reviewer drift. One request cost 15 full reviews, 58.5 minutes and $21.71. Release added 4 more, one of which reversed an earlier clean verdict.
2. **Point reviews at substance, not just wording.** Each review should check the user's standing requirements: page length, definitions consistent with findings, caveats beside outliers, validation claims. The user caught four substantive defects that 15 reviews missed.
3. **Make reconciliation a default result.** Input = kept + excluded, and joins preserve row counts. Stop stamping "not assessed: row_counts, joins" on every finding, including the one that performs the check.
4. **Add a result-level decision rule to the analysis guidance.** "A threshold, minimum or exclusion not in the brief is a user decision; ask before recording a finding that depends on it." This prevents post-hoc filters like the 1,000-trip minimum and the rc99 exclusion proposal.
5. **Keep records in step with the package.** Corrections made during review (holiday list, "almost all") should flow back to `findings.json` and `state.md`, or `check-draft` should flag claim drift and not only number drift.
6. **Support investigation-local shared SQL.** The screening CTE was copied into 15+ queries, and `[eda] where` repeated the rules as literals.
7. **Fix the small tooling papercuts** in pain point 11 (`findings.json` taxi-B-15 to taxi-B-21), and add a README section for analysts on what "checked" covers and when a draft is stable.
