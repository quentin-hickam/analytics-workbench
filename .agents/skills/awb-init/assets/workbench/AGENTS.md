# Analytics workbench

One data foundation serves every investigation here. Source knowledge and references, quality records, vocabulary, the catalog, and canonical SQL views belong in `foundation/`; reusable operations in `src/`; each question's scope, settings, exploration, findings, and history in `investigations/<name>/`.

## Start or resume

For investigation work, run `python3 src/awb.py state` to resume README's active investigation (`--investigation <name>` for another) and name it briefly; read history when prior reasoning matters. Switch with `state switch <name>`. When an ask could belong to several investigations, ask which before changing records.

Use the workbench skills for their work even when you start it yourself; take a new business question or a consequential scope change, such as a broader or different population, through `awb-scope`.

## Procedures

- **Data**: before assessing a source, landing, retaining, or publishing data, editing `foundation/views/`, or adding a cache, read [workbench-guides/data.md](workbench-guides/data.md).
- **Analysis**: before adding or changing a result, recording a finding, or rerunning flagged findings, read [workbench-guides/analysis.md](workbench-guides/analysis.md).

Read each guide once per session. Existing project conventions win; surface any conflict for a decision.

## Commands

Run workbench helpers with `python3 src/awb.py <command>`; `--help` lists them and `<command> --help` their arguments. Compute through saved queries: run every query with `awb.py sql`, and counts, null rates, and distinct values with `awb.py profile`; save a query you run twice as `investigations/<name>/exploration/<topic>.sql` and rerun it by path. Run the project's helpers, customized or not, as black boxes; open one's source only to adapt or debug it. When a helper or package is missing, repair through `awb-init`. Keep complete records in files; in chat, report counts, paths, and helper failures verbatim.

## Analytical invariants

Let the active question bound preparation; broader preparation needs an explicit request. Keep exploratory transformations local to the investigation until deliberately promoted, and intermediate computation in views and in-process results.

Compute before interpreting: read other investigations' conclusions only after this investigation has its own results, unless the user asks otherwise. Preserve results that challenge the expected explanation.

Only a result from the investigation's `run.py`, run with its settings, can become a finding; present other query output as exploration. Understand and record each failed check before promoting a finding. Word a finding no more strongly than its Claim in `state.md`: an association never drives, causes, or leads to anything.

## Record maintenance

Settle ambiguous terms with concrete examples and the data. Record shared meanings in `foundation/glossary.md`, local departures in the brief, population and period choices in settings, and dataset, view, and cache descriptions in `foundation/catalog.md`; these replace context maps and ADRs.

`run.py` writes findings rows; hand edits to the table are refused as drift. Change wording, status, claim strength, or caveats with `awb.py state finding`, which writes any history entry due, and issues and next steps with `state issues` or `state next`. Unresolved issues hold data problems and blockers, Next steps actions; a question raised in the work goes in the investigation's ledger with `awb.py questions add`, and an answer the user gives with `questions answer`. A data question is answered only by a result whose settings table declares it. Write history by hand only when a scope, method, caveat, or data limitation changes understanding. Rerun flagged findings and revise conclusions only on request. When the user names who will read the deliverables, record it in the brief's Audience section.

Commit when the user asks; suggest one when analytical code is uncommitted, so evidence carries a SHA.

Answer in chat. Package files come only from `awb-package` and `awb-release`, on the user's request; numbered releases are frozen. When the user corrects a package draft while reviewing it, take the correction through `awb-package`, which first appends a correction later drafts could repeat to `foundation/review-rules.md` as a numbered rule that every later review checks.
