# Analytics Workbench Skills Specification

## Status and purpose

This specification puts the accepted design for a reusable analytics workbench workflow into one document. It is a drafting contract for the skills and templates that are described below. It is not an implementation plan for a software product. Acceptance is based on the workflow scenarios in this document. An issue-tracker publication, an application framework and an automated test suite are not necessary.

Requirements outside the final **Unresolved design choices** section are accepted behavior. The items in that final section stay deliberately open. They must not be inferred from examples in this document.

The workbench supports one project with a shared data foundation and multiple investigations. It must let an analyst change or expand a business question without a rebuild of reusable data preparation. At the same time, it must keep the findings, decisions and release history of each investigation distinct.

## Artifacts to produce

Keep the skills as agent-agnostic folders under `.agents/skills/`. Generated projects use root `AGENTS.md` instructions. They do not need `.github` directories, project-local skill copies or vendor-specific instruction bridges. Git is still the code-history mechanism. GitHub hosting is not necessary.

The eventual implementation must provide these artifacts:

1. **Initialization skill (`awb-init`).** Sets up the project structure, the working conventions, the shared data foundation and the first investigation. A new project starts from a business question. If the user does not supply a business question, the skill asks for one. The skill completes setup without an investigation only when the user explicitly has no investigation yet. The skill also starts later investigations and resolves consequential scope changes. For these tasks, it uses the self-contained scoping interview below. After newer skills are installed, its repair also brings an existing workbench up to date. The `--upgrade` option of the helper installer replaces only unmodified copies of earlier shipped helpers, package formats, and workbench guides. The install receipt of the project identifies these copies. The upgrade reports customized copies, and the user decides about them. The upgrade removes retired unmodified files only on request. Then the agent reconciles the adapted `AGENTS.md` and `README.md` against the current templates. The upgrade does not change investigation records, data or releases. Initialization does not create a delivery package.
2. **Project `AGENTS.md` template.** Controls these subjects: daily analytical work, architectural boundaries, automatic record maintenance, source and cache handling, changes from one investigation to another, and the prohibition on deliverables that the user did not ask for.
3. **Status skill (`awb-status`).** Gives a read-only report. The report covers the active investigation, its findings (flagged findings also), unresolved issues, package and release state, and landed data and release storage. The report ends with the requests that are relevant now. The skill changes nothing. It lets the analyst discover the request-gated capabilities of the workbench.
4. **Packaging skill (`awb-package`).** Creates or revises the working draft of a named delivery package only when the user explicitly asks for it. It collects the dataset selection of the package and records provenance. It includes a caveat for each flagged finding. It produces an audience-facing findings document, an internal methodology reference and M365 assembly instructions. It owns the draft layout, the shared package format, the manifest fields and the draft consistency rules.
5. **Release skill (`awb-release`).** Preserves a frozen, numbered release from the working draft only when the user explicitly marks the package delivered. Its structural gate is `check-draft --verify-only`. A pass proves that the draft is byte-identical to the draft that the packaging skill checked. For this reason, the release skill's own review covers only what can change after packaging. That is a disposition for each flagged finding that the draft represents. The skill records the release storage location of the project. When that location is reachable, the skill copies each release there. When that location is recorded or changed later, `copy-releases` copies the existing releases.
6. **Cleaning skill (`awb-clean`).** Cleans one dataset at the shared foundation level. A scan proposes candidate issues in one call. The user decides about the issues that change meaning. Corrections become canonical view definitions or a new validated publication. A record script writes quality rows and catalog cells. In the same call, the record script also flags affected findings through the provenance helper of the project. Question-specific exclusions stay in the investigation.
7. **Exploration skill (`awb-eda`).** Explores one dataset for the active investigation, in the scope and settings of that investigation. One scan writes the complete exploration under the `exploration/` of the investigation. Follow-ups are saved queries. Shared data problems go to `awb-clean`. A confirmed coverage gap becomes an open row in `foundation/quality.md`. Exploration records no findings.
8. **Supporting templates.** Give consistent starting formats for the shared source register, the data catalog, the quality record and the glossary. Also give them for the investigation brief, the current state and the investigation history. Also give them for the package findings and methodology documents, the M365 assembly instructions and the package manifest. We recommend that you create or instantiate a template only when the related artifact is necessary.

Every skill name has the `awb-` prefix, so that the actions of the workbench are together in hosts that list skills as commands.

The skills can also supply a concise project orientation file and ignore rules that are applicable to the selected analytical backend. Those details must support the accepted workflow. They must not add another necessary ledger or documentation system. The two JSON files that **Records and vocabulary** names are `findings.json` and `foundation/quality.json`. They are part of their Markdown records. They are not second ledgers.

## Core working model

### Project, foundation, and investigations

A project contains a shared data foundation and zero or more investigations. Initialization can occur before a business question is defined, and this does not start broad data preparation. The data foundation owns these items:

- reusable source knowledge
- preparation logic
- canonical data
- data-quality knowledge
- shared vocabulary
- a catalog of datasets, views, and deliberate caches.

Each investigation owns these items:

- its business question
- its population or scope
- its intended decision or exploratory purpose
- its usefulness criteria
- its analytical settings
- its current state
- its meaningful history
- its findings.

An investigation can expand and keep its identity. A related inquiry about an independent population starts a new investigation. The new investigation inherits the current method, settings and package format as a start point, unless the user corrects them. Its findings and progress start fresh.

When you create an investigation, record these items:

- the business question
- the population or scope
- the decision that the analysis is intended to support, or the fact that the work is exploratory
- what makes the answer useful
- material unknowns. We recommend that they stay visible and do not block exploration.

When work starts again, continue the last active investigation, unless the user indicates a change to a different investigation. Briefly identify the investigation that you continue. If a request can reasonably belong to more than one investigation, ask before you change investigation records.

### Question-driven data preparation

Data gathering must always land source records durably and independently before it puts them into the canonical database. Before conversion or canonical publication, capture API responses, SQL Server extracts and other acquired data as source artifacts with provenance. Do not make direct ingestion into canonical tables the only retained representation of acquired records. An incomplete acquisition must not be made available as a completed canonical dataset. For incremental projects, apply this boundary to each acquired batch.

The default flow is:

- landed originals in `data/raw/`
- validated Parquet representations in `data/parquet/`
- canonical DuckDB views over those files.

Keep landed originals separately, so that conversion and preparation can be tried again without another source fetch. Conversion is not the same as cleaning. Documented normalization and correction rules can stay in views. Initial CSV or JSON landing is source acquisition. It is not a prohibited intermediate CSV handoff.

The generated ignore rules exclude `data/raw/` from Git. Also, it is frequently not possible to fetch a landed original again. Examples are a point-in-time API response, or an extract from a system that changed after the extract. Before the first acquisition is landed, the agent asks where landed originals are kept outside the checkout. The agent records the answer in the project README, on a line that reads `Landed data is kept at: <location>`. A declined answer is recorded as `none chosen`. This is a decision, and its only-copy warning is repeated after each landing.

After each completed landing, if the location is a reachable filesystem path, the agent copies the landed artifact and its provenance to the same relative path under `<location>/data/raw/`. The agent never overwrites an existing destination. If the location is not a reachable filesystem path, the agent states exactly what to copy and where. The source register records the retained copy of each acquisition, as the verified destination path or as `this checkout only`. The status skill reports the acquisitions that are kept only in this checkout.

Each analytical process owns its DuckDB session and loads shared SQL definitions from Git. Published Parquet inputs stay stable during analysis. Conversion writes to an unpublished location and completes validation before publication. Refresh and cleanup must not overwrite or remove files that readers currently use. The default batch workflow does not need a shared writable DuckDB database or a full system for dataset-version management.

The active question sets the preparation effort. Inspect candidate sources only as much as is necessary to assess relevance and fitness. Then prepare the sources that the investigation needs. If a source is shown to be irrelevant, record the reason and stop work on it. Do broader preparation only when the user explicitly asks for it.

An investigation can be the reason for preparation. But reusable cleaning and normalization rules, and knowledge about data limitations, belong to the shared foundation. Investigation-specific populations, periods, filters, exclusions and assumptions stay with that investigation.

### Architectural boundaries

The workbench must enforce these conceptual boundaries, and it must not need separate databases or a heavyweight pipeline to do this:

1. **Preparation owns canonical data.** It parses, normalizes, checks and corrects source data with explicit, reusable rules. It records limitations and the rationale for corrections in the shared foundation.
2. **EDA consumes canonical data.** It explores distributions, relationships, quality and possible explanations. Exploratory transformations stay local to an investigation until they are deliberately promoted into shared preparation logic.
3. **Question-specific choices do not silently become cleaning rules.** A population exclusion or an analytical filter stays local, unless it is a genuine, reusable correction to the data foundation and is consciously promoted as such.
4. **Shared analytical code implements neutral operations.** Reusable modules compute measurements, comparisons, profiles, graph structures or similar outputs. They do this independently of a desired conclusion.
5. **Investigations compose operations through a thin layer.** The run script of the investigation, `run.py`, selects the scope, the configuration and the relevant operations. It must not duplicate shared operations. It must not embed the desired narrative throughout the computation.
6. **Interpretation and presentation follow computation.** The narrative explains results after neutral operations produce them. Outputs must keep relevant results that contradict an expected explanation.

EDA can show a shared data problem, but the correction must go back through preparation. A shared correction that can change existing findings flags those findings with the reason. It does not silently rewrite conclusions.

## Code and data principles

Code must be readable, reusable and modular. We recommend that modules have cohesive responsibilities and small, explicit interfaces. Parameterize meaningful variation. Group related settings into named configuration objects or files with sensible defaults. A CLI is optional. Do not turn parameterization into a universal command with a very large interface. We recommend that distinct workflows use distinct entry points or modules, and that they share common logic.

Before a result is presented or recorded as a finding, it is validated. The checks are recorded with its evidence. The checks are:

- The necessary columns exist, and their meaning is clear.
- Row counts before and after each filter are plausible.
- Joins cause no unexpected row multiplication. Key uniqueness is inspected each time that counts change.
- Missing-value rates of important fields are checked.
- Date filters and grouping dimensions are explicit.
- Metric definitions and assumptions are documented.
- Distinct values are inspected when the business interpretation depends on them.

The workbench must use consistent logical locations across projects. It must not use intermediate CSV exports as handoffs between analytical steps. Intermediate computation stays in the analytical runtime. It is better to keep it as views. Materialize or cache a result only when recomputation is expensive. Record deliberate caches in the catalog. Dataset exports that are selected for a delivery package are audience-facing artifacts, and the intermediate-CSV rule does not apply to them.

Canonical, reusable views are preferred. The default is DuckDB that queries external Parquet datasets. A project can select a different backend for a concrete need, for example incremental workloads. It then keeps independent source landing and the preparation/EDA boundary. Source conversion to Parquet is a deliberate storage boundary. It is not a requirement to materialize every transformation. An accumulation of materialized results without an explicit reason violates the workflow.

All analytical code is tracked in Git. Under the current convention, delivery packages are not part of the code history. Each package manifest identifies the Git commit that produced the represented results. A commit identifies code, not input data. For this reason, the manifest also records input provenance and analytical settings.

The evidence of each result is a JSON file in the `evidence/` directory of the investigation. A shipped provenance helper, copied into `src/`, writes and compares this file. `state.md` links to it.

## Records and vocabulary

Each investigation keeps a concise current state separate from a chronological history:

- `state.md` records the active question, current findings, unresolved issues, flagged findings and next steps, so that work can start again quickly.
- `history.md` records meaningful findings, analytical decisions, caveats, superseded conclusions, and data limitations or errors that affected the investigation.

When a finding, decision, flag or next step changes, the workbench updates these records automatically. The user can also ask for a checkpoint before a change to a different investigation. The records and the methodology document of a package keep limitations and errors in the data. They also keep the methodological mistakes that changed a finding or that explain why an earlier conclusion was wrong. They do not keep routine debugging, coding mistakes and abandoned execution attempts that changed no understanding. Git is still the record for code evolution.

Two Markdown records keep machine state in a JSON file next to them. Each table cell has exactly one owner.

- The `findings.json` of an investigation owns every cell of the Current findings table in `state.md`. Only the provenance helper of the project (`src/provenance.py`, shipped as `awb_provenance.py`) writes it and renders the table from it. `run.py` and `awb.py state` write through the helper. `awb-clean` flags a finding with a call to the helper, and never with an edit to `state.md`. If the helper of the project is from before `findings.json`, `awb-clean` refuses to flag and refers to `awb-init` repair. A writer refuses when the table is different from its render. As a result, a hand edit to the table is reported as drift, and it is not overwritten or kept. Other readers of findings, for example status and packaging, read the rendered table. The rest of `state.md` and all of `history.md` stay Markdown.
- The record script of `awb-clean` writes `foundation/quality.json`, and its scan reads it. It holds only the links from cleaning-scan issues to quality rows. The key of a link is the lowercase hex SHA-256 of the UTF-8 text `<scan name> + "\n" + <issue key>`. In this text, the scan name is the name of the scan file under `foundation/scans/`. The link records the quality ID of the row. It also records the issue count, total and observation date that were most recently recorded for that row, at creation or reopening. `awb-clean` compares later scans with those values, but the observation of the row keeps the values that it was written with. Every cell of `quality.md` stays Markdown, with its IDs, its statuses, and the `<scan>#<key>` marker and counts of the observation. A link counts only while exactly one row has its quality ID and the observation of that row has its marker. A repeated ID or marker voids only the links that it touches. The observation prose is read back only to link the one row that has a marker that no link names.

`findings.json` holds only the cells of the table itself. As a result, it adds no value that `state.md` does not already show. `quality.json` holds issue keys only as hashes, because a key can contain source values. When `foundation/sources.md` restricts copies of the source values, the quality record requires a confirmation before commit. The example values of a quality row and the key of its marker stay in `quality.md`, under that confirmation.

Shared business and analytical terms are in `foundation/glossary.md`. Investigations inherit those definitions. A deliberate local meaning or departure is recorded and explained in the `brief.md` of that investigation. The full glossary is not copied. Population and reporting-period choices are settings, not competing definitions.

The glossary defines terminology. The catalog describes actual datasets, canonical views, and caches. Keep these responsibilities distinct, and do not duplicate their contents.

The workflow must include an analytics-specific domain-modeling discipline. This discipline has these parts:

- Challenge ambiguous terms.
- Test definitions with concrete scenarios.
- Compare definitions with source data and analytical logic.
- Record resolved meanings immediately in the correct analytics artifact.

The workflow must not invoke the unmodified `domain-modeling` skill. It must not need `CONTEXT.md`, create `CONTEXT-MAP.md`, or use ADRs. The `CONTEXT.md` in this repository belongs only to the design session. It is not generated in initialized workbenches.

## Scoping behavior

Initialization and consequential scope changes use a self-contained interview in `awb-init`. Follow the decisions that depend on each scope or purpose choice:

- ask one question at a time about an unresolved consequential decision, with a recommended answer
- carry settled answers forward
- resolve facts directly from the environment
- record the question, population, decision or exploratory purpose, usefulness criteria, and material unknowns
- finish when the consequential decisions are settled or explicitly recorded as material unknowns. Then create the records without a separate confirmation round.

Routine implementation choices need no interview. The vocabulary discipline above is part of this workflow. No external interview or domain-modeling skill is necessary.

## Instruction loading

Keep universal invariants and task routing in the generated `AGENTS.md`. Copy acquisition and analytical procedures into `workbench-guides/`. Make the relevant guide mandatory before each of those operations. Keep customized guides during reconciliation. Skill references are loaded by branch:

- An unchanged release relies on `check-draft --verify-only`. It reads package rules only to settle the disposition of a flagged finding.
- Rare helper branches (a hand export, a non-JSON manifest, a new copy of releases) read the package helper reference.
- Bounded narrative revisions start with the current draft and the relevant records. If the evidence is incomplete or inconsistent, they then expand.

Complete draft verification still applies.

The status collector is read-only and reports mechanical facts. It identifies unsupported formats or uncertain values for targeted manual inspection. Semantic claim matching is still the responsibility of the agent. Full audit evidence stays in durable files. Routine tool output uses counts, failures and paths. The agent reports them verbatim, and does not repeat inventories and checksums. Computation runs as saved queries or as the run script, not as scratch scripts.

## Directory convention

The generated workbench uses the logical structure that follows. Concrete filenames for executable code and configuration formats can be different for each language or backend. But their responsibilities and boundaries must stay recognizable.

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
│   ├── scans/                    # Cleaning scans; Git-ignored because they quote source values
│   ├── glossary.md               # Shared business and analytical vocabulary
│   └── views/                    # Version-controlled canonical definitions, if used
├── investigations/
│   └── <investigation-name>/
│       ├── brief.md              # Question, scope, purpose, audience, usefulness, local terms
│       ├── state.md              # Current findings, flags, issues, and next steps
│       ├── findings.json         # The findings table's source, rendered into state.md
│       ├── history.md            # Meaningful learnings and analytical decisions
│       ├── <configuration>       # Population and analytical settings
│       ├── run.py                # Run script: thin composition of shared operations
│       ├── evidence/             # One JSON evidence file per result
│       └── exploration/          # Local exploratory queries and notebooks
├── package-format/
│   ├── findings-template.md
│   ├── methodology-template.md
│   ├── m365-assembly.md
│   └── manifest-template.md      # Shared manifest field list; serialization is project-specific
├── deliveries/
│   └── <investigation-name>/
│       └── <package-name>/
│           ├── draft/
│           │   ├── findings.md          # Audience-facing deck outline; the only source of slide content
│           │   ├── methodology.md       # Internal reference; never shown in the deck
│           │   ├── m365-assembly.md
│           │   ├── manifest.<format>
│           │   ├── charts/              # Only when findings.md specifies charts: one CSV per chart
│           │   └── datasets/            # Only when datasets were selected
│           └── released/
│               ├── 001/
│               └── 002/
└── .gitignore
```

Create investigation, cache, package and release locations lazily. The structure is a stable convention. It is not a requirement to create empty directories or placeholder documents during initialization. There is no `CONTEXT.md` in the generated structure.

## Packaging and release behavior

Create or refresh a package only when the user explicitly asks for it. Automatic maintenance of investigation records must never trigger a package. By default, an investigation has one named package. Its draft has an audience-facing `findings.md`, which is the deck outline, and an internal `methodology.md`. The **Answer** slide of the deck outline is the executive summary.

Only an independent scope or delivery schedule justifies a second package. Package format and M365 assembly conventions are shared across investigations.

When you create a package, ask which datasets to include. Revisions inherit that selection, unless the user changes it or the selected datasets no longer fit the package scope. If the selected datasets no longer fit the package scope, ask again. Do not choose a default export set for a new package.

Each package has a stable name and one working `draft`. Revisions update that draft. Only an explicit delivery milestone creates a preserved, numbered release. From then on, that release is frozen. Later changes continue in the working draft for the next release. This replaces filename-based revision schemes, for example `really-final-v3`.

Every release is self-contained and includes:

- `findings.md`: the complete audience-facing account of the analysis that the release represents. It is written for the audience that is recorded in the investigation brief. It is a slide-by-slide outline of the deck, so the user can read its headings to check the storyline. It is also the only source of slide content. It follows a translation rule: it uses only the business terms of the glossary. It has no file names or paths, no view, table, or column names, no settings keys, no internal identifiers and no code terms. Its **Answer** slide is the executive summary. Each chart is a specification (form, comparison, highlight, axis, interval, source, caveat, alt text). The plotted values of the chart are in a separate chart file.
- `methodology.md`: the internal reference for the same analysis. Identifiers are expected in it. The M365 agent reads it to understand a decision, or to answer a question from the requester about a decision. But the M365 agent never renders it or quotes it into a document. Its sections for each finding have the same headings as `findings.md`. The two documents agree in claims, numbers, qualifications and caveats.
- a brief description of changes since the previous release, when applicable, in both documents.
- one CSV for each chart that `findings.md` specifies, and any user-selected datasets. Each chart CSV serializes a recorded result that is not stale, as the datasets do.
- M365 assembly instructions. M365 Copilot builds the PowerPoint deck and draws its charts under these instructions.
- a manifest. It contains the Git commit that produced the results, input provenance, analytical settings, dataset selection and unresolved caveats. If no commit existed, the manifest contains `uncommitted` and the checksums of the producing files in place of the commit.

The package narrative is authoritative upstream. The approved flow is from the workbench to M365. In the Microsoft 365 Copilot app, the PowerPoint agent builds a deck from `findings.md`. The deck has one slide for each outline slide, with headlines, bullets, caveats and numbers as written, and notes as speaker notes. The PowerPoint agent draws each chart as a native chart from its chart file, under the chart rules in the assembly instructions. The datasets are delivered next to the deck.

Visual style, chart forms and honest-display rules are only in those instructions. The workbench ships no figure style. The PowerPoint agent asks the requester before it builds, in these conditions:

- The audience or decision is different.
- A slide will not fit.
- A chart cannot be drawn as specified.
- The effect of a caveat is not clear.

The PowerPoint agent does not supply substantive revisions back to the workbench. If a document needs something that only `methodology.md` holds, this is raised with the requester as an upstream gap. Reverse synchronization is out of scope.

The generated ignore rules exclude `deliveries/` from Git. As a result, a numbered release is kept in local storage only. The preservation of releases in other locations, for example shared storage or backup, is a responsibility of the project. Before the first release, the release skill asks for that location and records it in the project README. When the location is reachable from the project, the skill copies each new release there. If not, it states exactly what to copy and where.

Landed data follows the same rule through the project `AGENTS.md`, on its own README line. The reason is that a release manifest cites acquisition identifiers. Without this rule, the landed originals of those acquisitions are on one disk only. At each release, the release skill warns about each cited acquisition that has no retained copy.

Working analysis uses current data and definitions. A release is frozen. It keeps its exact exported results and provenance, so that later changes do not change what it represented. By default, full database snapshots and exact rerun capability are not kept for each release. The preservation of enough original data for an exact rerun is an explicit choice.

A draft can include flagged findings if these two conditions are true:

- Each affected conclusion has a clear caveat.
- The draft lists unresolved issues.

Before a draft with flagged findings is marked delivered, make sure that the user gives a disposition for each flagged finding. The disposition is one of these:

- revalidate the finding
- omit the finding
- explicitly release the finding with the caveat.

Packaging must not automatically rerun analysis. When a result is not stale, serialization of an already-recorded result through a neutral operation is an export, not a rerun. A result is not stale when these items still match the producing state that is recorded with it:

- its producing code
- its view definitions
- its input publications and acquisitions
- its resolved settings.

## Acceptance scenarios

These scenarios are the main acceptance checks for the eventual skills and templates.

### 1. Expansion from approximately 120 to 900 employees

An initial organizational-communications investigation covers about 120 employees. The user expands the same request to a population of about 900. This population includes the original group.

Expected behavior:

- continue the existing investigation, and do not create a new one
- revise its population setting and its current state
- reuse shared preparation and neutral graph operations
- when meaningful prior findings are superseded, keep them in the investigation history
- do not create a duplicate script that is tailored to the expanded narrative
- update a delivery package only if the user explicitly asks for it.

### 2. Pivot to an independent employee group

The user asks the same communications questions about a separate population. This population is independent of the 900-person group.

Expected behavior:

- create a new investigation with fresh state, history, and findings
- start with the current method, parameters, and package format, inherited from the related investigation, unless the user changes them
- reuse foundation preparation and shared analytical operations
- run the scoping interview one question at a time, only for unresolved scope or purpose decisions
- treat findings from the original population as context for method selection, not as evidence about the new group.

### 3. Shared-data correction discovered through EDA

During the exploration of one investigation, the analyst finds that employee email aliases were treated as separate people.

Expected behavior:

- keep the exploratory correction local during its assessment
- when it is accepted as a general data issue, implement it through shared preparation, and document the correction and limitation in the foundation
- update canonical data through the preparation boundary. Do not silently change it inside EDA.
- identify existing investigation findings that can be affected, flag them, and explain why
- do not rerun investigations or revise their conclusions automatically
- leave prior releases frozen.

### 4. Package creation, revision, and release

The user explicitly asks for a package for an investigation. The user chooses which supporting datasets to include (one option is to include none). Later, the user asks for narrative revisions and a second release.

Expected behavior:

- create one stable named package and ask for its initial dataset selection
- keep the complete storyline in the `findings.md` of the draft package as a slide-by-slide outline. Do not rely on M365 to supply missing substance. M365 only builds and styles the deck from it.
- revise the same draft path, and do not create ad hoc names
- on revision, inherit the selected datasets, unless the scope makes them unsuitable
- create release `001` only when the user explicitly marks the first draft delivered
- create release `002` only at the next explicit delivery milestone
- record the Git commit, input provenance, settings, and dataset selection in each manifest
- if a finding is flagged, allow a draft with a caveat. But before release, make sure that there is an explicit revalidate, omit, or release-with-caveat disposition.

### 5. Irrelevant candidate data

A source looks promising at first. It gets a brief relevance and fitness review, and the review shows that it is not related to the active business question.

Expected behavior:

- record why it was rejected
- stop work to clean or standardize it
- do not add unused materialized tables or intermediate CSV exports
- leave the option for broader preparation to a later explicit request.

### 6. Independent source landing and Parquet publication

The user asks for data from an API or SQL Server for a batch investigation.

Expected behavior:

- before canonical ingestion, capture the acquired records on disk with source and acquisition provenance
- before the first landing, ask where landed originals are kept outside the checkout, and record the answer in the README. After each completed landing, if the location is reachable, copy the landed artifact and provenance there, and do not overwrite. If the location is not reachable, state exactly what to copy and where. Record the retained copy in `foundation/sources.md`.
- if conversion fails, keep the completed landed inputs, so that preparation can try again without a new acquisition
- assess relevance and fitness. Then convert the necessary inputs into validated Parquet, and do not change the landed originals.
- keep partial outputs unpublished
- make completed datasets available through shared SQL view definitions that are loaded into the DuckDB session of each process
- let separate analytical sessions query completed, stable datasets while another job prepares new files. Do not make access to a shared writable DuckDB file necessary for this.
- if a project uses an incremental workflow or another backend, apply the same landing-first rule to acquired batches.

## Explicit exclusions

The workbench does not:

- make it necessary for every project to use DuckDB, or make Python, YAML, notebooks, or a particular CLI design mandatory
- make a database snapshot necessary for every release
- treat delivery packages as the source of analytical code history
- synchronize substantive deck edits back into the workbench
- generate packages or ad hoc deliverables without explicit invocation
- automatically rerun analyses when shared data changes
- silently promote investigation-specific transformations into canonical preparation
- keep routine debugging, coding mistakes, or abandoned execution attempts that changed no understanding as analytical history
- create `CONTEXT.md`, `CONTEXT-MAP.md`, or ADRs in initialized workbenches
- invoke `grill-with-docs` or the unmodified `domain-modeling` skill
- read the conclusions of other investigations or projects on the agent's own initiative before the investigation has its own results. The only exception: the findings of a related investigation can inform method selection, as in scenario 2.
- make a speculative general-purpose analytics framework necessary beyond the current work.

## Unresolved design choices

The choices that follow stay open. The specification and implementations must not silently fix them without a concrete project need:

- the general rule for when a scope change becomes a new investigation and not an expansion, beyond the accepted population scenarios above
- the backend and refresh strategy for the exceptional incremental project (DuckDB over Parquet is the batch default)
- precise cache identity, freshness detection, invalidation, and refresh mechanics
- the serialization format of the package manifest and the exact format of the foundation catalog (the shared template fixes the manifest field list and the field names)
- implementation language, executable filenames, and configuration serialization format
- backend-specific raw-data retention and ignore rules, beyond the landed-data storage rule in **Question-driven data preparation**
- which releases, if any, justify the preservation of original inputs for exact reruns.

Result evidence files, acquisition provenance files (`provenance.json`), and publication files (`publication.json`) are JSON with fixed keys. The shipped `awb-init` helpers `awb_provenance.py` and `awb_landing.py` write them. The serialization of the package manifest stays open.
