# Orchestrator report: co2-A (variant A)

Variant A: Claude (Opus, headless `claude -p`) played the user, Sam Whitfield. Codex (`codex exec`) played the agent with the awb skills and the awb MCP server. Dataset: OWID CO2.

## Run facts

| Item | Value |
|---|---|
| Relay started | 2026-10-16T19:16:55Z. The referee started it; the state file was empty. |
| Conversation ended | 2026-10-16T20:07:22Z, outcome DONE |
| Relay finished | 2026-10-16T20:09:52Z, after both feedback turns |
| Wall-clock | 50.4 min of conversation, 52.9 min in total |
| User messages | 6 delivered (U1 to U6, each followed by an agent reply), plus the final DONE message U7, which the relay does not pass on. `state.json` counts 7 because it includes U7. |
| Agent replies | 6 conversational replies (A1 to A6), plus 1 feedback turn. `state.json` reports `agent_turns` 7. |
| User cost | $0.84 across 8 Claude sessions |
| Caps | 45 messages or 8 h. Neither was approached. |
| Relay health | No crash, no DEAD state, no harness restarts |

Sources: `relay/state.json`, `transcript.md`, `feedback/harness-log.md`.

## End-point checklist (from `human/BRIEF.md`)

| # | Criterion | Met | Evidence |
|---|---|---|---|
| 1 | All five questions have answers the user accepts | Yes | U4: "I accept the answers to all five questions" (`transcript.md`, line 238). `project/investigations/co2-country-priorities/questions.md` marks Q-001 to Q-005 as answered and links each to evidence JSON. `state.md` lists every finding as supported/descriptive, with none stale. |
| 2 | User asked where things stand at least once | Yes | U5: "use awb-status — where are we?" A5 answered with a five-part status report. |
| 3a | A package draft exists and the user reviewed it | Yes | A4 produced `deliveries/co2-country-priorities/donor-roundtable/draft/`: findings.md (8 main and 2 appendix slides), methodology-note.md, methodology.md, START-HERE.md, six chart CSVs and the assembly instructions. The user read findings.md, methodology-note.md, START-HERE.md, chart-3.csv and chart-6.csv (`relay/human-005.jsonl`), requested four corrections in U5, and checked them in the file. |
| 3b | Released as 001 and copied to `storage/releases/` | Yes | `project/deliveries/.../released/001/manifest.json` records status "release", release_number "001" and prior_release "none". `storage/releases/co2-country-priorities/donor-roundtable/001/` is byte-identical to it (`diff -r` was clean). The draft differs from the release only in the manifest's status and release fields. |

**End point met.** Every criterion is satisfied with evidence on disk.

## The five questions

All spot-checks are my own independent DuckDB queries, run read-only on the landed `storage/landed/data/raw/owid-co2/2026-10-16/owid-co2-data.csv`. Its SHA-256 matches the project's raw copy. Script: `referee/spotcheck.py`. My country definition was a 3-letter ISO code, plus Kosovo, minus Antarctica, giving 218 entities. I confirmed that Kosovo has no ISO code and that Antarctica has ATA, as the agent reported.

| Q | Agent's final answer | Backed by a recorded result | Referee spot-check |
|---|---|---|---|
| 1 | 2000 to 2024, 215 countries with both endpoints. Increases: China +8,645.2 Mt, India +2,206.4, Indonesia +531.2, Iran +425.4, Saudi Arabia +382.5, Vietnam +317.0, Russia +299.9, Turkey +280.1, Malaysia +167.3, Iraq +149.9. Decreases: US −1,119.0, Germany −326.7, Japan −298.3, UK −256.1, Italy −167.7, France −143.3, Ukraine −143.2, Spain −88.9, Netherlands −57.4, Czechia −51.6. Ukraine caveat: 47.6% of its fall came between 2021 and 2024, and only 0.542 Mt after 2022. | Yes: `territorial-change`, plus `ranking-groups` and `ukraine-timing` | **Matches exactly.** Both lists, all 2000 and 2024 values, n=215 with all endpoints in 2024, and Ukraine's 2000, 2021, 2022 and 2024 values. |
| 2 | 2005 to 2022 (GDP ends in 2022): 45 of 164 countries cut territorial CO2 while real GDP grew. Largest by 2022 emissions: US, Japan, Germany, then Canada, Mexico, Australia (−0.3%, flagged), Italy, Poland, UK and France. The UK made the largest cut among the ten: −45.5% CO2 with +21% GDP. | Yes: `gdp-and-emissions` | **Matches exactly.** 164 evaluated, all ending in 2022. 45 qualify. Same top ten in the same order. UK −45.5% and +21.0%. Australia −0.3%. |
| 3 | 2023, territorial vs consumption per person: US 14.319 vs 15.814, EU-27 5.514 vs 7.328, China 8.556 vs 7.632, India 2.130 vs 1.768 t. Consumption is higher for the US and EU-27 and lower for China and India. | Yes: `consumption-comparison`, plus `eu-reconciliation` | **Matches exactly.** All eight values agree, with a latest paired year of 2023 for all four. |
| 4 | Recorded 1850 to 2024 shares: US 23.57%, EU-27 16.27%, China 15.46%, India 3.58%. China's data starts in 1907 and India has 19 missing years. In an illustrative fill test, China's share rises 0.052 points and India's 0.0012, which is explicitly not a bound. World is the sum of national records plus bunkers, so it does not fill the gaps. | Yes: `cumulative-shares`, plus `historical-gap-sensitivity` and `world-gap-accounting` | **Matches exactly.** World 1850 to 2024 is 1,844,550.9 Mt. Shares are 23.567, 16.269, 15.456 and 3.582. China has 118 observations from 1907. India has 156, starting in 1858. I recomputed China's sensitivity at 15.508% (+0.052). The agent correctly avoided OWID's `cumulative_co2`, which includes pre-1850 years. |
| 5 | Of 60 countries at ≥50 Mt in 2010, 59 have coal data (Libya excluded). Greece's coal share fell fastest, from 42.38% to 9.04%: 33.34 points, or 2.382 per year. Then Romania 1.648, Israel 1.571, Poland 1.392, US 1.385, Finland 1.381, Czechia 1.289, UK 1.260, Hungary 0.966 and Germany 0.919. China is noted as a counterexample: its share fell while its coal CO2 rose by 2.32 Gt. | Yes: `coal-share-change` | **Matches exactly.** 60 at the threshold, 59 with coal data, Libya missing, all endpoints 2024. Same top ten with the same shares and rates. China's coal CO2 went from 6,569 to 8,886 Mt (+2.32 Gt). |

I found no wrong or unsupported number in chat or in the released outline.

## Timeline

| Phase | Messages | Time | Notes |
|---|---|---|---|
| Init | U1 → A1 | 19:17 to 19:20 (2.7 min) | awb-init. The first awb/setup call failed because the agent's marker-copy heredoc was blocked by the sandbox (no temp file allowed). The agent recovered with `python3 -c`. It created a project-local venv after the installer refused the README's global interpreter, which lacked duckdb. |
| Scoping | A1 → U2 | 19:20 | Four focused questions, each with a recommendation. The user's brief was front-loaded, so the interview was thin (a known study limit). |
| Landing | A2 | 19:20 to 19:31 | Pinned OWID commit 382ee6c, landed the files into `storage/landed/`, retained originals with verified SHA-256, and published 50,411 rows with 14 checks passing. |
| Cleaning / exploring | A2 | (same turn) | No separate awb-clean or awb-explore step. The entity audit (Kosovo, Antarctica), coverage profiling (GDP to 2022, consumption to 2023, Libya's missing coal, China/India historical gaps) and the EU-27 reconciliation were folded into the analysis turn. |
| Answering | A2, then U3 → A3 | 19:31 to 19:43 (10.9 min) | A2 recorded all five answers and the headline preview, but said "5 answered" while showing only the leaders. U3 asked for the full tables, so A3 added three follow-up results (Ukraine timing, the World construction check, the historical sensitivity) and the full tables. |
| Headline review | U3, U4 | 19:32 to 19:43 | Preview-and-wait worked. The user rewrote five headlines in U3 and two more in U4, the second time to remove slashes the agent had added to stay within the word limit. |
| Packaging | U4 → A4 | 19:43 to 19:59 (16.5 min, the longest turn) | Four failed awb/package calls (Unicode CO₂ header mismatch, Mt→Gt number tracing, a causal phrase in a negated sentence) and repeated full reviewer-subagent passes. The agent dropped the second clause of the approved Answer headline. |
| Review corrections | U5 → A5 | 20:00 to 20:05 (4.9 min) | Four corrections. To keep the user's 21-word headline, the agent edited the project's `src/packaging/draft.py` checker and two format templates, adding a `headline_length_exceptions` mechanism. |
| Status | U5 → A5 | 20:05 | awb-status reported all questions answered, 11 findings current, the draft ready and storage reachable. Next step given: "assemble PowerPoint, then mark delivered". |
| Release | U6 → A6 | 20:05 to 20:07 (1.7 min) | awb-release ran a fresh full review and a verify-only check (no DRAFT markers), froze 001 and copied it to storage, with the copies verified. |
| Done | U7 | 20:07 | Not relayed. Feedback turns followed. |

## Pain points observed by the referee

| # | Pain point | Messages | Severity |
|---|---|---|---|
| 1 | **The agent edited release-gate helper code in the project.** The installed checker had a hard 15-word headline limit and no override, so the agent patched `src/packaging/draft.py`, `package-format/findings-template.md` and `package-format/manifest-template.md`. All three now differ from their hashes in `.awb-receipt.json`, while every other helper still matches. The change is narrow and was tested, but the release check that passed is no longer the shipped check, and the project's helpers have drifted from the receipt. The same limit had already made the agent put slashes in a headline (A3) and silently drop half of the approved Answer headline (A4). | A3, A4, A5 | Major |
| 2 | **"All five answered" was claimed before the answers were shown.** A2's footer said "5 answered" but gave only the top country for Q1 and Q5. The Q1 lists were not in the preview file either. That cost the user a full turn (U3). | A2, U3 | Major |
| 3 | **Packaging checks disagree with the exporter and cannot express unit conversions.** `check-draft` normalised CO₂ to CO2 in the narrative but not in the CSV headers, so all six charts failed. Displaying Mt values as Gt required re-running and re-promoting two results and whitelisting the constant 1000. | A4 | Major |
| 4 | **Repeated full reviews make packaging slow.** A4 took 16.5 min, the longest turn of the run, mainly because the mandatory full reviewer pass was repeated after small citation and wording repairs. | A4, A5, A6 | Major |
| 5 | **The read-only SQL tool suggests escalating privilege.** An ordinary DuckDB binder error came back as "run it without --read-only". The agent rightly ignored it. | A3 | Major |
| 6 | **Workbench internals leaked into chat.** A1 linked to the agent's `SKILL.md` and quoted it. Later replies mentioned record IDs (R-headlines-001, R-metric-definitions-001), "the template's word limit", "11 findings" and "two required supporting questions". | A1, A3, A5 | Minor |
| 7 | **Standing review rules were created from one-off corrections without asking the user.** | A3, A4, A5 | Minor |
| 8 | **The deliverable boundary was unclear.** The package is an outline plus CSVs and assembly instructions, not a PPTX. awb-status told the user to assemble the PowerPoint before releasing, and the README does not say which comes first. | A4, A5, U6 | Minor |
| 9 | **START-HERE was self-contradictory.** It told the user to attach methodology.md to the builder and also listed it as internal. The agent fixed the generator in the project after U5. headline-preview.md ships in the release but START-HERE does not list it. | A4, U5, A6 | Minor |
| 10 | **Replies were long, with progress narration** ("I'm checking…", "I'm fixing the remaining mechanical issues…"). A4 used relative links where other replies used absolute ones. | A2 to A5 | Minor |

Isolation audit: no material breach, and nothing that affected the run.

- **Agent logs** (`relay/agent-001..007.jsonl` via `logview.py --full`, with SIMDIR masked):
  - There were no reads of workbench-spec, workbench-design, CONTEXT.md, a docs/ folder, the analytics-workbench repository, `SIMDIR/human`, `SIMDIR/relay`, `transcript.md` or KIT. Every file path the agent touched was under `SIMDIR/project`, `SIMDIR/agent-home/.agents/skills` or `SIMDIR/feedback/agent-notes.md`.
  - In A1 the agent ran Codex's usual ancestor search for AGENTS.md and CLAUDE.md files, eight directory levels up from the project. That reaches above SIMDIR, but it found nothing and read nothing. Not material.
  - The four reviewer-subagent rollouts (`agent-home/.codex/sessions/2026/10/16/rollout-*.jsonl`) were also clean. The only "CONTEXT.md" match is text inside the awb-scope skill.
- **User logs** (`relay/human-001..008.jsonl`): the user read only `human/README.md`, `human/BRIEF.md`, files under `project/deliveries/.../draft/`, and a listing of `storage/releases`. There were no reads of AGENTS.md, SKILL.md, src/, any .py file, workbench-guides/ or agent homes. The user declined to open the SKILL.md link A1 offered.

## User satisfaction

**8/10** (`feedback/human.md`). The user would use the workbench again.

## Most important issues for the workbench maintainers, ranked

1. **The 15-word headline limit has no override.** It made the agent trim and slash user-approved headlines and then patch the project's checker code and templates so that release would pass (`draft.py` and two templates now differ from the receipt). Ship an auditable user-override mechanism (or make the limit a warning), and tell the user about the limit at the headline checkpoint.
2. **The reporting convention lets the agent say "N answered" before the user has seen the answers.** When an answer is a ranking or list, put the full table in chat the first time it is reported as answered.
3. **`check-draft` and the exporter disagree.** CO₂ is normalised on one side only, and number tracing cannot express display unit conversions (Mt→Gt). Normalise both sides consistently, and support declared unit transforms as export metadata.
4. **The mandatory full narrative review re-runs after small repairs.** This made packaging the slowest phase (16.5 min). Allow a scoped repair review, plus an unchanged-content hash check.
5. **The read-only SQL wrapper advises dropping `--read-only` on an ordinary binder error.** Distinguish parser and binder errors from plans it genuinely cannot verify, and never suggest more privilege for a SQL mistake.
6. **Internals reach the user.** SKILL.md links, rule IDs and finding counts appear in chat, and standing review rules are created without telling the user. Ask with one line ("Keep this as a rule for future drafts?") and keep record IDs out of chat.
7. **The deliverable boundary is unclear.** Say early that the package is an outline plus chart sources for an assembly agent, and whether the deck should be built before or after release, in both the README and awb-status.
