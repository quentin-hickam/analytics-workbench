# Referee report: co2-B (2026-10-17 re-run)

`SIMS` is the simulation root and `SIMDIR` is `SIMS/co2-B`. Message numbers: U*n* is user message *n* and A*n* is agent reply *n*, both from `SIMDIR/transcript.md`.

## Run

| | |
|---|---|
| Run / variant | co2-B, variant **B**: Codex plays the user (Sam Whitfield, a research lead at a climate nonprofit); Claude (Opus, headless `claude -p`) plays the agent, with the awb skills discovered through `--add-dir` |
| Dataset | Our World in Data CO2 CSV and codebook, fetched by URL |
| Relay | Started by the orchestrator at 2026-10-17T11:17:43Z. The conversation ended DONE at 11:48:53Z, and the relay finished at 11:50:34Z after the feedback turns. `relay.log` is empty, and nothing died or restarted |
| Wall-clock | **31.2 min** from relay start to DONE, 32.9 min including feedback |
| User messages | 7. Six were delivered and answered; the seventh was the DONE message, which is never relayed |
| Agent replies | 6, plus 1 feedback turn (7 agent turns in `state.json`) |
| Agent cost | $11.67 in total ($11.37 for the conversation, $0.30 for feedback) |
| Permission prompts | 0. `SIMDIR/relay/permission-prompts.jsonl` was never created, because every tool the agent used was pre-allowed |
| Satisfaction (user) | **8/10** |

Compared with the Oct 16 co2-B run (from `SIMS/oct16-ref`): 142.9 min fell to 31.2 min, 9 user messages to 7, 8 agent replies to 6, $48.38 to $11.67, 38 full reviews to 1 full review plus 4 scoped ones, and satisfaction rose from 7 to 8.

## End-point checklist (from `SIMDIR/human/BRIEF.md`)

| Criterion | Met | Evidence |
|---|---|---|
| All five answers accepted | Yes | In U4 the user said: "I accept the five quantitative answers with those qualifications". U7 accepted them again. `project/investigations/co2-emissions-change/questions.md` shows Q-001 to Q-005 answered, each linked to an evidence file. `findings.json` shows all six findings `supported` with claim `descriptive`. Q-006 (the Ukraine follow-up) is still open at priority "could", and the user asked that it stay untested |
| Asked where things stand | Yes | U3 said "Use awb-status — where are we?". In A3 the agent loaded the `awb-status` skill (`relay/agent-003.jsonl`) and replied under "Where we are" |
| Draft reviewed by the user | Yes | The user's log shows it read `draft/findings.md` and `draft/methodology-note.md` in U5 (`relay/human-005.jsonl`), and `START-HERE.md` plus the revised `findings.md` passages in U6 (`relay/human-006.jsonl`). Corrections were requested in U4 and U5 |
| Released as 001 and copied to storage | Yes | `project/deliveries/co2-emissions-change/donor-deck/released/001/` and `SIMDIR/storage/releases/co2-emissions-change/donor-deck/001/` are identical (`diff -r` is clean, 15 files). The landed originals under `SIMDIR/storage/landed/` are identical to `project/data/raw/`. The user opened `START-HERE.md` in the releases folder in U7 |

**End point met.**

## The five questions

Spot-checks are my own read-only DuckDB queries on `SIMDIR/storage/landed/data/raw/owid-co2/2026-10-17/owid-co2-data.csv` (scripts in `SIMDIR/referee/spotcheck.py` and `spot_q3.py`, run with the project's own `.venv`). I spot-checked all five answers, not just two. Countries were defined as entities with an ISO code, plus Kosovo, minus Antarctica, as the agent disclosed.

| Q | Agent's final answer | Recorded result | Spot-check |
|---|---|---|---|
| 1 | 2000 to 2024, 215 countries ranked. Largest increases: China +8,645 Mt, India +2,206, Indonesia +531, Iran +425, Saudi Arabia +382, Vietnam +317, Russia +300, Turkey +280, Malaysia +167, Iraq +150. Largest decreases: US −1,119, Germany −327, Japan −298, UK −256, Italy −168, France −143, Ukraine −143, Spain −89, Netherlands −57, Czechia −52 | `results/q1-change-since-2000.csv`, plus `q1-full-ranking.csv` for the 215-country dataset | **Exact match**: all 20 countries, their order and their values; 215 countries ranked; 218 entities with an ISO code |
| 2 | 45 countries had lower CO2 and higher GDP in 2022 than in 2005 (2022 is GDP's latest year). Largest by 2022 CO2: US 5,055 Mt, Japan, Germany, Canada, Mexico, Australia, Italy, Poland, UK, France. Seven fell by less than 5% (Canada, Mexico, Australia, Poland, Uzbekistan, Belarus, Trinidad and Tobago) | `results/q2-decoupling-since-2005.csv` | **Exact match**: the count of 45 and the top 10 in order; the latest GDP year is 2022 |
| 3 | 2023, tonnes per person, territorial vs consumption-based: US 14.32 vs 15.81 (+10%), EU-27 5.51 vs 7.33 (+33%), China 8.56 vs 7.63 (−11%), India 2.13 vs 1.77 (−17%) | `results/q3-consumption-vs-territorial.csv` | **Exact match**. I also confirmed that 2023 is the right year: in 2024 only World and the two international bunker rows carry consumption CO2, and 120 countries do in 2023, which matches the agent's "120 countries" |
| 4 | Shares of reported cumulative CO2 from 1850 to 2024, with OWID World (which includes international aviation and shipping) as the base: US 23.6%, EU-27 16.3%, China 15.5%, India 3.6%, with 41.1% for other countries plus bunkers. China's data starts in 1907 and India's in 1858; the illustrative gap scenario moves China's share from 15.46% to 15.51% | `results/q4-cumulative-shares.csv` | **Exact match** (23.57 / 16.27 / 15.46 / 3.58%; World 1,844,551 Mt). First reported years confirmed as 1907 and 1858 |
| 5 | 60 countries were eligible (at least 50 Mt in 2010) and 59 were analyzed; Libya has no coal data. Largest falls in coal's share of CO2, 2010 to 2024, in percentage points: Greece −33.3, Romania −23.1, Israel −22.0, Poland −19.5, US −19.4, Finland −19.3, Czechia −18.0, UK −17.6, Hungary −13.5, Germany −12.9 | `results/q5-coal-share-decline.csv` | **Exact match**: 60 eligible, 59 analyzed, Libya the only one without coal data, and the top 10 with the same values |

## Timeline

| Phase | Messages | Time | Notes |
|---|---|---|---|
| Init and scope, round 1 | U1 → A1 | 11:18 → 11:20 (1.9 min) | `awb-init` then `awb-scope` in the same reply. Four method decisions, each with a recommendation. The agent peeked at the codebook to ground them |
| Scoping answers | U2 | 11:20 | The user accepted all four recommendations and pre-empted the announced second round |
| Landing, publishing, coverage checks, exploring, answering | A2 | 11:20 → 11:27 (7.4 min) | `land()` plus `data retain` copied the files to storage; `publish` ran 15 checks; `awb-explore` ran the EDA scan and three coverage queries; `run.py` produced five results with no failed checks. No `awb-clean` skill was invoked: coverage and missing-value checks went through `awb-explore` and `foundation/quality.md` |
| Status, corrections, headline preview | U3 → A3 | 11:28 → 11:31 (3.8 min) | `awb-status`; complete tables; the early-gap wording fixed; coal counts clarified; `awb-package` preview of 8 main and 3 appendix slides |
| Approval and full draft | U4 → A4 | 11:32 → 11:42 (10.2 min) | Draft, export, a full review (9 problems), repairs, a scoped review (7 problems), then a stop with three decisions for the user |
| Review decisions and final checks | U5 → A5 | 11:42 → 11:47 (4.6 min) | Two review rules added; a scoped review (3 rule violations and 3 narrative problems), repairs, a scoped review (clean); writing check-draft passed and wrote `START-HERE.md` |
| Release | U6 → A6 | 11:47 → 11:48 (1.4 min) | Energy-mix rule added, then a scoped review (clean), verify-only check, and release 001 copied to storage and verified. No commit, as the user asked |
| Done | U7 | 11:48:53 | |

The user's turns took 0.2 to 0.4 min each, so almost all of the 31 minutes was agent time.

## Package review loop: still stuck in a perfectionism loop?

Source: `python3 SIMS/kit/reviewloop.py SIMS/co2-B`, plus the review reports recorded in `relay/agent-004.jsonl` to `agent-006.jsonl`.

| Request | User waited | Review rounds | Reviewer subagents | check-draft runs | Review tail | Outcome |
|---|---|---|---|---|---|---|
| U3: headline preview | 3.8 min | 0 | 0 | 0 | 0 | Preview shown; no review at this stage |
| U4: full draft | **10.2 min** | 2 (1 full, 1 scoped) | 2 | 4 | 5.1 min | Full review: 9 narrative problems. Scoped review: 7. Stopped by the two-review cap with 3 decisions for the user |
| U5: corrections and final checks | 4.6 min | 2 (both scoped) | 2 | 4 | 3.6 min | First: 3 rule violations (1 error) and 3 narrative problems. Second: clean |
| U6: release | 1.4 min | 1 (scoped) | 1 | 1 | 1.0 min | Clean on the first pass. The review ran only because the user's new rule changed `review-rules.md` |
| **Total** | **20.0 min** | **5** | **5** | **9** | **9.7 min** | |

The packaging turns (A3 to A6) took 21 of the 30 agent minutes (69%) and $8.52 of the $11.37 conversation cost (75%). The review-heavy turns (A4 to A6) cost $6.94. The reviewloop script also reports "starts=1" for the feedback turn (agent-007). That is a false positive from the text of `agent.md`, not a review.

**Verdict: not stuck.** Every request converged within the two-review cap. The last two review rounds were clean on their first pass, and release took 1.4 minutes. That is a large change from Oct 16, when this run made 38 full reviews in 129.5 of 142.9 minutes. Some over-strictness remains, and it cost one extra user decision round (U5) and about 5 minutes of review in the drafting turn:

1. **Churn over reconciliation wording.** 4 of the 9 first-round problems, and 4 of the 7 second-round problems, were about how to say that World equals countries plus international bunkers, or that the sums match OWID's `cumulative_co2`. The rules on recorded tolerances and on citing a check left no acceptable way to state an approximate match. The agent finally cited OWID's processing code and deleted useful context (`feedback/agent.md` pain point 1). Unlike Oct 16, it invented no tolerance.
2. **The reviewer flagged wording the user had approved.** "45 countries cut CO2" was the user's own wording from U4. The reviewer called it an agent-verb overclaim, and the cap sent it back to the user as a decision. The user called the cut-versus-fell question "disproportionate" (`feedback/human.md` pain point 2). The agent did offer to record the user's acceptance instead.
3. **An incomplete first pass created an extra round.** The A4 reviews flagged "cut" only in the headlines. The first A5 review then raised three more instances on slide 4 that had not changed since the earlier pass. The deck title, "Who has cut and who has grown CO2 emissions since 2000", passed every review even under the same logic.
4. **A rules-only change triggered another review before release.** It was cheap (1.0 min), but the user noted it as unexpected (`human/notes.md`, turn 7).
5. **The reviews missed what the user caught in one read.** "Energy mix" (for coal's share of CO2) passed both A4 reviews; the user caught it in U5.

## Pain points observed as referee

| # | Issue | Messages | Severity |
|---|---|---|---|
| 1 | The first answers described China's and India's missing early years as "count[ing] as zero". The fix in A3 then called the sensitivity calculation a "ceiling". The user caught both, and this class of error also appeared on Oct 15 and Oct 16 (Oct 16 C-20). The agent's coverage query had the first reported years at A2 | A2, U3, A3, U4 | major |
| 2 | Review churn over reconciliation wording and the escalation of user-approved wording (above) | A4, U5 | major |
| 3 | Meaning errors were left for the user to catch: "counting imports" without exports in the headline preview, and "energy mix" in a reviewed draft | A3, U4, A4, U5 | major |
| 4 | The first answers named rankings without values, and the coal eligibility count (59 or 60) was ambiguous | A2, U3 | minor |
| 5 | Interim narration and internal vocabulary reached the user: "That producer came out convoluted", an "unassessed join check", "promote", "mechanical checks", and a "spurious" warning about the number 2 | A2, A4, A6 | minor |
| 6 | The agent decided some exclusions itself (Antarctica out, Kosovo in, Libya out) and chose the Q3 matched year before asking, then disclosed each. The user accepted all of them | A2 | minor |
| 7 | Commit talk in five of six replies: two suggestions to commit (A2, A5) and three status mentions (A1, A3, A6). Release 001 was frozen from a repository with no commits, because the user declined one | A1–A6 | minor |
| 8 | The agent wrote the OWID processing code to system `/tmp` (outside the simulation's bounds) and then moved it into the project. It also ran `git add -A` out of habit, then reset it | A3, A2 | minor (harness) |
| 9 | The Codex user's preamble ("I'll read BRIEF.md and README.md, then follow the simulation's response format.") was relayed as the first line of U1. The agent ignored it | U1 | minor (harness) |

There were no tool failures, MCP failures or stalls. Helper use was mostly over MCP: 57 awb MCP calls against 13 main-thread Bash calls to `src/awb.py` or `run.py` (Oct 16: 32 against 83). Skills used: `awb-init`, `awb-scope`, `awb-explore`, `awb-status`, `awb-package`, `awb-release`.

## Isolation audit

**Agent logs.** I rendered `relay/agent-001.jsonl` to `agent-007.jsonl` with `logview.py --full` (copies in `SIMDIR/referee/`) and searched every tool input, subagent calls included:

- No reads of `workbench-spec`, `workbench-design`, `CONTEXT.md`, any `docs/` folder, any analytics-workbench repository path, `SIMDIR/human`, `SIMDIR/relay` or `transcript.md`.
- No tool input names any path under the real home directory, and no Claude Code spill files were read.
- The awb MCP SQL read files only inside the project: the landed CSV under `data/raw/` and the published Parquet.
- The reviewer subagents read only the skill's `references/review.md` in the simulated home, plus project files.

Edge cases, none of which exposed study contents:

- **A1:** an `ls` of `SIMDIR/feedback` showed the file name `harness-log.md`. The file was never opened.
- **A1:** a throwaway `awk` addressed `$HOME/../agent-home/...` with its output sent to `/dev/null`. It was harmless and was followed by the correct simulated-home path.
- **A3:** the agent wrote `/tmp/claude-gcb-garden.py`, a public OWID file fetched from GitHub, outside the allowed folders. It moved the file into `foundation/references/owid-co2/` in the next call and disclosed the slip itself. This does not matter for the study.
- The agent only ever appended to `feedback/agent-notes.md`, which it was allowed to do.

**User logs.** The user's reads, from `relay/human-*.jsonl`, were:

- `SIMDIR/human/BRIEF.md` and `README.md` in U1;
- `draft/findings.md` and `draft/methodology-note.md` in U5;
- `draft/START-HERE.md` and selected lines of `draft/findings.md` in U6;
- `storage/releases/.../001/START-HERE.md` in U7;
- its own `notes.md`.

It read no `AGENTS.md`, `SKILL.md`, `src/`, `.py` file, `workbench-guides/` file or agent home. **The user side is clean.**

## Identity check

- `git log --all` in the project returned nothing, because the repository has no commits (the user declined one). Its local `.git/config` has no identity. The simulated home's `.gitconfig` holds only the placeholder name and the `example.com` address.
- **Project files and storage:** no real person's name as text, no email other than the placeholder (one binary false positive inside the Parquet file), and no path under the real home directory.
- One exposure: the storage locations recorded in `project/README.md` and `project/foundation/sources.md` (and in the copy of `sources.md` in `deliveries/.../review/snapshot/`) are the session scratchpad path. That directory's name encodes the real account's home path, including the account username.
  - The same string appears in `project/.venv` (`pyvenv.cfg`, the activate scripts, `.pyc` files) because the environment was created under that path.
  - `.venv/` and `deliveries/` are gitignored. `README.md` and `foundation/sources.md` are not, so a commit would have carried the account name.
  - The released package and `storage/releases/` contain none of it.
  - This comes from where the harness places the simulation (the persona brief gives those storage paths), not from the product.

## User satisfaction

8/10. The user said it would use the workbench again, especially for analysis that needs a clear record and repeatable delivery. It wanted less procedural chatter, and qualifications done properly in the first results report (`feedback/human.md`).

## Most important issues for maintainers, ranked

1. **Package review is still over-strict, though no longer runaway (co2-B-02, 03, 04, 06).** The reconciliation and tolerance rules leave no acceptable wording for an approximate match. Narrative findings against wording the user approved still go back to the user. A first review that covers only some instances of a pattern guarantees another round. The two-review cap bounds the cost, but it pushes trivial edits back to the user. Suggested fixes:
   - let an approved substitution apply to its sibling instances;
   - let the user accept wording, with a reason, at the headline checkpoint;
   - give a sanctioned way to state a post-hoc tolerance.
2. **The coverage-gap error recurred a third time (co2-B-01).** Missing early years were called zero, then the scenario was called a ceiling. Nothing in the analysis or explore flow prompts the agent to say how missing years enter a cumulative sum before it reports one.
3. **The reviews miss meaning errors the user catches (co2-B-05).** "Energy mix" for coal's share of CO2 passed both reviews of the drafting turn.
4. **First-pass answers fall short (co2-B-08), and narration reaches the user (co2-B-07).** Rankings came without values and denominators were ambiguous, which cost a follow-up round. Internal terms ("producer", "join check", "promotion", "mechanical checks") reached the user.
5. **Helper friction (co2-B-09 to 15).**
   - verify-only check-draft always reports failure before the first writing run;
   - export's own scale divisor fails the numbers check;
   - the preview file goes in a folder that does not exist yet;
   - new results default to `association`;
   - joins always come back `not_assessed`;
   - the EDA scan is noisy on panel data;
   - `review-rules add` gave a spurious number warning.

Improvements since Oct 16 that held in this run:

- MCP is now the main path for helpers.
- The preview file was not shipped inside the release.
- No tolerance was invented.
- The user's acceptance of wording can be recorded.
- Commit reminders are fewer, though they persist.

The full list is in `SIMDIR/feedback/findings.json`.
