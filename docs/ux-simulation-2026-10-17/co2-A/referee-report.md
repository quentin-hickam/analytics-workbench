# Referee report: co2-A

Run **co2-A**, variant **A**: Claude (Opus, headless) played the user (persona: a research lead at a climate-policy nonprofit); Codex (`codex exec`) played the agent with the awb skills and MCP server. Dataset: OWID CO2. SIMS = the sims scratchpad folder; all paths below are relative to it.

## Run summary

| Item | Value |
|---|---|
| Relay started | 2026-10-17T11:17:42Z |
| Conversation ended | 2026-10-17T11:56:57Z (DONE from the user) |
| Relay finished (after feedback) | 2026-10-17T11:58:44Z |
| Wall-clock | 39.2 min conversation, 41.0 min total |
| User messages | 9 (8 delivered and answered; message 9 was the DONE message, not relayed by design) |
| Agent turns | 9 (8 conversation replies plus 1 feedback turn) |
| Agent time across the 8 replies | 37.1 min (user wait per request 0.8 to 10.4 min) |
| Outcome | DONE, end point met |
| User satisfaction | **8/10** ("Yes, I'd use it again") |
| User cost (Claude) | about $0.82 |

Sources: `SIMS/co2-A/relay/state.json`, `SIMS/co2-A/transcript.md`, `SIMS/co2-A/feedback/harness-log.md`.

## End-point checklist

| Criterion (from `human/BRIEF.md`) | Met | Evidence |
|---|---|---|
| All five questions answered with specific answers the user accepts | Yes | Q1, Q3, Q5 accepted in message 4; Q2 (38-country headline, 45 in notes) and Q4 (with aviation/shipping caveat) accepted in message 5. Ledger `project/investigations/emissions-and-country-focus/questions.md`: Q-001 to Q-005 all `answered`, each linked to recorded evidence; Q-011 records the user's headline decision. All 11 findings in `findings.json` are `supported`. |
| Asked where things stand at least once | Yes | Message 5: "Use awb-status — where are we?"; reply 5 opens with the status report. |
| Package draft exists and was reviewed by the user | Yes | Headline preview reviewed in message 6 (four edits), full draft reviewed in message 7 (rounding and punctuation edits). The user log shows reads of `draft/.preview/headlines.md`, `draft/findings.md`, `draft/methodology-note.md`, `draft/START-HERE.md`, `draft/charts/chart-1.csv`. |
| Released as 001 | Yes | Reply 8; `project/deliveries/emissions-and-country-focus/donor-roundtable/released/001/` (12 files). |
| Copied to the releases folder | Yes | `storage/releases/emissions-and-country-focus/donor-roundtable/001/` is byte-identical to the local frozen release (`diff -r` clean). The landed CSV in `storage/landed/data/raw/owid-co2/2026-10-17-01/` has the same SHA-256 as the project's raw copy. |

The released deck carries all user edits: the slide 5 and 6 headlines as dictated, no trailing periods, the Q2 chart as CO2 % change next to GDP % change, a plain-words definition of "territorial", whole million tonnes in chart 1, one-decimal per-person figures and historical shares.

## The five questions

| # | Agent's final answer (year used) | Recorded result | Referee spot-check (own DuckDB query on the landed CSV, `referee/spotcheck.py`) |
|---|---|---|---|
| 1 | 2000 to 2024, 216 comparable countries. Increases: China +8,645.2 Mt, India +2,206.4, Indonesia +531.2, Iran, Saudi Arabia, Vietnam, Russia, Turkey, Malaysia, Iraq (+149.9). Decreases: US −1,119.0, Germany −326.7, Japan −298.3, UK, Italy, France, Ukraine, Spain, Netherlands, Czechia (−51.6). | Yes: `territorial-change` (plus `territorial-change-tonnes` for the "about 8.6 billion tonnes" wording) | **Exact match**: same 216 count, both top-10 lists and every value to 0.1 Mt. 219 eligible entities (218 ISO-coded plus Kosovo) confirmed. |
| 2 | 2005 to 2022: 45 of 164 cut CO2 while GDP grew; 38 with a cut of at least 5% (the headline). Largest by 2022 emissions: US, Japan, Germany, Canada, Mexico, Australia, Italy, Poland, UK, France (any decline). | Yes: `gdp-and-co2`, `gdp-co2-thresholds` | **Exact match**: 164 comparable, 45 any decline, 38 at least 5%. Top 10 and their % changes match (US −17.5% / +32.8%, UK −45.5% / +21.0%). GDP ends in 2022 in this file. |
| 3 | 2023, tonnes per person, territorial vs consumption: US 14.32 vs 15.81 (+10.4%), China 8.56 vs 7.63 (−10.8%), India 2.13 vs 1.77 (−17.0%), EU-27 5.51 vs 7.33 (+32.9%). | Yes: `consumption-per-person`, `eu27-audit` | **Exact match**. Consumption per person has no 2024 values for these four, so 2023 is the correct common year. |
| 4 | 1850 to 2024, share of 1,844.55 Gt global: US 23.57%, EU-27 16.27%, China 15.46%, India 3.58%; US plus EU-27 39.8%. China lacks 57 early years, India 19; not zero-filled. World includes international aviation and shipping. | Yes: `historical-shares`, `historical-combined` | **Exact match**: same denominator, same shares and cumulative totals; observed years China 118, India 156 of 175 (consistent with the stated gaps). |
| 5 | 2010 to 2024, 59 of 60 countries emitting at least 50 Mt in 2010 (Libya lacks coal data). Largest percentage-point drops in coal's share: Greece 33.3, Romania 23.1, Israel 22.0, Poland 19.5, US 19.4, Finland 19.3, Czechia 18.0, UK 17.6, Hungary 13.5, Germany 12.9. | Yes: `coal-share` | **Exact match**: 60 qualifying, 59 comparable, same ten and same values. |

All five answers replicate exactly. No wrong or unsupported number was found in chat or in the release.

One wording slip: in reply 6 the agent said slide 4's chart covers "the same ten countries". The chart actually shows the ten largest of the **38** (Spain, Netherlands, Czechia and Belgium replace Canada, Mexico, Australia and Poland from the reply-3 table). The slide text names the ten correctly, and the choice is consistent with the 38 headline, but the chat summary was inaccurate and the user did not notice.

## Timeline

| Phase | Messages | Time (UTC) | Notes |
|---|---|---|---|
| Init | m1 → r1 | 11:17:59 to 11:20:34 (2.6 min) | Git, venv, helpers, OWID codebook kept as a reference, storage paths recorded. The brief was held in the project README because the scope skill wants the interview before investigation records exist. |
| Scoping | r1 → m2 | 11:20:45 | Four questions with recommendations (priority lens, land-use scope, common year, coal metric); the user replied "use these recommendations". |
| Landing and import | m2 → r2 | to 11:23:40 (2.9 min) | Downloaded, checksummed, retained to the landed folder, 16 ingestion checks passed, 50,411 rows × 79 columns. |
| Cleaning and entity audit | m3 → r3 | 11:23:52 to 11:30:46 (6.9 min) | Clean scan (no fixes), Kosovo exception found, 35 non-country entities excluded, EU-27 member-sum check. |
| Exploring | — | — | No separate exploration step; the agent went from cleaning to the analysis. |
| Answering | r3 → m4 → r4 | to 11:33:24 | All five answered in r3. Follow-ups: the Q2 ≥5% threshold (38) and the Q4 denominator caveat, both in r4 (2.4 min). |
| Status | m5 → r5 | 11:33:32 to 11:37:56 (4.4 min, shared with the preview) | Prose status: results current, no draft, uncommitted work. |
| Packaging: headline preview | r5 | same turn | 8 headlines plus an appendix in `draft/.preview/headlines.md`. |
| Packaging: full draft | m6 → r6 | 11:38:15 to 11:48:40 (10.4 min) | Full draft, 5 chart files, methodology note; review found 1 issue, fixed, scoped re-review clean. |
| User review and corrections | m7 → r7 | 11:49:04 to 11:55:47 (6.7 min) | Rounding and punctuation edits, as one-off changes; scoped review clean. |
| Release | m8 → r8 | 11:55:54 to 11:56:44 (0.8 min) | Release 001 frozen, external copy verified, caveats listed. |
| Done | m9 | 11:56:57 | User accepted. |

## Package review loop (the main focus of this run)

From `kit/reviewloop.py` on this run, cross-checked against the agent logs:

| Request | Turn | User wait | Review rounds | Outcome | Review tail |
|---|---|---|---|---|---|
| Status plus headline preview (m5) | agent-005 | 4.4 min | 0 (preview stage, before review; 2 preflight check-draft runs) | — | 0 |
| Full draft (m6) | agent-006 | **10.4 min** | **2**: full review (1 narrative problem: a "consistent within source rounding" tolerance phrase in the donor note), then one fix and a scoped re-review (clean) | passed | 3.1 min |
| One-off rounding edits (m7) | agent-007 | 6.7 min | **1**: scoped review (clean) | passed | 3.0 min |
| Release (m8) | agent-008 | 0.8 min | 0 (reused the current receipt; 1 verify check) | passed | 0 |

Packaging and release requests took 22.3 min of 37.1 min of agent time (60%); the review tails (first review start to end of turn) took 6.1 min (16%). **There was no perfectionism loop.** No request ran more than two review rounds, each review problem was fixed in one edit, the release did not trigger another review, and no review rule was invented (the user asked for one-off edits; 1 read-only review-rules check ran in agent-006). The second round in agent-006 cost about 2 minutes, to rewrite one sentence that a reviewer flagged under a fine-grained editorial rule.

The cost that remains sits in the **work around** review rather than in review cycles. The rounding turn needed a new recorded result (`territorial-change-tonnes`) so that the number checker would accept "about 8.6 billion tonnes". That turn also ran 4 check-draft passes and a package export retry. The full-draft turn ran 6 check-draft passes and spent about 7 minutes reading skills and templates and writing the draft before the first review started.

Measurement note: reviewloop.py reports `reviewers=0` for every turn. The Codex logs carry only `collab_tool_call` items with `tool: wait` (2 in agent-006, 1 in agent-007), never `spawn_agent`. The agent's notes name three read-only reviewers (package_review, package_review_scoped, precision_review). That is a harness counter gap, not missing reviews.

## Referee-observed pain points

| # | Observation | Where | Severity |
|---|---|---|---|
| 1 | Default display precision was too high for the stated donor audience (8,645.2 Mt, 23.57%), which cost a full correction round. | r6, m7, r7 | major |
| 2 | A cosmetic unit or rounding change needed a new analytical result and seven validations, because check-draft cannot trace scale conversions (Mt to billion tonnes). | r7; agent-notes; `evidence/territorial-change-tonnes.json` | major |
| 3 | Heavy instruction load: long skill, template and guide reads, several truncated and re-read; the full-draft turn waited about 7 minutes before review started. | agent-001, agent-005, agent-006 logs; agent.md #2 | major |
| 4 | The agent linked the user to an agent-only `awb-scope/SKILL.md` to justify asking questions. The user did not open it. | r1 | minor |
| 5 | Interim narration plus final summary repeated content in one reply (the four scoping questions twice; "all five accepted" twice). | r1, r3, r5 | minor |
| 6 | The status reply was prose, not the scannable one-screen report with suggested next requests that the user expected from the README. | r5 | minor |
| 7 | Internal identifiers in user-facing text: "cohort checks", "shared dataset `owid_co2`", "Primary result: territorial-change" in the preview. | r2, r5, preview file | minor |
| 8 | The headline preview sits in a hidden `.preview` folder. | r5 | minor |
| 9 | Absolute links in early replies, relative links in r7. | r7 | minor |
| 10 | No materiality threshold was proposed for Q2; the user had to raise it (cost one exchange). | m4 | minor |
| 11 | Chat said "the same ten countries" for the Q2 chart, but the set changed with the 38 threshold (the slide text is correct). | r6 | minor |
| 12 | Tool quirks: MCP `read profile` rejected `settings` despite the schema; read-only check-draft returns an error for expected lifecycle state (inflating the harness's "MCP failures"); the name checker flagged the prose word "coal-share" as a result ID; status called state "out of date" over a one-second timestamp skew. | harness-log (agent-003, -006, -007); agent.md #4, #5, #7, #8 | minor |
| 13 | "About 8 slides" became 10 assembled slides (8 main, 1 appendix, 1 divider); disclosed, and the user accepted. | r5 | minor |
| 14 | Sandbox noise: zsh heredoc temp-file failures, git xcrun and pip cache warnings. | agent-001, agent-008; agent.md #10 | minor (harness) |

There were no stalls, loops, wrong numbers, protocol breaches by the user, or unauthorized commits or releases. The agent never committed; it mentioned a commit once, in the status report.

## Isolation audit

- **Agent (Codex) logs**, all 9 turns, read through `logview.py --full`: no reads of `workbench-spec`, `workbench-design`, `CONTEXT.md`, any `docs/` folder, the analytics-workbench repository, `co2-A/human`, `co2-A/relay` or `transcript.md`. File-reading SQL in MCP calls (`read_csv`) touched only the project's own `data/raw/...` and `investigations/.../results/` files. Web access went only to OWID hosts (ourworldindata.org, github.com/owid, raw.githubusercontent.com/owid). Outside the project, the agent touched only its own skill files under `agent-home/.agents/skills/`, its own `agent-home/.cache/tmp`, and `../feedback/agent-notes.md` (by design). In agent-001 it ran an ancestor scan for AGENTS.md or CLAUDE.md over the project's parent folders: the output was empty and nothing was read, so it did not matter.
- **User (Claude) logs**, all 10 turns: reads limited to `human/BRIEF.md`, `human/README.md`, its own `human/notes.md`, globs of `storage/landed` and `storage/releases`, and deliverables the agent pointed to (preview, findings, methodology note, START-HERE, chart-1.csv under `deliveries/`). No AGENTS.md, SKILL.md, `src/`, `.py`, `workbench-guides/` or agent-home reads. The user ignored the SKILL.md link and logged it as friction.
- **Verdict**: clean on both sides.

## Identity check

- `git log --all` in the project returns nothing: the project has **no commits**, so no author or committer identities exist. The agent home's git identity is the placeholder sim analyst at example.com, unused.
- In project files and storage (excluding the third-party `.venv`): no real person's name, **no email address at all**, and no macOS home-folder path.
- The one identity-adjacent string is the account-name slug that is part of the harness's scratchpad path. The user gave that path as the storage location, so it appears in `project/README.md`, `project/foundation/sources.md`, the review snapshot copy of `sources.md`, compiled `.pyc` files and `.venv` scripts. **It does not appear in the released package or in `storage/`.** This is caused by the harness location, not by the product.
- The `.venv` contains macOS home-folder strings and author emails from upstream packages (pip, pandas, duckdb). None of them is this machine's home folder or user.

## Most important issues for the workbench maintainers (ranked)

1. **Presentation transforms in package number checking**: unit scaling, rounding and "about N" wording should be declarable and checked against the source result, without creating a new analytical result for a display change (r7; agent.md #1).
2. **Audience-appropriate default precision**: when the brief names a semi-technical audience, propose display precision at the headline checkpoint or default to coarser rounding; this run lost a full round to rounding (m7).
3. **Instruction load for packaging**: a compact task index of required reads would cut the 7 minutes of reading and drafting before review in the full-draft turn, and the truncation re-reads (agent.md #2).
4. **Agent-facing material leaking to the user**: SKILL.md links, result IDs and "cohort" or "records" vocabulary in chat and in the preview (r1, r2, r5).
5. **Status output shape**: the status report should come back as the scannable list with suggested next requests, not as prose (r5).
6. **Tool polish**: `read profile` and `settings` schema mismatch, check-draft preflight exit codes for expected lifecycle states, the result-ID name false positive, timestamp-based staleness noise (harness-log; agent.md #4, #5, #7, #8).
7. **Proposing materiality thresholds** for "reduced" style questions during scoping (m4).
8. The review loop itself is **no longer a problem** in this run: at most 2 rounds per request, a 3-minute review tail, and no review at release.
