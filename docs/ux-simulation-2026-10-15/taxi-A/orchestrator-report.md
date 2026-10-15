# Orchestrator report: taxi-A

## Run summary

- **Variant:** A. Opus played the human (nested subagent `taxi-A-human`, persona Dana Ortiz, mobility policy analyst). Codex played the agent (session `01a13f93-a054-7633-b2d6-9f8b05a7f814`, run through `kit/simctl.py`).
- **Dataset:** NYC TLC yellow taxi, January and July 2024 (6,041,527 records), plus the zone lookup.
- **Start:** 2026-10-15 12:39:11Z (playbook read). First message to the agent: 12:40:01Z.
- **Conversation end:** 14:55:03Z, when the human sent `STATUS: DONE`. Feedback was complete at 14:57Z.
- **Wall-clock:** about 2 h 16 min to DONE and 2 h 18 min including feedback. The 8 h cap was not approached.
- **Turns:** 12 human messages. The 12th was the DONE message and was not relayed. There were 11 conversational agent turns and 1 feedback turn. The 45-message cap was not approached.
- **Agent turn durations:** 4 to 21 minutes (median about 9). The longest was turn 9, the full deck build, at about 21 min.
- **Protocol incidents:** none. Every Codex turn finished on its first attempt, with no FAILED and no retries. The human always replied in protocol format. The conversation never looped and no harness notes were needed after turn 1.
- **Fallback:** not used. The orchestrator played no role.
- **Transcript note:** `simctl.py send` already appends each relayed human message to `transcript.md`, so I logged only the final unrelayed human message (DONE) with `simctl.py log`. That avoided duplicate entries. The feedback request appears in the transcript as "HUMAN → agent (turn 12)" because simctl labels every agent input that way. It is the harness note, not a user message.

## End-point checklist

| Criterion | Met? | Evidence |
|---|---|---|
| All five questions answered specifically and accepted by the human | Met | Q1 and Q2 accepted in human msg 5, Q3 in msg 7, Q4 and Q5 in msg 8. `project/investigations/yellow-taxi-monthly-patterns/questions.json` has all of Q-002..Q-006 `answered`: 18 answered, 4 open, and the 4 open are TLC/provider and source-interpretation questions. |
| Human asked where things stand at least once | Met | Human msg 7 ("Use awb-status — where are we?"). The agent's status summary is in turn 7. |
| Deck package draft exists and was reviewed | Met | `project/deliveries/yellow-taxi-monthly-patterns/board-decisions/draft/` (board-deck.pdf/.pptx, methodology-note.pdf). Storyline reviewed in msg 9, full deck in msg 10 (5 corrections), corrected deck in msg 11. |
| Released as 001 and copied to the releases folder | Met, with a defect | `storage/releases/yellow-taxi-monthly-patterns/board-decisions/released/001/` has 25 files including board-deck.pdf/.pptx and methodology-note.pdf. A local copy is in `project/deliveries/.../released/001/`. **Defect:** the released files still say they are drafts. See issue 1 below. |
| Landed originals at the requested location | Met | `storage/landed/data/raw/tlc-yellow/supplied-20261015/` (both parquet files plus provenance.json) and `storage/landed/data/raw/tlc-zones/supplied-20261015/`. |
| Findings recorded | Met | `findings.json` holds 40 findings, all `supported`. Evidence JSON and saved SQL for each are under `investigations/yellow-taxi-monthly-patterns/{evidence,queries}/`. |

## The five questions

My spot-check used the project venv's duckdb on the original `inbox/` files, run from my own scratch folder (`sims/orch-checks-taxiA/check.py`). It recomputes the agent's stated screening rules independently: fare ≤ 0, distance ≤ 0, duration < 1 or > 180 min, speed > 80 mph, pickup outside the file month.

| # | Agent's final answer (abridged) | Recorded? | Orchestrator spot-check |
|---|---|---|---|
| 1 | Retained trips rose 3.59%, from 2,858,883 to 2,961,523. Holiday-excluded weekday change: Mon +10.0%, Tue +16.0%, Wed +11.0%, Thu +9.1% (−3.9% with July 4 included), Fri −7.5%, Sat −10.3%, Sun +4.2%. 6 pm busiest in both months; late evening (9–11 pm) grew 11.9–15.2%. | Yes: volume-monthly/weekday/hourly/grid and holiday-* evidence | **Match** for retained totals: 2,858,883 and 2,961,523. Weekday figures not recomputed. |
| 2 | Airport trips (either endpoint JFK/LGA/EWR) were 280,663 (9.82%) in January and 334,061 (11.28%) in July, carrying 29.77% and 32.11% of fare revenue. Median fare $54.80→$57.60 vs $12.10→$12.80 for other trips. Median duration 32.12→35.65 vs 10.83→11.78 min. Airport volume +19.0% vs +1.9% for other trips. | Yes: airport-summary/detail/changes | **Exact match** on every figure: count, share, revenue share, median fares and median durations. |
| 3 | Tip % is the median of tip ÷ fare including zeros, card trips only, cash tips absent. All vendors: 26.25% (Jan) and 25.65% (Jul). Lead view is Curb-only by borough: Manhattan 26.61/26.25, Queens 23.13/22.88, Brooklyn 23.23/22.84, Bronx 15.90/21.05 (n=154/339). Staten Island omitted. Hourly Curb range about 24.5–27.8%. All-vendor Brooklyn/Bronx medians of 0% are a CMT artifact, an open question for TLC. | Yes: tip-* evidence | **Exact match** for overall medians and card trip counts (2,293,326 / 2,226,243), and for every Curb borough median and sample size. |
| 4 | Any-rule flag rate: 3.567% (105,741) in January, 3.750% (115,380) in July. By rule: fare 38,341/59,730; distance 60,371/48,045; duration 37,104/43,421; speed 1,107/1,091; out-of-month 18/47. By vendor: CMT 4.86%→2.49%, Curb 3.14%→4.13%, Myle 35.77% (260 January records only). | Yes: record-quality, quality-rules | **Exact match** for every rule count, the union, and all vendor percentages, Myle included. |
| 5 | Board definition: ≥100 trips and ≥10 occupied hours. Flushing Meadows-Corona Park is set aside pending TLC verification (JFK-rate $70 trips with no JFK endpoint). January top 3: Maspeth $117.01, South Ozone Park $111.86, Kew Gardens $108.02. July top 3: Elmhurst/Maspeth $120.95, Kew Gardens $117.10, Randalls Island $110.51. | Yes: zone-board-top10, flushing-* | **Match** for all ten zones and rates in both months. **Undisclosed in chat:** the ranking also excludes the "Outside of NYC" pseudo-zone (ID 265). Without that exclusion it would rank #1 in July at $181.83 and #3 in January at $115.53. The exclusion is reasonable and is stated in the methodology note and the slide-6 footnote, but the user was never told in conversation. |

No numeric discrepancies found.

## Timeline

| Phase | Turns (human msg → agent reply) | Time (Z) |
|---|---|---|
| Init | 1 | 12:40–12:44 |
| Scoping (one question on decision thresholds, answered in msg 3) | 1–3 | 12:44–13:03 |
| Landing and cleaning/screening | 2–3 | 12:45–13:03 |
| Exploring and answering: Q4 rule breakdown, Q1 volume | 3 | 12:55–13:03 |
| Q1 holiday sensitivity, Q2 airports | 4 | 13:05–13:17 |
| Geography coverage, Q3 tipping | 5 | 13:18–13:31 |
| Curb-only tipping, card share, Q5 zones | 6 | 13:33–13:49 |
| Flushing sanity check, status (`awb-status`) | 7 | 13:51–14:00 |
| Packaging: storyline and methodology checkpoint | 8 | 14:02–14:11 |
| Packaging: full deck build | 9 | 14:14–14:35 |
| Review corrections | 10 | 14:37–14:46 |
| Release 001 | 11 | 14:48–14:53 |
| Human DONE, feedback | 12 | 14:55–14:57 |

## Pain points observed as referee

| # | Observation | Turn | Severity |
|---|---|---|---|
| 1 | **Release 001 still identifies itself as a draft.** Every released slide header reads "BOARD REVIEW DRAFT". The released methodology note says "Board review draft" and "This is a working draft, not a numbered release." The released README is titled "board review draft" and says the files "are working copies, not a numbered release; the next revision overwrites them." Release copied the draft byte-for-byte without updating its status labels. Neither the agent's release checks nor the human caught it. A board member opening the shared-drive copy would see a draft. | 11 | Major |
| 2 | The agent linked the user to its own `awb-package/SKILL.md` (under the agent home `.agents/skills/`) to justify the package checkpoints. The human declined to open it. That is a user-facing isolation leak of agent internals, and it adds friction. | 8 | Major |
| 3 | Tooling chatter reached the user: Git creation blocked, "MCP reads work; writes require the CLI fallback", Git repeated in the status summary, "provenance gaps … two geography-validation metadata entries" at release. The user had to spend a turn asking whether to fix something. Per the agent, the MCP write tools were unusable under the approval policy, and `awb.py eda-scan`/`clean-scan` named in AGENTS.md do not exist in the installed CLI. | 1, 2, 7, 11 | Major (product) / minor (user impact) |
| 4 | Turn 1 announced "1 needs your context" without asking the question, which cost a turn. The scoping interview the README promises was one indirect question. It worked here only because the user's first message was detailed. | 1 | Minor |
| 5 | The weekday comparison went out without a calendar/holiday check. The user caught it, and setting holidays aside flipped Thursday from −3.9% to +9.1%. Turn 3 also contained "Correction to my earlier note" about something the user never saw, an intermediate Codex commentary leak. | 3–4 | Minor (trust) |
| 6 | The first full deck passed the agent's "independent review and final package checks" but needed 5 human corrections. Per-value asterisks on every number were mandated by the shipped `deck-rules.md`. $ signs were dropped by Matplotlib math parsing. There was an off-topic tipping bullet on the airport slide, an unlabeled holiday-adjusted chart, and Maspeth vs Elmhurst/Maspeth ambiguity. | 9–10 | Minor–Major |
| 7 | The package checkpoint (headline approval plus a "datasets" choice) was presented without explaining the options or giving a recommendation. | 8 | Minor |
| 8 | Packaging was the slowest phase: turn 9 took 21 min. The agent says it wrote its own PDF/PPTX renderer and extended the exporter with row selection, because the shipped package path targets an outline plus M365 handoff. The README likewise led the user to expect building the deck in M365. | 8–10 | Major (product) |
| 9 | Release folder clutter: 25 files, about 20 of them audit JSON, five folders deep on the shared drive. | 11 | Minor |
| 10 | Myle (third vendor) and the exclusion of Outside-NYC pickups from Q5 first appeared in deliverables, not in chat. | 9 / 6–7 | Minor |
| 11 | The agent used inconsistent link styles (relative vs absolute paths). | 3–11 | Minor |

### Isolation check

- **Codex agent:** I searched `relay/agent-*.log` for `workbench-spec`, `workbench-design`, `CONTEXT.md`, `docs/` paths and `/Users/` paths outside SIMDIR.
  - The `CONTEXT.md` hits are only the shipped AGENTS.md text being read ("never in `CONTEXT.md` or ADRs"), not reads of a CONTEXT.md file.
  - No `docs/` paths turned up.
  - The `/Users/` hits are interpreter discovery during turn 1 (`~/.pyenv/shims/python3`, `python3.12`, `~/.local/bin/python3.12`), which is benign and not documentation.
  - Every `sims/` path reference is `sims/taxi-A`, with none to sibling simulations.
  - No breach.
- **Opus human:** stayed in bounds. It read the README, the BRIEF, the files the agent pointed to (storyline, methodology note, deck PDFs, the Flushing summary md), and the releases folder. It explicitly declined the SKILL.md link. Its "JFK (~$100)" reference in msg 7 came from an exploration summary the agent had linked in turn 6. No breach.

## Most important issues for maintainers (ranked)

1. **The release does not restamp draft status.** Released artifacts (deck header, methodology note, README) keep "draft / not a numbered release / will be overwritten" wording. awb-release should rewrite status labels, or the package templates should take status from release metadata, and release checks should fail on draft markers.
2. **The packaging path does not match the deliverable users expect.** The shipped flow produces an outline plus M365 handoff, so the agent had to write its own PPTX/PDF renderer and add row selection to `src/packaging/draft.py`. The shipped `deck-rules.md` per-value asterisk rule cluttered every chart. Review checks pass slides a human would not show. The fix is to ship a deck renderer with visual checks and to set the README's expectations to match.
3. **MCP/CLI routing is broken in practice.** MCP writes were blocked by the approval policy, and `awb.py eda-scan`/`clean-scan` named in AGENTS.md are missing even though the installer `--check` passes. That status chatter reached the user. The fix is a capability-aware fallback, tested command parity, and keeping infrastructure state out of user messages.
4. **Agent-to-user communication leaks internals.** The agent linked a SKILL.md, used tool jargon ("CLI fallback", "provenance gaps"), announced a pending question without asking it, and presented checkpoint choices with no recommendation.
5. **The scoping interview and analytical defaults are thin.** There was no real scoping interview, and weekday comparisons had no default calendar/holiday check. The analysis itself was accurate, and every spot-checked figure matched exactly.
