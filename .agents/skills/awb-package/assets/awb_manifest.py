"""Build and check an analytics workbench package's file inventory.

Copy this file to `src/packaging/manifest.py`; do not import it from the skill folder.
"""

import hashlib
import os
from pathlib import Path

_CHUNK_BYTES = 1024 * 1024  # 1 MiB reads keep memory flat on large datasets


def _checked_manifest_name(name):
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"Invalid manifest path: {name!r}")
    return path.as_posix()


def _scan(directory):
    root = Path(directory)
    if root.is_symlink():
        raise ValueError(f"Symlink in tree: {root}")

    def fail(error):
        raise error

    files = {}
    for current, dirnames, filenames in os.walk(root, onerror=fail):
        for name in dirnames + filenames:
            if Path(current, name).is_symlink():
                raise ValueError(f"Symlink in tree: {Path(current, name)}")
        for name in filenames:
            file = Path(current, name)
            if not file.is_file():
                continue
            digest = hashlib.sha256()
            size = 0
            with file.open("rb") as stream:
                for chunk in iter(lambda: stream.read(_CHUNK_BYTES), b""):
                    size += len(chunk)
                    digest.update(chunk)
            path = file.relative_to(root).as_posix()
            files[path] = {"path": path, "bytes": size, "sha256": digest.hexdigest()}
    return files


def inventory(package_dir: str | os.PathLike, *, manifest_name: str) -> list[dict]:
    """List files in path order, reserving a path-only row for the manifest."""
    manifest_name = _checked_manifest_name(manifest_name)
    files = _scan(package_dir)
    files[manifest_name] = {"path": manifest_name}
    return [files[path] for path in sorted(files)]


def _difference(path, kind, expected, actual):
    return {"path": path, "kind": kind, "expected": expected, "actual": actual}


def _compare(expected, actual, manifest_name=None):
    differences = []
    for path in sorted(expected.keys() | actual.keys()):
        if path not in actual:
            recorded = None if path == manifest_name else expected[path]["sha256"]
            differences.append(_difference(path, "missing", recorded, None))
        elif path not in expected:
            differences.append(_difference(path, "extra", None, actual[path]["sha256"]))
        elif path != manifest_name:
            recorded, found = expected[path], actual[path]
            if recorded["bytes"] != found["bytes"]:
                differences.append(_difference(path, "size", recorded["bytes"], found["bytes"]))
            # A size change is also reported as a checksum change, so both kinds always name it.
            if recorded["bytes"] != found["bytes"] or recorded["sha256"].lower() != found["sha256"]:
                differences.append(_difference(path, "checksum", recorded["sha256"], found["sha256"]))
    return differences


def verify(package_dir: str | os.PathLike, inventory: list[dict], *, manifest_name: str) -> list[dict]:
    """Compare a package with the inventory recorded in its manifest."""
    manifest_name = _checked_manifest_name(manifest_name)
    expected = {}
    for row in inventory:
        path = row.get("path")
        if not isinstance(path, str):
            raise ValueError(f"Inventory row without a path: {row!r}")
        if path in expected:
            raise ValueError(f"Duplicate inventory path: {path}")
        expected[path] = dict(row)
        if path != manifest_name:
            if "bytes" not in row or not isinstance(row.get("sha256"), str):
                raise ValueError(f"Incomplete inventory row: {path}")
            size = row["bytes"]
            if isinstance(size, str) and size.isascii() and size.isdigit():
                size = int(size)
            if type(size) is not int or size < 0:
                raise ValueError(f"Invalid inventory byte size: {path}")
            expected[path]["bytes"] = size
    return _compare(expected, _scan(package_dir), manifest_name)


def compare_trees(local_dir: str | os.PathLike, copy_dir: str | os.PathLike) -> list[dict]:
    """Compare every file, including the manifest, with the local release as expected."""
    return _compare(_scan(local_dir), _scan(copy_dir))
