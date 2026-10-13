# Analytics workbench skills

A portable, agent-agnostic workflow for shared data preparation, separate investigations, and repeatable delivery packages. Git tracks analytical code. You do not need GitHub hosting.

## Included skills

Every skill name has the `awb-` prefix. As a result, when you type `awb-` in a host that lists skills as commands, the host shows every workbench action.

- [awb-init](.agents/skills/awb-init/SKILL.md): use it for these tasks:
  - Initialize a project.
  - Repair a project, or bring it up to date after you install newer skills.
  - Start an investigation.
  - Resolve a consequential scope change.

  Its [project AGENTS.md template](.agents/skills/awb-init/assets/workbench/AGENTS.md) controls everyday analysis and recordkeeping.
- [awb-clean](.agents/skills/awb-clean/SKILL.md): clean one dataset at the shared foundation level. The skill does these steps:
  - In one call, it scans the dataset for candidate issues.
  - It decides with you where meaning changes.
  - It corrects the issues through canonical views.
  - In one call, it records the quality rows and catalog cells, and flags affected findings.
- [awb-eda](.agents/skills/awb-eda/SKILL.md): explore one dataset for the active investigation. The skill does these steps:
  - It does one scan in the scope and settings of the investigation.
  - It follows up with saved queries.
  - It records what was learned.

  Shared data problems go to `awb-clean`. A confirmed coverage gap becomes an open row in `foundation/quality.md`. Exploration records no findings.
- [awb-status](.agents/skills/awb-status/SKILL.md): a read-only report of the current status of the project, and of the requests that are applicable now.
- [awb-package](.agents/skills/awb-package/SKILL.md): create or revise the working draft of a delivery package.
- [awb-release](.agents/skills/awb-release/SKILL.md): when you mark a package delivered, preserve a frozen, numbered release. Also copy releases to the recorded storage location of the project.

## Requirements

- For package chart files, the chart helper that `awb-package` supplies needs Python 3.10 or later and pandas.
- The project helpers need Python 3.10 or later. For TOML settings, they need 3.11 or later, or `tomli`. The installer of `awb-init` declares and checks their packages: pandas for validation and charts, and `duckdb` for sessions, queries, and publication. `land()`, `publish()`, and `retain()` themselves use only the standard library.
- For result validation under the project `AGENTS.md`, the Python environment of the analysis project needs Python 3.10 or later and pandas. The shared validation file was tested with pandas 2.2.
- The `awb-clean` and `awb-eda` scans need Python 3.10 or later and the `duckdb` package in the interpreter of the project. TOML settings need 3.11 or later, or `tomli`. The `awb-clean` record script needs only the standard library.
- The read-only status collector needs Python 3.10 or later and the standard library. For unsupported project record formats, targeted manual reads are used.
<!-- dist:exclude -->
- pytest is necessary only to run the tests of this repository under `tests/`. These tests check the shipped helper files and are not part of the distributed archive.
<!-- /dist:exclude -->

## Install

Download `analytics-workbench-skills-vX.Y.Z.zip` from the GitHub releases of the repository, and unzip it to any location. It unpacks to one folder, `analytics-workbench-skills/`. This folder holds the six `awb-*` skill folders beside this README, `LICENSE`, and `CHANGELOG.md`. Copy the six `awb-*` folders into the user-level skills directory of your agent host. Replace all earlier copies.

If an earlier release left an `awb-update` folder, delete it: its job now belongs to `awb-init`. Do not unzip the archive into the skills directory itself. A host looks for `<skills directory>/<skill name>/SKILL.md`, and the extra folder level hides the skills. In a clone of this repository, the same six folders are under `.agents/skills/`.

The skills serve every project from the user-level directory. Projects need no local copies.

User-level skills directories:

- Claude Code: `~/.claude/skills/`. Claude Code does not find skills in `~/.agents/skills/`. See [Claude Code skills](https://code.claude.com/docs/en/skills).
- OpenAI Codex: `~/.agents/skills/`. Codex also scans `.agents/skills/` in each directory from the working directory up to the repository root. See [Codex agent skills](https://developers.openai.com/codex/skills).
- Other hosts: each `awb-*` folder follows the agent skills convention, that is, a folder that holds a `SKILL.md` with `name` and `description` frontmatter. Refer to the documentation of the host for its user-level skills directory.

### Project instructions in AGENTS.md

`awb-init` writes a compact project `AGENTS.md` and copies the conditional procedures into `workbench-guides/`. Keep those guides with the project. The root instructions tell when to read each guide. Scoping is self-contained and does not need an external interview skill. Hosts read `AGENTS.md` at different times.

- Claude Code reads a project `AGENTS.md` from version 2.1.277. By default, it reads that file only when no `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` exists in the working directory or in a directory above it. When one of these files exists, Claude Code reads the `CLAUDE.md` files and skips `AGENTS.md`. Your own `~/.claude/CLAUDE.md` does not count for this check. See [How Claude remembers your project](https://code.claude.com/docs/en/memory#agents-md).
- As a result, if a workbench is created in a repository or folder that already has a `CLAUDE.md`, the workbench rules are lost in Claude Code. The host gives no warning about this. `awb-init` reports such a file when it finds one, but it never edits it. To load the rules, add an import line to that file. The import line gives the path from that file to the `AGENTS.md` of the project, because Claude Code resolves imports relative to the file that contains them:
  - `@AGENTS.md` in a `CLAUDE.md` beside it.
  - `@../AGENTS.md` in `.claude/CLAUDE.md`.
  - The relative path down into the project, in the `CLAUDE.md` of an ancestor directory.

  Or, set Project instructions in `/config` to `claude-md-and-agents-md`, which reads both files. See [import additional files](https://code.claude.com/docs/en/memory#import-additional-files). On Claude Code versions before 2.1.277, use the import.
- OpenAI Codex reads `AGENTS.md` from its home directory (`~/.codex` by default). Then it reads the same file from each directory from the Git root down to the working directory. In every directory that it reads, it prefers an `AGENTS.override.md` in the same directory. See [Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md).

## Use

In the agent session of the target project, start from the business question:

> Use awb-init to initialize this analytics project. The question is …

If you ask without a question, `awb-init` asks for one. To set up the project alone, say that there is no question yet. Then continue analytical work normally with the generated AGENTS.md instructions. The default data flow is independent source landing, validated Parquet datasets, and DuckDB views that are loaded into separate analytical sessions. Data collection never writes directly into the canonical database as its only retained representation.

`awb-init` installs the project helpers under `src/` with its installer, `scripts/install_helpers.py`. If the project declares no dependencies, it also writes a `requirements.txt`. It records what it installs in a receipt, `.awb-receipt.json`. With this receipt, its `--upgrade` can bring unmodified earlier copies up to date.

Then mechanical work runs as single commands, and the agent reports their output verbatim. Computation runs as saved queries, not as scratch scripts. `python3 src/awb.py --help` lists the commands (`sql`, `profile`, `land`, `retain`, `publish`, `state`, `stale`, `export`, `check-draft`, `release`, `copy-releases`). The run script of each investigation, `run.py`, produces, validates, and records its results in one run, and writes their `state.md` rows. `state` prints the brief and state of the active investigation to resume. It also records finding wording and status (with history where due), and issues and next steps.

To see the current status and what you can ask for next:

> Use awb-status — where are we?

When a package is necessary:

> Use awb-package to prepare a draft for the active investigation.

The skill asks which datasets to include. Later requests revise the same draft. Work on the draft never releases it. When it is ready:

> Use awb-release — mark the package delivered.

After you choose a disposition for each flagged finding that the draft represents, this request preserves the next numbered release. That release is frozen from then on. Releases are kept under `deliveries/`, which the generated ignore rules exclude from Git. For this reason, before the first release, `awb-release` asks where released packages are kept. It records the location in the project README, and copies each release there when the location is reachable. If the location is recorded or changed later, `python3 src/awb.py copy-releases` copies existing releases.

M365 receives these items:

- The audience-facing findings, written as a slide-by-slide deck outline.
- An internal methodology reference.
- One data file for each chart.
- Chosen exports.
- Assembly instructions.

In the Microsoft 365 Copilot app, the PowerPoint agent builds the deck from the outline. It draws each chart as a native chart from its data file, under the chart rules of the assembly instructions. It asks you when something is not clear. To check the storyline, you read the headings of the outline before anything is built.

The same procedure applies to landed source data. `data/raw/` is also excluded from Git, and frequently it is not possible to fetch a landed original again. For this reason, before the first acquisition is landed, the agent asks where landed originals are kept outside the checkout. The agent records the location on the `Landed data is kept at` line of the project README. When the location is reachable, the agent copies each completed landing there. `awb-status` reports landed data that is only in the checkout.

After you install a newer release of the skills, bring each existing workbench up to date with the repair of `awb-init`:

> Use awb-init to repair this workbench.

Repair runs the helper installer with `--upgrade`. It replaces only unmodified copies of earlier shipped helpers, package formats, and workbench guides. It recognizes these copies from the checksum receipt that it writes at each install. It reports customized copies for you to decide on, and removes retired files only when you ask. The agent then reconciles the adapted `AGENTS.md` and `README.md` of the project against the current templates.

<!-- dist:exclude -->
## Design and validation

The [specification](docs/workbench-spec.md) defines the workflow and acceptance scenarios. The [design notes](docs/workbench-design.md) keep a record of the decisions behind it. Backend exceptions and exact cache-retention mechanics stay project-specific choices.

This section gives the historical validation of the `awb-*` skills. On 2026-10-07 four isolated agents ran it on separate fixture projects with synthetic data. Each agent read the skills from this repository and followed them as written. Each agent played both the analyst and the agent. For this reason, the scoping-interview transcripts are self-simulated and are weak evidence. Every other check is based on files that the agent produced.

Every expected-behavior bullet of acceptance scenarios 1 through 6 passed. None failed. The runs tested these items:

- `awb-init` on an empty directory with a business question:
  - One question at a time, with a recommended answer.
  - Git initialized without a commit.
  - Foundation records created only where their conditions fired.
  - The check of the host instruction file.
  - The question about the landed-data location, before the first landing.
- Scenario 1 and 2:
  - An expansion from 120 to 900 employees stayed in the same investigation. It revised the settings and state of the investigation, reused the preparation and neutral operations without change, and kept superseded findings in history.
  - A pivot to an independent group started a new investigation that inherited method and settings. Only the decisions that the pivot reopened were asked about. The earlier findings were used only as method context.
- Scenario 3:
  - An email-alias correction was assessed locally, implemented through shared preparation and view definitions, and documented in the quality record.
  - The correction flagged two findings with reasons. The conclusions, the draft, and the numbered release stayed byte-identical.
  - A second release attempt stopped to ask for a disposition for each affected conclusion.
- Scenario 4:
  - One stable package with a dataset selection that was asked for.
  - Release `001`, only at the explicit milestone.
  - A narrative-only revision to the same draft.
  - Release `002`. Before this release, a flag that was raised after the draft was made got a release-with-caveat disposition.
  - Manifests that record the producing commit separately from the packaging checkout.
  - Each release copied to the recorded storage location, and compared by file list and bytes.
- Scenario 5: a candidate source was assessed only enough to reject it. The reason was recorded. Nothing was converted, cached, or exported for that source.
- Scenario 6:
  - Paged API and extract acquisitions landed with provenance before conversion, and were copied to the recorded location.
  - A failed partial acquisition stayed unpublished.
  - A conversion failure was retried from landed files without reacquisition.
  - Two reader processes queried published Parquet through Git-managed views at the same time as a third process prepared a new publication. There was no shared DuckDB file.
- `awb-status` after each run: the shape of the report, the storage lines for landed data and releases, the `none chosen` risk path, and the request menu.

The runs also showed places where the instructions were silent or in conflict. These places included:

- The order of verification and revalidation dispositions in `awb-release`.
- The manifest field names that `awb-status` reads.
- The landing and publication layout.
- Where acquisition and settings code is kept.
- How an expansion is scoped.

Those places were corrected in the skills after the runs. The corrected wording itself was not run again. No API acquisition, production data conversion, or M365 assembly was done. The runs used the earlier package format: a `journal.md` and an `executive-summary.md` written in the workbench, with captions drawn into figure images. Those historical runs did not test the `findings.md` and `methodology.md` format that replaced it, the findings check, the slide-outline format, or the chart files. The efficiency validation below records the current helper and recipe checks. Real M365 assembly stays untested.

The token-efficiency revision separates conditional procedures, adds a read-only status collector, and narrows revision reads. [Efficiency validation](docs/token-efficiency.md) describes how to compare instruction load and full agent runs, and how not to confuse file size with token usage.
<!-- /dist:exclude -->

## Versioning

Releases are Git tags `vX.Y.Z`. Each release has a zip asset named `analytics-workbench-skills-vX.Y.Z.zip`. [CHANGELOG.md](CHANGELOG.md) lists the changes.

<!-- dist:exclude -->
`scripts/build-dist.sh` builds the archive as `dist/analytics-workbench-skills.zip`. When you attach it to the release, add the version. The archive contains these items:

- The skills.
- This README, without its design, validation, and build notes.
- `LICENSE`.
- `CHANGELOG.md`.

`docs/` and `CONTEXT.md` stay in the repository.
<!-- /dist:exclude -->

## License

MIT. See [LICENSE](LICENSE).
