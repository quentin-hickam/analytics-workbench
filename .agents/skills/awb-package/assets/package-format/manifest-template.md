# Delivery manifest fields

Every draft and release manifest records these fields. Serialize them in the project's established manifest format; when none exists, choose a simple readable format consistent with the repository and keep it for every later manifest.

## Package identity

- investigation and package name;
- status: draft, or release with its number and release time;
- creation or revision time;
- prior release reference, or none; and
- file inventory of the package directory.

## Producing state

The analytical results this package represents.

- producing commit SHA, recovered from result provenance in the investigation records or an earlier manifest, never assumed from the packaging checkout;
- uncommitted producing changes: none, or the affected code, view, and settings paths, since a SHA with uncommitted changes does not fully identify the producing code;
- inputs actually used: source and acquisition or publication identifiers, plus the versions, dates, or checksums available in the foundation records; and
- analytical settings and scope represented by the results.

## Packaging state

The operation that assembled this package, recorded separately from the producing state.

- packaging checkout commit; and
- relevant uncommitted package-source changes.

## Selection and caveats

- dataset selection: the exported datasets, or an explicit none;
- unresolved caveats and revalidation flags, each with its recorded disposition: revalidate, omit, or release with caveat; and
- exact-rerun inputs or snapshots included, only when the user chose them.

A field that cannot be determined is recorded as unknown with the reason. A dirty or unknown producing state is never described as reproducible.
