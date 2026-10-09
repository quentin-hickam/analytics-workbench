# Analytics workbench skills

A portable, agent-agnostic workflow for shared data preparation, distinct investigations, and repeatable delivery packages. Git tracks analytical code; GitHub hosting is not required.

## Included skills

Every skill name carries the `awb-` prefix, so typing `awb-` in a host that lists skills as commands shows every workbench action.

- [awb-init](.agents/skills/awb-init/SKILL.md): initialize a project, repair it or bring it up to date after installing newer skills, start an investigation, or resolve a consequential scope change. Its [project AGENTS.md template](.agents/skills/awb-init/assets/workbench/AGENTS.md) governs everyday analysis and recordkeeping.
- [awb-clean](.agents/skills/awb-clean/SKILL.md): clean one dataset at the shared foundation level: scan it for candidate issues in one call, decide with you where meaning changes, correct them through canonical views, and record the quality rows and catalog cells and flag affected findings in one call.
- [awb-eda](.agents/skills/awb-eda/SKILL.md): explore one dataset for the active investigation with one scan within its scope and settings, follow up with saved queries, and record what was learned; shared data problems go to `awb-clean`, and exploration records no findings.
- [awb-status](.agents/skills/awb-status/SKILL.md): read-only report of where the project stands and the requests that fit right now.
- [awb-package](.agents/skills/awb-package/SKILL.md): create or revise a delivery package's working draft.
- [awb-release](.agents/skills/awb-release/SKILL.md): preserve a frozen, numbered release when you mark a package delivered, and copy releases to the project's recorded storage location.

## Requirements

- For package chart files, the chart helper that `awb-package` ships needs Python 3.10 or later and pandas.
- The project helpers need Python 3.10 or later (3.11 or later, or `tomli`, for TOML settings). `awb-init`'s installer declares and checks their packages: pandas for validation and charts, and `duckdb` for sessions, queries, and publication. `land()`, `publish()`, and `retain()` themselves use only the standard library.
- For result validation under the project `AGENTS.md`, the analysis project's Python environment needs Python 3.10 or later and pandas. The shared validation file was tested with pandas 2.2.
- The `awb-clean` and `awb-eda` scans need Python 3.10 or later and the `duckdb` package in the project's interpreter (TOML settings need 3.11 or later, or `tomli`); the `awb-clean` record script needs only the standard library.
- The read-only status collector needs Python 3.10 or later and the standard library; unsupported project record formats use targeted manual reads.
<!-- dist:exclude -->
- pytest is needed only to run this repository's own tests under `tests/`; they exercise the shipped helper files and are not part of the distributed archive.
<!-- /dist:exclude -->

## Install

Download `analytics-workbench-skills-vX.Y.Z.zip` from the repository's GitHub releases and unzip it anywhere. It unpacks to one folder, `analytics-workbench-skills/`, holding the six `awb-*` skill folders beside this README, `LICENSE`, and `CHANGELOG.md`. Copy the six `awb-*` folders into your agent host's user-level skills directory, replacing any earlier copies, and delete an `awb-update` folder left by an earlier release: its job now belongs to `awb-init`. Do not unzip the archive into the skills directory itself: a host looks for `<skills directory>/<skill name>/SKILL.md`, and the extra folder level hides the skills. In a clone of this repository, the same six folders are under `.agents/skills/`.

The skills serve every project from the user-level directory; projects need no local copies.

User-level skills directories:

- Claude Code: `~/.claude/skills/`. Claude Code does not discover skills in `~/.agents/skills/`. See [Claude Code skills](https://code.claude.com/docs/en/skills).
- OpenAI Codex: `~/.agents/skills/`. Codex also scans `.agents/skills/` in each directory from the working directory up to the repository root. See [Codex agent skills](https://developers.openai.com/codex/skills).
- Other hosts: each `awb-*` folder follows the agent skills convention of a folder holding a `SKILL.md` with `name` and `description` frontmatter. Check the host's documentation for its user-level skills directory.

### Project instructions in AGENTS.md

`awb-init` writes a compact project `AGENTS.md` and copies the conditional procedures into `workbench-guides/`. Keep those guides with the project; the root instructions say when to read each. Scoping is self-contained and requires no external interview skill. Hosts differ in when they read `AGENTS.md`.

- Claude Code reads a project `AGENTS.md` starting with version 2.1.277, and by default only when no `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` exists in the working directory or any directory above it. When one does, Claude Code reads the `CLAUDE.md` files and skips `AGENTS.md`. Your own `~/.claude/CLAUDE.md` does not count for this check. See [How Claude remembers your project](https://code.claude.com/docs/en/memory#agents-md).
- So a workbench created inside a repository or folder that already has a `CLAUDE.md` loses the workbench rules in Claude Code without any warning from the host. `awb-init` reports such a file when it finds one but never edits it. To load the rules, add an import line to that file giving the path from it to the project's `AGENTS.md`, since Claude Code resolves imports relative to the file that contains them: `@AGENTS.md` in a `CLAUDE.md` beside it, `@../AGENTS.md` in `.claude/CLAUDE.md`, and the relative path down into the project in an ancestor directory's `CLAUDE.md`, or set Project instructions in `/config` to `claude-md-and-agents-md`, which reads both files. See [import additional files](https://code.claude.com/docs/en/memory#import-additional-files). On Claude Code versions before 2.1.277, use the import.
- OpenAI Codex reads `AGENTS.md` from its home directory (`~/.codex` by default) and then from each directory from the Git root down to the working directory, preferring an `AGENTS.override.md` in the same directory. See [Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md).

## Use

In the target project's agent session, start from the business question:

> Use awb-init to initialize this analytics project. The question is …

If you ask without a question, `awb-init` asks for one; say there is no question yet to set up the project alone. Continue analytical work normally using the generated AGENTS.md instructions. The default data flow is independent source landing, validated Parquet datasets, and DuckDB views loaded into separate analytical sessions. Data gathering never writes directly into the canonical database as its only retained representation.

`awb-init` installs the project helpers under `src/` with its installer, `scripts/install_helpers.py`, and writes a `requirements.txt` when the project declares no dependencies; the installer's `--upgrade` brings earlier shipped copies up to date. Mechanical work then runs as single commands whose output the agent reports verbatim, and computation runs as saved queries rather than scratch scripts: `python3 src/awb.py --help` lists the commands (`sql`, `profile`, `land`, `retain`, `publish`, `stale`, `check-draft`, `draft-provenance`, `export`, `release`, `copy-releases`). Each investigation's run script, `run.py`, produces, validates, and records its results in one run and prints the `state.md` rows to paste.

To see where things stand and what you can ask for next:

> Use awb-status — where are we?

When a package is needed:

> Use awb-package to prepare a draft for the active investigation.

The skill asks which datasets to include. Subsequent requests revise the same draft. Drafting never releases it. When it is ready:

> Use awb-release — mark the package delivered.

That preserves the next numbered release, frozen from then on, once you have chosen a disposition for each flagged finding the draft represents. Releases live under `deliveries/`, which the generated ignore rules exclude from Git, so before the first release `awb-release` asks where released packages are kept, records it in the project README, and copies each release there when the location is reachable; `python3 src/awb.py copy-releases` copies existing releases when the location is recorded or changed later. M365 receives the audience-facing findings, written as a slide-by-slide deck outline, an internal methodology reference, one data file per chart, chosen exports, and assembly instructions. In the Microsoft 365 Copilot app, the PowerPoint agent builds the deck from the outline, draws each chart as a native chart from its data file under the assembly's chart rules, and asks you when something is unclear. Checking the storyline means reading the outline's headings before anything is built.

Landed source data gets the same treatment. `data/raw/` is also excluded from Git, and a landed original often cannot be fetched again, so before the first acquisition is landed the agent asks where landed originals are kept outside the checkout, records it on the project README's `Landed data is kept at` line, and copies each completed landing there when the location is reachable. `awb-status` reports landed data that exists only in the checkout.

After installing a newer release of the skills, bring each existing workbench up to date with `awb-init`'s repair:

> Use awb-init to repair this workbench.

Repair runs the helper installer with `--upgrade`. It replaces only unmodified copies of earlier shipped helpers, package formats, and workbench guides, which it recognizes from the record of every version the skills have shipped; it reports customized copies for you to decide and removes retired files only when you ask. The agent then reconciles the project's adapted `AGENTS.md` and `README.md` against the current templates.

<!-- dist:exclude -->
## Design and validation

The [specification](docs/workbench-spec.md) defines the workflow and acceptance scenarios. The [design notes](docs/workbench-design.md) preserve the decisions behind it. Backend exceptions and exact cache-retention mechanics remain project-specific choices.

Historical validation of the `awb-*` skills, run 2026-10-07 by four isolated agents on separate fixture projects with synthetic data. Each agent read the skills from this repository and followed them as written, playing both the analyst and the agent, so the scoping-interview transcripts are self-simulated and are weak evidence; every other check rests on files the agent produced. Every expected-behavior bullet of acceptance scenarios 1 through 6 passed; none failed. The runs exercised:

- `awb-init` on an empty directory with a business question: one question at a time with a recommended answer, Git initialized without a commit, foundation records created only where their conditions had fired, the host instruction-file check, and the landed-data location question before the first landing.
- Scenario 1 and 2: an expansion from 120 to 900 employees stayed in the same investigation, revised its settings and state, reused the preparation and neutral operations unchanged, and kept superseded findings in history; a pivot to an independent group started a new investigation that inherited method and settings, asked only about the decisions the pivot reopened, and used the earlier findings as method context only.
- Scenario 3: an email-alias correction was assessed locally, implemented through shared preparation and view definitions, documented in the quality record, and flagged two findings with reasons while leaving conclusions, the draft, and the numbered release byte-identical; a second release attempt stopped to ask for a disposition per affected conclusion.
- Scenario 4: one stable package with an asked-for dataset selection, release `001` only on the explicit milestone, a narrative-only revision to the same draft, release `002` after a flag raised since drafting was given a release-with-caveat disposition, manifests recording the producing commit separately from the packaging checkout, and each release copied to the recorded storage location and compared by file list and bytes.
- Scenario 5: a candidate source was assessed only far enough to reject it, the reason recorded, and nothing converted, cached, or exported for it.
- Scenario 6: paged API and extract acquisitions landed with provenance before conversion and copied to the recorded location; a failed partial acquisition stayed unpublished; a conversion failure was retried from landed files without reacquisition; two reader processes queried published Parquet through Git-managed views while a third process prepared a new publication, with no shared DuckDB file.
- `awb-status` after each run: the report shape, the landed-data and release storage lines, the `none chosen` risk path, and the request menu.

The runs also surfaced places where the instructions were silent or conflicted, including the order of verification and revalidation dispositions in `awb-release`, the manifest field names `awb-status` reads, the landing and publication layout, where acquisition and settings code lives, and how an expansion is scoped. Those were corrected in the skills afterwards; the corrected wording has not itself been rerun. No API acquisition, production data conversion, or M365 assembly was performed. The runs used the earlier package format, a `journal.md` and an `executive-summary.md` written in the workbench, with captions drawn into figure images; the `findings.md` and `methodology.md` format that replaced it, the findings check, the slide-outline format, and the chart files were not exercised in those historical runs. Current helper and recipe checks are recorded in the efficiency validation below; real M365 assembly remains untested.

The token-efficiency revision separates conditional procedures, adds a read-only status collector, and narrows revision reads. [Efficiency validation](docs/token-efficiency.md) describes how to compare instruction load and full agent runs without confusing file size with token usage.
<!-- /dist:exclude -->

## Versioning

Releases are Git tags `vX.Y.Z`, each with a zip asset named `analytics-workbench-skills-vX.Y.Z.zip`. Changes are listed in [CHANGELOG.md](CHANGELOG.md).

<!-- dist:exclude -->
`scripts/build-dist.sh` builds the archive as `dist/analytics-workbench-skills.zip`; add the version when attaching it to the release. The archive carries the skills, this README without its design, validation, and build notes, `LICENSE`, and `CHANGELOG.md`; `docs/` and `CONTEXT.md` stay in the repository.
<!-- /dist:exclude -->

## License

MIT. See [LICENSE](LICENSE).
