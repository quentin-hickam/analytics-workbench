# Analytics workbench

This repository contains one shared data foundation and multiple investigations. Keep source knowledge, quality records, vocabulary, the catalog, and canonical SQL views in `foundation/`. Keep reusable executable preparation and analytical operations in `src/`. Keep each question's scope, settings, exploration, findings, and history in `investigations/<name>/`.

## Start or resume work

- Resume the active investigation named in `README.md` unless the user names another one, and briefly identify it. Update that pointer when an investigation is created or the user switches investigations. Read its `brief.md` and `state.md`; consult `history.md` when prior reasoning matters. If a request could belong to more than one investigation, ask before changing their records.
- A broader population that contains the current population can remain the same investigation. A related question about an independent population starts a new investigation with fresh state, history, and findings. Inherit the related investigation's method, settings, and package format as starting points, subject to the user's corrections; prior findings are context for method selection, not evidence about the new population.
- Use `workbench-init` to establish or repair the workbench structure. Invoke `grilling` directly when establishing an investigation's question and scope or resolving a consequential scope change. Ask one decision question at a time, recommend an answer, preserve settled answers, and ask only about choices that materially affect the analysis. Resolve repository and data facts yourself. Do not interview the user about routine implementation choices.
- At investigation creation, record the question, population or scope, intended decision or exploratory purpose, usefulness criteria, and material unknowns in `investigations/<name>/brief.md`.

## Prepare and analyze data

- Let the active question bound preparation. Assess candidate sources only far enough to establish relevance and fitness. Record the assessment in `foundation/sources.md`; when a source is irrelevant, record why and stop preparing it. Broader preparation requires an explicit request.
- Land every acquisition independently and durably in `data/raw/` with provenance before canonical ingestion. CSV and JSON are valid landed source artifacts. Retain completed landed originals unchanged so conversion can be retried; keep incomplete acquisitions unpublished.
- The default publication path is landed originals to validated Parquet in `data/parquet/`, then canonical DuckDB views. Write conversion output to an unpublished location, validate it, and publish it without overwriting files used by readers. Each analytical process owns its DuckDB session and loads the version-controlled SQL definitions in `foundation/views/`; do not depend on a shared writable DuckDB file.
- Preparation owns reusable parsing, normalization, checks, and documented corrections. Record limitations and correction rationale in `foundation/quality.md`. EDA consumes canonical data. Keep exploratory transformations in `investigations/<name>/exploration/` until deliberately promoting a generally valid rule through preparation. Keep population choices, periods, filters, exclusions, and assumptions local to the investigation.
- Prefer canonical views and in-process computation. Use `data/cache/` only for expensive, rebuildable results and describe each deliberate cache in `foundation/catalog.md`. Do not use intermediate CSV exports between analytical steps. Audience-facing dataset exports selected for a delivery package are separate.
- When a different backend is justified, preserve independent source landing and the preparation/EDA boundary. Avoid inventing a versioning, invalidation, or pipeline system without a concrete project need.

## Write analytical code

- Build cohesive modules with small, explicit interfaces. Put reusable normalization and correction code in `src/preparation/`. Put neutral reusable measurements, comparisons, profiles, graph operations, and similar computations in `src/exploration/`. An investigation should provide a thin composition layer for scope, settings, and selected operations.
- Group meaningful variation in named configuration with sensible defaults. Use distinct entry points for distinct workflows rather than a universal CLI with a sprawling option surface. Reuse existing operations and avoid speculative frameworks.
- Compute before interpreting. Preserve relevant results that challenge the expected explanation, and keep presentation logic out of neutral operations.
- Track all analytical code in Git. Record the producing commit, any uncommitted producing changes, input identifiers, and settings with result evidence in investigation records. Packaging must be able to distinguish that producing state from a later checkout; identify unknown provenance explicitly.

## Maintain meaning and records

- Challenge ambiguous business and analytical terms, test proposed definitions with concrete cases, and compare them with source data and analytical logic. Record resolved shared meanings immediately in `foundation/glossary.md`. Record a brief, explained local departure in the investigation's `brief.md`; record population and period choices as settings. Describe datasets, views, and caches in `foundation/catalog.md` rather than the glossary.
- Use these analytics records instead of `CONTEXT.md`, `CONTEXT-MAP.md`, ADRs, or the unmodified `domain-modeling` skill.
- Automatically update `state.md` when current findings, unresolved issues, revalidation flags, or next steps change. Append to `history.md` when a meaningful finding, analytical decision, caveat, superseded conclusion, or relevant source limitation changes. Preserve an explicit checkpoint when the user requests one before switching investigations.
- Retain source-data errors and limitations that affected the work. Exclude our analytical approach mistakes, coding or execution mistakes, discarded false starts, and routine debugging; Git records code evolution.
- When EDA reveals a shared data issue, assess the candidate correction locally. Once accepted as general, implement it through preparation, document it in the foundation, and flag every finding it may affect for revalidation with a reason. Do not rerun affected analyses or rewrite conclusions automatically. Leave prior numbered releases unchanged.

## Package only on request

- Create or refresh a delivery package only when the user explicitly asks; invoke `workbench-package`. Automatic record maintenance never triggers packaging or another ad hoc deliverable.
- Dataset selection, manifest provenance, revalidation checks, and package revision mechanics belong to `workbench-package`. Maintain one stable named package and one working `draft/`; create an immutable numbered directory under `released/` only at an explicit delivery milestone. Packaging does not rerun analysis.
- Keep the package narrative complete and authoritative. M365 only formats its Markdown and selected datasets into Word or Excel; substantive revisions stay in the workbench.
