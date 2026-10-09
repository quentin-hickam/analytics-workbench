# Delivery manifest fields

The manifest is `manifest.json`. Record times in ISO 8601 with a UTC offset, such as `2026-09-30T14:05:00-04:00`.

## Package identity

- `investigation`, `package`, and `status` (`draft` or `release`): written by `export` when it creates the manifest;
- `revised_at`: stamped by `check-draft` when the inventory changes; a release keeps the draft's value;
- `release_number` (such as `002`), `released_at`, and `prior_release` (the latest numbered release before this one, such as `released/001`, or `none`): written by `release` on the release copy; and
- `inventory`: every file in the package directory, each with its path relative to the package directory using `/` separators, byte size, and SHA-256; directories are not listed. The manifest lists itself by path only, with no size or checksum, since writing them would change them. `python3 src/awb.py check-draft` writes it.

## Producing state

The analytical results this package represents.

- `producing_commit`: the producing commit SHA, recovered from result evidence in the investigation records or an earlier manifest, never assumed from the packaging checkout; or `uncommitted` with the recorded SHA-256 checksums of the producing files when no commit existed;
- `producing_uncommitted_changes`: `none`, or each affected code, view, and settings path with the checksum recorded for it when the result was produced, since a SHA with uncommitted changes does not fully identify the producing code; paths without recorded checksums are listed as such, and the producing state is then not recoverable;
- `inputs`: the inputs actually used: source and acquisition or publication identifiers with the checksums their provenance or publication files record, and the view definitions read with their checksums; and
- `analytical_settings`: the analytical settings represented by the results.

`python3 src/awb.py export` writes these fields from the represented results' evidence files. When every result records the same value, the field holds it; when results differ, it holds each distinct value with the results that recorded it, under `value` and `results`. `inputs` holds `publications`, `acquisitions`, and `views` lists copied from the evidence; list entries name the results that recorded them under `results`. An unknown is `{"unknown": "<reason>"}`. For an `uncommitted` state, `producing_uncommitted_changes` holds the checksum of every producing file.

## Packaging state

The operation that assembled this package, recorded separately from the producing state.

- `packaging_commit`: the packaging checkout commit;
- `packaging_uncommitted_changes`: `none`, or the relevant uncommitted package-source paths; and
- `export_checks`: each serialized result's `compare_evidence` output; `none` without exports.

`export` writes `packaging_commit` and `packaging_uncommitted_changes` (paths under `src/` and `package-format/`), and `export_checks` as one entry per result, each with `result_id`, `evidence`, and the unchanged `comparisons`: a serialized result's entry is replaced, a represented result not serialized keeps its entry, and an entry outside the represented set is dropped.

## Selection

- `dataset_selection`: the exported dataset paths, or an explicit `none`; and
- `charts`: each chart file's path with the result ID it serializes, or `none`.

`export` writes both. `revalidation_flags`, the one field recorded by hand, holds one entry per flagged finding, with `disposition` required when `represented_in` lists places; the package contract's **Revalidation caveats** defines it.

Say the provenance locates the producing state; never call a package reproducible. Record an undeterminable field as `unknown` with the reason.
