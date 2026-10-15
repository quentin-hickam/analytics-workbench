# Orchestrator report: taxi-B

## Run facts

- **Variant:** B. Codex played the human (Dana Ortiz, persona from `human/BRIEF.md`; session `01a13f93-11e4-7030-aff3-a5923ba1510d`). Opus played the agent (nested subagent `taxi-B-agent`, id `a29731a90740ece54`).
- **Start:** 2026-10-15T12:39:25Z. **Conversation end (human `STATUS: DONE`):** 14:06:29Z. **Feedback complete:** 14:07:48Z.
- **Wall-clock:** about 1 h 27 min for the conversation, 1 h 28 min including feedback. Well inside the 8-hour cap.
- **Turns:** 9 human messages (plus 1 feedback turn), 8 agent replies (plus 1 feedback turn). Well inside the 45-message cap.
- **Protocol incidents:** none. Neither role needed a harness note. No loops, stalls, failed Codex turns, or nested-messaging failures. The fallback was not used.
- **Relay fidelity:** every human message reached the agent verbatim with the STATUS line stripped. I checked this mechanically against the subagent transcript (`relay/checkin.py`: all of `to-agent-001..008` matched). Agent replies were taken verbatim from the agent's SubagentHandback calls (`relay/extract.py`) and logged with `simctl.py log`.
- **Harness texts:** I used the fixed texts. One exception: the agent's feedback request ended with one added sentence asking it to state whether it had read anything outside its bounds. This is the isolation question the playbook asks for in Variant B.

## End-point checklist

| Criterion | Met? | Evidence |
|---|---|---|
| All five questions answered with specific figures the human accepted (or a reasoned limitation) | Met | Human turn 5 ("I accept the five answers with the documented limitations") and turn 9. Borough tipping was accepted as a reasoned partial limitation: Manhattan/Queens shown, Brooklyn caveated, Bronx/Staten Island/EWR not reportable. `project/investigations/airport-trips-and-tipping/questions.md`: Q-001..Q-005 `answered`, each linked to evidence. `findings.json`: 18 findings, all `supported`. |
| Human asked where things stand at least once | Met | Human turn 4: "Use awb-status — where are we…". Agent reply 4 has a "Where we are" section. |
| Deck package draft exists, was reviewed, released as 001 and copied to the releases folder | Met | Draft: `project/deliveries/airport-trips-and-tipping/board-briefing/draft/`. The human read `findings.md` and `methodology.md` (human log turn 7) and `board-methodology-note.md` (turn 8), then asked for three corrections, all of which were applied. Release: `project/deliveries/.../released/001/` and `storage/releases/airport-trips-and-tipping/board-briefing/released/001/` (12 files). `diff -r` of the two showed them identical. The human listed the release folder in turn 9. |
| Landed originals kept in `storage/landed/` | Met | `storage/landed/data/raw/tlc_yellow_trips/yellow-2024-01-07/` (both parquet files plus provenance.json) and `.../tlc_taxi_zones/zones-2024-10-15/`. |
| Project records committed | Met | 14 local commits (`git log` in `project/`). `deliveries/` is git-ignored by design. |

## The five questions

| # | Question | Agent's final answer (abridged) | Recorded? | My spot-check |
|---|---|---|---|---|
| 1 | Volume by day of week and hour, Jan vs Jul | July had 3.1% more valid trips (3,013,214 vs 2,922,610). Both months peak at 6 pm (6,769 and 6,794 trips/day) with the trough at 4 am. Busiest days: Jan Thu 105,735/day and Sat 103,743; Jul Wed 108,143 and Tue 105,542. More 9 pm trips in July (5,682 vs 5,115). | Yes: `results/volume-by-weekday-hour.csv`, `volume-by-hour.csv`, `volume-by-weekday.csv`, `monthly-volume.csv` | **Matches.** Per-day weekday averages for all 14 month×weekday cells matched exactly, as did the valid totals. |
| 2 | Airport share and fare/duration comparison | Any-airport share 9.8% (Jan) and 11.3% (Jul). Median metered fare $54.80/$57.60 vs $12.10/$12.80 for other trips. Median duration 31.8/35.2 min vs 10.8/11.7 min. Per-airport shares overlap slightly because of 3,444 and 5,187 between-airport trips. | Yes: `results/airport-comparison.csv`, `airport-overlap.csv` | **Matches exactly:** 9.80% / 11.33%, $54.80 / $57.60, $12.10 / $12.80, 31.8 / 35.2 min, 10.8 / 11.7 min. |
| 3 | Credit-card tip % by hour and borough | Median recorded tip 26.2% (Jan) and 25.6% (Jul) on 2,316,911 and 2,250,563 card trips; 23.5–28.0% by hour. Manhattan 26.6–26.7% / 26.2% and Queens 23.1% / 22.6–22.9% are "relatively stable" under a sensitivity test. Vendor 1 rate-code-99 card trips record essentially no tips (0 of 28,560; 1 of 41,853). Brooklyn is usable only with that group removed, and the Bronx, Staten Island and EWR have no reliable figure. Cash tips are about 0% recorded. | Yes: `results/tip-overall.csv`, `tip-by-hour.csv`, `tip-by-borough.csv`, `tip-by-borough-without-rc99.csv`, `rate-code-99-tips.csv`, `tip-manhattan-queens.csv` | **Matches:** overall median 26.25% / 25.63% on exactly 2,316,911 / 2,250,563 trips. Cash trips with a recorded tip: 0.029% / 0.043%. |
| 4 | Invalid share and vendor differences | 105,703 excluded (1.75%): 42,014 Jan (1.42%), 63,689 Jul (2.07%), under 7 approved rules. Vendor 1: 0.25% / 0.31%. Vendor 2: 1.79% / 2.61%. Vendor 6: 35% of its 260 Jan records. Zero-distance records reported separately (2.04% / 1.56%). Invalid or zero distance combined: 3.30% / 3.45%. Suspected reversal twins are flagged, kept, and covered by a sensitivity test. | Yes: `results/excluded-records.csv`, `invalid-by-vendor.csv`, `zero-distance-and-invalid.csv`, `suspected-reversal-pairs.csv`, `sensitivity-zero-distance-reversals.csv` | **Matches exactly:** 42,014 / 63,689 invalid. By vendor: 0.25 / 1.79 / 35.38 (Jan) and 0.31 / 2.61 (Jul). |
| 5 | Top 10 pickup zones by fare revenue per trip-hour | Ranked by month, minimum 1,000 trips, unknown and outside-NYC zones excluded. Jan: LIC/Hunters Point $121.03, JFK $102.39, LGA $93.99, East Elmhurst … Seaport $77.95. Jul: South Ozone Park $147.29, Queensbridge/Ravenswood $115.18, LIC $113.82 … East Williamsburg $84.01. Labelled as pickup-to-drop-off time only, so not driver earnings. | Yes: `results/top-zones-revenue-per-hour.csv`; release attachment `datasets/zone-rankings.csv` | **Matches exactly** for all 20 rows: zone, trip count and $/trip-hour. If zones 264/265 (N/A, Outside of NYC) are not excluded, "Outside of NYC" tops January at $418/h. The agent's exclusion of them is disclosed and sensible. |

The spot-check scripts are in `scratchpad/orch-taxiB/` (`spot.py`, `q1.py`). They are read-only DuckDB queries against the landed parquet files, run with the project venv's Python and written independently from the agent's rule descriptions. **I found no discrepancies.** (My own first pass misread the month because the landed folder is named `yellow-2024-01-07`, so a filename match on "2024-01" catches both files. That was my bug, not the agent's.)

## Isolation

- **Codex human:** in bounds. Its commands (`relay/human-*.log`) were limited to `cat BRIEF.md README.md`, appending to `notes.md`, reading `deliveries/.../draft/findings.md`, `methodology.md` and `board-methodology-note.md` (each pointed to by the agent), listing `storage/releases/...`, and writing `feedback.md`. It never opened AGENTS.md, src/, workbench-guides, skills, or the investigation's `state.md` (which the agent had pointed to).
- **Opus agent:** it states in `feedback/agent.md` ("Bounds") that it opened no file outside its permitted folders. It reports two directory-level slips:
  - `ls -la <scratch> | head` and `ls /private/tmp | grep -i claude`, run while looking for an enclosing git repo on turn 1.
  - Existence-only `test -e` checks for CLAUDE.md in every ancestor directory up to `/`, which awb-init step 1.3 instructs.

  Both are minor. The second comes from the skill itself: in a sandbox, "check every ancestor" walks outside the project. It also spawned read-only reviewer subagents scoped to the project. I saw no evidence that it read workbench design documents.

## Timeline

| Phase | Turns (human → agent reply) | Notes |
|---|---|---|
| Init | H1 → A1 (4.8 min) | awb-init set up the project, venv, helpers and git, and seeded the investigation with 16 ledger questions. It asked the user to run `pip install duckdb pandas` and offered MCP config in `~/.codex/config.toml`. |
| Scoping | A1, H2 | Four definitional decisions with recommendations, plus storage and board thresholds. All resolved in H2. |
| Landing, preparation, first look | H2 → A2 (10.7 min) | Landed to storage with verification, published views, profiled. Cash tips about 0%. Proposed six invalidity rules with counts, found the reversal twins, and asked four more decisions. |
| Cleaning decisions | H3 | User approved the rules plus fares over $500. Zero distance and twins kept, flagged, with sensitivity tests. |
| Answering | H3 → A3 (9.2 min) | All five results plus a findings draft. Found the vendor-1/RC-99 no-tip group. |
| Follow-ups and status | H4 → A4 (8.3 min) | Borough sensitivity test, full top-10 tables, zero-distance union, airport overlap, awb-status. |
| Findings acceptance and package start | H5 → A5 (7.7 min) | Findings marked supported. awb-package stopped at a mandatory headline-approval gate, proposed 11 slides, and asked three decisions. |
| Package draft | H6 → A6 (18.3 min) | 8 slides. Refused two explicit user requests on format grounds (merge title and answer; airports before volumes). Independent review took 6 rounds. |
| Package revision | H7 → A7 (17.8 min) | Separate plain-language one-page note, plus the 3.1% statement, which needed a new recorded result. 2 more review rounds. |
| Release | H8 → A8 (7.3 min) | Wording fix, then awb-release 001, copied and verified. Human confirmed in H9 (DONE). |

## Pain points observed as referee

1. **Package format overrode explicit user editorial instructions (A5, A6). Major.** The user asked for about 8 slides, title merged with the answer, and airports before volumes. The agent first proposed 11 slides as format-required. It then delivered 8, but still refused to merge title and answer ("format only allows title and subtitle on the title page") and to reorder, because slide order derives from ledger priority, so airports-first would mean demoting the volume question. The user objected in H6 ("Moving airports earlier doesn't make the volume question less important") and conceded in H7 "to keep this moving". The agent's own feedback reports that the outline check does not actually require several of the slides it first called mandatory.
2. **The requested one-page methodology handout had no slot in the package format (A6 → H7). Major.** The user asked for a one-page, non-technical methodology note on turn 1. The format produced only `methodology.md`, an internal technical reference of about 2,400 words. This cost a revision round of about 18 minutes. The added `board-methodology-note.md` falls outside the automated number and review-rule checks, so only the LLM reviewer protects it.
3. **Package review loop cost (A6, A7). Major (time).** The two package turns took 36 of the 87 minutes: 8 reviewer rounds across two revisions, plus evidence reruns because editing `run.py` invalidated every result's export (agent feedback item 3). The reviews did catch real overstatements ("never" vs "almost never", "demand" vs "trips"), but the user found reports of the round counts unhelpful.
4. **Too many approval gates for routine work (A1, A2, A3, A5). Major in the human's ranking.** These included asking the user to run `pip install` themselves (awb-init step 3.3), asking before each local commit, asking whether to investigate an anomaly the agent had found itself, and the headline-approval gate after the user had asked for the full draft. The human ranked this its #3 pain point.
5. **First-pass claims ran ahead of the evidence (A2, A3). Minor to major.** These were "cash tips: you were right that they're missing", the twins framed as voided trips, payment type 1 described as inferred from records (it was the user's recollection), and Manhattan/Queens called "reliable". The human corrected each one, and all were fixed. The workbench's caution discipline engaged only at the package-review stage.
6. **Jargon and internal mechanics leaked into chat (A4, A5). Minor.** These included "each finding carries a technical note about a validation step that doesn't fit this kind of result" (a `joins` check always "not assessed" for aggregate results, which the user then had to ask about) and talk of ledger priority, supported findings and review rounds. One question-count footer contradicted the body (A4: "answered 6" against "18 answered").
7. **Deliverable expectations: no PowerPoint (A6, A8). Minor.** The release is an assembly kit for M365 Copilot (`assembly/m365.md`). The README disclosed this, but the human still noted it as a gap in its feedback.
8. **awb-init's ancestor CLAUDE.md walk crosses the sandbox boundary (A1). Minor.** This is an isolation side effect of the skill's instructions.

No errors reached the user, and no unsupported numbers appeared: every figure I checked matched the source data.

## Most important issues for the workbench maintainers, ranked

1. **Separate presentation order and slide count from the question ledger and the fixed template.** Let users reorder slides, merge the title and Answer slides, and drop optional sections without editing ledger priorities. Document which sections are actually mandatory (see `awb-package` `findings-template.md` and `package-contract.md`).
2. **Add a first-class audience-facing one-page methodology note to the package contract.** Cover it in `check-draft` numbers/names and in `review-rules check`, and produce it whenever the brief asks for a handout.
3. **Cut package-turn cost.**
   - Make export freshness per result, so adding one producer to `run.py` doesn't invalidate every other result.
   - Allow row filters in chart specs, so a chart subset doesn't need a new result.
   - Let honest derived figures (cross-month totals, percent changes) be checked without a new recorded result each time.
   - Warn at `state finding` time when finding text has numbers that don't trace to a result.
4. **Reduce routine approval gates.** Let the agent install declared requirements into the project venv when the user asks to be guided, treat routine local commits as pre-approved once the user says so, and skip the headline-approval stop when the user has asked for a full draft.
5. **Make the `joins` validation not-applicable for aggregate results.** It currently attaches a boilerplate caveat to every finding, and that caveat surfaces in status and worries users.
6. **Bound awb-init's ancestor CLAUDE.md check** to the project's git root or the user's home directory.
