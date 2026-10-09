# Landing helper

The [installer](../scripts/install_helpers.py) places this helper at `src/preparation/landing.py` and restores it when missing; run it, never copy by hand. Preserve a customized helper and call the project copy. Run examples from the project root with its `src` importable. Replace illustrative paths and identifiers with the actual source and acquisition. Follow the project's acquisition, retention, and publication rules before calling these interfaces.

## Acquire and publish

Run the commands from the project root; `src/awb.py` passes them the root, and each prints one line of compact JSON. Exit status 0 means done, 1 means something attempted failed (named in the JSON), and 2 means unusable arguments with nothing changed.

Land files the user supplies or that are already downloaded with one command:

```
python3 src/awb.py land <source> <acquisition-id> <file-or-directory>... [--request TEXT] [--records NAME=COUNT ...] [--notes TEXT]
```

Each input is copied byte for byte under its own name through `land()`; relative input paths resolve from the current directory. Put options after the inputs. `--request` records the source version, query, or request and defaults to the copied paths. `--records` gives a landed file's record count by its path inside the acquisition. When README's `Landed data is kept at` line names a reachable filesystem path, the command runs `retain()`. It then writes the acquisition's Acquisitions row in `foundation/sources.md` (acquired at, request, landed directory, retained copy, integrity summary, and `--notes`) and sets a `candidate` source to `acquired`; fill Restrictions yourself. The output has `landed`, `files`, `bytes`, `retention`, and `ledger`. `retention` is the `retain()` result, or `skipped` (`unrecorded`, `none chosen`, `not a filesystem path`, or `unreachable`) with a `warning` to act on. `ledger` has `row` (`added`, or `not written` with the `error`) and `source_status`; `missing` means the source still needs its Sources row. Exit status 1 means the acquisition landed but its retention or row failed.

For an API or other fetched source, call `land()` from a script with a `fetch` callable, then run `python3 src/awb.py retain` to retain the acquisition and write its row.

`land(root, source, acquisition_id, fetch, *, request, records=None, notes=None) -> Path` calls `fetch(partial_directory)`. The callback writes every original file and raises on incomplete acquisition; its return value is ignored. `request` and `notes` must be JSON serializable. `records` maps relative filenames to integer counts; omitted counts become null. `provenance.json` is reserved. Completed files are hashed, provenance is written, and the directory is renamed from `.partial` only on success.

Publish with a saved SELECT over the landed files, for example `src/preparation/orders.sql`, and an optional check query (requires `duckdb`):

```
python3 src/awb.py publish <dataset> <publication-id> --from <acquisition-dir>... --sql <select.sql> [--check <check.sql>] [--notes TEXT]
```

The select reads landed files by project-relative path, such as `read_csv('data/raw/orders/received-001/orders.csv')`, which resolve against the project root from any directory. `--from` names, project-relative, exactly the acquisition directories the select reads; the command refuses a mismatch so `publication.json` lists the true inputs. SQL file paths are project-relative or absolute. The select's result is written with `COPY ... TO` as `<dataset>.parquet` in the partial publication directory, through `publish()`. The check reads that output as the view `publication`, can also read landed files, and returns failing rows; any row refuses publication. A select returning no rows is refused too. For example, `src/preparation/orders-check.sql`:

```sql
SELECT * FROM publication WHERE order_id IS NULL OR amount < 0
```

`publication.json` notes record both SQL paths, their SHA-256 values, the row count, and `--notes` as `comment`. Commit the SQL first so `conversion_commit` holds it; the output carries a `warning` otherwise. On success the output has `published`, `rows`, `bytes`, `inputs`, `conversion_commit`, and `catalog_row`: a `foundation/catalog.md` row to complete with grain and availability, then add or use to update the dataset's existing row. On failure it has `published: false`, the `error`, `failing_rows` with up to 20 of them under `first`, and the `partial` directory left behind.

For a conversion a select cannot express, call `publish()` with a `convert` callable.

`publish(root, dataset, publication_id, convert, *, acquisitions, validate=None, notes=None) -> Path` calls `convert(partial_directory)`, then `validate(partial_directory)`. Supply validation for publication: raise on failure or return the Python boolean `False`; every other return value permits publication. `acquisitions` lists completed acquisition directories, absolute or project-relative. Conversion reads them without modification. `publication.json` is reserved; the helper records inputs, hashes, and Git HEAD (or `uncommitted`), then renames the output directory.

Both helpers refuse existing final or partial destinations. Failures leave an unpublished partial directory; resolve it deliberately before retrying. Source, dataset, and run identifiers are single directory names, excluding `.`, `..`, and names ending in `.partial`.

## Retain and query

`python3 src/awb.py retain` retains, at README's recorded location, every completed acquisition whose Acquisitions row has no retained copy or that has no row, and writes or updates those rows. Run it when a location is first recorded or changed, and after a library `land()`. Without a reachable filesystem location it only writes missing rows. The output has `location` (or the skip reason), `acted_on` with each acquisition's retention result and row outcome, `already_retained`, and `still_this_checkout_only`.

`retain(root, acquisition_dir, location) -> dict` copies to `<location>/data/raw/<source>/<acquisition-id>/` without overwriting. Its result has `destination`, `copied`, `conflict`, and `discrepancies`. Report conflicts and discrepancies. A verified copy has no discrepancies; an existing destination can match while still reporting a conflict.

`record_acquisition(root, acquisition_dir, retained_copy=None) -> dict` writes a completed acquisition's Acquisitions row from its provenance, with `retained_copy` a verified destination or `None` for `this checkout only`. It never rewrites an existing row except to fill an empty or `this checkout only` Retained copy cell with a verified copy, and it sets a `candidate` source to `acquired`. It returns `row` (`added`, `updated`, or `unchanged`) and `source_status`, and raises `LookupError` when the Acquisitions table is missing.

`session(root, *, views_dir='foundation/views')` returns a new in-memory DuckDB connection (requires `duckdb`). It loads `*.sql` in filename order; dependent views sort after their inputs. Project-relative data paths resolve against `root`. A composition entry imports it, executes its saved queries by path, and closes the connection.

To run a saved query or a one-off query, use the command instead of writing a snippet:

```sh
python3 src/awb.py sql investigations/order-quality/exploration/missing-ids.sql
python3 src/awb.py sql "select status, count(*) from orders group by all" --limit 50
python3 src/awb.py sql investigations/order-quality/exploration/missing-ids.sql --out investigations/order-quality/exploration/missing-ids.parquet
```

The argument is a query file when it names an existing file (absolute or project-relative), otherwise SQL text. Each run opens a fresh `session(root)`, runs every statement, and prints the last statement's result: the first `--limit` rows (default 20) as a Markdown table, then the total row count. `--out` writes the full result to a `.csv` or `.parquet` file through DuckDB; relative paths are project-relative. Errors print one line on stderr and exit 1.
