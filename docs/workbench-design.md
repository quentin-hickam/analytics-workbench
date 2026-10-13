# Workbench design decisions

These notes record the decisions that the design interview accepted. The workflow design is not complete.

## Baseline principles

- If possible, write readable, reusable, modular code. Organize code around cohesive responsibilities. Use small, explicit interfaces between data preparation, analytical methods, and packaging.
- Parameterize meaningful variation across populations or iterations, and keep the interface of each module focused. Group related settings into named configuration objects or files, with sensible defaults. At the entry point, expose only the small set of controls that the task needs. A CLI is optional, and it is not the goal. When options represent distinct workflows, separate those workflows into modules or entry points. Do not expand one universal command for them. Share common logic instead of duplicate scripts.
- Use a consistent directory structure across projects and investigations. The current workflow uses root-level `src/` and `data/`. The expanded layout is not specified yet.
- Do not export intermediate CSV files as handoffs between analysis steps. Keep intermediate computation in views or in the analytical runtime. Cache expensive results as a deliberate decision. Dataset exports that the user selects for delivery packages are separate from intermediate computation.
- Keep canonical, reusable views of the data in the shared analytical store. At this time, DuckDB has this role. But the principle stays the same if the storage technology changes.
- Keep a catalog of the datasets and canonical views in the shared analytical store. Keep this catalog separate from investigation records. Its exact format is not specified yet.
- Before you present results, validate these items: columns, row counts, joins, nulls, scope, metrics, and values. This checklist comes from the earlier framework. It always applies, and the evidence of each result records it.
- Make ad hoc deliverables only when the user explicitly invokes them.
- Track all analytical code in Git. Identify the producing commit in the package manifest.

## Project and investigation boundaries

A project contains a shared data foundation and multiple investigations. Each investigation has its own business question, progress, and findings. Data preparation and quality knowledge belong to the shared foundation.

The example from the user shows three different cases:

- An initial communications analysis of about 120 employees.
- An expansion to about 900 employees in the same investigation.
- A separate investigation that asks the same questions about an independent group.

A general rule for investigation boundaries is not defined yet.

When you start a related investigation, assume that the current analytical method and parameters apply, unless the user corrects them. Use those choices as the initial configuration. Reuse shared preparation logic and analysis code. Start new findings and new progress for the new scope. Earlier findings are not evidence for the new population.

## Storage and computation

The active business question drives data preparation. First, assess candidate sources for relevance and fitness. Do only enough cleaning to make that assessment. Prepare the data that the question needs. Broader preparation needs an explicit request. If a source is shown to be irrelevant, record why and stop the preparation of that source.

An investigation is the reason for preparation. But reusable cleaning and normalization logic, and discoveries about data quality, belong in the shared foundation. Question-specific filters, exclusions, and analytical assumptions belong to the investigation. Preparation and analysis can continue in iterations when new issues are found.

The default storage workflow is independently landed source files, validated Parquet datasets, and canonical DuckDB views over those files. Each analytical process owns its DuckDB session and loads shared, Git-managed SQL definitions. A shared writable DuckDB file is not necessary. Projects with different needs (incremental workloads are one example) can use a different backend if they keep the ingestion boundary below.

Data gathering must always land source records durably and independently before it puts them into the canonical database. API responses and SQL Server extracts are captured as source artifacts with acquisition provenance. They are not streamed directly into canonical tables as their only retained representation. Completed landed artifacts are the inputs to conversion and preparation. Incomplete acquisitions stay unpublished. You can do preparation again from those artifacts, without a new fetch of the source.

Keep landed originals separate from derived Parquet datasets. Conversion makes a validated storage representation. It is not an automatic claim that cleaning is complete. Canonical views apply documented normalization and correction rules. Initial CSV/JSON landing is source acquisition, and it does not break the prohibition on intermediate CSV handoffs. The same independent-landing boundary applies to each batch of an incremental project.

`data/raw/` is excluded from Git, as `deliveries/` is. For the same reason, the project records where the copies are kept. You can rebuild Parquet datasets and caches from landed originals and Git-managed code. But frequently it is not possible to fetch a landed original again. If the one disk that holds a point-in-time API response is lost, the response is lost too. The same applies to an extract from a system that changed after the extract. Then every release manifest that cites that acquisition points at nothing.

For this reason:

- The project README records where landed data is kept.
- When the location is reachable, the agent copies each completed landing there. If it is not reachable, the agent says what to copy.
- The source register records the retained copy of each acquisition. Then status and release can report what exists only in this checkout.

The project AGENTS.md makes the data guide mandatory before acquisition or storage changes. That conditional guide holds the retention procedure. The procedure keeps landed originals outside the checkout. It does not add inputs to releases. The addition of inputs to releases is still the explicit exact-rerun choice.

If possible, use views. When recomputation is expensive, cache the results. In the past, an accumulation of materialized tables in one database caused too much storage growth.

## Preparation and exploration boundary

Preparation owns explicit, reusable normalization, quality checks, and documented corrections that produce canonical data. EDA uses canonical data and can apply local exploratory transformations. EDA does not silently rewrite canonical data or shared preparation rules. Promote an exploratory transformation into shared preparation as a deliberate decision, and keep question-specific exclusions local. This boundary does not need cleaning to finish before exploration. It also does not need separate databases or a heavyweight pipeline.

Shared analytical code implements neutral operations on data, independently of a desired narrative or conclusion. Investigations compose those operations through a thin run script, `run.py`, over their scope and settings. Interpretation and presentation stay separate from computation. Where possible, reuse existing operations. Return relevant results, also when they contradict an expected explanation. Do not make speculative general-purpose frameworks.

## Working data and release history

Working analysis uses current data and definitions, and it refreshes caches when necessary. Each release is frozen. A release keeps its exact exported results. It also records its Git commit SHA, input provenance, and analytical parameters. As a result, later workbench changes cannot change what an earlier release represents.

To keep enough data for exact reruns is an explicit choice. It is not a default full database snapshot for every release. Git tracks the code. At this time, Git does not track delivery packages.

## Package revisions

Create or refresh a delivery package only when the user explicitly requests it. Automatic maintenance of investigation records does not trigger package generation or revision.

When you create a package, ask the user which datasets to include. Reuse that selection for revisions, unless the user changes it or the selected datasets no longer fit the scope. When the selected datasets no longer fit, ask again. Do not assume a default set of dataset exports for a new package.

Draft packages can include flagged findings. A draft package with flagged findings has a clear caveat beside each affected conclusion and a short list of unresolved issues. Before you mark the package as delivered, get the disposition of the user for each flagged finding. The disposition is one of these: revalidation, omission of the affected conclusion, or explicit release with the caveat. Packaging does not automatically trigger analysis reruns.

Each package has one stable name and one current working draft. Revisions update that draft until the user explicitly marks it as delivered. That milestone keeps a numbered, frozen release. Later edits start the next working revision. Numbered releases are created only at explicit delivery milestones.

By default, an investigation has one delivery package. Its draft holds an audience-facing findings document and an internal methodology reference. The findings document is written as the deck outline, and the **Answer** slide of that outline is the executive summary. Other packages are created only for an independent scope or delivery schedule.

Package structure is a shared format choice, not an investigation choice. Related investigations inherit the findings, methodology, and M365 assembly conventions. Their narrative and results are specific to the investigation.

The findings document of each release is self-contained for the audience that the investigation brief records. It is the only source of slide content. It uses the business terms of that audience. File names, view and column names, settings keys, internal identifiers, and code terms stay out of it. A packaging helper checks for them.

The methodology document is self-contained as the account of the analysis, and those identifiers belong in it. It lets the M365 agent and analysts look up the internal logic behind a decision. The two documents agree in claims, numbers, qualifications, and caveats. Each finding has a section under the same heading in the two documents. When applicable, the two documents include a brief section that describes changes since the previous release.

An earlier format packaged a journal. The journal was the internal record of decisions and also the source text for the audience document. M365 built its report when it made a narrative from the journal. As a result, file and column names went into delivered documents. Because the two documents are now separate, that internal record stays out of what M365 renders.

The delivered output is a PowerPoint deck, not Word and Excel documents. The reason is that the conceptual outline of a deck is easier to check than the outline of a report. For this reason, the findings document is written as the slide-by-slide outline of the deck. Each slide has:

- A one-sentence headline with its number.
- A few bullets.
- Caveats on the slide that they qualify.
- Speaker notes.

With this structure, the user reads the headings to check the storyline before M365 builds anything. The **Answer** slide of the outline is the executive summary. M365 no longer derives one.

The workbench ships no figure style. An earlier visualization skill rendered PNG figures in a shared style. Its chart forms, style, and honest-display rules are now only in the M365 assembly instructions. M365 draws native, editable charts. The plotted numbers stay upstream. Each chart is these two items:

- A specification in the findings outline (form, comparison, highlight, axis, interval, source, caveat, alt text).
- One CSV of exactly the plotted values. This CSV is serialized from a recorded result. When that result is stale, the CSV is refused, as datasets are.

M365 draws from that file and never aggregates. As a result, every number on a slide still traces to a recorded result.

## M365 handoff

The approved direction is from the workbench to M365. Each package contains a complete findings outline and an internal methodology reference. It also contains any accompanying chart files, datasets, and assembly instructions. In the Microsoft 365 Copilot app, the PowerPoint agent builds and styles the deck from the outline, and it draws each chart from its file. That is its role. The datasets are delivered beside the deck.

The agent asks the requester before it builds when one of these conditions occurs:

- The audience or decision is different.
- A slide will not fit.
- It is not possible to draw a chart as specified.
- The effect of a caveat is not clear.

The agent consults the methodology reference only to understand a decision. It never copies identifiers from that reference onto a slide. Reverse synchronization from M365 is out of scope. Substantive narrative revisions belong in the package sources.

## Workflow responsibilities

Keep the skills as agent-agnostic folders under `.agents/skills/`. Keep generated project behavior in the root AGENTS.md. Do not generate vendor-specific instruction bridges. Do not make project-local skill installations mandatory. Git is mandatory for code history, but GitHub hosting is not.

Keep initialization and packaging as separate skills. Initialization sets up the workspace and conventions. The project's AGENTS.md controls everyday analytical work and automatic recordkeeping. The packaging skill creates or revises packages only when it is explicitly invoked.

The analyst could not see request-gated capabilities, because their trigger phrases were only in agent-facing instructions. For this reason, each user-initiated action that has its own procedure and gate is a skill. Every skill name has the `awb-` prefix, so that the actions are together in hosts that list skills as commands. The skills are `awb-init`, `awb-status`, `awb-clean`, `awb-eda`, `awb-package`, and `awb-release`.

Cleaning and exploration work on one dataset at a time, on the two sides of the preparation/EDA boundary. `awb-clean` changes shared canonical data and flags affected findings. `awb-eda` reads canonical data in one investigation and gives shared problems to `awb-clean`. It records a confirmed coverage gap as an open quality row, because no correction can fill missing periods.

Universal invariants and routing stay in the project AGENTS.md. Acquisition and analysis procedures are in project-local workbench-guides. These guides are read before their applicable operations.

Initialization and investigation scoping stay one skill. The reason is that a project always starts with a use case. A separate investigation skill will add a choice at the start, and it will not serve a distinct need. AGENTS.md routes later investigations and scope changes to this skill.

Releasing is separate from packaging, so that the invocation of the release skill is itself the explicit delivery request. The packaging skill stays the single owner of the draft layout, manifest fields, and consistency rules. `deliveries/` is excluded from Git. For this reason, the release skill asks for the release storage location and records it. When the location is reachable, the skill copies each release there. Gates stay description-based, because user-only invocation needs vendor-specific frontmatter.

When newer skills are installed, the work to bring a workbench up to date is part of the `awb-init` repair. A separate `awb-update` skill was removed. Without a record, the agent cannot tell an earlier shipped copy from a copy that the project customized. This applies to a helper, a package-format file, or a workbench guide. For this reason, that check stays mechanical:

- The installer writes a receipt (`.awb-receipt.json`, path to SHA-256) of every file that it installs or replaces.
- `--upgrade` replaces only files whose checksum matches their receipt entry. It reports customized copies for the user to decide. It removes retired unmodified files only when asked.

Adapted files (`AGENTS.md`, `README.md`) are edited for each project, so no record can recognize them. In repair, the agent reconciles them against the current templates. Because the update is part of repair, there is one fewer always-loaded skill description. Also, no per-release list of instruction migrations accumulates. The current templates are the single target.

The receipt replaced an earlier repository-side record of every shipped version. That record had to be regenerated after each asset change, and a test had to guard it. The project-side receipt needs neither of these. A refine pass with a second model lineage also made these changes:

- It removed the per-package `audit/` records. These records were in the Git-ignored `deliveries/` folder, they were never copied to release storage, and nothing read them.
- It merged the packaging helpers into one standard-library `draft.py`.
- It folded `draft-provenance` into `export`.
- It narrowed evidence to the code that computes each result. As a result, repairs and edits to unrelated results no longer mark findings stale.

One gap is known and accepted. A chart CSV that is reused across package revisions is attributed to the current evidence of its result. This is also true when the result was rerun after the file was written. To close the gap, it is necessary to record which run produced each exported file. If a revision reruns a result, it is better to re-export that result.

Release trusts `check-draft --verify-only` as its structural gate. `awb-package` runs every structural check before `check-draft` writes the manifest inventory. A passing verify proves that the draft is byte-identical to what was checked. For this reason, release does not read the package contract or the two narratives again to repeat that review. The items that can change after packaging are investigation-side: findings flagged after the draft was made, and the dispositions that they need. Release has its own review, which covers those items. Also, the `release` command itself runs the verify again before it copies.

## Design-session artifacts and generated workbenches

The CONTEXT.md in this design workspace is an artifact of the grill-with-docs session. It is not a mandatory artifact of an initialized analytics workbench. Do not include it in the proposed generated directory structure. The same distinction applies to these design notes: they give information to the skills, but they do not become default project scaffolding.

The domain-modeling skill itself introduces CONTEXT.md and ADR conventions. grill-with-docs is the wrapper that invokes it together with grilling. These software-engineering document conventions are not mandatory analytics deliverables or project records.

Investigation scoping is self-contained in `awb-init`. Follow the dependent decisions behind the business question. Ask one consequential decision question at a time, with a recommendation. Carry settled answers forward. Resolve facts directly from the environment.

Finish when scope and purpose decisions are settled or explicitly recorded as material unknowns. Routine implementation choices need no interview. This replaces the external `grilling` dependency and the competing instruction overrides that it needed.

The workflow instructions must include an analytics-specific adaptation of domain modeling:

- Challenge ambiguous terms.
- Test definitions against concrete examples.
- Check definitions against source data and analytical logic.
- Record resolved meanings immediately.

Shared vocabulary belongs in foundation/glossary.md. Local departures belong in investigation briefs. Analytical decisions belong in investigation histories. Dataset and view descriptions belong in the foundation catalog. These destinations replace the CONTEXT.md, CONTEXT-MAP.md, and ADR conventions of domain-modeling. Put the adapted guidance into the workflow, instead of an invocation of the unmodified domain-modeling skill or grill-with-docs wrapper. The installed skills were not modified.

## Glossary ownership

Generated workbenches include `foundation/glossary.md` for shared business and analytical vocabulary. Investigations inherit those definitions. Record investigation-specific meanings or deliberate departures in the `brief.md` of that investigation. Explain the difference there. Do not silently change the shared definition, and do not duplicate the full glossary.

Keep definitions separate from scope and configuration. Usually, a selected population or reporting period changes the settings of the investigation, not the meaning of shared terms. The glossary holds terminology. The foundation catalog describes datasets and views. This analytics glossary is different from the CONTEXT.md of the design session.

## Investigation records

When you create an investigation, record these items:

- The business question.
- The population or scope.
- The decision that the analysis will support.
- What will make the answer useful.

When the user says who will read the delivered documents, record it. If this is still missing, packaging asks for it. Accept an exploratory purpose and explicitly record unknowns. Do not make a predetermined decision or outcome mandatory. Use this brief to guide source relevance and preparation effort.

Keep a concise current-state summary separate from a chronological history of meaningful learnings and decisions. The current state supports the resumption of work. The history keeps analytical reasoning, caveats, superseded conclusions, and relevant data limitations or errors. Routine debugging, coding mistakes, and abandoned execution attempts that changed no understanding are excluded from the investigation history and from the methodology document of the package. A methodological mistake that changed a finding, or that explains why an earlier conclusion was wrong, is kept. The reason is that the account must explain how the conclusion was reached. Shared data preparation and quality knowledge stay part of the data foundation.

When a finding, decision, or next step changes, the agent maintains these records automatically. Explicit checkpoints are also available before a switch to a different investigation.

The findings table and the scan links behind quality rows are machine state that helpers must read back. For this reason, each is in a JSON file beside its Markdown record (`findings.json`, `foundation/quality.json`). They are not in table cells that are parsed by pattern. The findings table is rendered from its file, and a hand edit is refused as drift. The reason is that the promotion guards in `awb.py state finding` mean nothing if the table can be edited around them.

The quality record keeps every cell in Markdown, because people write coverage-gap rows and statuses by hand. Its file holds only links. The links are keyed by a hash, because scan issue keys can embed source values.

When a shared data correction can affect investigation findings, flag those findings and explain the reason. Do not automatically rerun the affected analysis or revise its conclusions. Releases stay frozen.

When work starts again, continue the last active investigation, unless the user indicates a switch. Briefly identify that investigation. If a request can fit multiple investigations, ask before you change their records.

## Open design questions

- When a change starts a new investigation, and when it expands an existing investigation instead.
- How cache freshness and expensive recomputation are managed.
