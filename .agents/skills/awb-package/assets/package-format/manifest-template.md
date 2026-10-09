# Delivery manifest fields

Every draft and release manifest records these fields under the field names shown. Serialize them in the project's established manifest format; when none exists, choose a simple readable format consistent with the repository and keep it for every later manifest. Every serialization uses these field names, so other skills can find a field without knowing the format. Record times in ISO 8601 with a UTC offset, such as `2026-09-30T14:05:00-04:00`.

## Package identity

- `investigation`: the investigation name;
- `package`: the package name;
- `status`: `draft` or `release`;
- `release_number`: the release number, such as `002`, on a release; empty on a draft;
- `created_at`: when the draft was first created, kept across revisions;
- `revised_at`: when this draft revision was written; a release keeps the value of the draft it copies;
- `released_at`: when the release was made; empty on a draft;
- `prior_release`: the latest numbered release before this one, such as `released/001`, or `none`; and
- `inventory`: every file in the package directory, each with its path relative to the package directory using `/` separators, byte size, and SHA-256; directories are not listed. The manifest lists itself by path only, with no size or checksum, since writing them would change them. Produce the rows with `inventory` in `src/packaging/manifest.py` and serialize them in order under the keys `path`, `bytes`, and `sha256`; `python3 src/awb.py check-draft` does both for a JSON manifest.

## Producing state

The analytical results this package represents.

- `producing_commit`: the producing commit SHA, recovered from result evidence in the investigation records or an earlier manifest, never assumed from the packaging checkout; or `uncommitted` with the recorded SHA-256 checksums of the producing files when no commit existed;
- `producing_uncommitted_changes`: `none`, or each affected code, view, and settings path with the checksum recorded for it when the result was produced, since a SHA with uncommitted changes does not fully identify the producing code; paths without recorded checksums are listed as such, and the producing state is then not recoverable;
- `inputs`: the inputs actually used: source and acquisition or publication identifiers with the checksums their provenance or publication files record, and the view definitions read with their checksums;
- `analytical_settings`: the analytical settings represented by the results; and
- `scope`: the population, period, and other scope the results cover.

`python3 src/awb.py draft-provenance` writes the first four fields into a JSON manifest from the results' evidence files. When every result records the same value, the field holds it; when results differ, it holds each distinct value with the results that recorded it, under `value` and `results`. `inputs` holds `publications`, `acquisitions`, and `views` lists copied from the evidence; list entries name the results that recorded them under `results`. An unknown is `{"unknown": "<reason>"}`. For an `uncommitted` state, `producing_uncommitted_changes` holds the checksum of every producing file.

## Packaging state

The operation that assembled this package, recorded separately from the producing state.

- `packaging_commit`: the packaging checkout commit;
- `packaging_uncommitted_changes`: `none`, or the relevant uncommitted package-source paths; and
- `export_checks`: each export's `compare_evidence` output, written by `export`; carried forward unchanged by a revision that reuses the export; `none` without exports.

`draft-provenance` writes `packaging_commit` and `packaging_uncommitted_changes` (paths under `src/` and `package-format/`), and with `--export-checks` writes `export_checks` as one entry per result, each with `result_id`, `evidence`, and the unchanged `comparisons`.

## Selection and caveats

- `dataset_selection`: the exported dataset paths, or an explicit `none`;
- `charts`: each chart file's path with the result ID it serializes, or `none`;
- `caveats`: unresolved caveats that need no disposition, such as source limitations, each with the conclusions it qualifies;
- `revalidation_flags`: each finding `state.md` currently flags, with `finding` and `reason` exactly as its row writes them, and `represented_in`: every place the draft represents an affected conclusion (findings text, methodology text, chart, dataset, or dataset column), each with its `disposition` (`revalidate`, `omit`, `release_with_caveat`, or `none` until the user chooses) and `disposition_recorded_at`, or `none` when the draft represents none of it; `none` when nothing is flagged; and
- `exact_rerun_inputs`: the exact-rerun inputs or snapshots included, only when the user chose them; otherwise `none`.

Call a package reproducible only when its producing state is a clean commit and it includes exact-rerun inputs; otherwise say its provenance locates the producing state. Record an undeterminable field as `unknown` with the reason.
