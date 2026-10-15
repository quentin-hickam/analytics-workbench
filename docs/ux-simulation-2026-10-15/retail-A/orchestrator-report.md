# Orchestrator report: retail-A

## Run summary

- **Variant:** A. Claude Opus played the human (nested subagent `retail-A-human`, persona Priya Natarajan, head of e-commerce). OpenAI Codex played the agent (`codex exec`, session `01a13f93-7cd2-7b92-aca8-47c00f09c719`, HOME = `retail-A/agent-home`, cwd = `retail-A/project`).
- **Start:** 2026-10-15 08:39 local (12:39Z). **Conversation end (human STATUS: DONE):** 10:15 local (14:15Z). **Feedback complete:** 10:17 local (14:17Z).
- **Wall-clock:** about 1 h 36 min to the end point; about 1 h 40 min including feedback.
- **Turns:** 10 human messages (9 relayed to the agent, the 10th was the closing DONE message) and 9 agent conversation turns, plus 1 agent feedback turn. Well inside the caps (45 messages / 8 h).
- **Fallback:** not used. Nested spawning and SendMessage worked on every turn. No Codex turn failed or needed a retry.
- **Protocol incidents:** none. Neither role needed a harness note; no loops.

## End-point checklist

| Criterion | Met? | Evidence |
| --- | --- | --- |
| All five questions answered specifically and accepted by the human | Met | Agent turn 3 (answers), turn 4 (Q4 rework, April and December follow-ups); human acceptance in human turn 5. Ledger: `project/investigations/marketing-budget-priorities/questions.md` (Q-002, Q-003, Q-004, Q-006 answered; Q-005 superseded by Q-014 answered) |
| Human asked where things stand at least once | Met | Human turn 5 ("Use awb-status — where are we?"); agent turn 5 status reply |
| Deck package draft exists and was reviewed | Met | `project/deliveries/marketing-budget-priorities/leadership-budget/draft/` (findings.md, methodology.md, charts/chart-1..3.csv, datasets/*.csv, manifest.json); human review and corrections in human turns 7 and 8 |
| Released as release 001 and copied to the releases folder | Met | `project/deliveries/.../released/001/` and `storage/releases/marketing-budget-priorities/leadership-budget/released/001/`; `diff -r` of the two trees reports identical |
| Original data kept in the landed folder | Met | `storage/landed/data/raw/uci-online-retail-ii/2026-10-15-uci-original/` (ZIP, XLSX, provenance.json) |
| All findings recorded with evidence | Met | `project/investigations/marketing-budget-priorities/state.md` lists 21 findings with evidence files under `evidence/`; 20 supported, 1 superseded (raw product ranking) |

## The five questions

Spot checks are my own read-only DuckDB queries (project venv Python, run with `-I` from outside the project) against the agent's published raw-line Parquet `project/data/parquet/retail_lines/2026-10-15-v1/lines.parquet` (1,067,371 rows, both sheets). I removed the cross-sheet overlap myself (sheet "Year 2009-2010" rows dated on or after 2010-12-01) and applied the agreed revenue scope myself (excluding AMAZONFEE, B, M, BANK CHARGES, CRUK, S, ADJUST*, TEST*, gift vouchers; keeping merchandise, POST, DOT, C2, D).

| # | Question | Agent's final answer | Recorded? | Spot check |
|---|---|---|---|---|
| 1 | Monthly net revenue Dec 2009–Nov 2011, seasonality | 24 monthly figures (e.g. Nov 2010 £1,423.5k, Apr 2011 £492.1k, Nov 2011 £1,479.8k); annual £9.335m → £9.602m (+2.9%); Sep–Nov = 36.0% / 37.5% of each year | Yes: `evidence/monthly-revenue.json`, `evidence/seasonality.json` | **Checked, exact match.** All 24 months match to £0.1k; two-year total £18,937,639 matches the agent's £18.938m. Overlap-corrected row count 1,044,848 also matches. |
| 2 | Top-10% customer share; revenue with no customer ID | Top 585 of 5,850 identified customers = £10.219m = 63.1% of identified, 54.0% of all net revenue; no-ID revenue £2.748m = 14.5% | Yes: `evidence/customer-concentration.json` | **Checked, exact match.** 5,850 customers, top 585 = £10,219,492, 63.12% / 53.96%; no-ID £2,747,591 = 14.51%. |
| 3 | 90-day repeat rate by 2010 first-purchase month | 3,364 customers, 1,362 repeat (40.5%); monthly range 52.4% (Jan) to 15.8% (Dec) | Yes: `evidence/repeat-cohorts.json` | **Checked overall, exact match.** First positive merchandise purchase in 2010, later-day non-cancelled purchase within 90 days: 3,364 / 1,362. Monthly breakdown not separately checked. |
| 4 | Highest cancellation rate by value, meaningful sales | Raw ranking (turn 3) superseded at the human's request by a screened top 10 (turn 4): ≥ £1,000 gross, ≥ 20 net-positive identified buyers, no single credit > 25% of cancellation value. Black Cherry Lights 99.0%, then six other Cherry Lights variants, Vintage Blue Kitchen Cabinet 25.5%, Rococo Wall Mirror 19.8%, Cream Sweetheart Magazine Rack 19.4% | Yes: `evidence/product-screened.json`, `evidence/product-screen-sensitivity.json`; raw in `evidence/product-cancellations.json` (superseded) | **Checked the rates, match.** 79323B gross £1,572 / credits £1,557 = 99.0% across 51 credit invoices; 79323W 35.6%; 85063 19.4%; 23166 95.1% (raw). I did not re-derive the buyer-count and credit-share screen. |
| 5 | Non-UK countries with largest net revenue growth | Australia +£107.7k, France +£69.8k, Japan +£31.2k, Norway +£26.1k, Germany +£22.4k; Ireland −£91.2k flagged | Yes: `evidence/country-growth.json`, `evidence/country-growth-chart.json` | **Checked, exact match.** All five values and both period totals match to £0.1k; EIRE −£91.2k matches. |

No discrepancies found. Every number I tested reproduced exactly.

## Timeline of phases

| Phase | Turns | Notes |
|---|---|---|
| Init + scoping | 1 | `awb-init` and scoping done together in one turn, about 5 min. The agent recorded 10 questions, "3 need your context", but did not name them. MCP writes were unavailable and `git init` was blocked; the agent fell back to the CLI and continued without Git. |
| Scoping answers | 2 | The human supplied definitions unprompted, because it could not tell which three questions were open. |
| Landing + cleaning | 2 | Download, landing with checksums, and Parquet publication in one turn (about 8 min). One user decision: cross-sheet duplicates. |
| Exploring + answering | 3 | All five answers in one turn (about 15 min), plus a retention-led recommendation. |
| Follow-ups | 4 | April 2011 dip bridge, Q4 rework with a recommended screen, December cohort diagnostic (about 22 min, the longest turn). |
| Status | 5 | `awb-status`: short and accurate. |
| Packaging | 6–8 | Headline checkpoint (6); full draft and methodology (7); chart for slide 6 and a plain-English methodology summary, plus Copilot build instructions (8). |
| Review | 7–8 | Human requested headline rewrites, CSV rounding, a slide 6 chart, and a summary-first methodology note. |
| Release | 9 | Release 001 frozen and copied; verified identical. |

## Pain points observed as referee

1. **Agent linked agent-internal SKILL.md files in user-facing messages (minor, repeated).** Turn 2 (awb-clean SKILL.md) and turn 6 (awb-package SKILL.md, with a quote). The agent's feedback says a higher-priority instruction requires naming or quoting the skill whenever it forces a pause. That instruction pushes users toward files they should not need to open. The human declined both times and flagged it.
2. **Default methodology note unsuitable for the stated audience (major).** Turn 7. It used question codes, file paths and terms like "immutable publication" despite "leadership, non-technical" being recorded in turn 1. Fixed in one turn on request (turn 8).
3. **Deliverable is a content package, not a .pptx, and this surfaced late (major for the user's expectations).** First mentioned in turn 7. Exact files and a one-line Copilot instruction came only after the human asked (turn 8).
4. **Turn-1 "3 need your context" without listing them (minor).** It cost part of a turn.
5. **Unrounded audience CSVs (minor).** Turn 6 exports had floating-point tails such as 366.89000039169395; fixed in turn 7 after the human asked.
6. **Raw Q4 ranking presented as the answer despite an obvious outlier (minor).** Turn 3. The agent flagged the storage-jar order itself but still led with the raw list; it needed a rework in turn 4.
7. **Weak external citation (minor).** Turn 4. A district-council committee PDF was cited as the "Official 2011 holiday list". The agent's own log shows GOV.UK fetches timed out.
8. **Environment friction handled by the agent:** MCP write tools refused under approval policy "never"; `git init` was blocked by filesystem policy; system python3 3.9.6 is below the helpers' 3.10+ requirement. The CLI fallback worked, but the user was shown "MCP writes were unavailable" and "Git initialization was prevented" in turn 1 and had to ask what they meant.
9. **Heavy internal cost of small presentation changes (agent-side, major for efficiency).** Per agent.md: editing methodology prose marked all 19 results stale; a six-bar chart subset required a new recorded result and a refresh of 21 results; storyline inference from citations moved slides; the quality-table parser rejected custom rows four times. None of this reached the user as an error, but it inflated turns 4, 7 and 8.

**Isolation:**
- **Codex logs** (`relay/agent-*.log`): no reads of `workbench-spec`, `workbench-design` or `docs/`. `CONTEXT.md` appears only inside workbench-guide text that the agent read (an instruction never to write meanings there), not as a file it opened. The only `/Users/` paths are `which python3` interpreter-discovery output (pyenv and `~/.local/bin` shims), not file reads. No references to sibling simulations.
- **Human role:** opened only README.md and the files the agent pointed it to for review: findings.md, methodology.md, the CSVs, and the releases folder. It explicitly declined the SKILL.md links.
- **No isolation breaches.**

## Most important issues for maintainers, ranked

1. **Audience-appropriate package defaults.** Generate a plain-English, summary-first methodology note; leadership-ready headlines; rounded audience exports; and a chart for every evidence slide whenever the recorded audience is non-technical. Turns 7–8 were spent largely on these. (Human pain points 2, 5, 6; agent pain points 5, 6, 10.)
2. **Make the deliverable format explicit early.** The README and the agent should say at scoping time that the package is slide content plus editable-chart CSVs for the M365 Copilot PowerPoint agent, not a .pptx. Ship the exact attachment list and a one-line build prompt with every draft by default. (Human's top pain point.)
3. **Stop surfacing internal instruction files to users.** Replace "required by [awb-package](…/SKILL.md)" links with plain decision requests. The rule mandating skill links in user-facing pauses conflicts with the README audience. (Repeated in turns 2 and 6.)
4. **Lightweight provenance for presentation edits.** Narrative-only edits should not invalidate computation. Chart row selections need a projection facility rather than a new recorded result with a full refresh. Storyline order should be explicit, not inferred from citations. (Agent pain points 1, 3, 4; the main time sink.)
5. **Environment robustness and messaging.** Detect MCP write unavailability and missing Git once, route silently to the CLI and a no-VCS mode, and tell the user only when an action is needed. Bootstrap a 3.10+ interpreter automatically. (Agent pain points 2, 9; human turn 2 confusion.)
6. **Scoping should ask, not just record.** List the open user questions by number in the turn-1 reply. The README promises that awb-scope "interviews you"; here the scope was recorded without asking anything directly, and it worked only because the human front-loaded detail.
