# Changelog

All notable changes to this project are recorded in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Each release is a Git tag `vX.Y.Z` with the zip archive attached to its GitHub release.

## [Unreleased]

### Changed

- The delivered output is a PowerPoint deck built by the PowerPoint agent in the Microsoft 365 Copilot app, replacing the Word and Excel documents. `findings.md` is the deck's slide-by-slide outline: a one-sentence headline with its number per slide, at most five bullets, caveats on the slide they qualify, and speaker notes, so the storyline can be checked by reading the headings before anything is built. Its **Answer** slide is the executive summary; M365 no longer distills one. The assembly instructions tell the PowerPoint agent to build one slide per outline slide with headlines, numbers, and caveats as written, and to ask before building when the audience or decision differs, a slide will not fit, a chart cannot be drawn as specified, or a caveat's effect is unclear. Supporting datasets are delivered beside the deck. Existing drafts are rewritten in the new format on their next `awb-package` revision; released packages are untouched.
- Charts are drawn by M365 as native, editable PowerPoint charts. Each chart in `findings.md` is a specification (form, comparison, highlight, axis, interval, source, caveat, alt text), and its plotted values are one CSV in the draft's `charts/` directory, serialized from a recorded result under the same export check as datasets, so M365 draws from the numbers and never aggregates them. Chart forms, style, and honest-display rules live in the M365 assembly instructions. The manifest gains a `charts` field naming the result each chart file serializes.
- Result evidence is `awb-evidence/2`: `record_evidence()` no longer takes `figure=` and the evidence file has no figure entry. `compare_evidence()` still reads `awb-evidence/1` files, ignoring their figure entry, so earlier evidence keeps passing export checks.

### Added

- `awb-update` brings an existing workbench up to date after newer skills are installed. Its helper compares every file the skills copy verbatim (shared package formats, project helpers, project guides) with every version the skills have shipped, replaces unmodified earlier copies, leaves customized ones for the user to decide with a diff, and offers to remove retired files such as the old figure style and journal templates. Its migrations section lists the edits for adapted files such as `AGENTS.md` and `README.md`. `scripts/record-shipped-versions.py` regenerates the shipped-version record from Git history, and a test fails when it is out of date.
- `awb-package` ships a chart helper, `awb_charts.py`, copied to `src/packaging/charts.py` on first use. `write_charts()` writes one `chart-N.csv` per chart in specification order and refuses headers that are not display names; `check_charts()` matches the chart specifications in `findings.md` with the chart files, and `awb-package` and `awb-release` run it.

### Removed

- The `awb-visualize` skill, its figure style module, references, and rendering notes. The workbench renders no figures for delivery; the chart rules moved to the M365 assembly instructions, and an exploratory chart in chat follows the host's defaults. `src/presentation/` is gone from the generated layout, and matplotlib and seaborn are no longer requirements. The instruction-load script drops its table scenario.

## [0.3.0] - 2026-10-09

### Changed

- The release archive carries only the five `awb-*` skills, `README.md`, `LICENSE`, and `CHANGELOG.md`. The specification, design notes, and efficiency validation under `docs/`, and the README's design, validation, and build notes, stay in the repository.
- Reconciled conditional package and figure references with the audience-facing findings/methodology layout: both release verification passes run the findings check, figures use document captions and the current style API, and status reads methodology for affected findings. Instruction-size comparisons now use the PR #6 merge as their baseline.
- Reduced routine instruction load: the generated `AGENTS.md` routes to project data and analysis guides; visualization routes by output type; release reads a focused shared package contract; narrative revisions begin with relevant records and still verify the complete draft.
- Investigation scoping is self-contained in `awb-init`, removing the external `grilling` dependency while retaining one consequential question at a time, recommendations, settled answers, and explicit material unknowns.
- Helper interface references show project imports and direct serialization of complete audit records, with compact tool output.
- The project `AGENTS.md` names the investigation's composition entry as the only producer of a finding. A rerun of flagged findings runs the entry with its settings file and records evidence instead of rebuilding the analysis in chat, and `awb-status` routes "Rerun the flagged findings" to it. A query run a second time is saved under the investigation's `exploration/` or promoted to a view and rerun by path; profiling goes through the shared `profile()` operation.
- Package format: a draft now carries `findings.md`, the audience-facing account and the only source of document content, and `methodology.md`, an internal reference where view names, settings keys, and result IDs belong, in place of `journal.md` and `executive-summary.md`. `findings.md` is written for the audience in the investigation brief and keeps file names, view and column names, settings keys, internal identifiers, and code terms out; the two documents agree and share finding headings. Delivered documents had carried those internal names because M365 built its report from a journal that was also the internal record. This breaks existing drafts: the next revision through `awb-package` rewrites them in the new format. Released packages are untouched. Exported datasets name their columns with glossary display names, and `methodology.md` maps each back to its source column.
- M365 assembly instructions tell M365 Copilot to distill the executive summary from `findings.md` under stated guidelines (answer first, three to five key findings with their numbers, decision-relevant and revalidation caveats, no new claims or internal names), to consult `methodology.md` only to understand a decision, and to ask the requester before drafting when the audience, decision, length, or a caveat's effect is unclear. `awb-release` verifies the new consistency rules, and `awb-status` reads the draft `methodology.md` to match flagged findings.
- The investigation brief gains an **Audience** section: who reads the delivered documents, what they already know, the decision they own, and the terms they use. The agent records it when the user gives it; `awb-package` asks for it when a package needs it and the brief lacks it.
- Figures carry no caption in the image. The caption lives in the document that contains the figure: an italic line under it in chat, text beside the figure link in records, and the `*Figure N. ...*` line in `findings.md`, which M365 turns into a Word caption. Titles are short one-line headlines, and every text element in the image, including tick labels, legend titles, and facet titles, uses display labels from the glossary rather than column names or codes.

### Fixed

- Status collection normalizes Markdown-formatted storage values, treats missing optional storage lines as unrecorded, scopes Git observations within larger repositories, and reports inaccessible directories as uncertainties rather than crashing.

### Added

- A read-only status collector with explicit uncertainty and targeted fallback for custom record formats, plus regression tests.
- An instruction-load comparison script and agent-run evaluation procedure for measuring efficiency without weakening correctness checks.
- `awb-package` ships a manifest helper, copied to `src/packaging/manifest.py` on first use, that builds the manifest `inventory`, verifies a draft against it, and compares a release with its storage copy. `awb-package` and `awb-release` now run it instead of hashing and comparing files by hand.
- `awb_validate.py`, a shared validation file that `awb-init` ships and the project copies to `src/exploration/validate.py`: `validate()` runs the columns, row-count, join, and null checks and records the scope, metrics, and values judgments in the same list, which is stored with result evidence; `profile()` reports row count and per-column type, null rate, distinct count, and sample values.
- `awb-init` ships `awb_landing.py`, copied to `src/preparation/landing.py` on the first landing. `land()`, `publish()`, `retain()`, and `session()` replace the landing, publication, retained-copy, and view-loading procedures the project `AGENTS.md` described step by step. Provenance and publication files are JSON with fixed keys (`provenance.json`, `publication.json`). `session()` needs `duckdb`.
- `awb-init` ships a provenance helper, copied to `src/provenance.py` the first time a result needs it, that writes each result's evidence to `investigations/<name>/evidence/<result-id>.json` and compares the current state with it. `state.md` findings link to that file instead of holding checksums, and `awb-package` export checks run the comparison and record its output. Evidence, acquisition provenance, and publication files are fixed as JSON; the delivery manifest format stays open.
- `awb-package` ships a findings check, `awb_findings.py`, copied to `src/packaging/findings.py` on first use. `check()` reports backticked code, paths, file names, snake_case and dotted identifiers, commit SHAs, and caller-supplied internal names in `findings.md`; `awb-package` repairs the draft until it reports nothing, and `awb-release` runs it as part of verification.
- `check_text()` in the `awb-visualize` figure style lists image text that leaks identifiers, file names, `column = value` facet titles, or runs past 65 characters. `save_figure()` runs it and refuses to write a figure that fails.

### Removed

- The executive summary template and the journal template in `package-format/`. M365 Copilot distills the executive summary from `findings.md`; `findings-template.md` and `methodology-template.md` replace the journal.
- `add_caption()` from the `awb-visualize` figure style, since captions no longer go in the image.

## [0.2.0] - 2026-10-07

### Changed

- The export check in `awb-package` covers data as well as code: view definitions, the publications they read, input publication and acquisition checksums, and resolved settings must match the state recorded with the result. Each publication directory now holds a publication file with its inputs, conversion commit, and file checksums, and result evidence records those identities.
- The dirty-state comparison no longer contradicts itself: committed result code paths are compared with the producing commit, and paths recorded as uncommitted producing changes are compared with their recorded checksums.
- The validation checklist (columns, row counts, joins, nulls, scope, metrics, values) is an always-on requirement in the project `AGENTS.md`, recorded with each result's evidence and stated in the package journal.
- Investigation history and the package journal retain methodological mistakes that changed a finding or explain why an earlier conclusion was wrong; only routine debugging, coding mistakes, and abandoned attempts that changed no understanding are excluded.
- The two workbench skills are repackaged as five skills under the `awb-` prefix, so typing `awb-` in a host that lists skills as commands shows every workbench action. `workbench-init` and `workbench-package` no longer exist.
  - `awb-init` keeps project setup, investigation scoping, and scope changes, and now asks for a business question when none is given.
  - `awb-package` creates and revises a package's working draft only.
  - `awb-release` makes numbered releases when you mark a package delivered. It checks the revalidation flags current at release time, asks where released packages are kept, records that in the project README, and copies each release there when the location is reachable.
- The release archive unpacks to one folder, `analytics-workbench-skills/`, with the five `awb-*` skill folders at its top level beside `README.md`, `LICENSE`, `CHANGELOG.md`, and `docs/`. Earlier archives named the top folder after the checkout directory and nested the skills under `.agents/skills/`. The archive no longer carries the build script, `.gitignore`, or `CONTEXT.md`, which serve only the repository.
- Install instructions now say to unzip the archive anywhere and copy the five `awb-*` folders into the host's user-level skills directory. The v0.1.0 and v0.1.1 release notes said to unzip into the skills directory, which leaves the skills nested a level too deep for any host to find.

### Added

- `awb-status`: a read-only report of where the project stands, covering the active investigation, findings and revalidation flags, open issues, package and release state, and landed data and release storage, ending with the requests that fit right now.
- `awb-visualize`: principles, libraries, and style defaults for charts and tables that display inline in agent chat and survive pasting into a document, with a shared matplotlib and seaborn style file and image paths that hosts can display in chat.
- Landed-data retention. `data/raw/` is excluded from Git and a landed original often cannot be fetched again, so before the first landing the agent asks where landed originals are kept outside the checkout and records the answer on the project README's `Landed data is kept at` line. It copies each completed landing there when the location is reachable and records the retained copy for each acquisition in `foundation/sources.md`. `awb-status` reports landed data that exists only in the checkout.
- `awb-init` reports an instruction file, such as a `CLAUDE.md` in the project directory or above it, that the current host reads in place of the workbench `AGENTS.md`. It never creates or edits that file.
- MIT license (`LICENSE`).
- This changelog.
- Validation of acceptance scenarios 1 through 6 by isolated agents on fixture projects, recorded in the README. Every expected-behavior bullet passed.
- Instruction gaps those runs surfaced are closed: `awb-release` verifies structural rules before asking for revalidation dispositions and re-verifies the caveat rule afterwards; dispositions cover every place a conclusion is represented, including figures and dataset columns; the manifest template fixes field names that `awb-status` reads; the project `AGENTS.md` gives a default landing, provenance, retention, and publication layout and homes for acquisition and settings code; an expansion is scoped through `awb-init`; `awb-status` compares current flags with draft dispositions, handles repositories with no commits, and offers the next analytical step.
- README sections on requirements, host compatibility, and versioning. Requirements name the source of the `grilling` dependency (`skills/productivity/grilling` in [mattpocock/skills](https://github.com/mattpocock/skills), tested against release v1.3.1) and the Python packages `awb-visualize` assumes. Host compatibility covers where Claude Code and OpenAI Codex look for user-level skills, and when Claude Code reads a project `AGENTS.md`.

### Removed

- The migration of projects from the `workbench-init` and `workbench-package` names, drafted during the repackaging, was removed before release. No project had been created with an earlier release, so there is nothing to migrate.
- The knowledge vault (`awb-vault`, the project `AGENTS.md` vault section, and the vault specification) is removed from this release. Its current state is preserved on the `dev/knowledge-vault` branch for later work.

### Release notes

Ready to paste into the GitHub release for v0.2.0:

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

The skills now carry all the guidance an agent needs; nothing the agent relies on lives only in the repository's specification or design notes.

### Changed

- Drafts are working copies overwritten by the next revision, and the agent says that only marking one delivered preserves it.
- Corrections may stay in views. Materialized tables do not accumulate in a persistent DuckDB file except as a catalogued cache.
- A commit without retained inputs is not described as an exact rerun.
- Vault claims copied into a project are its fixed basis, and newer vault claims are checked before use.
- The instructions explain why other analyses' conclusions are read only after your own results exist.
- Exploration does not wait for cleaning, and canonical data is still checked for fit for each question.
- CLIs are optional, entry points stay small, and investigation composition code lives in `investigations/<name>/`.
- After setup, the agent says how work continues and that the vault fills only when you ask.

## [0.1.0] - 2026-10-02

First release.

### Added

- `workbench-init`: set up an analytics project, start investigations through a scoping interview that invokes the external `grilling` skill, and, on request, create a knowledge vault.
- `workbench-package`: create, revise, or explicitly release a delivery package.
- Project templates: the `AGENTS.md` workflow rules, project README, data foundation records (catalog, glossary, quality, sources), investigation records (brief, state, history), and delivery package formats including M365 assembly instructions.
- The knowledge vault, which carries knowledge about systems, databases, schemas, and tables from one project to the next through `WORKBENCH_VAULT`.
- The specification, design notes, and an archive build script that packages an explicit allowlist of tracked files.

[Unreleased]: https://github.com/quentin-hickam/analytics-workbench/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/quentin-hickam/analytics-workbench/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/quentin-hickam/analytics-workbench/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/quentin-hickam/analytics-workbench/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/quentin-hickam/analytics-workbench/releases/tag/v0.1.0
