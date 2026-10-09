# Analytics workbench

One data foundation serves every investigation here. Source knowledge, quality records, vocabulary, the catalog, and canonical SQL views belong in `foundation/`; reusable operations in `src/`; each question's scope, settings, exploration, findings, and history in `investigations/<name>/`.

## Start or resume

For investigation work, resume the investigation on README's `Active investigation` line unless the user names another, and name it briefly. Read its `brief.md` and `state.md`, and history entries when prior reasoning matters. When switching, repoint that line at the new `state.md`. When an ask could belong to several investigations, ask which before changing records.

Use the workbench skills for their work even when you start it yourself; take a consequential scope change, such as a broader or different population, through `awb-init`'s scoping interview.

## Procedures

- **Data**: before assessing a source, landing, retaining, or publishing data, editing `foundation/views/`, or adding a cache, read [workbench-guides/data.md](workbench-guides/data.md).
- **Analysis**: before adding or changing a result, recording a finding, or rerunning flagged findings, read [workbench-guides/analysis.md](workbench-guides/analysis.md).

Read each guide once per session. Existing project conventions win; surface any conflict for a decision.

## Commands

Run workbench helpers with `python3 src/awb.py <command>`; `--help` lists them and `<command> --help` their arguments. Compute through saved queries: run every query with `awb.py sql`, and counts, null rates, and distinct values with `awb.py profile`; save a query you run twice as `investigations/<name>/exploration/<topic>.sql` and rerun it by path. Run the project's helpers, customized or not, as black boxes; open one's source only to adapt or debug it. When a helper or package is missing, repair through `awb-init`. Keep complete records in files; in chat, report counts, paths, and helper failures verbatim.

## Analytical invariants

Let the active question bound preparation; broader preparation needs an explicit request. Keep exploratory transformations local to the investigation until deliberately promoted, and intermediate computation in views and in-process results.

Compute before interpreting: read other investigations' conclusions only after this investigation has its own results, unless the user asks otherwise. Preserve results that challenge the expected explanation.

Only a result from the investigation's `run.py`, run with its settings, can become a finding; present other query output as exploration. Understand and record each failed check before promoting a finding.

## Record maintenance

Settle ambiguous terms with concrete examples and the data. Record shared meanings in `foundation/glossary.md`, local departures in the brief, population and period choices in settings, and dataset, view, and cache descriptions in `foundation/catalog.md`; these replace context maps and ADRs.

Update `state.md` when findings, issues, flags, or next steps change; append to `history.md` when a finding becomes supported, is superseded, or changes its conclusion, or when a scope, method, caveat, or data limitation changes the investigation's understanding. Rerun flagged findings and revise conclusions only on request. When the user names who will read the deliverables, record it in the brief's Audience section.

Commit when the user asks; suggest one when analytical code is uncommitted, so evidence carries a SHA.

Answer in chat. Package files come only from `awb-package` and `awb-release`, on the user's request; numbered releases are frozen.
