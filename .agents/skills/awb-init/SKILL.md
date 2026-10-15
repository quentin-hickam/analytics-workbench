---
name: awb-init
description: "Set up or repair an analytics workbench. Use for \"set up a workbench\", \"repair this workbench\", or \"update it to the newer skills\"; hand the business question to awb-scope."
---

# Initialize an analytics workbench

Build a project around one shared data foundation and zero or more investigations. Initialization establishes conventions and durable records, then hands the business question to `awb-scope`, which creates the investigation; data preparation, analysis, and packages follow on request.

## 1. Resolve the target

1. Use the project root the user names, otherwise the current directory when it is clearly the intended data project. A directory holding skill sources, design records, or an unrelated codebase is not one; obtain a separate target path before writing project files.
2. Inspect the target before changing it: its repository instructions, orientation, and ignore rules, and the README's active investigation.
3. Check whether the target or any directory above it holds a host-specific instruction file the current host reads in preference to `AGENTS.md`; Claude Code reads `CLAUDE.md` and skips `AGENTS.md` when a `CLAUDE.md` or `CLAUDE.local.md` is present. Such a file means the workbench rules in `AGENTS.md` may not be loaded. Leave that file to the user; report it with the import line that loads `AGENTS.md` (for Claude Code, a path relative to the file holding it: `@AGENTS.md` beside it, `@../AGENTS.md` from `.claude/CLAUDE.md`).
4. Merge conservatively. Existing files and project conventions are authoritative: create missing artifacts, add clearly compatible missing sections, and preserve existing content. When an existing artifact conflicts with the workbench model, explain the conflict and ask for the project-specific decision.
5. Use the existing Git repository when the target is inside one. Otherwise initialize a local repository if Git is available, with no commit or remote; if Git is unavailable, report that code history is not established.

A rerun is reconciliation: settled records, answered questions, working paths, and customized templates stay as they are.

For a repair or an update to newer skills, follow [references/repair.md](references/repair.md), then report under step 5; otherwise continue below.

## 2. Get the business question

A new project starts from a business question. Ask for it in one line before creating any project file, unless the user gave it; set up the project without an investigation only when the user explicitly says there is no question yet. Do not interview here: step 4 hands the question to `awb-scope`. In an existing workbench, a new question or a change of scope belongs to `awb-scope`, not this skill.

## 3. Create the project foundation

Adapt asset files to the target; their instructional comments and example rows are guidance, not project facts. The user-level skills serve every project, so the project holds only these files.

1. Adapt the [orientation](assets/workbench/README.md), [ignore rules](assets/workbench/.gitignore), and [agent instructions](assets/workbench/AGENTS.md) into missing root files; merge `.gitignore` rules one by one, each negation after every rule it overrides. A repair reconciles existing ones through references/repair.md.
2. When merging into an existing `AGENTS.md`, link both guides relatively and check the links resolve.
3. Install the project helpers, workbench guides, and the `foundation/references/` folder, and declare the helpers' packages, with the interpreter that will run the project's analysis, such as its virtual environment. When the host offers the workbench MCP server, use its `setup` tool for this installation. Run the installer as a black box; `--check` reports without writing. A repair runs it from references/repair.md instead.

   ```sh
   python3 <skill-directory>/scripts/install_helpers.py <project-root>
   ```

   Carry into the report every `files` entry not `installed` or `current`, any `requirements` entry marked `missing` or `unread` (a line the helpers could not read, which may declare a missing package), and the `install` command it prints; the user adds or runs those.
4. Create shared foundation records as their conditions fire: the [source register](assets/workbench/foundation/sources.md) when a source becomes a real candidate, the [catalog](assets/workbench/foundation/catalog.md) when a dataset, view, or deliberate cache exists, the [quality record](assets/workbench/foundation/quality.md) when a shared limitation, check, or correction is known, the [dataset checks](assets/workbench/foundation/datasets.toml) when a dataset's publication checks are declared, and the [glossary](assets/workbench/foundation/glossary.md) when shared vocabulary is resolved. `foundation/review-rules.md` has no template: `python3 src/awb.py review-rules add` creates it with the first rule. Keep an existing project's format when it serves the same responsibility; create each ledger only with content.
5. Create `data/raw/`, `data/parquet/`, `data/cache/`, `foundation/views/`, `.env.example` (credential variable names, under the data guide's rule), and further code or configuration only when their first content exists; the installer creates `foundation/references/`.

Package templates and `deliveries/` stay absent. If the user explicitly asks for a package, finish initialization, then invoke the sibling [`awb-package` skill](../awb-package/SKILL.md).

## 4. Hand off the question

With the foundation in place, invoke the sibling [`awb-scope` skill](../awb-scope/SKILL.md) with the user's question. It interviews the user, creates the investigation's brief, state, history, run script, settings, and question ledger, and points the README's Active investigation line at it. Without a question, leave that line at `none`.

## 5. Report

Report:

- the target root;
- files created, replaced, and existing files preserved or augmented;
- unresolved decisions, file conflicts, and files left for the user to decide;
- any host instruction file from step 1, with its import line;
- installer items needing attention;
- if the host's MCP status has no `awb` registration, offer the printed entry and its destination together in one line: run `python3 <skill-directory>/scripts/install_helpers.py --mcp-config <host>` (`copilot`, `claude`, or `codex`) with a stable Python 3.10+ interpreter outside a project virtual environment. Report any interpreter warning; the entry still prints. Leave merging user configuration to the user. If registered but unavailable, report the host's diagnostic instead;
- which lazy directories were deferred;
- how work continues: a new question or scope change through `awb-scope`, analysis through normal requests, a package only when the user asks `awb-package` for one; and
- the active investigation from `awb-scope`'s report, or that none exists, followed by a suggestion to use `awb-status` to see where things stand and what to ask next.

Commit when the user asks; after a repair, suggest committing it as one commit so it can be reviewed and reverted as a unit. Initialization is complete when the project conventions are usable, foundation records exist for the knowledge already established, the user's business question has gone to `awb-scope`, and the work has stopped short of packages and analysis the user has not requested.
