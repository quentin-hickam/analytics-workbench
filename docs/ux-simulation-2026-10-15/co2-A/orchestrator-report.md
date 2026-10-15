# Orchestrator report: co2-A

## Run facts

- **Variant:** A. Claude Opus played the human (`co2-A-human`, persona Sam Whitfield, research lead). Codex played the agent (session `01a13f93-8b07-76e2-9478-6175bfe3373b`, cwd `SIMDIR/project`).
- **Start:** 2026-10-15 08:39:11 EDT (first agent turn sent 08:39:56). **End of conversation:** 09:53:20 (human `STATUS: DONE`). **Feedback complete:** 09:56. **Wall clock:** about 1 h 17 min, far under the 8-hour cap.
- **Turns:** 10 human messages. The human first sent `STATUS: DONE` at message 9 together with a last question, so I relayed that question and the human closed with a second DONE at message 10. There were 9 agent conversation turns plus 1 feedback turn. All turns finished on the first try, with no FAILED runs and no retries.
- **Agent turn durations:** t1 3 min, t2 5 min, t3 10 min, t4 11 min, t5 4 min, t6 10.5 min, t7 9.5 min, t8 3.5 min, t9 0.2 min.
- **Harness incidents:** none. Neither role broke protocol, and no harness notes were needed after the first-turn study note.
- **Fallback:** not used. The Opus human role ran as a nested subagent throughout.

## End-point checklist

| Criterion | Met? | Evidence |
|---|---|---|
| All five questions answered specifically and accepted | Met | Agent answers in `transcript.md` turn 4 (Q1–Q4 accepted in human message 5) and turn 5 (Q5 sensitivity; measure chosen in human message 6). Ledger: `project/investigations/emissions-accounting-shifts/questions.md` (Q-007..Q-011 answered, linked to r-001..r-005, r-009..r-016) |
| Asked where things stand at least once | Met | Human message 5 ("use awb-status — where are we?"); agent turn 5 reply contains the status |
| Deck package draft exists and was reviewed | Met | `project/deliveries/emissions-accounting-shifts/donor-roundtable/draft/` (findings.md, 6 chart CSVs, methodology-donor.pdf/.md, methodology.md, manifest, assembly guides). Reviewed in human messages 7 and 8 |
| Released as release 001 | Met | `project/deliveries/.../donor-roundtable/released/001/` |
| Copied to the releases folder | Met | `SIMDIR/storage/releases/emissions-accounting-shifts/donor-roundtable/released/001/`. `diff -r` against the project copy is identical |
| Landed originals in the landed folder | Met | `SIMDIR/storage/landed/data/raw/owid-co2/2026-10-15-382ee6c/` (CSV, codebook, README, provenance.json), pinned to OWID commit 382ee6c |
| Human corrections applied in the release | Met | Chart CSVs are rounded (for example chart-1 `8.65`), chart-4 and chart-5 use `EU-27`, there are no "European Union" strings in the charts, findings or donor note, and the slide 8 headline was revised |

## The five questions

My spot-checks were run read-only with the project venv's duckdb on the landed CSV, using my own script (`sims/orch-co2A-scripts/check.py`). Country = ISO code not starting `OWID`, plus Kosovo, minus Antarctica.

| # | Agent's final answer | Recorded? | Spot-check |
|---|---|---|---|
| 1 | 2000→2024, 215 countries. Increases: China +8,645.2 Mt, India +2,206.4, Indonesia +531.2, Iran, Saudi Arabia, Vietnam, Russia, Turkey, Malaysia, Iraq (+149.9). Decreases: US −1,119.0, Germany −326.7, Japan −298.3, UK, Italy, France, Ukraine, Spain, Netherlands, Czechia (−51.6) | Yes (r-001, r-010, r-011; Q-007) | **Exact match** for all 20 values and n=215. Slide-2 claim "68.7% of combined increases" also verified (10,851.6 / 15,805.6) |
| 2 | 45 of 164 countries cut CO2 while growing real GDP, 2005→2022 (GDP ends 2022). Largest by 2022 CO2: US, Japan, Germany, Canada, Mexico, Australia, Italy, Poland, UK, France. No top-20 emitter lost for missing GDP (largest excluded: Sudan, rank 95) | Yes (r-002, r-012, r-006, r-008; Q-008, Q-016) | **Exact match** on 164 eligible and 45 qualifying. Latest country GDP year is 2022 |
| 3 | 2023 per person, territorial vs consumption: US 14.32/15.81 (+10.4%), China 8.56/7.63 (−10.8%), India 2.13/1.77 (−17.0%), EU-27 5.51/7.33 (+32.9%) | Yes (r-003; Q-009) | **Exact match.** Consumption series end in 2023 for all four |
| 4 | Share of cumulative CO2 1850–2024 (sum of recorded years; World denominator includes international transport): US 23.57%, EU-27 16.27%, China 15.46%, India 3.58%. China has no data for 1850–1906; India has gaps | Yes (r-004, r-007, r-015; Q-010, Q-017) | **Exact match** to two decimals |
| 5 | 60 countries ≥50 Mt in 2010; 59 ranked (Libya unranked). Percentage-point decline per year 2010→2024: Greece 2.38, Romania 1.65, Israel 1.57, Poland, US, Finland, Czechia, UK, Hungary, Germany (0.92). Relative-decline ranking also given (Portugal 96.3% first); human chose percentage points with relative callouts | Yes (r-005, r-013, r-009, r-016; Q-011, Q-018, Q-019) | **Exact match** on n=60 and the full top-10 values |

I found no discrepancies. All five answers reproduce from the raw landed file under the stated definitions.

## Timeline

| Phase | Turns | Notes |
|---|---|---|
| Init | H1 → A1 | awb-init done in 3 min. The agent reported git and MCP-write denials without saying whether they mattered |
| Scoping | A1–H2 | No separate scoping interview (awb-scope was never invoked). Init listed open ledger items, and the human answered them in H2 along with the five questions and definitions |
| Landing | A2 | Full OWID snapshot pinned to a commit, with checksums, copied to the landed folder; 17 structural checks |
| Cleaning | H3 → A3 | Verified the ISO-code assumption: Kosovo would be dropped and Antarctica admitted. Three decisions offered as a recommendation plus an alternative. Self-corrected its earlier "2024" consumption claim to 2023 |
| Exploring + answering | H4 → A4 | All five answered in one turn with years, coverage and footnotes. No separate explore step was visible to the user |
| Sensitivity + status | H5 → A5 | Coal metric sensitivity check plus awb-status |
| Packaging | H6 → A6 | Headline checkpoint only. The internal methodology draft was produced as the default note |
| Review | H7 → A7, H8 | Human revised headlines and asked for a donor methodology note (delivered as a 2-page PDF), then asked for rounding, EU-27 labels and a slide 8 rewrite |
| Release | A8 | Release 001 frozen, copied and verified in 3.5 min |
| Wrap | H9 → A9, H10 | Which files go to donors (one-line answer) |

## Pain points observed as referee

1. **The default methodology deliverable was internal, not donor-facing** (A6/H7, major). It was full of result IDs, settings and file names, and the user had to ask again. Root cause per the agent: the package methodology template is an internal reference with no audience-facing variant.
2. **Bookkeeping leaked into user messages** (A3, A5, A6, minor-to-major). Two unrelated "Q-" numbering schemes appeared (ledger questions and quality records Q-001–Q-013), and "17 questions answered / 10 findings" against 5 asked cost a user turn (H6). Presentation projections and headline checks get recorded as extra "findings" and ledger questions (Q-020–Q-022), which inflates counts further.
3. **The agent linked the user to its own SKILL.md** (A6, minor). It cited `agent-home/.agents/skills/awb-package/SKILL.md` and quoted a rule as the reason for the checkpoint. The human correctly declined to open it. This is an agent-side isolation slip toward the user, not a design-doc read.
4. **Environment failures were reported with no impact statement** (A1, minor). Both were real environment limits: `git init` → Operation not permitted, and MCP writes → "requires approval, but approval policy is never". The user had to ask whether to act. Agent-side root causes: no Python 3.10+ on PATH (system Python 3.9.6; the agent built a .venv by hand), and `foundation/quality.md` as initialized did not match the `record_cleaning.py` parser (`RecordError: no '## Active limitations and issues' section`).
5. **First chart exports were not presentation-ready** (A7, minor). They had floating-point noise (`0.42541799999999996`) and the raw label "European Union (27)" against "EU-27" on the slides. Both were fixed in one round once display settings were configured.
6. **The package is not a deck** (release, major for this persona). It is a markdown outline plus CSVs plus M365 Copilot or manual assembly guides. The README does not make clear that Copilot is optional or that the user builds the slides.
7. **Link style was inconsistent** (A3–A8, minor). Early links were absolute paths and later ones relative (`deliveries/...`). The release path nests "released" inside "releases".
8. **Staleness tracking over-triggered** (agent-side, per agent.md). Editing methodology prose marked r-009 stale (`uncommitted-code`) and forced an unchanged rerun. This was not visible to the user but cost agent time.
9. **Scratch files written to system /tmp** (minor isolation note). The agent wrote helper scripts and dependencies to `/tmp/co2_*.py`, `/tmp/co2-donor-pdf-deps` and others, outside SIMDIR. These were not reads of forbidden material.
10. **The awb-scope interview never happened.** This was harmless here because the persona volunteered every definition up front. A less forthcoming user would not get the interview the README promises unless they ask for it.

**Isolation check:** I searched all Codex logs for `workbench-spec`, `workbench-design`, `CONTEXT.md` and `docs/`. The only `CONTEXT.md` hits are lines of the shipped project AGENTS.md text ("never in CONTEXT.md or ADRs"), not file reads. The only `docs/` reference is OWID's own GitHub docs (`owid/etl docs/data/regions.md`), which is permitted source research. The only `/Users/` paths are Python interpreter shims during setup (`~/.pyenv/shims/python3`, `~/.local/bin/python3.12`), and no other sims folders were touched. **No isolation breach found.** On the human side, the human role declined the SKILL.md link and stayed within its permitted files.

## Most important issues for the workbench maintainers, ranked

1. **Ship an audience-facing methodology note by default** when the package audience is external, keeping the internal reference as a backing file with a name that says so (`methodology-internal.md`). This was the largest deliverable mismatch.
2. **Keep internal bookkeeping out of user-facing status and replies.** Report "5 of 5 research questions answered" first. Use one ID scheme, or none, in chat. Do not count chart projections and headline checks as findings or questions. Never link users to SKILL.md files.
3. **Make the README and package honest about the output.** Say the package is an outline plus chart data plus a donor note, not a .pptx, and that M365 Copilot is optional with manual assembly supported. Ideally render a basic deck or preview. Add a "send these to your audience" file to each release.
4. **Fix init robustness:**
   - Detect Python older than 3.10 and bootstrap a venv automatically.
   - Emit a `quality.md` that `record_cleaning.py` can parse.
   - Declare an MCP-read / CLI-write fallback, and a no-git mode, so environment limits are reported once with "no action needed".
5. **Apply display defaults on the first export:** round chart CSVs to displayed precision and map source labels to audience labels (EU-27) when chart specs are created.
6. **Let agents record analyst-authored quality issues in the cleaning recorder,** not only issues the scanner emitted. The user's main cleaning concern (aggregate vs country classification) fell outside the scanner's output.
7. **Narrow the staleness dependency surface,** so prose and caveat edits don't invalidate unchanged computations.

## Files

- Transcript: `SIMDIR/transcript.md`
- Human feedback: `SIMDIR/feedback/human.md` (satisfaction 8/10, would use again)
- Agent feedback: `SIMDIR/feedback/agent.md`
- Agent friction log: `SIMDIR/feedback/agent-notes.md`
- Human friction log: `SIMDIR/human/notes.md`
- Relay files and Codex logs: `SIMDIR/relay/`
