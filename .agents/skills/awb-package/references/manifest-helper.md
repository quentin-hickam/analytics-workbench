# Manifest helper interface

Use this when interpreting the inventory and copy comparisons that `check-draft` and `release` report, or when comparing a copied release by hand. If the project lacks `src/packaging/manifest.py`, copy [awb_manifest.py](../assets/awb_manifest.py) there. Preserve an existing helper. Call the project copy; source inspection is needed only for an incompatible interface or a failure requiring diagnosis.

## Calls

- `inventory(package_dir, *, manifest_name) -> list[dict]`: sorted relative paths with `bytes` and `sha256`; reserves a path-only row for the manifest, even before it exists.
- `verify(package_dir, inventory, *, manifest_name) -> list[dict]`: compare files with the recorded rows; manifest content is excluded but its presence is checked.
- `compare_trees(local_dir, copy_dir) -> list[dict]`: compare all files, including the manifest, with the local release as expected.

`manifest_name` is a relative path inside the package. Differences retain `path`, `kind` (`missing`, `extra`, `size`, `checksum`), `expected`, and `actual`. Empty differences means success. Invalid inventories, missing/unreadable directories, and symlinks raise errors; report them as failed checks. Files are hashed in bounded chunks. The helper checks file integrity; narrative consistency and dispositions still require review.

## Commands that call it

`python3 src/awb.py check-draft <investigation> <package>` regenerates `inventory` into a JSON manifest, preserving every other field, and runs `verify`; run it only once every other draft file is final. Release verification uses `--verify-only`, which reloads the current manifest and verifies its recorded rows without regenerating them. `python3 src/awb.py release <investigation> <package>` runs `compare_trees` with the local release as `local_dir` after copying it to reachable storage. Both report every discrepancy unchanged and keep their complete records under the package's `audit/` directory, never inside a verified draft or release. For a non-JSON manifest, serialize `inventory` rows in order under `path`, `bytes`, and `sha256` with the project's established serializer and call `verify` directly.

To copy existing releases to newly recorded storage, call `compare_trees(local_dir, copy_dir)` after each copy and report each returned discrepancy unchanged, or that none were returned. If a discrepancy list is large, save it outside the package, report its count and path, and make every unchanged discrepancy available in the report; never silently truncate it or add report files inside a verified release.
