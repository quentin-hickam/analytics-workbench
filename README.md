# Analytics workbench skills

A portable, agent-agnostic workflow for shared data preparation, distinct investigations, and repeatable delivery packages. Git tracks analytical code; GitHub hosting is not required.

## Included skills

Every skill name carries the `awb-` prefix, so typing `awb-` in a host that lists skills as commands shows every workbench action.

- [awb-init](.agents/skills/awb-init/SKILL.md): initialize or repair a project, start an investigation, or resolve a consequential scope change. Its [project AGENTS.md template](.agents/skills/awb-init/assets/workbench/AGENTS.md) governs everyday analysis and recordkeeping.
- [awb-status](.agents/skills/awb-status/SKILL.md): read-only report of where the project stands and the requests that fit right now.
- [awb-package](.agents/skills/awb-package/SKILL.md): create or revise a delivery package's working draft.
- [awb-release](.agents/skills/awb-release/SKILL.md): preserve a numbered release when you mark a package delivered, and record and copy releases to the project's storage location.
- [awb-visualize](.agents/skills/awb-visualize/SKILL.md): principles, libraries, and style defaults for charts and tables that display inline in agent chat and survive pasting into a document.

## Requirements

- The `grilling` skill, from the `skills/productivity/grilling` folder of [mattpocock/skills](https://github.com/mattpocock/skills). The workbench was written against the copy in that repository's release v1.3.1, whose `grilling` folder is identical to commit `85f83d3` of 2026-08-20; later commits change its question format and have not been tested here. It is not included or redistributed in this bundle. It must be installed where the host's skill discovery finds it, normally the same user-level skills directory as the `awb-*` folders. Workbench instructions invoke it directly by name, one question at a time, preserving settled answers. Without it, `awb-init` reports the missing dependency and pauses the scoping interview; project setup continues.
- For figures made under `awb-visualize`, the analysis project's Python environment needs Python 3.10 or later, matplotlib, and seaborn 0.13. The shared style file was tested with matplotlib 3.10.0 and seaborn 0.13.2.
- For result validation under the project `AGENTS.md`, the analysis project's Python environment needs Python 3.10 or later and pandas. The shared validation file was tested with pandas 2.2.

## Install

Download `analytics-workbench-skills-vX.Y.Z.zip` from the repository's GitHub releases and unzip it anywhere. It unpacks to one folder, `analytics-workbench-skills/`, holding the five `awb-*` skill folders beside this README, `LICENSE`, `CHANGELOG.md`, and `docs/`. Copy the five `awb-*` folders into your agent host's user-level skills directory, alongside `grilling`, replacing any earlier copies. Do not unzip the archive into the skills directory itself: a host looks for `<skills directory>/<skill name>/SKILL.md`, and the extra folder level hides the skills. In a clone of this repository, the same five folders are under `.agents/skills/`.

The skills serve every project from the user-level directory; projects need no local copies.

User-level skills directories:

- Claude Code: `~/.claude/skills/`. Claude Code does not discover skills in `~/.agents/skills/`. See [Claude Code skills](https://code.claude.com/docs/en/skills).
- OpenAI Codex: `~/.agents/skills/`. Codex also scans `.agents/skills/` in each directory from the working directory up to the repository root. See [Codex agent skills](https://developers.openai.com/codex/skills).
- Other hosts: each `awb-*` folder follows the agent skills convention of a folder holding a `SKILL.md` with `name` and `description` frontmatter. Check the host's documentation for its user-level skills directory.

### Project instructions in AGENTS.md

`awb-init` writes the workbench rules into the project's root `AGENTS.md`. Hosts differ in when they read it.

- Claude Code reads a project `AGENTS.md` starting with version 2.1.277, and by default only when no `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` exists in the working directory or any directory above it. When one does, Claude Code reads the `CLAUDE.md` files and skips `AGENTS.md`. Your own `~/.claude/CLAUDE.md` does not count for this check. See [How Claude remembers your project](https://code.claude.com/docs/en/memory#agents-md).
- So a workbench created inside a repository or folder that already has a `CLAUDE.md` loses the workbench rules in Claude Code without any warning from the host. `awb-init` reports such a file when it finds one but never edits it. To load the rules, add an import line to that file giving the path from it to the project's `AGENTS.md`, since Claude Code resolves imports relative to the file that contains them: `@AGENTS.md` in a `CLAUDE.md` beside it, `@../AGENTS.md` in `.claude/CLAUDE.md`, and the relative path down into the project in an ancestor directory's `CLAUDE.md`, or set Project instructions in `/config` to `claude-md-and-agents-md`, which reads both files. See [import additional files](https://code.claude.com/docs/en/memory#import-additional-files). On Claude Code versions before 2.1.277, use the import.
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

## Design and validation

The [specification](docs/workbench-spec.md) defines the workflow and acceptance scenarios. The [design notes](docs/workbench-design.md) preserve the decisions behind it. Backend exceptions and exact cache-retention mechanics remain project-specific choices.

Validation of the current `awb-*` skills, run 2026-10-07 by four isolated agents on separate fixture projects with synthetic data. Each agent read the skills from this repository and followed them as written, playing both the analyst and the agent, so the scoping-interview transcripts are self-simulated and are weak evidence; every other check rests on files the agent produced. Every expected-behavior bullet of acceptance scenarios 1 through 6 passed; none failed. The runs exercised:

- `awb-init` on an empty directory with a business question: one question at a time with a recommended answer, Git initialized without a commit, foundation records created only where their conditions had fired, the host instruction-file check, and the landed-data location question before the first landing.
- Scenario 1 and 2: an expansion from 120 to 900 employees stayed in the same investigation, revised its settings and state, reused the preparation and neutral operations unchanged, and kept superseded findings in history; a pivot to an independent group started a new investigation that inherited method and settings, asked only about the decisions the pivot reopened, and used the earlier findings as method context only.
- Scenario 3: an email-alias correction was assessed locally, implemented through shared preparation and view definitions, documented in the quality record, and flagged two findings with reasons while leaving conclusions, the draft, and the numbered release byte-identical; a second release attempt stopped to ask for a disposition per affected conclusion.
- Scenario 4: one stable package with an asked-for dataset selection, release `001` only on the explicit milestone, a narrative-only revision to the same draft, release `002` after a flag raised since drafting was given a release-with-caveat disposition, manifests recording the producing commit separately from the packaging checkout, and each release copied to the recorded storage location and compared by file list and bytes.
- Scenario 5: a candidate source was assessed only far enough to reject it, the reason recorded, and nothing converted, cached, or exported for it.
- Scenario 6: paged API and extract acquisitions landed with provenance before conversion and copied to the recorded location; a failed partial acquisition stayed unpublished; a conversion failure was retried from landed files without reacquisition; two reader processes queried published Parquet through Git-managed views while a third process prepared a new publication, with no shared DuckDB file.
- `awb-status` after each run: the report shape, the landed-data and release storage lines, the `none chosen` risk path, and the request menu.

The runs also surfaced places where the instructions were silent or conflicted, including the order of verification and revalidation dispositions in `awb-release`, the manifest field names `awb-status` reads, the landing and publication layout, where acquisition and settings code lives, and how an expansion is scoped. Those were corrected in the skills afterwards; the corrected wording has not itself been rerun. No API acquisition, production data conversion, or M365 assembly was performed.

## Versioning

Releases are Git tags `vX.Y.Z`, each with a zip asset named `analytics-workbench-skills-vX.Y.Z.zip`. `scripts/build-dist.sh` builds the archive as `dist/analytics-workbench-skills.zip`; add the version when attaching it to the release. Changes are listed in [CHANGELOG.md](CHANGELOG.md).

## License

MIT. See [LICENSE](LICENSE).
