# Analytics workbench skills

A portable, agent-agnostic workflow for shared data preparation, distinct investigations, and repeatable delivery packages. Git tracks analytical code; GitHub hosting is not required.

## Included artifacts

- [workbench-init](.agents/skills/workbench-init/SKILL.md): initialize a project and establish an investigation when its business question is available.
- [Project AGENTS.md template](.agents/skills/workbench-init/assets/workbench/AGENTS.md): govern everyday analysis and recordkeeping.
- [workbench-package](.agents/skills/workbench-package/SKILL.md): create, revise, or explicitly release a delivery package.
- [Knowledge vault conventions](.agents/skills/workbench-init/assets/vault/AGENTS.md): the only file a new knowledge vault starts with.

External dependency: `grilling` must already be installed and discoverable by the agent. It is not included or redistributed in this bundle. Workbench instructions invoke it directly, one question at a time, preserving settled answers.

## Use

In the target project's agent session, explicitly request:

> Use workbench-init to initialize this analytics project. The initial question is …

Continue analytical work normally using the generated AGENTS.md instructions. The default data flow is independent source landing, validated Parquet datasets, and DuckDB views loaded into separate analytical sessions. Data gathering never writes directly into the canonical database as its only retained representation.

When a package is needed:

> Use workbench-package to prepare a draft for the active investigation.

The skill asks which datasets to include. Subsequent requests revise the same draft. Explicitly marking it delivered preserves the next numbered release; drafting alone does not release it. Releases live under `deliveries/`, which the generated ignore rules exclude from Git, so each project records where released packages are kept. M365 receives the complete narrative, chosen exports, and assembly instructions for presentation work.

To carry knowledge about your data estate (systems, databases, schemas, and tables) from one project to the next, optionally create a knowledge vault outside every project:

> Use workbench-init to create a knowledge vault at …

Then set `WORKBENCH_VAULT` to that path, or add an equivalent line to your user-level agent instructions. Projects read the vault for the objects they touch and write to it only when you ask, for example "record what we learned about pay_detail in the vault". The vault holds knowledge about the data, never analytical conclusions, and projects work fully without it.

## Design and validation

The [specification](docs/workbench-spec.md) defines the workflow and acceptance scenarios. The [design notes](docs/workbench-design.md) preserve the decisions behind it. Backend exceptions and exact cache-retention mechanics remain project-specific choices.

Validation completed for the first draft:

- Skill frontmatter and relative asset links passed checks. Both skills are model-invocable so that `AGENTS.md` and `workbench-init` can reach `workbench-package`; its description and body require an explicit packaging request, and no vendor-specific frontmatter is used.
- An isolated agent initialized an empty project without a question or data, then reran initialization after a README customization. The customization survived and the second pass changed no files.
- Another isolated agent refreshed a synthetic existing package with a finding awaiting revalidation. It updated the same draft, retained the empty dataset selection, added caveats beside the finding in both narratives, and preserved the numbered release, source inputs, code, and investigation records unchanged.

Validation completed for the knowledge vault:

- An isolated agent created a vault twice at a named path. The first run wrote only the conventions file; the second changed nothing.
- An isolated agent recorded estate knowledge on request (scenario 8): it kept the earlier pay_detail claim beside the new one, created the term_events and system pages with only supplied facts, linked the glossary entry, declined the attrition conclusion, and created no other pages.
- An isolated agent used a vault from two projects (scenarios 7 and 9): it read the system, database, and object pages for the objects in use and not a similarly named page in another schema, did not recommend a preference whose coverage missed contractors, recorded relied-on claims with `vault:` references, reported a contradiction without changing the vault, and continued without a vault when none was configured. The vault was byte-identical before and after.
- A conformance audit compared the package with the specification. Instruction gaps these checks found were corrected afterwards.

These checks exercised the instructions with agents and local fixtures. No API acquisition, production data conversion, or M365 assembly was performed here.
