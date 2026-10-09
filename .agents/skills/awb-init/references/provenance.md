# Result evidence helper

Call the project copy at `src/provenance.py`; its module docstring holds the full `awb-evidence/3` schema.

## Paste the printed row

A result that raises prints `{"result_id", "error"}` with the traceback on stderr, the other results still run, and `run.py` exits 1. Paste each `state_row` into the state's Current findings table, replacing the placeholder with the finding, or replacing the row that already links that evidence. The row keeps an existing row's finding text, starts `provisional`, and names failed and unassessed checks as its caveat. Understand failed checks before promoting the status.

The saved table under `results/` holds the computed values packaging later serializes. `results/` is output, not producing code. `run.py` deletes a result's evidence before rewriting its table, so a run that fails partway leaves no evidence rather than evidence for another table.

## Adapt what a result records

`run.py` records each result through `record_evidence()`. Set `views = [...]` in a result's settings when its producer reads views its queries do not name (detection errs toward recording a view). Producing code is `run.py`, the result's own `queries`, the investigation's other code, and `src/` except `awb.py`, `provenance.py`, and `packaging/`, which only dispatch, record, or package; another result's queries never make it stale. Pass `code_paths=[...]` in `run.py`'s `record_evidence` call to add producing code outside those, such as exploration SQL a producer reads. Unknown provenance is recorded as `{"unknown": reason}`.

Settings are recorded per result: `record_evidence()` refuses a settings file without the result's `[results.<id>]` table, and the evidence keeps only `[parameters]` and that table, compared by content alone. Adding or editing another result's table, or another top-level table such as `[eda]`, leaves the result current, while a change to `[parameters]` or its own table fails the `settings` comparison. Keep anything a result reads in `[parameters]` or its own table.

## Evidence comparison

`awb-package`'s `export` command and `python3 src/awb.py stale`, run `compare_evidence(root, evidence_path)`: five comparisons in order (`committed-code`, `uncommitted-code`, `views`, `inputs`, `settings`), each `{name, paths, outcome, detail}`. It compares state; it does not revalidate. It reads `awb-evidence/1`, `/2`, and `/3` files; the first two, and `/3` files written before settings were always scoped, record settings whole.
