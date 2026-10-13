---
name: awb-init
description: Initialize or repair an analytics workbench. Use when the user sets one up, brings a new business question, changes an investigation's scope, or asks to update the workbench to newer skills.
---

# Initialize an analytics workbench

Build a project around one shared data foundation and zero or more investigations. Initialization sets up the conventions and the durable records. Data preparation, analysis, and packages come later, on request.

## 1. Resolve the target

1. Use the project root that the user names. If the user names no project root, use the current directory when it is clearly the intended data project. A directory that holds skill sources, design records, or an unrelated codebase is not a data project. In that case, get a separate target path before you write project files.
2. Before you change the target, examine its repository instructions, orientation, and ignore rules. Then examine the investigation records that step 2 names.
3. Find out if the target or a directory above it holds a host-specific instruction file that the current host reads instead of `AGENTS.md`. When a `CLAUDE.md` or `CLAUDE.local.md` is present, Claude Code reads `CLAUDE.md` and does not read `AGENTS.md`. If such a file exists, it is possible that the host does not load the workbench rules in `AGENTS.md`. Leave that file to the user. Report the file with the import line that loads `AGENTS.md`. For Claude Code, the import line is a path relative to the file that holds it. It is `@AGENTS.md` from a file beside `AGENTS.md`, and `@../AGENTS.md` from `.claude/CLAUDE.md`.
4. Merge conservatively. Existing files and project conventions are the authority:
   - Create missing artifacts.
   - Add missing sections that are clearly compatible.
   - Keep existing content.

   When an existing artifact conflicts with the workbench model, explain the conflict. Then ask for the project-specific decision.
5. If the target is inside a Git repository, use that repository. If not, and Git is available, initialize a local repository with no commit and no remote. If Git is not available, report that the code history is not set up.

A rerun is a reconciliation: settled records, answered questions, working paths, and customized templates stay as they are.

For a repair or an update to newer skills, follow [references/repair.md](references/repair.md). Then report as step 5 tells you. For all other work, continue below.

## 2. Decide how much to initialize

An investigation exists only when the user gave a business question. For a new project, ask for the question before you create any project file. Set up the project and the shared foundation without an investigation only when the user explicitly says that there is no question yet. A repair does not need a new question.

For an existing workbench, read the brief of the active investigation before you decide to extend it or start another investigation. Read its findings only when the new investigation is related, as context for the method.

If the same ask expands to a population that contains the original group, the expansion stays in that investigation. Revise its brief. Ask only about the decisions that the expansion opens again, for example purpose, usefulness, or new unknowns. Carry the settled decisions forward. The same questions about an independent group start another investigation.

For a related investigation, inherit the current method, settings, and package format, unless they are corrected. But start with new findings and new progress. Ask about boundaries that are genuinely ambiguous, and do not apply these examples to every scope change.

## 3. Run the scoping interview

When a business question is available and scope or purpose decisions are still open:

- Follow the decision tree: settle the choices that limit later choices before the branches that depend on them. Establish these items: the business question, the population or scope, the supported decision or exploratory purpose, the usefulness criteria, and the material unknowns.
- Ask for a decision only after the decisions that it depends on. Ask for independent decisions together, and give a recommended answer for each. Carry settled answers forward. Ask only about choices that have a material effect on the analysis.
- Find facts yourself in the repository, the source systems, and the tools. Ask the user only for decisions.
- If the user describes a reader, record that reader in the Audience section of the brief. `awb-package` asks for it when a package needs it.
- Challenge ambiguous terms. Test a proposed meaning with a concrete example. When source data and analytical logic are available, compare the meaning with them. Keep each resolved meaning, and in step 4 put it into its record:
  - Shared meanings go in `foundation/glossary.md`.
  - The departure of an investigation goes in its `brief.md`.
  - Dataset and view descriptions go in `foundation/catalog.md`.
  - Consequential analytical decisions go in the history of the investigation.

  Record terms in these records, not in `CONTEXT.md` or ADRs.

The interview is complete when each of these items is settled, or is recorded in the brief as an unknown:

- The question.
- The population.
- The supported decision or exploratory purpose.
- The usefulness criteria.
- The material unknowns.

Unknowns can stay open, and they do not block exploration. Create the investigation records without a separate confirmation round.

## 4. Create the project foundation

Adapt the asset files to the target. Their instructional comments and example rows are guidance, not project facts. The user-level skills serve every project, so the project holds only these files.

1. Adapt the [orientation](assets/workbench/README.md), [ignore rules](assets/workbench/.gitignore), and [agent instructions](assets/workbench/AGENTS.md) into the root files that are missing. Merge `.gitignore` rules one at a time. A repair reconciles existing root files through references/repair.md.
2. When you merge into an existing `AGENTS.md`, use relative links to the two guides. Check that the links resolve.
3. Install the project helpers and the workbench guides, and declare their packages. Use the interpreter that will run the analysis of the project, for example its virtual environment. Run the installer as a black box. With `--check`, it reports and does not write. A repair runs the installer from references/repair.md instead.

   ```sh
   python3 <skill-directory>/scripts/install_helpers.py <project-root>
   ```

   Put these items into the report:
   - Each `files` entry that is not `installed` or `current`.
   - Each `requirements` entry that is marked `missing`.
   - The `install` command that the installer prints.

   The user adds or runs these items.
4. Create each shared foundation record when its condition occurs:
   - The [source register](assets/workbench/foundation/sources.md): when a source becomes a real candidate.
   - The [catalog](assets/workbench/foundation/catalog.md): when a dataset, view, or deliberate cache exists.
   - The [quality record](assets/workbench/foundation/quality.md): when a shared limitation, check, or correction is known.
   - The [glossary](assets/workbench/foundation/glossary.md): when shared vocabulary is resolved.

   If the format of an existing project serves the same responsibility, keep that format. Create each ledger only when it has content.
5. Investigation:
   - New: Adapt the [brief](assets/workbench/investigation/brief.md), [state](assets/workbench/investigation/state.md), and [history](assets/workbench/investigation/history.md), and copy [run.py](assets/workbench/investigation/run.py) with its [settings.toml](assets/workbench/investigation/settings.toml). Put them under `investigations/<stable-slug>/`. Name the slug for the question, not for the population, so that the slug stays correct after an expansion. Put only settled facts in them. Put open questions in the brief and the state. Point the `Active investigation` line of README at the state file.
   - Extending: Revise the brief, the settings, and the state to agree with the settled scope. Record superseded findings in the history.
6. Create `data/raw/`, `data/parquet/`, `data/cache/`, `foundation/views/`, and other code or configuration only when their first content exists.

Package templates and `deliveries/` stay absent. If the user explicitly asks for a package, finish initialization. Then invoke the sibling [`awb-package` skill](../awb-package/SKILL.md).

## 5. Report

Report these items:

- The target root.
- The files that you created or replaced, and the existing files that you kept or added to.
- Unresolved decisions, file conflicts, and files that you left for the user to decide.
- Each host instruction file from step 1, with its import line.
- Installer items that need attention.
- The lazy directories that you deferred.
- How work continues: analysis comes through normal requests, and a package comes only when the user asks `awb-package` for one.
- The active investigation, or a statement that none exists. After it, suggest `awb-status` to see where things stand and what to ask next.

Commit when the user asks. After a repair, suggest one commit for the repair, so that it can be reviewed and reverted as a unit.

Initialization is complete when all these conditions are true:

- The project conventions are usable.
- Foundation records exist for the knowledge that is already established.
- The investigation for the business question of the user has populated brief, state, and history records.
- The work stopped before packages and analysis that the user did not request.
