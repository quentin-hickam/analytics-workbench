# Referee report: retail-B (variant B)

Variant B: Codex (`codex exec`) played the user, Priya Natarajan (head of e-commerce, UK giftware wholesaler). Claude (Opus, headless `claude -p`, real skill discovery) played the agent with the awb skills and MCP server.

Paths below are relative to `SIMDIR` = `SIMS/retail-B`. Message references: U*n* = user message *n*, A*n* = agent reply *n* (in `transcript.md`).

## Run summary

| Item | Value |
|---|---|
| Relay start | 2026-10-16T19:16:56Z. `relay.py status` showed DEAD with an empty state (never started), so the referee started it fresh. |
| Conversation end | 2026-10-16T20:32:08Z, user STATUS: DONE |
| Relay finished | 2026-10-16T20:34:15Z, after feedback from both roles |
| Wall-clock | 75.2 min of conversation; 77.3 min in total |
| User messages | 8 sent. 7 were delivered and answered; U8 is the DONE message, which is never relayed. |
| Agent replies | 7 conversation replies. `agent_turns` = 8, counting the feedback turn. |
| Agent cost | $20.72. A5 alone cost $11.86 (57%). |
| Caps | Not reached: 8 of 45 messages, 1.3 of 8 hours |
| MCP failures | None (`feedback/harness-log.md`) |
| Permission prompts | 1, a compound Bash call in A1 that copied templates, filled the README storage lines and ran `uv venv` (`relay/permission-prompts.jsonl`) |
| User satisfaction | **8/10** (`feedback/human.md`) |

## End-point checklist (`human/BRIEF.md`, "The path to the end point")

| Criterion | Met | Evidence |
|---|---|---|
| 1. All five questions answered with specific answers the user accepts | Yes | A2 gave provisional answers. A3 added the full tables. U4 says "I accept the quantitative answers". U8 confirms. `project/investigations/marketing-budget-2012/questions.md` shows Q-001 to Q-005 (plus follow-ups Q-006 and Q-007) answered by recorded evidence. `state.md` lists all 8 findings as `supported`. |
| 2. Asked where things stand at least once | Yes | U3: "Use awb-status — where are we…". A3 ran the `awb-status` skill and MCP `read status` (`relay/agent-003.jsonl`). |
| 3a. Package draft exists | Yes | `project/deliveries/marketing-budget-2012/leadership-budget-pack/draft/` holds findings.md, methodology.md, methodology-note.md, 6 chart CSVs, 4 datasets, START-HERE.md and manifest.json |
| 3b. User reviewed it | Yes | In human turn 6 the user ran `cat` on draft/findings.md, methodology-note.md and START-HERE.md (`relay/human-006.jsonl`), then asked for two corrections in U6. A6 applied them. |
| 3c. Released as 001 | Yes | `released/001/manifest.json`: `status: release`, `release_number: 001`, `producing_commit` and `packaging_commit` both `c18e2e7`, `revalidation_flags: none`. Release commit `0f76848`. |
| 3d. Copied to `storage/releases/` | Yes | `storage/releases/marketing-budget-2012/leadership-budget-pack/001/` holds 17 files. The referee's `diff -r` against `project/.../released/001` is identical. |

**End point met.**

## The five questions

The referee recomputed the figures from the landed workbook (`storage/landed/.../online_retail_II.xlsx`) with independent pandas and DuckDB queries (`referee/load.py`, `referee/check1.py` to `referee/check4.py`). The load gave 1,067,371 rows across both sheets. The 1–9 Dec 2010 overlap is confirmed: 22,523 rows and £377,488.45 in each sheet, and an `EXCEPT ALL` comparison of the two copies returned 0 rows. The referee removed one copy. The referee's own trading classification was: goods plus POST, DOT and C2, minus AMAZONFEE, B, M, BANK CHARGES, D, CRUK, ADJUST*, S, TEST* and gift vouchers. The period was Dec 2009–Nov 2011.

| Q | Agent's final answer | Recorded? | Referee spot-check |
|---|---|---|---|
| 1. Monthly net revenue and seasonality | All 24 months given (A3 table). Year 1 £9,342,483.02, year 2 £9,608,007.01, up £265,523.99 (+2.84%). November peaks at £1.43m and £1.48m (index 183.1 and 184.9). Sep–Nov brought 36.03% and 37.51% of each year. Lows: Feb 2010 (index 68.9), Apr 2011 (61.7). | Yes: `evidence/monthly-net-revenue.json`, `evidence/annual-net-revenue.json`, supported | **Exact match** to the penny for all 24 months and both year totals. Two-year total £18,950,490.04. |
| 2. Top-10% share; revenue without customer ID | Top 10% of identified customers (585 accounts) brought in £10,231,538: 54.0% of all net revenue, 63.1% of identified-customer revenue. £2,747,685 (14.5%) has no customer ID. | Yes: `evidence/customer-concentration.json`, supported | **Exact match**: 5,850 identified customers, top 585 = £10,231,537.70, identified £16,202,804.89, no ID £2,747,685.15. |
| 3. 90-day repeat by 2010 first-purchase month | Jan 52.4% (193/368), Feb 47.7%, Mar 41.3%, Apr 38.1%, May 33.7%, Jun 34.5%, Jul 43.2%, Aug 49.7%, Sep 43.1%, Oct 38.4%, Nov 30.1%, Dec 15.8% (12/76). First purchase means first observed in the export. | Yes: `evidence/repeat-90d.json`, supported | **Exact match** for all 12 cohorts under the agent's recorded definition: a purchase is a non-cancellation invoice day with a positive-quantity goods line. Counting postage-only orders as purchases shifts repeat counts by 1–3 customers in several cohorts (for example Jan 194/368 = 52.7%). The headline range does not change. |
| 4. Highest cancellation rate by value (≥ £5,000 sales) | 872 products qualify. Medium Ceramic Top Storage Jar 95.1% (£77,480 of £81,448, 10 invoices), Pantry Chopping Board 82.7%, Small Fairy Cake Fridge Magnets 53.0%. Cherry lights: white 35.6% (124 invoices), light pink 31.9% (59), pink 29.2% (86). All-product average 2.86%. | Yes: `evidence/product-cancellation.json`, supported | **Match** on the top 7 products' sales, cancelled values, rates and invoice counts, and on the 2.86% average. The referee counts 873 qualifying products because it case-folded stock codes; this does not matter. |
| 5. Non-UK net revenue growth, year 1 to year 2 | Established markets: Australia +£107,718 (+366.9%), France +£69,836 (+58.0%), Germany +£22,400, Spain +£21,593, Belgium +£17,184. EIRE fell most (−£90,818, −26.1%). Small-base markets: Japan +£31,210, Norway +£26,137. New markets are tiny (largest £1,292). Follow-ups: Australia's largest growth contributor supplied 96.8% of its growth; France's top three supplied 32.9%; Germany's top three supplied 99.6%. | Yes: `evidence/country-growth.json`, plus `market-buyer-concentration.json` and `market-growth-concentration.json`, supported | **Exact match** on all listed pound and percent figures, including Denmark −£27,092, Sweden −£14,696, Finland +£13,278. The concentration follow-ups were not recomputed. |

All five answers rest on recorded results, and the referee's independent recomputation reproduces every headline figure.

## Timeline

| Phase | Messages | Time (UTC) | Notes |
|---|---|---|---|
| Init | U1 → A1 | 19:19–19:21 (1.5 min) | `awb-init` ran. Git repo created, records copied, project `.venv` (Python 3.12) created, MCP `setup` installed duckdb and pandas. Storage paths recorded in the README. |
| Scoping | A1, U2 | 19:21–19:23 | First `awb-scope` round: four definition decisions, each with a recommendation. The user agreed and changed two points: a single 24-month window throughout, and small or new markets shown separately. |
| Landing, cleaning, exploring, answering | U2 → A2 | 19:23–19:33 (10.0 min) | Download, `land` and retain, `publish` (1,067,371 rows, 17 checks). The agent found the cross-sheet overlap through its own date check and removed it. Clean scan and records. A line-type foundation view. Five results run through `run.py`, plus a buyer-concentration extra. Decision asked on about 12k exact repeated lines (about £55k). |
| Follow-ups and status | U3 → A3 | 19:34–19:36 (2.0 min) | Repeated lines kept. Full monthly and cohort tables. Cancellation counts clarified. Germany "spread growth" claim withdrawn after a new growth-concentration result. `awb-status` run. |
| Acceptance and headline preview | U4 → A4 | 19:37–19:39 (1.2 min) | Findings accepted with caveat edits. `awb-package` preview: 9 main slides plus 2 appendix slides, with a dataset choice. |
| Drafting | U5 → A5 | 19:40–20:21 (**40.4 min**, $11.86) | Export, findings.md, methodology files, then a review loop of 12 Plan-subagent reviewer runs. The loop found double-rounded 52.5% and 63.2% figures and fixed them. A third appendix slide was added for the supporting datasets. |
| Review and revision | U6 → A6 | 20:21–20:29 (7.5 min) | Thresholds removed from audience text. "Largest contributors to revenue growth" and "unidentified-orders group" wording adopted. Reconciliation and identified-contributor checks recorded. Commits `6fb0cc2`, `c18e2e7`, `c1e1393`. Two reviewer runs. |
| Release | U7 → A7 | 20:29–20:32 (2.5 min) | One full reviewer run, then MCP `release`: 001 frozen and copied, storage comparison clean, agent's own `diff -r` byte-identical. Commit `0f76848`. |
| Close | U8 | 20:32 | DONE |

## Pain points observed by the referee

| # | Observation | Messages | Severity |
|---|---|---|---|
| 1 | **The drafting turn took 40.4 minutes and cost 57% of the agent's spend.** It ran 12 reviewer subagents. Each full review found new, mostly legitimate, problems, and every small fix restarted the full review. Across the run there were 15 subagent runs: 12 in A5, 2 in A6, 1 in A7. The agent itself counts 14 review passes. | A5–A7; `relay/agent-005.jsonl`; `feedback/agent.md` §1.1 | major |
| 2 | **Interpretations went beyond the evidence in chat:** "probably Christmas-season buyers", "the real pattern is…", France and Germany growth "spread across many accounts" based on buyer counts (in fact three accounts supplied 99.6% of Germany's growth), and "January to March are overstated". The user caught each one. No check covers interpretive wording in chat. | A2, A3, U3, U4 | major |
| 3 | **Double rounding produced wrong displayed figures.** Results were stored at 4 decimal places and export rounded them again, giving 52.5% (true 52.4%) and 63.2% (true 63.1%) in the draft. `check-draft` accepted both. A reviewer subagent caught them before the user saw the draft. | A5; `feedback/agent.md` §1.2 | major |
| 4 | **The first draft's audience-facing methods text listed filter row-retention thresholds.** Plain-language checks ("totals reconcile", "overlap counts once") were not recorded results until the user asked for them, which forced producer changes and reruns after the findings had been accepted. | U6, A6 | major |
| 5 | **The cleaning scan cannot see the cross-sheet overlap** (22,523 lines, about £377k, double-counted) because the scan key includes the sheet. The agent found the overlap only through its own date-range check. | A2; `feedback/agent-notes.md` turn 2 | major (latent) |
| 6 | **The status report understated the caveats:** "none open… the one recorded caveat is the kept repeated lines". It left out missing IDs, the first-observed definition, cancellation timing and the December 2011 exclusion. | A3, U4 | minor |
| 7 | **The draft departed from the approved preview.** Rounded headlines became exact figures, the France/Australia headline was reworded to satisfy a review rule, and a third appendix slide appeared that the preview had not mentioned. The user had to ask for rounding again. | A5, U6 | minor |
| 8 | **Implementation narration and long replies.** Interim messages reported settings-file mistakes, shell word-splitting, repeated review passes and commit details. | A2, A5, A6 | minor (the user rated it major) |
| 9 | **The Q3 purchase definition was not shown to the user.** A purchase meant a positive-quantity goods line, so postage-only orders were excluded. The definition is recorded in the settings validation detail but not in the user-facing definition, and it moves counts by 1–3 customers per cohort. | A2/A3; `settings.toml` line 76; `methodology-note.md` | minor |
| 10 | **`check-draft` refused the user's own caveat wording** ("the effect on repeat rates is unknown", "causes cannot be inferred"). The agent paraphrased it but told the user the definition was "in your wording". | A5; `feedback/agent.md` §3 | minor |
| 11 | **The agent ran the CLI for `run`, `package`, `export` and `check-draft`, not the MCP tools.** AGENTS.md prefers the MCP tools. Nothing failed. | A2–A6; `feedback/agent.md` | minor |
| 12 | **Isolation: one scratch write outside SIMDIR.** The agent wrote `check.json` and `export.json` to `/tmp/claude-501` (the sandbox TMPDIR), then deleted them and moved scratch files to `agent-home/tmp`. | A5 | minor |

## Isolation audit

- **Agent logs** (`relay/agent-*.jsonl` read through `logview.py --full`, including the reviewer subagents' tool calls): no reads of `workbench-spec`, `workbench-design`, `CONTEXT.md`, a `docs/` folder, the analytics-workbench repository, `SIMDIR/human`, `SIMDIR/relay` or `transcript.md`. No tool input names a path under `/Users/`. The MCP `data` and `read` calls were `clean-scan` (twice), `status` and `stale`, all on the project. The search hits were benign:
  - Claude Code's own background-task output files under `<scratch>` (A2), whose path happens to contain "analytics-workbench".
  - The agent's own `feedback/agent-notes.md`.
  - The scratch writes to `/tmp/claude-501` in row 12 above. Outside SIMDIR, but writes only, and they did not affect results.
  - Skill files were read only from `agent-home/.claude/skills/`, which is the release.
- **User logs** (`relay/human-*.jsonl`):
  - Commands were `rg --files -g BRIEF.md -g README.md -g AGENTS.md` in its own `human/` folder, which lists file names and has no AGENTS.md; `cat BRIEF.md README.md`; and, in turn 6, `cat` of the three draft files the agent had pointed to.
  - There were no reads of AGENTS.md, SKILL.md, `src/`, `.py` files, `workbench-guides/` or agent homes.
  - The `AGENTS.md` glob did not matter.
- **Protocol:**
  - U1 began with the Codex role's own preamble, "I'll read BRIEF.md and README.md, then follow the simulation's response format." The relay passed both of turn 1's Codex messages. The agent noticed the line and ignored it.
  - A1 contained "Now the friction log.", an interim line caused by the harness's friction-log note. The user flagged it as unexplained.

## Most important issues for the maintainers, ranked

1. **The package review loop converges slowly.** A5 took 40 minutes and $11.86 with 12 reviewer subagent runs, and the run used 15 in all. Possible fixes: give reviewers a checklist of common problem types, allow a scoped re-review when the change since a clean full review is small, and add a self-check before drafting. (Rows 1 and 4.)
2. **Interpretive overreach in chat findings goes unchecked.** The AGENTS.md rule against untested explanations was broken twice before the user intervened. The finding-number and `check-draft` checks do not reach chat summaries. (Row 2.)
3. **Double rounding passes silently.** Shares rounded in result queries and again on display gave wrong figures, and `check-draft` accepted them. Possible fixes: guidance to keep full precision in results, and an export warning. (Row 3.)
4. **Audience-facing method text exposes internal validation thresholds.** Plain-language reconciliation and coverage checks are not set up as recorded results from the start, so adding them late forces reruns. (Row 4.)
5. **The cleaning scan is blind to overlapping extracts or sheets.** A £377k double count was possible, and a less careful agent would have kept it. (Row 5.)
6. **Updates are verbose and narrate implementation detail**, and the status report understates the caveats. (Rows 6 and 8.)
7. **The draft departs from the approved preview** (precision, rule-forced rewording, unannounced appendix slide) without asking first. (Row 7.)
8. **Small helper defects** (detailed in `findings.json`):
   - `validate.py` raises `KeyError: 'left_rows'`.
   - `run.py` producers cannot import sibling helpers.
   - `awb.py sql` takes no parameters and treats a missing path as SQL text.
   - `export` needs the draft folder to exist, although the package step order puts writing before export.
   - The chart-spec blank-line rule is ambiguous.
   - The project stays "uncommitted" until a rerun after the first commit.
