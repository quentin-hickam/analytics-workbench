# Referee report: taxi-B (variant B: Codex plays the user, headless Claude Opus plays the agent)

Paths are written as `SIMS/taxi-B/...`.

## Run summary

| Item | Value |
|---|---|
| Run / variant | taxi-B / B (user = Codex `codex exec`, agent = headless Claude Code with the awb skills and MCP server) |
| Relay started | 2026-10-17T11:17:42Z |
| Conversation ended | 2026-10-17T12:00:34Z (42.9 min) |
| Relay finished (after feedback turns) | 2026-10-17T12:02:12Z (44.5 min) |
| Outcome | DONE (user STATUS: DONE on message 8) |
| User messages | 8 written; 7 delivered and answered (message 8, the DONE, is not relayed by design) |
| Agent turns | 8 (7 replies + 1 feedback turn); 220 model turns in the 7 replies |
| Agent cost | $14.15 |
| Permission prompts logged | 0 (`SIMS/taxi-B/relay/permission-prompts.jsonl` was never created; every agent turn reports `denials=0`) |
| Relay errors | none (`relay.log` empty; harness log shows no MCP failures and no non-zero user commands) |
| User satisfaction | 7/10 (`SIMS/taxi-B/feedback/human.md`) |

## End-point checklist (from `SIMS/taxi-B/human/BRIEF.md`)

| Criterion | Met | Evidence |
|---|---|---|
| All five questions answered with specific answers the user accepts | Yes | Answers in agent replies 3 and 4. Accepted in user message 5 ("I accept the five descriptive answers"), again in messages 7 and 8. Ledger `SIMS/taxi-B/project/investigations/airport-trips-and-tipping/questions.md` shows Q-001 to Q-011 all `answered`, and every data question is linked to evidence files. All 11 findings in `state.md` are `supported`. |
| Asked where things stand at least once | Yes | User message 4: "Use awb-status — where are we, including unresolved caveats?". Agent reply 4 ran `mcp__awb__read command=status` (`SIMS/taxi-B/relay/agent-004.jsonl`) and gave a "Where we are" section. |
| Package draft exists and the user reviewed it | Yes | Draft at `SIMS/taxi-B/project/deliveries/airport-trips-and-tipping/board-briefing/draft/`. The user opened `findings.md`, `methodology-note.md` and `START-HERE.md` (`SIMS/taxi-B/relay/human-006.jsonl`) and asked for three wording corrections in message 6. |
| Released as 001 and copied to `storage/releases/` | Yes | `SIMS/taxi-B/storage/releases/airport-trips-and-tipping/board-briefing/001/` holds 12 files. `diff -r` against the project's `released/001` shows no differences. `manifest.json` records `status: release` and `release_number: 001`, with a scoped review and no accepted problems. Landed originals in `SIMS/taxi-B/storage/landed/data/raw/nyc-tlc/2026-10-17-inbox/` match the inbox files byte for byte. |

## The five questions

My spot-check script is `SIMS/taxi-B/referee/spotcheck.py`, and its output is `SIMS/taxi-B/referee/spotcheck-output.txt`. It runs DuckDB from the project's venv, read-only, on the landed copies. I re-implemented the validity rules from the agreed wording in the transcript: pickup outside the file's month, duration of zero seconds or less or over 3 h, distance of zero or less or over 100 mi, fare of zero or less, and speed over 65 mph. I did not copy the agent's SQL. I spot-checked all five questions. Every figure I tested matched to the last digit.

| Q | Agent's final answer (short) | Recorded result | Referee spot-check |
|---|---|---|---|
| 1 Volume by weekday/hour | Valid trips averaged 92,467 a day in January and 95,825 in July. July was busier midweek and January busier on Saturdays. Weekdays peak in the 6 pm hour. The full weekday by hour table is in reply 4. | `volume-by-weekday`, `volume-by-hour` | **Match.** Valid trips are 2,866,474 in January and 2,970,584 in July, which is 92,467 and 95,825 a day. |
| 2 Airport share, fares, durations | Airport trips were 9.9% of trips in January and 11.4% in July (282,144 and 336,348). Of these, 7.9% and 9.2% were from an airport and 2.3% and 2.6% to one. The base drops 20,060 and 20,248 no-airport trips with a missing zone. Median base fare was $54.80 and $57.60 against $12.10 and $12.80 for other trips. Median duration was 32.0 and 35.5 min against 10.8 and 11.7. | `airport-share`, `airport-fares-durations`, `newark-rate-sensitivity` | **Match** on every number: 9.91% / 11.40%, 7.93 / 9.17, 2.25 / 2.59, dropped 20,060 / 20,248, and medians 54.8 / 57.6 / 12.1 / 12.8 and 32.0 / 35.5 / 10.8 / 11.7. |
| 3 Card tip % by hour and borough | The median tip was 26.25% of base fare in January and 25.65% in July (n 2,296,318 and 2,229,862). No-tip trips were 4.7% and 6.6%. Hourly medians run from about 24% to 28%. Manhattan is about 26.6%, Queens about 23%, and Bronx/Brooklyn 0% with the vendor-1 rate-code-99 sensitivity check. | `tips-by-hour`, `tips-by-borough`, `tips-ratecode-99-sensitivity` | **Match**: 26.25 / 25.65, 4.7 / 6.6, and identical n. |
| 4 Invalid fraction, by vendor | 204,469 of 6,041,527 records (3.4%) are invalid: 3.3% in January and 3.5% in July. By vendor: vendor 1 3.6%, vendor 2 3.3%, vendor 6 35.4% (of 260). 2,433 records exceed 65 mph. | `invalid-records` | **Match**: 204,469; 98,150 / 106,319; vendor 1 52,310 of 1,447,436 (3.61%), vendor 2 152,067 of 4,593,831 (3.31%), vendor 6 92 of 260 (35.38%); speed 2,433. |
| 5 Top 10 zones by fare per trip hour | All ten are in Queens: Flushing Meadows-Corona Park $169.00 (1,189 trips) … Jackson Heights $89.82. Minimum of 1,000 valid trips, both months. | `top-zones-fare-per-hour` | **Match**: the same ten zones in the same order, with the same trip counts and the same $/hour to the cent. |

I also checked that payment_type 0 is explicit and never null: 140,162 in January and 278,989 in July, with 0 nulls. That matches the agent's correction in reply 4.

## Timeline

| Phase | Messages | Time (UTC) | Notes |
|---|---|---|---|
| Init | U1 → A1 | 11:18 to 11:19:47 | `awb-init`: venv, MCP `setup`, storage paths in README. The agent also peeked at the inbox Parquet before landing. |
| Scoping | A1, U2, A2, U3 | 11:19 to 11:26 | Four decisions in round 1 (tip median, airport definition, invalid rules, fare per hour), then speed limit, missing geography and permission to read the dictionary. The agent correctly overturned the user's premise that the weekday mix differed between the months. |
| Landing | A2 | 11:20 to 11:25 | Landed 3 files with a storage copy, published 6,041,527 trips and 265 zones, and found 1 exact duplicate. |
| Cleaning | (no `awb-clean`) | n/a | The validity rules were settled in scoping and applied in a shared flagged view. No scans exist, which later fed the review friction. |
| Exploring | A2, A3 | 11:20 to 11:35 | Speed distribution, missing geography, the rate-code-99 zero-tip anomaly and payment code 0. |
| Answering | A3, A4 | 11:26 to 11:40 | 11 results, all five questions answered (provisional), the TLC dictionary downloaded and retained, the tip sensitivity check, and complete tables in A4. |
| Status | U4 → A4 | 11:36 to 11:40 | Status ran, but the MCP output was truncated (5,233 characters cut). |
| Packaging (headline preview) | A4 | 11:40 | 8 main slides plus 3 appendix slides proposed. Q1 and Q5 were moved to the appendix. |
| Packaging (full draft + review) | U5 → A5 | 11:40:32 to 11:53:56 | Draft, a full review (21 narrative problems), repairs, a scoped review (2 narrative problems), then the stop rule handed a two-word wording choice to the user. |
| User review | U6 → A6 | 11:54:17 to 11:59:44 | The user asked for three wording fixes. Two scoped reviews followed (1 rule error and 3 narrative problems, then clean). A result was rerun to record a flat-fare check. |
| Release | U7 → A7 | 11:59:54 to 12:00:21 | Release 001 in 27 s, storage copy verified. |
| End | U8 (DONE) | 12:00:34 | |

## Package review loop (the perfectionism check)

Source: `python3 KIT/reviewloop.py SIMS/taxi-B`. The review reports are extracted to `SIMS/taxi-B/review-reports/`.

| User request | Review rounds | User waited | Review tail (first review start to reply) | Outcome |
|---|---|---|---|---|
| U4: status + headlines (preview only) | 0 | 4.0 min | none | Headline preview, no review needed |
| U5: full draft + methodology note | 2 (full, scoped) | 13.4 min | 6.2 min | Full review found 0 violations and 21 narrative problems. The scoped review found 2 narrative problems that the repair itself created. The stop rule then took the choice to the user. |
| U6: three wording corrections | 2 (scoped, scoped) | 5.5 min | 4.6 min | 1 rule violation (error) and 3 narrative problems, then clean |
| U7: release 001 | 0 | 0.5 min (27 s) | none | Release passed first time |

Totals: 4 review rounds across two requests, all inside the two-per-request cap. Packaging turns took 24 of 41 agent minutes (58%), and the review tails took about 11 minutes (26%). The `starts=1 (?)` that reviewloop shows for agent-008 is a false positive. That turn is the feedback turn, and its only tool call is the Write of `agent.md`, whose text mentions "review-receipt start".

**Verdict: no runaway loop, but the reviewer is still strict.** The cap and the stop rule held: there was never a third round in one request, and release went through first time. What the 21 first-round problems were:
- **About 6 were real catches.** July's tip peak is a tie at 6 pm and 7 pm (27.3418 against 27.3446). July's Newark pickup median fare is $82.52, not "near $90". Four sentences had no recorded support: JFK trips "mostly flat fare", cash trips show "almost no tips", trips show "no extra or congestion charges", and "limitations don't change the airport finding".
- **About 15 were citation-form complaints.** "Every" or "exactly" claims needed result IDs or `foundation/scans/` paths, and DQ rows that cite exploration queries were rejected. "Flagged" was rejected as a record word outside Implications. Four were the same sentence in two files.

Remaining signs of perfectionism:
- In round 3 the reviewer challenged wording the user had asked for ("including flat fares"). The agent had to rerun `airport-fares-durations` only to record a check, which demoted a supported finding and forced it to be promoted again.
- The new review rule, added at the user's request, immediately flagged the methodology's own sentence describing the rule.
- The stop rule cost the user a decision on "lack other fields" against "lack a passenger count". The user handled it inside a message that had substantive review anyway, so it did not cost a separate turn.

## Pain points seen as referee

| # | Pain point | Messages | Severity |
|---|---|---|---|
| 1 | The agent stated untested explanations as fact: "timing errors", Outside-NYC trips "mostly heading to Long Island or Westchester", code 0 "is a Flex Fare trip", and a "recording gap". It also said "about 419,000 trips … have no payment type" when the value was an explicit 0. The user had to police the line between observation and explanation four times. | A1, A2, A3, U3, U4, U5 | major |
| 2 | After seeing the outcome, the agent recommended dropping the vendor-1 rate-code-99 group from the primary tip figures and calling the rest "reliable". That framing could have steered a public tipping position. The user overrode it in favour of a sensitivity check. | A3, U4 | major |
| 3 | Review strictness on citation form: 21 narrative problems on the first pass, most about how evidence is cited rather than about the numbers; a rerun only to record a definitional check; demotion and re-promotion of a finding. See above. | A5, A6 | major |
| 4 | The `status` MCP output was truncated (16.5 KB payload, 5,233 characters cut into an overflow file in `/tmp`). The overflow file was outside the sim's allowed paths, so the agent rebuilt the questions section by hand. | A4 | minor |
| 5 | The agent read inbox data before landing, and proposed the speed threshold after looking at the distribution of affected rows. The README says thresholds come before the agent sees which rows lead. The guidance is inconsistent: awb-scope says to "look facts up yourself", while data.md says to inspect only landed copies. | A1, A2 | minor |
| 6 | The agent marked Q1 and Q5 as `should` in the ledger without asking. It then used that label to move them to the appendix. The user disputed the label in their notes but accepted the appendix. | A2 (ledger), A4 | minor |
| 7 | The closing line said "0 open" while a user decision (Q-011, tip population) was pending. | A3 | minor |
| 8 | The agent edited `sources.md` with a string replace that silently changed nothing. The source kept "reference: not yet retained" for two turns. Status did not flag it; the reviewer caught it. | A3 to A5 | minor |
| 9 | The release chat called the outline and chart files "for the board", contradicting `START-HERE.md`, which sends them to the deck builder. | A7 | minor |
| 10 | After release, `state.md` still listed "Preview the slide headlines with Dana before drafting the package" as the next step. Its airport finding still said "JFK trips mostly pay the $70 median fare", wording the reviewer had removed from the deck. | after A7 | minor |
| 11 | The agent downloaded the TLC PDF with `curl -A "Mozilla/5.0"` (a browser user-agent). The persona says the site blocked downloads; in the sim it returned 200. Whether the spoofed user-agent was needed is unknown. | A3 | minor |
| 12 | Interim progress messages kept naming internal files and steps ("Now state.md", "Ledger done", "Exporting needs display names") after the user asked for results-focused updates. | A2 to A6 | minor |
| 13 | The Codex user's first message began with a stray preamble line ("I'll read BRIEF.md and README.md…"). The persona also front-loaded facts it should have given only if asked: storage paths, the cash-tip suspicion, the headline preview. | U1 | minor (harness) |

**Isolation audit.**
- **Agent**: every Read, Grep, Glob, Write and Edit path and every Bash path in `agent-001` to `agent-008`, including 106 reviewer-subagent tool calls, stays inside `SIMS/taxi-B` (project, simulated agent home, feedback). Nothing touched `workbench-spec`, `workbench-design`, `CONTEXT.md`, `docs/`, the source repository, `human/`, `relay/` or `transcript.md`, and no path under the real home appears. The only network access was the user-authorized TLC dictionary URL. The `/tmp/awb-mcp-…` overflow file is mentioned only in note text; the agent never read it. No hits.
- **User**: the Codex user read only `BRIEF.md` and `README.md` (its own human folder), the three draft files the agent pointed to, the released `START-HERE.md`, and its own `notes.md`. It read no `AGENTS.md`, `SKILL.md`, `src/`, `.py`, `workbench-guides/` or agent home. No hits.

**Identity audit.**
- **Git identities:** all 14 commits have author and committer "Sim Analyst" with the example.com address.
- **Commit messages:** each carries a co-author trailer with a vendor no-reply bot address. That is not a person.
- **No leaks found:** no real person's name, no other email address and no `/Users/` path in the project working tree, `.venv`, storage or git history.
- **Harness-caused exposure:** the sim root path itself contains the host account's username in encoded form. That absolute path appears in:
  - the project's `README.md` (storage locations);
  - `foundation/sources.md`;
  - `.venv/pyvenv.cfg`;
  - git history, through `README.md`.

  The venv also records the host's Python install location (under `/opt`), which is a machine detail rather than an identity.

## Most important issues for the workbench maintainers (ranked)

1. **Observation versus explanation (pain point 1).** Early answers turned patterns into causes or labels: Flex Fare, timing errors, recording gap, inferred destinations, "missing" for an explicit code. The user had to correct this repeatedly, and it is the main reason they scored 7/10. The skills should make the agent say which statements are observed and which are hypotheses from the first profile onward.
2. **Choosing exclusions after seeing outcomes (pain point 2).** The analysis guidance should keep the agreed population as primary and offer a sensitivity check by default, never recommend a post-hoc exclusion as the headline figure, and never call the remaining records "reliable".
3. **Review evidence forms (pain point 3).** Let a saved exploration query, with its checksum, count as citable support for context sentences. Do not demote a supported finding when only a judgment's detail text changes. Do not apply a review rule to the methodology's own description of that rule. Do not demand a recorded check for definitional wording the user asked for, when the dictionary is retained. Accept `joins` as not applicable for aggregate results.
4. **Status payload size (pain point 4).** Add a summary or per-section status so one MCP response holds it.
5. **Pre-landing inspection and threshold timing (pain point 5).** Reconcile awb-scope with data.md, and say how choices informed by a first look are recorded.
6. **Question bookkeeping (pain points 6 and 7).** Do not set must/should priorities without the user. Count pending decision sub-questions as open in the closing line.
7. **Stale records after release (pain point 10)**, and a release chat handoff that does not match `START-HERE.md` (pain point 9).
8. **Minor helper ergonomics:** a scaffold for a new investigation, adding several questions in one call, multi-column `@where` in export, noisy number warnings on review rules, an answerer value for documentation lookups, and the duplicated caveat line in release output.
