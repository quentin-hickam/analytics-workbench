# Analytics workbench skills

A portable, agent-agnostic workflow for shared data preparation, distinct investigations, and repeatable delivery packages. Git tracks analytical code; GitHub hosting is not required.

## Included artifacts

- [workbench-init](.agents/skills/workbench-init/SKILL.md): initialize a project and establish an investigation when its business question is available.
- [Project AGENTS.md template](.agents/skills/workbench-init/assets/workbench/AGENTS.md): govern everyday analysis and recordkeeping.
- [workbench-package](.agents/skills/workbench-package/SKILL.md): create, revise, or explicitly release a delivery package.

External dependency: `grilling` must already be installed and discoverable by the agent. It is not included or redistributed in this bundle. Workbench instructions invoke it directly, one question at a time, preserving settled answers.

## Use

In the target project's agent session, explicitly request:

> Use workbench-init to initialize this analytics project. The initial question is …

Continue analytical work normally using the generated AGENTS.md instructions. The default data flow is independent source landing, validated Parquet datasets, and DuckDB views loaded into separate analytical sessions. Data gathering never writes directly into the canonical database as its only retained representation.

When a package is needed:

> Use workbench-package to prepare a draft for the active investigation.

The skill asks which datasets to include. Subsequent requests revise the same draft. Explicitly marking it delivered preserves the next numbered release; drafting alone does not release it. Releases live under `deliveries/`, which the generated ignore rules exclude from Git, so each project records where released packages are kept. M365 receives the complete narrative, chosen exports, and assembly instructions for presentation work.

## Design and validation

The [specification](docs/workbench-spec.md) defines the workflow and acceptance scenarios. The [design notes](docs/workbench-design.md) preserve the decisions behind it. Backend exceptions and exact cache-retention mechanics remain project-specific choices.

Validation completed for the first draft:

- Skill frontmatter and relative asset links passed checks. Both skills are model-invocable so that `AGENTS.md` and `workbench-init` can reach `workbench-package`; its description and body require an explicit packaging request, and no vendor-specific frontmatter is used.
- An isolated agent initialized an empty project without a question or data, then reran initialization after a README customization. The customization survived and the second pass changed no files.
- Another isolated agent refreshed a synthetic existing package with a finding awaiting revalidation. It updated the same draft, retained the empty dataset selection, added caveats beside the finding in both narratives, and preserved the numbered release, source inputs, code, and investigation records unchanged.

These checks exercised the instructions with agents and local fixtures. No API acquisition, production data conversion, or M365 assembly was performed here.
