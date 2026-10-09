# Result evidence helper

If the project lacks `src/provenance.py`, copy [awb_provenance.py](../assets/awb_provenance.py) there. Preserve an existing customized helper and import the project copy. The helper uses Python 3.10+ and the standard library; parsed TOML settings require `tomllib` (Python 3.11+). A non-Python project ports the same interface and `awb-evidence/2` format.

## Produce and record results

Run the investigation's composition entry; do not write recording snippets. `python3 investigations/<name>/run.py [result-id ...]` produces every result in `settings.toml`, or the named ones, in one call. For each result it runs the result's saved queries in a fresh `session()` of canonical views, validates the frame with `validate()`, saves the table to `results/<result-id>.csv` and its profile to `results/<result-id>.profile.json`, records evidence through `record_evidence()`, and prints one JSON line:

```json
{"result_id": "orders-by-month", "rows": 6, "failed_checks": [], "not_assessed": ["joins"], "evidence": "investigations/order-quality/evidence/orders-by-month.json", "table": "investigations/order-quality/results/orders-by-month.csv", "profile": "investigations/order-quality/results/orders-by-month.profile.json", "state_row": "| <state the finding from orders-by-month> | [orders-by-month](evidence/orders-by-month.json) | provisional | not assessed: joins |"}
```

A result that raises prints `{"result_id", "error"}` with the traceback on stderr, the other results still run, and the entry exits 1. Paste `state_row` into the state's Current findings table, replacing the placeholder with the finding, or replacing the row that already links that evidence. The row keeps an existing row's finding text, starts `provisional`, and names failed and unassessed checks as its caveat. Understand failed checks before promoting the status.

A new investigation starts from the skeleton [run.py](../assets/workbench/investigation/run.py) and [settings.toml](../assets/workbench/investigation/settings.toml). A result is a `[results.<result-id>]` table in settings plus its query in `queries/<result-id>.sql`. Settings hold the query parameters (`[parameters]`, read in SQL as `$name`), the validation spec (`[results.<result-id>.validation]`), and the three judgments with explicit outcome and detail; an omitted judgment is recorded as not assessed. Add a producer to `run.py` only when a result needs more than its query, such as a count before a filter for `row_counts`; it returns the frame and the run-time spec entries. Keep reusable operations in `src/`.

The saved table holds the computed values packaging later serializes. `results/` is output, not producing code; the evidence default excludes it.

## Record a produced result

`record_evidence(root, investigation, result_id, *, views, publications=None, acquisitions=None, settings_path, checks, notes=None, code_paths=None) -> Path` writes the full evidence atomically at `investigations/<investigation>/evidence/<result_id>.json`, replacing that result ID's previous record. The composition entry calls it after producing and validating the result.

Use project-relative paths for views, input directories, settings, and code; paths must remain within the project. `investigation` and `result_id` are simple identifiers starting with an alphanumeric character and continuing with alphanumerics, `.`, `_`, or `-`. Omitted `publications` are the `data/parquet/<dataset>/<publication>` directories the views read; omitted `acquisitions` are the `data/raw/<source>/<acquisition-id>` inputs recorded in those publications' `publication.json`. Explicit lists are recorded as given; supply them when a result reads data outside its views. `checks` is the unchanged validation list of `{name, outcome, detail}` strings. `settings_path=None` records unknown settings, not an empty known configuration. Settings parsing is TOML; projects with another configuration format adapt the project helper to record their resolved settings.

`views_read(root, sql_paths, *, views_dir='foundation/views') -> list[str]` returns the view files that SQL files read, including the view files those views read. A view file defines the names in its `CREATE VIEW` and `CREATE TABLE` statements, and a name counts as read where `FROM`, `JOIN`, or a comma precedes it, so detection errs toward recording a view. The entry passes its result's query files; settings `views` replaces detection for a result whose producer reads views its queries do not name.

`code_paths` accepts producing files or directories. Its default covers `src` and investigation files while excluding brief/state/history and the evidence, exploration, and results directories (and `figures/` in older layouts). Supply explicit paths when producing code lies outside that default, including saved exploratory SQL consumed by the composition entry.

The file preserves producing commit and uncommitted-file hashes, view definitions, publications, acquisitions, resolved settings, checks, and notes. `compare_evidence` also reads `awb-evidence/1` files written before figures left the workbench, ignoring their figure entry. Unknowns are `{"unknown": "reason"}`. Data hashes are copied from acquisition/publication metadata during recording and checked against files during comparison. Before a first commit, evidence records `uncommitted` and producing-file hashes; suggest a commit so later results carry a SHA. Track analytical code in Git.

`finding_row(root, investigation, result_id, checks, *, finding=None, status='provisional') -> str` returns the Current findings row the entry prints. `finding_rows(state_path) -> dict` maps each result ID to the state rows, as text, that link its evidence file.

## Find stale findings

`python3 src/awb.py stale [--investigation NAME]` compares every `investigations/*/evidence/*.json` file, plus any evidence a state row links that is missing, with the current project, and changes nothing. It prints one JSON object:

```json
{"checked": 4, "stale": 1, "skipped": [], "results": [{"investigation": "order-quality", "result_id": "orders-by-month", "evidence": "investigations/order-quality/evidence/orders-by-month.json", "failed": [{"name": "views", "detail": "foundation/views/01_orders.sql: sha256 differs; foundation/views/01_orders.sql: publications differ."}], "findings": ["| Orders peak in March | [orders-by-month](evidence/orders-by-month.json) | supported | |"]}]}
```

`results` lists only results with a failing comparison, each with the failing comparisons (details shortened to three mismatches) and the exact state rows that link the evidence, ready for an edit that flags them. An empty list means every recorded result matches the current state. JSON files in an evidence directory that are not evidence, such as saved export checks, are listed under `skipped`.

Run it after an accepted shared correction to flag exactly the affected findings, and before a rerun to choose the result IDs to pass to the entry. A rerun records fresh evidence, after which `stale` no longer lists those results.

## Compare before an export

`compare_evidence(root, evidence_path) -> list[dict]` returns five ordered comparisons: `committed-code`, `uncommitted-code`, `views`, `inputs`, `settings`. Each contains `name`, `paths`, `outcome` (`pass` or `fail`), and `detail`. Save the complete list and carry it unchanged into the package manifest's `export_checks`. This is a state comparison, not renewed analytical validation. Failed or missing evidence blocks the export under `awb-package`.

Use the package's existing audit location for comparison output during packaging. Read failure details as needed without dumping complete file inventories into chat. `file_checksums(paths, *, root=None)` supports inventories: it returns `{path, bytes, sha256}` entries in input order, with null size/digest for missing files. Store full inventories on disk and surface counts, discrepancies, and their paths.

For package inventories and draft/release verification, use the [manifest helper interface](../../awb-package/references/manifest-helper.md).
