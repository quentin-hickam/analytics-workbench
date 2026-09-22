# Analytics Workbench Skills Specification

## Status and purpose

This specification consolidates the accepted design for a reusable analytics workbench workflow. It is a drafting contract for the skills and templates described below, not an implementation plan for a software product. Acceptance is based on the workflow scenarios in this document; no issue-tracker publication, application framework, or automated test suite is required.

Requirements outside the final **Unresolved design choices** section are accepted behavior. Items in that final section remain deliberately open and must not be inferred from examples in this document.

The workbench supports one project with a shared data foundation and multiple investigations. It must let an analyst change or expand a business question without rebuilding reusable data preparation, while keeping the findings, decisions, and delivery history for each investigation distinct.

## Artifacts to produce

Keep the skills as agent-agnostic folders under `.agents/skills/`. Generated projects use root `AGENTS.md` instructions and do not require `.github` directories, project-local skill copies, or vendor-specific instruction bridges. Git remains the code-history mechanism; GitHub hosting is not required.

The eventual implementation must provide these artifacts:

1. **Initialization skill.** Establishes the project structure, working conventions, shared data foundation, and the first investigation when a business question is available. It directly invokes the `grilling` skill as described below. It does not create a delivery package.
2. **Project `AGENTS.md` template.** Governs daily analytical work, architectural boundaries, automatic record maintenance, source and cache handling, investigation switching, and the prohibition on unsolicited deliverables.
3. **Packaging skill.** Creates or revises a named delivery package only when the user explicitly requests it. It gathers the package's dataset selection, checks revalidation flags, records provenance, and produces a complete upstream narrative plus M365 assembly instructions.
4. **Supporting templates.** Provide consistent starting formats for the shared source register, data catalog, quality record, glossary, investigation brief, current state, investigation history, package journal, executive summary, M365 assembly instructions, and delivery manifest. Templates should be created or instantiated only when the corresponding artifact is needed.

The skills may also provide a concise project orientation file and ignore rules appropriate to the selected analytical backend. Those details must support the accepted workflow without introducing another required ledger or documentation system.

## Core working model

### Project, foundation, and investigations

A project contains a shared data foundation and zero or more investigations; initialization can precede a defined business question without triggering broad data preparation. The data foundation owns reusable source knowledge, preparation logic, canonical data, data-quality knowledge, shared vocabulary, and a catalog of datasets, views, and deliberate caches.

Each investigation owns its business question, population or scope, intended decision or exploratory purpose, usefulness criteria, analytical settings, current state, meaningful history, and findings. An investigation can expand while retaining its identity. A related inquiry about an independent population starts a new investigation and inherits the current method, settings, and package format as a starting point unless the user corrects them. Its findings and progress begin fresh.

At investigation creation, record:

- the business question;
- the population or scope;
- the decision the analysis is meant to support, or that the work is exploratory;
- what would make the answer useful; and
- material unknowns that should remain visible without blocking exploration.

When work resumes, continue the last active investigation unless the user indicates a switch, and briefly identify it. If a request plausibly belongs to more than one investigation, ask before changing investigation records.

### Question-driven data preparation

Data gathering must always land source records durably and independently before introducing them into the canonical database. Capture API responses, SQL Server extracts, and other acquired data as source artifacts with provenance before conversion or canonical publication. Do not make direct ingestion into canonical tables the only retained representation of acquired records. An incomplete acquisition must not be exposed as a completed canonical dataset. For incremental projects, apply this boundary to each acquired batch.

The default flow is landed originals in `data/raw/`, validated Parquet representations in `data/parquet/`, and canonical DuckDB views over those files. Preserve landed originals separately so conversion and preparation can be retried without another source fetch. Conversion is not synonymous with cleaning: documented normalization and correction rules may remain in views. Initial CSV or JSON landing is source acquisition, not a prohibited intermediate CSV handoff.

Each analytical process owns its DuckDB session and loads shared SQL definitions from Git. Published Parquet inputs remain stable during analysis; conversion writes to an unpublished location and completes validation before publication. Refresh and cleanup must not overwrite or remove files in use by readers. The default batch workflow does not require a shared writable DuckDB database or a full dataset-version management system.

The active question determines preparation effort. Inspect candidate sources only far enough to assess relevance and fitness, then prepare the sources needed for the investigation. If a source proves irrelevant, record the reason and stop work on it. Broader preparation requires an explicit user request.

An investigation may motivate preparation, but reusable cleaning and normalization rules and knowledge about data limitations belong to the shared foundation. Investigation-specific populations, periods, filters, exclusions, and assumptions remain with that investigation.

### Architectural boundaries

The workbench must enforce these conceptual boundaries without requiring separate databases or a heavyweight pipeline:

1. **Preparation owns canonical data.** It parses, normalizes, checks, and corrects source data through explicit, reusable rules. It records limitations and correction rationale in the shared foundation.
2. **EDA consumes canonical data.** It explores distributions, relationships, quality, and possible explanations. Exploratory transformations remain local to an investigation until they are deliberately promoted into shared preparation logic.
3. **Question-specific choices do not silently become cleaning rules.** A population exclusion or analytical filter stays local unless it represents a genuine, reusable correction to the data foundation and is consciously promoted as such.
4. **Shared analytical code implements neutral operations.** Reusable modules compute measurements, comparisons, profiles, graph structures, or similar outputs independently of a desired conclusion.
5. **Investigations compose operations through a thin layer.** Investigation code selects scope, configuration, and relevant operations. It must not duplicate shared operations or embed the desired narrative throughout the computation.
6. **Interpretation and presentation follow computation.** Narrative explains results after neutral operations produce them. Outputs must retain relevant results that contradict an anticipated explanation.

EDA can reveal a shared data problem, but the correction must return through preparation. A shared correction that may alter existing findings triggers revalidation flags; it does not silently rewrite conclusions.

## Code and data principles

Code must be readable, reusable, and modular. Modules should have cohesive responsibilities and small, explicit interfaces. Parameterize meaningful variation and group related settings into named configuration objects or files with sensible defaults. A CLI is optional. Do not turn parameterization into a universal command with a sprawling interface; distinct workflows should use distinct entry points or modules while sharing common logic.

The workbench must use consistent logical locations across projects. It must not use intermediate CSV exports as handoffs between analytical steps. Intermediate computation stays in the analytical runtime, preferably as views. Materialize or cache a result only when recomputation is expensive, and record deliberate caches in the catalog. Dataset exports selected for a delivery package are audience-facing artifacts and are exempt from the intermediate-CSV rule.

Canonical, reusable views are preferred. DuckDB querying external Parquet datasets is the default. A project may select a different backend for a concrete need, including incremental workloads, while retaining independent source landing and the preparation/EDA boundary. Source conversion to Parquet is a deliberate storage boundary, not a requirement to materialize every transformation. Accumulating materialized results without an explicit reason violates the workflow.

All analytical code is tracked in Git. Delivery packages are not part of the code history under the current convention; their metadata identifies the Git commit that produced them. A commit identifies code, not input data, so delivery metadata also records input provenance and analytical settings.

## Records and vocabulary

Each investigation separates a concise current state from a chronological history:

- `state.md` captures the active question, current findings, unresolved issues, revalidation flags, and next steps so work can resume quickly.
- `history.md` captures meaningful findings, analytical decisions, caveats, superseded conclusions, and data limitations or errors that affected the investigation.

The workbench updates these records automatically when a finding, decision, flag, or next step changes. The user can also request a checkpoint before switching investigations. Records and delivery journals retain limitations and errors in the data, but exclude our mistakes in approaching the data, execution mistakes, and routine debugging. Git remains the record for code evolution.

Shared business and analytical terms live in `foundation/glossary.md`. Investigations inherit those definitions. A deliberate local meaning or departure is recorded and explained in that investigation's `brief.md`; the full glossary is not copied. Population and reporting-period choices are settings rather than competing definitions.

The glossary defines terminology; the catalog describes actual datasets, canonical views, and caches. Keep these responsibilities distinct rather than duplicating their contents.

The workflow must embed an analytics-specific domain-modeling discipline: challenge ambiguous terms, test definitions with concrete scenarios, compare definitions with source data and analytical logic, and record resolved meanings immediately in the correct analytics artifact. It must not invoke the unmodified `domain-modeling` skill, require `CONTEXT.md`, create `CONTEXT-MAP.md`, or use ADRs. The `CONTEXT.md` in this repository belongs only to the design session and is not generated in initialized workbenches.

## Grilling behavior

The initialization and investigation-scoping instructions must invoke the `grilling` skill directly when establishing a question and scope or resolving a consequential scope change. They must not invoke `grill-with-docs`.

`grilling` is an external, preinstalled dependency. Do not bundle or redistribute its implementation. Resolve it through the host's skill discovery rather than assuming a sibling file in the distribution.

Adapt the skill's interview mechanics to the user's established preference:

- ask one decision question at a time;
- include a recommended answer;
- carry settled answers forward rather than reopening them;
- ask only questions that materially affect the analysis; and
- resolve facts from the environment directly instead of asking the user to look them up.

Routine implementation choices do not require an interview. The adapted domain-modeling behavior above is embedded in the workflow instructions; it is not a second skill invocation.

The installed `grilling` skill asks its whole frontier in one round and completes only when nothing remains unassumed. The workbench rules above replace that round format and completion criterion: one question per turn, and a material unknown may stay open. The direct invocation supplies grilling's design-tree discipline and environment fact-finding, and the workbench instructions state that their rules win where the two differ.

## Directory convention

The generated workbench uses the following logical structure. Concrete filenames for executable code and configuration formats may vary by language or backend, but their responsibilities and boundaries must remain recognizable.

```text
project-root/
├── AGENTS.md
├── README.md
├── src/
│   ├── preparation/              # Reusable normalization and correction logic
│   ├── exploration/              # Neutral profiling and analytical operations
│   └── packaging/                # Shared package assembly logic
├── data/
│   ├── raw/                      # Independently landed originals and provenance
│   ├── parquet/                  # Validated datasets queried by DuckDB views
│   └── cache/                    # Deliberate, rebuildable expensive results
├── foundation/
│   ├── sources.md                # Provenance, relevance, and fitness assessments
│   ├── catalog.md                # Canonical datasets, views, and deliberate caches
│   ├── quality.md                # Limitations, errors, and correction rationale
│   ├── glossary.md               # Shared business and analytical vocabulary
│   └── views/                    # Version-controlled canonical definitions, if used
├── investigations/
│   └── <investigation-name>/
│       ├── brief.md              # Question, scope, purpose, usefulness, local terms
│       ├── state.md              # Current findings, flags, issues, and next steps
│       ├── history.md            # Meaningful learnings and analytical decisions
│       ├── <configuration>       # Population and analytical settings
│       ├── <composition-entry>   # Thin composition of shared operations
│       └── exploration/          # Local exploratory queries or notebooks
├── package-format/
│   ├── journal-template.md
│   ├── executive-summary-template.md
│   ├── m365-assembly.md
│   └── manifest-template.md      # Shared manifest field list; serialization is project-specific
├── deliveries/
│   └── <investigation-name>/
│       └── <package-name>/
│           ├── draft/
│           │   ├── journal.md
│           │   ├── executive-summary.md
│           │   ├── m365-assembly.md
│           │   ├── manifest.<format>
│           │   └── datasets/
│           └── released/
│               ├── 001/
│               └── 002/
└── .gitignore
```

Create investigation, cache, package, and release locations lazily. The structure is a stable convention, not a requirement to create empty directories or placeholder documents during initialization. There is no `CONTEXT.md` in the generated structure.

## Packaging and delivery behavior

Package creation and refresh require an explicit user request. Automatic investigation record maintenance must never trigger a package. An investigation has one named package by default, containing a detailed journal and executive summary. A second package is justified only by an independent scope or delivery schedule. Package format and M365 assembly conventions are shared across investigations.

At package creation, ask which datasets to include. Revisions inherit that selection unless the user changes it or the selected datasets no longer fit the package scope; in the latter case, ask again. Do not choose a default export set for a new package.

Each package has a stable name and one working `draft`. Revisions update that draft. Only an explicit delivery milestone creates a preserved, numbered release; later changes resume in the working draft for the next release. This replaces filename-based revision schemes such as `really-final-v3`.

Every release is self-contained and includes:

- a complete project journal for the analysis represented by that release;
- an executive summary;
- a brief description of changes since the previous release, when applicable;
- any user-selected datasets;
- M365 assembly instructions; and
- a manifest containing the producing Git commit, input provenance, analytical settings, dataset selection, and unresolved caveats.

The package narrative is authoritative upstream. The approved flow is workbench to M365. M365 formats and beautifies the provided Markdown and datasets into Word and Excel outputs; it does not supply substantive revisions back to the workbench. Reverse synchronization is out of scope.

`deliveries/` is excluded from Git by the generated ignore rules, so a numbered release is retained in local storage only. Preserving releases elsewhere, such as shared storage or backup, is a project responsibility recorded in the project README.

Working analysis uses current data and definitions. A delivered release preserves its exact exported results and provenance so later changes do not alter what it represented. Full database snapshots and exact rerun capability are not retained per release by default. Preserving enough original data for an exact rerun is an explicit choice.

Drafts may include findings flagged for revalidation if each affected conclusion carries a clear caveat and the draft lists unresolved issues. Before a flagged draft is marked delivered, require the user to choose among revalidating the finding, omitting it, or explicitly releasing it with the caveat. Packaging must not automatically rerun analysis.

## Acceptance scenarios

These scenarios are the primary acceptance checks for the eventual skills and templates.

### 1. Expansion from approximately 120 to 900 employees

An initial organizational-communications investigation covers approximately 120 employees. The user expands the same ask to a population of approximately 900 that includes the original group.

Expected behavior:

- continue the existing investigation rather than create a new one;
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
- run the grilling flow one question at a time only for unresolved scope or purpose decisions; and
- treat findings from the original population as context for method selection, not evidence about the new group.

### 3. Shared-data correction discovered through EDA

While exploring one investigation, the analyst discovers that employee email aliases were being treated as separate people.

Expected behavior:

- keep the exploratory correction local while it is being assessed;
- when accepted as a general data issue, implement it through shared preparation and document the correction and limitation in the foundation;
- update canonical data through the preparation boundary rather than silently changing it inside EDA;
- identify existing investigation findings that may be affected, flag them for revalidation, and explain why;
- do not rerun investigations or revise their conclusions automatically; and
- preserve prior numbered deliveries unchanged.

### 4. Package creation, revision, and release

The user explicitly asks for a package for an investigation, chooses which supporting datasets to include (including the option to include none), and later asks for narrative revisions and a second delivery.

Expected behavior:

- create one stable named package and ask for its initial dataset selection;
- maintain the complete narrative in the draft package rather than relying on M365 to supply missing substance;
- revise the same draft path instead of creating ad hoc names;
- inherit the selected datasets on revision unless scope makes them unsuitable;
- create release `001` only when the user explicitly marks the first draft delivered;
- create release `002` only at the next explicit delivery milestone;
- record Git commit, input provenance, settings, and dataset selection in each manifest; and
- if a finding is flagged, allow a caveated draft but require an explicit revalidate, omit, or release-with-caveat choice before delivery.

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
- retain completed landed inputs when conversion fails, allowing preparation to retry without reacquisition;
- assess relevance and fitness, then convert needed inputs into validated Parquet without modifying the landed originals;
- keep partial outputs unpublished;
- expose completed datasets through shared SQL view definitions loaded into each process's DuckDB session;
- permit separate analytical sessions to query completed, stable datasets while another job prepares new files, without requiring access to a shared writable DuckDB file; and
- apply the same landing-first rule to acquired batches if a project uses an incremental workflow or another backend.

## Explicit exclusions

The workbench does not:

- require every project to use DuckDB, or mandate Python, YAML, notebooks, or a particular CLI design;
- require a database snapshot for every release;
- treat delivery packages as the source of analytical code history;
- synchronize substantive Word or Excel edits back into the workbench;
- generate packages or ad hoc deliverables without explicit invocation;
- automatically rerun analyses when shared data changes;
- silently promote investigation-specific transformations into canonical preparation;
- retain mistakes in approaching the data, coding mistakes, or debugging logs as analytical history;
- create `CONTEXT.md`, `CONTEXT-MAP.md`, or ADRs in initialized workbenches;
- invoke `grill-with-docs` or the unmodified `domain-modeling` skill; or
- require a speculative general-purpose analytics framework beyond the current work.

## Unresolved design choices

The following choices remain open and must not be silently fixed by the specification or by an implementation without a concrete project need:

- the general rule for when a scope change becomes a new investigation rather than an expansion, beyond the accepted population scenarios above;
- the backend and refresh strategy for the exceptional incremental project; DuckDB over Parquet is the batch default;
- precise cache identity, freshness detection, invalidation, and refresh mechanics;
- the serialization format of the delivery manifest and the exact formatting of the foundation catalog; the manifest field list is fixed by the shared template;
- implementation language, executable filenames, and configuration serialization format;
- backend-specific raw-data retention and ignore rules; and
- which deliveries, if any, warrant preserving original inputs for exact reruns.
