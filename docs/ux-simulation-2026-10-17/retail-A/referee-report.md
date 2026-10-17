# Orchestrator report: retail-A (variant A)

Variant A: Claude (Opus, headless) played the user, a head of e-commerce at a UK giftware wholesaler. Codex (`codex exec`) played the agent, with the awb skills and the awb MCP server. Dataset: Online Retail II (UCI), two-sheet workbook. Paths below are written as `SIMS/retail-A/...`.

## Run summary

| Item | Value |
|---|---|
| Relay started | 2026-10-17T11:17:43Z |
| Conversation ended | 2026-10-17T12:21:14Z (63.5 min) |
| Relay finished (after feedback turns) | 2026-10-17T12:24:08Z (66.4 min) |
| Outcome | DONE: the user declared the end point reached |
| User messages | 10 (9 delivered and answered, plus the closing DONE message, which is never relayed) |
| Agent replies | 9 conversation replies, plus 1 feedback turn (state.json `agent_turns` = 10) |
| User model cost | $0.85 |
| Relay errors | none (`relay/relay.log` empty; harness log shows 3 MCP "failures", all expected `check-draft` not-yet-passing results) |

Sources: `SIMS/retail-A/relay/state.json`, `SIMS/retail-A/transcript.md`, `SIMS/retail-A/feedback/harness-log.md`.

## End-point checklist (from `human/BRIEF.md`)

| Criterion | Met | Evidence |
|---|---|---|
| All five questions answered with specific answers the user accepts | Yes | Agent reply 4 gives all five. User message 5 accepts Q1, Q2, Q3 and Q5. User message 6 picks Q4 version B after reply 5's comparison. In `project/investigations/marketing-budget/questions.md`, all five root questions are `answered`, each with linked evidence JSON. |
| Asked where things stand at least once | Yes | User message 5: "Then use awb-status — where are we?". Reply 5 carries the awb-status report. |
| Package draft exists and the user reviewed it | Yes | Headline preview in reply 6, edited in message 7. Full draft in reply 7: `project/deliveries/marketing-budget/leadership-budget/draft/` (findings.md, methodology-note.md, START-HERE.md, 4 chart CSVs). In message 8 the user read all three files and requested two corrections, which reply 8 applied. Message 9 approved them. |
| Released as 001 and copied to the releases folder | Yes | Reply 9. `project/deliveries/marketing-budget/leadership-budget/released/001/` and `storage/releases/marketing-budget/leadership-budget/001/` are byte-identical (referee `diff -r`: no differences). The release holds findings.md, methodology-note.md, methodology.md, START-HERE.md, deck-rules.md, assembly/, charts/chart-1..4.csv and manifest.json (`release_number` 001). |

## The five answers

Spot-check method: the referee converted the landed workbook (`storage/landed/data/raw/online-retail-ii/uci-20261017/online_retail_II.xlsx`) to Parquet and recomputed each answer with DuckDB (`referee/convert.py`, `referee/spotcheck.py`, `referee/q4check.py`, `referee/extra.py`). The overlap was handled independently: sheet-1 rows dated on or after 2010-12-01 were dropped. That is exactly 22,523 rows worth £377,488.45 net, the same block the agent found, so the overlap is the whole sheet-1 December 2010 tail. The approved code treatment was applied: POST, DOT, C2 and D are included; internal codes, vouchers, M/m and BANK CHARGES are excluded. December 2011 is excluded.

| Q | Agent's final answer | Recorded result | Referee spot-check |
|---|---|---|---|
| 1 | Monthly net revenue for Dec 2009 to Nov 2011, 24 values (e.g. Nov 2010 £1,423.5k, Nov 2011 £1,479.8k). Total £18.94m. Year totals £9.34m and £9.60m (+2.9%). September to November is 36.0% and 37.5% of the year, with November the peak in both years. | Yes: `evidence/monthly.json`, `evidence/seasonality.json` | **Matches exactly**: all 24 months to £0.1k, total £18,937,555.76, years £9,335,300 and £9,602,256, September to November shares 36.0% and 37.5%. |
| 2 | Top 585 of 5,850 identified customers bring £10.22m: 63.1% of identified-customer revenue and 54.0% of all net revenue. No-ID revenue is £2.75m (14.5%). | Yes: `evidence/concentration.json` | **Matches exactly**: 5,850 customers, top 585, £10,219,492, 63.1% and 54.0%, no-ID £2,747,508 (14.5%). |
| 3 | 40.8% (1,372 of 3,365) of customers first seen in 2010 bought again on a later day within 90 days. Monthly cohorts run from 52.7% (Jan) to 15.8% (Dec). | Yes: `evidence/cohorts.json`, `evidence/retention-summary.json` | **Matches exactly**: all 12 cohort sizes and rates, and 1,372 of 3,365 overall. |
| 4 | Version B, which requires at least 3 identified cancelling customers. Of 1,261 eligible products, Black Cherry Lights ranks first: 99.0%, 51 cancellation invoices, 48 customers. The ceramic jar is second at 95.1%, with the caveat that one invoice is 99.6% of its cancellation value. | Yes: `evidence/products.json`, `evidence/products-three-customers.json`, `evidence/cancellation-drivers.json` | **Matches exactly**: the unrestricted top 10 (rates, invoice counts, customer counts) and 2,483 eligible products; the version B top 10 and 1,261 eligible products. |
| 5 | Ranked by £ increase: Australia +£107,718 (one customer supplies 90.3% of year 2), France +£69,836, Japan +£31,210, Norway +£26,137, Germany +£22,400. | Yes: `evidence/countries.json`, `evidence/market-concentration.json` | **Matches exactly**: top five, bases and increases; Australia's top customer is 90.3% of year 2. Manual/bank sensitivity also matches (−£118,465.59, −0.63%). |

All five answers are backed by recorded results and reproduce independently from the landed source.

## Timeline

| Phase | Messages | Agent minutes | What happened |
|---|---|---|---|
| Init | msg 1 → reply 1 | 2.0 | awb-init: Git, `.venv`, helpers through MCP setup. Storage paths and source URL recorded, ZIP deliberately not downloaded. Four scoping questions, each with a recommendation. |
| Scoping | msg 2 → reply 2 | 3.0 | User accepted all four recommendations and volunteered the persona facts. Investigation `marketing-budget` created. Revenue-treatment recommendation given. |
| Landing and checking | msg 3 → reply 3 | 12.2 | Downloaded and retained the ZIP and workbook. 1,067,371 rows published with 25 checks passing. Found the December 2010 cross-sheet overlap (22,523 lines, £377k), a voucher under numeric code 22016, and a positive-quantity cancellation. Presented a 27-code audit table with values. |
| Cleaning and answering | msg 4 → reply 4 | 17.5 | Applied the approved corrections (1,044,848 rows) and committed. Recorded 13 results with 91 checks, answered all five questions, and ran an unprompted manual/bank sensitivity check. Commits 9096f84, 90e317e, 7f1ccf0. There was no separate exploration step: the user asked for the answers directly. |
| Q4 refinement and status | msg 5 → reply 5 | 6.3 | Two Q4 rankings with invoice and customer counts. The agent pointed out that the ceramic jar still passes the 3-customer screen. awb-status report. |
| Packaging: headlines | msg 6 → reply 6 | 6.2 | Explained the "14 findings". Eight-slide headline preview, waiting for approval. |
| Packaging: full draft | msg 7 → reply 7 | 8.7 | Applied the headline edits, and pushed back with evidence on "broadest overseas growth". Full draft, 453-word note, 4 charts. Two review rounds. |
| Review corrections | msg 8 → reply 8 | 3.7 | Source wording and plain-English fixes, changed lines quoted in chat. Asked an optional question about future review rules. One scoped review round. |
| Release | msg 9 → reply 9 | 1.7 | Two global review rules added. One scoped review round, then release 001 frozen and copied, both copies verified. |
| End | msg 10 | none | User checked the releases folder and sent DONE. |

## Package review loop (perfectionism-loop check)

Source: `python3 SIMS/kit/reviewloop.py SIMS/retail-A`, cross-checked against the agent logs and `feedback/agent-notes.md`.

| Request | User waited | Review rounds | Detail |
|---|---|---|---|
| Headline preview (msg 6) | 6.2 min | 0 | Preview checkpoint only. 1 check-draft run. |
| Full draft (msg 7) | 8.7 min | 2 | The full review found 3 narrative problems: an unsupported verification adjective, a passing-check claim without evidence citations, and an imperative inside a chart-builder instruction. All were repaired, and a fresh scoped review was clean. 3 receipt starts (one scoped start repeated after an export refresh, before the reviewer launched), 4 check-draft runs. Time from first review start to end of turn: 3.3 min. |
| Wording corrections (msg 8) | 3.7 min | 1 | Scoped review clean on the first pass. 3 check-draft runs. Review tail 1.4 min. |
| Release (msg 9) | 1.7 min | 1 | Adding the two approved review rules made the earlier review stale, so the agent ran a fresh scoped review: clean. Review tail 1.2 min. |

Verdict: **no perfectionism loop in this run.** No request needed more than two review rounds. Every second or later review was clean on its first pass. No review was refused, and no third round ran. All packaging and release turns together cost the user 20.3 min of waiting, 32% of the 63.5-minute conversation. Review activity (first review start to end of turn) was 5.9 min, 9% of the conversation. The longest single packaging wait was the full draft at 8.7 min, well under the README's "up to about half an hour". The reviews also found real problems: all three first-round findings were genuine wording or citation issues.

Measurement notes:
- `reviewloop.py` reports `reviewers=0` for every turn. Codex's `--json` log does not record subagent spawns, only `wait` calls: 3 in reply 7, 1 each in replies 8 and 9. The agent's notes confirm a fresh read-only reviewer for each round, 4 reviewers in total.
- `reviewloop.py` also flags agent-001 as a packaging turn because the agent read the awb-package skill during init. Its "packaging turns 22 min (35%)" therefore includes 2 min of init. Without it the figure is 20.3 min.

## Isolation audit

- **Agent logs** (`relay/agent-001..010.jsonl`, rendered with `logview.py --full`): no reads of workbench-spec, workbench-design, CONTEXT.md, any `docs/` folder, the analytics-workbench repository, `SIMS/retail-A/human`, `SIMS/retail-A/relay`, `transcript.md` or the kit. No home-directory paths outside the sim. The agent read only its fake home's skills, the project, `storage/` and its own `feedback/agent-notes.md` and `agent.md`. MCP SQL read only project and landed data. It also fetched the public UCI dataset page from the web, which is the source the user named. Clean.
- **User logs** (`relay/human-001..011.jsonl`): reads were limited to `human/BRIEF.md`, `human/README.md`, the three draft files the agent pointed to (findings.md, methodology-note.md, START-HERE.md) and a Glob of `storage/releases`. The user never read AGENTS.md, SKILL.md, `src/`, `.py` files, workbench-guides or agent homes. Matches on "SKILL.md" in the user logs are the user's own notes text, not reads. Clean.
- **Near-breach, not a breach:** agent replies 1, 3, 6 and 8 linked the user to SKILL.md files in the agent home and quoted them. The user declined to open them each time (`human/notes.md`, turns 2, 4, 7 and 9).

## Identity audit

- **Git:** all 3 commits are authored and committed by the sim identity at the example.com address. No other author or committer.
- **Home paths:** no home-directory path in project files (excluding `.venv`), `.git` objects, Git history or storage.
- **Account name:** the OS account name appears in `project/README.md` (storage-location lines) and `project/foundation/sources.md` (retained-copy path). In both it is only part of the simulation's own scratchpad path: the temp directory's name encodes the real home-folder path. The user supplied these paths in message 1. Both files are committed, so the name is also in Git history. This is a harness artifact of where the sim runs.
- **Third-party email:** one address, not belonging to anyone in this study, is embedded in the JSON payload of the retained public dataset web page (`project/foundation/references/online-retail-ii/uci-dataset-page.html`, committed).
- **Real person's name:** the public dataset creator's name appears in provenance and attribution text: `foundation/sources.md`, `foundation/references/online-retail-ii/README.md`, the saved dataset page, `exploration/intake-review.md`, `foundation/review-rules.md` (in the rule that keeps it out of audience text), and the released, builder-only `methodology.md` (both release copies). The audience files (findings.md, methodology-note.md) are clean after the message 8 correction.
- **Persona name:** not present in the project or storage.
- **Minor:** recorded timestamps carry the host's local UTC offset (e.g. `foundation/sources.md`).

## Pain points observed by the referee

| # | Issue | Messages | Severity |
|---|---|---|---|
| 1 | The full draft named the public repository and the dataset creator as the source. The user had to correct it before release. Mostly a simulation premise conflict (a public dataset presented as company data), but no step asked how the source should be named for the audience. | reply 7, msg 8 | minor (harness-driven) |
| 2 | The agent cited and linked its own SKILL.md files to the user four times, using them as the reason it was asking. | replies 1, 3, 6, 8 | minor |
| 3 | Replies repeat themselves. Interim progress messages ("I'll do X… now checking Y") are followed by a full summary of the same content. In reply 4 the answers start halfway down. | replies 2–9 | minor |
| 4 | awb-status counts 14 calculation-level findings ("seven supported, seven provisional") for 5 business questions. This cost one user question. | reply 5, msg 6 | minor |
| 5 | The release location was given as a relative link (`../storage/releases/...`), though the README promises "the copy's full path". Other draft links were relative too. | replies 6–9 | minor |
| 6 | Workbench terms leaked into chat: commit hashes, check counts, "stale", `.venv/bin/python`, "UCI sent no version headers". | replies 1, 3, 4, 5 | minor |
| 7 | The future review-rule question came mid-reply, with three options, no plain explanation of what a rule does, and a skill quote. | reply 8 | minor |
| 8 | The audience text says the repeated lines were "as confirmed by the e-commerce lead". The user had only called them plausible. | reply 8 | minor |
| 9 | Release 001 shipped while the Q4 version B producer and queries, the review rules and the package formats were uncommitted. The manifest records them as `producing_uncommitted_changes` and `packaging_uncommitted_changes` with checksums, so they are disclosed, but the user was not reminded at release. | replies 5, 9 | minor |
| 10 | Agent-side packaging overhead: a manifest of about 20k tokens, truncated state and status reads, many format references, a strict note-length line parser, a date-like ID flagged as an unrecorded number, and the 15-word headline limit against a user's 16-word headline. The user saw little of this (the full draft took 8.7 min). | reply 7 (agent notes) | minor |
| 11 | Codex sandbox: zsh here-documents could not create temp files, and the xcrun and pip caches were unwritable. The agent worked around both. | replies 1, 6 | minor (harness) |
| 12 | The user volunteered every persona fact in message 2 without being asked, which thinned the scoping interview. This is a known study limit. | msg 2 | minor (harness) |

There were no wrong or unsupported numbers: every figure checked reproduces from source. There were no stalls or loops and no skill misuse. The slowest phases were cleaning plus answering (17.5 min) and landing (12.2 min).

## User satisfaction

**8/10.** The user would use the workbench again (`feedback/human.md`). The user praised the analysis quality, the data catches, the recommendations with every question, the pushback on an overstated headline and the changed lines shown before release. Marks were taken off for verbosity and visible internals.

## Most important issues for workbench maintainers (ranked)

1. **Status should lead with business questions.** awb-status reports calculation-level findings and a supported/provisional split that mixes user acceptance with evidence strength. Show per-question status and group supporting checks underneath. Raised by both the user and the agent.
2. **Keep agent-instruction files out of user-facing replies.** The agent repeatedly linked and quoted SKILL.md as the reason for asking. The skills should tell the agent to ask the question without citing skill files or paths.
3. **Lead with the result and cut the progress narrative.** Interim commentary followed by a full restated summary roughly doubles reading time. The skills' reply guidance should favour a single result-first message.
4. **Report absolute paths at release, as the README promises.** Draft links should be absolute too.
5. **Ask how the source should be named for the audience.** Store the business identity of the source separately from its download provenance and generate audience source lines from it. This run's trigger was harness-driven, but the gap is real for any downloaded or third-party data.
6. **Make the review-rule question non-blocking and plain.** Explain in one line what saving a rule does for the user.
7. **Trim the packaging mechanics the agent must read and handle:** a short preview-only path, compact structured state and status output, manifest summaries, and tolerant metadata parsing. No user-visible loop happened this time, but agent-side cost remains high.
8. **Remind the user about uncommitted producing code at release,** or offer a commit before freezing.
