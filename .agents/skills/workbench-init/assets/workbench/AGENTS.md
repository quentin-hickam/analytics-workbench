# Analytics workbench

This repository contains one shared data foundation and multiple investigations. Keep source knowledge, quality records, vocabulary, the catalog, and canonical SQL views in `foundation/`. Keep reusable executable preparation, analytical operations, and package assembly in `src/`. Keep each question's scope, settings, exploration, findings, and history in `investigations/<name>/`.

## Start or resume work

- Resume the active investigation linked from `README.md` unless the user names another one, and briefly identify it. Point that link at `investigations/<name>/state.md` when an investigation is created or the user switches. Read its `brief.md` and `state.md`; consult `history.md` when prior reasoning matters. If a request could belong to more than one investigation, ask before changing their records.
- The same ask about a broader population that contains the current population can remain the same investigation; a different question starts a new one, and an ambiguous boundary goes to the scoping interview. A related question about an independent population starts a new investigation with fresh state, history, and findings. Inherit the related investigation's method, settings, and package format as starting points, subject to the user's corrections; prior findings are context for method selection, not evidence about the new population.
- Invoke `workbench-init` to establish or repair the workbench structure, to start an investigation, or to resolve a consequential scope change. It owns the scoping interview and the investigation brief.

## Prepare and analyze data

- Let the active question bound preparation. Assess candidate sources only far enough to establish relevance and fitness, and record the assessment in `foundation/sources.md`. When a source is irrelevant, record why and stop there. Broader preparation requires an explicit request.
- Land every acquisition durably in `data/raw/` with provenance before canonical ingestion. CSV and JSON are valid landed formats. Keep completed landed originals unchanged so conversion can be retried, and keep incomplete acquisitions unpublished.
- Publish by converting landed originals into validated Parquet in `data/parquet/`, then exposing canonical DuckDB views. Write conversion output to an unpublished location, validate it, and publish it beside the files readers are using rather than over them. Each analytical process opens its own DuckDB session and loads the version-controlled SQL definitions in `foundation/views/`.
- Preparation owns reusable parsing, normalization, checks, and documented corrections; record limitations and correction rationale in `foundation/quality.md`. EDA consumes canonical data. Keep exploratory transformations in `investigations/<name>/exploration/` until a generally valid rule is deliberately promoted through preparation. Population choices, periods, filters, exclusions, and assumptions stay local to the investigation.
- Keep intermediate computation in canonical views and in-process results. Use `data/cache/` only for expensive, rebuildable results, each described in `foundation/catalog.md`. Audience-facing dataset exports selected for a delivery package are separate from intermediate computation.
- When a different backend is justified, preserve independent source landing and the preparation/EDA boundary. Add versioning, invalidation, or pipeline machinery only for a concrete project need.

## Write analytical code

- Put reusable normalization and correction code in `src/preparation/`; neutral measurements, comparisons, profiles, and graph operations in `src/exploration/`; and shared package assembly in `src/packaging/`. An investigation composes those operations through a thin layer of scope, settings, and selected operations.
- Group meaningful variation in named configuration with sensible defaults, and give distinct workflows distinct entry points. Reuse existing operations before adding new ones.
- Compute before interpreting. Preserve relevant results that challenge the expected explanation, and keep presentation logic out of neutral operations.
- Track all analytical code in Git. Record the producing commit, any uncommitted producing changes, input identifiers, and settings beside each result in the investigation records, and name unknown provenance explicitly, so packaging can distinguish the producing state from a later checkout.

## Maintain meaning and records

- Challenge ambiguous business and analytical terms, test proposed definitions with concrete cases, and compare them with source data and analytical logic. Record resolved shared meanings immediately in `foundation/glossary.md`, a brief explained local departure in the investigation's `brief.md`, population and period choices as settings, and dataset, view, and cache descriptions in `foundation/catalog.md`. These records replace `CONTEXT.md`, `CONTEXT-MAP.md`, and ADRs.
- Update `state.md` whenever current findings, unresolved issues, revalidation flags, or next steps change. Append to `history.md` whenever a meaningful finding, analytical decision, caveat, superseded conclusion, or relevant source limitation changes; its header defines what belongs there and what stays in Git history. Write an explicit checkpoint when the user requests one before switching investigations.
- When EDA reveals a shared data issue, assess the candidate correction locally. Once accepted as general, implement it through preparation, document it in the foundation, and flag every finding it may affect for revalidation with a reason. Affected analyses are rerun and conclusions revised only on request. Prior numbered releases stay unchanged.

## Package only on request

- Create or refresh a delivery package only when the user explicitly asks, by invoking `workbench-package`. Automatic record maintenance never triggers packaging or another ad hoc deliverable.
