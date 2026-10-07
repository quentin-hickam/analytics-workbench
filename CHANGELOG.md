# Changelog

All notable changes to this project are recorded in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Each release is a Git tag `vX.Y.Z` with the zip archive attached to its GitHub release.

## [Unreleased]

### Changed

- The project `AGENTS.md` names the investigation's composition entry as the only producer of a finding. A rerun of flagged findings runs the entry with its settings file and records evidence instead of rebuilding the analysis in chat, and `awb-status` routes "Rerun the flagged findings" to it. A query run a second time is saved under the investigation's `exploration/` or promoted to a view and rerun by path; profiling goes through the shared `profile()` operation.

### Added

- `awb-package` ships a manifest helper, copied to `src/packaging/manifest.py` on first use, that builds the manifest `inventory`, verifies a draft against it, and compares a release with its storage copy. `awb-package` and `awb-release` now run it instead of hashing and comparing files by hand.

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

[Unreleased]: https://github.com/quentin-hickam/analytics-workbench/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/quentin-hickam/analytics-workbench/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/quentin-hickam/analytics-workbench/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/quentin-hickam/analytics-workbench/releases/tag/v0.1.0
