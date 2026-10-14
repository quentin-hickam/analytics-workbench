# Casefile: a conversational data-analysis package for agentic harnesses

*Design proposal, blind ideation session, 2026-10-14*

---

## 0. The short answer

The package should not be built from prompt files, and it should not be one large prompt. It has four parts, and each part handles one thing the others cannot:

| Layer | Artifact type | What it is responsible for | Why this type |
|---|---|---|---|
| **Verbs** (what the human types) | ~7 user-invocable **Agent Skills** (`SKILL.md`) | The human's vocabulary: `/analyze`, `/data`, `/questions`, `/status`, `/story`, `/deck`, `/check` | Skills are the one format that Copilot in VS Code, Copilot CLI and Copilot cloud agent all load. They show up in the `/` menu with an argument hint, they load progressively, and they can carry scripts and templates. Claude Code, Codex and others read the same format. |
| **Craft** (what the agent knows) | ~5 model-only **Agent Skills** (`user-invocable: false`) | Data profiling and contextualization, ledger discipline, evidence standards, chart grammar, narrative construction | These load automatically when relevant and stay out of the human's `/` menu. |
| **Discipline** (what is always true) | A short **always-on instruction block** (`.github/copilot-instructions.md` / `AGENTS.md`) | "Keep the ledger current, cite findings, end turns with a delta." These rules apply even when the human never types a command. | Skills load only when matched. Free-form chat needs a floor that holds on every turn. |
| **Integrity** (what must not drift) | A small deterministic **engine**: the `casefile` CLI, also served as an MCP server | It owns the state files and validates schemas, IDs, provenance hashes, staleness, and story-to-evidence links. It also renders charts and decks. | An LLM editing YAML by hand will eventually corrupt the ledger. The skills tell the agent *when* and *why* to act. The engine makes *how* the state changes deterministic. |

There is also an optional **custom agent** (`analyst.agent.md`) that pins tools and a preferred model and adds handoff buttons in VS Code. It improves the experience but nothing depends on it.

The human's experience comes down to one principle: **the conversation is the interface, commands are shortcuts, and the files are the memory.** A human who never types a slash command should still get a ledger, contextualized data and a deck. The commands make the main moves easy to discover and give the human a reliable way to get back on track after a chat resets.

---

## 1. Why this shape and not the alternatives

- **Prompt files (`.prompt.md`)**: these are single-shot, cannot bundle resources, and VS Code's current docs mark them deprecated for Agent Host sessions with a migration path to skills. They are not a foundation for new work.
- **Custom agent only**: an agent is a persona you switch into. It is not a verb you can use mid-conversation. Handoffs and tool pinning are VS Code-specific, and an agent-only package makes the human "enter a mode" before anything works.
- **MCP server only**: MCP provides tools but no workflow knowledge. MCP prompts do appear in the slash menu, but under server-prefixed names, and they cannot carry the craft guidance (narrative rules, chart grammar) that makes the output good.
- **One monolithic instruction file**: it is always loaded and costs context on every turn. It also cannot be invoked as a verb and grows without limit. We keep the always-on part under about 40 lines and push everything else into skills that load progressively.

---

## 2. Package layout

### 2.1 Source repository (what we ship)

The layout follows the Agent Plugins 1.0 convention: portable components sit at the root and Copilot-specific components sit under `com.github.copilot/`. A legacy `plugin.json` and `.claude-plugin/plugin.json` sit alongside for older loaders.

```
casefile/
├── plugin.json                         # Agent Plugins 1.0 manifest ($schema pinned)
├── .claude-plugin/plugin.json          # legacy / Claude Code manifest (same components)
├── mcp.json                            # casefile engine as MCP server (stdio: `uvx casefile mcp`)
├── skills/
│   ├── analyze/SKILL.md                # USER VERB  start or resume an investigation
│   ├── data/SKILL.md                   # USER VERB  add / explain a data source
│   ├── questions/SKILL.md              # USER VERB  show / manage the question ledger
│   ├── status/SKILL.md                 # USER VERB  "where are we?"
│   ├── story/SKILL.md                  # USER VERB  build / revise the storyline (ghost deck)
│   ├── deck/SKILL.md                   # USER VERB  produce deck inputs + render
│   ├── check/SKILL.md                  # USER VERB  pre-share review
│   ├── data-context/                   # MODEL-ONLY profiling & semantic inference
│   │   ├── SKILL.md
│   │   └── reference/column-semantics.md
│   ├── question-ledger/                # MODEL-ONLY ledger lifecycle rules
│   │   ├── SKILL.md
│   │   └── reference/state-machine.md
│   ├── evidence/                       # MODEL-ONLY findings, provenance, key numbers
│   │   └── SKILL.md
│   ├── charts/                         # MODEL-ONLY Vega-Lite grammar + house style
│   │   ├── SKILL.md
│   │   └── reference/chart-chooser.md
│   └── narrative/                      # MODEL-ONLY pyramid / SCQA / action titles
│       ├── SKILL.md
│       └── reference/storyline-patterns.md
├── com.github.copilot/
│   ├── agents/analyst.agent.md         # optional persona with handoff buttons
│   └── hooks/hooks.json                # optional: run `casefile lint --quiet` at turn end
├── templates/
│   ├── copilot-instructions.snippet.md # always-on discipline block (also AGENTS.md form)
│   ├── vscode-settings.json            # terminal auto-approve for `casefile *`, etc.
│   └── deck/default.potx               # neutral, legible PowerPoint template
└── engine/                             # Python package `casefile` (published to PyPI)
    ├── pyproject.toml                  # deps: duckdb, pyyaml, jsonschema, vl-convert-python, python-pptx, mcp
    └── casefile/{cli.py, mcp_server.py, ledger.py, profile.py, story.py, deck.py, schemas/*.json}
```

### 2.2 Install targets

| Route | How | Result |
|---|---|---|
| Copilot CLI | `copilot plugin install <org>/casefile` | Skills, agent, MCP and hooks are registered |
| Copilot cloud agent | `.github/copilot/settings.json` → `"enabledPlugins": ["casefile@<marketplace>"]` | The same components are available on the cloud agent |
| VS Code (plugin) | Agent plugin from the Extensions view (still experimental in some builds) | Skills appear in the `/` menu |
| **Repo-local (the fallback that always works)** | `uvx casefile install` | Copies skills into `.github/skills/`, the agent into `.github/agents/`, appends the discipline block to `.github/copilot-instructions.md` (creating it if needed), writes `.vscode/mcp.json`, and merges recommended `.vscode/settings.json`. `--harness claude` also writes `.claude/skills/`. `--harness codex` writes `AGENTS.md` plus the skills dir. |

Repo-local install is the default recommendation for teams. The skills are versioned with the analysis, every collaborator gets them by cloning, and the commands are plain `/analyze` rather than a plugin-prefixed `/casefile:analyze` (see Risk R3).

### 2.3 Workspace state (what the package creates in the user's project)

The state is visible, diffable and readable by humans. It lives in `analysis/`, not a hidden dot-directory, because the human should feel they own it.

```
analysis/
├── .casefile.yaml                      # active investigation pointer, settings (privacy mode, deck format)
└── churn-q3/                           # one folder per investigation (slug)
    ├── BRIEF.md                        # HUMAN-OWNED: question, audience, decision, scope, deadline
    ├── context/
    │   ├── sources.yaml                # ENGINE: registered data, fingerprints, grain, coverage
    │   ├── profiles/subs.json          # ENGINE: mechanical profile (never hand-edited)
    │   ├── dictionary.yaml             # SHARED: column meanings, units, confidence, who confirmed
    │   ├── glossary.md                 # HUMAN-OWNED: business terms ↔ metric definitions
    │   └── caveats.yaml                # SHARED: data quality issues ("watch-outs")
    ├── ledger.yaml                     # ENGINE-OWNED: canonical question ledger
    ├── QUESTIONS.md                    # GENERATED: human view of the ledger
    ├── findings/F-007.yaml             # ENGINE-VALIDATED: claim + evidence + key numbers
    ├── work/q012_churn_by_plan.py      # AGENT: reproducible scripts / SQL
    ├── runs/                           # ENGINE: run manifests (inputs hashes, outputs, timestamps)
    ├── exhibits/X-004.vl.json|.svg|.png|.csv   # chart spec, renders, and the data behind it
    ├── story/
    │   ├── storyline.yaml              # the narrative spine (see §6)
    │   ├── GHOST_DECK.md               # GENERATED: headlines only, the readability checkpoint
    │   ├── deck.md                     # GENERATED: Marp markdown with speaker notes
    │   ├── deck.json                   # GENERATED: harness-neutral slide spec
    │   └── deck.pptx                   # RENDERED (optional)
    └── journal.md                      # APPEND-ONLY: decisions, assumptions, human confirmations
```

Ownership rules, which the engine enforces and the skills state:

- **HUMAN-OWNED** files: the agent proposes edits and makes them only with assent. The engine never overwrites them.
- **ENGINE-OWNED** files: the agent changes them only through `casefile` commands or MCP tools, never by direct edit. If the human hand-edits `ledger.yaml`, `casefile lint` validates the result and reports any breakage in plain language.
- **GENERATED** files: they are re-rendered on every state change and carry a "do not edit — generated from ledger.yaml" banner.
- **SHARED** files: either party may edit them. Each entry records `confirmed_by: human|agent`.

---

## 3. The human side: commands, conversation contract, example

### 3.1 The seven verbs

Copilot shows each `argument-hint` in the input box after the human types the command.

| Command | Argument hint shown in the chat box | What the human gets |
|---|---|---|
| `/analyze` | *what you want to find out, and where the data is* | Starts a new investigation or resumes the active one. On a cold start it asks three questions at most (question, audience/decision, data), each with a proposed default. |
| `/data` | *a file, folder, table, or connection — or a column you're unsure about* | Registers and profiles a source and returns a **data card**: a plain-language description plus up to three "is this right?" checks. With a column name it explains that column. |
| `/questions` | *optional: "open", "waiting on me", or a question to add* | Shows the ledger grouped as **Waiting on you / In progress / Answered / Set aside**. Accepts natural edits ("park 15", "merge 9 into 4"). |
| `/status` | *(none)* | A one-screen orientation: the question, the current best answer, what is open, what is blocking, and the suggested next step. This is the recovery command after a chat reset. |
| `/story` | *optional: audience or emphasis, e.g. "for the CFO, 6 slides"* | A **ghost deck**: headlines only, read top to bottom. The human revises the story here, before any rendering happens. |
| `/deck` | *optional: format (pptx, marp, pdf) or template path* | Deck inputs plus a rendered deck, with a lint report written in human language. |
| `/check` | *(none)* | A pre-share review: unsupported claims, stale data, open must-questions, chart legibility, and numbers that do not trace to a finding. |

Free text works without any command. "What's left?" behaves like `/questions open`, "where are we" like `/status`, and "make me slides" like `/deck`. The skill descriptions are written so that Copilot matches these phrasings, and the always-on block says so explicitly.

### 3.2 The conversation contract (how the machinery stays out of the way)

These rules are written into the always-on block and repeated in each verb skill. They are the main mechanism that keeps the experience accessible.

1. **Answer first, in the human's words.** The first sentence of a reply is the answer or the number. Method comes after, and only briefly.
2. **The machinery is cited, not narrated.** Write "(script: `work/q012…py`)" as a link. Never write "I will now call casefile q answer with --finding F-007".
3. **Every state-changing turn ends with a one-line ledger delta**, for example `Questions: answered 1 · opened 2 (1 needs you) · next: compare by region`. A turn that changed nothing gets no footer.
4. **Asks are batched and come with defaults.** At most three questions to the human at once, each with what the agent will assume if the human does not answer: "I'll treat `amount` as cents unless you say otherwise." An ask never stops progress that does not depend on it.
5. **IDs are handles the human may use but never needs.** Lists show short IDs (Q12, F7), and the agent understands "the monthly-plan question" just as well as "Q12".
6. **Vocabulary map.** The agent speaks the human column and thinks in the machine column.

   | Machine term | Human term |
   |---|---|
   | ledger | questions / the list |
   | finding | what we found |
   | exhibit | chart |
   | caveat | watch-out |
   | source / profile | data / what's in the data |
   | storyline / ghost deck | the story / the outline |
   | stale | out of date (data changed) |

7. **Consequential changes need a yes.** This covers dropping or parking a *must* question, changing `BRIEF.md`, retracting a finding, and overwriting a rendered deck the human edited.
8. **Show the work on request.** "How did you get that?" returns the method sentence, the source list with date coverage, the script link and any watch-outs. That content comes straight from the finding record, so it is consistent every time.
9. **Recover from resets silently.** Every verb starts by calling `casefile status --json`, a compact digest of about 1–2k tokens, instead of re-reading files or relying on chat history.

### 3.3 Example conversation (Copilot Chat in VS Code, `analyst` agent or default agent)

> **Human:** `/analyze` why did churn go up last quarter? data's in data/subscriptions.parquet, it's for Dana (VP Customer Success) — she wants to know if a retention offer is worth funding
>
> **Agent:** Started an investigation called **churn-q3**. I wrote what I understood to `BRIEF.md`:
> - **Question:** why did churn rise in Q3 2025?
> - **For:** Dana (VP Customer Success). **Decision:** whether to fund a retention offer.
>
> Here's what's in the data:
> **subscriptions.parquet** has one row per subscription per month, Jan 2023 to Sep 2025 (48,210 rows, 6,912 customers). It has plan type (monthly/annual), region, MRR, and a status field.
>
> Two quick checks, with my assumption in brackets:
> 1. Is `mrr` in **cents**? [Yes: values run 900–49,900, which looks like $9–$499.]
> 2. Is `status = 'paused'` counted as churned? [No, I'll treat paused as still active.]
>
> I've broken the main question into four parts I'll work through. Q2 and Q3 are next:
> Q2 Is the rise real or a data artifact? · Q3 Which customers drove it? · Q4 When exactly did it start? · Q5 What would an offer need to recover to pay off?
>
> `Questions: opened 5 (2 need you) · next: confirm the rise is real`
>
> **Human:** yes cents. paused should count as churned actually, that's how finance does it
>
> **Agent:** Got it. Paused now counts as churned, and I added that to the glossary as finance's definition. With that definition Q3 churn is **5.8%, up from 4.0% in Q2**, so the rise is real. It is not a reporting artifact: the row counts and customer IDs are continuous across the quarter boundary.
>
> `Questions: answered 1 (Q2) · next: which customers drove it`
>
> **Human:** is it the monthly people?
>
> **Agent:** Mostly. **Monthly-plan churn went from 4.6% to 7.4%; annual stayed flat at about 1.1%.** Monthly plans account for 83% of the increase. One watch-out: 212 rows in August have no region, so the regional split I'm running next will carry a footnote.
> (chart: `exhibits/X-004.svg` · script: `work/q003_churn_by_plan.py`)
>
> I also noticed monthly churn starts climbing in the **first full month after the July 1 price change**, so I opened a question about that.
>
> `Questions: answered 1 (Q3) · opened 1 (Q6: is the July price change the trigger?) · next: Q6`
>
> **Human:** park the region thing, Dana doesn't care
>
> **Agent:** Parked Q7 (regional breakdown). Reason recorded: *out of scope for Dana's decision*. The August missing-region watch-out stays on file but won't appear in the deck.
>
> *(…two more exchanges, Q4–Q6 answered…)*
>
> **Human:** `/story` for Dana, keep it short
>
> **Agent:** Here's the story as headlines only. Read top to bottom and it should make sense on its own:
>
> 1. **A targeted monthly-plan offer is the cheapest way to recover Q3's churn spike.**
> 2. Churn rose from 4.0% to 5.8% in Q3, and the rise is real, not a reporting change.
> 3. Monthly plans drove 83% of the increase; annual customers didn't move.
> 4. The climb starts the month after the July 1 price change, and is steepest on the plan with the largest increase.
> 5. An offer that wins back 1 in 4 at-risk monthly customers pays for itself within 5 months.
> 6. Still open: we haven't tested whether a discount or a plan downgrade retains better.
>
> Appendix: definitions (churn incl. paused), data coverage, watch-outs.
>
> Slide 5 rests on an assumption you haven't confirmed: offer cost = one month's MRR. OK to keep, or do you have a number?
>
> **Human:** use 50% off for 2 months. and make the deck
>
> **Agent:** Updated. The payback changes to **4 months**, and slide 5's headline is updated to match. The deck is at `story/deck.pptx` (also `deck.md` if you use Marp). Six slides plus a two-slide appendix. Every number on the slides traces to a finding, and each chart puts the comparison its headline describes in a highlight color.
> `/check` found nothing blocking. One note: Q8 (discount vs downgrade) is still open, and it's shown on slide 6 as a next step rather than hidden.

The human never sees YAML and never learns the word "finding". They still get a reproducible, auditable trail behind every sentence.

---

## 4. Data contextualization

The goal is for the agent to understand what the data *means* (grain, units, definitions, coverage, quality) before it computes anything, and for that understanding to carry through to every finding and every slide footnote.

### 4.1 The four layers

1. **Mechanical profile (engine, deterministic).** `casefile profile <source>` uses DuckDB to read CSV, Parquet, Excel, JSON, or SQL via attached databases. It produces: schema and physical types, row count, null rates, distinct counts, min/max/quantiles, top-k values, date coverage and gaps, candidate keys, **inferred grain** (the minimal unique column set, e.g. `(subscription_id, month)`), and join-key overlap with the other registered sources. The output goes to `context/profiles/<source>.json`. **The agent never needs raw rows to understand the shape.**
2. **Semantic inference (agent, guided by the `data-context` skill).** For each column the agent proposes a meaning, unit, role (`id | dimension | measure | time | flag | free_text`) and a confidence level, and cites its evidence ("values 900–49,900 in steps of 100 → cents").
3. **Human confirmation, used sparingly.** Only columns that are **low-confidence and high-impact** go to the human, where high impact means the column is referenced by an open *must* question. Confirmations are recorded with `confirmed_by: human` and a journal entry.
4. **Caveats register.** Data-quality issues become `caveats.yaml` entries with a scope (which source, columns and rows). A **finding inherits the caveats of every source and column it touched.** That inheritance is how watch-outs reach the deck footnotes without anyone remembering to add them.

### 4.2 Schemas

`context/sources.yaml`

```yaml
- id: subs
  label: "Subscriptions (monthly snapshots)"
  location: data/subscriptions.parquet      # or duckdb/postgres URI; credentials never stored here
  fingerprint: sha256:ab12…                  # content hash (files) or schema+rowcount+max(updated_at) (tables)
  registered: 2025-10-02T14:11:00Z
  grain: [subscription_id, month]
  coverage: {time_column: month, from: 2023-01, to: 2025-09}
  rows: 48210
  card: >                                    # the human-readable "data card" sentence
    One row per subscription per month, Jan 2023–Sep 2025, with plan type,
    region, MRR (in cents) and status.
```

`context/dictionary.yaml`

```yaml
subs.mrr:
  meaning: "Monthly recurring revenue for the subscription in that month"
  role: measure
  unit: USD cents
  aggregation: sum            # sum | mean | last | none; guards against averaging a total
  confidence: high
  confirmed_by: human         # human | agent
  evidence: "Range 900–49,900, step 100; human confirmed 2025-10-02"
subs.status:
  meaning: "Subscription state at month end"
  role: dimension
  values: {active: "billing", paused: "billing suspended — counts as churned (finance definition)", cancelled: "ended"}
  confidence: high
  confirmed_by: human
  glossary: churn             # links to glossary.md#churn
```

`context/caveats.yaml`

```yaml
- id: C-002
  text: "212 rows in Aug 2025 have no region"
  scope: {source: subs, columns: [region], filter: "month = '2025-08'"}
  severity: minor              # minor | material | blocking
  affects_deck: footnote       # footnote | appendix | none
```

### 4.3 Keeping context small for the model

`casefile context --for Q-006 --json` returns only the dictionary entries, glossary terms and caveats relevant to the columns that a question's scripts touch, or are likely to touch. The skills tell the agent to request context this way and not to read the full dictionary. This matters on Copilot, where context windows and the model's attention are often the binding constraint.

### 4.4 Staleness

If a source's fingerprint changes, `casefile status` marks every finding whose run manifest used the old fingerprint as **stale**, the ledger re-opens the questions those findings answered (as `needs_recheck`), and `/check` blocks the deck until they are re-run or explicitly accepted.

### 4.5 Privacy mode

`.casefile.yaml: privacy: aggregate_only | samples_masked | full`. In `aggregate_only` mode the skills forbid printing raw rows to chat, and `casefile peek` returns masked samples (IDs hashed, free text truncated). This is a policy enforced by the instructions, not a security boundary, and the docs must say so.

---

## 5. The question ledger

### 5.1 Purpose

The ledger serves three purposes at once:
1. **Working memory** that survives chat resets.
2. **Accountability**: nothing the human asked silently disappears.
3. **The storyline skeleton**: the ledger is a tree, and that tree is the pyramid the deck is built from (see §6).

### 5.2 Question kinds

| kind | Example | Who usually answers |
|---|---|---|
| `analytic` | "Did monthly plans drive the increase?" | agent, with evidence |
| `data` | "Is `mrr` in cents?" | agent (inference), human confirms |
| `definition` | "Does paused count as churned?" | human / business owner |
| `scope` | "Does Dana care about regions?" | human |
| `assumption` | "What does an offer cost?" | human, or agent with a stated default |

Kinds `data`, `definition`, `scope` and `assumption` with `owner: human` make up the **"Waiting on you"** group.

### 5.3 Schema (`ledger.yaml`, engine-owned)

```yaml
investigation: churn-q3
root: Q-001
questions:
  - id: Q-006
    text: "Is the July 1 price change the trigger for the monthly-plan churn rise?"
    kind: analytic
    parent: Q-003                  # tree structure; root's children = the key line of the story
    priority: must                 # must | should | could   (relative to the BRIEF decision)
    status: answered               # see state machine
    owner: agent                   # agent | human | "@finance" (external)
    origin: {by: agent, at: 2025-10-02T15:40Z, why: "noticed timing coincidence in X-004"}
    blocked_by: []
    assumption_default: null       # for asks: what the agent will assume if unanswered
    answer:
      summary: "Yes, likely: churn climbs from the first full month after the change, steepest on the plan with the largest increase."
      findings: [F-009, F-010]
      confidence: medium           # high | medium | low — drives hedging language on slides
      at: 2025-10-02T16:05Z
    resolution: null               # required text for parked / dropped / superseded
    story: {role: key_line, slide: SL-04}   # set by /story; key_line | support | appendix | open_thread | none
    history:
      - {at: 2025-10-02T15:40Z, to: open}
      - {at: 2025-10-02T15:52Z, from: open, to: in_progress}
      - {at: 2025-10-02T16:05Z, from: in_progress, to: answered, by: agent}
```

### 5.4 Lifecycle (state machine, enforced by the engine)

```
            ┌──────────────► parked ─────────────┐
            │  (needs reason; must → needs human yes)
 open ──► in_progress ──► answered ──► needs_recheck ──► in_progress
   │          │               │        (source changed)
   │          ▼               └──► superseded (replaced by better-framed Q; link required)
   │       blocked (blocked_by: [Q..] or owner: human)
   └──────► dropped (needs reason; must → needs human yes)
```

Guards in the engine, where a violation returns a plain-language error the agent can relay:

- `answered` requires at least one finding with `status: verified`, or, for `definition`/`scope`/`assumption` kinds, a journal entry recording the human's answer.
- `dropped` and `parked` require `resolution`. For `priority: must` they also require `--confirmed-by human`, which the skill only passes after an explicit yes in chat.
- `superseded` requires `superseded_by`. The new question inherits the old one's children.
- When all children of a question are answered, the engine flags the parent as **ready to synthesize**. The agent then writes the parent's answer, so the pyramid fills from the bottom up.
- Duplicate detection: `casefile q add` warns when the new text closely matches an existing question (simple token similarity), and the skill tells the agent to merge rather than duplicate.

### 5.5 Agent behavior rules (the `question-ledger` skill)

- Open a question when **the work reveals something the BRIEF decision might depend on**. Do not open one for every passing thought. Questions that are not relevant to the decision become `could` and are not surfaced as asks.
- Surface new questions in the turn footer and do not interrupt the answer with them.
- Never let a human request disappear: a question the human asks in free text is recorded (as `origin.by: human`) before it is worked on.
- Rebalance at milestones (end of `/data`, before `/story`) by proposing: "3 open *could* questions don't affect Dana's decision. Set them aside?"

### 5.6 Human view (`QUESTIONS.md`, generated; `/questions` prints a compact form)

```markdown
# Questions — churn-q3
**Main question:** Why did churn rise in Q3 2025? → *Monthly plans after the July price change; an offer pays back in ~4 months.*

## Waiting on you (1)
- **Q8** Should we test discount vs downgrade before recommending? *(I'll show it as a next step if unanswered)*

## In progress (0)

## Answered (6)
- **Q2** Is the rise real? → Yes: 4.0% → 5.8%, no reporting break. *(high confidence)*
- **Q3** Who drove it? → Monthly plans: 83% of the increase.
- …

## Set aside (1)
- **Q7** Regional breakdown — *parked: out of scope for Dana's decision*
```

---

## 6. From findings to a deck: evidence, exhibits, narrative

### 6.1 Findings (the unit of truth)

Every claim that can appear on a slide must be a finding, and every number on a slide must be one of a finding's **key numbers**. That rule is the main defense against hallucinated figures in the deck.

`findings/F-007.yaml`

```yaml
id: F-007
claim: "Monthly-plan churn rose from 4.6% (Q2) to 7.4% (Q3); annual held at ~1.1%."
answers: [Q-003]
status: verified                    # draft | verified | retracted | stale
confidence: high
method: "Logo churn = customers moving active→(cancelled|paused) in month / active at start of month; quarterly = mean of months."
run: runs/2025-10-02T15-31-07_q003.json   # engine manifest: script hash, source fingerprints, outputs
key_numbers:
  monthly_churn_q2: {value: 0.046, format: "0.0%"}
  monthly_churn_q3: {value: 0.074, format: "0.0%"}
  annual_churn_q3:  {value: 0.011, format: "0.0%", qualifier: "~"}
  monthly_share_of_increase: {value: 0.83, format: "0%"}
caveats: [C-002]                     # inherited automatically from touched columns; agent may add
exhibits: [X-004]
so_what: "The problem is concentrated where customers can leave month to month."
```

`casefile run work/q003_churn_by_plan.py` runs the script, hashes the script and its input sources, captures the declared outputs, and writes the run manifest. `casefile finding add` refuses a finding whose `run` manifest is missing or whose key numbers do not appear in the run's output JSON. The agent's scripts end by printing a JSON object of key numbers, a convention that the `evidence` skill describes along with a script template.

### 6.2 Exhibits (charts built to be legible)

The agent writes **declarative chart specs** (Vega-Lite JSON) rather than ad-hoc matplotlib code. The engine renders them with a house style: minimum 14pt text at slide size, a colorblind-safe palette, direct labels instead of legends where possible, no chart junk, and a **highlight encoding** that colors the series or bar the headline is about while greying the rest.

```yaml
# exhibits/X-004.meta.yaml
id: X-004
finding: F-007
intent: compare_trend          # compare_trend | rank | part_to_whole | distribution | before_after | single_number
highlight: {field: plan, value: monthly}
title_source: slide            # chart has no title of its own; the slide headline is the title
data: exhibits/X-004.csv       # the exact data behind the chart, shipped for audit
alt_text: "Line chart: monthly-plan churn rises from 4.6% to 7.4% Jul–Sep 2025; annual flat near 1.1%."
```

The `charts` skill holds a chart-chooser that maps `intent` to a mark type, with rules such as "no pie charts beyond 3 slices" and "dual axes are forbidden". `casefile exhibit render` checks text size, label overlap and that a highlight is present.

### 6.3 Narrative logic: the ledger tree becomes the pyramid

The storyline is **derived from the ledger**, not written from scratch:

| Ledger structure | Pyramid / deck role |
|---|---|
| Root question (Q-001) + its synthesized answer | **Governing thought**: slide 1 headline / exec summary |
| Root's children with `priority: must`, answered | **Key line**: one section (or one slide) each, ordered by the logic below |
| Grandchildren's verified findings | **Support**: evidence slides, each built on one finding and one exhibit |
| Open `must` questions | **"What we don't know yet"** slide. They are never silently omitted. |
| Answered `should/could` not used in the key line | Appendix, or omitted with the reason recorded in `story.role: none` |
| `definition` / `assumption` answers, caveats with `affects_deck: appendix`, methods | **Appendix**: definitions, data coverage, method |

Ordering logic, chosen by the `narrative` skill and shown to the human as part of the ghost deck:

- **Answer-first (default for decision-makers):** governing thought → reasons in order of impact on the decision → recommendation → open items.
- **SCQA (for audiences new to the problem):** Situation → Complication → Question → Answer, then support.
- **Chronological diagnosis (for technical reviewers):** symptom → ruled-out causes → cause → implication.

### 6.4 `storyline.yaml` (the core deck-input artifact)

```yaml
investigation: churn-q3
audience: {who: "Dana, VP Customer Success", knows: "churn rose; not why", wants: "fund / don't fund decision"}
decision: "Whether to fund a retention offer for monthly-plan customers"
pattern: answer_first
slide_budget: {main: 6, appendix: 3}
governing_thought:
  text: "A targeted monthly-plan offer is the cheapest way to recover Q3's churn spike."
  from_question: Q-001
scqa:
  situation: "Churn had been stable near 4% for six quarters."
  complication: "Q3 churn jumped to 5.8%."
  question: "What drove it, and is an offer worth funding?"
  answer: "Monthly plans after the July price change; an offer pays back in ~4 months."
slides:
  - id: SL-01
    role: title_summary
    headline: "A targeted monthly-plan offer is the cheapest way to recover Q3's churn spike."
    bullets_from: [Q-002, Q-003, Q-006, Q-005]   # one bullet per key-line answer
  - id: SL-03
    role: evidence
    headline: "Monthly plans drove 83% of the increase; annual customers didn't move."
    question: Q-003
    findings: [F-007]
    exhibit: X-004
    numbers_used: [F-007.monthly_churn_q2, F-007.monthly_churn_q3, F-007.monthly_share_of_increase]
    footnotes: [C-002]
    notes: "If asked: annual churn is ~1.1% both quarters; the definition counts paused as churned (finance's definition)."
  - id: SL-06
    role: open_threads
    headline: "Still open: whether a discount or a downgrade retains better."
    questions: [Q-008]
appendix:
  - {id: AP-01, role: definitions, glossary_terms: [churn, mrr]}
  - {id: AP-02, role: data_coverage, sources: [subs]}
  - {id: AP-03, role: method, findings: [F-007, F-009, F-012]}
```

### 6.5 Story lint (`casefile story check`, also run by `/check` and `/deck`)

Each item is reported to the human in plain words, with its rule ID available for the agent.

| Rule | Check |
|---|---|
| S1 headline-is-claim | Every headline is a full sentence containing a verb and a claim; no topic labels like "Churn by plan". |
| S2 ghost-deck-reads | Main-slide headlines alone, in order, must form an argument. The agent self-tests by summarizing the headlines and comparing the summary to the governing thought. |
| S3 numbers-trace | Every numeral in headlines, bullets and notes resolves to a `numbers_used` key number, formatted from that key number. Free-typed numbers fail. |
| S4 evidence-verified | Evidence slides cite only `verified`, non-stale findings. |
| S5 confidence-language | Findings with medium confidence require hedged headline verbs ("likely", "points to"). Low confidence cannot appear in the key line. |
| S6 nothing-hidden | Every open `must` question appears on an open-threads slide. |
| S7 one-message | At most one exhibit and five bullets per slide, and each headline is 15 words or fewer (a soft limit with a warning). |
| S8 budget | The main slide count is within the audience budget. |
| S9 caveats-surface | Material caveats on cited findings appear as footnotes. |
| S10 exhibit-matches-claim | The exhibit's `highlight` field matches the entity named in the headline. |

### 6.6 Rendered outputs

- `GHOST_DECK.md`: headlines only, numbered, with the appendix list. This is the checkpoint the human edits in conversation.
- `deck.md`: **Marp** markdown with headline, exhibit image, bullets, footnotes and `<!-- speaker notes -->`. It previews in VS Code with the Marp extension and exports to PDF/PPTX there, so the human gets a deck with no extra tooling.
- `deck.json`: a harness-neutral slide spec (the same content as `storyline.yaml` with numbers resolved and assets linked). Downstream tools such as a Google Slides script, a corporate generator or another agent's slide skill can consume it.
- `deck.pptx`: rendered by the engine via `python-pptx` into `templates/deck/default.potx` or a corporate template passed with `--template`. Exhibits are embedded as SVG/PNG and the exhibit CSVs are attached in the appendix notes.

---

## 7. Agent-side skill text (excerpts)

### 7.1 `skills/analyze/SKILL.md`

```markdown
---
name: analyze
description: Start or resume a data investigation. Use when the user wants to find out why/what/whether something is happening in their data, names a dataset and a question, or says "let's look into…", "start an analysis", "pick up where we left off".
argument-hint: what you want to find out, and where the data is
---

# Start or resume an investigation

1. Run `casefile status --json` (MCP: `casefile/status`). If an investigation is active and the
   user's request fits it, RESUME: give a 3-line orientation (question, best current answer,
   next step) and continue. If it doesn't fit, ask once: "new investigation, or part of <name>?"
2. Cold start: extract from the user's message, and propose a default for anything missing:
   - the question (one sentence), the audience and the decision it informs, the data location.
   Ask for at most what's missing; never re-ask what they said. Write BRIEF.md via
   `casefile init --slug <slug> --brief -` (pass the brief on stdin).
3. For each data location: follow the `data-context` skill (register → profile → data card).
4. Decompose the question into 3–6 child questions (root = Q-001) using the
   `question-ledger` skill. Mark as `must` the ones the decision depends on.
5. Reply using the conversation contract: answer/orientation first, the data card,
   ≤3 checks with defaults, the child questions as one line each, then the ledger delta footer.

Never show YAML or CLI commands to the user unless they ask how it works.
See [conversation contract](../question-ledger/reference/state-machine.md#contract).
```

### 7.2 Always-on block (`templates/copilot-instructions.snippet.md`, also emitted as an `AGENTS.md` section)

```markdown
## Data investigations (casefile)
When the user asks questions about data in this repo, an investigation may be active (see `analysis/.casefile.yaml`).
- Start any data-analysis turn with `casefile status --json` unless you already did this turn.
- Record every question the user asks about the data in the ledger before answering it (`casefile q add`).
- State numbers only from script output; record substantive results as findings (`casefile run`, `casefile finding add`).
- Change ledger/findings/sources ONLY via casefile commands or the casefile MCP tools — never edit those YAML files directly.
- Answer first in plain language. Cite scripts/charts as links. End state-changing turns with one line:
  `Questions: answered N · opened M (K need you) · next: …`
- Ask the user at most 3 things at once, each with the default you'll assume.
- Dropping or parking a "must" question, editing BRIEF.md, or retracting a finding requires the user's explicit yes.
Skills with details: analyze, data, questions, status, story, deck, check, data-context, question-ledger, evidence, charts, narrative.
```

### 7.3 `com.github.copilot/agents/analyst.agent.md` (optional, VS Code)

```markdown
---
name: analyst
description: Investigate a question with your data and turn the answer into a deck.
argument-hint: what you want to find out
tools: ['read', 'edit', 'search', 'runCommands', 'casefile/*']
model: ['Claude Sonnet 4.5 (copilot)', 'GPT-5 (copilot)']   # prioritized list; strongest available wins
handoffs:
  - label: Show the questions
    agent: analyst
    prompt: /questions
    send: true
  - label: Draft the story
    agent: analyst
    prompt: /story
    send: true
  - label: Build the deck
    agent: analyst
    prompt: /deck
    send: true
---
You are a careful analyst working with a non-technical colleague. Follow the casefile conversation contract …
```

The handoff buttons make the next move clickable for humans who would rather not type commands. Model names in `model` are placeholders that must be checked against the current Copilot model list at release time.

---

## 8. The engine (`casefile` CLI / MCP)

```
casefile install [--harness copilot|claude|codex] [--plugin-only]
casefile init --slug <slug> [--brief -]
casefile status [--json]                              # compact digest: brief, tree, counts, stale, blockers, next
casefile source add <path|uri> [--id subs]
casefile profile <source-id>
casefile context [--for Q-xxx | --columns a,b] [--json]
casefile dict set <source.column> --meaning … --unit … --role … --confidence … [--confirmed-by human]
casefile caveat add --text … --scope … --severity …
casefile q add "<text>" [--parent Q-001] [--kind analytic] [--priority must] [--owner human] [--default "…"]
casefile q set <id> --status in_progress|blocked|parked|dropped|superseded [--why …] [--confirmed-by human]
casefile q answer <id> (--finding F-xxx … | --human-answer "…")
casefile q list [--group human|status] [--json]
casefile run <script> [--declare-outputs …]           # executes, hashes, writes run manifest
casefile finding add --from <draft.yaml>              # validates run + key numbers + inherits caveats
casefile exhibit render <X-id>
casefile story derive                                  # proposes storyline.yaml from the ledger tree
casefile story check [--json]
casefile deck build [--format marp|pptx|json|all] [--template path]
casefile lint [--quiet]                               # everything; nonzero exit only on integrity errors
casefile mcp                                          # stdio MCP server exposing the same operations
```

MCP tools are thin wrappers around the same functions: `status`, `source_add`, `profile`, `context`, `dict_set`, `q_add`, `q_set`, `q_answer`, `q_list`, `run`, `finding_add`, `exhibit_render`, `story_derive`, `story_check`, `deck_build`, `lint`.

Every mutating command re-renders `QUESTIONS.md` / `GHOST_DECK.md` and appends one line to `journal.md`. Doing this automatically is what keeps the human-readable view current with no agent discipline required.

**Packaging:** pure Python, distributed on PyPI and run with `uvx casefile …`, so there is no virtualenv for the human to manage. If `uv` is missing, the `analyze` skill's first-run check explains in one line how to install it.

---

## 9. Copilot compatibility specifics

| Copilot surface | What loads | Notes and mitigations |
|---|---|---|
| **VS Code, local agent** | Skills from `.github/skills/` (also `.claude/skills/`, `.agents/skills/`), each listed in the `/` menu with `argument-hint`. Custom agents from `.github/agents/`. Instructions from `.github/copilot-instructions.md`. MCP from `.vscode/mcp.json`. | Primary target. Handoff buttons work here. Prompt files are deliberately **not used**. |
| **VS Code, Agent Host sessions** | Skills and agents. Prompt files are not loaded there. | This is another reason to use skills rather than prompt files. |
| **Copilot CLI** | Plugin skills, agents, MCP, hooks. `.github/skills` in the repo. | Exposure of skills as slash commands in the CLI needs verification (open decision D2). Fallback: the descriptions are written so "analyze churn…" matches without a slash. |
| **Copilot cloud agent** | Repo skills and instructions. Plugins via `.github/copilot/settings.json` `enabledPlugins`. MCP via repo agent settings. | Non-interactive: asks cannot be answered mid-run. The skills switch to "assume the default, record it as an assumption, and list it on the open-threads slide". This is useful for "refresh the deck with September data" issues assigned to Copilot. |
| **Org-level** | Org custom agents (VS Code setting `github.copilot.chat.organizationCustomAgents.enabled`) | Lets an analytics team roll out `analyst` organization-wide. |

Recommended `.vscode/settings.json` additions written by `casefile install`. Exact keys must be verified against the VS Code version at release time.

```jsonc
{
  // Avoid an approval prompt on every engine call; scope narrowly to casefile itself.
  "chat.tools.terminal.autoApprove": { "/^uvx casefile (status|q|context|profile|story check|lint)/": true },
  // Skills and plugins may still sit behind preview flags on some builds:
  "chat.useAgentSkills": true
}
```

**Tool approval UX matters.** A non-technical user who has to click "Allow" 30 times will give up. The MCP route needs only one per-server trust decision. The terminal route needs the narrow auto-approve rule above. Recommendation: **prefer MCP in VS Code and the CLI in cloud/CLI contexts.** The skills name both forms, for example "`casefile q add` (MCP: `casefile/q_add`)", and the agent uses whichever is available.

---

## 10. Portability to other harnesses

The portable core is the **engine + state files + SKILL.md text**. Harness-specific pieces are thin adapters.

| Harness | Verbs | Always-on block | Engine | Extras |
|---|---|---|---|---|
| **Claude Code** | Skills in `.claude/skills/` or the plugin (`.claude-plugin/plugin.json`); slash-invocable | `CLAUDE.md` section (installer writes it) | MCP via plugin `.mcp.json`, or CLI | Hooks: `Stop` → `casefile lint --quiet` to catch an un-updated ledger; subagents for `context: fork` profiling of large sources |
| **OpenAI Codex CLI** | Agent Skills format (verify directory at release) | `AGENTS.md` section | CLI (Codex has a shell); MCP via `config.toml` | No handoff buttons; footer suggestions do that job |
| **Cursor / Windsurf / others** | Where skills are unsupported, the installer renders the verb skills into the harness's rules or commands format | Rules file | MCP | Lowest common denominator: AGENTS.md + MCP |
| **Any shell-capable agent** | Free text only | `AGENTS.md` | CLI | Everything still works, with less discoverability |

Two design choices keep portability cheap:
1. **SKILL.md bodies avoid harness-specific tool names.** They say "run `casefile status --json` (or call the casefile `status` tool)" and never "use the runCommands tool".
2. **No feature depends on handoffs, hooks or forked context.** Each of these improves the experience where it exists and nothing breaks where it does not.

---

## 11. Risks and open decisions

### Risks

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R1 | **Ledger drift in free-form chat.** The agent answers a question without recording it or recording a finding. | High: the ledger and the deck's traceability depend entirely on this discipline. | Always-on block; `status` digest shows "numbers stated in chat since last finding" (heuristic, from the journal); a turn-end `lint` hook where hooks exist; `/check` audit before deck. |
| R2 | **Tool-approval fatigue** in VS Code makes the experience feel broken to non-technical users. | High for adoption | MCP-first in VS Code, narrow terminal auto-approve, and batching commands so the engine does more per call (e.g. `finding add` also answers the question and re-renders views). |
| R3 | **Command name collisions and prefixing.** Short names like `/analyze` collide with other installed skills. Plugin-distributed skills get a plugin prefix (`/casefile:analyze`?). | Medium | Repo-local install as the default for clean names; descriptions written for free-text matching so the prefix rarely matters. Decide D1. |
| R4 | **Weaker models in the Copilot model picker** follow multi-step skills poorly. | Medium–High | Keep each SKILL.md under about 120 lines with numbered steps; push logic into the engine (derive the story, inherit caveats, check numbers); `model` priority list in `analyst.agent.md`; `/check` catches what slips. |
| R5 | **Copilot surface drift.** Preview flags, Agent Host vs local, and CLI skill invocation keep changing. | Medium | Pin a compatibility matrix in the README and run CI that installs into each surface with a smoke script. Avoid prompt files entirely. |
| R6 | **Data exposure.** Raw rows reach the model or chat logs. | Medium (high in regulated orgs) | Privacy modes, profile-first workflow, `peek` with masking. State clearly that this is a policy, not a sandbox. |
| R7 | **Deck legibility vs corporate templates.** House style collides with brand templates. | Low–Medium | `--template` for pptx; exhibit style tokens configurable in `.casefile.yaml`; `deck.json` for organizations with their own generators. |
| R8 | **Ledger bloat.** Dozens of `could` questions bury what matters. | Medium | Priority tied to the BRIEF decision, rebalancing prompts at milestones, `/questions` shows *must* first and collapses *could*. |
| R9 | **Python runtime friction** for analysts on locked-down machines. | Medium | `uvx` distribution; a later option is a single-binary engine (PyInstaller) or a Node port. |

### Open decisions

| # | Decision | Options | Lean |
|---|---|---|---|
| D1 | Distribution default | Repo-local install vs plugin | **Repo-local** for clean `/analyze` names and versioning with the work; the plugin for CLI and cloud. |
| D2 | Skill invocation in Copilot CLI | Slash command vs natural-language trigger | Verify at build time; write descriptions for both. |
| D3 | Engine transport priority | CLI-first vs MCP-first | **MCP-first in VS Code**, CLI elsewhere; the same function core. |
| D4 | Command set size | 7 verbs vs 4 (merge `status` into `questions`, `check` into `deck`) | Keep 7 for discoverability, but `/deck` always runs `check` implicitly. Test with users. |
| D5 | Canonical deck output | Marp md vs PPTX vs JSON spec | **`storyline.yaml` + `deck.json` are canonical**; Marp and PPTX are renderers. |
| D6 | Multi-investigation workspaces | One investigation per repo vs `analysis/<slug>/` | `analysis/<slug>/` with an active pointer; costs little and avoids a later migration. |
| D7 | Human-edited generated files | Ignore edits vs reverse-sync | Ignore with a banner; tell the human to edit via chat or the human-owned files. Revisit if users fight it. |
| D8 | Agent-opened questions | Free vs capped per turn | Soft cap of 2 surfaced per turn; the rest are recorded as `could` silently and shown at rebalancing. |
| D9 | Story derivation | Engine-derived skeleton then agent writes headlines, vs agent-first | **Engine derives the skeleton from the tree**, the agent writes the language, and lint verifies. |

---

## 12. Build order (suggested)

1. Engine core: `init`, `status`, `q *`, `source add`, `profile`, `run`, `finding add`, `lint`, with schemas and tests.
2. Verb skills `analyze`, `data`, `questions`, `status` and the always-on block, plus repo-local installer for Copilot VS Code. **First usability test:** five non-technical analysts, one real dataset, no documentation.
3. Evidence and exhibits: chart rendering, key-number enforcement.
4. Narrative: `story derive`, `story check`, ghost deck, `/story`.
5. Deck renderers: Marp first, PPTX second.
6. MCP server, plugin packaging (Agent Plugins 1.0 + legacy), Copilot CLI and cloud agent verification.
7. Portability adapters (Claude Code, Codex) and the compatibility CI matrix.

---

## Sources consulted (Copilot extension mechanisms)

- [Use Agent Skills in VS Code](https://code.visualstudio.com/docs/agent-customization/agent-skills) — skill locations, frontmatter (`argument-hint`, `user-invocable`, `disable-model-invocation`, `context: fork`), slash invocation, progressive loading
- [Custom agents in VS Code](https://code.visualstudio.com/docs/agent-customization/custom-agents) — `.agent.md` locations, `tools`, `agents`, `model` lists, `handoffs`, `target`, hooks (preview)
- [Use prompt files in VS Code](https://code.visualstudio.com/docs/agent-customization/prompt-files) — prompt files deprecated for Agent Host sessions; migration to skills
- [Copilot CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference) — legacy `plugin.json` vs Agent Plugins 1.0 layout, `com.github.copilot/` components, `.claude-plugin` lookup
- [Creating a plugin marketplace for Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-marketplace) and [About plugins](https://docs.github.com/en/enterprise-cloud@latest/copilot/concepts/agents/about-plugins) — marketplaces, install sources, cloud agent `enabledPlugins`
- [GitHub Copilot in VS Code v1.110 changelog](https://github.blog/changelog/2026-03-06-github-copilot-in-visual-studio-code-v1-110-february-release/) — agent plugins (experimental) in VS Code
