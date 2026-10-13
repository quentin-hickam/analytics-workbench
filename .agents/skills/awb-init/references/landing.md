# Landing helper

Call the project copy at `src/preparation/landing.py`. The `land`, `retain`, `publish`, and `sql` commands cover supplied files and select-based conversions. `python3 src/awb.py <command> --help` gives the arguments and output of each command. This reference covers the two library calls for the work that the commands cannot do.

## Fetch a source with `land()`

For an API or other fetched source, call `land()` from a script with a `fetch` callable. Then run `python3 src/awb.py retain` to retain the acquisition and write its Acquisitions row.

`land(root, source, acquisition_id, fetch, *, request, records=None, notes=None) -> Path` calls `fetch(partial_directory)`. The callback writes every original file. If the acquisition is incomplete, the callback raises an exception. The return value of the callback is ignored. `request` and `notes` must be JSON serializable. `records` maps relative filenames to integer counts. An omitted count becomes null. `provenance.json` is reserved. Completed files are hashed, provenance is written, and the directory is renamed from `.partial` only on success.

## Convert with `publish()`

For a conversion that a select cannot express, call `publish()` with a `convert` callable.

`publish(root, dataset, publication_id, convert, *, acquisitions, validate=None, notes=None) -> Path` calls `convert(partial_directory)` and then `validate(partial_directory)`. Supply validation for publication. On failure, raise an exception or return the Python boolean `False`. Every other return value permits publication. `acquisitions` lists completed acquisition directories, as absolute or project-relative paths. The conversion reads them and does not change them. `publication.json` is reserved. The helper records the inputs, the hashes, and the Git HEAD (or `uncommitted`). Then it renames the output directory. Record the publication in `foundation/catalog.md` in the same way as the `catalog_row` of the `publish` command.

## Both calls

Both calls refuse a final or partial destination that exists. A failure leaves an unpublished partial directory. Resolve it deliberately before you try again. Source, dataset, and run identifiers are single directory names. They cannot be `.`, `..`, or a name that ends in `.partial`.
