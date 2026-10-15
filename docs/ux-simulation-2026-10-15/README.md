# UX simulation, 2026-10-15: synthesis

Six simulated first-time users each took the `awb-*` skills from an empty folder to a released deck package, on three public datasets. Each dataset ran twice with the models swapped. This file brings together the feedback from all six runs. The per-run evidence sits beside it.

## Bottom line

- **All six runs reached the end point.** Each one answered all five questions, asked `awb-status` once, and had a package drafted, reviewed by the user, released as 001, and copied to the releases folder.
- **The numbers were right.** Each orchestrator recomputed the answers from the landed source files with its own read-only queries. Every figure checked matched exactly.
- **The friction was in delivery and conversation, not analysis.** All six users rated the session 7 or 8 out of 10. They lost points on:
  - a package shaped for the format, not the audience;
  - approval stops before the first draft;
  - internal bookkeeping leaking into chat;
  - a README written for whoever installs the tool, not the analyst.

  On the agent side, the main cost was provenance churn: small presentation edits forced full reruns and repeated review rounds.

## Method

| | Detail |
|---|---|
| Release under test | `dist/analytics-workbench-skills.zip` built by `scripts/build-dist.sh` at `7f92e8e` |
| Datasets | NYC TLC yellow taxi trips, Jan and Jul 2024 (two Parquet files plus the zone lookup, handed over as local files); Our World in Data CO2 (CSV and codebook, by URL); UCI Online Retail II (zipped XLSX, by URL) |
| Questions | Five per dataset, set in a persona brief with an audience, a deadline and a decision ([kit/personas/](kit/personas/)) |
| Variant A | Opus played the human, Codex the agent |
| Variant B | Codex played the human, Opus the agent |
| Human's view | The release README (the dist copy, with dist-excluded blocks dropped), its persona brief ([kit/human-rules.md](kit/human-rules.md)), the agent's replies, and only the project files the agent pointed it to |
| Agent's view | The installed release only: skills at user level in a sandboxed home, plus the downloaded release folder. No design docs, spec, `CONTEXT.md` or `docs/` |
| Codex isolation | A fake `HOME`/`CODEX_HOME` holding only the release skills; account apps, plugins and browser tools turned off; the `awb` MCP server registered from the installer's `--mcp-config codex` output; sandbox `workspace-write` with network on |
| Opus isolation | Nested subagents bounded by their briefs ([kit/agent-role-opus.md](kit/agent-role-opus.md), [kit/human-role-opus.md](kit/human-role-opus.md)). The Opus agent read each `SKILL.md` on demand, imitating a skill host, and had no MCP server, so it used the CLI fallback |
| Orchestration | One Opus orchestrator per run ([kit/orchestrator.md](kit/orchestrator.md)) relayed messages verbatim, ran Codex turns through [kit/simctl.py](kit/simctl.py), checked the end point, spot-checked answers against source data, audited isolation, and collected feedback from both roles |

Paths in the copied evidence are rewritten to `SIMS/<run>`, `~` and `<scratch>`.

## Results by run

| Run | Human / agent | Human msgs | Agent turns | Wall-clock | Satisfaction | End point | Spot-check |
|---|---|---|---|---|---|---|---|
| [taxi-A](taxi-A/) | Opus / Codex | 12 | 11 | 2 h 16 m | 8/10 | met | all 5 match |
| [taxi-B](taxi-B/) | Codex / Opus | 9 | 8 | 1 h 27 m | 7/10 | met | all 5 match |
| [co2-A](co2-A/) | Opus / Codex | 10 | 9 | 1 h 17 m | 8/10 | met | all 5 match |
| [co2-B](co2-B/) | Codex / Opus | 7 | 6 | 1 h 10 m | 7/10 | met | all 5 match; a narrative reconciliation claim was false and the user caught it |
| [retail-A](retail-A/) | Opus / Codex | 10 | 9 | 1 h 36 m | 8/10 | met | all 5 match |
| [retail-B](retail-B/) | Codex / Opus | 7 | 6 | 1 h 11 m | 7/10 | met | all 5 match |

Each run folder holds `human.md` (user feedback), `human-notes.md` (the user's per-turn friction log), `agent.md` (agent feedback), `agent-notes.md` (the agent's per-turn friction log), `orchestrator-report.md` (referee findings, end-point evidence, spot-checks, isolation audit) and `transcript.md`.

Skill use: none of the six users or agents used `awb-brainstorm`. `awb-scope` was named twice across all transcripts. `awb-explore` ran as a distinct step only in taxi-A and taxi-B. co2-B skipped both clean and explore, folding its checks into `publish`.

## Findings, ranked

Ranking weighs how many runs hit an issue against its severity. "n/6" counts the runs where a human, an agent or the orchestrator reported it.

### 1. The package is shaped for the format, not the audience (6/6, major)

- **Methodology note (5/6):** by default it is an internal reference. Users who asked for a one-page or donor-ready methods note got 2,400 to 4,300 words of result IDs, file paths, settings and terms like "immutable publication". Each run needed a revision round, about 18 minutes in taxi-B. The audience-facing note the agents then wrote sits outside `check-draft` and `review-rules check`, which read only `findings.md` and `methodology.md`. ([co2-A](co2-A/human.md), [taxi-B](taxi-B/agent.md), [retail-A](retail-A/human.md))
- **Slide budget and order (5/6):** "About 8 slides" became 11 or 12 because of the template's fixed non-finding slides. There is no appendix marker. Slide order comes from ledger priority, so "put airports before volumes" could only be done by demoting a question. The taxi-B user objected, then gave in "to keep this moving". The taxi-B agent found that `check-draft` does not actually require several of the slides it had called mandatory. ([taxi-B](taxi-B/orchestrator-report.md), [co2-B](co2-B/agent.md))
- **Display defaults (4/6):** chart and dataset CSVs went out unrounded (`366.89000039169395`, `0.42541799999999996`), with rates as fractions and source labels ("European Union (27)") instead of audience labels. The `display.toml` machinery fixed this once it was configured, so the gap is the defaults. `display.toml` labels are also global per column name, which silently mislabeled a dataset in co2-B.
- **Possible fixes:**
  - an optional audience-facing `methodology-note.md` in the package contract, covered by the mechanical checks;
  - an appendix divider and a slide-budget reconciliation at the headline checkpoint;
  - presentation order separate from ledger priority;
  - display rounding and label mapping applied on the first export.

### 2. "Deck package" means an outline, and users learn this late (6/6, major)

- **What users found:** five of six users expected slides and got an outline plus chart CSVs for the M365 Copilot PowerPoint agent. The README states this in one dense sentence in **Use**. The co2-B, taxi-B and retail-B users found that sentence but said it needs far more prominence. The retail-A user missed it. The co2-A user couldn't tell whether a Copilot licence is required.
- **What the agent built in taxi-A:** its own PPTX/PDF renderer, plus row selection added to the shipped exporter. That gave the user real slides, but the user then noted the README had led them to expect a manual M365 build.
- **What users asked for:**
  - a "What you get" section near the top of the README;
  - the attach list and a one-line build prompt shipped with every draft;
  - a rendered preview of the deck.

### 3. Approval stops before the first draft (6/6, major)

- **The headline checkpoint:** `awb-package`'s mandatory headline approval stopped every run, including runs where the user had supplied the storyline and asked for the full draft. It was in the users' top three pain points in three runs (retail-B first, co2-B second, taxi-B third), and all three Codex agents called it a major pain point.
- **Opus agents also stopped for routine work:** `pip install` (awb-init step 3.3 tells the user to run it), each local commit, and whether to investigate an anomaly the agent had found itself.
- **What agents and users suggested:**
  - draft in full with the headlines marked provisional, unless a consequential choice is still open;
  - a user-selectable mode: preview-and-wait or draft-then-review;
  - routine, reversible setup proceeds without asking.

### 4. Internal mechanics leak into the conversation (6/6, major for trust, minor per instance)

- **Counts and IDs:**
  - "17 questions answered / 10 findings" against five asked (co2-A). Explaining it cost the user a turn.
  - Two unrelated `Q-NNN` schemes: ledger questions and quality IDs. The `record_cleaning.py` help example uses `Q-004` for a quality ID, which collides with ledger IDs (co2-A, retail-B, taxi-A).
  - A footer contradicting the body ("answered 6" vs "18 answered", taxi-B).
- **Links to agent instruction files:** all three Codex agents sent the user to a `SKILL.md` to justify a pause (co2-A, retail-A twice, taxi-A). Every human declined to open it. The retail-A agent traces this to its host's own instructions, not the workbench's. The workbench could still head it off with a line saying to phrase pauses as plain decision requests.
- **Environment status with no impact statement:** "Git initialization was denied", "MCP writes require the CLI fallback", "provenance gaps: two geography-validation metadata entries". Each made the user ask whether they had to act. They didn't.
- **Long setup reports (Opus agents):** venv, uv, receipts, helpers, MCP registration, 15 or 16 opened ledger questions. One user was pointed at a `.sql` file to review the country classification.
- **Questions announced but not asked (Codex agents):** "3 need your context" (retail-A) and "1 needs your context" (taxi-A), with the question itself missing. This cost a turn each time.
- **A false action claim:** the co2-B agent twice said it had "attached" files. The host has no attachment channel.

### 5. Presentation edits cost analytical rework (6/6 agents, major for time)

- **Staleness reaches too far (5/6):**
  - Editing `run.py` to register one producer stales every result's export (`committed-code: run.py differs from producing commit`).
  - Editing investigation `methodology.md` prose staled every result in co2-A and retail-A.
  - Adding a global `[parameters]` entry stales every result. A result first run on uncommitted code comes back `refreshed`/provisional at the commit, so it needs promoting twice.
  - Agents asked for per-result dependency tracking.
- **Charts cannot select rows (5/6):** a top-10 chart from a 45-row ranking needs a new recorded result, with settings, validation, a finding and promotion. In retail-A, a six-bar chart forced 21 results to refresh. The taxi-A agent patched `src/packaging/draft.py` with a `--chart-selections` option rather than do that.
- **The numbers check fires late:** derived totals and shares must be recorded results. This surfaces only at `check-draft`, never at `state finding --text`. There were also false positives on DOI fragments, dates, slash-paired values, and negated causal wording ("does not establish the effect of …").

### 6. Review is expensive, and it checks form more than substance (4/6, major)

- **Round counts:** fresh reviewer rounds per run were 11 (retail-B), 8 (taxi-B) and 4 + 2 + 1 (co2-B). Every edit makes the review stale. Rules are read bullet by bullet: one wording rule produced 13 errors in co2-B.
- **What the reviews missed:**
  - co2-B: the agent wrote "countries plus non-country entries sum to World". It had checked six years. The claim was promoted to `supported` and passed four reviewer rounds. The Codex user questioned it, and checking every year showed a 478 Mt double count in 1991 (Kuwaiti oil fires).
  - taxi-A: the first deck passed the agent's review and package checks, yet still needed five user corrections.
- **Suggested fixes:**
  - require that any "checked" or reconciliation assertion in a judgment trace to a recorded result;
  - have `state finding --status supported` warn on figures that appear in no result;
  - give review rules a scope (slide, bullet or document);
  - ask reviewers for one exhaustive pass, and allow scoped re-review of changed lines.

### 7. First-pass answers run ahead of the evidence (5/6, major for trust)

The workbench's caution about claims engaged at package review, not when the agent first answered in chat:
- taxi-B treated the user's recollection about cash tips as confirmed, and called matched positive fares voided trips.
- taxi-A showed a weekday comparison with no holiday check. When the user raised it, setting holidays aside flipped Thursday from −3.9% to +9.1%.
- retail-B offered untested explanations, for example that April's fall was calendar timing.
- retail-A led with a raw cancellation ranking dominated by one-off orders.
- co2-B asserted, without support, that missing early years "matter little".

In every case the user had to separate observation from explanation.

### 8. Scoping: the interview the README promises happened only with Opus agents (3/6, major)

- **Codex agents (co2-A, retail-A, taxi-A):** each ran init and scope in one turn and recorded open decisions in the ledger, asking the user nothing directly. All three users noted the README says awb-scope "interviews you". It worked only because every persona had front-loaded definitions.
- **Opus agents:** asked four bundled decisions, each with a recommendation. Users rated these well, but one said method questions were split across rounds when they could have been bundled.

### 9. Setup and environment friction (6/6 agents; partly simulation artifacts)

**Real workbench issues:**
- `AGENTS.md`, the guides and every skill hardcode `python3`. With a project venv, bare `python3` lacks duckdb, so every command is wrong as written (3/3 Opus agents). Fix: record the installer's interpreter and template it in.
- `install_helpers.py` prints `.venv/bin/python -m pip install …`, which fails in a uv-created venv because it has no pip (co2-B, retail-B; co2-A hit the same "No module named pip").
- `foundation/quality.md` as `awb-init` writes it does not parse in `record_cleaning.py` (`RecordError: no '## Active limitations and issues' section`, co2-A). Custom rows below the template prose are rejected (retail-A). There is no helper for analyst-authored issues that the scanner did not emit.
- **The CLI fallback mapping is unclear.** `AGENTS.md` routes `eda_scan.py` and `scan_dataset.py` through the MCP `data` commands `eda-scan` and `clean-scan`. With MCP writes unavailable, the taxi-A agent ran `awb.py eda-scan` and got `unknown command`. These were never `awb.py` subcommands, so the instructions name no missing command. They just don't spell out the CLI form for agents that fall back.
- `awb-init`'s ancestor `CLAUDE.md` walk (step 1.3) runs `test -e` up to `/`, outside the project. No contents were read.
- No guidance on landing zip or XLSX sources: which form to keep, the `read_xlsx` extension, Excel serial dates under `all_varchar` (retail-B).

**Simulation artifacts:** these hit all three Codex agents and are partly caused by the harness, but the workbench's handling still matters:
- **MCP writes:** every MCP write returned `MCP tool call requires approval, but approval policy is never`, because `codex exec` ran non-interactively. An interactive user would approve the call. The issue that remains: `AGENTS.md` says "use MCP when offered" and gives no read-MCP/write-CLI fallback, so each agent had to work that out itself.
- **Git:** `git init` was blocked by Codex's `workspace-write` protection of `.git`. A no-Git mode, reported once, would have avoided the repeated "suggest committing" prompts.
- **Python version:** the sandbox shell's `python3` was 3.9.6. The installer refused it clearly, but nothing bootstraps a 3.10+ interpreter.

### 10. Release details (3/6, minor to major)

- **Draft markers survived release (taxi-A):** release 001 still read "BOARD REVIEW DRAFT" on every slide header and "a working draft, not a numbered release" in its notes. The agent wrote those labels itself; no shipped template contains them. But `awb-release` copies the draft byte for byte and checks for no draft markers. A board member opening the shared-drive copy would see a draft.
- **Folder layout (co2-A, taxi-A, retail-A):** the release sits four or five folders deep, with "released" inside "releases". About 20 audit JSON files surround the 3 files a colleague wants. Users asked for deliverables at the top, audit files in a subfolder, and a "send these" note.
- **Unreviewed change (co2-B):** a revision requested together with the release went into the freeze before the user saw it.
- **Open caveat reported as nothing outstanding (retail-B):** the agent said nothing was outstanding while VAT treatment remained an open caveat.

### 11. The README (6/6 humans, major)

Every human said the same things:
- About three-quarters of it is for whoever installs the tool: MCP JSON, symlinks, VS Code targets, the `AGENTS.md`/`CLAUDE.md` rules. The analyst's part is the **Use** section.
- Jargon goes unexplained: canonical views, Parquet/DuckDB views, question ledger, receipt, "disposition for each flagged finding", the M365 assembly file, `R-<area>-NNN`.
- It promises things that didn't happen: an interview, and a disposition prompt the taxi-A user never got and couldn't define. It leaves out what did happen: the headline gate, the template's extra slides, an internal methodology note by default.

What users asked for: a one-page analyst quick-start covering what to say, what you'll be asked (storage locations, audience, deadline), how many exchanges to expect, what you receive, and the six requests in order. Setup would move to an admin section. Two things worked as written: the example phrasings ("Use awb-status — where are we?") and the warning that the agent would ask for storage locations. Several users gave both paths up front because of that warning.

## What worked

- **Correct, reproducible numbers.** Every spot-checked figure matched the source data in all six runs. Answers stated the years they used, their coverage limits and their denominators.
- **Landing and retention.** Originals were pinned (co2-A to an OWID commit), checksummed, and copied to the user's landed folder. Release copies were verified file by file.
- **Cleaning that caught real problems:**
  - Kosovo had no ISO code and would have been dropped, while Antarctica would have counted as a country (co2-A).
  - Flushing Meadows trips were coded at the JFK flat rate (taxi-A).
  - CMT reported zero tips in Brooklyn and the Bronx (taxi-A).
  - The Kuwaiti oil-fires double count, once the user pushed (co2-B).
- **Candid self-correction.** For example, the co2-A agent corrected an earlier "2024" to 2023 for consumption data without being asked.
- **Decisions offered well.** Choices came as a recommendation plus an alternative, in tables.
- **`awb-status` was short and plain**, and ended with the exact phrase for the next request.
- **Review rules recorded user corrections** (appendix marking, missing versus zero, rounding notes), and later drafts were checked against them.

## Differences between the two variants

The samples are small (three runs per cell), and the model playing the human changes with the model playing the agent, so treat these as leads, not results.

- **Codex as agent (A runs):**
  - longer runs: 1 h 43 m on average, against 1 h 16 m for B;
  - no scoping interview;
  - linked users to `SKILL.md` files;
  - reported environment failures without saying whether they mattered;
  - more willing to change shipped helpers: taxi-A patched the exporter and wrote a renderer.
- **Opus as agent (B runs):**
  - asked bundled scoping questions;
  - wrote longer setup reports;
  - asked approval for routine steps;
  - ran more reviewer rounds;
  - made one false "attached" claim.
- **Opus as human:**
  - asked more follow-ups;
  - rated 8/10 in all three runs;
  - turned down instruction-file links explicitly.
- **Codex as human:**
  - terse, putting definitions up front, with fewer turns;
  - rated 7/10 in all three runs;
  - the hardest substantive reviewer: it caught the co2-B reconciliation error that four agent reviews missed.

## Isolation

The orchestrators searched Codex logs for reads of `workbench-spec`, `workbench-design`, `CONTEXT.md` or `docs/`, and asked each Opus agent role what it had read outside its bounds. They found none.

Edge cases:
- **taxi-A Codex agent:** in turn 1 it ran a broad `rg --files` over the scratch root, which listed other simulations' study files. Its notes say it used none of them.
- **Opus agents:** walked parent directories for `CLAUDE.md` with existence checks only, as awb-init step 1.3 instructs.
- **co2-B:** the Opus agent's reviewer subagents were bounded only by their briefs.
- **Human roles:** no human quoted internals it could not have known. Every human turned down the `SKILL.md` links.

## Limits of this study

- **Not real users.** Both roles were models, so personas front-loaded definitions more than real users would. That masked the missing Codex-side interview.
- **Opus agent only imitated a host.** It read `SKILL.md` on demand rather than through real host skill discovery, and had no MCP server. The two variants therefore tested different routes: MCP plus CLI for Codex, CLI only for Opus.
- **Codex ran non-interactively,** so its MCP write and `.git` failures partly come from the harness (see 9).
- **One run per cell.** No figure here is a measured rate.
