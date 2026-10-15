# Orchestrator report: co2-B

## Run facts

- **Variant:** B. The human (Sam Whitfield, research lead, Carbon Ledger Initiative) was played by Codex through `simctl.py` (session `01a13f92-fb0b-7661-860d-60d9c84dea60`). The agent was played by Claude Opus as the nested subagent `co2-B-agent`.
- **Dataset:** OWID CO2 (`owid-co2-data.csv` plus the codebook), downloaded 2026-10-15.
- **Start:** 2026-10-15 08:39 EDT. **End of conversation:** 09:48 EDT, when the human sent STATUS: DONE. **End of feedback and verification:** about 09:55 EDT.
- **Wall-clock:** about 1 h 10 min of conversation and about 1 h 16 min in total. Both caps (45 messages, 8 hours) were far away.
- **Turns:** 7 human messages and 6 agent replies in the conversation. After that came 1 human feedback turn, 1 agent feedback turn, and 1 isolation question to the agent.
- **Approximate agent turn durations:**

  | Turn | What it did | Time |
  |---|---|---|
  | T1 | init and scoping | 4 min |
  | T2 | landing and all five answers | 6.5 min |
  | T3 | status and headline checkpoint | 4.5 min |
  | T4 | full draft, four internal review rounds | about 23 min |
  | T5 | revision | about 9 min |
  | T6 | release | about 7 min |

- **Fallback:** not used. Nested spawning and SendMessage worked for every turn.
- **Protocol incidents:** none. No harness notes were needed during the conversation.

## End-point checklist

| Criterion | Met? | Evidence |
|---|---|---|
| All five questions answered specifically and accepted by the user | Met | Agent T2 (`relay/agent-002.out.md`); human acceptance in H6 ("I accept all five answers with the documented caveats"). Ledger `project/investigations/program-country-focus/questions.md`: Q-009 to Q-013 are all `answered`, each linked to an evidence file. `findings.json` has 12 findings, all `supported`. |
| User asked where things stand at least once | Met | H3 "Use awb-status — where are we?" The answer is in `relay/agent-003.out.md`. |
| Package draft exists and was reviewed by the user | Met | `project/deliveries/program-country-focus/donor-country-focus/draft/` holds `findings.md`, `methodology.md`, 5 charts and 9 datasets. The human read findings.md and methodology.md (H5, confirmed in `relay/human-005.log`) and asked for 5 corrections, all applied in T5. |
| Released as 001 and copied to the releases folder | Met | Project copy: `project/deliveries/.../released/001/`. Storage copy: `storage/releases/program-country-focus/donor-country-focus/released/001/`, 19 files. I ran `diff -r` between them: identical. The released `manifest.json` has status `release`. |
| Landed data kept in the agreed location | Met | `storage/landed/data/raw/owid-co2/2026-10-15/` holds the data CSV, the codebook and `provenance.json`. `cmp` against the project's raw copy: identical. |
| Analysis committed | Met | 13 commits in `project/` with a clean tree; `bcab5ff` is the last. |

## The five questions

| # | Agent's final answer (T2, carried into release 001) | Recorded? | My spot-check (duckdb on the landed CSV) |
|---|---|---|---|
| 1 | **Increases, 2000→2024:** China +8,645 Mt, India +2,206, Indonesia +531, Iran +425, Saudi Arabia +382, Vietnam +317, Russia +300, Turkey +280, Malaysia +167, Iraq +150. **Decreases:** US −1,119, Germany −327, Japan −298, UK −256, Italy −168, France −143, Ukraine −143, Spain −89, Netherlands −57, Czechia −52. | Yes: result `co2-change-since-2000`, plus the full 216-country ranking | **Exact match** for all 20 countries and values. I used 3-letter ISO codes as the country filter; Kosovo, which has an OWID_ code, makes no difference. |
| 2 | 45 of the 164 countries with both measures had CO2 down and GDP up, 2005→2022. Largest by 2022 emissions: US (5,055 Mt), Japan, Germany, Canada, Mexico, Australia, Italy, Poland, UK, France. | Yes: `decoupling-since-2005` and `-top10` | **Exact match**: 45/164, the same top 10 in the same order, and the same % changes (e.g. Australia −0.3% CO2 / +60.0% GDP; Mexico −2.1% / +42.5%). |
| 3 | 2023, tonnes per person, consumption vs territorial: US 15.8 vs 14.3; EU-27 7.3 vs 5.5; China 7.6 vs 8.6; India 1.8 vs 2.1. | Yes: `consumption-vs-territorial` | **Exact match**: 15.81/14.32, 7.33/5.51, 7.63/8.56, 1.77/2.13. |
| 4 | Share of World CO2, 1850–2024: US 23.6%, EU-27 16.3%, China 15.5%, India 3.6%; together 58.9%. Final version adds coverage: China's data start in 1907 (57 missing years) and India's in 1858 (19 missing). Upper bounds +2.9 and +0.5 points. | Yes: `cumulative-share-since-1850` | **Exact match**: 23.57 / 16.27 / 15.46 / 3.58. Missing years confirmed (China first year 1907 with 57 missing; India 1858 with 19 missing; US and EU complete). China's bound recomputed as 2.94 points. |
| 5 | Coal share 2010→2024 among countries over 50 Mt in 2010 (59 with coal data): Greece 42.4%→9.0% (−33.3 pts), Romania −23.1, Israel −22.0, Poland −19.5, US −19.4, Finland −19.3, Czechia −18.0, UK −17.6, Hungary −13.5, Germany −12.9. Libya excluded (no coal data). | Yes: `coal-share-since-2010` and `-top10` | **Exact match** on order and values. |

I also checked the reconciliation correction. Kuwaiti Oil Fires (GCP) is 477.9 Mt in 1991, against Kuwait's 493.0 Mt, which already includes it. That confirms the agent's corrected statement.

**No numerical discrepancies were found.** The only substantive error in the session was the narrative reconciliation claim. It contained no ranking or share figure, and it was corrected in T5 (see pain point 1).

## Timeline of phases

| Phase | Turns | Notes |
|---|---|---|
| Init | H1 → T1 | Covered git init, the helper install, `.venv` via uv (the printed pip hint failed), AGENTS.md, the source register and the brief. Optional MCP registration was offered. |
| Scoping | T1 → H2 | The agent opened 15 ledger questions, put 4 decisions to the user and deferred 3 method choices. The user settled all 7 in H2. |
| Landing | T2 | Fetched, retained to `storage/landed/` and published canonical views with a custom check. The check found that Namibia 1990 has consumption CO2 but no territorial CO2 (QI-001). |
| Cleaning | (T2, implicit) | **`awb-clean` was never invoked.** Quality rows QI-001 to QI-004 were written during publishing and analysis, not through a clean scan. |
| Exploring | (T2, implicit) | **`awb-explore` was never invoked.** The agent went straight from publishing to `run.py` results. |
| Answering | T2 | All five answers came in one turn, with years stated and caveats on Russia, Ukraine, marginal decouplers and Libya. |
| Status | H3 → T3 | Status was combined with a stand-out-rule revision and the start of packaging. |
| Packaging | T3 (headline checkpoint), T4 (full draft) | The template's mandatory slides raised the deck from 8 to 12 slides; the user resolved this as 8 plus a 4-slide appendix. T4 went through four internal reviewer rounds. |
| Review | H5 → T5 | The user's review exposed a false reconciliation claim and a materiality claim with no support. Both were fixed, and coverage bounds were added. |
| Release | H6 → T6 | A small revision (a ninth dataset and a column rename) was folded into the release turn. Release 001 was frozen and copied, with all 19 files verified. |

## Pain points observed as referee

1. **A validation claim based on a sample was promoted and survived review. Major** (T2 to T5).
   - What happened: `methodology.md` and the `entity-classification` finding said that country totals plus non-country entries equal World. It had been checked in only six years.
   - Why it slipped through: it passed every automated check, was promoted to `supported`, and passed four fresh reviewer rounds in T4.
   - How it was caught: only the human's question in H5 exposed it, revealing a 478 Mt double count in 1991. The agent's own feedback ranks this first.
   - Gap: neither the validation judgments nor the reviewer checks whether a "checked" assertion is backed by a recorded result.
2. **The clean and explore phases were skipped entirely. Major as a coverage gap** (T2).
   - The user asked to "proceed with the download, data checks and analysis".
   - The agent did data checks inside `publish` and went straight to results. It never invoked `awb-clean` or `awb-explore`, and never offered them.
   - The answers were correct, so in this dataset the omission did no harm. Still, two of the eight skills went unexercised. Nothing in the flow nudged the user or the agent toward them.
3. **Repeated approval gates and a long T4. Major for the user's experience** (H3, T3, T4).
   - The user asked for a draft in H3 and received headlines plus an approval request, with no files to review.
   - The full draft then took about 23 minutes, much of it on reviewer loops. Four rounds were needed, mostly because of a review rule the agent wrote itself and the reviewer applied to every bullet.
   - The human ranked "repeated gates before I could see a draft" as its second pain point.
4. **The package template's slide count overrode the user's budget. Minor to major** (T3).
   - The mandatory Implications, How we know, Limitations and Supporting datasets slides made an 8-slide request into 12. The format has no appendix concept.
   - The appendix was first marked only in speaker notes, so the user had to ask for visible "Appendix:" headings (H5).
5. **Inaccurate claims about attachments. Minor** (T4 and T5).
   - The agent wrote "I've also sent it to you as an attachment" and "I've attached both narratives again". No attachment channel exists in the host.
   - The user did not notice, but it is an unsupported claim about the agent's own actions.
6. **Jargon and plumbing in user-facing replies. Minor** (T1 and T3).
   - T1 was a long setup report covering venv, uv, git, helpers, receipts and MCP registration.
   - T3 pointed the research lead at a `.sql` file to review classification. The user pushed back in H2 and H4.
7. **The release turn included unreviewed changes. Minor** (T6).
   - The user asked for a ninth dataset and the release in the same message. The agent revised the draft, renamed a result column to fix a label collision in `display.toml`, re-reviewed internally and froze release 001.
   - The user never saw the final draft before it was frozen. It is defensible, since the user asked for both, but the release skill could flag that the revision has not been reviewed.
8. **Isolation. Minor; no breach found.**
   - The agent says it read only allowed paths. Two edge cases:
     - It ran existence-only `test -e` checks for CLAUDE.md and AGENTS.md in every ancestor directory up to `/`, per awb-init step 1.3. That is outside its bounds, but no contents were read.
     - It spawned 7 `Plan`-type reviewer subagents. They have Bash, and their scope was limited only by their briefs, so I cannot verify that they stayed in bounds.
   - The Codex human's logs show reads of only the README and BRIEF, the draft `findings.md` and `methodology.md`, `charts/chart-4.csv` and `datasets/q4-cumulative-shares.csv`. All are user-facing.
   - Neither role quoted internals it could not have known.
9. **Mechanical friction the agent reported** (from `agent.md`):
   - Global parameters and commit-driven reruns made every finding provisional again, which forced repeated re-promotion.
   - `display.toml` labels are global per column name and silently mislabeled a dataset.
   - Charts cannot filter rows, so the agent had to build extra top-10 results.
   - The pip hint printed by the installer fails in a uv venv.
   - AGENTS.md and the guides hardcode `python3`.
   - `state next --drop 1 --drop 1` silently dropped only one item.

## Most important issues for maintainers, ranked

1. **Make validation and review check substance, not just form.**
   - Require any "checked" or reconciliation assertion in a judgment or narrative to trace to a recorded result. Ideally `state finding --status supported` warns when a judgment cites years or figures that appear in no result.
   - Have the reviewer challenge full-period claims and missing-versus-zero handling.
   - In this run, every mechanical gate and four reviewers missed an error that a non-technical user found.
2. **Clean and explore are easy to skip.**
   - When asked to "check and analyze", the agent folded quality checks into `publish` and never ran `awb-clean` or `awb-explore`.
   - Either make awb-scope or the run flow propose them before answering (at least a single scan), or say clearly in the README and AGENTS.md when they are optional.
3. **Reconcile the package format with the user's slide budget, and reduce gating before the first draft.**
   - Add an appendix marker to the outline format and deck rules.
   - Have the headline checkpoint raise any conflict with the slide count.
   - Consider writing the full draft with the headlines marked provisional, so a user who asked for "the draft" gets files in one turn.
   - Cut review-loop churn by giving review rules a scope (slide, bullet or document).
4. **Stop needless re-promotion and churn.**
   - Limit staleness to the parameters each result reads.
   - Treat a rerun of the same table at a commit as `kept`.
   - Allow per-result display labels.
   - Allow row-limited chart exports.
5. **Make first-run setup smoother and plainer.**
   - Fix the installer's pip hint for uv venvs.
   - Template the interpreter into AGENTS.md.
   - Steer the agent to keep setup detail and SQL pointers out of user-facing messages: the README, the skills, or both should say that a non-technical user needs a short readiness summary.
6. **Prevent unsupported claims about the agent's own actions** ("attached"). A line in awb-package's reporting instructions would cover it: say where the files are; never claim to attach them.

## Files

- **Transcript:** `transcript.md`
- **Human feedback:** `feedback/human.md` (copied from `human/feedback.md`). Satisfaction 7/10.
- **Agent feedback:** `feedback/agent.md`
- **Agent friction log:** `feedback/agent-notes.md`
- **Relay files:** `relay/`
  - `to-agent-NNN.md` and `agent-NNN.out.md`: Opus agent turns.
  - `human-NNN.{in,out}.md` and `human-NNN.log`: Codex human turns.
