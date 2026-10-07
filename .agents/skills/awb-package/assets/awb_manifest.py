"""Build and check an analytics workbench package's file inventory.

Copy this file to `src/packaging/manifest.py`; do not import it from the skill folder.
"""

import hashlib
import os
from pathlib import Path


def _manifest_path(name):
    path = Path(name)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Invalid manifest path: {name}")
    return path.as_posix()


def _scan(directory):
    files = {}
    root = Path(directory)
    if root.is_symlink():
        raise ValueError(f"Symlink in tree: {root}")
    for file in root.rglob("*"):
        if file.is_symlink():
            raise ValueError(f"Symlink in tree: {file}")
        if file.is_file():
            digest = hashlib.sha256()
            size = 0
            with file.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    size += len(chunk)
                    digest.update(chunk)
            path = file.relative_to(root).as_posix()
            files[path] = {"path": path, "bytes": size, "sha256": digest.hexdigest()}
    return files


def inventory(package_dir: str | os.PathLike, *, manifest_name: str) -> list[dict]:
    """List files in path order, reserving a path-only row for the manifest."""
    manifest_name = _manifest_path(manifest_name)
    files = _scan(package_dir)
    files[manifest_name] = {"path": manifest_name}
    return [files[path] for path in sorted(files)]


def _compare(expected, actual, manifest_name=None):
    differences = []
    for path in sorted(expected.keys() | actual.keys()):
        if path not in actual:
            differences.append({"path": path, "kind": "missing",
                                "expected": expected[path].get("sha256"), "actual": None})
        elif path not in expected:
            differences.append({"path": path, "kind": "extra", "expected": None,
                                "actual": actual[path]["sha256"]})
        elif path != manifest_name:
            size_differs = expected[path]["bytes"] != actual[path]["bytes"]
            if size_differs:
                differences.append({"path": path, "kind": "size",
                                    "expected": expected[path]["bytes"],
                                    "actual": actual[path]["bytes"]})
            if size_differs or expected[path]["sha256"].lower() != actual[path]["sha256"].lower():
                differences.append({"path": path, "kind": "checksum",
                                    "expected": expected[path]["sha256"],
                                    "actual": actual[path]["sha256"]})
    return differences


def verify(package_dir: str | os.PathLike, inventory: list[dict], *, manifest_name: str) -> list[dict]:
    """Compare a package with the inventory recorded in its manifest."""
    manifest_name = _manifest_path(manifest_name)
    expected = {}
    for row in inventory:
        path = row["path"]
        if path in expected:
            raise ValueError(f"Duplicate inventory path: {path}")
        expected[path] = dict(row)
        if path != manifest_name:
            if "bytes" not in row or "sha256" not in row:
                raise ValueError(f"Incomplete inventory row: {path}")
            expected[path]["bytes"] = int(row["bytes"])
    return _compare(expected, _scan(package_dir), manifest_name)


def compare_trees(local_dir: str | os.PathLike, copy_dir: str | os.PathLike) -> list[dict]:
    """Compare every file, including the manifest, with the local release as expected."""
    return _compare(_scan(local_dir), _scan(copy_dir))
