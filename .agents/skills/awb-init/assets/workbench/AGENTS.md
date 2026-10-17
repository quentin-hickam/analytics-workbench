# Analytics workbench

`foundation/` holds the data foundation every investigation shares, `src/` reusable operations, and `investigations/<name>/` each question's records.

## Start or resume

For investigation work, resume README's active investigation with `python3 src/awb.py state` (`--investigation <name>` for another) and name it; read history when prior reasoning matters. Switch with `state switch <name>`. When an ask could belong to several investigations, ask which before changing records.

Use the workbench skills even for work you start; take a new business question or a consequential scope change through `awb-scope`.

## Procedures

- **Data**: before assessing a source, landing, retaining, or publishing data, editing `foundation/views/`, or adding a cache, read [workbench-guides/data.md](workbench-guides/data.md).
- **Analysis**: before adding or changing a result, recording a finding, or rerunning flagged findings, read [workbench-guides/analysis.md](workbench-guides/analysis.md).

Read each guide once per session. Existing project conventions win; surface conflicts for a decision.

## Commands

When the host offers the `awb` MCP server, use its tools for `awb.py` commands, and the CLI otherwise: `read` for reads; `records`, `data`, `package`, and `release` for writes. Route `investigations/<name>/run.py` through `run`; `collect_status.py` through `read` command `status`; `eda_scan.py` through `data` command `eda-scan`, or `--show` through `read` command `eda-show`; `scan_dataset.py` through `data` command `clean-scan`; `record_cleaning.py` through `records` command `clean-record`; and `install_helpers.py` through `setup`. Each tool's description lists its commands. Pass the absolute project root as `project` on every call.

If a write tool is refused or unavailable, run its CLI command, keep using the tools that work, and say so once. Skill scripts run by path, never as `awb.py` commands.

In every workbench command, `python3` means README's `Project interpreter`. Run workbench helpers with `python3 src/awb.py <command>`; `--help` lists them. Compute through saved queries: run every query with `awb.py sql`, and counts, null rates, and distinct values with `awb.py profile`; save a query you run twice as `investigations/<name>/exploration/<topic>.sql` and rerun it by path. Run helpers as black boxes; open one's source only to adapt or debug it. Repair a missing helper or package through `awb-init`.

## Conversation

Records keep precise terms; chat uses plain words: ledger rows are questions, findings are what we found, flagged findings await recheck, limitations are caveats, and a disposition is the decision on <finding>. An ID such as `Q-007` may sit beside plain text, never replace it. Summarize helper output, quoting it only for a failure or on request. Answer in chat, giving file paths; never say a file was attached or sent.

When you need the user, ask in that message for a plain decision, with your recommendation and the alternative; never send them to a skill or instruction file. Report an environment or tool limit only when it affects the user: whether they must act, and what the workbench does instead.

A turn that changed workbench records ends with one plain line: what changed for the user's questions, the ledger's roots, if anything, and the next step; other turns have none. For example: Your five questions: 3 answered, 2 open · next: explore the March extract.

## Analytical invariants

The active question bounds preparation, and exploratory work stays in the investigation until deliberately promoted; broader preparation needs an explicit request.

Compute before interpreting: read other investigations' conclusions only once this one has results, unless asked. Preserve results that challenge the expected explanation, and offer an untested explanation as a question, not an answer.

Only a result from the investigation's `run.py`, run with its settings, can become a finding; present other query output, saved queries' too, as exploration. Record what the user recalls as their statement, not as confirmed, and name what a comparison leaves uncontrolled when a decision rests on it. Word a finding no more strongly than its Claim in `state.md`: an association never drives, causes, or leads to anything.

## Record maintenance

Settle ambiguous terms with concrete examples and the data. Record shared meanings in `foundation/glossary.md`, local departures in the brief, population and period choices in settings, and dataset, view, and cache descriptions in `foundation/catalog.md`; never in context maps or ADRs.

Change findings, issues, and next steps with `awb.py state finding`, `state issues`, and `state next`; record a question the work raises with `questions add --parent <question it serves>`, and the user's answer with `questions answer`. Write history by hand only when a scope, method, caveat, or data limitation changes understanding. Rerun flagged findings and revise conclusions only on request. Record a reader the user names in the brief's Audience section.

Commit when asked; when README's `Commits:` line says `as I go`, which you set when asked, also commit analytical code as you go. Otherwise suggest one at most once a session while analytical code is uncommitted. While README's `Code history:` line says `none`, make and suggest no commits.

Package files come only from `awb-package` and `awb-release`, on the user's request; numbered releases are frozen. Take a user's correction to a package draft through `awb-package`, which offers to keep one later drafts could repeat in `foundation/review-rules.md`.
