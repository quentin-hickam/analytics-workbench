# Landing helper

Call the project copy at `src/preparation/landing.py`. The `land`, `retain`, `publish`, and `sql` commands cover supplied files and select-based conversions; `python3 src/awb.py <command> --help` gives each one's arguments and output. This reference covers the two library calls for what the commands cannot do.

## Fetch a source with `land()`

For an API or other fetched source, call `land()` from a script with a `fetch` callable, then run `python3 src/awb.py retain` to retain the acquisition and write its Acquisitions row.

`land(root, source, acquisition_id, fetch, *, request, records=None, notes=None) -> Path` calls `fetch(partial_directory)`. The callback writes every original file and raises on incomplete acquisition; its return value is ignored. `request` and `notes` must be JSON serializable. `records` maps relative filenames to integer counts; omitted counts become null. `provenance.json` is reserved. After `fetch` returns, `land()` checks the files and `records`, hashes the files, writes provenance, and renames the directory from `.partial`. If `fetch` or any of these steps fails, the directory keeps its `.partial` name and every file `fetch` wrote, including a `provenance.json` it wrote by mistake; `land()` removes only the provenance it wrote itself.

## Convert with `publish()`

For a conversion a select cannot express, call `publish()` with a `convert` callable.

`publish(root, dataset, publication_id, convert, *, acquisitions, validate=None, notes=None) -> Path` calls `convert(partial_directory)`, runs the dataset's checks declared in `foundation/datasets.toml` over the Parquet files it wrote, then calls `validate(partial_directory)`. A failing declared check raises `ChecksFailed`, whose `checks` lists every declared check. Use `validate` for checks a declaration cannot express: raise on failure or return the Python boolean `False`; every other return value permits publication, and a returned string becomes the detail of its `validate` check. `acquisitions` lists completed acquisition directories, absolute or project-relative. Conversion reads them without modification. `publication.json` is reserved; the helper records inputs, hashes, Git HEAD (or `uncommitted`), and the checks with their outcomes, then renames the output directory. Record the publication in `foundation/catalog.md` as the `publish` command's `catalog_row` would.

## Both calls

Both refuse existing final or partial destinations. A failure leaves an unpublished partial directory; resolve it deliberately before retrying. Source, dataset, and run identifiers are single directory names, excluding `.`, `..`, and names ending in `.partial`.
