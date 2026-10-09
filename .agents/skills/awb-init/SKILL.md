---
name: awb-init
description: Initialize or repair an analytics workbench. Use when the user sets one up, brings a new business question, changes an investigation's scope, or asks to update the workbench to newer skills.
---

# Initialize an analytics workbench

Build a project around one shared data foundation and zero or more investigations. Initialization establishes conventions and durable records; data preparation, analysis, and packages follow on request.

## 1. Resolve the target

1. Use the project root the user names, otherwise the current directory when it is clearly the intended data project. A directory holding skill sources, design records, or an unrelated codebase is not one; obtain a separate target path before writing project files.
2. Inspect the target before changing it: its repository instructions, orientation, and ignore rules, then the investigation records step 2 names.
3. Check whether the target or any directory above it holds a host-specific instruction file the current host reads in preference to `AGENTS.md`; Claude Code reads `CLAUDE.md` and skips `AGENTS.md` when a `CLAUDE.md` or `CLAUDE.local.md` is present. Such a file means the workbench rules in `AGENTS.md` may not be loaded. Leave that file to the user; report it with the import line that loads `AGENTS.md` (for Claude Code, a path relative to the file holding it: `@AGENTS.md` beside it, `@../AGENTS.md` from `.claude/CLAUDE.md`).
4. Merge conservatively. Existing files and project conventions are authoritative: create missing artifacts, add clearly compatible missing sections, and preserve existing content. When an existing artifact conflicts with the workbench model, explain the conflict and ask for the project-specific decision.
5. Use the existing Git repository when the target is inside one. Otherwise initialize a local repository if Git is available, with no commit or remote; if Git is unavailable, report that code history is not established.

A rerun is reconciliation: settled records, answered questions, working paths, and customized templates stay as they are.

For a repair or an update to newer skills, follow [references/repair.md](references/repair.md), then report under step 5; otherwise continue below.

## 2. Decide how much to initialize

An investigation exists only when the user has supplied a business question. For a new project, ask for the question before creating any project file; set up the project and shared foundation without an investigation only when the user explicitly says there is no question yet. A repair needs no new question.

For an existing workbench, read the active investigation's brief before deciding whether to extend it or start another; read its findings only when the new investigation is related, as context for method. An expansion of the same ask to a population containing the original group stays in that investigation: revise its brief and ask only about the decisions the expansion reopens, such as purpose, usefulness, or new unknowns, carrying the settled ones forward. The same questions about an independent group start another. Inherit the current method, settings, and package format for a related investigation unless corrected, but start fresh findings and progress. Ask about genuinely ambiguous boundaries rather than applying these examples to every scope change.

## 3. Run the scoping interview

When a business question is available and scope or purpose decisions remain open:

- Follow the decision tree: settle the choices that constrain later choices before their dependent branches. Establish the business question, population or scope, supported decision or exploratory purpose, usefulness criteria, and material unknowns.
- Ask a decision only after those it depends on; ask independent decisions together, each with a recommended answer. Carry settled answers forward; ask only about choices that materially affect the analysis.
- Look facts up yourself in the repository, source systems, and tools; ask the user only for decisions.
- Record any reader the user describes in the brief's Audience section; `awb-package` asks for it when a package needs it.
- Challenge ambiguous terms, test a proposed meaning with a concrete example, and compare it with source data and analytical logic when available. Keep each resolved meaning and carry it into its record in step 4: shared meanings in `foundation/glossary.md`, an investigation's departure in its `brief.md`, dataset and view descriptions in `foundation/catalog.md`, consequential analytical decisions in its history. Record terms there instead of `CONTEXT.md` or ADRs.

The interview is done when the question, population, supported decision or exploratory purpose, usefulness criteria, and material unknowns are each settled or recorded as an unknown in the brief. Unknowns may stay open without blocking exploration. Create the investigation records without a separate confirmation round.

## 4. Create the project foundation

Adapt asset files to the target; their instructional comments and example rows are guidance, not project facts. The user-level skills serve every project, so the project holds only these files.

1. Adapt the [orientation](assets/workbench/README.md), [ignore rules](assets/workbench/.gitignore), and [agent instructions](assets/workbench/AGENTS.md) into missing root files; merge `.gitignore` rules one by one. A repair reconciles existing ones through references/repair.md.
2. When merging into an existing `AGENTS.md`, link both guides relatively and check the links resolve.
3. Install the project helpers and workbench guides and declare their packages, with the interpreter that will run the project's analysis, such as its virtual environment. Run it as a black box; `--check` reports without writing. A repair runs it from references/repair.md instead.

   ```sh
   python3 <skill-directory>/scripts/install_helpers.py <project-root>
   ```

   Carry into the report every `files` entry not `installed` or `current`, any `requirements` entry marked `missing`, and the `install` command it prints; the user adds or runs those.
4. Create shared foundation records as their conditions fire: the [source register](assets/workbench/foundation/sources.md) when a source becomes a real candidate, the [catalog](assets/workbench/foundation/catalog.md) when a dataset, view, or deliberate cache exists, the [quality record](assets/workbench/foundation/quality.md) when a shared limitation, check, or correction is known, and the [glossary](assets/workbench/foundation/glossary.md) when shared vocabulary is resolved. Keep an existing project's format when it serves the same responsibility; create each ledger only with content.
5. Investigation:
   - New: adapt the [brief](assets/workbench/investigation/brief.md), [state](assets/workbench/investigation/state.md), and [history](assets/workbench/investigation/history.md), and copy [run.py](assets/workbench/investigation/run.py) with its [settings.toml](assets/workbench/investigation/settings.toml), under `investigations/<stable-slug>/`, with a slug named for the question rather than the population so an expansion keeps it right. Populate them only with settled facts, put open questions in the brief and state, and point README's `Active investigation` line at the state file.
   - Extending: revise the brief, settings, and state to the settled scope; record superseded findings in the history.
6. Create `data/raw/`, `data/parquet/`, `data/cache/`, `foundation/views/`, and further code or configuration only when their first content exists.

Package templates and `deliveries/` stay absent. If the user explicitly asks for a package, finish initialization, then invoke the sibling [`awb-package` skill](../awb-package/SKILL.md).

## 5. Report

Report:

- the target root;
- files created, replaced, and existing files preserved or augmented;
- unresolved decisions, file conflicts, and files left for the user to decide;
- any host instruction file from step 1, with its import line;
- installer items needing attention;
- which lazy directories were deferred;
- how work continues: analysis through normal requests, a package only when the user asks `awb-package` for one; and
- the active investigation, or that none exists, followed by a suggestion to use `awb-status` to see where things stand and what to ask next.

Commit when the user asks; after a repair, suggest committing it as one commit so it can be reviewed and reverted as a unit. Initialization is complete when the project conventions are usable, foundation records exist for the knowledge already established, the investigation for the user's business question has populated brief, state, and history records, and the work has stopped short of packages and analysis the user has not requested.
