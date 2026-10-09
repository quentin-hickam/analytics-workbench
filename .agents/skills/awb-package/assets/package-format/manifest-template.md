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
- `inventory`: every file in the package directory, each with its path relative to the package directory using `/` separators, byte size, and SHA-256; directories are not listed. The manifest lists itself by path only, with no size or checksum, since writing them would change them. Produce the rows with `inventory` in `src/packaging/manifest.py` and serialize them in order under the keys `path`, `bytes`, and `sha256`.

## Producing state

The analytical results this package represents.

- `producing_commit`: the producing commit SHA, recovered from result provenance in the investigation records or an earlier manifest, never assumed from the packaging checkout; or `uncommitted` with the recorded SHA-256 checksums of the producing files when no commit existed;
- `producing_uncommitted_changes`: `none`, or each affected code, view, and settings path with the checksum recorded for it when the result was produced, since a SHA with uncommitted changes does not fully identify the producing code; paths without recorded checksums are listed as such, and the producing state is then not recoverable;
- `inputs`: the inputs actually used: source and acquisition or publication identifiers with the checksums their provenance or publication files record, and the view definitions read with their checksums;
- `analytical_settings`: the analytical settings represented by the results; and
- `scope`: the population, period, and other scope the results cover.

## Packaging state

The operation that assembled this package, recorded separately from the producing state.

- `packaging_commit`: the packaging checkout commit;
- `packaging_uncommitted_changes`: `none`, or the relevant uncommitted package-source paths; and
- `export_checks`: for each exported dataset, the output of `compare_evidence` in `src/provenance.py`, run before its export: the five named comparisons showing that the current code and data match the complete producing state (committed result code paths against the producing commit, uncommitted producing changes against their recorded checksums or every producing file for an `uncommitted` state, view definitions and the publications they read against the recorded ones, input publication and acquisition files against their recorded checksums, and resolved settings against the recorded settings), each with its paths or identifiers and outcome. A revision that reuses an export carries its checks forward unchanged; with no exported datasets, `none`.

## Selection and caveats

- `dataset_selection`: the exported dataset paths, or an explicit `none`;
- `caveats`: unresolved caveats that need no disposition, such as source limitations, each with the conclusions it qualifies;
- `revalidation_flags`: each represented finding awaiting revalidation, with `finding`, `reason` as currently recorded in `state.md`, and `represented_in`: every place the draft represents an affected conclusion (findings text, methodology text, figure, dataset, or dataset column), each with its `disposition` (`revalidate`, `omit`, `release_with_caveat`, or `none` until the user chooses) and `disposition_recorded_at`; or `none`; and
- `exact_rerun_inputs`: the exact-rerun inputs or snapshots included, only when the user chose them; otherwise `none`.

A field that cannot be determined is recorded as `unknown` with the reason. A dirty, `uncommitted`, or unknown producing state is never described as reproducible. Unless exact-rerun inputs are included, the commit, input identifiers, and settings locate what produced the results but do not guarantee an exact rerun; do not describe such a package as exactly reproducible.
