# Manifest helper interface

Use this when building an inventory, verifying a draft, or comparing a copied release. If the project lacks `src/packaging/manifest.py`, copy [awb_manifest.py](../assets/awb_manifest.py) there. Preserve an existing helper. Call the project copy; source inspection is needed only for an incompatible interface or a failure requiring diagnosis.

## Calls

- `inventory(package_dir, *, manifest_name) -> list[dict]`: sorted relative paths with `bytes` and `sha256`; reserves a path-only row for the manifest, even before it exists.
- `verify(package_dir, inventory, *, manifest_name) -> list[dict]`: compare files with the recorded rows; manifest content is excluded but its presence is checked.
- `compare_trees(local_dir, copy_dir) -> list[dict]`: compare all files, including the manifest, with the local release as expected.

`manifest_name` is a relative path inside the package. Differences retain `path`, `kind` (`missing`, `extra`, `size`, `checksum`), `expected`, and `actual`. Empty differences means success. Invalid inventories, missing/unreadable directories, and symlinks raise errors; report them as failed checks. Files are hashed in bounded chunks. The helper checks file integrity; narrative consistency and dispositions still require review.

## Build and check without printing an inventory

Run from the project root, replacing the draft path and using the project's established serializer. This example assumes an existing JSON manifest; it preserves all other fields. Finish all other draft files first. Run inventory generation only while drafting; release verification must use the recorded rows.

```python
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path("src/packaging").resolve()))
from manifest import inventory, verify

draft = Path("deliveries/INVESTIGATION/PACKAGE/draft")
manifest_name = "manifest.json"
path = draft / manifest_name
record = json.loads(path.read_text())
record["inventory"] = inventory(draft, manifest_name=manifest_name)
path.write_text(json.dumps(record, indent=2) + "\n")
differences = verify(draft, record["inventory"], manifest_name=manifest_name)
print(json.dumps({"files": len(record["inventory"]), "manifest": str(path),
                  "differences": differences}))
```

For the inventory part of each release verification pass, reload the current manifest and call `verify(draft, record["inventory"], manifest_name=manifest_name)` without regenerating inventory. Also run the [findings helper](findings-helper.md) afresh with the complete names set, as the package contract requires. Report every returned result and discrepancy unchanged; never reuse either first-pass result for the second.

After copying a release, call `compare_trees(local_dir, copy_dir)` and report each returned discrepancy unchanged, or that none were returned. Keep complete inventories and audit evidence serialized on disk rather than copying successful rows into conversation. If a discrepancy list is large, save it outside the package, report its count and path, and make every unchanged discrepancy available in the report; never silently truncate it or add report files inside a verified release.
