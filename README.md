# Analytics workbench skills

A portable, agent-agnostic workflow for shared data preparation, distinct investigations, and repeatable delivery packages. Git tracks analytical code; GitHub hosting is not required.

## Included skills

Every skill name carries the `awb-` prefix, so typing `awb-` in a host that lists skills as commands shows every workbench action.

- [awb-init](.agents/skills/awb-init/SKILL.md): initialize or repair a project, start an investigation, or resolve a consequential scope change. Its [project AGENTS.md template](.agents/skills/awb-init/assets/workbench/AGENTS.md) governs everyday analysis and recordkeeping.
- [awb-status](.agents/skills/awb-status/SKILL.md): read-only report of where the project stands and the requests that fit right now.
- [awb-package](.agents/skills/awb-package/SKILL.md): create or revise a delivery package's working draft.
- [awb-release](.agents/skills/awb-release/SKILL.md): preserve a numbered release when you mark a package delivered, and record and copy releases to the project's storage location.
- [awb-vault](.agents/skills/awb-vault/SKILL.md): create a knowledge vault or record data-estate knowledge in it. Its [vault conventions](.agents/skills/awb-vault/assets/vault/AGENTS.md) are the only file a new vault starts with.
- [awb-visualize](.agents/skills/awb-visualize/SKILL.md): principles, libraries, and style defaults for charts and tables that display inline in agent chat and survive pasting into a document.

## Requirements

- The `grilling` skill, from the `skills/productivity/grilling` folder of [mattpocock/skills](https://github.com/mattpocock/skills). The workbench was written against the copy in that repository's release v1.3.1, whose `grilling` folder is identical to commit `85f83d3` of 2026-08-20; later commits change its question format and have not been tested here. It is not included or redistributed in this bundle. It must be installed where the host's skill discovery finds it, normally the same user-level skills directory as the `awb-*` folders. Workbench instructions invoke it directly by name, one question at a time, preserving settled answers. Without it, `awb-init` reports the missing dependency and pauses the scoping interview; project setup continues.
- For figures made under `awb-visualize`, the analysis project's Python environment needs Python 3.10 or later, matplotlib, and seaborn 0.13. The shared style file was tested with matplotlib 3.10.0 and seaborn 0.13.2.

## Install

Download `analytics-workbench-skills-vX.Y.Z.zip` from the repository's GitHub releases and unzip it anywhere. It unpacks to one folder, `analytics-workbench-skills/`, holding the six `awb-*` skill folders beside this README, `LICENSE`, `CHANGELOG.md`, and `docs/`. Copy the six `awb-*` folders into your agent host's user-level skills directory, alongside `grilling`, replacing any earlier copies. Do not unzip the archive into the skills directory itself: a host looks for `<skills directory>/<skill name>/SKILL.md`, and the extra folder level hides the skills. In a clone of this repository, the same six folders are under `.agents/skills/`.

The skills serve every project from the user-level directory; projects need no local copies.

User-level skills directories:

- Claude Code: `~/.claude/skills/`. Claude Code does not discover skills in `~/.agents/skills/`. See [Claude Code skills](https://code.claude.com/docs/en/skills).
- OpenAI Codex: `~/.agents/skills/`. Codex also scans `.agents/skills/` in each directory from the working directory up to the repository root. See [Codex agent skills](https://developers.openai.com/codex/skills).
- Other hosts: each `awb-*` folder follows the agent skills convention of a folder holding a `SKILL.md` with `name` and `description` frontmatter. Check the host's documentation for its user-level skills directory.

### Project instructions in AGENTS.md

`awb-init` writes the workbench rules into the project's root `AGENTS.md`. Hosts differ in when they read it.

- Claude Code reads a project `AGENTS.md` starting with version 2.1.277, and by default only when no `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` exists in the working directory or any directory above it. When one does, Claude Code reads the `CLAUDE.md` files and skips `AGENTS.md`. Your own `~/.claude/CLAUDE.md` does not count for this check. See [How Claude remembers your project](https://code.claude.com/docs/en/memory#agents-md).
- So a workbench created inside a repository or folder that already has a `CLAUDE.md` loses the workbench rules in Claude Code without any warning from the host. `awb-init` reports such a file when it finds one but never edits it. To load the rules, add a line reading `@AGENTS.md` to that `CLAUDE.md`, which imports the file, or set Project instructions in `/config` to `claude-md-and-agents-md`, which reads both files. On Claude Code versions before 2.1.277, use the import.
- OpenAI Codex reads `AGENTS.md` from its home directory (`~/.codex` by default) and then from each directory from the Git root down to the working directory, preferring an `AGENTS.override.md` in the same directory. See [Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md).

## Use

In the target project's agent session, start from the business question:

> Use awb-init to initialize this analytics project. The question is …

If you ask without a question, `awb-init` asks for one; say there is no question yet to set up the project alone. Continue analytical work normally using the generated AGENTS.md instructions. The default data flow is independent source landing, validated Parquet datasets, and DuckDB views loaded into separate analytical sessions. Data gathering never writes directly into the canonical database as its only retained representation.

To see where things stand and what you can ask for next:

> Use awb-status — where are we?

When a package is needed:

> Use awb-package to prepare a draft for the active investigation.

The skill asks which datasets to include. Subsequent requests revise the same draft. Drafting never releases it. When it is ready:

> Use awb-release — mark the package delivered.

That preserves the next numbered release after any outstanding revalidation decisions. Releases live under `deliveries/`, which the generated ignore rules exclude from Git, so before the first release `awb-release` asks where released packages are kept, records it in the project README, and copies each release there when the location is reachable. M365 receives the complete narrative, chosen exports, and assembly instructions for presentation work.

Landed source data gets the same treatment. `data/raw/` is also excluded from Git, and a landed original often cannot be fetched again, so before the first acquisition is landed the agent asks where landed originals are kept outside the checkout, records it on the project README's `Landed data is kept at` line, and copies each completed landing there when the location is reachable. `awb-status` reports landed data that exists only in the checkout.

To carry knowledge about your data estate (systems, databases, schemas, and tables) from one project to the next, optionally create a knowledge vault outside every project:

> Use awb-vault to create a knowledge vault at …

Then set `WORKBENCH_VAULT` to that path, or add an equivalent line to your user-level agent instructions. Projects read the vault for the objects they touch and write to it only when you ask, for example "Use awb-vault to record what we learned about pay_detail". The vault holds knowledge about the data, never analytical conclusions, and projects work fully without it.

## Design and validation

The [specification](docs/workbench-spec.md) defines the workflow and acceptance scenarios. The [design notes](docs/workbench-design.md) preserve the decisions behind it. Backend exceptions and exact cache-retention mechanics remain project-specific choices.

Validation completed for the first draft, under the earlier `workbench-init` and `workbench-package` names and before the `awb-` repackaging; it has not been rerun against the current skills:

- Skill frontmatter and relative asset links passed checks. Both skills were model-invocable so that `AGENTS.md` and `workbench-init` could reach `workbench-package`; its description and body require an explicit packaging request, and no vendor-specific frontmatter is used.
- An isolated agent initialized an empty project without a question or data, then reran initialization after a README customization. The customization survived and the second pass changed no files.
- Another isolated agent refreshed a synthetic existing package with a finding awaiting revalidation. It updated the same draft, retained the empty dataset selection, added caveats beside the finding in both narratives, and preserved the numbered release, source inputs, code, and investigation records unchanged.

Validation completed for the knowledge vault, before vault creation moved from `workbench-init` to `awb-vault`:

- An isolated agent created a vault twice at a named path. The first run wrote only the conventions file; the second changed nothing.
- An isolated agent recorded estate knowledge on request (scenario 8): it kept the earlier pay_detail claim beside the new one, created the term_events and system pages with only supplied facts, linked the glossary entry, declined the attrition conclusion, and created no other pages.
- An isolated agent used a vault from two projects (scenarios 7 and 9): it read the system, database, and object pages for the objects in use and not a similarly named page in another schema, did not recommend a preference whose coverage missed contractors, recorded relied-on claims with `vault:` references, reported a contradiction without changing the vault, and continued without a vault when none was configured. The vault was byte-identical before and after.
- A conformance audit compared the package with the specification. Instruction gaps these checks found were corrected afterwards.

These checks exercised the instructions with agents and local fixtures. No API acquisition, production data conversion, or M365 assembly was performed here.

## Versioning

Releases are Git tags `vX.Y.Z`, each with a zip asset named `analytics-workbench-skills-vX.Y.Z.zip`. `scripts/build-dist.sh` builds the archive as `dist/analytics-workbench-skills.zip`; add the version when attaching it to the release. Changes are listed in [CHANGELOG.md](CHANGELOG.md).

## License

MIT. See [LICENSE](LICENSE).
