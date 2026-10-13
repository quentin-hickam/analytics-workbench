# Changelog

This file records all notable changes to this project. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Each release is a Git tag `vX.Y.Z`, and the zip archive is attached to its GitHub release.

## [Unreleased]

### Changed

- The `findings.json` file of an investigation owns the rendered Current findings table. State writers refuse drift that hand edits cause. `state render` restores the table, `state flag` records flags through the project helper, and draft checks report drift.

- `awb-clean` keeps hashed scan links, and recorded counts and dates, in the committed `foundation/quality.json`. As a result, quality observations stay unchanged on reopen. The record step writes Active rows and catalog cells before flags, and writes corrections last. As a result, interrupted passes can be retried. If a correction row is identical to a row that is already recorded, it is not appended again. The output lists it under `corrections_unchanged`.
- The delivered output is a PowerPoint deck that the PowerPoint agent builds in the Microsoft 365 Copilot app. This deck replaces the Word and Excel documents. `findings.md` is the slide-by-slide outline of the deck. The outline has these parts:
  - A one-sentence headline with its number for each slide.
  - At most five bullets.
  - Caveats on the slide that they qualify.
  - Speaker notes.

  As a result, the storyline can be checked from the headings before anything is built. Its **Answer** slide is the executive summary. M365 no longer distills one. The assembly instructions tell the PowerPoint agent to do these steps:
  - Build one slide for each outline slide, with headlines, numbers, and caveats as written.
  - Ask before it builds, when one of these conditions is true:
    - The audience or decision is different.
    - A slide will not fit.
    - A chart cannot be drawn as specified.
    - The effect of a caveat is not clear.

  Supporting datasets are delivered beside the deck.
- M365 draws charts as native, editable PowerPoint charts. Each chart in `findings.md` is a specification (form, comparison, highlight, axis, interval, source, caveat, alt text). Its plotted values are one CSV in the `charts/` directory of the draft. This CSV is serialized from a recorded result under the same export check as datasets. As a result, M365 draws from the numbers and never aggregates them. Chart forms, style, and honest-display rules are in the M365 assembly instructions. The manifest gets a `charts` field that names the result that each chart file serializes.
- Result evidence is `awb-evidence/3`:
  - `record_evidence()` no longer takes `figure=`.
  - Every result has a `[results.<id>]` table in `settings.toml`, and its evidence records only `[parameters]` and that table. As a result, a new result or a new `[eda]` table no longer marks other results stale.
  - Producing code is `run.py`, the result's own queries, the other code of the investigation, and `src/` except the dispatcher, provenance, and packaging helpers. As a result, an `awb-init` repair no longer marks every finding stale. `code_paths` adds to these paths.
  - `run.py` removes the evidence of a result before it writes its table again. As a result, an interrupted rerun shows as stale.
  - The settings parser uses `tomli` as a fallback on Python 3.10.

- After an eight-agent audit, every skill and project template was rewritten against the writing-for-agents guidelines:
  - Skill descriptions are shorter and start with their trigger.
  - The project `AGENTS.md` decreases from 667 to 528 words. It names the `awb-init` skill folder, so reference pointers resolve without a search.
  - The references of the guides load only for the rare branches that need them.
  - One vocabulary is used in all files: *stale* (evidence no longer matches), *flagged* (awaiting revalidation), *frozen* (a release), *verbatim* (helper output), *saved query*, *release*, and `run.py`.

  A typical cleaning pass decreases from 9–11 tool calls to 6 and an exploration pass decreases from 8–9 to 5–6.
- Packaging follows a numbered sequence. `export` runs on every revision with the complete set of represented results:
  - `--chart` and `--dataset` serialize behind the freshness check.
  - `--result` records producing state without the freshness check.
  - A blocked export stops with "changed results need separately authorized analytical work", and does not suggest a rerun.

  `draft-provenance` is merged into `export`. Manifests are `manifest.json`, and exports are CSV. The `audit/` records for each package are removed. `findings.py`, `manifest.py`, and `charts.py` merge into a standard-library `src/packaging/draft.py`. `m365-assembly.md` is copied into the draft, but it is not read before the copy. Each flagged finding has one disposition.
- `land --records` and `publish --from` take one value for each flag. As a result, the printed usage can be copied as it is. Generated requirements declare `tomli; python_version < "3.11"` when a project asset falls back to that package.
- `awb-status` has these changes:
  - It counts a `revalidate` disposition as a block on a release.
  - It reports a recorded `none chosen` storage line as the decision of the user.
  - It accepts flags that the draft does not represent.
  - It renames its state check to `git.state_status` (`out of date` / `up to date`).
  - It keeps its request map in `SKILL.md`.

### Fixed

These fixes come from the tool-call audit in `docs/tool-call-audit-2026-10-11/`. That audit found about 22 avoidable calls in a 123-call lifecycle.

- `export` now keeps the `revalidation_flags` of the manifest in agreement with `state.md` on every write. It records `none` when nothing is flagged. A flagged finding gets an entry with these values:
  - Its finding and reason, copied verbatim.
  - `represented_in: []`.
  - Disposition `none`.

  An entry whose finding and reason still match is kept as it was. An entry for a cleared flag is removed. `export` lists the unfinished entries as `flags_pending`. When `state.md` cannot be read, it reports `flags_error`. The sync is complete before any file is written. An entry whose finding or reason is not text matches no flag. As a result, it no longer crashes `export` or `check-draft`. `check-draft` reports malformed or unfinished entries as `flag_entries` and fails on them. Previously, a draft with no flags passed `check-draft`, but then `release` refused it.
- When display names are missing, `export` prints `display_stub`: a ready-to-paste line under `[columns]` for each absent name. A blank display name now counts as missing and gets its own error. `awb-package` sets the display names before it writes the outline. As a result, chart **Data:** lines use the exported headers.
- `awb-package` says that a revision that only adds caveats runs `export --result` alone. The reason is that `--chart`, `--dataset`, and `--no-datasets` serialize again. It reviews the places of each flag, and asks for the disposition during the revision. `awb-release` asks where releases are kept before the first release. As a result, `release` copies the release itself.
- `land` creates a missing `foundation/sources.md` from the template, writes its Acquisitions row, and reports `"created": true`. Previously, it exited 1 after the landing. `retain` reports `matched` for a retained copy with no discrepancies. It reports `conflict` only for an existing copy that is different.
- `check-draft` no longer reports a slash between two plain words, such as yes/no, as a path. A slash token is a path when it has one of these:
  - A `./`, `../` or scheme prefix.
  - Two or more slashes.
  - A segment with a file extension or underscore.
  - A workbench directory as its first segment.
  - A recorded project name as any segment, also when that name is plain words.
- When `install_helpers.py` runs outside a workbench, it now reports the `missing` markers and a `hint` that names the first step (adapt README.md and AGENTS.md). It no longer exits with no guidance.
- `publish` prints `view_sql` (the canonical view definition, with the dataset name and path escaped) beside `catalog_row`.
- `record_cleaning.py` accepts a recorded quality ID, such as `Q-004`, as an `issues` key. As a result, a decision on an issue that the scan no longer lists revises its row and can append a correction. It refuses a row recorded from another scan, two keys that name the same row, and unknown keys.
- `awb-eda` names the `state issues` and `state next` commands. `analysis.md` says that `state finding` takes `--text`, `--status`, `--reason`, and `--caveat` in one call.
- When a publication row has the same name, `record_cleaning.py` sets the catalog row of the canonical view. Previously, it refused with `several rows are named <dataset>`. The cause was that the `catalog_row` that `publish` prints has the name of the dataset, as its view does. Two rows with one name that are not views still cause a refusal. A blind rerun of the audit found this problem in both of its runs.
- `export` records every represented result and its evidence path in a new manifest field, `results`. This field includes results that it does not serialize. `awb-status` reads it to report `rerun_since_draft` for each package: the represented results whose evidence was recorded after the last revision of the draft. It also suggests a revision of the draft. A manifest written before `results` existed reports this as unknown. Previously, if a rerun changed a packaged result, the draft and its release were still reported as current.

### Added

- Mechanical work runs as single commands through a project dispatcher, `python3 src/awb.py <command>`. As a result, agents no longer write throwaway helper scripts or type helper output into records again:
  - `sql` runs a saved query file or SQL text in a new session, and prints a capped table. `profile` profiles a view or query, samples very large results, and saves the full profile.
  - `land` copies files into an acquisition. It retains the acquisition when a storage location is recorded, and writes its Acquisitions row. `retain` does the same for every acquisition that has no retained copy or row. `publish` converts acquisitions to validated Parquet from a SQL select and an optional check query.
  - `state` prints the `brief.md` and `state.md` of the active investigation verbatim. It gives a warning about findings whose evidence is missing.
  - `state finding` sets the wording of findings, promotes them, or supersedes them. It can do this for several findings at one time for a status. It refuses to promote stale or unexplained findings, where notes explain only the checks that they were written against. For supported, superseded, and flagged changes, it writes a `history.md` entry, and that entry must have a reason.
  - `state issues` and `state next` add and remove items in one call. `state switch` changes the active investigation in the README and prints it. A resume and a switch each take one call, not 3–5.
  - `stale` compares the evidence of every finding with the current state. It lists the findings, with their `state.md` rows, that a shared correction affects.
  - `check-draft` derives the complete internal-name set, runs the findings and chart checks, writes the manifest inventory again, and verifies it. `release` numbers, copies, and stamps the release, and copies it to storage with a tree comparison.
- Each investigation gets a run script, `run.py`, with `settings.toml`. One run produces, validates, saves, and records every result, and writes its `state.md` row:
  - A new result gets a `provisional` placeholder row.
  - If the table, checks, and settings of a rerun match the previous run, the rerun keeps its row unchanged.
  - Any other rerun makes the row `provisional` (superseded stays superseded), and keeps its notes. It also removes a flag reason, and records the rerun of a supported or flagged finding in `history.md`.

  A failed state write removes the new evidence and fails the run. When publications and acquisitions are not given, `record_evidence()` derives them from the views. The settings template documents the validation spec keys and the `[eda]` scan keys.
- `awb-init` installs every project helper one time with `scripts/install_helpers.py`. This installer never overwrites. When the project declares no dependencies, it writes `requirements.txt`. Otherwise, it reports missing entries. It also checks the interpreter. The "copy on first use" steps for each helper are removed.
- `python3 src/awb.py export` writes the chart and dataset files of a package in one call, from the saved result tables of the investigation. It does these steps:
  - It keeps the named columns.
  - It applies display names and code labels from `foundation/display.toml`.
  - It rounds half up.
  - It runs the export checks.
  - Only after these steps, it writes the files and records `charts`, `dataset_selection`, and `export_checks` in the manifest.

  It prints the header-to-source lines for `methodology.md`. This removes the last scratch script from routine packaging.
- `awb-clean` cleans one dataset at the shared foundation level. Its scan does these steps:
  - In one DuckDB call, it finds candidate issues: parse failures, whitespace, case and spelling variants, placeholder values, duplicate rows and keys, out-of-range and impossible dates, orphans, and null patterns.
  - It writes the complete scan to `foundation/scans/<name>.json`.
  - With `--rescan`, it reports before and after counts for each issue.

  Its record script writes quality issue and correction rows, catalog cells, and revalidation flags in one call, from the judgments of the agent. Corrections are in canonical view definitions. Exclusions for a specific question stay in the investigation.
- `awb-eda` explores one dataset for the active investigation. Its scan computes these values in one DuckDB call, in the scope that the settings of the investigation define:
  - The grain and candidate keys.
  - Per-column distributions.
  - Null patterns.
  - Date coverage and gaps.
  - The measure by dimension and over time, with groups that move against the overall trend.
  - The strongest correlations of the measure with other numeric columns.

  It writes the complete scan to `investigations/<name>/exploration/eda/<dataset>.json`. It prints a compact summary, with anomalies routed to `awb-clean` or to the investigation. A confirmed coverage gap becomes an open row in `foundation/quality.md`. Follow-ups are saved queries that run with `python3 src/awb.py sql`. Exploration records no findings.
- The `awb-init` repair brings a workbench up to date:
  - `scripts/install_helpers.py --upgrade` replaces only unmodified earlier copies of helpers, package formats, and project guides. It recognizes them from the install receipt of the project (`.awb-receipt.json`, which the installer writes).
  - It reports customized copies for the user to decide on (`--replace PATH`, which you can give more than one time).
  - On request, it removes unmodified retired files (`--remove-retired`).
  - With `--package-formats`, it installs missing package formats.
  - The agent reconciles `AGENTS.md` and `README.md` against the current templates.
- `awb-package` supplies a chart helper, installed at `src/packaging/charts.py`. `write_charts()` writes one `chart-N.csv` for each chart, in specification order. It refuses headers that are not display names. `check_charts()` matches the chart specifications in `findings.md` with the chart files.

- `copy-releases` copies existing releases to a newly recorded storage location and compares each copy. `check-draft` also reports `unmatched_flags` (findings that are flagged in `state.md` but are missing from the manifest). It also checks that every finding heading has a methodology section. `release` has these changes:
  - It refuses while flags are unmatched or dispositions are not settled.
  - It trusts `check-draft --verify-only` as its structural gate.
  - It verifies its local copy.
  - It returns the datasets, dispositions, provenance gaps, and checkout-only acquisitions that its report needs.
- When no `[eda]` period is set, the `awb-eda` scan takes the period from the `[parameters]` of the investigation. When scope or measure are missing, it prints `not set` lines that name the flags to pass. It gets `--show PATH`, which prints one saved section. `awb-clean` gets a shared-limitation class, prints the count of each recorded issue, and keeps recorded counts current.

### Removed

- The removed items are:
  - Readers for evidence other than result-scoped `awb-evidence/3`.
  - The installer's frozen list of hashes that were shipped before receipts, and the installer's list of retired files.
  - The tolerance of `awb-status` for a release without `manifest.json`. It now reports such a release as uncertain.

  Packaging and `stale` refuse other evidence until its result is rerun.

- Cleaning scan files are no longer committed. The workbench `.gitignore` excludes `/foundation/scans/`, and quality rows keep the scan marker and date. EDA scans stay tracked.

- The `awb-visualize` skill, its figure style module, references, and rendering notes. The workbench renders no figures for delivery. The chart rules moved to the M365 assembly instructions, and an exploratory chart in chat follows the defaults of the host. `src/presentation/` is removed from the generated layout, and matplotlib and seaborn are no longer requirements. The instruction-load script no longer has its table scenario.

## [0.3.0] - 2026-10-09

### Changed

- The release archive contains only the five `awb-*` skills, `README.md`, `LICENSE`, and `CHANGELOG.md`. These items stay in the repository: the specification, design notes, and efficiency validation under `docs/`, and the design, validation, and build notes of the README.
- Reconciled the conditional package and figure references with the audience-facing findings/methodology layout:
  - Both release verification passes run the findings check.
  - Figures use document captions and the current style API.
  - Status reads methodology for affected findings.

  Instruction-size comparisons now use the PR #6 merge as their baseline.
- Reduced routine instruction load:
  - The generated `AGENTS.md` routes to project data and analysis guides.
  - Visualization routes by output type.
  - Release reads a focused shared package contract.
  - Narrative revisions start with relevant records and still verify the complete draft.
- Investigation scoping is self-contained in `awb-init`. This removes the external `grilling` dependency, but keeps one consequential question at a time, recommendations, settled answers, and explicit material unknowns.
- Helper interface references show project imports and direct serialization of complete audit records, with compact tool output.
- The project `AGENTS.md` names the composition entry of the investigation as the only producer of a finding. A rerun of flagged findings runs the entry with its settings file and records evidence. It does not rebuild the analysis in chat. `awb-status` routes "Rerun the flagged findings" to the entry. A query run a second time is saved under the `exploration/` of the investigation, or promoted to a view and rerun by path. Profiling goes through the shared `profile()` operation.
- Package format: in place of `journal.md` and `executive-summary.md`, a draft now has two documents:
  - `findings.md`: the audience-facing account and the only source of document content.
  - `methodology.md`: an internal reference where view names, settings keys, and result IDs belong.

  `findings.md` is written for the audience in the investigation brief. It keeps out file names, view and column names, settings keys, internal identifiers, and code terms. The two documents agree and share finding headings. Before this change, delivered documents carried those internal names because M365 built its report from a journal that was also the internal record. This breaks existing drafts: the next revision through `awb-package` rewrites them in the new format. Released packages are not changed. Exported datasets name their columns with glossary display names, and `methodology.md` maps each name back to its source column.
- M365 assembly instructions tell M365 Copilot to do these steps:
  - Distill the executive summary from `findings.md` under stated guidelines: answer first, three to five key findings with their numbers, decision-relevant and revalidation caveats, and no new claims or internal names.
  - Refer to `methodology.md` only to understand a decision.
  - Ask the requester before it writes a draft when the audience, decision, length, or effect of a caveat is not clear.

  `awb-release` verifies the new consistency rules. `awb-status` reads the draft `methodology.md` to match flagged findings.
- The investigation brief gets an **Audience** section: who reads the delivered documents, what they already know, the decision they own, and the terms they use. The agent records it when the user gives it. When a package needs it and the brief does not have it, `awb-package` asks for it.
- Figures have no caption in the image. The caption is in the document that contains the figure:
  - An italic line under the figure in chat.
  - Text beside the figure link in records.
  - The `*Figure N. ...*` line in `findings.md`, which M365 turns into a Word caption.

  Titles are short one-line headlines. Every text element in the image (including tick labels, legend titles, and facet titles) uses display labels from the glossary, not column names or codes.

### Fixed

- Status collection has these changes:
  - It normalizes storage values in Markdown format.
  - It treats missing optional storage lines as unrecorded.
  - It scopes Git observations within larger repositories.
  - It reports inaccessible directories as uncertainties, and does not crash.

### Added

- A read-only status collector with explicit uncertainty and targeted fallback for custom record formats, and also regression tests.
- An instruction-load comparison script and an agent-run evaluation procedure to measure efficiency, without a decrease in the strength of correctness checks.
- `awb-package` supplies a manifest helper, which is copied to `src/packaging/manifest.py` on first use. The helper builds the manifest `inventory`, verifies a draft against it, and compares a release with its storage copy. `awb-package` and `awb-release` now run it, and do not hash and compare files by hand.
- `awb_validate.py`: a shared validation file that `awb-init` supplies, and that the project copies to `src/exploration/validate.py`. `validate()` runs the columns, row-count, join, and null checks. It records the scope, metrics, and values judgments in the same list, which is stored with result evidence. `profile()` reports row count and per-column type, null rate, distinct count, and sample values.
- `awb-init` supplies `awb_landing.py`, which is copied to `src/preparation/landing.py` on the first landing. `land()`, `publish()`, `retain()`, and `session()` replace the landing, publication, retained-copy, and view-loading procedures. Before, the project `AGENTS.md` described these procedures step by step. Provenance and publication files are JSON with fixed keys (`provenance.json`, `publication.json`). `session()` needs `duckdb`.
- `awb-init` supplies a provenance helper, which is copied to `src/provenance.py` the first time a result needs it. The helper writes the evidence of each result to `investigations/<name>/evidence/<result-id>.json`, and compares the current state with it. `state.md` findings link to that file, and do not hold checksums. `awb-package` export checks run the comparison and record its output. Evidence, acquisition provenance, and publication files are fixed as JSON. The delivery manifest format stays open.
- `awb-package` supplies a findings check, `awb_findings.py`, which is copied to `src/packaging/findings.py` on first use. `check()` reports these items in `findings.md`: backticked code, paths, file names, snake_case and dotted identifiers, commit SHAs, and internal names that the caller supplies. `awb-package` repairs the draft until the check reports nothing. `awb-release` runs it as part of verification.
- `check_text()` in the `awb-visualize` figure style lists image text that exposes identifiers, file names, or `column = value` facet titles, or that is longer than 65 characters. `save_figure()` runs it and refuses to write a figure that fails.

### Removed

- The executive summary template and the journal template in `package-format/`. M365 Copilot distills the executive summary from `findings.md`. `findings-template.md` and `methodology-template.md` replace the journal.
- `add_caption()` from the `awb-visualize` figure style, because captions no longer go in the image.

## [0.2.0] - 2026-10-07

### Changed

- The export check in `awb-package` covers data as well as code. These items must match the state recorded with the result: view definitions, the publications they read, input publication and acquisition checksums, and resolved settings. Each publication directory now holds a publication file with its inputs, conversion commit, and file checksums. Result evidence records those identities.
- The dirty-state comparison no longer contradicts itself. Committed result code paths are compared with the producing commit. Paths recorded as uncommitted producing changes are compared with their recorded checksums.
- The validation checklist (columns, row counts, joins, nulls, scope, metrics, values) is an always-on requirement in the project `AGENTS.md`. It is recorded with the evidence of each result and stated in the package journal.
- Investigation history and the package journal keep methodological mistakes that changed a finding or explain why an earlier conclusion was wrong. Only routine debugging, coding mistakes, and abandoned attempts that changed no understanding are excluded.
- The two workbench skills are repackaged as five skills under the `awb-` prefix. As a result, when you type `awb-` in a host that lists skills as commands, the host shows every workbench action. `workbench-init` and `workbench-package` no longer exist.
  - `awb-init` keeps project setup, investigation scoping, and scope changes. It now asks for a business question when none is given.
  - `awb-package` creates and revises the working draft of a package only.
  - `awb-release` makes numbered releases when you mark a package delivered. It checks the revalidation flags that are current at release time. It asks where released packages are kept, records that in the project README, and copies each release there when the location is reachable.
- The release archive unpacks to one folder, `analytics-workbench-skills/`. The five `awb-*` skill folders are at its top level, beside `README.md`, `LICENSE`, `CHANGELOG.md`, and `docs/`. Earlier archives named the top folder after the checkout directory, and put the skills under `.agents/skills/`. The archive no longer contains the build script, `.gitignore`, or `CONTEXT.md`, which are only for the repository.
- Install instructions now say to unzip the archive to any location, and to copy the five `awb-*` folders into the user-level skills directory of the host. The v0.1.0 and v0.1.1 release notes said to unzip into the skills directory. That puts the skills one level too deep for any host to find them.

### Added

- `awb-status`: a read-only report of the current status of the project. It covers the active investigation, findings and revalidation flags, open issues, package and release state, and landed data and release storage. It ends with the requests that are applicable now.
- `awb-visualize`: principles, libraries, and style defaults for charts and tables that show inline in agent chat and stay intact when pasted into a document. It includes a shared matplotlib and seaborn style file, and image paths that hosts can show in chat.
- Landed-data retention. `data/raw/` is excluded from Git, and frequently it is not possible to fetch a landed original again. For this reason, before the first landing, the agent asks where landed originals are kept outside the checkout. It records the answer on the `Landed data is kept at` line of the project README. It copies each completed landing there when the location is reachable, and records the retained copy for each acquisition in `foundation/sources.md`. `awb-status` reports landed data that is only in the checkout.
- `awb-init` reports an instruction file that the current host reads in place of the workbench `AGENTS.md`, for example a `CLAUDE.md` in the project directory or above it. It never creates or edits that file.
- MIT license (`LICENSE`).
- This changelog.
- Validation of acceptance scenarios 1 through 6 by isolated agents on fixture projects, recorded in the README. Every expected-behavior bullet passed.
- Instruction gaps that those runs showed are closed:
  - `awb-release` verifies structural rules before it asks for revalidation dispositions, and verifies the caveat rule again after that.
  - Dispositions cover every place where a conclusion is represented, including figures and dataset columns.
  - The manifest template sets fixed field names that `awb-status` reads.
  - The project `AGENTS.md` gives a default landing, provenance, retention, and publication layout, and locations for acquisition and settings code.
  - An expansion is scoped through `awb-init`.
  - `awb-status` compares current flags with draft dispositions, handles repositories with no commits, and offers the next analytical step.
- README sections on requirements, host compatibility, and versioning. Requirements name the source of the `grilling` dependency: `skills/productivity/grilling` in [mattpocock/skills](https://github.com/mattpocock/skills), tested against release v1.3.1. They also name the Python packages that `awb-visualize` assumes. Host compatibility covers where Claude Code and OpenAI Codex look for user-level skills, and when Claude Code reads a project `AGENTS.md`.

### Removed

- The migration of projects from the `workbench-init` and `workbench-package` names was drafted during the repackaging, and was removed before release. No project was created with an earlier release, so there is nothing to migrate.
- The knowledge vault (`awb-vault`, the project `AGENTS.md` vault section, and the vault specification) is removed from this release. Its current state is kept on the `dev/knowledge-vault` branch for later work.

### Release notes

This text is ready to paste into the GitHub release for v0.2.0:

```markdown
The workbench is now five skills under the `awb-` prefix, replacing `workbench-init` and `workbench-package`. Typing `awb-` in a host that lists skills as commands shows every workbench action.

## Changes since v0.1.1
- `awb-init` sets up a project and scopes investigations, and asks for a business question when none is given.
- `awb-status` (new) reports where the project stands and the requests that fit right now. It changes nothing.
- `awb-package` creates and revises a package's working draft. `awb-release` makes numbered releases, asks where released packages are kept, and copies each release there.
- `awb-visualize` (new) sets figure and table conventions for chat and documents.
- Landed source data in `data/raw/` is excluded from Git, so the agent now asks where landed originals are kept outside the checkout and copies each completed landing there.
- The zip now unpacks to `analytics-workbench-skills/` with the skill folders at its top level. The v0.1.x instructions to unzip into your skills directory were wrong for those archives.
- Results are validated before they are presented (columns, row counts, joins, nulls, scope, metrics, values), package exports are checked against the recorded code and data state, and histories keep the methodological mistakes that changed a finding.
- The project is MIT licensed, and changes are listed in CHANGELOG.md.

## Install
1. Download `analytics-workbench-skills-v0.2.0.zip` and unzip it anywhere. It unpacks to one folder, `analytics-workbench-skills/`.
2. Copy the five `awb-*` folders from that folder into your agent host's user-level skills directory: `~/.claude/skills/` for Claude Code, `~/.agents/skills/` for OpenAI Codex. Do not unzip the archive into the skills directory itself; the extra folder level hides the skills from the host.
3. Delete any `workbench-init` and `workbench-package` folders left there by v0.1.x.

**Required:** the `grilling` skill from https://github.com/mattpocock/skills (`skills/productivity/grilling`, tested against release v1.3.1) must be installed where your host discovers skills, normally the same directory. It is not included.

**Claude Code:** the workbench rules live in the project's `AGENTS.md`. Claude Code reads it from version 2.1.277, and by default only when no `CLAUDE.md` or `CLAUDE.local.md` exists in the working directory or above it. If one does, add an import line to it with the path from that file to the project's `AGENTS.md` (`@AGENTS.md` beside it, `@../AGENTS.md` in `.claude/CLAUDE.md`, the relative path into the project from an ancestor's `CLAUDE.md`), or set Project instructions to `claude-md-and-agents-md` in `/config`.

## Use
> Use awb-init to initialize this analytics project. The question is …

> Use awb-status to show where things stand.

The README covers packaging, releases, and Python requirements for figures.
```

## [0.1.1] - 2026-10-02

The skills now contain all the guidance that an agent needs. Nothing that the agent relies on is only in the specification or design notes of the repository.

### Changed

- Drafts are working copies that the next revision overwrites. The agent says that a draft is preserved only when you mark it delivered.
- Corrections can stay in views. Materialized tables do not accumulate in a persistent DuckDB file, except as a catalogued cache.
- A commit without retained inputs is not described as an exact rerun.
- Vault claims that are copied into a project are its fixed basis. Newer vault claims are checked before use.
- The instructions explain why the conclusions of other analyses are read only after your own results exist.
- Exploration does not wait for cleaning, and canonical data is still checked for fit for each question.
- CLIs are optional, entry points stay small, and investigation composition code is in `investigations/<name>/`.
- After setup, the agent says how work continues, and that the vault fills only when you ask.

## [0.1.0] - 2026-10-02

First release.

### Added

- `workbench-init`: set up an analytics project, and start investigations through a scoping interview that calls the external `grilling` skill. On request, create a knowledge vault.
- `workbench-package`: create, revise, or explicitly release a delivery package.
- Project templates:
  - The `AGENTS.md` workflow rules.
  - The project README.
  - Data foundation records (catalog, glossary, quality, sources).
  - Investigation records (brief, state, history).
  - Delivery package formats, including M365 assembly instructions.
- The knowledge vault, which carries knowledge about systems, databases, schemas, and tables from one project to the next through `WORKBENCH_VAULT`.
- The specification, design notes, and an archive build script that packages an explicit allowlist of tracked files.

[Unreleased]: https://github.com/quentin-hickam/analytics-workbench/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/quentin-hickam/analytics-workbench/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/quentin-hickam/analytics-workbench/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/quentin-hickam/analytics-workbench/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/quentin-hickam/analytics-workbench/releases/tag/v0.1.0
