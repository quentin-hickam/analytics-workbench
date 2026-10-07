---
name: awb-init
description: Initialize or repair an analytics workbench, start a new investigation in an existing analytics workbench, or resolve a consequential scope change through the scoping interview.
---

# Initialize an analytics workbench

Build a project around one shared data foundation and zero or more investigations. Initialization establishes conventions and durable records; broad data preparation, an analytical framework, and delivery packages come later and only on request.

## Resolve the target

1. Use the project root named by the user. Otherwise, use the current working directory only when it is clearly the intended data project.
2. A directory holding skill sources, design records, or an unrelated codebase is not a data project. If the current directory is one, obtain a separate target path before writing project files.
3. Inspect the target before changing it. Read its repository instructions, orientation, ignore rules, foundation records, and investigation records when present.
4. Check whether the target directory or any directory above it holds a host-specific instruction file that the current host reads in preference to `AGENTS.md`. For example, Claude Code reads `CLAUDE.md` and skips `AGENTS.md` when a `CLAUDE.md` or `CLAUDE.local.md` is present. Such a file means the workbench rules in `AGENTS.md` may not be loaded. Never create, edit, or bridge that file; report it at completion.
5. Merge conservatively. Existing files and project conventions are authoritative. Create missing artifacts, add clearly compatible missing sections when useful, and preserve all existing content. When an existing artifact conflicts with the workbench model, explain the conflict and ask for the project-specific decision instead of overwriting it.

A rerun is reconciliation, not a reset: settled records, answered questions, working paths, and customized templates stay as they are.

Use the existing Git repository when the target is inside one. Otherwise, initialize a local Git repository if Git is available, without creating a commit or configuring a remote. If Git is unavailable, report that limitation rather than claiming code history is established.

## Decide how much to initialize

An investigation exists only when the user has supplied a business question. A new project starts from one: when the user asks to initialize a new project without supplying a question, ask for the business question before creating any project file. Set up the project and shared foundation without an investigation only when the user explicitly says there is no question yet. Repairing or reconciling an existing workbench needs no new question.

For an existing workbench, read the active investigation's brief before deciding whether to extend it or start another; read its findings only when the new investigation is related, as context for method selection. An expansion of the same ask to a population containing the original group stays in that investigation: revise its brief and ask only about the decisions the expansion reopens, such as purpose, usefulness, or new unknowns, carrying the settled ones forward. The same questions about an independent group start another. Inherit the current method, settings, and package format for a related investigation unless corrected, but start fresh findings and progress. Ask about genuinely ambiguous boundaries rather than applying these examples to every scope change.

## Run the scoping interview

When a business question is available and its consequential scope or purpose decisions remain unresolved, invoke the separately installed `grilling` skill through the host's skill discovery. When more than one `grilling` is discoverable, use the one installed in the same user-level skills directory as the `awb-*` skills. It is an external dependency, not part of this bundle. If it is unavailable, report the missing dependency and pause the scoping interview; independent workspace setup may continue.

`grilling` contributes the design-tree discipline: every decision branches into the decisions that hang off it, and facts come from the environment rather than the user. The rules below replace its round format, its sub-agent fact dispatch, its completion rule, and its confirmation before acting; where the two differ, these win:

- Ask exactly one decision question at a time and include a recommended answer.
- Carry every settled answer forward. Ask only about unresolved choices that materially affect the analysis; routine implementation choices need no question.
- Resolve facts directly from the repository, source systems, and available tools rather than asking the user to retrieve them or dispatching a sub-agent.
- Establish the business question, population or scope, supported decision or exploratory purpose, usefulness criteria, and material unknowns.
- The interview is complete when every consequential scope and purpose decision is either settled or explicitly recorded as a material unknown. Unknowns may remain visible without blocking exploration. Create the investigation records at that point under the workbench rules, without a separate confirmation round.

Apply this vocabulary discipline while interviewing and initializing: challenge ambiguous terms, test a proposed meaning with a concrete example, compare it with source data and analytical logic when available, and record the resolved meaning immediately. Shared meanings go in `foundation/glossary.md`; an investigation-specific departure goes in its `brief.md`; dataset and view descriptions go in `foundation/catalog.md`; consequential analytical decisions go in the investigation history. These records replace `CONTEXT.md`, `CONTEXT-MAP.md`, ADRs, `grill-with-docs`, and the unmodified `domain-modeling` skill.

## Create the project foundation

Adapt the asset files to the target; instructional comments and example rows are guidance, not project facts.

- For every new workbench, read and adapt the [project orientation](assets/workbench/README.md), [ignore rules](assets/workbench/.gitignore), and [project agent instructions](assets/workbench/AGENTS.md). Create each missing target file at the project root. Merge `.gitignore` rules individually when that file already exists. The installed user-level skills serve every project; project-specific skill copies and vendor-specific instruction files are unnecessary.
- For the shared foundation, use the [source register](assets/workbench/foundation/sources.md) when a source becomes a real candidate, the [catalog](assets/workbench/foundation/catalog.md) when a dataset, view, or deliberate cache exists, the [quality record](assets/workbench/foundation/quality.md) when a shared limitation, check, or correction is known, and the [glossary](assets/workbench/foundation/glossary.md) when shared vocabulary has been resolved. Read and adapt only the records whose conditions have fired. Retain an existing project's format when it serves the same responsibility; an empty ledger created to complete the directory tree is a defect.
- When an investigation has been established, read and adapt the [brief](assets/workbench/investigation/brief.md), [current state](assets/workbench/investigation/state.md), and [history](assets/workbench/investigation/history.md). Create missing records under `investigations/<stable-slug>/`, with a slug named for the question rather than the population so an expansion does not make it wrong, populate them only with settled facts, and point the `Active investigation` line in the project README at its state file. When extending an investigation, revise its brief, settings, and state to the settled scope, record superseded findings in its history, and otherwise preserve existing records. Put unresolved questions in the brief and state rather than filling gaps by assumption.

Create executable code, configuration, `foundation/views/`, and data directories only when current work needs them. Use cohesive shared preparation and neutral analytical modules plus a thin investigation composition layer; a speculative framework is out of scope.

The default batch storage path is always:

1. independently land completed source artifacts with acquisition provenance;
2. validate and publish derived Parquet without modifying the landed originals; then
3. load Git-managed canonical view definitions into each analytical process's own DuckDB session.

Land every acquired API response, SQL extract, or other source before canonical ingestion. Keep incomplete acquisitions and conversion outputs unpublished, following the landing and publication layout in the project `AGENTS.md`. Initial CSV or JSON may be a landed source format; analytical steps exchange results through views and the runtime rather than intermediate CSV files. A concrete project need may justify another backend; preserve independent landing and the preparation/EDA boundary.

Create `data/raw/` only for an acquisition, `data/parquet/` only for validated publication, and `data/cache/` only for a deliberate expensive result whose purpose is recorded in the catalog. Create `foundation/views/` when the first canonical definition exists. Let readers query stable published files while new outputs are prepared elsewhere and validated before publication.

Package templates and `deliveries/` remain absent during initialization. If the user explicitly asks for a package, complete initialization and then invoke the sibling [`awb-package` skill](../awb-package/SKILL.md); that skill owns `package-format/` and the package's working draft.

## Complete initialization

Check that every created link is relative and every created record has a clear responsibility. Report:

- the target root;
- files created and existing files preserved or augmented;
- unresolved decisions or file conflicts;
- any host-specific instruction file found that the host reads in preference to `AGENTS.md`, with a warning that the workbench rules may not be loaded and how that host imports or enables `AGENTS.md` (for Claude Code, an import line in the found file giving the path from that file to the project's `AGENTS.md`, such as `@AGENTS.md` beside it, `@../AGENTS.md` in `.claude/CLAUDE.md`, or the path down into the project from an ancestor's `CLAUDE.md`, because imports resolve relative to the file that contains them), leaving that change to the user;
- which lazy directories were intentionally deferred;
- how work continues: analysis proceeds through normal requests, and nothing is packaged until the user asks for a package, which `awb-package` creates; and
- the active investigation, or that none exists, followed by a suggestion to use `awb-status` to see where things stand and what can be asked for next.

Create a Git commit only when the user explicitly requests one. Initialization is complete when the project conventions are usable, foundation records exist for the knowledge already established, the investigation for the user's business question has populated brief/state/history records, and no package or unsolicited analysis has been produced. A project with `Active investigation: none` is a valid completed initialization only when the user explicitly said there is no question yet, or when a repair leaves an existing workbench without one.
