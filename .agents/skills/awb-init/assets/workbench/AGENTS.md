# Analytics workbench

This repository shares one data foundation across multiple investigations. Source knowledge, quality records, vocabulary, the catalog, and canonical SQL views belong in `foundation/`; reusable executable operations in `src/`; each question's scope, settings, exploration, findings, and history in `investigations/<name>/`.

## Start or resume

Resume the active investigation linked from `README.md` unless the user names another, and briefly identify it. Read its `brief.md` and `state.md`; read relevant history entries when prior reasoning matters. Point the README's `Active investigation` link at the investigation's `state.md` when creating or switching investigations. Ask before changing records when an ask could belong to several investigations.

Use `awb-init` to establish or repair structure, start an investigation, or resolve a consequential scope change. The same ask about a broader population containing the current population expands the existing investigation and reopens only affected decisions. A related question about an independent population starts a new investigation with fresh findings, state, and history; inherit method, settings, and package format as starting points subject to correction. Prior findings guide method selection, not evidence about the new population. Use `awb-status` for status and possible next requests.

## Load the relevant procedures

- Before assessing sources, acquiring or retaining data, configuring canonical sessions, changing preparation or publication, or adding a cache, read [data procedures](workbench-guides/data.md).
- Before writing analytical code, presenting any result, recording a finding, or correcting shared data and revalidating findings, read [analysis procedures](workbench-guides/analysis.md).
- Whenever producing a chart, figure, diagram, or formatted results table, invoke `awb-visualize`.

Read only the procedures needed for the current work. Once loaded, reuse their context until a relevant change requires rereading. Preserve existing project conventions; resolve conflicts explicitly instead of overwriting customized records or code.

## Analytical invariants

Let the active question bound preparation; broader preparation requires an explicit request. Check source coverage and limitations against each investigation. Land complete acquisitions with provenance before canonical ingestion, preserve originals, and publish only validated outputs. Keep preparation reusable and exploratory transformations local until deliberately promoted. Intermediate computation belongs in canonical views and in-process results; materialized caches require a recorded purpose.

Compute before interpreting. Apart from related findings used to select methods, read other investigations' or projects' conclusions only after this investigation produces its own results unless the user requests otherwise. Preserve results that challenge the expected explanation.

Only an investigation's composition entry run with its settings can produce a finding. Validate every result before presentation or recording; retain the complete checks with its evidence, and understand and record failures before promoting a finding. Track analytical code in Git and record producing state, input provenance, views, settings, and validation through the project evidence helper. Reuse helpers and save queries or checks executed a second time for rerunning by path.

## Maintain records and delivery boundaries

Resolve ambiguous terms with concrete examples and available data. Record shared meanings in `foundation/glossary.md`, local departures in the brief, population and period choices in settings, and dataset/view/cache descriptions in `foundation/catalog.md`; these replace separate context maps and ADRs.

Update `state.md` when findings, issues, revalidation flags, or next steps change. Append meaningful findings, decisions, caveats, superseded conclusions, and relevant source limitations to history according to its header. Write a checkpoint before switching investigations when requested. Accepted shared corrections flag every potentially affected finding with a reason while preserving its prior status; rerun affected analyses and revise conclusions only on request.

When the user says who will read the delivered documents, record it in the Audience section of the investigation's `brief.md`.

Create or refresh delivery packages only on explicit request through `awb-package`. Preserve numbered releases unchanged; create one only when the user explicitly marks the package delivered through `awb-release`. Routine record maintenance never triggers packaging or an ad hoc deliverable.
