# Analytics Workbench Skills Specification

## Status and purpose

This specification consolidates the accepted design for a reusable analytics workbench workflow. It is a drafting contract for the skills and templates described below, not an implementation plan for a software product. Acceptance is based on the workflow scenarios in this document; no issue-tracker publication, application framework, or automated test suite is required.

Requirements outside the final **Unresolved design choices** section are accepted behavior. Items in that final section remain deliberately open and must not be inferred from examples in this document.

The workbench supports one project with a shared data foundation and multiple investigations. It must let an analyst change or expand a business question without rebuilding reusable data preparation, while keeping the findings, decisions, and release history for each investigation distinct.

## Artifacts to produce

Keep the skills as agent-agnostic folders under `.agents/skills/`. Generated projects use root `AGENTS.md` instructions and do not require `.github` directories, project-local skill copies, or vendor-specific instruction bridges. Git remains the code-history mechanism; GitHub hosting is not required.

The eventual implementation must provide these artifacts:

1. **Initialization skill (`awb-init`).** Establishes the project structure, working conventions, and shared data foundation, then hands the business question to the scoping skill, which creates the first investigation. A new project starts from a business question; the skill asks for it in one line when none is supplied, without interviewing, and completes setup without an investigation only when the user explicitly has none yet. Its repair also brings an existing workbench up to date after newer skills are installed: the helper installer's `--upgrade` installs missing helpers, guides, and the `foundation/references/` README and replaces only unmodified copies of earlier shipped helpers, package formats, workbench guides, and that README, recognized by the project's install receipt. It reports customized copies for the user to decide and removes retired unmodified files only when asked. The agent then reconciles the adapted `AGENTS.md`, `README.md`, and `.gitignore` against the current templates. The upgrade leaves investigation records, data, and releases as they are. The installer records the interpreter it runs under on the project README's `Project interpreter` line, project-relative when it lies inside the project, and refuses to run under another interpreter while that line names one that exists. The installer prints the command that installs missing packages, `<python> -m pip install`, or `uv pip install --python <python>` for an interpreter without pip whose environment uv made or with uv on the path; initialization runs it itself when the interpreter is inside the project, and asks before installing outside it. Initialization does not create a delivery package.
2. **Project `AGENTS.md` template.** Governs daily analytical work, architectural boundaries, automatic record maintenance, source and cache handling, investigation switching, and the prohibition on unsolicited deliverables.
3. **Status skill (`awb-status`).** A read-only report of the active investigation, its findings including flagged ones, how many of its root questions are answered, its open ledger questions, unresolved issues, package and release state, landed data and release storage, and sources assessed from documentation with no recorded reference, ending with the requests that are relevant now. It changes nothing and makes the workbench's request-gated capabilities discoverable to the analyst.
4. **Packaging skill (`awb-package`).** Creates or revises a named delivery package's working draft only when the user explicitly requests it. It gathers the package's dataset selection, records provenance, carries a caveat for each flagged finding, and produces an audience-facing findings document, an internal methodology reference, the deck rules, and the M365 assembly file. Before its final check it runs a read-only review of the draft against the project's review rules (see **Packaging and release behavior**). It owns the draft layout, shared package format, manifest fields, and draft consistency rules.
5. **Release skill (`awb-release`).** Preserves a frozen, numbered release from the working draft only when the user explicitly marks the package delivered. Its structural gate is `check-draft --verify-only`, which reruns every mechanical check, so it refuses a draft whose narrative numbers a rerun result no longer backs, and verifies every file but the manifest against the inventory the packaging skill recorded (see `awb-release`), so the releasing agent does not repeat the structural checks itself. Review rules can be added after packaging, so release runs the whole read-only review again, narrative checks included (see **Packaging and release behavior**), and it settles a disposition for each flagged finding the draft represents. It records the project's release storage location, copying each release there when reachable; `copy-releases` copies existing releases when that location is recorded or changed later.
6. **Cleaning skill (`awb-clean`).** Cleans one dataset at the shared foundation level: a scan proposes candidate issues in one call, the user decides those that change meaning, corrections become canonical view definitions or a new validated publication, and a record script writes quality rows, including issues the analyst found that the scan did not report, and catalog cells and, through the project's provenance helper, flags affected findings in one call. Question-specific exclusions stay in the investigation.
7. **Exploration skill (`awb-explore`).** Explores one dataset for the active investigation within its scope and settings: one scan writes the complete exploration under the investigation's `exploration/`, follow-ups are saved queries, shared data problems go to `awb-clean`, and a confirmed coverage gap becomes an open row in `foundation/quality.md`. Exploration records no findings.
8. **Scoping skill (`awb-scope`).** Starts an investigation, digs into its business question and context, and resolves consequential scope changes, including whether a new ask extends an investigation or starts another, through the self-contained interview in **Scoping behavior**. It creates and rescopes the investigation's records and keeps its question ledger.
9. **Brainstorming skill (`awb-brainstorm`).** Proposes new questions for an investigation from its answered and open ledger questions, its findings, and the cataloged data, each naming what prompted it, who can answer it, and the decision it serves. It runs no queries and records in the ledger only the questions the user keeps, parks, or declines, so a declined proposal is not repeated.
10. **Supporting templates.** Provide consistent starting formats for the shared source register, data catalog, quality record, glossary, investigation brief, current state, investigation history, package findings and methodology documents, deck rules, M365 assembly file, and package manifest. Templates should be created or instantiated only when the corresponding artifact is needed.

Every skill name carries the `awb-` prefix so the workbench's actions group together in hosts that list skills as commands.

The skills may also provide a concise project orientation file and ignore rules appropriate to the selected analytical backend. Those details must support the accepted workflow without introducing another required ledger or documentation system. The three JSON files named in **Records and vocabulary**, `findings.json`, `questions.json`, and `foundation/quality.json`, are part of their Markdown records, not second ledgers.

## Core working model

### Project, foundation, and investigations

A project contains a shared data foundation and zero or more investigations; initialization can precede a defined business question without triggering broad data preparation. The data foundation owns reusable source knowledge, preparation logic, canonical data, data-quality knowledge, shared vocabulary, and a catalog of datasets, views, and deliberate caches.

Each investigation owns its business question, population or scope, intended decision or exploratory purpose, usefulness criteria, analytical settings, current state, meaningful history, and findings. An investigation can expand while retaining its identity. A related inquiry about an independent population starts a new investigation and inherits the current method, settings, and package format as a starting point unless the user corrects them. Its findings and progress begin fresh.

At investigation creation, record:

- the business question;
- the population or scope;
- the decision the analysis is meant to support, or that the work is exploratory;
- what would make the answer useful; and
- material unknowns, as open questions in the investigation's question ledger, which remain visible without blocking exploration.

When work resumes, continue the last active investigation unless the user indicates a switch, and briefly identify it. If a request plausibly belongs to more than one investigation, ask before changing investigation records.

### Question-driven data preparation

Data gathering must always land source records durably and independently before introducing them into the canonical database. Capture API responses, SQL Server extracts, and other acquired data as source artifacts with provenance before conversion or canonical publication. Do not make direct ingestion into canonical tables the only retained representation of acquired records. An incomplete acquisition must not be exposed as a completed canonical dataset. For incremental projects, apply this boundary to each acquired batch.

The default flow is landed originals in `data/raw/`, validated Parquet representations in `data/parquet/`, and canonical DuckDB views over those files. Preserve landed originals separately so conversion and preparation can be retried without another source fetch. Conversion is not synonymous with cleaning: documented normalization and correction rules may remain in views. Initial CSV or JSON landing is source acquisition, not a prohibited intermediate CSV handoff.

`data/raw/` is excluded from Git by the generated ignore rules, and a landed original often cannot be fetched again, such as a point-in-time API response or an extract from a system that has since changed. Before the first acquisition is landed, the agent asks where landed originals are retained outside the checkout and records the answer in the project README on a line reading `Landed data is kept at: <location>`. A declined answer is recorded as `none chosen`, a decision whose only-copy warning is repeated after each landing. After each completed landing, the agent copies the landed artifact and its provenance to the same relative path under `<location>/data/raw/` when the location is a reachable filesystem path, never overwriting an existing destination; otherwise it states exactly what to copy and where. The source register records each acquisition's retained copy, as the verified destination path or `this checkout only`, and the status skill reports acquisitions held only in this checkout.

An acquisition's provenance records, per file, the upstream URL and validators the fetch received (ETag, Last-Modified, object-store version ID) when it has them. The URL carries no credentials: provenance file entries are copied into committed result evidence, so landing refuses a URL with a user name, password, or credential-named parameter (the `awb-init` landing reference lists them). On request, the status skill checks those validators with read-only HEAD requests (its skill file says which files) and reports each checked file as changed, unchanged, or unknown since its acquisition; an ETag is opaque and only as reliable as the server. A changed upstream is landed again as a new acquisition only on explicit request, never as a side effect of rerunning analysis.

An archive is landed as received, with the members a conversion reads extracted beside it in the same acquisition, and the acquisition's notes record that the archive is the original. A spreadsheet is published through DuckDB's `read_xlsx`, from its `excel` extension, reading every cell as text and converting Excel serial dates explicitly.

Acquisition credentials come from environment variables, with local values in a Git-ignored `.env`. They never enter settings, provenance requests or notes, foundation records, or saved SQL. Saved SQL names no credential at all; the others name the variable instead. A tracked `.env.example` lists the variable names without values, created when a fetch first needs one.

Each analytical process owns its DuckDB session and loads shared SQL definitions from Git. Published Parquet inputs remain stable during analysis; conversion writes to an unpublished location and completes validation before publication. Refresh and cleanup must not overwrite or remove files in use by readers. The default batch workflow does not require a shared writable DuckDB database or a full dataset-version management system.

The active question determines preparation effort. Inspect candidate sources only far enough to assess relevance and fitness, then prepare the sources needed for the investigation. If a source proves irrelevant, record the reason and stop work on it. Broader preparation requires an explicit user request.

The source register records each assessment's basis. A data dictionary, manual, codebook, or schema export that an assessment or catalog entry relies on is kept in `foundation/references/<source-id>/` and suggested for commit, and the register and catalog link it. Material whose license or confidentiality bars committing it stays out of Git like a landed original: the register records its retained location and checksum instead. The status skill reports a source assessed from documentation with no recorded reference.

An investigation may motivate preparation, but reusable cleaning and normalization rules and knowledge about data limitations belong to the shared foundation. Investigation-specific populations, periods, filters, exclusions, and assumptions remain with that investigation.

### Architectural boundaries

The workbench must enforce these conceptual boundaries without requiring separate databases or a heavyweight pipeline:

1. **Preparation owns canonical data.** It parses, normalizes, checks, and corrects source data through explicit, reusable rules. It records limitations and correction rationale in the shared foundation.
2. **EDA consumes canonical data.** It explores distributions, relationships, quality, and possible explanations. Exploratory transformations remain local to an investigation until they are deliberately promoted into shared preparation logic.
3. **Question-specific choices do not silently become cleaning rules.** A population exclusion or analytical filter stays local unless it represents a genuine, reusable correction to the data foundation and is consciously promoted as such.
4. **Shared analytical code implements neutral operations.** Reusable modules compute measurements, comparisons, profiles, graph structures, or similar outputs independently of a desired conclusion.
5. **Investigations compose operations through a thin layer.** The investigation's run script, `run.py`, selects scope, configuration, and relevant operations. It must not duplicate shared operations or embed the desired narrative throughout the computation.
6. **Interpretation and presentation follow computation.** Narrative explains results after neutral operations produce them. Outputs must retain relevant results that contradict an anticipated explanation.

EDA can reveal a shared data problem, but the correction must return through preparation. A shared correction that may alter existing findings flags them with the reason; it does not silently rewrite conclusions.

## Code and data principles

Code must be readable, reusable, and modular. Modules should have cohesive responsibilities and small, explicit interfaces. Parameterize meaningful variation and group related settings into named configuration objects or files with sensible defaults. A CLI is optional. Do not turn parameterization into a universal command with a sprawling interface; distinct workflows should use distinct entry points or modules while sharing common logic.

Before a result is presented or recorded as a finding, it is validated and the checks are recorded with its evidence: required columns exist and their meaning is clear; row counts before and after each filter are plausible; joins cause no unexpected row multiplication, with key uniqueness inspected whenever counts change; missing-value rates of important fields are checked; date filters and grouping dimensions are explicit; metric definitions and assumptions are documented; and distinct values are inspected when they drive business interpretation.

Each finding records a claim strength, the strongest wording it supports: `descriptive`, `association`, or `causal`. A result starts at `association`, the most that exploration and observational comparison support; `causal` requires a stated design basis, an experiment or an identified natural experiment. A claim change is recorded in the investigation history, and a finding's delivered narrative may not word it more strongly.

The workbench must use consistent logical locations across projects. It must not use intermediate CSV exports as handoffs between analytical steps. Intermediate computation stays in the analytical runtime, preferably as views. Materialize or cache a result only when recomputation is expensive, and record deliberate caches in the catalog. Dataset exports selected for a delivery package are audience-facing artifacts and are exempt from the intermediate-CSV rule.

Canonical, reusable views are preferred. DuckDB querying external Parquet datasets is the default. A project may select a different backend for a concrete need, including incremental workloads, while retaining independent source landing and the preparation/EDA boundary. Source conversion to Parquet is a deliberate storage boundary, not a requirement to materialize every transformation. Accumulating materialized results without an explicit reason violates the workflow.

All analytical code is tracked in Git where Git is available. When it is absent or a repository cannot be created, initialization records `Code history: none (<reason>)` on a project README line and reports it once; while that line says none, the agent makes and suggests no commits, and evidence records the producing files' checksums outside version control. The agent commits on the user's request, and commits analytical code as the work goes once the user asks for that, which the project README records as `Commits: as I go`; otherwise it suggests a commit at most once a session while analytical code is uncommitted. Delivery packages are not part of the code history under the current convention; each package manifest identifies the Git commit that produced the represented results. A commit identifies code, not input data, so the manifest also records input provenance, analytical settings, and the runtime (Python, platform, and package versions) each represented result was produced under. Each result's evidence is a JSON file in the investigation's `evidence/` directory, written and compared by a shipped provenance helper copied into `src/`; `state.md` links to it. It records, verbatim, the question the result answers as the user framed it, which the methodology reference repeats. Its producing code is only what can compute that result: the run script, the result's own queries and producer module, the files its settings table declares, and shared code under `src/` other than the helpers that only dispatch, record, or package. Its settings are its own table and the parameters it reads. Notes, prose, another result's code or settings, and an unread parameter never make it stale. When a finding is worded or promoted, a number it states that its result does not record, and wording that asserts a check no recorded check backs, draw a warning then, not first at packaging.

## Records and vocabulary

Each investigation separates a concise current state from a chronological history:

- `state.md` captures the active question, current findings, unresolved issues, flagged findings, and next steps so work can resume quickly.
- `history.md` captures meaningful findings, analytical decisions, caveats, superseded conclusions, and data limitations or errors that affected the investigation.

The workbench updates these records automatically when a finding, decision, flag, or next step changes. The user can also request a checkpoint before switching investigations. Records and a package's methodology document retain limitations and errors in the data and the methodological mistakes that changed a finding or explain why an earlier conclusion was wrong, but exclude routine debugging, coding mistakes, and abandoned execution attempts that changed no understanding. Git remains the record for code evolution.

Three Markdown records keep machine state in a JSON file beside them. Each table cell has exactly one owner.

- An investigation's `findings.json` owns every cell of the Current findings table in `state.md`. Only the project's provenance helper (`src/provenance.py`, shipped as `awb_provenance.py`) writes it and renders the table from it: `run.py` and `awb.py state` write through it, and `awb-clean` flags a finding by calling it, never by editing `state.md`. When the project's helper predates `findings.json`, `awb-clean` refuses to flag and points to `awb-init` repair. A writer refuses when the table differs from its render, so a hand edit to the table is reported as drift rather than overwritten or kept. Other readers of findings, such as status and packaging, read the rendered table. The rest of `state.md` and all of `history.md` remain Markdown.
- An investigation's `questions.json` owns its question ledger, and `questions.md` is rendered from it whole; `awb.py questions` and `run.py` write both through the provenance helper, finding writes refresh `questions.md` for the derived awaiting-recheck status when the ledger is readable and its view matches. A ledger problem leaves that view untouched and returns a `questions` error without blocking the finding, evidence, state, or history write. Ledger writers refuse a `questions.md` that differs from its render. See **Question ledger**.
- `foundation/quality.json`, written by `awb-clean`'s record script and read by its scan, holds only the links from cleaning-scan issues to quality rows. A link is keyed by the lowercase hex SHA-256 of the UTF-8 text `<scan name> + "\n" + <issue key>`, where the scan name is the scan file's name under `foundation/scans/`, and it records the row's quality ID with the issue count, total, and observation date most recently recorded for that row, at creation or reopening; `awb-clean` compares later scans with those, while the row's observation keeps the values it was written with. Every cell of `quality.md`, including its IDs, statuses, and the observation's `<scan>#<key>` marker and counts, remains Markdown. Quality IDs are `DQ-NNN`, apart from the ledger's `Q-NNN`; a project already numbering rows another way keeps its prefix. A row for an issue the analyst found that no scan reported carries its evidence, a saved query or a reference, and has no marker and no link. The record script reads only its two sections' tables, each a header, its separator, and the rows directly under them, and refuses a row elsewhere in either section by its line number, so the template keeps its guidance above each table. A link counts only while exactly one row has its quality ID and that row's observation carries its marker; a repeated ID or marker voids only the links it touches. The observation prose is read back only to link the one row that carries a marker no link names.

`findings.json` holds only the table's own cells, so it adds no value `state.md` does not already show. `quality.json` holds issue keys only as hashes, because a key can embed source values; a quality row's example values and its marker's key stay in `quality.md`, under the confirmation before commit that the quality record requires when `foundation/sources.md` restricts copying the source's values.

Shared business and analytical terms live in `foundation/glossary.md`. Investigations inherit those definitions. A deliberate local meaning or departure is recorded and explained in that investigation's `brief.md`; the full glossary is not copied. Population and reporting-period choices are settings rather than competing definitions.

The glossary defines terminology; the catalog describes actual datasets, canonical views, and caches. Keep these responsibilities distinct rather than duplicating their contents.

The workflow must embed an analytics-specific domain-modeling discipline: challenge ambiguous terms, test definitions with concrete scenarios, compare definitions with source data and analytical logic, and record resolved meanings immediately in the correct analytics artifact. It must not invoke the unmodified `domain-modeling` skill, require `CONTEXT.md`, create `CONTEXT-MAP.md`, or use ADRs. The `CONTEXT.md` in this repository belongs only to the design session and is not generated in initialized workbenches.

## Scoping behavior

A new investigation, a sharpening of its question, and a consequential scope change use a self-contained interview in `awb-scope`; `awb-init` only collects the first question and hands it over. Follow the decisions that depend on each scope or purpose choice:

- ask in dependency order: a decision whose answer shapes the next question alone, and decisions at the same level together, at most four, each with a recommended answer;
- follow up a vague, hedged, or conflicting answer at once, restated as a concrete case, before moving on;
- push on what makes an answer usable: the measure's and population's definitions, the comparison that gives a number meaning, the result that would change the decision, and what is already believed;
- carry settled answers forward, and in a rescope ask only about the decisions the change reopens;
- resolve facts directly from the environment, and never ask the user a question the data can answer;
- capture the question, population, decision or exploratory purpose, and usefulness criteria in the brief, and every material unknown as an open ledger question with who can answer it;
- ask every decision and context question the user can answer before writing the records, recording one as open only when the user defers it, and when setup hands the question over in the same turn, ask the first interview round before the investigation is created; and
- finish when those are settled or recorded as open questions, then create the records without a separate confirmation round.

Routine implementation choices need no interview. The vocabulary discipline above is embedded in this workflow. No external interview or domain-modeling skill is required.

### Question ledger

Each investigation keeps every question it raises, answered or not, in `questions.json`, rendered whole to `questions.md`. A question has a never-reused ID `Q-NNN`, its analytical text, optional audience wording for the Open questions slide (empty by default, whitespace collapsed like text), a kind (context, decision, or analytical), who can answer it (the user, a stakeholder, or the data), what an answer unblocks, what raised it (scoping, brainstorming, exploration, or analysis), a parent question or none for a root, a priority (must, should, or could, defaulting to should), and a status: open, answered, parked, declined, or superseded, each but open and answered with a reason. A parent must exist and a cycle is refused; listings show the tree depth-first, siblings by priority then ID. A package proposes the order of its finding slides from this tree, as the default, and lists the unanswered must questions on its **Open questions** slide.

- The ledger holds questions. Settled scope and purpose decisions stay in the brief, data problems and coverage limitations in the state's Unresolved issues, and actions in its Next steps. The brief's Material unknowns section points to the ledger.
- A person's answer records the answer and who gave it, and only a person answers a user or stakeholder question. A data question is answered only by a recorded result: the result's settings table declares `answers = ["Q-NNN"]`, evidence recording refuses an ID the ledger lacks or one a person answers, and `run.py` marks the question answered with the result linked. The ledger stores the link, never the numbers; status and resume views show each linked finding's current status, and an answered data question with any flagged or superseded linked finding displays as `answered (awaiting recheck)`, derived each time it is shown while its stored status stays answered.
- `answers` links questions and computes nothing, so it is left out of every settings comparison: declaring or changing it makes no result stale and leaves an exact rerun exact. `awb.py questions answer --result` links an already recorded result whose settings declare the question.
- An answered question is never reopened or reworded; a scope change supersedes it, keeping its answer, and adds a replacement. Its parent, priority, and audience wording stay editable in every status; an empty audience value clears it. Lists and the rendered ledger show audience wording when set. Open questions bullets use that exact rendered wording, falling back to text when unset; packaging presents it with the headlines for approval. Parent and priority express the question's role in the decision and decide **Open questions** membership, so a presentation reorder never changes them: an order of finding slides the user approves that differs from the derived one is recorded in the package manifest's `presentation_order`, which then decides the slide order.
- `awb-explore` records each untested candidate explanation as an open data question, and `awb-brainstorm` records the proposals the user keeps, parks, or declines.
- An investigation that predates the ledger keeps its records; `awb-scope` moves its Material unknowns and question-shaped Next steps into a new ledger when it next runs on it.

## Instruction loading

Keep universal invariants and task routing in the generated `AGENTS.md`; copy acquisition and analytical procedures into `workbench-guides/` and require the relevant guide before that operation. Preserve customized guides during reconciliation. `AGENTS.md` routes helper commands through the `awb` MCP server's tools when the host offers them and through the command line otherwise; when a write tool call is refused or unavailable, the agent runs the same command on the command line, keeps using the tools that work, and says so once. The skills' scripts run by path, never as `awb.py` subcommands. `python3` in every workbench command means the README's `Project interpreter`: `src/awb.py` reruns itself under it when another interpreter starts it, and the MCP server runs its commands under it, `AWB_PYTHON` overriding both and the project's `.venv` or `venv` serving when the README records none. Skill references are loaded by branch: an unchanged release relies on `check-draft --verify-only`, reads the draft review brief to launch the read-only review, and reads package rules only to settle a flagged finding's disposition, rare helper branches (a hand export, a non-JSON manifest, re-copying releases) read the package helper reference, and bounded narrative revisions begin with the current draft and relevant records before expanding when evidence is incomplete or inconsistent. Complete draft verification still applies.

The status collector reports mechanical facts read-only and identifies unsupported formats or uncertain values for targeted manual inspection. Semantic claim matching remains the agent's responsibility. Full audit evidence stays in durable files and tool results; chat summarizes outcomes in plain words, quoting helper output only for a failure or when the user asks. A question that needs the user is asked in the message that says so, as a plain decision with a recommendation and the alternative, never by pointing to a skill or instruction file; an environment or tool limit is reported only when it affects the user, with whether they must act and what the workbench does instead; files are named by path and never said to be attached. A turn that changed records ends with one plain line on what changed for the user's own questions, counted in their terms and never as ledger rows, and on the next step. The setup report holds at most five items: the project root, the question handed to scoping, any host instruction file, what the user must act on with its impact, and the next request. Status leads with the root and must questions in the user's terms, and the package and release reports state a provenance gap as what went unrecorded, or leave it out when it changes nothing the user decides. The exact reviewer-to-caller report is retained so every review rule and diagnostic can be checked. Computation runs as saved queries or the run script rather than scratch scripts.

## Directory convention

The generated workbench uses the following logical structure. Concrete filenames for executable code and configuration formats may vary by language or backend, but their responsibilities and boundaries must remain recognizable.

```text
project-root/
├── AGENTS.md
├── README.md
├── workbench-guides/             # Procedures read only for the applicable operation
│   ├── data.md
│   └── analysis.md
├── src/
│   ├── preparation/              # Reusable normalization and correction logic
│   ├── exploration/              # Neutral profiling and analytical operations
│   ├── packaging/                # Shared package assembly logic
│   └── provenance.py             # Result evidence recording and comparison
├── data/
│   ├── raw/                      # Independently landed originals and provenance
│   ├── parquet/                  # Validated datasets queried by DuckDB views
│   └── cache/                    # Deliberate, rebuildable expensive results
├── foundation/
│   ├── sources.md                # Provenance, relevance, and fitness assessments
│   ├── catalog.md                # Canonical datasets, views, and deliberate caches
│   ├── quality.md                # Limitations, errors, and correction rationale
│   ├── quality.json              # Links from cleaning-scan issues to quality rows (written by awb-clean)
│   ├── datasets.toml             # Declared checks each dataset's publications must pass
│   ├── scans/                    # Cleaning scans; Git-ignored because they quote source values
│   ├── glossary.md               # Shared business and analytical vocabulary
│   ├── references/               # Third-party data dictionaries, manuals, codebooks, schema exports; one folder per source ID
│   ├── review-rules.md           # Numbered rules from review corrections, checked by every package review
│   └── views/                    # Version-controlled canonical definitions, if used
├── investigations/
│   └── <investigation-name>/
│       ├── brief.md              # Question, scope, purpose, audience, usefulness, local terms
│       ├── state.md              # Current findings, flags, issues, and next steps
│       ├── findings.json         # The findings table's source, rendered into state.md
│       ├── questions.json        # Question ledger source: every question raised, answered or not
│       ├── questions.md          # Question ledger, rendered whole from questions.json
│       ├── history.md            # Meaningful learnings and analytical decisions
│       ├── <configuration>       # Population and analytical settings
│       ├── run.py                # Run script: thin composition of shared operations
│       ├── producers/            # One module per result that needs more than its query, named by result ID
│       ├── evidence/             # One JSON evidence file per result
│       └── exploration/          # Local exploratory queries and notebooks
├── package-format/
│   ├── findings-template.md
│   ├── methodology-template.md
│   ├── methodology-note-template.md
│   ├── deck-rules.md             # How any builder builds the deck from findings.md and charts/
│   ├── assembly/
│   │   └── m365.md               # Microsoft 365 Copilot specifics
│   └── manifest-template.md      # Shared manifest field list; serialization is project-specific
├── deliveries/
│   └── <investigation-name>/
│       └── <package-name>/
│           ├── draft/
│           │   ├── findings.md          # Audience-facing deck outline; the only source of slide content
│           │   ├── methodology.md       # Internal reference; never shown in the deck
│           │   ├── methodology-note.md  # Optional audience-facing account of method; delivered beside the deck
│           │   ├── deck-rules.md
│           │   ├── assembly/m365.md
│           │   ├── manifest.<format>
│           │   ├── charts/              # Only when findings.md specifies charts: one CSV per chart
│           │   └── datasets/            # Only when datasets were selected
│           └── released/
│               ├── 001/
│               └── 002/
├── .env.example                  # Credential variable names, no values; only when a fetch needs one
└── .gitignore
```

Create investigation, cache, package, and release locations lazily. The structure is a stable convention, not a requirement to create empty directories or placeholder documents during initialization. The exception is `foundation/references/`, which the helper installer creates with a README describing it, so documentation has a home before the first source is assessed and repair adds it to an existing workbench. There is no `CONTEXT.md` in the generated structure.

## Packaging and release behavior

Package creation and refresh require an explicit user request. Automatic investigation record maintenance must never trigger a package. An investigation has one named package by default. Its draft carries an audience-facing `findings.md`, the deck outline whose **Answer** slide is the executive summary, an internal `methodology.md`, and, when the audience needs one, an audience-facing `methodology-note.md`. A second package is justified only by an independent scope or delivery schedule. Package format, deck rules, and assembly conventions are shared across investigations.

At package creation, ask which datasets to include. Revisions inherit that selection unless the user changes it or the selected datasets no longer fit the package scope; in the latter case, ask again. Do not choose a default export set for a new package.

A new draft, or a changed storyline, passes a headline checkpoint. In preview-and-wait mode the user sees the title and every slide headline before the full slides are written; in draft-then-review mode the full draft is written and the draft report shows its headlines, marked provisional, for approval or reorder. The mode is the first of these that applies: a mode the request states; draft-then-review when the request supplies the storyline or asks for the full draft; the mode the brief's Audience section records, where a mode the user states is kept for later packages; preview-and-wait. A consequential open choice, such as audience wording the user has not approved, stops the draft in either mode and is asked in the same message. The checkpoint says in one sentence that the deck opens with a title slide and then the answer slide, reports the main and appendix slide counts against a length the Audience section records, proposes what moves to the appendix when the main slides exceed it, and proposes the ledger-derived finding order.

Each package has a stable name and one working `draft`. Revisions update that draft. Only an explicit delivery milestone creates a preserved, numbered release, which is frozen from then on; later changes resume in the working draft for the next release. This replaces filename-based revision schemes such as `really-final-v3`.

Every release is self-contained and includes:

- `findings.md`, the complete audience-facing account of the analysis represented by that release, written for the audience recorded in the investigation brief. It is a slide-by-slide outline of the deck, so the user can check the storyline by reading its headings, and the only source of slide content. It follows a translation rule: no file names or paths, view, table, or column names, settings keys, internal identifiers, or code terms, only the glossary's business terms. The deck opens with a title slide and then its **Answer** slide, the executive summary. The title, **Answer**, at least one finding, **How we know**, and **Limitations and open caveats** are required, in that order; the other slides are conditional or optional, and a closing **Appendix** holds slides kept for reference after the main sequence, where **How we know**, **Limitations and open caveats**, **Supporting datasets**, and individual findings may move, **How we know** staying before **Limitations and open caveats** when both move. Each chart is a specification (form, comparison, highlight, axis, interval, source, caveat, alt text) whose plotted values live in a separate chart file;
- `methodology.md`, the internal reference for the same analysis, in which identifiers are expected. The deck builder consults it to understand a decision or answer the requester's question about one, but never renders or quotes it into a document. Its sections per finding carry the same headings as `findings.md`, each stating its finding's claim strength, and the two agree in claims, numbers, qualifications, and caveats; the packaging check refuses causal wording in `findings.md` above a finding's claim strength;
- `methodology-note.md`, when the audience needs one: a short plain-language account of method, sources, definitions, exclusions, and limitations under the same translation rule as `findings.md`, stating nothing `methodology.md` does not support, delivered beside the deck like datasets and not given to the deck builder;
- a brief description of changes since the previous release, when applicable, in both documents;
- one CSV per chart `findings.md` specifies, each serializing a recorded result that is not stale, as datasets do, and any user-selected datasets;
- the deck rules, under which any builder builds the deck and draws its charts, and the Microsoft 365 assembly file, under which M365 Copilot's PowerPoint agent does; and
- a manifest containing the producing Git commit (or `uncommitted` with checksums of the producing files when no commit existed), input provenance, analytical settings, the runtime of each represented result, dataset selection, and unresolved caveats.

The package narrative is authoritative upstream. The approved flow is workbench to M365. In the Microsoft 365 Copilot app, the PowerPoint agent builds a deck from `findings.md`, one slide per outline slide with headlines, bullets, caveats, and numbers as written and notes as speaker notes, and a divider slide before any appendix, and draws each chart as a native chart from its chart file under the chart rules in the deck rules; the datasets and any methodology note are delivered beside the deck. Visual style, chart forms, and honest-display rules live only in the deck rules; the workbench ships no figure style. It asks the requester before building when the audience or decision differs, a slide will not fit, a chart cannot be drawn as specified, or the effect of a caveat is unclear. It does not supply substantive revisions back to the workbench; a document that needs something only `methodology.md` holds is raised with the requester as an upstream gap. Reverse synchronization is out of scope.

`deliveries/` is excluded from Git by the generated ignore rules, so a numbered release is retained in local storage only. Preserving releases elsewhere, such as shared storage or backup, is a project responsibility. The release skill asks for that location before the first release, records it in the project README, and copies each new release there when the location is reachable from the project; otherwise it states exactly what to copy and where. Landed data follows the same rule through the project `AGENTS.md`, on its own README line, because a release manifest cites acquisition identifiers whose landed originals would otherwise exist on one disk only. The release skill warns at each release about any cited acquisition without a retained copy.

Working analysis uses current data and definitions. A release is frozen: it preserves its exact exported results and provenance so later changes do not alter what it represented. Full database snapshots and exact rerun capability are not retained per release by default. Preserving enough original data for an exact rerun is an explicit choice.

The agent that writes a draft does not review it. Before the final `check-draft`, and again before a release, a fresh subagent limited to read tools reviews the narratives: their agreement, each flagged finding's caveats, and every rule in `foundation/review-rules.md`. It reports and does not fix; the packaging skill repairs. The restriction is tool scoping where the host supports it (Claude Code subagent types) and an instruction elsewhere (Codex subagents), not isolation. The one exception is a host with no subagents, where the writing agent follows the read-only review brief itself; `awb-package/references/review.md` says how each host starts the review. Each correction the user makes while reviewing a draft that later drafts could repeat is appended to `foundation/review-rules.md` as a rule numbered `R-<area>-NNN`, with a severity (`error` or `warning`), a fix, and a pattern where one line of text can show the violation. IDs are never renumbered or reused; a rule is retired by its severity, never deleted. The `review-rules` command appends rules and lists each one with the narrative lines its pattern matches, so every later review reports against every rule.

Drafts may include flagged findings if each affected conclusion carries a clear caveat and the draft lists unresolved issues. Before a draft with flagged findings is marked delivered, require the user's disposition for each: revalidate the finding, omit it, or explicitly release it with the caveat. Packaging must not automatically rerun analysis. Serializing an already-recorded result through a neutral operation is an export rather than a rerun when the result is not stale, that is, when its producing code, view definitions, input publications and acquisitions, and the settings it reads still match the producing state recorded with it.

## Acceptance scenarios

These scenarios are the primary acceptance checks for the eventual skills and templates.

### 1. Expansion from approximately 120 to 900 employees

An initial organizational-communications investigation covers approximately 120 employees. The user expands the same ask to a population of approximately 900 that includes the original group.

Expected behavior:

- handle the change through `awb-scope` as a rescope;
- continue the existing investigation rather than create a new one;
- supersede the ledger answers the expansion invalidates, keeping them, and add their replacements;
- revise its population setting and current state;
- reuse shared preparation and neutral graph operations;
- preserve meaningful prior findings in investigation history when they are superseded;
- avoid creating a duplicate script tailored to the expanded narrative; and
- update a delivery package only if the user explicitly requests it.

### 2. Pivot to an independent employee group

The user asks the same communications questions about a separate population independent of the 900-person group.

Expected behavior:

- create a new investigation with fresh state, history, and findings;
- begin with the current method, parameters, and package format inherited from the related investigation unless the user changes them;
- reuse foundation preparation and shared analytical operations;
- run the `awb-scope` interview in dependency order only for unresolved scope or purpose decisions, with a fresh question ledger; and
- treat findings from the original population as context for method selection, not evidence about the new group.

### 3. Shared-data correction discovered through EDA

While exploring one investigation, the analyst discovers that employee email aliases were being treated as separate people.

Expected behavior:

- keep the exploratory correction local while it is being assessed;
- when accepted as a general data issue, implement it through shared preparation and document the correction and limitation in the foundation;
- update canonical data through the preparation boundary rather than silently changing it inside EDA;
- identify existing investigation findings that may be affected, flag them, and explain why;
- do not rerun investigations or revise their conclusions automatically; and
- leave prior releases frozen.

### 4. Package creation, revision, and release

The user explicitly asks for a package for an investigation, chooses which supporting datasets to include (including the option to include none), and later asks for narrative revisions and a second release.

Expected behavior:

- create one stable named package and ask for its initial dataset selection;
- maintain the complete storyline in the draft package's `findings.md` as a slide-by-slide outline rather than relying on M365 to supply missing substance, with M365 only building and styling the deck from it;
- revise the same draft path instead of creating ad hoc names;
- inherit the selected datasets on revision unless scope makes them unsuitable;
- create release `001` only when the user explicitly marks the first draft delivered;
- create release `002` only at the next explicit delivery milestone;
- record Git commit, input provenance, settings, runtime, and dataset selection in each manifest; and
- if a finding is flagged, allow a caveated draft but require an explicit revalidate, omit, or release-with-caveat disposition before release.

### 5. Irrelevant candidate data

An initially promising source receives a brief relevance and fitness review and proves unrelated to the active business question.

Expected behavior:

- record why it was rejected;
- stop cleaning or standardizing it;
- avoid adding unused materialized tables or intermediate CSV exports; and
- leave the option for broader preparation to a later explicit request.

### 6. Independent source landing and Parquet publication

The user requests data from an API or SQL Server for a batch investigation.

Expected behavior:

- capture the acquired records on disk with source and acquisition provenance before canonical ingestion;
- before the first landing, ask where landed originals are retained outside the checkout and record it in the README; after each completed landing, copy the landed artifact and provenance there without overwriting when the location is reachable, or state exactly what to copy and where, and record the retained copy in `foundation/sources.md`;
- retain completed landed inputs when conversion fails, allowing preparation to retry without reacquisition;
- assess relevance and fitness, then convert needed inputs into validated Parquet without modifying the landed originals;
- keep partial outputs unpublished;
- expose completed datasets through shared SQL view definitions loaded into each process's DuckDB session;
- permit separate analytical sessions to query completed, stable datasets while another job prepares new files, without requiring access to a shared writable DuckDB file; and
- apply the same landing-first rule to acquired batches if a project uses an incremental workflow or another backend.

### 7. Question ledger and brainstorming

The user starts an investigation with open questions only a stakeholder can answer, explores a dataset, records a result that answers one question, and later asks what else to explore.

Expected behavior:

- record each open question in the ledger with who can answer it, and ask the user none that the data can answer;
- record a stakeholder's answer with who gave it;
- record exploration's untested candidate explanations as open data questions, not findings;
- mark a data question answered only when a recorded result declaring it is run, without making that result stale when the declaration is added later;
- report an answered data question as `answered (awaiting recheck)` when any answering finding is flagged or superseded, even when another answering finding is settled; its stored status remains `answered`;
- propose new questions that each name what prompted them, who can answer them, and the decision they serve, skipping those already asked; and
- record the proposals the user declines so a later brainstorm does not repeat them.

## Explicit exclusions

The workbench does not:

- require every project to use DuckDB, or mandate Python, YAML, notebooks, or a particular CLI design;
- require a database snapshot for every release;
- treat delivery packages as the source of analytical code history;
- synchronize substantive deck edits back into the workbench;
- generate packages or ad hoc deliverables without explicit invocation;
- automatically rerun analyses when shared data changes;
- silently promote investigation-specific transformations into canonical preparation;
- retain routine debugging, coding mistakes, or abandoned execution attempts that changed no understanding as analytical history;
- create `CONTEXT.md`, `CONTEXT-MAP.md`, or ADRs in initialized workbenches;
- invoke `grill-with-docs` or the unmodified `domain-modeling` skill;
- read other investigations' or projects' conclusions on the agent's own initiative before an investigation's own results exist, except that a related investigation's findings may inform method selection as in scenario 2; or
- require a speculative general-purpose analytics framework beyond the current work.

## Unresolved design choices

The following choices remain open and must not be silently fixed by the specification or by an implementation without a concrete project need:

- the general rule for when a scope change becomes a new investigation rather than an expansion, beyond the accepted population scenarios above;
- the backend and refresh strategy for the exceptional incremental project; DuckDB over Parquet is the batch default;
- precise cache identity, freshness detection, invalidation, and refresh mechanics;
- the serialization format of the package manifest and the exact formatting of the foundation catalog; the manifest field list and field names are fixed by the shared template;
- implementation language, executable filenames, and configuration serialization format;
- backend-specific raw-data retention and ignore rules, beyond the landed-data storage rule in **Question-driven data preparation**; and
- which releases, if any, warrant preserving original inputs for exact reruns.

Result evidence files, acquisition provenance files (`provenance.json`), and publication files (`publication.json`) are JSON with fixed keys written by the shipped `awb-init` helpers `awb_provenance.py` and `awb_landing.py`; the package manifest's serialization stays open.
