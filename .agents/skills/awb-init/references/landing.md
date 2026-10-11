# Landing helper

Call the project copy at `src/preparation/landing.py`. The `land`, `retain`, `publish`, and `sql` commands cover supplied files and select-based conversions; `python3 src/awb.py <command> --help` gives each one's arguments and output. This reference covers the two library calls for what the commands cannot do.

## Fetch a source with `land()`

For an API or other fetched source, call `land()` from a script with a `fetch` callable, then run `python3 src/awb.py retain` to retain the acquisition and write its Acquisitions row.

`land(root, source, acquisition_id, fetch, *, request, records=None, notes=None) -> Path` calls `fetch(partial_directory)`. The callback writes every original file and raises on incomplete acquisition; its return value is ignored. `request` and `notes` must be JSON serializable. `records` maps relative filenames to integer counts; omitted counts become null. `provenance.json` is reserved. Completed files are hashed, provenance is written, and the directory is renamed from `.partial` only on success.

## Convert with `publish()`

For a conversion a select cannot express, call `publish()` with a `convert` callable.

`publish(root, dataset, publication_id, convert, *, acquisitions, validate=None, notes=None) -> Path` calls `convert(partial_directory)`, then `validate(partial_directory)`. Supply validation for publication: raise on failure or return the Python boolean `False`; every other return value permits publication. `acquisitions` lists completed acquisition directories, absolute or project-relative. Conversion reads them without modification. `publication.json` is reserved; the helper records inputs, hashes, and Git HEAD (or `uncommitted`), then renames the output directory. Record the publication in `foundation/catalog.md` as the `publish` command's `catalog_row` would.

## Both calls

Both refuse existing final or partial destinations. A failure leaves an unpublished partial directory; resolve it deliberately before retrying. Source, dataset, and run identifiers are single directory names, excluding `.`, `..`, and names ending in `.partial`.
