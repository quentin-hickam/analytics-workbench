# Analytics workbench

One data foundation serves every investigation here. Source knowledge, quality records, vocabulary, the catalog, and canonical SQL views belong in `foundation/`. Reusable operations belong in `src/`. The scope, settings, exploration, findings, and history of each question belong in `investigations/<name>/`.

## Start or resume

For investigation work, run `python3 src/awb.py state` to resume the active investigation of README (`--investigation <name>` for another investigation). Name the investigation briefly. When prior reasoning is important, read the history. Switch with `state switch <name>`. If an ask can belong to several investigations, ask which one before you change records.

Use the workbench skills for their work, even when you start that work yourself. Take a consequential scope change (for example a broader or different population) through the scoping interview of `awb-init`.

## Procedures

- **Data**: before you assess a source, land, retain, or publish data, edit `foundation/views/`, or add a cache, read [workbench-guides/data.md](workbench-guides/data.md).
- **Analysis**: before you add or change a result, record a finding, or rerun flagged findings, read [workbench-guides/analysis.md](workbench-guides/analysis.md).

Read each guide one time in each session. Existing project conventions have priority. Report each conflict for a decision.

## Commands

Run workbench helpers with `python3 src/awb.py <command>`. `--help` lists the helpers, and `<command> --help` lists the arguments of a helper. Compute through saved queries:

- Run every query with `awb.py sql`.
- Compute counts, null rates, and distinct values with `awb.py profile`.
- If you run a query two times, save it as `investigations/<name>/exploration/<topic>.sql`, and rerun it by path.

Run the helpers of the project as black boxes, customized or not. Open the source of a helper only to adapt or debug it. When a helper or package is missing, repair through `awb-init`. Keep complete records in files. In chat, report counts, paths, and helper failures verbatim.

## Analytical invariants

Let the active question set the limits of preparation. Broader preparation needs an explicit request. Keep exploratory transformations local to the investigation until they are deliberately promoted. Keep intermediate computation in views and in-process results.

Compute before you interpret: read the conclusions of other investigations only after this investigation has its own results, unless the user asks otherwise. Keep results that challenge the expected explanation.

Only a result from the `run.py` of the investigation, run with its settings, can become a finding. Present other query output as exploration. Before you promote a finding, understand and record each failed check.

## Record maintenance

Settle ambiguous terms with concrete examples and the data. Record these items:

- Shared meanings in `foundation/glossary.md`.
- Local departures in the brief.
- Population and period choices in settings.
- Dataset, view, and cache descriptions in `foundation/catalog.md`.

These records replace context maps and ADRs.

`run.py` writes findings rows. Hand edits to the table are refused as drift. Change wording, status, or caveats with `awb.py state finding`, which writes each history entry that is due. Change issues and next steps with `state issues` or `state next`. Write history by hand only when a scope, method, caveat, or data limitation changes understanding. Rerun flagged findings and revise conclusions only on request. When the user names who will read the deliverables, record this in the Audience section of the brief.

Commit when the user asks. When analytical code is uncommitted, suggest a commit, so that evidence carries a SHA.

Answer in chat. Package files come only from `awb-package` and `awb-release`, on the request of the user. Numbered releases are frozen.
