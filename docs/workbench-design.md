# Workbench design decisions

These notes capture accepted decisions from the design interview. The workflow design remains in progress.

## Baseline principles

- Prefer readable, reusable, modular code. Organize code around cohesive responsibilities, with small, explicit interfaces between data preparation, analytical methods, and packaging.
- Parameterize meaningful variation across populations or iterations while keeping each module's interface focused. Group related settings into named configuration objects or files, with sensible defaults. Expose only the small set of controls needed for the task at the entry point; a CLI is optional, not the goal. When options represent distinct workflows, separate those workflows into modules or entry points rather than expanding one universal command. Share common logic instead of duplicating scripts.
- Maintain a consistent directory structure across projects and investigations. The current workflow uses root-level `src/` and `data/`; the expanded layout is still to be specified.
- Do not export intermediate CSV files as handoffs between analysis steps. Keep intermediate computation in views or the analytical runtime; cache expensive results deliberately. User-selected dataset exports for delivery packages are separate from intermediate computation.
- Maintain canonical, reusable views of the data in the shared analytical store. DuckDB currently serves this role, but the principle survives a change in storage technology.
- Maintain a catalog of the shared analytical store's datasets and canonical views, separate from investigation records. Its exact format remains to be specified.
- Generate ad hoc deliverables only upon explicit user invocation.
- Track all analytical code in Git and identify the producing commit in delivery metadata.

## Project and investigation boundaries

A project contains a shared data foundation and multiple investigations, each with its own business question, progress, and findings. Data preparation and quality knowledge belong to the shared foundation.

The user's example distinguishes an initial communications analysis of approximately 120 employees, an expansion to approximately 900 employees within the same investigation, and a separate investigation asking the same questions about an independent group. A general rule for investigation boundaries remains to be defined.

When starting a related investigation, assume the current analytical method and parameters apply unless the user corrects them. Carry those choices forward as the starting configuration, reuse shared preparation logic and analysis code, and begin fresh findings and progress for the new scope. Prior findings are not evidence for the new population.

## Storage and computation

Data preparation is driven by the active business question. Assess candidate sources for relevance and fitness first, doing only enough cleaning to make that assessment. Prepare the data needed for the question; broader preparation requires an explicit request. If a source proves irrelevant, record why and stop preparing it.

An investigation motivates preparation, while reusable cleaning and normalization logic and discoveries about data quality belong in the shared foundation. Question-specific filters, exclusions, and analytical assumptions belong to the investigation. Preparation and analysis can proceed iteratively as new issues are discovered.

The default storage workflow is independently landed source files, validated Parquet datasets, and canonical DuckDB views over those files. Each analytical process owns its DuckDB session and loads shared, Git-managed SQL definitions. A shared writable DuckDB file is not required. Projects with different needs, including incremental workloads, may use a different backend while preserving the ingestion boundary below.

Data gathering must always land source records durably and independently before introducing them into the canonical database. API responses and SQL Server extracts are captured as source artifacts with acquisition provenance, rather than being streamed directly into canonical tables as their only retained representation. Completed landed artifacts are the inputs to conversion and preparation; incomplete acquisitions remain unpublished. Preparation can be retried from those artifacts without fetching the source again.

Preserve landed originals separately from derived Parquet datasets. Conversion establishes a validated storage representation, not an automatic claim that cleaning is complete. Canonical views apply documented normalization and correction rules. Initial CSV/JSON landing is source acquisition and does not violate the prohibition on intermediate CSV handoffs. The same independent-landing boundary applies to each batch of an incremental project.

Prefer views; cache results when recomputation is expensive. Accumulating materialized tables within one database has caused excessive storage growth.

## Preparation and exploration boundary

Preparation owns explicit, reusable normalization, quality checks, and documented corrections that produce canonical data. EDA consumes canonical data and may apply local exploratory transformations; it does not silently rewrite canonical data or shared preparation rules. Promote an exploratory transformation into shared preparation deliberately, keeping question-specific exclusions local. This boundary does not require cleaning to finish before exploration, separate databases, or a heavyweight pipeline.

Shared analytical code implements neutral operations on data independently of a desired narrative or conclusion. Investigations compose those operations through a thin layer of scope and settings; interpretation and presentation remain separate from computation. Reuse existing operations where possible, return relevant results even when they contradict an anticipated explanation, and avoid speculative general-purpose frameworks.

## Working data and delivery history

Working analysis uses current data and definitions, refreshing caches as needed. Each delivered package retains its exact exported results and records its Git commit SHA, input provenance, and analytical parameters. Later workbench updates must not silently change what an earlier delivery represents.

Preserving enough data for exact reruns is an explicit choice, rather than a default full database snapshot for every delivery. Code is tracked in Git; delivery packages currently are not.

## Package revisions

Creating or refreshing a delivery package requires an explicit user request. Automatic maintenance of investigation records does not trigger package generation or revision.

When creating a package, ask the user which datasets to include. Reuse that selection for revisions unless the user changes it or the selected datasets no longer fit the scope; ask again when they no longer fit. Do not assume a default set of dataset exports for a new package.

Draft packages may include findings awaiting revalidation, with a clear caveat beside each affected conclusion and a short list of unresolved issues. Before marking the package delivered, require the user to choose revalidation, omission of the affected conclusion, or explicit delivery with the caveat. Packaging does not automatically trigger analysis reruns.

Each package has one stable name and one current working draft. Revisions update that draft until the user explicitly marks it as delivered. That milestone preserves a numbered delivery; subsequent edits begin the next working revision. Numbered deliveries are created only at explicit delivery milestones.

An investigation has one delivery package by default, containing both the detailed journal and executive summary. Additional packages are created only for an independent scope or delivery schedule.

Package structure is a shared format choice, not an investigation choice. Related investigations inherit the journal, executive-summary, and M365 assembly conventions; their narrative and results are specific to the investigation.

Each delivery's detailed journal is self-contained and explains the analysis represented by that delivery. When applicable, include a brief section describing changes since the previous delivery.

## M365 handoff

The approved direction is the workbench to M365. Each package contains a cohesive, complete narrative and any accompanying datasets and assembly instructions. M365's role is presentation and formatting in Word and Excel. Reverse synchronization from M365 is out of scope; substantive narrative revisions belong in the package sources.

## Workflow responsibilities

Keep the skills as agent-agnostic folders under `.agents/skills/`. Keep generated project behavior in root AGENTS.md; do not generate vendor-specific instruction bridges or require project-local skill installations. Git is required for code history, but GitHub hosting is not.

Keep initialization and packaging as separate skills. Initialization establishes the workspace and conventions. The project's AGENTS.md governs everyday analytical work and automatic recordkeeping. The packaging skill creates or revises packages only when explicitly invoked.

## Design-session artifacts and generated workbenches

The CONTEXT.md in this design workspace is an artifact of the grill-with-docs session, not a required artifact of an initialized analytics workbench. Omit it from the proposed generated directory structure. The same distinction applies to these design notes: they inform the skills rather than becoming default project scaffolding.

The domain-modeling skill itself introduces CONTEXT.md and ADR conventions; grill-with-docs is the wrapper that invokes it alongside grilling. These software-engineering document conventions are not required analytics deliverables or project records.

The workflow instructions must invoke the grilling skill directly when establishing an investigation's question and scope or resolving a consequential scope change. Do not route this through grill-with-docs. Honor the user's preference for one question at a time, provide a recommendation, and carry forward settled answers rather than reopening them. Keep the interview focused on decisions that affect the analysis; routine implementation choices do not require another interview. These rules replace grilling's one-round frontier format and its empty-frontier completion rule; the workbench instructions say so explicitly so the two loaded skills do not compete.

Grilling is an external dependency. Do not include its source in this repository or generated archives; discover the installed skill by name.

The workflow instructions must include an analytics-specific adaptation of domain modeling: challenge ambiguous terms, test definitions against concrete examples, check definitions against source data and analytical logic, and record resolved meanings immediately. Shared vocabulary belongs in foundation/glossary.md, local departures in investigation briefs, analytical decisions in investigation histories, and dataset/view descriptions in the foundation catalog. These destinations replace domain-modeling's CONTEXT.md, CONTEXT-MAP.md, and ADR conventions. Incorporate the adapted guidance into the workflow rather than invoking the unmodified domain-modeling skill or grill-with-docs wrapper. The installed skills have not been modified.

## Glossary ownership

Generated workbenches include `foundation/glossary.md` for shared business and analytical vocabulary. Investigations inherit those definitions. Record investigation-specific meanings or deliberate departures in that investigation's `brief.md`, explaining the difference without silently changing the shared definition or duplicating the full glossary.

Keep definitions separate from scope and configuration: a selected population or reporting period ordinarily changes the investigation's settings, not the meaning of shared terms. The glossary holds terminology; the foundation catalog describes datasets and views. This analytics glossary is distinct from the design session's CONTEXT.md.

## Investigation records

At investigation creation, capture the business question, population or scope, the decision the analysis will support, and what would make the answer useful. Allow an exploratory purpose and explicitly record unknowns rather than requiring a predetermined decision or outcome. Use this brief to guide source relevance and preparation effort.

Separate a concise current-state summary from a chronological history of meaningful learnings and decisions. The current state supports resuming work; the history retains analytical reasoning, caveats, superseded conclusions, and relevant data limitations or errors. Execution mistakes, mistaken approaches to the data, and routine debugging are excluded from both the investigation history and the delivery journal. Shared data preparation and quality knowledge remain part of the data foundation.

The agent maintains these records automatically when a finding, decision, or next step changes. Explicit checkpoints are also available before switching investigations.

When a shared data correction could affect investigation findings, flag those findings for revalidation and explain the reason. Do not automatically rerun the affected analysis or revise its conclusions. Previously delivered packages remain preserved.

When work resumes, continue the last active investigation unless the user indicates a switch, and briefly identify that investigation. If a request could fit multiple investigations, ask before changing their records.

## Open design questions

- When a change starts a new investigation rather than expanding an existing one.
- How cache freshness and expensive recomputation are managed.
