# Result evidence helper

Call the project copy at `src/provenance.py`; its module docstring holds the full `awb-evidence/3` schema.

## Paste the printed row

A result that raises prints `{"result_id", "error"}` with the traceback on stderr, the other results still run, and `run.py` exits 1. Paste each `state_row` into the state's Current findings table, replacing the placeholder with the finding, or replacing the row that already links that evidence. The row keeps an existing row's finding text, starts `provisional`, and names failed and unassessed checks as its caveat. Understand failed checks before promoting the status.

The saved table under `results/` holds the computed values packaging later serializes. `results/` is output, not producing code; the evidence default excludes it.

## Adapt what a result records

`run.py` records each result through `record_evidence()`. Set `views = [...]` in a result's settings when its producer reads views its queries do not name (detection errs toward recording a view). Pass `code_paths=[...]` in `run.py`'s `record_evidence` call when producing code lies outside `src/` and the investigation's own files, such as exploration SQL the entry reads. Unknown provenance is recorded as `{"unknown": reason}`.

Settings are recorded per result. When `settings.toml` has a `[results]` table holding the result's ID, the evidence keeps only `[parameters]` and that result's own `[results.<id>]` table, and the file is compared by that content alone: adding or editing another result's table, or another top-level table such as `[eda]`, leaves the result current, while a change to `[parameters]` or its own table fails the `settings` comparison. A settings file without that layout is recorded and compared whole. Keep anything a result reads in `[parameters]` or its own table.

## Evidence comparison

`awb-package`'s `export` and `draft-provenance` commands, and `python3 src/awb.py stale`, run `compare_evidence(root, evidence_path)`: five comparisons in order (`committed-code`, `uncommitted-code`, `views`, `inputs`, `settings`), each `{name, paths, outcome, detail}`. It compares state; it does not revalidate. It reads `awb-evidence/1`, `/2`, and `/3` files; the first two record settings whole.
