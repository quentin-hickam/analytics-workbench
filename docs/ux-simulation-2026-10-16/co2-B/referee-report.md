# Referee report: co2-B (variant B)

- **Run:** co2-B, dataset OWID CO2, variant B: Codex (`codex exec`) plays the user (Sam Whitfield, research lead); Claude Opus (headless `claude -p`, real skill discovery) plays the agent.
- **Relay:** found with no state file (status `DEAD`, `{}`), so this was a fresh sandbox; started by the referee (pid 2760). Ran to `FINISHED`, outcome `DONE`. No crash, no restart.
- **Times (UTC):** started 2026-10-16T19:16:55Z; conversation ended 21:39:47Z; relay finished 21:41:12Z.
- **Wall-clock:** 142.9 min of conversation, 144.3 min in total including feedback collection.
- **Messages:** 9 user messages written. 8 were delivered as requests and each got an agent reply. The 9th was the closing `STATUS: DONE` message, which is never relayed. That makes 8 agent replies, plus 1 feedback turn (9 agent sessions). Caps: 45 messages / 8 h, never close.
- **Cost:** agent $48.38. Of that, $44.12 (91%) went to the packaging and review turns A4–A8.
- **User satisfaction:** **7/10** (`feedback/human.md`).

## End-point checklist (`human/BRIEF.md`)

| # | Criterion | Met | Evidence |
|---|---|---|---|
| 1 | All five questions answered and accepted | Yes | U4 "I accept the five answers". Q4 re-accepted in U7 as "shares of recorded emissions" after the missing-years correction. Ledger `project/investigations/co2-cuts-growth-consumption/questions.md`: Q-001–Q-006 all `answered`, each linked to evidence JSON. |
| 2 | Asked where things stand at least once | Yes | U3 "Use awb-status — where are we?". In A3 the agent invoked the `awb-status` skill and the MCP `read status` (`relay/agent-003.jsonl`). |
| 3a | Package draft exists and the user reviewed it | Yes | Draft at `project/deliveries/co2-cuts-growth-consumption/donor-briefing/draft/`. User opened `findings.md`, `methodology-note.md` and `START-HERE.md` in turn 5 (`relay/human-005.jsonl`) and asked for corrections in U5, U6 and U7. |
| 3b | Released as 001 | Yes | `project/deliveries/.../donor-briefing/released/001/`. `manifest.json` has `status: release`, `release_number: "001"`, `prior_release: none` and `released_at 2026-10-16T17:39:15-04:00`. |
| 3c | Copied to `storage/releases/` | Yes | `storage/releases/co2-cuts-growth-consumption/donor-briefing/001/` (16 files). `diff -r` against the frozen release: identical. |

**End point met.** One provenance gap: the project repository has no commits (`git log`: "does not have any commits yet"). The manifest therefore records `producing_commit: "uncommitted"` and identifies inputs by sha256 only.

## The five questions

The referee checked the answers with independent DuckDB queries on `storage/landed/data/raw/owid-co2/2026-10-16/owid-co2-data.csv`, with "countries" defined as `iso_code IS NOT NULL OR country='Kosovo'` (218 coded entities + Kosovo = 219). The scripts are in `referee/spotcheck*.py`. Every value checked matched exactly.

| Q | Agent's final answer | Recorded result | Referee spot-check |
|---|---|---|---|
| 1 | 2000→2024, 216 countries compared. **Increases:** China +8,645.2 Mt, India +2,206.4, Indonesia +531.2, Iran +425.4, Saudi Arabia +382.5, Vietnam +317.0, Russia +299.9, Turkey +280.1, Malaysia +167.3, Iraq +149.9. **Decreases:** US −1,119.0, Germany −326.7, Japan −298.3, UK −256.1, Italy −167.7, France −143.3, Ukraine −143.2, Spain −88.9, Netherlands −57.4, Czechia −51.6. | Yes: `results/q1-change-since-2000.csv`, evidence JSON | **Match.** All 20 countries, values and order identical; 216 countries with data in both years. |
| 2 | 2005→2022 (GDP ends 2022). 45 of 164 countries cut CO2 while growing real GDP; 38 of them above 10 Mt in 2022. Largest: US (5,055.4 Mt; −17.5% CO2; +32.8% GDP), Japan, Germany, Canada, Mexico, Australia, Italy, Poland, UK, France. Added check (Q-006): 27 of the 39 with consumption data also cut consumption-based CO2; 12 did not; 6 have no data. | Yes: `q2-decoupling-counts.csv`, `q2-decouplers.csv`, `q6-consumption-counts.csv` | **Match.** 164 / 45 / 38. Q-006: 45 / 39 / 27 / 12 / 6. Max GDP year is 2022. |
| 3 | 2023 (latest consumption year). Per person, territorial vs consumption: US 14.32 vs 15.81 t (+10.4%); EU-27 5.51 vs 7.33 (+32.9%); China 8.56 vs 7.63 (−10.8%); India 2.13 vs 1.77 (−17.0%). | Yes: `q3-consumption-vs-territorial.csv` | **Match.** All eight values. Country consumption data ends 2023; only World and the international aviation and shipping rows have 2024 values. |
| 4 | 1850–2024, as shares of **recorded** global CO2 (World, including international aviation and shipping): US 23.6%, EU-27 16.3%, China 15.5%, India 3.6%. China has no figures for 1850–1906 and India none for 1850–1857 and 1867–1877. Those years are unknown, not zero. | Yes: `q4-cumulative-shares.csv`, `q4-missing-years.csv` | **Match.** Shares identical. Missing years confirmed: China 57, India 19, US/EU-27 0. |
| 5 | 2010→2024, 59 countries ≥50 Mt in 2010 with coal data (Libya excluded). Largest percentage-point drops: Greece 42.4→9.0% (−33.3), Romania −23.1, Israel −22.0, Poland −19.5, US −19.4, Finland −19.3, Czechia −18.0, UK −17.6. | Yes: `q5-coal-share-drop.csv` | **Match.** Top 8 and the 59-country count identical. |

The referee also confirmed several coverage claims the agent made in chat: no aggregate carries an `OWID_`-style code in this release; 120 countries have consumption data for 2023; 55 countries have no GDP at all. One small misstatement: in A2 the agent wrote "219 entities with a code, plus Kosovo". The correct count is 218 with a code plus Kosovo, 219 in total. A3 gives it correctly.

## Timeline

| Phase | Messages | Time (UTC) | Notes |
|---|---|---|---|
| Init | U1 → A1 | 19:17–19:18 (1.3 min) | `awb-init`: git init, venv, helpers installed through the CLI rather than the MCP `setup` tool. One permission prompt, auto-approved (19:20:48, during A2). |
| Scoping | A1 → U2 | 19:18–19:19 | `awb-scope` round 1: four bundled decisions, each with a recommendation. U2 accepted all four. The persona front-loaded most facts in U1, so this was the only scoping round. |
| Landing, cleaning, exploring, answering | U2 → A2 | 19:19–19:26 (7.5 min) | Investigation recorded. OWID files landed with provenance and retained to `storage/landed/`, then published to parquet. `awb-clean` recorded one issue (countries vs aggregates; Kosovo). `awb-explore` coverage: co2 and coal to 2024, consumption to 2023, GDP to 2022. Nine results via `run.py`; all five answered, plus an added Q-006. |
| Status | U3 → A3 | 19:26–19:28 (1.9 min) | `awb-status`. Full Q1 and Q2 tables, Q-006 counts recorded, aggregate filter verified, headline preview (`awb-package`). |
| Packaging | U4 → A4 | 19:28–19:45 (16.7 min) | User accepted the answers and the headlines. Full draft built, with 5 review-subagent rounds. |
| Review | U5 → A5, U6 → A6, U7 → A7 | 19:45–21:32 (105.9 min) | Three requested edits took 43.3 min and 14 reviews. The missing-years question and the tolerance move took 21.0 min and 5 reviews. Two wording fixes took 41.6 min and 12 reviews. |
| Release | U8 → A8 → U9 | 21:32–21:39 (6.9 min) | `awb-release`: 2 more reviews and one more edit to approved text, then frozen as 001, copied and verified. U9 `DONE`. |

The analysis itself (A1–A3) took 10.7 min. Packaging and review (A4–A8) took 129.5 min of the 142.9, and used 38 full-review subagent runs (5 + 14 + 5 + 12 + 2).

## Pain points observed by the referee

1. **The package review never settled (major, product).** It took 38 full-review subagent runs. Each "clean" pass was followed by a fresh pass that found new issues in text the user had already approved. A5 spent 43.3 min and $14.20 on three wording edits; A7 spent 41.6 min and $14.50 on two. The user's progress view was a stream of "Running another full review" interim messages (A5, A6, A7). Evidence: `relay/agent-004..008.jsonl`, `feedback/agent.md` §1.1, `feedback/human.md` §2.2.
2. **Approved text kept changing, against an explicit user request (major, product).** U7: "I'd like to avoid another round of unrelated wording changes." A7 still made six review-driven changes, and A8 made one more at release. The agent disclosed each one, but the skill gives no way to accept or waive a narrative finding with the user's consent (`feedback/agent-notes.md` turn 7).
3. **The historical-coverage problem surfaced late and was misdescribed (major, product).** Clean and explore (A2) never flagged that China and India lack early-year values that feed the 1850 cumulative shares. The gap first appeared in A5 as a caveat saying the missing years "count as zero", which the agent says the reviewer pushed it toward. The user challenged it in U6. A6 then asserted that OWID's World series also omits those years, an inference drawn only from reconciliation; the user challenged that too in U7. The workbench's review caught neither error. The numbers never changed (SUM ignores NULLs), but the interpretation shown to the user was wrong twice.
4. **Review rules made the deck worse (major, product).** The subtitle grew into a list of every comparison period (A6), and the Answer caveat accumulated many qualifications in one bullet (A5). A contract rule that "checked" sentences must state a tolerance led the agent to invent a 0.15 Mt tolerance after observing a 0.13 Mt maximum gap (A4). It also kept the tolerance in a visible bullet after U5 asked for it in the notes; U6 had to repeat the request.
5. **The first answers were incomplete in chat (minor, product).** A2 gave figures for only 3 of the 20 Q1 countries, listed Q2 countries without numbers, and said "most" for the consumption check. U3 spent a round asking for the tables and counts.
6. **Commit reminders came repeatedly (minor, product).** The agent mentioned uncommitted state in A1, A2, A3, A4 and A8, with explicit invitations in A2 and A4. The README, as the user read it, promises at most one reminder; the agent's feedback says it suggested once. The release went out from a repository with no commits.
7. **Helper defects the agent worked around (minor to major, product):**
   - `validate.py` raised `KeyError: 'left_rows'` on a partial `joins` spec;
   - `eda_scan.py` fails on an integer year column (`INTEGER -> DATE`);
   - `export` refused before a draft folder existed;
   - `display.toml` boolean keys silently failed to map;
   - `check-draft` false positives on a negated causal word and on a bare year (all A2/A4/A6, per `feedback/agent.md` §3).
8. **Protocol and isolation (minor, harness).**
   - The Codex user's first message began with a stray preamble line ("I'll read BRIEF.md and README.md, then follow the simulation's response format."), relayed verbatim. The agent ignored it.
   - The agent wrote scratch files outside SIMDIR: `/tmp/q.sql` in A2, and `/tmp/claude-501/review-diff.txt` in A4, which it then deleted.
   - A review subagent in A7 read two of Claude Code's own tool-result overflow files under the real `~/.claude/projects/...`.
   - None of these leaked study material.

## Isolation audit

**Agent logs** (`relay/agent-001..009.jsonl`, through `logview.py --full`):
- **No reads of** `workbench-spec`, `workbench-design`, `CONTEXT.md`, any `docs/` folder or analytics-workbench repository paths.
- **No reads of** `SIMDIR/human`, `SIMDIR/relay`, `transcript.md` or `REFEREE.md`.
- **MCP calls:** all were `records`/`read`, and none read files outside the project.
- **Web access:** the only fetches were OWID's public codebook and data URLs.

| Turn | Hit | Mattered? |
|---|---|---|
| A1 | `ls project/..` printed SIMDIR's top-level names (`human`, `relay`, `transcript.md`, `REFEREE.md`, `prompts`, `sim.json`). The agent was looking for `.claude` folders. | No. Names only; nothing opened. |
| A2 | Wrote `/tmp/q.sql` from a no-op shell loop. | No. A write outside bounds, self-reported. |
| A4 | Wrote, then deleted, `/tmp/claude-501/review-diff.txt`. | No. Self-reported. |
| A7 | Review subagent `Read` two files under `~/.claude/projects/-private-tmp-...-co2-B-project/<session>/tool-results/` (`btq6e9nhu.txt`, `bqj86m26a.txt`). | No. These are Claude Code's persisted copies of the session's own oversized tool outputs, under the real home because the agent CLI's own state lives there. Harness artefact. |

**User logs** (`relay/human-001..010.jsonl`):
- **Commands:** `cat BRIEF.md README.md` (human folder), then `cat` of `state.md`, which the agent pointed to in A2.
- **Package files:** `findings.md`, `methodology-note.md` and `START-HERE.md` in the draft.
- **Release check:** `ls` of both release folders, and `cat notes.md`.
- **No reads of** `AGENTS.md`, `SKILL.md`, `src/`, `.py` files, `workbench-guides/` or agent homes. Clean.

**Permission prompts** (`relay/permission-prompts.jsonl`): **1**. In A2 a `Bash` command copied a template from the skill folder and appended rows to `foundation/catalog.md` with a heredoc. A real user would have had to approve it. No denials, no MCP failures, no agent errors.

## Top issues for the workbench maintainers, ranked

1. **Make package review settle.**
   - Let a scoped re-review finish a bounded revision when the last full review was clean.
   - Require the reviewer to be exhaustive on its first pass against a stable checklist.
   - Let the user accept or waive narrative findings, so approved text stops changing.
   - Here it took 38 reviews, 129.5 of 142.9 minutes, and about 91% of the cost.
2. **Have the reviewer, and the explore/clean skills, check claims about how the source is built and what it covers, not only that each number traces to a recorded result.**
   - Missing-as-zero and "World omits those years" both passed review and were caught only by the user.
   - Coverage of every series that feeds a cumulative calculation should be checked before the first answer.
3. **Weigh readability against completeness in review rules.**
   - Attach each period to the claim it qualifies, rather than listing every period in subtitles and summary caveats.
   - Do not force a tolerance figure into slide text; this run invented 0.15 Mt after observing 0.13 Mt.
   - Let the user's own instruction override the rule on placement.
4. **Give a complete numeric table at first answer** for ranking questions, and counts instead of "most". This saves a round.
5. **Honour the README's once-per-session commit reminder**, and make the provenance cost of releasing uncommitted work clear in that one reminder.
6. **Fix the helper defects:**
   - `validate.py` `left_rows` KeyError;
   - `eda_scan.py` integer years;
   - `export` with a missing draft folder;
   - silent `display.toml` boolean keys;
   - a way to amend a `record_cleaning` observation;
   - a `package order` command.
