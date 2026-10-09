# Analytical implementation, validation, and evidence

Paths are relative to the workbench root. Follow the universal analytical and record rules in `AGENTS.md`; this guide supplies implementation procedures.

## Structure and execute

Use `src/preparation/` for acquisition, landing, conversion, session loading, normalization, and corrections; `src/exploration/` for neutral measurements, comparisons, profiles, and graph operations; and `src/packaging/` for shared package assembly. Keep presentation logic out of neutral operations.

Each investigation has its own runnable composition entry and one named settings file in the project's configuration format (`settings.toml` by default). This thin layer selects shared operations and supplies scope and settings. Group meaningful variation in named configuration with sensible defaults; give distinct workflows distinct entry points. Reuse existing operations first. A CLI is optional and exposes only the controls its task needs.

Save repeated queries as `investigations/<name>/exploration/<topic>.sql` and run them with `python3 src/awb.py sql <path>`, which opens a fresh DuckDB session containing canonical views, prints the first rows and the row count, and writes the full result with `--out`; pass SQL text in place of the path for a one-off query. Do not write Python snippets to run queries. The composition entry imports the project's `session()` helper and executes saved queries by path; for its interface, consult the installed `awb-init` skill's `references/landing.md`. Load [data procedures](data.md) before changing shared preparation, view definitions, or publications.

Use one project helper per repeated operation, including landing, publication, retention, evidence, validation, sessions, manifest inventory, and state comparison. Regenerate helpers only to change behavior. Computation performed ad hoc remains exploration until reproduced by the composition entry.

## Validate results

Read the installed `awb-init` skill's `references/validation.md` for setup, the `profile` command, `profile()` and `validate(frame, spec)` interfaces, and examples. Copy the supplied helper to `src/exploration/validate.py` only if missing; preserve customized copies and import from the project. Non-Python projects port its interface and check record.

Run four mechanical checks: required columns; plausible counts before and after each filter; joins without unexpected multiplication, inspecting key uniqueness whenever counts change; and missing-value rates for important fields. For counts, null rates, and distinct values, run `python3 src/awb.py profile <view | query.sql | "SQL"> --out <path>.json` rather than ad hoc counting queries or snippets; it saves the full `profile()` result and prints a per-column summary. The composition entry calls `profile()` and `validate()` directly.

Supply three judgment checks to `validate()` as outcomes with one-sentence details: scope (explicit date filters and grouping dimensions), metrics (definitions, assumptions, and column meanings), and values (inspect distinct values that drive business interpretation). Omitted judgments are not assessed, not passes. Retain the returned check list unchanged with the result's evidence.

## Record evidence and rerun

Read the installed `awb-init` skill's `references/provenance.md` before recording evidence or comparing producing state. Copy its helper to `src/provenance.py` only if missing; preserve customized helpers and import the project copy. Non-Python projects port the interface and file format.

Call `record_evidence()` for each result. It writes `investigations/<name>/evidence/<result-id>.json` with producing commit, uncommitted producing-file checksums, input publications and acquisitions and their recorded checksums, view definitions and checksums, resolved settings, and validation checks. Name unknown provenance with its reason. Before a first commit, record `uncommitted` and producing-file checksums; suggest a commit so later results carry a SHA. This evidence distinguishes the producing state from a later checkout.

Assess candidate shared-data corrections locally; implement accepted general corrections through preparation and document them in the foundation. For an authorized rerun, execute the composition entry with its settings and record each result's evidence through `record_evidence()`. If that entry cannot reproduce a flagged finding, extend it first.

Inspect helper implementations only for adaptation or debugging. Save complete profiles, checks, and evidence in files; surface relevant failures, concise findings, and paths in chat.
