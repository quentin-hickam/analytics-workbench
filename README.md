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

External dependency: `grilling` must already be installed and discoverable by the agent. It is not included or redistributed in this bundle. Workbench instructions invoke it directly, one question at a time, preserving settled answers.

## Install

Copy the six `awb-*` folders from `.agents/skills/` into your agent host's user-level skills directory, alongside `grilling`. The skills serve every project from there; projects need no local copies. Projects initialized with the earlier `workbench-init` and `workbench-package` names are migrated the next time `awb-init` reconciles them.

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
