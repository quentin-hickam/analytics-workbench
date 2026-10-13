# Delivery manifest fields

The manifest is `manifest.json`. Record times in ISO 8601 with a UTC offset, for example `2026-09-30T14:05:00-04:00`.

## Package identity

- `investigation`, `package`, and `status` (`draft` or `release`): `export` writes these fields when it creates the manifest.
- `revised_at`: `check-draft` stamps this field when the inventory changes. A release keeps the value of the draft.
- `release_number` (for example `002`), `released_at`, and `prior_release` (the latest numbered release before this one, for example `released/001`, or `none`): `release` writes these fields on the release copy.
- `inventory`: every file in the package directory. Each file has its path relative to the package directory (with `/` separators), its byte size, and its SHA-256. Directories are not listed. The manifest lists itself by path only, with no size or checksum, because the size and checksum change if they are written into the manifest. `python3 src/awb.py check-draft` writes this field.

## Producing state

The analytical results that this package represents.

- `producing_commit`: the producing commit SHA. The SHA is recovered from result evidence in the investigation records or from an earlier manifest. It is never assumed from the packaging checkout. If no commit existed, the value is `uncommitted`, with the recorded SHA-256 checksums of the producing files.
- `producing_uncommitted_changes`: `none`, or each affected code, view, and settings path, with the checksum that was recorded for it when the result was produced. The reason is that a SHA with uncommitted changes does not fully identify the producing code. Paths without recorded checksums are listed as such, and then the producing state is not recoverable.
- `inputs`: the inputs that were actually used. These are the source and acquisition or publication identifiers, with the checksums that their provenance or publication files record. They also include the view definitions that were read, with their checksums.
- `analytical_settings`: the analytical settings that the results represent.

`python3 src/awb.py export` writes these fields from the evidence files of the represented results. If every result records the same value, the field holds that value. If the results differ, the field holds each different value with the results that recorded it, under `value` and `results`. `inputs` holds `publications`, `acquisitions`, and `views` lists copied from the evidence. List entries name the results that recorded them under `results`. An unknown is `{"unknown": "<reason>"}`. For an `uncommitted` state, `producing_uncommitted_changes` holds the checksum of every producing file.

## Packaging state

The operation that assembled this package. It is recorded separately from the producing state.

- `packaging_commit`: the packaging checkout commit.
- `packaging_uncommitted_changes`: `none`, or the relevant uncommitted package-source paths.
- `export_checks`: the `compare_evidence` output of each serialized result. If there are no exports, the value is `none`.
- `results`: every represented result (serialized or not), as `result_id` and `evidence` path.

`export` writes `packaging_commit` and `packaging_uncommitted_changes` (paths under `src/` and `package-format/`). It also writes `export_checks` as one entry for each result. Each entry has `result_id`, `evidence`, and the unchanged `comparisons`:

- The entry of a serialized result is replaced.
- A represented result that is not serialized keeps its entry.
- An entry outside the represented set is removed.

## Selection

- `dataset_selection`: the exported dataset paths, or an explicit `none`.
- `charts`: the path of each chart file, with the result ID that it serializes, or `none`.

`export` writes both fields. It also writes the finding and reason of each `revalidation_flags` entry, one entry for each flagged finding. You fill `represented_in` and the user's `disposition`. If `represented_in` lists places, `disposition` must have a value. The **Revalidation caveats** section of the package contract defines the field.

Say that the provenance locates the producing state. Never call a package reproducible. If you cannot determine a field, record it as `unknown` with the reason.
