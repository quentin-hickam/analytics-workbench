# Orchestrator report: retail-B

## Run summary

- **Variant:** B. Codex played the human (Priya Natarajan, head of e-commerce, persona in `human/BRIEF.md`); Claude Opus played the agent (nested subagent `retail-B-agent`).
- **Dataset:** UCI Online Retail II (two-sheet Excel workbook, 1,067,371 rows).
- **Start:** 2026-10-15T12:39:20Z. **End of conversation:** 13:50:13Z (human `STATUS: DONE`). **End of feedback:** 13:51:31Z.
- **Wall-clock:** about 71 minutes for the conversation, 72 minutes including feedback. Caps were 45 human messages and 8 hours; neither was approached.
- **Turns:** 7 human messages in the conversation plus 1 feedback turn; 6 agent replies plus 1 feedback turn.
- **Fallback:** not used. Nested spawning and SendMessage worked throughout.
- **Protocol incidents:**
  - Turn 2: the agent sent a near-duplicate copy of its reply by SendMessage just before its official hand-back. I relayed only the hand-back. Harmless.
  - No harness notes were needed. Neither role looped or broke protocol.

## End-point checklist

| Criterion | Met? | Evidence |
|---|---|---|
| All five questions answered with specific figures and accepted by the user | Met | Human turn 5: "I accept the answers to all five questions on the agreed definitions." Ledger `project/investigations/marketing-budget-priorities/questions.md` shows Q-001 to Q-005 as `answered`, each linked to recorded evidence |
| User asked where things stand at least once (`awb-status`) | Met | Human turn 3 ("Use awb-status — where are we?"); agent turn 3 opens with a "Where we are" section |
| Deck package drafted and reviewed by the user | Met | `project/deliveries/marketing-budget-priorities/leadership-budget/draft/`. The user read `findings.md`, `methodology.md`, the dataset CSVs and the chart CSVs (human log commands), then requested two rounds of corrections (turns 5 and 6) |
| Released as 001 and copied to the releases folder | Met | `storage/releases/marketing-budget-priorities/leadership-budget/released/001/`. `diff -r` against `project/deliveries/.../released/001` reports the two copies identical; commit `cf2c4e7 Record release 001 in state` |
| Landed data kept in the requested folder | Met | `storage/landed/data/raw/online_retail_ii/2026-10-15/` holds the zip, the xlsx and `provenance.json` |
| Data checked and cleaned | Met, without the user asking | `project/foundation/quality.md` records DQ-001 to DQ-006: sheet overlap corrected, description whitespace corrected, duplicates kept by user decision, and others |

## The five questions

All figures are net merchandise revenue, GBP as recorded. Year 1 is Dec 2009–Nov 2010; year 2 is Dec 2010–Nov 2011. For my spot-check I loaded the landed xlsx with pandas into my own scratch folder, wrote my own code for the agreed definitions, and dropped the sheet overlap myself.

| # | Agent's final answer | Recorded? | My spot-check |
|---|---|---|---|
| 1 | £9.19m in year 1, £9.35m in year 2 (+1.8%). Sep–Nov carries 36.1% and 37.5% of each year. Cancellations are 2.56% and 3.15% of gross sales. April 2011 is the lowest of the 24 months. All 24 months are in `datasets/monthly-revenue.csv` | Yes: `monthly-net-revenue`, `yearly-summary` | **Exact match:** 9,188,552.63 and 9,351,342.37; Sep–Nov 0.3610 and 0.3752; cancellation share 0.0256 and 0.0315; lowest month 2011-04, highest 2011-11 |
| 2 | Top 10% of identified customers (585 of 5,848, each with at least £5,168) produced £10.16m: 54.8% of total and 63.2% of identified-customer revenue. No-ID revenue was £2.47m (13.3%) | Yes: `customer-concentration` | **Exact match:** 585 of 5,848; £10,160,951; 0.5481 and 0.6322; no-ID £2,467,119 (0.1331); threshold £5,168 |
| 3 | 1,362 of 3,364 first observed customers in 2010 (40.5%) bought again on a later day within 90 days. Cohorts range from 52% (Jan) to 30% (Nov); the Dec cohort is 16% on 76 customers | Yes: `repeat-90-days`, `repeat-90-days-total` | **Exact match:** 3,364 / 1,362 / 0.4049; Jan 0.524, Nov 0.301, Dec 0.158 on n=76 |
| 4 | Among 872 products with at least £5k gross sales, the top rates are Medium Ceramic Top Storage Jar 95.1% (£77.5k of £81.4k, 10 cancellation invoices), Pantry Chopping Board 82.7%, Small Fairy Cake Fridge Magnets 53.0%, then the cherry lights at 35.6%, 31.9% and 29.2% | Yes: `product-cancellation-rates`, `cancellation-leaders` | **Jar matches exactly:** gross £81,448.21, cancelled £77,479.64, 0.9513 |
| 5 | Overseas grew from £1.27m to £1.45m (+14%). Largest gains: Australia +£108k, France +£64k, Japan +£31k, Norway +£23k, Germany +£20k, Spain +£18k, Belgium +£15k. Largest falls: EIRE −£91k, Denmark −£27k, Sweden −£14k | Yes: `overseas-growth`, `overseas-top-gains` | **Exact match:** totals £1,269,190 and £1,448,938, and all seven gains and three falls to the pound |

The checks found no discrepancies. The agent's non-merchandise list is reasonable. It leaves a few trivial codes in merchandise (PADS, DCGS*, GIFT, C3, SP1002), each worth tens to hundreds of pounds or nothing, so they do not affect any answer.

There is one presentation gap. Australia qualifies for a percentage under the agreed rule (first-year revenue £29.4k, above the £10k minimum), and its growth is +367%. The dataset CSV carries it (3.6659), but the agent showed "—" for Australia in its turn-2 chat table, and the deck text never gives the figure. The answer is correct, but the most striking percentage is missing from what leadership will see.

## Timeline

| Phase | Turn(s) | Notes |
|---|---|---|
| Init, landing, first scoping | H1 → A1 (~6.5 min) | awb-init and awb-scope; download, retention and sheet-overlap detection on turn 1. The agent asked about four definitions now and deferred two to a later round |
| Scoping completed, cleaning, analysis | H2 → A2 (~9.5 min) | The user settled all six definitions at once. The agent ran the cleaning scans (DQ-002 to DQ-006), built a canonical sales view, and computed all five answers with commercial reads |
| Status, evidence tightening, headline checkpoint | H3 → A3 (~9 min) | awb-status. The agent turned its quick-query figures into recorded results, then stopped for headline approval even though the user had asked for the draft |
| Package draft | H4 → A4 (~27 min) | The longest phase. The internal read-only review took 8 rounds to come back clean |
| Revisions | H5 → A5 (~9 min) | Added a named-product table, a top-7 overseas chart and the full reconciliation table |
| Percentage fix and release | H6 → A6 (~7 min) | Fixed the rate display, then awb-release 001 with a verified copy to storage |
| Done | H7 | `STATUS: DONE` |

## Referee observations: pain points

1. **Slow package phase (major, A4).** The first draft took about 27 minutes, 38% of the conversation, because the internal review needed 8 rounds. Across the session there were 11 reviewer subagents. The agent reported these rounds to the user, who found them noise (human feedback §6).
2. **Approval gates the user did not want (major, A2, A3).**
   - A2 asked "shall I draft the deck now?" although the user had asked for slides in H1.
   - A3 stopped for headline approval although H3 said "use awb-package to draft".
   - Together they cost about one full exchange.
   - A1's split of the interview into two rounds (four decisions now, two next round) was undone only because the user volunteered the rest.
3. **Presentation elements missing from the first draft (major, A4 → H5).**
   - The first draft had no overseas chart, and product names were absent from the visible cancellation slide.
   - The reconciliation was a paragraph rather than a closing table.
   - Cancellation rates appeared as fractions (0.9513), which the user caught in H6.
   - The agent's feedback traces all of this to the chart model, where a chart serializes a whole result table and display formatting is lacking. Every slide tweak therefore became a new recorded result.
4. **Interpretation ahead of evidence in the first findings (major, A2).** These included an untested Easter explanation for April, cancellations called "product problems", growth "across a widening customer base" without counts, and quick-query figures mixed with checked results. The user had to request the tightening in H3, and it was then done well.
5. **Technical noise to a business user (minor, A1).** Python environment, Git, helper scripts, MCP server registration and a config.toml snippet appeared in the first reply. The user flagged it in H2 notes.
6. **"Nothing outstanding" alongside an open VAT question (minor, A6).** The release message said there were no unresolved caveats, then noted that VAT is still open. The user found this contradictory.
7. **Australia's percentage omitted in conversation and deck (minor, A2 and later).** See above.
8. **`findings.json` notes split inside parentheses (minor, my own observation).** Caveat strings are broken at commas inside parentheses. For example, `"repeated identical invoice lines kept as possibly legitimate entries (DQ-003"` and `"removing them would lower ... 0.3%)"` are stored as two notes. This looks like a comma split in the caveat input.
9. **Interpreter and environment friction (minor, agent-side).**
   - The docs say `python3 src/awb.py`, which fails without duckdb.
   - The printed install command uses pip inside a uv venv, which has none.
   - The agent installed packages itself, deviating from awb-init's "the user runs the printed install".
10. **Editing `run.py` makes every result stale (major for agent time, A3–A5).** The agent reran and re-promoted all results three times.

## Isolation

- **Agent (Opus):**
  - The agent self-reports reading nothing outside its bounds. It disclosed writing a scratch script briefly to `sims/retail-B/` and `sims/retail-B/scratch/`, moved at once into agent-home, and running existence tests (no reads) for host instruction files in `sims/retail-B/` per awb-init step 1.3.
  - I scanned its tool calls and those of its 12 reviewer subagents for `workbench-spec`, `workbench-design`, `CONTEXT.md`, the repository's `docs/`, `retail-B/human`, `retail-B/relay`, and paths outside SIMDIR. None of them hit.
- **Human (Codex):**
  - The logs show it ran only `cat BRIEF.md README.md`, wrote `notes.md` and `feedback.md`, and read files under `project/deliveries/.../draft/`: `findings.md`, `methodology.md`, `monthly-revenue.csv`, `chart-4.csv` and `chart-5.csv`.
  - It did not read AGENTS.md, skills, src or workbench-guides. Those names appear in its logs only through the README text.
- **Verdict:** no breaches.

## Most important issues for the workbench maintainers, ranked

1. **Package review convergence (awb-package `references/review.md`).** Eight rounds for one draft and 11 in total made this the largest time sink. Ask the reviewer for one exhaustive pass, allow a scoped re-review of changed lines only, and give the writer a pre-review checklist built from the problems reviewers commonly find. Do not narrate review rounds to the user.
2. **Presentation changes cost analytical work.**
   - Allow `--chart` to take a row filter or limit over an existing result.
   - Add display formatting (percent, thousands separators) in `display.toml`.
   - Encourage the first draft to include a chart for every ranked finding and named items on the slide.

   Together these prevent missing charts and fraction displays in first drafts.
3. **Checkpoints after an explicit request.**
   - Skip the headline checkpoint, or make it optional, when the user explicitly asked for a full draft.
   - Don't re-ask permission for work already requested.
   - Let awb-scope bundle all definition decisions into one interview when the user is on a deadline (the current limit is four).
4. **Separate checked results from exploration, and observation from hypothesis, from the first findings reply.** Untested causal explanations and quick-query figures reached the user before tightening.
5. **Agent-side mechanics.**
   - Editing `run.py` should not make every result stale.
   - Record the project interpreter in AGENTS.md and README.
   - Print a uv-aware install command.
   - Add guidance for xlsx and zip sources.
   - Avoid the `Q-` prefix in quality-ID examples, where it collides with ledger IDs.
6. **User communication.**
   - Keep setup detail out of the first reply.
   - Word the release summary so that accepted open caveats such as VAT are not called "nothing outstanding".
   - State prominently, in the README and at package time, that the package is an outline plus data for PowerPoint assembly in M365 Copilot, not a rendered deck. The user rated this major for meeting preparation.

## Files

- Transcript: `transcript.md`
- Human feedback: `feedback/human.md` (copied from `human/feedback.md`); human notes in `human/notes.md`
- Agent feedback: `feedback/agent.md`; agent friction log in `feedback/agent-notes.md`
- Relay files: `relay/`
- Orchestrator spot-check scripts, outside SIMDIR: `scratchpad/orch-retailB-check/check2.py`
