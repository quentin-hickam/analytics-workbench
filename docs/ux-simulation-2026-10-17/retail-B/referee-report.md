# Referee report: retail-B (variant B)

Variant B: Codex plays the user (head of e-commerce persona, retail dataset); Claude Opus (headless `claude -p`, real skill discovery) plays the agent with the awb skills and MCP server.

## Run summary

| Item | Value |
|---|---|
| Relay started | 2026-10-17T11:17:43Z |
| Conversation ended | 2026-10-17T11:55:23Z (outcome DONE) |
| Relay finished (after feedback) | 2026-10-17T11:56:57Z |
| Wall clock | 37.7 min conversation, 39.2 min total |
| User messages | 8 written; 7 delivered and answered, plus the final DONE message (not relayed, by design) |
| Agent turns | 7 replies plus 1 feedback turn (8 in `state.json`) |
| Agent cost | $13.26 |
| Permission prompts a real user would have approved | 0 (`SIMS/retail-B/relay/permission-prompts.jsonl` was never created) |
| MCP failures | 0 (harness log) |
| User satisfaction | 8/10 |

Sources: `SIMS/retail-B/relay/state.json`, `SIMS/retail-B/transcript.md`, `SIMS/retail-B/feedback/harness-log.md`.

## End-point checklist

| Criterion (from the user brief) | Met | Evidence |
|---|---|---|
| All five questions answered with specific figures the user accepts | Yes | Message 5 ("I accept the five quantitative answers"), message 8; `SIMS/retail-B/project/investigations/marketing-budget-evidence/questions.md` shows Q-001 to Q-005 `answered`, each linked to recorded evidence; `state.md` shows all eight findings `supported` |
| User asked where things stand at least once | Yes | Message 4 opens "Use awb-status — where are we?"; reply 4 has a "Where we are" section built from the `read status` MCP call |
| Package draft exists and the user reviewed it | Yes | Reply 5 lists review paths; the user's log shows reads of `draft/START-HERE.md`, `findings.md`, `methodology-note.md` and heads of the four CSVs (human-006); corrections requested in message 6 and applied in reply 6 |
| Released as 001 and copied to the releases folder | Yes | `SIMS/retail-B/project/deliveries/marketing-budget-evidence/leadership-deck/released/001/` and `SIMS/retail-B/storage/releases/marketing-budget-evidence/leadership-deck/001/`; `diff -r` of the two trees is empty; manifest `release_number` 001, `status` release, no revalidation flags, no uncommitted changes |

Landed original (`online_retail_ii.zip`, extracted workbook, provenance) is in `SIMS/retail-B/storage/landed/data/raw/uci-online-retail-ii/2026-10-17/`.

## The five questions

All spot-checks are the referee's own read-only queries on the referee's own conversion of the landed workbook (`SIMS/retail-B/referee/convert.py`, `spotcheck.py`, `q3b.py`, `q4.py`). The conversion reproduced the agent's 1,067,371 lines; the 22,523 lines of 1 to 9 December 2010 in the first sheet each have an identical counterpart in the second sheet (EXCEPT ALL leaves 0), so the agent's de-duplication is correct.

| Q | Agent's final answer | Recorded result | Spot-check |
|---|---|---|---|
| 1. Monthly net revenue and seasonality | Full 24-month table (reply 4); Year 1 £9.16m, Year 2 £9.31m, £18.48m total; September to November 36% of Year 1 and 38% of Year 2; November peak 2.7x and 3.0x the weakest month | Yes: `monthly-net-revenue`, `seasonality`, `revenue-reconciliation` | **Exact match.** All 24 months agree to the £k; Year 1 £9,161,996, Year 2 £9,314,080, total £18,476,076 to the pound; Sep-Nov 36.25% and 38.14% |
| 2. Top-10% share and no-ID revenue | Top 10% of identified customers (592 of 5,914) bring 64% of identified revenue and 55% of total; £2.47m (13.4%) has no customer ID | Yes: `customer-concentration` | **Match.** 5,914 identified customers, top 592; 63.6% of identified revenue, 55.05% of total; no-ID £2,474,931 (13.4%) |
| 3. 90-day repeat by 2010 first-purchase month | All 12 cohorts shown (reply 4): 52% (Jan) to 30% (Nov) for Jan-Nov, December 16% of 76; follow-up complete for every cohort | Yes: `repeat-within-90-days`, `december-2010-coverage` | **Exact match** on all 12 cohort sizes, repeaters and rates when a purchase is a non-cancelled invoice with a product line of positive quantity and price (the agent's query definition). Counting any non-cancelled line instead moves the January cohort from 368 to 383 and rates by at most 1.3 points; the released methodology note does not state the product-line restriction (finding retail-B-24) |
| 4. Highest cancellation rate among meaningful products | 1,720 products with at least £2,000 of sales before cancellations; median 1%; medium ceramic top storage jar 95% (almost all one cancelled order), pantry chopping board 83%, cherry lights 36-56% | Yes: `product-cancellation-rate` | **Match.** 1,720 products, median 0.01; stock code 23166 at 95.1%, 23113 at 82.7% |
| 5. Overseas growth, Year 1 to Year 2 | Australia +£108k (97%, £104k, from one account), France +£66k (45 to 86 customers), Norway +£32k and Japan +£31k (small bases), Germany +£23k; EIRE fell most (-£91k) | Yes: `overseas-growth` | **Match.** Australia +£107,643 with the largest account at £104,182 (96.8%); France +£65,848, 45 to 86 identified customers; Norway, Japan, Germany and EIRE agree |

## Timeline

| Phase | Messages | Time (UTC) | Notes |
|---|---|---|---|
| Init | msg 1 / reply 1 | 11:18-11:19 | awb-init, `setup` MCP first try, project venv, git; first scoping round of four definitions in the same turn |
| Scoping | msg 2 / reply 2 (start) | 11:19-11:21 | User settled all definitions plus the next round's choices in one message; brief, questions and settings written |
| Landing | reply 2 | ~11:21-11:24 | Fetch callable + `retain` (copy to storage) + `publish` with 20 checks passing |
| Cleaning | reply 2, msg 3 | ~11:24-11:27 | `clean-scan`; agent removed the 22,523 cross-sheet duplicates itself and asked about 11,812 within-invoice repeats and a small-base threshold |
| Exploring and answering | reply 3 | 11:28-11:33 | Seven `run.py` results, all supported; agent added an account-concentration check after seeing Australia lead; headline preview written |
| Status | msg 4 / reply 4 | 11:34-11:36 | awb-status plus the user's checks (December cohort coverage, full tables, Australia attribution); wording revised |
| Packaging | msg 5 / reply 5 | 11:36-11:48 | Full draft, full review (15 problems) then scoped review (clean); 16-word headline left for the user |
| Review and corrections | msg 6 / reply 6 | 11:48-11:53 | Reconciliation table restored, cohort wording fixed, three review rules added; two scoped reviews; one pre-existing internal citation problem escalated to the user |
| Release | msg 7 / reply 7 | 11:53-11:55 | Citation fixed, scoped review clean, `release` froze 001 and copied it to storage |
| Close | msg 8 | 11:55 | DONE |

## Package review loop (the extra check for this run)

From `python3 KIT/reviewloop.py SIMS/retail-B`: packaging turns took 24 of 36 agent minutes (66%); time from the first review start to turn end, summed, was 10.6 min (29%).

| Request | Review rounds | Outcome per round | User wait |
|---|---|---|---|
| msg 5: build the full draft (awb-package) | 2 (full, scoped) | Full: 15 narrative problems, all repaired. Scoped: clean | 11.7 min (11:36:34 to 11:48:14) |
| msg 6: two corrections, review rules | 2 (scoped, scoped) | 3 problems repaired; then 1 problem marked "unchanged since prior review", taken to the user instead of repaired | 4.8 min (11:48:35 to 11:53:20) |
| msg 7: fix the citation and release (awb-release) | 1 (scoped) | Clean; release ran in the same turn | 1.7 min (11:53:33 to 11:55:12) |

**Verdict: no perfectionism loop.** No request ran more than two review rounds; each turn ended either clean or by handing a residual problem to the user. Total review work was 5 rounds and the user waited 18.1 min in total across the three packaging and release requests. The remaining overhead is two approval gates created by mechanical rules rather than by iteration:

1. A 16-word headline (one over the 15-word limit) that the user had already approved at the preview stage became a decision in reply 5, because the preview step does not count words.
2. A wrong evidence citation in the internal-only `methodology.md` was escalated in reply 6 under the "unchanged since prior review, take it to the user" rule. The user called this the clearest unnecessary gate. It cost no extra message, because the user's next message asked for the release anyway, but it held back the "checks pass" confirmation the user had asked for in message 6.

## Pain points observed by the referee

| # | Issue | Messages | Severity |
|---|---|---|---|
| 1 | Agent removed 22,523 cross-sheet rows before asking. The README says the user decides unless the source confirms re-extraction; the awb-clean skill let the agent decide. The removal was correct (verified), but the user lost trust and asked to be consulted in future | reply 2, msg 3 | major |
| 2 | Explanations offered as facts before any review: "not product demand", "Christmas closure", early cohorts "push their repeat rates up", "lean the budget towards retention". The user caught each one; the independent reviewer only runs at draft time, so the headline preview and chat answers are not checked | replies 3-4, msgs 4-5 | major |
| 3 | The imperative-sentence rule collided with the user's explicit request for a recommendation; the released Answer headline reads "Recommendation: protecting key accounts, testing retention alongside acquisition; ..." | reply 5, released `findings.md` | major |
| 4 | Two rule-driven approval gates at the end (word count, internal citation); see the review-loop section | replies 5-6 | minor |
| 5 | First answers gave ranges and highlights instead of the complete monthly and cohort tables the questions ask for | reply 3, msg 4 | minor |
| 6 | Agreed reconciliation table turned into a bar chart in the draft | reply 5, msg 6 | minor |
| 7 | First recommended net-revenue definition (products only) did not fit a company-total question | reply 1, msg 2 | minor |
| 8 | Floating-point gap (-4.4e-06) made "equals the total exactly" fail review; `state.md` still says "reconciliation_gap 0" for customer concentration | reply 5 | minor |
| 9 | Cohort purchase definition narrower than stated (product lines, positive quantity and price), not disclosed in the methodology note | released `methodology-note.md` | minor |
| 10 | Review rules cannot be scoped to an investigation; agent chose "every package" | reply 6 | minor |
| 11 | Codex user leaked a preamble line into message 1 ("I'll read BRIEF.md and README.md, then follow the simulation's response format.") | msg 1 | minor (harness) |
| 12 | Claude Code kept its session files under the real home; a review subagent read a tool-result spill file there | agent-006 | minor (harness) |

No errors, stalls, unsupported numbers or skill misuse beyond the above. All five answers are correct against the source data.

## Isolation audit

- **Agent (Claude) logs**, `SIMS/retail-B/relay/agent-*.jsonl` through `logview.py --full`, with the simulation prefix masked: no reads of `workbench-spec`, `workbench-design`, `CONTEXT.md`, any `docs/` folder, the analytics-workbench repository, `SIMS/retail-B/human`, `SIMS/retail-B/relay` or `transcript.md`. Every awb MCP `data`/`read` SQL statement reads only project files. Hits:
  - agent-001: `ls -a ..` listed the simulation folder, which shows the names `human/`, `relay/` and `transcript.md`; the follow-up `ls ../..` was piped into a failing `head -0` and printed nothing. A directory listing only, no reads. Did not matter.
  - agent-006: a scoped-review subagent read a file under the real home directory, Claude Code's own spill file for one of its oversized Grep results (`~/.claude/projects/<session>/tool-results/...`). The content was its own grep of the draft. Did not matter for the result. It shows the agent's Claude Code session state lives in the real home (harness).
  - agent-001 created the project venv with a system interpreter outside the simulation folder (not under the real home). Did not matter.
- **User (Codex) logs**, `SIMS/retail-B/relay/human-*.jsonl`: read only `BRIEF.md`, `README.md`, the headline preview, the four draft files the agent pointed to, dataset CSV heads, the released folder's `START-HERE.md`, and its own `notes.md`. One `rg --files -g AGENTS.md` in its own folder (a file-name search with no match, not a read). No reads of `AGENTS.md`, `SKILL.md`, `src/`, `.py` files, `workbench-guides/` or agent homes. Did not matter.

## Identity check

- Git history of `SIMS/retail-B/project`: 10 commits, all authored and committed by the simulated identity with the `analyst@example.com` address. No other author.
- No absolute path under the real home directory anywhere in the project (including the venv and git history) or in storage.
- The real account name does appear inside the scratchpad directory name, which encodes the real home path. The user's message 1 supplied the storage folders as absolute paths, and the agent recorded them in `project/README.md` (storage lines) and `project/foundation/sources.md` (retained-copy column), both committed. Harness cause: the simulation folder's name.
- One third-party email address is in the saved public UCI dataset page (`project/foundation/references/uci-online-retail-ii/uci-dataset-page.html`): the dataset's published contact, not the user's.

## Satisfaction

The user rated the run **8/10** (`SIMS/retail-B/feedback/human.md`). They would use it again. They valued the account-concentration check on overseas growth most, and want uncertain data changes brought to them first, claims kept within the evidence, and routine repairs made without a permission round.

## Most important issues for the maintainers, ranked

1. **Plausible explanations reach the user as facts before any review** (retail-B-02). The independent reviewer catches overclaims only at draft time; the headline preview and the answer messages that the user approves go unchecked. Apply the reviewer's evidence and claim rules, or a light version of them, to the headline preview.
2. **The README and awb-clean disagree on who decides cross-sheet duplicates** (retail-B-01). Require source documentation before the agent removes overlapping rows itself, or change the README.
3. **Review rules force worse prose into the deliverable** (retail-B-03). Exempt a labelled recommendation on the Answer slide from the imperative rule when the user asks for one.
4. **Rule-driven approval gates at the end of packaging** (retail-B-04, retail-B-05). Let the agent repair citation-only problems in internal files and report them; run the word count at the preview stage.
5. **Packaging output volume and the commit, rerun, re-export sequence** (retail-B-17, retail-B-18). The review loop no longer spirals, but packaging is still 66% of agent time.
6. **Smaller record-keeping gaps:** joins "not assessed" noise, review-rule scope, a tolerance path for money sums, duplicate-issue granularity (retail-B-08, -10, -11, -14).
