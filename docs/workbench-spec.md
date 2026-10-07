# Analytics Workbench Skills Specification

## Status and purpose

This specification consolidates the accepted design for a reusable analytics workbench workflow. It is a drafting contract for the skills and templates described below, not an implementation plan for a software product. Acceptance is based on the workflow scenarios in this document; no issue-tracker publication, application framework, or automated test suite is required.

Requirements outside the final **Unresolved design choices** section are accepted behavior. Items in that final section remain deliberately open and must not be inferred from examples in this document.

The workbench supports one project with a shared data foundation and multiple investigations. It must let an analyst change or expand a business question without rebuilding reusable data preparation, while keeping the findings, decisions, and delivery history for each investigation distinct. An optional knowledge vault carries one analyst's reusable knowledge about the data estate (systems, databases, and tables) across projects, without carrying analytical conclusions.

## Artifacts to produce

Keep the skills as agent-agnostic folders under `.agents/skills/`. Generated projects use root `AGENTS.md` instructions and do not require `.github` directories, project-local skill copies, or vendor-specific instruction bridges. Git remains the code-history mechanism; GitHub hosting is not required.

The eventual implementation must provide these artifacts:

1. **Initialization skill (`awb-init`).** Establishes the project structure, working conventions, shared data foundation, and the first investigation. A new project starts from a business question; the skill asks for one when none is supplied and completes setup without an investigation only when the user explicitly has none yet. It also starts later investigations and resolves consequential scope changes, directly invoking the `grilling` skill as described below. It does not create a delivery package or a knowledge vault.
2. **Project `AGENTS.md` template.** Governs daily analytical work, architectural boundaries, automatic record maintenance, source and cache handling, investigation switching, when the knowledge vault is read, and the prohibition on unsolicited deliverables.
3. **Status skill (`awb-status`).** A read-only report of the active investigation, findings and revalidation flags, unresolved issues, package and release state, landed data and release storage, and vault configuration, ending with the requests that are relevant now. It changes nothing and makes the workbench's request-gated capabilities discoverable to the analyst.
4. **Packaging skill (`awb-package`).** Creates or revises a named delivery package's working draft only when the user explicitly requests it. It gathers the package's dataset selection, records provenance, carries caveats for findings awaiting revalidation, and produces a complete upstream narrative plus M365 assembly instructions. It owns the draft layout, shared package format, manifest fields, and draft consistency rules.
5. **Release skill (`awb-release`).** Preserves a numbered release from the working draft only when the user explicitly marks the package delivered. It verifies the draft against the packaging skill's consistency rules, obtains a disposition for each unresolved revalidation flag, and records the project's release storage location, copying each release there when reachable.
6. **Knowledge vault skill (`awb-vault`).** Creates a knowledge vault, and records data-estate knowledge in one, only when the user explicitly asks. Its one asset is the vault-root `AGENTS.md`, stating the page conventions in **Knowledge vault**, written only at vault creation and never over an existing file.
7. **Visualization skill (`awb-visualize`).** Principles for attractive, legible charts, figures, diagrams, and results tables that display correctly inline in the agent chat and when pasted into a document, while keeping presentation logic out of neutral analytical operations.
8. **Supporting templates.** Provide consistent starting formats for the shared source register, data catalog, quality record, glossary, investigation brief, current state, investigation history, package journal, executive summary, M365 assembly instructions, and delivery manifest. Templates should be created or instantiated only when the corresponding artifact is needed.

Every skill name carries the `awb-` prefix so the workbench's actions group together in hosts that list skills as commands.

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

`data/raw/` is excluded from Git by the generated ignore rules, and a landed original often cannot be fetched again, such as a point-in-time API response or an extract from a system that has since changed. Before the first acquisition is landed, the agent asks where landed originals are retained outside the checkout and records the answer in the project README on a line reading `Landed data is kept at: <location>`. A declined answer is recorded as `none chosen`, a decision whose only-copy warning is repeated after each landing. After each completed landing, the agent copies the landed artifact and its provenance to the same relative path under `<location>/data/raw/` when the location is a reachable filesystem path, never overwriting an existing destination; otherwise it states exactly what to copy and where. The source register records each acquisition's retained copy, as the verified destination path or `this checkout only`, and the status skill reports acquisitions held only in this checkout.

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
│   ├── packaging/                # Shared package assembly logic
│   └── presentation/             # Shared figure style and figure builders
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
│       ├── figures/              # Figures cited as evidence for findings
│       └── exploration/          # Local exploratory queries, notebooks, and figures
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
│           │   ├── figures/
│           │   └── datasets/
│           └── released/
│               ├── 001/
│               └── 002/
└── .gitignore
```

Create investigation, cache, package, and release locations lazily. The structure is a stable convention, not a requirement to create empty directories or placeholder documents during initialization. There is no `CONTEXT.md` in the generated structure. The knowledge vault, when used, lives outside every project in a folder of its own; see **Knowledge vault**.

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

`deliveries/` is excluded from Git by the generated ignore rules, so a numbered release is retained in local storage only. Preserving releases elsewhere, such as shared storage or backup, is a project responsibility. The release skill asks for that location before the first release, records it in the project README, and copies each new release there when the location is reachable from the project; otherwise it states exactly what to copy and where. Landed data follows the same rule through the project `AGENTS.md`, on its own README line, because a release manifest cites acquisition identifiers whose landed originals would otherwise exist on one disk only. The release skill warns at each release about any cited acquisition without a retained copy.

Working analysis uses current data and definitions. A delivered release preserves its exact exported results and provenance so later changes do not alter what it represented. Full database snapshots and exact rerun capability are not retained per release by default. Preserving enough original data for an exact rerun is an explicit choice.

Drafts may include findings flagged for revalidation if each affected conclusion carries a clear caveat and the draft lists unresolved issues. Before a flagged draft is marked delivered, require the user to choose among revalidating the finding, omitting it, or explicitly releasing it with the caveat. Packaging must not automatically rerun analysis.

## Knowledge vault

An analyst may keep a knowledge vault: a folder of plain Markdown, opened in Obsidian, that records what they have learned about the data estate they work with (its systems, databases, schemas, and tables) so that knowledge gained in one project is found when a later project touches the same object. The vault lives outside every project and is optional. A project works fully without it, and nothing a project's results depend on lives only in the vault.

### Scope: how to read the data, not what it showed

The vault records knowledge about data objects and how to read and use them. It does not record analytical conclusions. The boundary test is whether a statement would change if the business changed: "pay_detail excludes contractors" belongs in the vault; "contractor share is rising" does not. A known issue may note that ignoring it once changed a result, without saying which way.

The vault records curated knowledge about interpreting and handling data objects: meaning, grain, coverage, keys and joins, code values and their meanings, refresh behavior, known issues and their handling, and which object to use for which need. It does not mirror schemas: no exhaustive column lists, types, or row counts. A structural detail appears only where it explains meaning or handling, and each object page says where its full column list can be read. The vault contains no credentials or other secrets, no record-level data, and no paths that work only on one machine. System, server, and database names, code values, and access instructions are allowed.

### Layout

```text
<vault-root>/
├── AGENTS.md               # Conventions; the only file a new vault starts with
├── choosing.md             # Which object to use for which need (created when first needed)
├── glossary.md             # Business terms that span objects (created when first needed)
└── <system>/               # One folder per system the analyst connects to or receives data from
    ├── README.md           # What the system is, how it is identified and accessed, system-wide behavior
    └── <qualified-name>.md # One page per object used or assessed, e.g. PAY.dbo.pay_detail.md
```

A system is a database server, warehouse, application, or provider. Its folder has a short name the analyst chooses, and its `README.md` records how the system is identified in connections (server, host, or provider name). An object is a table, view, file extract, or API endpoint in a system. An object's page is named by its qualified name within the system (`database.schema.table` for a database; the extract name or endpoint path otherwise), with any character not allowed in file names, including `/`, replaced by `_`. If two exact names map to the same file name, including names that differ only in letter case, give each a distinct file name and list the exact-name-to-file mapping in the system `README.md`. The page's first line states the exact qualified name; before using or changing a page, check that it names the intended object. An agent holding a qualified name finds the page by path, through the system `README.md` mapping, or by searching the system `README.md` files for the server or provider name when the folder is not obvious.

Knowledge that applies to many objects goes on the narrowest page that covers them: the system `README.md`, or a database or schema page named by its qualified name (`PAY.md`, `PAY.dbo.md`). Create a page only for an object the analyst has used or assessed, and only when something is recorded about it; never populate the vault from a system catalog.

An object page covers, as far as known: what the object is and its grain; keys and how it joins to other objects, with cardinality and conditions; fields whose meaning, coding, or behavior is not obvious from their names; coverage and refresh behavior; known issues and how to handle them; copies of it in other systems, or the object it copies, with any lag; and where its full column list can be read. No section and no frontmatter is required.

`choosing.md` has one entry per recurring need: the preferred object, alternatives and when they fit, objects to avoid and why, and the coverage and date the preference rests on. Comparative preference lives only there; object pages state facts. `glossary.md` holds business terms whose definition spans objects; a term defined by one field is recorded on that object's page.

Each claim carries, inline, its date and how it was established (documentation, a query or check, or the system owner's word), for example "a rerun pay run duplicates rows per (employee_id, pay_period); keep the highest run_id within each (checked by query, 2026-08)". A claim about a period states the period. Refreshing one claim never makes another look current. When an object is renamed or moved, rename its page, update links to it, and keep the old name on the page. Agents write file-relative Markdown links inside the vault; Obsidian resolves those and any wikilinks a person adds.

### Access and reading

Agents read and write the vault through the filesystem; no Obsidian plugin, REST API, or MCP server is required. The vault location is a user-level setting: the `WORKBENCH_VAULT` environment variable or an equivalent line in user-level agent instructions. When it is unset or inaccessible, report that the vault was not consulted and continue from project records.

The project `AGENTS.md` template gains a short **Knowledge vault** section holding the location rule, the read triggers, and the write rule. `awb-init` applies the read triggers during scoping. `awb-vault` creates a vault on explicit request at a user-named path by writing only its `AGENTS.md`, and records knowledge in it on explicit request. Project initialization never creates a vault as a side effect. The vault-root `AGENTS.md` alone owns page conventions.

Read triggers:

- once per session, before the first vault read: the vault-root `AGENTS.md`;
- before first assessing, querying, or interpreting an object in a session: its system `README.md`, any database or schema page above it, and its own page; if it has no page, search the vault once for its name and move on;
- when choosing which object to use for a need: `choosing.md`; and
- when defining a business term against data: `glossary.md`.

Do not sweep the vault. Vault claims are dated prior knowledge, not evidence about the data a project acquired: before preparation depends on one, check it against the acquired data when a check is feasible, and record the result in the project. During scoping, a `choosing.md` preference whose recorded coverage fits the question supplies the recommended answer to the source question, with its date. When that coverage does not fit the question's population or period, do not recommend the preference as it stands; state the gap and recommend objects that together cover the question, or leave the source question open.

### Relationship to project records

The vault describes estate objects as they exist, independent of any project. Project records describe what the project did with them:

- `foundation/sources.md`: which objects the project uses, their fitness for its question, and its acquisitions;
- `foundation/catalog.md`: the project's own datasets, views, and caches, which never go in the vault;
- `foundation/quality.md`: the issues that affect the project's canonical data and the treatment applied; and
- `foundation/glossary.md`: the definitions the project adopted.

When the project relies on a vault claim, it records the claim with its date and basis, and a labeled plain-text reference in the cell that holds it, for example `vault: payroll/PAY.dbo.pay_detail.md`, so the project stays complete and later vault edits do not change it. When project work contradicts or extends a vault page, record that in the project and tell the user which page differs; change the vault only on request.

### Writing

Write to the vault only when the user explicitly asks, having read the vault-root `AGENTS.md`. Apply the boundary test; when a candidate statement fails it, explain why and leave it out. Put each fact on the narrowest page it applies to, creating that page and its system `README.md` when absent. Git is optional; if the vault is a Git repository, commit only on explicit request.

### Sharing with a team (optional)

The solo vault never depends on this subsection. A team can share a vault by keeping it in a Git repository with a remote. Then pull fast-forward-only before changing pages and stop if the clone has diverged; push only on explicit request; do not also sync the folder through a file-sync service or Obsidian Sync; and add the observer's initials to each new claim. Curation and review policy are the team's choice.

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
- before the first landing, ask where landed originals are retained outside the checkout and record it in the README; after each completed landing, copy the landed artifact and provenance there without overwriting when the location is reachable, or state exactly what to copy and where, and record the retained copy in `foundation/sources.md`;
- retain completed landed inputs when conversion fails, allowing preparation to retry without reacquisition;
- assess relevance and fitness, then convert needed inputs into validated Parquet without modifying the landed originals;
- keep partial outputs unpublished;
- expose completed datasets through shared SQL view definitions loaded into each process's DuckDB session;
- permit separate analytical sessions to query completed, stable datasets while another job prepares new files, without requiring access to a shared writable DuckDB file; and
- apply the same landing-first rule to acquired batches if a project uses an incremental workflow or another backend.

### 7. Reusing estate knowledge in a new project

The vault has `payroll/README.md`; `payroll/PAY.md` (every PAY table reloads nightly and the previous day is incomplete until 06:00); `payroll/PAY.dbo.pay_detail.md` (a rerun pay run duplicates rows per (employee_id, pay_period); keep the highest run_id within each); and pages for both `hrdw/HRDW.dbo.emp_snapshot.md` and `hrdw/HRDW.stage.emp_snapshot.md`. Its `choosing.md` prefers `HRDW.dbo.emp_snapshot` for headcount as of a date, resting on coverage of employees only (observed 2026-05). A new investigation needs headcount as of a date for employees and contractors, and will use pay_detail.

Expected behavior:

- read the vault-root `AGENTS.md`, `choosing.md`, and for each object considered its system `README.md`, database page and object page, reading the `dbo` emp_snapshot page and not the `stage` one when the query uses `HRDW.dbo.emp_snapshot`; do not sweep the vault;
- not recommend emp_snapshot as it stands: state that its coverage excludes contractors, and recommend objects that together cover contractors or leave the source question open;
- account for the PAY reload window when setting the acquisition cutoff, and check the pay_detail duplication against the acquired data before preparation applies the handling;
- record the source choice and reason in `foundation/sources.md`, and the pay_detail issue, check result and treatment in `foundation/quality.md`, each with the claim's date, basis and a `vault:` reference; and
- leave the vault unchanged.

### 8. Recording estate knowledge on request

During an investigation the user asks the agent to record: that a query in this project shows pay_detail reruns no longer duplicate rows from the 2026-09 pay period; that `HRDW.dbo.term_events` has one row per termination event and that its reason codes `RES` and `RET` mean voluntary exits; the definition of voluntary exit used across HRDW and payroll; and that attrition is highest in sales.

Expected behavior:

- read the vault-root `AGENTS.md` first;
- on the pay_detail page, keep the earlier duplication claim with its original date, basis and scope; add the new claim that reruns from the 2026-09 pay period onward do not duplicate rows, with its date and basis; and narrow the handling advice only as far as the new evidence supports, leaving the status of earlier periods as recorded;
- create `hrdw/HRDW.dbo.term_events.md` (and `hrdw/README.md` if absent) with the supplied grain and code meanings, without copying its column list or adding facts that were not supplied;
- add voluntary exit to `glossary.md`, linking the object pages it rests on;
- decline to record the sales attrition statement, explaining the boundary test;
- create no page for any object not involved; and
- commit only on explicit request when the vault is a Git repository.

### 9. A project that contradicts the vault, and a project without one

A project's query shows that `PAY.dbo.pay_detail` no longer duplicates rows on rerun, contrary to its vault page. Separately, a project runs where no vault location is configured.

Expected behavior:

- the first project records the observation in its own `foundation/quality.md`, tells the user the vault page differs, and leaves the vault unchanged; and
- the second reports that the vault was not consulted and continues from its own records.

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
- invoke `grill-with-docs` or the unmodified `domain-modeling` skill;
- store analytical conclusions in the knowledge vault or mirror system schemas into it;
- read other investigations' or projects' conclusions on the agent's own initiative before an investigation's own results exist, except that a related investigation's findings may inform method selection as in scenario 2;
- require the knowledge vault for project work, write to it without an explicit request, populate it in bulk from system catalogs, or require Git, an Obsidian plugin, REST API, or MCP server to use it; or
- require a speculative general-purpose analytics framework beyond the current work.

## Unresolved design choices

The following choices remain open and must not be silently fixed by the specification or by an implementation without a concrete project need:

- the general rule for when a scope change becomes a new investigation rather than an expansion, beyond the accepted population scenarios above;
- the backend and refresh strategy for the exceptional incremental project; DuckDB over Parquet is the batch default;
- precise cache identity, freshness detection, invalidation, and refresh mechanics;
- the serialization format of the delivery manifest and the exact formatting of the foundation catalog; the manifest field list is fixed by the shared template;
- implementation language, executable filenames, and configuration serialization format;
- backend-specific raw-data retention and ignore rules, beyond the landed-data storage rule in **Question-driven data preparation**; and
- which deliveries, if any, warrant preserving original inputs for exact reruns.
