# UX simulation, 2026-10-15: fix plan

This plan turns the [synthesis](README.md) into PR-sized phases. Each finding was checked against the shipped files at `7f92e8e` (`.agents/skills/`) and against the design record (`docs/workbench-spec.md`, `docs/workbench-design.md`, `CONTEXT.md`), so the plan can tell a defect apart from a deliberate trade-off that needs better communication. Paths below are relative to the repository root unless they start with a skill name, which means `.agents/skills/<skill>/`.

## Summary

- **The analysis core held up.** Every confirmed defect is about delivery, conversation, provenance scope, setup, or documentation. No finding questions a computed number.
- **Seven phases**, each one PR:
  1. Package contract and storyline control
  2. Conversation hygiene
  3. Provenance churn
  4. Delivered files: export shaping and release layout
  5. Setup robustness
  6. Review economy and claim discipline
  7. README
- **The starting grouping changed in three ways, each because two phases would otherwise edit the same code:**
  - The headline-checkpoint mode moves from Conversation hygiene into Phase 1. It is a step of `awb-package` that Phase 1 rewrites anyway: the slide-budget reconciliation and the presentation order are shown at that checkpoint.
  - Display rounding and labels move out of Phase 1 and join chart row selection in Phase 4. All three change `export`'s `_shape` in `awb-package/assets/awb_draft.py:2314-2347`. The release-layout items join them, because both decide which files the user receives.
  - The distinct quality-ID namespace moves from Conversation hygiene into Phase 5. It is a change to `record_cleaning.py` and the `quality.md` template, which Phase 5 already rewrites.
- **Review economy becomes its own phase (6).** It also takes the "checked or reconciled" claim discipline that the co2-B error exposed. It follows Phase 1, so its rules cover the new methodology note.
- **Counts by classification (57 rows in the table below):**

  | Classification | Rows |
  |---|---|
  | Confirmed defect | 30 (2 of them residuals of simulation artifacts) |
  | Intended behavior, badly communicated | 13 (4 of them also need a design change) |
  | Simulation artifact | 3 |
  | Agent-authored, not the workbench's | 6 |
  | Rejected | 4, plus one sub-item of 9.9 |
  | Unverified, to reproduce first | 1 |

- **The three most important items:**
  1. **Staleness scope (Phase 3).**
     - What is wrong: evidence treats every non-record file in the investigation folder as producing code for every result. That covers `run.py` and any prose file an agent adds, such as an investigation `methodology.md` (`awb-init/assets/awb_provenance.py:564-567, 601-604`).
     - The consequence: registering one producer, or editing one note, stales every export.
     - Why it is a defect: it contradicts the design's stated intent that "edits to unrelated results no longer mark findings stale" (`docs/workbench-design.md:93`).
     - The cost: it drove most of the rerun-and-re-review churn in all six runs.
  2. **The package's audience contract (Phase 1).**
     - The gaps: there is no checked, audience-facing methods note; slide order can only be changed by rewriting ledger priority; the template's fixed slides silently inflate the deck past the user's budget.
     - Reach: this hit 6 of 6 runs as major.
  3. **Asking the user, inline and only when needed (Phases 1 and 2).**
     - The causes: the mandatory headline stop; the `AGENTS.md` record footer, whose example teaches "(1 needs you)" counts without the question (`awb-init/assets/workbench/AGENTS.md:28`); and an `awb-scope` report rule that lets a user's decision be parked "to answer now or later" (`awb-scope/SKILL.md:63`).
     - Reach: together these produced most of the extra turns users complained about.

**Issues.** One GitHub issue per phase: [#61](https://github.com/quentin-hickam/analytics-workbench/issues/61), [#62](https://github.com/quentin-hickam/analytics-workbench/issues/62), [#63](https://github.com/quentin-hickam/analytics-workbench/issues/63), [#64](https://github.com/quentin-hickam/analytics-workbench/issues/64), [#65](https://github.com/quentin-hickam/analytics-workbench/issues/65), [#66](https://github.com/quentin-hickam/analytics-workbench/issues/66), [#67](https://github.com/quentin-hickam/analytics-workbench/issues/67).

## Finding classification

"Class" uses: **D** confirmed defect; **I** intended behavior, badly communicated (**I+** where the evidence argues for changing the design too); **S** simulation artifact; **A** agent-authored, not the workbench's; **R** rejected; **U** unverified. Synthesis section numbers are in the ID.

### 1. Package shaped for the format, not the audience

| ID | Finding | Class | Evidence | Phase |
|---|---|---|---|---|
| 1.1 | `methodology.md` is a 2,400 to 4,300-word internal reference full of IDs and paths | I | Intended. `CONTEXT.md:62` defines the package "with an internal methodology reference". `awb-package/assets/package-format/methodology-template.md:3` says "It stays internal to the package". `awb-package/references/package-contract.md:21`. Nothing tells the *user* it is not the methods note they asked for. | 1 |
| 1.2 | No audience-facing methods note inside the checks | D | The draft holds only `findings.md` and `methodology.md` (`package-contract.md:9-17`). `check-draft` and `review-rules check` read only those two (`package-contract.md:64-65`; `awb-package/references/helpers.md:5`). The notes the agents wrote (taxi-B `board-methodology-note.md`, taxi-A `methodology-note.pdf`) escaped the names, numbers and claims checks. | 1 |
| 1.3 | "About 8 slides" became 11 or 12; agents called non-finding slides mandatory, but `check-draft` does not require them | D | `findings-template.md:12` says each `##` section "is one slide, in this order". The template has five fixed slides and up to three conditional ones (`findings-template.md:31-83`). `outline_problems` (`awb_draft.py:1659-1719`) checks no required section. taxi-B passed with Implications and Supporting datasets dropped (`taxi-B/agent-notes.md:103`). Nothing reconciles the slide count with a length the user asked for. | 1 |
| 1.4 | No appendix marker | D | No appendix construct exists in `findings-template.md`. `deck-rules.md:27` says "add no slide, and drop none". co2-B put appendix marking in speaker notes first (`co2-B/human.md:17`). | 1 |
| 1.5 | Slide order follows ledger priority, so "airports before volumes" meant demoting a question | I+ | Specified behavior: `docs/workbench-spec.md:141` says "when an approved reorder cannot preserve their meaning, keep the derived order and tell the user". Also `package-contract.md:29, 33`; `storyline` rows fail the check (`package-contract.md:65`). The taxi-B user conceded "to keep this moving" (`taxi-B/human.md:11`). The cost outweighs the coupling. | 1 |
| 1.6 | Chart and dataset CSVs unrounded (`366.89000039169395`), rates as fractions | D | Rounding applies only when `foundation/display.toml` `[round]` names a column (`awb_draft.py:2342-2343, 2376`). `awb-package/SKILL.md:51` asks for display names before writing, but nothing about rounding. Display names are already a required gap (`awb_draft.py:2333-2339`); rounding has no such gap. | 4 |
| 1.7 | `display.toml` labels are global per column name and silently mislabeled a co2-B dataset | D | `_display_name` looks up by column name alone (`awb_draft.py:2302-2306`). The co2-B case is in `co2-B/agent.md:15`. | 4 |
| 1.8 | Title and Answer slides could not be merged | I | `outline_problems` keeps the title slide to heading plus subtitle (`awb_draft.py:1674-1683`). The design makes **Answer** the executive summary (`docs/workbench-design.md:73`). Document it at the headline checkpoint; no change. | 1 |

### 2. "Deck package" means an outline

| ID | Finding | Class | Evidence | Phase |
|---|---|---|---|---|
| 2.1 | Users expected slides and got an outline, chart CSVs and builder instructions | I | Intended direction (`docs/workbench-design.md:73-81`; `docs/workbench-spec.md:238`). The README says it in one dense sentence (`README.md:108`). | 7 |
| 2.2 | Attach list and build prompt wanted with every draft | I | It already ships in every draft (`awb-package/assets/package-format/assembly/m365.md:7`), and the report tells the user (`awb-package/SKILL.md:85`). Users did not find it among the package files. | 4 (the start-here note) |
| 2.3 | taxi-A agent wrote a PPTX/PDF renderer and patched the shipped exporter | A | No shipped instruction asks for either. A reference renderer exists only in `tests/` (`tests/deck_renderer.py`), and whether to ship one is open (`docs/workbench-design.md:79`). | — |
| 2.4 | A rendered deck preview | R | Shipping a renderer is a recorded open decision (`docs/workbench-design.md:79`). It is a product decision beyond a UX fix and is out of scope for this plan. | — |

### 3. Approval stops before the first draft

| ID | Finding | Class | Evidence | Phase |
|---|---|---|---|---|
| 3.1 | Mandatory headline approval stopped every run, even with a storyline supplied | I+ | Specified: `awb-package/SKILL.md:45` says "wait for their answer before expanding the slides"; also `package-contract.md:33` and `docs/workbench-spec.md:141`. The design's goal is that the user checks the storyline *before M365 builds anything* (`docs/workbench-design.md:73`). Reviewing a full draft meets that goal as well as a preview does. | 1 |
| 3.2 | Opus agents stopped to have the user run `pip install` | D | `awb-init/SKILL.md:38` says to carry the printed `install` command into the report, and "the user adds or runs those". Installing into the project's own virtual environment is routine and reversible. | 5 |
| 3.3 | Opus agents asked before each local commit | I | `AGENTS.md:44` and `awb-init/SKILL.md:62` say "Commit when the user asks". There is no way to give standing permission once. | 2 |
| 3.4 | Asked whether to investigate an anomaly the agent found | R | Intended scope bounding: "broader preparation needs an explicit request" (`AGENTS.md:32`; `docs/workbench-design.md:27`). No change. | — |

### 4. Internal mechanics leak into chat

| ID | Finding | Class | Evidence | Phase |
|---|---|---|---|---|
| 4.1 | "17 questions answered / 10 findings" against five asked | D | The footer example teaches ledger counts: "Questions: answered 1 · opened 2 (1 needs you)" (`AGENTS.md:28`). `awb-status` reports raw ledger `counts` (`awb-status/SKILL.md:28`), and those include agent-added sub-questions. | 2 |
| 4.2 | Two `Q-NNN` schemes (ledger and quality) | D | `record_cleaning.py` defaults new quality IDs to the `Q-` prefix (`awb-clean/scripts/record_cleaning.py:127-133`). Its help (`:15-16`) and `awb-clean/SKILL.md:67` use `Q-004` as a quality ID. Ledger IDs are `Q-NNN` (`docs/workbench-spec.md:136`). | 5 |
| 4.3 | Footer contradicted the body ("answered 6" vs "18 answered") | A | The agent's own arithmetic. 4.1's fix removes the count that invited it. | 2 (side effect) |
| 4.4 | Environment status with no impact statement | D | Nothing asks for one. `awb-init/SKILL.md:50-60` lists what to report, with no "does the user need to act". `AGENTS.md:26` covers terms, not consequences. | 2 |
| 4.5 | Long setup reports | D | `awb-init/SKILL.md:50-60` asks for nine report items: files created, lazy directories deferred, installer items and more. The spec asks chat to "summarize outcomes in plain words" (`docs/workbench-spec.md:149`). | 2 |
| 4.6 | "3 need your context" with the questions missing | D | The `AGENTS.md:28` footer pattern "(1 needs you)" plus `awb-scope/SKILL.md:63`, which groups user questions "to answer now or later", so announcing without asking complies. | 2 |
| 4.7 | Codex agents linked users to `SKILL.md` files | A | No shipped file asks for this (searched `.agents/skills`). The retail-A agent attributes it to higher-priority host instructions (`retail-A/agent.md:32`). The workbench can still head it off with one line. | 2 |
| 4.8 | "Provenance gaps: two geography-validation metadata entries" | D | Two problems. The jargon is a conversation issue. The gap itself is a false positive: `provenance_gaps` reports any manifest string that starts with "unknown" (`awb_draft.py:2901`), so a validation column named `unknown_pickup` became a "gap" (`taxi-A/agent.md:21`). | 3 |
| 4.9 | Agent said it had "attached" files | A | The host has no attachment channel. No shipped text claims one. One line prevents it. | 2 |

### 5. Presentation edits cost analytical rework

| ID | Finding | Class | Evidence | Phase |
|---|---|---|---|---|
| 5.1 | Editing `run.py` to register one producer stales every result | D | Producing paths are all of `src/` (minus dispatch helpers) plus every file in the investigation folder outside `_NOT_CODE` (`awb_provenance.py:564-567, 601-604`). `run.py` holds every producer (`awb-init/assets/workbench/investigation/run.py:54-67`). This contradicts `docs/workbench-design.md:93`. | 3 |
| 5.2 | Editing an investigation `methodology.md` staled every result | D | Same mechanism: any file not on the deny list counts as code. retail-A left its note alone "because it participates in evidence hashes" (`retail-A/agent-notes.md:97`). | 3 |
| 5.3 | Adding a global `[parameters]` entry stales every result | I+ | Documented to agents: `settings.toml:1-3`; `awb_provenance.py:18-23, 198-203`. It is coarse, though: `run()` passes a query only the `$name` parameters it uses (`run.py:43-46`), so the evidence could scope parameters the same way. | 3 |
| 5.4 | A result first run on uncommitted code needs promoting twice | U | Not reproduced from the code. `record_finding` keeps a row whose table, checks and settings equal the prior baseline (`awb_provenance.py:1363-1367`). The double promotion may come from a `prior` the agent's adapted `run.py` did not capture. Reproduce first in Phase 3. | 3 |
| 5.5 | Charts cannot select rows; a top-10 chart needs a new recorded result | D | `_shape` writes every row of the result (`awb_draft.py:2314-2347`). The design asks for "one CSV of exactly the plotted values serialized from a recorded result" (`docs/workbench-design.md:75`). A recorded row selection keeps that trace. | 4 |
| 5.6 | The numbers check fires only at `check-draft` | D | `update_findings` (`awb_provenance.py:1403-1432`) checks no number in `--text`. The number reader lives only in `packaging/draft.py` (`awb_draft.py:1366`). | 3 |
| 5.7 | False positives: negated causal wording, slash pairs, dates, a DOI | I | Designed to err toward refusing (`docs/workbench-design.md:69`; `helpers.md:35`, "Reading fails safe"). A DOI (`10.24432/…`) is a cheap, safe skip (Phase 3, optional); keep the rest. | 3 (DOI only) |
| 5.8 | `findings.json` notes split inside parentheses | D | `--caveat` splits on every `;` (`awb_provenance.py:1432`), and its help (`:2308-2309`) does not say so (retail-B orchestrator observation 8). | 3 |

### 6. Review cost and substance

| ID | Finding | Class | Evidence | Phase |
|---|---|---|---|---|
| 6.1 | Up to 11 reviewer rounds per run; every edit stales the review | I+ | Specified: a review "is stale once, after it, the narratives … change" (`awb-package/references/review.md:33`). Release already reruns the whole review (`awb-release/SKILL.md:18`), so packaging rounds can be cheaper without weakening the gate. | 6 |
| 6.2 | Rules are read bullet by bullet: one wording rule gave 13 errors | D | Rule fields are Severity, Rule, Pattern and Fix (`awb_draft.py:2567`). Patterns match lines, and no field limits a rule to a slide, bullet or document. | 6 |
| 6.3 | "Countries plus non-countries sum to World" was promoted and passed four reviews; a 478 Mt double count existed | D | The review brief's step 3 (`review.md:22`) checks agreement and claim strength but not that a "checked" or reconciliation assertion traces to a recorded result. `state finding --status supported` warns about nothing (see 5.6). | 6, 3 |
| 6.4 | taxi-A's first deck passed checks and still needed five user corrections | R | Not a distinct defect. Its parts are covered by 1.x, 6.2 and 6.3. | — |

### 7. First-pass answers run ahead of the evidence

| ID | Finding | Class | Evidence | Phase |
|---|---|---|---|---|
| 7 | Chat answers stated untested explanations, treated a user's recollection as confirmed, compared groups without a check on what drove them | D | The invariants govern findings and claim strength (`AGENTS.md:34-36`), not chat answers built from exploration queries. `awb-explore/SKILL.md:35` labels exploratory observations only inside that skill. No rule says a user's statement is recorded as theirs, not as confirmed. | 2 |

### 8. Scoping interview skipped by Codex agents

| ID | Finding | Class | Evidence | Phase |
|---|---|---|---|---|
| 8 | init and scope ran in one turn, and open decisions went to the ledger unasked | D | `awb-scope/SKILL.md:25-42` says to interview. But `:42` finishes when each item is "settled … or held open as a ledger question", and `:63` reports user questions "to answer now or later". Both let a user-answerable decision be parked unasked. `README.md:84` promises an interview. | 2 |

### 9. Setup and environment

| ID | Finding | Class | Evidence | Phase |
|---|---|---|---|---|
| 9.1 | Bare `python3` everywhere; with a project venv every command lacks duckdb | D | 56 lines naming `python3 ` across the skills, references, `AGENTS.md`, guides and project README. The MCP server already resolves the project's `.venv`/`venv` or `AWB_PYTHON` (`awb-init/assets/awb_mcp.py:303-311`); the CLI path does not. | 5 |
| 9.2 | Install hint `… -m pip install` fails in a uv venv | D | `install_helpers.py:263` and the `requirements.txt` header at `:237`. | 5 |
| 9.3 | `quality.md` would not parse; custom rows rejected; no helper for analyst-authored issues | D | Contributory. The shipped template has the heading (`awb-init/assets/workbench/foundation/quality.md:5`), but `awb-init/SKILL.md:28` invites adapting templates, and co2-A's adapted copy lost it (`co2-A/agent-notes.md:37`). Template prose sits right after the table (`quality.md:10`), so appended rows fall outside it. `Table` reads only contiguous rows (`record_cleaning.py:72-90`) and then reports "issues not in the scan" (`:231`), a misleading message. Decisions accept only scan issues or existing IDs (`:231`). | 5 |
| 9.4 | `awb.py eda-scan` → "unknown command" | I | The CLI forms exist: `awb-explore/SKILL.md:19` and `awb-clean/SKILL.md:15` run the scripts by path. `AGENTS.md:20` names the scripts beside their MCP commands without saying they are not `awb.py` commands. | 5 |
| 9.5a | Every MCP write refused: "approval policy is never" | S | The harness set `approval_policy = "never"` (`kit/setup.sh:28, 53`); reads worked. | — |
| 9.5b | No read-MCP/write-CLI fallback rule | D (residual) | `AGENTS.md:20` says MCP when offered, otherwise CLI, with no rule for a refused write tool. Each agent worked it out alone. | 5 |
| 9.6a | `git init` blocked | S | Codex `workspace-write` protects `.git` (`kit/setup.sh:29`); "Operation not permitted" (`co2-A/agent-notes.md:8`). | — |
| 9.6b | No recorded no-Git mode; repeated "suggest committing" | D (residual) | `awb-init/SKILL.md:16` reports "code history is not established" once, but `AGENTS.md:44` and `workbench-guides/analysis.md:17` keep suggesting commits. Provenance already handles no Git (`awb_provenance.py:614-620`). | 5 |
| 9.7 | No guidance on landing zip or XLSX sources | D | Neither `awb-init/references/landing.md` nor `workbench-guides/data.md` mentions zip, XLSX, `read_xlsx`, or Excel serial dates. | 5 |
| 9.8 | Ancestor `CLAUDE.md` walk runs `test -e` up to `/` | R | Intended and documented: `awb-init/SKILL.md:14`, `README.md:74-75`. Existence checks only. | — |
| 9.9 | Sandbox `python3` was 3.9.6 and nothing bootstraps 3.10+ | S | The installer refuses clearly (`install_helpers.py:160-163`). Bootstrapping an interpreter is out of scope; the README quick-start should name the requirement (Phase 7). | 7 |

### 10. Release details

| ID | Finding | Class | Evidence | Phase |
|---|---|---|---|---|
| 10.1 | "BOARD REVIEW DRAFT" survived into release 001 | A | The agent wrote it; no shipped template contains it (searched `.agents/skills`). Release copies the draft byte for byte (`awb_draft.py:3033`). A warning before release is cheap insurance. | 4 |
| 10.2 | Release four or five folders deep; deliverables mixed with internal files; no "send these" note | D | The storage path is `<location>/<investigation>/<package>/released/<n>/` (`awb_draft.py:2971, 2981`). The draft mixes builder and audit files with deliverables (`package-contract.md:9-17`; `co2-A/human.md:18`). | 4 |
| 10.3 | taxi-A's ~20 audit JSON files in the release | A | `artifact-checks.json`, `review-state.json` and others are not shipped outputs (`taxi-A/human.md:19`). | — |
| 10.4 | A revision requested with the release was frozen before the user saw it | D | `awb-package/SKILL.md:89`: "finish any revision requested with it, then invoke the sibling awb-release", with no user check of the changed draft. | 4 |
| 10.5 | "Nothing outstanding" while VAT remained an open caveat | D | The agent's wording, but the release report has no unresolved-caveats item (`awb-release/SKILL.md:53`), although the spec puts "unresolved caveats" in the manifest (`docs/workbench-spec.md:236`). | 4 |

### 11. README and other observations

| ID | Finding | Class | Evidence | Phase |
|---|---|---|---|---|
| 11 | README written for the installer; jargon unexplained; promises an interview and a disposition prompt; omits the headline stop, extra slides, internal methodology | D | Install and admin material fills `README.md:18-76`; **Use** is `:78-118`. "interviews you" `:84`; "chosen a disposition for each flagged finding" `:108`, which applies only when flags exist (taxi-A had none). The deck description is one sentence (`:108`). | 7 |
| X.1 | `awb-brainstorm` never used | I | User-initiated by design. `awb-status` offers it only when few questions are open (`awb-status/SKILL.md:55`). The quick-start should say when it helps. | 7 |
| X.2 | Clean and explore are easy to skip (co2-B folded them into publish) | I | Preparation is question-driven (`docs/workbench-design.md:27`). `awb-status` already suggests both (`awb-status/SKILL.md:56-57`). The quick-start should list the requests in order. | 7 |

## Phases

Each phase is one PR, reviewed by a fresh Codex reviewer and a fresh Opus reviewer before merge (Phase 7 excepted; see there). Every phase that changes a helper's arguments or adds a command keeps it reachable over MCP: arguments pass through the existing `records`, `data`, `package` and `release` tools (`awb_mcp.py:12-15`), and a new command is added to a tool's command list and covered in `tests/test_awb_mcp.py`. Every phase that changes accepted behavior updates the matching sentences of `docs/workbench-spec.md`, `docs/workbench-design.md` and `CONTEXT.md` in the same PR, and adds a `CHANGELOG.md` fragment.

### Phase 1: Package contract and storyline control

Tracked in [#61](https://github.com/quentin-hickam/analytics-workbench/issues/61).

**Goal.** Let the package match the audience and the user's editorial choices without editing analytical records, and stop drafting from waiting on a preview the user may not need.

**Closes.** 1.1, 1.2, 1.3, 1.4, 1.5, 1.8, 3.1.

**Files.**
- `awb-package/SKILL.md`
- `awb-package/references/package-contract.md`, `references/review.md`, `references/helpers.md`
- `awb-package/assets/package-format/findings-template.md`, `deck-rules.md`, `assembly/m365.md`, `manifest-template.md`, and a new `methodology-note-template.md`
- `awb-package/assets/awb_draft.py`
- `awb-init/assets/workbench/investigation/brief.md` (Audience section)
- `awb-init/scripts/install_helpers.py`, to ship the new template
- `docs/workbench-spec.md`, `docs/workbench-design.md`, `CONTEXT.md` (Delivery package, Package format, Question ledger)
- Tests

**Changes.**
1. **Audience-facing methodology note.**
   - Add an optional `methodology-note.md` to the draft layout. It is a short plain-language account of method, sources, definitions, exclusions and limitations for the brief's Audience.
   - It follows the same translation rule as `findings.md`.
   - It is delivered beside the deck, like datasets, and is not attached to the builder.
   - `check-draft` runs its names, numbers, claims and Markdown checks on it when it exists.
   - `review-rules check` lists pattern matches in it.
   - The review brief adds it to the agreement check: it must not state what `methodology.md` does not support.
   - `awb-package` asks whether the audience needs one when the brief's Audience or the request mentions a methods note. Otherwise it offers one in the report.
   - Rename nothing: `methodology.md` stays the internal reference, and the report and README call it that.
2. **Required and optional slides.**
   - Settle which template sections are required: the title, **Answer**, at least one finding, **How we know**, and **Limitations and open caveats**. Limitations must stay because flagged findings are listed there (`package-contract.md:53`).
   - The rest are conditional or optional.
   - Make `outline_problems` enforce the required set and the order. Make `findings-template.md` say "required" or "optional" beside each section, so the template and the check agree.
3. **Appendix.**
   - Add a `## Appendix` deck section that, like **Findings**, holds `###` slides after the main sequence.
   - **How we know**, **Limitations**, **Supporting datasets** and individual findings may move there.
   - `deck-rules.md` tells the builder to start it with a divider slide titled "Appendix".
   - The outline reader and every check treat appendix slides like main slides. Claims checks still read appendix finding slides.
4. **Slide budget.**
   - Record a requested length in the brief's Audience section when the user gives one ("about 8 slides").
   - At the headline step, report main slides plus appendix slides against that number. When the count exceeds it, propose what moves to the appendix.
5. **Presentation order separate from ledger priority.**
   - Add an optional manifest field, `presentation_order`: the finding headings in the user's order, written at headline approval. It is recorded by hand like `allowed_numbers`, and `export` keeps it.
   - When it is present, the `storyline` check verifies that the finding slides follow it and that it lists every finding slide exactly once. Otherwise the ledger-derived order still applies as the default proposal.
   - Ledger priority keeps its analytical meaning: Open questions membership and status.
   - Update `docs/workbench-spec.md:136, 141`, `CONTEXT.md:86` ("A package's finding slides follow that tree") and `package-contract.md:29, 33`.
6. **Headline-checkpoint mode.**
   - Replace the unconditional wait (`SKILL.md:45`, `package-contract.md:33`) with two modes:
     - **preview-and-wait**: today's behavior;
     - **draft-then-review**: write the full draft with headlines marked provisional in the report, then ask for approval or reorder of the finished draft.
   - Default to draft-then-review when the request supplies the storyline or asks for the full draft. Default to preview-and-wait otherwise.
   - Record a stated preference in the brief's Audience section, so later packages reuse it.
   - Keep one hard stop in either mode: a consequential open choice, such as an audience wording the user has not approved or an unsettled usefulness criterion. Ask that in the same message.
   - The design goal of checking the storyline before M365 builds (`docs/workbench-design.md:73`) holds in both modes.
7. **Title and Answer.**
   - Keep them separate (1.8).
   - At the headline step, say in one plain sentence that the deck opens with a title slide and then the answer slide.

**Acceptance checks.**
- `tests/test_awb_outline.py`:
  - a draft missing **How we know** or **Limitations** fails with an `outline` row;
  - a draft without **Implications** passes;
  - `## Appendix` slides parse, keep their order, and count separately.
- `tests/test_awb_draft.py`:
  - a `methodology-note.md` with a view name, an untraced number, or causal wording above claim strength fails `check-draft` with rows that name the file;
  - without the file, `check-draft` behaves as before;
  - with `presentation_order` set to a non-ledger order, `storyline` passes; an order missing a finding, or listing one twice, fails;
  - `export` preserves the field.
- `tests/test_awb_review.py`: `review-rules check` lists matches in `methodology-note.md`.
- `tests/test_skill_surface.py`:
  - `awb-package/SKILL.md` names both checkpoint modes;
  - no shipped text says "wait for their answer before expanding the slides" unconditionally.
- `tests/test_deck_renderer.py`: the reference renderer builds an appendix divider.

**Depends on.** Nothing.

**Risks.**
- A third narrative file adds a place for the narratives to disagree. Mitigation: the review brief's agreement check covers it, and the file is optional.
- `presentation_order` keys on finding headings, which revisions change. Mitigation: `check-draft` refuses a stale order with a row naming the missing heading, so it cannot drift silently.
- Draft-then-review costs a full rewrite when the user rejects the storyline. Mitigation: preview-and-wait stays the default when the user has not supplied one.

### Phase 2: Conversation hygiene

Tracked in [#62](https://github.com/quentin-hickam/analytics-workbench/issues/62).

**Goal.** Chat carries decisions and results in the user's terms; bookkeeping stays in files.

**Closes.** 3.3, 4.1, 4.3, 4.4, 4.5, 4.6, 4.7, 4.9, 7, 8. The `AGENTS.md` half of 4.8: say what a provenance gap means, or say nothing.

**Files.**
- `awb-init/assets/workbench/AGENTS.md` (Conversation, Analytical invariants, Record maintenance)
- `awb-init/assets/workbench/README.md` (a commit-preference line)
- `awb-init/SKILL.md` (steps 4 and 5)
- `awb-scope/SKILL.md` (steps 2 and 4)
- `awb-status/SKILL.md` (Open work)
- `awb-status/scripts/collect_status.py`, only if root-question counts need a new field
- `awb-package/SKILL.md` and `awb-release/SKILL.md` (report sections)
- `docs/workbench-spec.md` (Instruction loading paragraph, Scoping behavior)
- Tests

**Changes.**
1. **The record footer** (`AGENTS.md:28`).
   - Drop ledger counts.
   - When the turn changed what the user asked about, say it in their terms: "Your five questions: 3 answered, 2 open." Otherwise name the next step only.
   - Never say a question needs the user without asking it in the same message.
2. **Plain decision requests.**
   - Add to Conversation: a pause is a plain decision request, saying what is needed, the recommendation and the alternative.
   - Never send the user to a skill or instruction file to justify it.
3. **Impact statements.**
   - Report an environment or tool limit with what it means for the user: whether they need to act, and what the workbench does instead.
   - Say nothing when they need do nothing and the outcome is unchanged.
4. **No claimed attachments.** Give file paths; never say a file was attached or sent.
5. **First-pass claims** (Analytical invariants).
   - A figure from a saved query is exploratory until `run.py` records it; say so.
   - Present an explanation the data has not tested as a question, not an answer.
   - Record what the user recalls as their statement, naming them, not as confirmed.
   - Name what a comparison has not controlled for when the user's decision depends on it.
6. **Scoping loophole.**
   - `awb-scope`: ask every open decision the user can answer before writing the records, and park one only when the user defers it.
   - Remove "to answer now or later" (`:63`).
   - Bundle same-level method questions, as the pacing rule already says (`:25`).
   - `awb-init` step 4: when the hand-off happens in the same turn, run `awb-scope`'s first interview round before creating the investigation, rather than creating the records and reporting open questions.
7. **Shorter setup report** (`awb-init` step 5).
   - Report the project root, the question handed to scoping, each item the user must act on with its impact, and the next request.
   - Move the rest to the installer's JSON and the files themselves.
   - Keep the host instruction-file line, because it needs the user.
8. **Status counts** (`awb-status` Open work).
   - Lead with the root and `must` questions as the user framed them: "5 of 5 answered".
   - Show sub-question counts after them, or only on request.
9. **Commit preference.**
   - A README line `Commits: on request` (default) or `as I go`, recorded when the user says so.
   - `AGENTS.md:44` commits analytical code as it goes when the line says `as I go`, and otherwise suggests at most once per session.
10. **Plain provenance gaps** (release and package reports). A gap is reported as what it means ("the Python version for one result was not recorded") or not at all when it changes nothing the user decides.

**Acceptance checks.**
- `tests/test_skill_surface.py`, which already tests instruction text (for example `test_every_question_add_example_carries_priority`):
  - the `AGENTS.md` footer example holds no ledger count;
  - Conversation contains the plain-decision, impact and no-attachment rules;
  - `awb-scope/SKILL.md` no longer contains "now or later";
  - the setup report list in `awb-init/SKILL.md` has at most five items.
- `tests/test_awb_status.py`, if the collector gains a root-question count: a ledger with 5 roots and 12 children reports 5 roots answered, separately from the totals.
- `scripts/measure-instruction-load.py` (`tests/test_measure_instruction_load.py`): the always-loaded `AGENTS.md` grows by no more than the lines it drops.

**Depends on.** Phase 1 for the package report wording only. Otherwise none.

**Risks.**
- Instruction text competes with host instructions (4.7 came from the host). The line reduces the behavior but cannot guarantee it.
- Asking all user decisions at scope time can lengthen the first exchange. Mitigation: the existing cap of four per round, each with a recommendation.

### Phase 3: Provenance churn

Tracked in [#63](https://github.com/quentin-hickam/analytics-workbench/issues/63).

**Goal.** An edit that cannot change a result's numbers never stales it. A number that no result records is flagged when the finding is worded, not at `check-draft`.

**Closes.** 4.8 (the false positive), 5.1, 5.2, 5.3, 5.4 (reproduce, then fix or drop), 5.6, 5.8, the DOI part of 5.7, and the `state finding` part of 6.3.

**Files.**
- `awb-init/assets/awb_provenance.py` (`record_evidence`, `_scoped`, `_NOT_CODE`, `update_findings`)
- `awb-init/assets/workbench/investigation/run.py` and `settings.toml`
- `awb-init/assets/workbench/workbench-guides/analysis.md`
- `awb-init/references/provenance.md`
- `awb-package/assets/awb_draft.py` (`provenance_gaps`; DOI skip in the number reader)
- `awb-package/references/helpers.md`
- `docs/workbench-design.md:93`, `docs/workbench-spec.md` (Stale wording if needed)
- Tests

**Changes.**
1. **An allow list replaces the deny list for investigation code.**
   - A result's producing paths become:
     - `run.py`;
     - the result's own queries;
     - its own producer module, `investigations/<name>/producers/<result-id>.py` when present;
     - any `code = [...]` paths its settings table declares;
     - `src/` minus the dispatch helpers, as today.
   - Prose, notes and any other file in the investigation folder never count.
2. **Producers out of `run.py`.**
   - `run.py` loads `producers/<result-id>.py` by result ID, so adding a result never edits `run.py`.
   - The `PRODUCERS` dict and its comment block (`run.py:54-67`) go.
   - `run.py` still counts as producing code, but it now changes only when its harness does, and a harness change should stale everything.
3. **Parameters scoped per result.**
   - Evidence records only the `[parameters]` a result's queries reference as `$name`, plus any its table lists in `parameters = [...]`. The settings comparison then sees only those.
   - `run.py` passes a producer only those names, so an undeclared read fails loudly instead of silently escaping staleness.
   - Update `settings.toml:1-3` and the docstring at `awb_provenance.py:18-23`.
4. **Reproduce 5.4.**
   - Add a test: record a result with uncommitted code, commit, rerun. Assert the row is `kept` and that one promotion suffices.
   - If the test fails, fix `record_finding`'s baseline comparison. If it passes, drop 5.4 and note it in the PR.
5. **Numbers warning at `state finding`.**
   - When `--text` is given, or `--status supported` is set, read the finding text with the package helper's number reader and warn on each number the result's table, profile, checks and settings do not record.
   - Load the reader lazily from `src/packaging/draft.py` when it is present.
   - Warn, never refuse.
   - Also warn when the text asserts a reconciliation or a completed check ("sums to", "reconciles", "checked every") and no check in the result's evidence records it. This is the substance behind co2-B's false "sum to World".
6. **`provenance_gaps`.** Report only `{"unknown": …}` objects and the runtime's `unread_requirements`. Drop the "string starts with unknown" rule (`awb_draft.py:2901`), which reads analytical settings values and column names as gaps.
7. **`--caveat` splitting.** Split notes only on `;` outside parentheses and brackets, and say in `--help` that `;` separates notes.
8. **DOI skip.** The number reader skips a DOI (`10.NNNN/…`) like a path, and `helpers.md` lists it among skipped contexts.

**Acceptance checks.**
- `tests/test_awb_provenance.py`:
  - adding a second result's producer module leaves the first result's `compare_evidence` all `pass`;
  - adding `investigations/<name>/notes.md` leaves every comparison `pass`;
  - editing `run.py` still fails `committed-code` for every result;
  - adding an unreferenced `[parameters]` key leaves a result current, while changing a referenced one stales it;
  - a declared `code` path counts.
- `tests/test_awb_state.py`:
  - `state finding --text` with an unrecorded number returns a warning naming it and still writes;
  - a recorded number at another precision traces;
  - "sums to" without a matching check warns;
  - `--caveat "a (b; c); d"` stores two notes.
- `tests/test_awb_draft.py`:
  - a manifest whose `analytical_settings` holds `"unknown_pickup"` yields no provenance gap, while `{"unknown": "reason"}` still does;
  - `10.24432/C5CG6D` is not a `numbers` row.
- `tests/test_awb_findings.py`: the uncommitted-then-committed rerun from change 4.
- Each new test fails on the current code before the fix.

**Depends on.** Nothing. It touches different files from Phases 1 and 2, so it can be developed alongside them and merged in order.

**Risks.**
- **The allow list can miss a real dependency.** Example: a helper module in the investigation folder that a producer imports. Mitigation: `code = [...]` declares it, and the analysis guide says so. Dropping a producing path is critical because a missed path makes a stale result read as current; the tests assert both directions.
- **`src/` still stales everything.** Finer `src/` dependency tracking, such as an import graph, is left out deliberately and noted in the design doc.
- **Package reader inside provenance.** Loading the package reader from provenance couples two helpers that `_NOT_PRODUCING` treats as independent. Mitigation: a lazy load with no import at module level, so provenance still works without `src/packaging/`.

### Phase 4: Delivered files: export shaping and release layout

Tracked in [#64](https://github.com/quentin-hickam/analytics-workbench/issues/64).

**Goal.** What the user receives is rounded, labeled for the audience, as long as the chart needs, and organized so a colleague knows which files to send.

**Closes.** 1.6, 1.7, 2.2, 5.5, 10.1, 10.2, 10.4, 10.5.

**Files.**
- `awb-package/assets/awb_draft.py` (`_shape`, `export`, `display_names`, `check_draft`, `release`, `_copy_to_storage`, `copy_releases`)
- `awb-package/SKILL.md`, `references/package-contract.md`, `references/helpers.md`
- `awb-package/assets/package-format/manifest-template.md`, `deck-rules.md`, `assembly/m365.md`
- `awb-release/SKILL.md`
- `awb-status/scripts/collect_status.py`, which reads release paths
- `awb-init/assets/awb_mcp.py`, if new `export` options need schema text
- `docs/workbench-spec.md` (directory convention, Packaging and release behavior), `docs/workbench-design.md` (chart-file paragraph)
- Tests

**Changes.**
1. **Rounding as a required gap.**
   - On export, a numeric column whose values carry more decimals than a display threshold, and that `[round]` does not cover, becomes a gap, listed with a `round_stub` like the existing `display_stub`.
   - `awb-package` fills it from the slide's number format before writing.
   - Add an optional `[percent]` list that multiplies fractions by 100 for display. Record it in the manifest's `charts` and `dataset_selection` entries, so `methodology.md` can state it.
2. **Value labels and per-result overrides.**
   - `[results."<id>".columns]` and `[results."<id>".values]` in `display.toml` override the global names for one result.
   - `export` warns when one column name feeds files from results with different questions and no override (the co2-B collision).
3. **Row selection.**
   - `--chart <result>[:<columns>][@first=<n>]` and `@where=<column>=<value>[,<value>]` select rows from the recorded result.
   - Results already have a stable total order (`workbench-guides/analysis.md:15`), so the first `n` rows are well defined.
   - The manifest's `charts` entry records the selection.
   - `check-draft` verifies that each chart file equals its result's table under the recorded selection, rounding and labels.
   - The number check is unchanged, since every plotted value is still a recorded value.
   - Update `docs/workbench-design.md:75` and the spec's chart-file sentence.
4. **Start-here note.**
   - `check-draft` (not `--verify-only`) writes `START-HERE.md` into the draft before writing the inventory. It is plain text in three parts:
     - **send these to your audience**: the deck once built, `methodology-note.md` when present, `datasets/`;
     - **to build the deck**: the attach list and one-line prompt from `assembly/m365.md`;
     - **internal**: `methodology.md`, `manifest.json`, `deck-rules.md`.
   - `--verify-only` verifies it like any other file.
5. **Shallower storage path.**
   - Copy releases to `<location>/<investigation>/<package>/<n>/`, dropping the `released/` segment, which repeats "releases" when the user names the location that.
   - Keep the in-project `deliveries/<investigation>/<package>/released/<n>/` path, which the directory convention fixes.
   - `collect_status.py` reads the new storage path.
   - No migration is needed.
6. **Draft markers.**
   - `check-draft` reports informational `draft_markers` rows for "draft", "working copy" or "not a numbered release" in the title, subtitle, headings, or the notes of the title slide.
   - `awb-release` shows them and asks the user to confirm or revise before running `release`.
7. **Review before releasing a folded revision.** `awb-package/SKILL.md:89`: when a revision comes with the release request, show the user the changed slides and wait for a yes before invoking `awb-release`, unless the user said to release without seeing it.
8. **Open caveats in the release report.** `awb-release/SKILL.md` **Report** lists every caveat released with the package, accepted dispositions included. It never calls the release clean while one remains.

**Acceptance checks.**
- `tests/test_awb_draft.py` (export):
  - an unrounded float column without `[round]` yields an `errors` row and a `round_stub`;
  - `[percent]` scales and is recorded;
  - a per-result override wins over the global name;
  - the collision warning fires;
  - `@first=10` writes 10 rows and records the selection;
  - `check-draft` refuses a chart file that differs from its result under the recorded selection.
- `tests/test_awb_draft.py` (check and release):
  - `START-HERE.md` is written, inventoried and verified;
  - "DRAFT" in the deck title yields a `draft_markers` row;
  - release copies to `<location>/<inv>/<pkg>/001/`;
  - `copy_releases` and `compare_trees` work on the new path.
- `tests/test_awb_status.py`: storage availability reads the new path.
- `tests/test_awb_mcp.py`: the `package` tool passes the new `--chart` syntax through.
- `tests/test_skill_surface.py`: `awb-package/SKILL.md`'s delivery-milestone paragraph requires the user's check of a folded revision.

**Depends on.**
- Phase 1, for `methodology-note.md` in the start-here note.
- Phase 3, only so the two PRs' `awb_draft.py` edits merge cleanly.

**Risks.**
- **Rounding at export can make a chart disagree with a narrative number written at another precision.** Mitigation: the existing `numbers` check still traces narrative numbers to the unrounded recorded value, within rounding.
- **`check-draft` writing a second file blurs its "checks plus inventory" role.** Alternative: `export` writes the note. But `export` runs before the methodology note is final, so `check-draft` is the right place; say so in the contract.
- **Selection syntax inside `--chart` is compact but easy to mistype.** Mitigation: `export` refuses an unknown column or an empty selection with a clear row.

### Phase 5: Setup robustness

Tracked in [#65](https://github.com/quentin-hickam/analytics-workbench/issues/65).

**Goal.** Commands run as written in the project's environment. Templates the helpers parse cannot be adapted into a broken shape. Each fallback is stated once.

**Closes.** 3.2, 4.2, 9.1, 9.2, 9.3, 9.4, 9.5b, 9.6b, 9.7.

**Files.**
- `awb-init/scripts/install_helpers.py`
- `awb-init/assets/awb_cli.py` (`src/awb.py`)
- `awb-init/assets/workbench/AGENTS.md` (Commands, Record maintenance), `README.md` (an interpreter line and a code-history line), `foundation/quality.md`, `workbench-guides/data.md`, `workbench-guides/analysis.md`
- `awb-init/SKILL.md` (steps 1.5, 1.3 report item, 3.3)
- `awb-init/references/landing.md`
- `awb-clean/scripts/record_cleaning.py`, `awb-clean/SKILL.md`
- `awb-init/assets/awb_mcp.py`, to keep the clean-record schema text current
- Tests

**Changes.**
1. **One interpreter, recorded once.**
   - The installer writes the interpreter it ran under to the project README as `Project interpreter: <path>`, the same line `AGENTS.md` and the skills refer to.
   - `AGENTS.md`'s Commands section says `python3` in every workbench command stands for that interpreter.
   - `src/awb.py` re-executes itself under the recorded interpreter, or under `.venv`/`venv` as `awb_mcp.py:303-311` does, when it is running under another one. Every documented `python3 src/awb.py …` line then works unchanged.
   - Skill-directory scripts (`eda_scan.py`, `scan_dataset.py`, `record_cleaning.py`) get the same one-line rule in their skills.
   - The 56 command lines stay as they are, which keeps this PR small.
2. **uv-aware install hint.** When the target interpreter has no `pip` module, and its `pyvenv.cfg` records `uv`, or `uv` is on `PATH`, print `uv pip install --python <interpreter> …` instead. Apply the same rule to the `requirements.txt` header line (`install_helpers.py:237, 263`).
3. **Install as routine setup.** `awb-init` step 3.3 runs the printed install command when it targets the project's own virtual environment, and reports it in one line. It asks only before installing into an interpreter outside the project. The host's own permission prompt still applies.
4. **Quality record the parser can read.**
   - The template marks its two section headings and tables as read by `record_cleaning.py`, so they are kept as written.
   - It moves its guidance prose above each table.
   - It names the ID format: `DQ-NNN`.
   - `record_cleaning.py` defaults new IDs to `DQ-` (`:127-133`), uses `DQ-004` in its help and in `awb-clean/SKILL.md:67`, and keeps continuing whatever prefix a project already uses.
   - When rows sit outside the table, it reports where they are, not "issues not in the scan".
5. **Analyst-authored issues.**
   - `record_cleaning.py` decisions accept a `new` list of issues the scanner did not emit. Each entry carries object, observation, evidence (a saved query path or reference) and the judgment columns.
   - Such rows get the next ID, no scan marker and no `quality.json` link.
   - This keeps one writer for `quality.md` and is already reachable over MCP as `records` `clean-record`.
6. **Fallback rules in `AGENTS.md` Commands.**
   - *Refused MCP writes:* when a write tool call is refused or unavailable, run the same command in its CLI form, keep using MCP reads, and say once, in plain words, that writes go through the command line.
   - *Scripts by path:* `eda_scan.py`, `scan_dataset.py` and `record_cleaning.py` are scripts in their skill folders, run by path as their skills show, never `awb.py` subcommands.
   - MCP stays the first choice wherever a tool works.
7. **No-Git mode.**
   - When `git init` fails or Git is absent, `awb-init` records `Code history: none (<reason>)` on a README line and reports it once.
   - `AGENTS.md:44` and `analysis.md:17` skip commit suggestions while that line says none.
   - Provenance already records `uncommitted` with checksums.
8. **Zip and XLSX landing** (`landing.md`, `data.md`).
   - Land the archive as received.
   - Publish from the extracted member through DuckDB's spreadsheet reader, and name its extension.
   - Read Excel serial dates under `all_varchar` explicitly.
   - Record which form is the retained original.

**Acceptance checks.**
- `tests/test_awb_install.py`:
  - the README gains the interpreter line;
  - in a venv without `pip` whose `pyvenv.cfg` names `uv`, the hint starts with `uv pip install --python`;
  - otherwise the existing hint is unchanged.
- `tests/test_awb_cli.py`: `src/awb.py` run by an interpreter other than a present `.venv/bin/python` re-executes under it, simulated with a stub venv. It does not loop when already under it.
- `tests/test_awb_clean.py`:
  - the shipped `quality.md`, adapted the way `awb-init` would adapt it (its guidance prose removed), still parses;
  - rows appended after the prose produce the new location message;
  - a fresh record allocates `DQ-001`;
  - a `new` analyst issue writes a row with the next ID and no link;
  - an existing `Q-` prefix project keeps `Q-`.
- `tests/test_skill_surface.py`:
  - `AGENTS.md` states both fallbacks;
  - no shipped help text uses `Q-004` as a quality ID.
- `tests/test_awb_mcp.py`: `clean-record` passes a `new` issue through.

**Depends on.** Phase 2, which also edits `AGENTS.md`. Merge this after it to avoid conflicts.

**Risks.**
- **Self-re-execution in `awb.py` can surprise users who run another interpreter on purpose.** Mitigation: `AWB_PYTHON` overrides, as for MCP, and the re-execution notes itself on stderr.
- **Installing without asking can collide with a site's package policy.** The host's command approval is the backstop; the rule is limited to the project's own venv.
- **The `DQ-` default changes IDs only for new projects.** No existing projects exist, so no migration is needed.

### Phase 6: Review economy and claim discipline

Tracked in [#66](https://github.com/quentin-hickam/analytics-workbench/issues/66).

**Goal.** Fewer, more exhaustive review rounds, with substance checked as hard as form.

**Closes.** 6.1, 6.2, 6.3 (review side).

**Files.**
- `awb-package/references/review.md`
- `awb-package/assets/awb_draft.py` (`review-rules add`, `review-rules check`, the rule parser at `:2567`)
- `awb-package/assets/awb-package-reviewer.agent.md`
- `awb-package/SKILL.md` (step 5)
- `awb-release/SKILL.md` (step 2: unchanged gate, wording only)
- `docs/workbench-spec.md:244`, `docs/workbench-design.md:99`
- Tests

**Changes.**
1. **Rule scope.**
   - Rules gain an optional `Scope` field: `line` (default, today's behavior), `slide`, or `document`.
   - `review-rules check` groups pattern matches by that scope, so one wording rule yields one verdict per slide or per document, not one per bullet.
   - `review-rules add --scope` sets it.
2. **One exhaustive pass.**
   - The brief tells the reviewer to report every violation in one pass, quoting each.
   - The caller repairs all of them before rerunning.
3. **Scoped re-review between packaging rounds.**
   - Within one `awb-package` request, a review after repairs may be limited to the changed lines, the prior report's violations, and every rule added since.
   - The reviewer gets the prior report and a diff.
   - A full review is still required before the request's final `check-draft`, and release always runs the full review (`awb-release/SKILL.md:18`, unchanged).
   - This keeps the gate and cuts the intermediate rounds.
4. **Checked and reconciliation assertions.**
   - Review step 3 adds a check: every sentence in either narrative or the methodology note asserting that something was checked, reconciles, sums to, or matches must cite the recorded result or check that establishes it.
   - A sentence without one is a narrative problem.
   - This pairs with Phase 3's warning at `state finding`.

**Acceptance checks.**
- `tests/test_awb_review.py`:
  - a `Scope: slide` rule with three matching bullets on one slide is listed as one slide entry with three lines;
  - `review-rules add --scope document` writes the field;
  - a malformed `Scope` value is a reported problem, and `add` refuses until it is repaired, as for other fields.
- `tests/test_skill_surface.py`:
  - `review.md` contains the reconciliation check and the scoped re-review rule;
  - `awb-release/SKILL.md` still requires the full review.

**Depends on.** Phase 1 (the methodology note joins the review) and Phase 3 (the shared reconciliation wording).

**Risks.**
- A scoped re-review can miss a violation that a repair introduced outside the changed lines, such as a heading rename breaking agreement. Mitigation: the full final review before `check-draft`, and the full release review.

### Phase 7: README

Tracked in [#67](https://github.com/quentin-hickam/analytics-workbench/issues/67).

**Goal.** An analyst can read one page and know what to say, what they will be asked, how many exchanges to expect, and what they will get.

**Closes.** 2.1, 9.9 (requirement stated), 11, X.1, X.2.

**Files.** `README.md` only. `scripts/build-dist.sh` changes only if the section markers move.

**Changes.**
1. **Order.** Put a "What you get" section and an analyst quick-start right after the opening paragraph.
2. **What you get.**
   - A deck outline, chart data, an optional audience-facing methods note, an internal methodology reference, and builder instructions. Not a .pptx.
   - The M365 Copilot PowerPoint agent is one builder, and a person can build the deck by hand from the same files.
   - A Copilot licence is needed only for the Copilot route.
3. **Quick-start.**
   - What to say first.
   - What you will be asked: storage locations, audience and length, a scoping round, and the headline checkpoint in the mode you choose.
   - The usual requests in order: init, scope, clean, explore, analyse, status, package, release, with brainstorm when few questions remain.
   - A typical exchange count.
   - Plain definitions of the five terms users stumbled on: canonical view, question ledger, receipt, disposition, review rule.
   - Say when a disposition is asked: only when a finding is flagged.
4. **Admin section.** Move the requirements, install, MCP, VS Code and `AGENTS.md`/`CLAUDE.md` material into an "Install and administer" section below the quick-start, unchanged in substance.

**Acceptance checks.**
- `scripts/build-dist.sh` still builds and its marker checks pass: no `](docs/` links, balanced `dist:exclude` markers (`build-dist.sh:57`).
- `tests/test_skill_surface.py`: README link targets resolve.
- A read-through confirms every behavior the quick-start promises matches the skills after Phases 1 to 6.

**Depends on.** Phases 1, 2, 4 and 5, whose behavior it describes.

**Risks.** It describes behavior, so it must merge last.

**Review.** This PR is docs-only. The standing preference is not to run the multi-model gate on docs-only PRs, so decide the review approach for this PR when it is opened rather than defaulting to the Codex and Opus pair.

## Recommended order

1. **Phase 1, the package contract.**
   - Highest reach: 6 of 6 runs, major.
   - It defines artifacts later phases name: `methodology-note.md`, `presentation_order`, the appendix and the checkpoint mode.
2. **Phase 2, conversation hygiene.**
   - Mostly instruction text, so it is cheap, and every run benefits from it.
   - It must precede Phase 5, because both edit `AGENTS.md`.
3. **Phase 3, provenance churn.**
   - The largest agent-time cost.
   - It shares no files with Phases 1 and 2 beyond `awb_draft.py`'s `provenance_gaps`, so it can be developed in parallel and merged third.
4. **Phase 4, delivered files.**
   - Needs Phase 1's methods note for the start-here note.
   - Lands after Phase 3 so the two `awb_draft.py` edits merge cleanly.
5. **Phase 5, setup robustness.**
   - Every item has a working workaround today: the MCP route already finds the venv, and agents fell back to the CLI.
   - It follows Phase 2's `AGENTS.md` edits.
6. **Phase 6, review economy.** Builds on Phase 1's coverage and Phase 3's reconciliation wording.
7. **Phase 7, README.** Last, because it describes the result of every other phase.

**If fewer PRs are wanted,** Phase 6 can fold into Phase 1. That makes Phase 1 the largest PR, but it removes a second pass over `review.md`.

## Rejected, artifact and agent-authored items

**Rejected:**
- **2.4 A rendered deck preview.** Shipping a renderer is an open design decision (`docs/workbench-design.md:79`), not a UX defect.
- **3.4 Asking before investigating an agent-found anomaly.** This is the intended question-bounded preparation (`AGENTS.md:32`).
- **6.4 taxi-A's five post-review corrections.** Not a separate defect; 1.x, 6.2 and 6.3 cover its parts.
- **9.8 The ancestor `CLAUDE.md` walk.** Intended, documented, and limited to existence checks (`awb-init/SKILL.md:14`, `README.md:74-75`).
- **Bootstrapping a Python 3.10+ interpreter (part of 9.9).** The installer refuses an old interpreter clearly. Installing interpreters is outside the workbench's job.

**Simulation artifacts** (from the harness, not the workbench):
- **9.5a MCP write denials.** The harness ran Codex with `approval_policy = "never"` (`kit/setup.sh:28, 53`). An interactive user approves the call. The residual gap, no stated fallback, is 9.5b in Phase 5.
- **9.6a The blocked `git init`.** Codex's `workspace-write` sandbox protects `.git`. The residual gap, no recorded no-Git state, is 9.6b in Phase 5.
- **9.9 Sandbox Python 3.9.6.** A harness interpreter choice. Phase 7 only states the requirement in the quick-start.

**Agent-authored** (no shipped instruction asks for it; a cheap guard is noted where one helps):
- **2.3 The taxi-A renderer and exporter patch.** The agent's own initiative. Phase 4's row selection removes the reason it patched the exporter.
- **4.3 The contradictory footer.** Agent arithmetic. Phase 2 removes the count.
- **4.7 `SKILL.md` links.** Host instructions, per `retail-A/agent.md:32`. Phase 2 adds a counter-instruction.
- **4.9 "Attached" claims.** The agent's wording. Phase 2 adds one line.
- **10.1 "BOARD REVIEW DRAFT".** The agent's label. Phase 4 adds a `draft_markers` warning.
- **10.3 About 20 audit JSON files in taxi-A's release.** The agent's own files. Phase 4's start-here note separates deliverables either way.

**Unverified:**
- **5.4 Promote twice after an uncommitted first run.** The code path suggests a rerun with an identical table is `kept`. Phase 3 reproduces it before changing anything.
