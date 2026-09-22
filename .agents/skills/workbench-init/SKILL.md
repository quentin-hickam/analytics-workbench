---
name: workbench-init
description: Initialize an analytics workbench or establish a new investigation within an existing one, preserving current project content and settled decisions.
---

# Initialize an analytics workbench

Build a project around one shared data foundation and zero or more investigations. Initialization establishes conventions and durable records; it does not prepare data broadly, implement an analytical framework, or create a delivery package.

## Resolve the target

1. Use the project root named by the user. Otherwise, use the current working directory only when it is clearly the intended data project.
2. Treat the repository containing this skill and `docs/workbench-spec.md` as the portable skill source. Never initialize that repository as a data project. If it is the current directory, obtain a separate target path before writing project files.
3. Inspect the target before changing it. Read its repository instructions, orientation, ignore rules, foundation records, and investigation records when present.
4. Merge conservatively. Existing files and project conventions are authoritative. Create missing artifacts, add clearly compatible missing sections when useful, and preserve all existing content. When an existing artifact conflicts with the workbench model, explain the conflict and ask for the project-specific decision instead of overwriting it.

A rerun is reconciliation, not a reset: do not recreate settled records, reopen answered questions, rename working paths, or replace customized templates.

Use the existing Git repository when the target is inside one. Otherwise, initialize a local Git repository if Git is available, without creating a commit or configuring a remote. If Git is unavailable, report that limitation rather than claiming code history is established.

## Decide how much to initialize

Initialization may stop after creating the project and shared foundation. Do not invent an investigation when the user has not supplied a business question.

For an existing workbench, read the active investigation before deciding whether to extend it or start another. An expansion of the same ask to a population containing the original group stays in that investigation; the same questions about an independent group start another. Inherit the current method and settings for a related investigation unless corrected, but start fresh findings and progress. Ask about genuinely ambiguous boundaries rather than applying these examples to every scope change.

When a business question is available and its consequential scope or purpose decisions remain unresolved, invoke the separately installed `grilling` skill directly through the host's skill discovery. This is an external dependency, not part of this bundle. If it is unavailable, report the missing dependency and pause the scoping interview; independent workspace setup may continue. Apply these workbench-specific interview rules while using it:

- Ask exactly one decision question at a time and include a recommended answer.
- Carry every settled answer forward. Ask only about unresolved choices that materially affect the analysis.
- Resolve facts from the repository, source systems, and available tools rather than asking the user to retrieve them.
- Establish the business question, population or scope, supported decision or exploratory purpose, usefulness criteria, and material unknowns. Unknowns may remain visible without blocking exploration.
- Finish the interview before creating the investigation records. Routine implementation choices do not require grilling.

Do not invoke `grill-with-docs` or `domain-modeling`. Instead, apply the vocabulary discipline below while interviewing and initializing: challenge ambiguous terms, test a proposed meaning with a concrete example, compare it with source data and analytical logic when available, and record the resolved meaning immediately. Shared meanings go in `foundation/glossary.md`; an investigation-specific departure goes in its `brief.md`; dataset and view descriptions go in `foundation/catalog.md`; consequential analytical decisions go in the investigation history. Do not create `CONTEXT.md`, `CONTEXT-MAP.md`, or ADRs.

## Create the project foundation

Adapt the asset files to the target; do not copy instructional comments or example rows as if they were project facts.

- For every new workbench, read and adapt the [project orientation](assets/workbench/README.md), [ignore rules](assets/workbench/.gitignore), and [project agent instructions](assets/workbench/AGENTS.md). Create each missing target file at the project root. Merge `.gitignore` rules individually when that file already exists. Use the installed user-level skills; no project-specific skill copies or vendor-specific instruction files are required by this workflow.
- For the shared foundation, use the [source register](assets/workbench/foundation/sources.md) when a source becomes a real candidate, the [catalog](assets/workbench/foundation/catalog.md) when a dataset, view, or deliberate cache exists, the [quality record](assets/workbench/foundation/quality.md) when a shared limitation, check, or correction is known, and the [glossary](assets/workbench/foundation/glossary.md) when shared vocabulary has been resolved. Read and adapt only the records whose conditions have fired. Retain an existing project's format when it serves the same responsibility; do not create empty ledgers merely to complete the directory tree.
- When an investigation has been established, read and adapt the [brief](assets/workbench/investigation/brief.md), [current state](assets/workbench/investigation/state.md), and [history](assets/workbench/investigation/history.md). Create missing records under `investigations/<stable-slug>/`, populate them only with settled facts, and update the `Active investigation` line in the project README to link to its state file. Preserve existing records when extending an investigation. Put unresolved questions in the brief and state rather than filling gaps by assumption.

Create executable code, configuration, `foundation/views/`, and data directories only when current work needs them. Use cohesive shared preparation and neutral analytical modules plus a thin investigation composition layer; do not scaffold a speculative framework.

The default batch storage path is always:

1. independently land completed source artifacts with acquisition provenance;
2. validate and publish derived Parquet without modifying the landed originals; then
3. load Git-managed canonical view definitions into each analytical process's own DuckDB session.

Land every acquired API response, SQL extract, or other source before canonical ingestion. Keep incomplete acquisitions and conversion outputs unpublished. Initial CSV or JSON may be a landed source format, but analytical steps do not exchange intermediate CSV files. A concrete project need may justify another backend; preserve independent landing and the preparation/EDA boundary.

Create `data/raw/` only for an acquisition, `data/parquet/` only for validated publication, and `data/cache/` only for a deliberate expensive result whose purpose is recorded in the catalog. Create `foundation/views/` when the first canonical definition exists. Let readers query stable published files while new outputs are prepared elsewhere and validated before publication.

Package templates and `deliveries/` remain absent during initialization. If the user explicitly asks for a package, complete initialization and then use the sibling [`workbench-package` skill](../workbench-package/SKILL.md); that skill owns `package-format/` and delivery creation.

## Complete initialization

Check that every created link is relative and every created record has a clear responsibility. Report:

- the target root;
- files created and existing files preserved or augmented;
- the active investigation, if one was created;
- unresolved decisions or file conflicts; and
- which lazy directories were intentionally deferred.

Do not create a Git commit unless the user explicitly requests one. Initialization is complete when the project conventions are usable, foundation records exist for the knowledge already established, any first investigation has populated brief/state/history records, and no package or unsolicited analysis has been produced. A project with `Active investigation: none` is a valid completed initialization.
