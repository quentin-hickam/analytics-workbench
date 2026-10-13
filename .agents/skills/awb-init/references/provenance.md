# Result evidence helper

Call the project copy at `src/provenance.py`. Its module docstring holds the full `awb-evidence/3` schema.

## The findings row

A result that raises an exception prints `{"result_id", "error"}`, with the traceback on stderr. The other results still run, and `run.py` exits 1. Before `run.py` unlinks the evidence, it calls `prior_result()`. `prior_result()` captures the `evidence_commit()` citation. As the baseline, it also captures the sha256 of the saved table, with the checks and scoped settings of the evidence. After `record_evidence()`, `record_finding()` writes the one row of the result. Then `run.py` prints `state`, which is one of these values:

- `added` (a `provisional` placeholder row)
- `kept` (the baseline did not change, and nothing was written)
- `refreshed`
- `flag cleared`

A refreshed row becomes `provisional` unless it is superseded. A refreshed row gets a history entry when it was supported. A flagged row returns to `superseded` or `provisional`. It keeps its notes and drops its flag reason, and the history entry records that flag reason.

The `notes_checks` of each entry records the checks caveat that its notes were written against. `state finding` counts the notes as an explanation of failed or not-assessed checks only while `notes_checks` is equal to the current checks caveat. The `failed checks:` and `not assessed:` segments of the caveat are reserved for the writer. Other segments are notes from `awb.py state finding --caveat`.

`findings.json` (`awb-findings/1`) owns all four cells. Without the file, the table renders empty. For this reason, a row written by hand is drift. Writers refuse table drift, and `prior_result()` checks before a rerun removes evidence. `python3 src/awb.py state render --investigation <name>` restores the JSON table and prints the discarded rows. Apply intended edits again with `state finding`. Apply flags again with `state flag`, which reads a JSON list of `result` and `reason` on stdin. With `--check`, `state flag` validates and does not write. Only table rows are rendered. A row that is cut off below the table still counts as drift. `state issues` and `state next` never touch the table.

All temporary files are written first. Then findings, state, and history are replaced in that order, with signals deferred. New evidence is removed only if findings.json was not replaced. A failed state replacement names `state render`. A failed history replacement names its missing prior rows. A kill or a power loss between replacements can still leave the table behind findings.json (`state render` restores it), or lose the history entry. These risks are accepted instead of a recovery mechanism. `finding_row()` returns the row but does not write it.

The saved table under `results/` holds the computed values that packaging serializes later. `results/` is output, not producing code. `run.py` deletes the evidence of a result before it writes the table again. As a result, a run that fails partway leaves no evidence, not evidence for a different table.

## Adapt what a result records

`run.py` records each result through `record_evidence()`. If the producer of a result reads views that its queries do not name, set `views = [...]` in the settings of that result. (When detection is not certain, it records the view.) Producing code is:

- `run.py`
- the `queries` that belong to the result
- the other code of the investigation
- `src/`, except `awb.py`, `provenance.py`, and `packaging/`, which only dispatch, record, or package

The queries of another result never make a result stale. To add producing code outside these, pass `code_paths=[...]` in the `record_evidence` call of `run.py`. An example is exploration SQL that a producer reads. Unknown provenance is recorded as `{"unknown": reason}`.

Settings are recorded for each result. `record_evidence()` refuses a settings file that does not have the `[results.<id>]` table of the result. The evidence keeps only `[parameters]` and that table, and compares them by content alone. If you add or edit the table of another result, or another top-level table (for example `[eda]`), the result stays current. But a change to `[parameters]` or to the table of the result fails the `settings` comparison. Keep everything that a result reads in `[parameters]` or in its own table.

## Evidence comparison

The `export` command of `awb-package` and `python3 src/awb.py stale` run `compare_evidence(root, evidence_path)`. It does five comparisons in this order: `committed-code`, `uncommitted-code`, `views`, `inputs`, `settings`. Each comparison is `{name, paths, outcome, detail}`. It compares state. It does not revalidate. It reads only `awb-evidence/3` files whose settings name their result. Any other evidence fails all five comparisons, so rerun its result.
