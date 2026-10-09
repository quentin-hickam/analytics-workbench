# Kept cases:
# test_inventory_lists_sorted_files_and_manifest_by_path_only: sorted paths, sizes and checksums; path-only manifest whether present or absent.
# test_inventory_rejects_empty_manifest_name: regression: empty manifest name is rejected.
# test_verify_accepts_unchanged_package_with_serialized_inventory: serialized inventory exact match returns no discrepancies.
# test_verify_reports_extra_file_including_manifest_without_row: extra file and manifest without a recorded row.
# test_verify_reports_missing_file: missing regular file reports its recorded digest.
# test_verify_reports_same_size_checksum_change: same-size checksum discrepancy.
# test_verify_reports_size_then_checksum_for_length_change: size and checksum discrepancies in order.
# test_verify_checks_manifest_presence_only: manifest content is excluded from verification.
# test_verify_accepts_digit_string_sizes_and_reports_int_sizes: regression: digit-string bytes parse and discrepancies report integers.
# test_verify_rejects_incomplete_non_manifest_rows: regression: null sha256 raises ValueError naming the path.
# test_verify_rejects_invalid_byte_sizes: regression: bytes rejects bool, float, negative int and non-digit string.
# test_verify_rejects_row_without_path: regression: missing path raises ValueError.
# test_verify_reports_missing_manifest_as_none_even_with_recorded_digest: regression: missing manifest expected digest is always None.
# test_compare_trees_checks_full_copy_including_manifest: exact tree match; manifest size and checksum are compared.
# test_compare_trees_reports_sorted_missing_extra_and_checksum: sorted missing, extra, size and checksum tree discrepancies.
# test_all_seams_reject_missing_directory: regression: missing directory raises for inventory, verify and compare_trees.
# test_all_seams_raise_on_unreadable_subdirectory: regression: an unreadable subdirectory raises through os.walk instead of being skipped.

import hashlib
import importlib.util
import json
import os
import shutil
from pathlib import Path

import pytest


ASSET = Path(__file__).resolve().parents[1] / ".agents/skills/awb-package/assets/awb_manifest.py"
spec = importlib.util.spec_from_file_location("awb_manifest", ASSET)
manifest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manifest)

# SHA-256 test vectors for the literal fixture contents, independent of tree scanning.
ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
EMPTY = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
HELLO = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"

# Each seam called on one directory with an empty inventory, for checks every seam shares.
SEAMS = {
    "inventory": lambda directory: manifest.inventory(directory, manifest_name="manifest.json"),
    "verify": lambda directory: manifest.verify(directory, [], manifest_name="manifest.json"),
    "compare_trees": lambda directory: manifest.compare_trees(directory, directory),
}


@pytest.fixture
def package(tmp_path):
    draft = tmp_path / "draft"
    draft.mkdir()
    (draft / "findings.md").write_bytes(b"abc")
    (draft / "figures").mkdir()
    (draft / "figures/a.png").write_bytes(b"")
    (draft / "datasets").mkdir()
    (draft / "datasets/d.csv").write_bytes(b"hello")
    (draft / "empty").mkdir()
    (draft / "manifest.json").write_bytes(b"{}")
    return draft


@pytest.mark.parametrize("manifest_exists", [True, False])
def test_inventory_lists_sorted_files_and_manifest_by_path_only(package, manifest_exists):
    (package / ".hidden").write_bytes(b"hello")
    if not manifest_exists:
        (package / "manifest.json").unlink()

    rows = manifest.inventory(package, manifest_name="manifest.json")
    for row in rows[:-1]:
        content = (package / row["path"]).read_bytes()
        assert (row["bytes"], row["sha256"]) == (len(content), hashlib.sha256(content).hexdigest())
    assert rows == [
        {"path": ".hidden", "bytes": 5, "sha256": HELLO},
        {"path": "datasets/d.csv", "bytes": 5, "sha256": HELLO},
        {"path": "figures/a.png", "bytes": 0, "sha256": EMPTY},
        {"path": "findings.md", "bytes": 3, "sha256": ABC},
        {"path": "manifest.json"},
    ]


def test_inventory_rejects_empty_manifest_name(package):
    with pytest.raises(ValueError, match="manifest path"):
        manifest.inventory(package, manifest_name="")


def test_verify_accepts_unchanged_package_with_serialized_inventory(package):
    rows = json.loads(json.dumps(manifest.inventory(package, manifest_name="manifest.json")))
    assert manifest.verify(package, rows, manifest_name="manifest.json") == []


@pytest.mark.parametrize("extra_path", ["added.md", "manifest.json"])
def test_verify_reports_extra_file_including_manifest_without_row(package, extra_path):
    rows = manifest.inventory(package, manifest_name="manifest.json")
    if extra_path == "manifest.json":
        rows = [row for row in rows if row["path"] != "manifest.json"]
    (package / extra_path).write_bytes(b"abc")
    assert manifest.verify(package, rows, manifest_name="manifest.json") == [
        {"path": extra_path, "kind": "extra", "expected": None, "actual": ABC},
    ]


def test_verify_reports_missing_file(package):
    rows = manifest.inventory(package, manifest_name="manifest.json")
    (package / "findings.md").unlink()
    assert manifest.verify(package, rows, manifest_name="manifest.json") == [
        {"path": "findings.md", "kind": "missing", "expected": ABC, "actual": None},
    ]


def test_verify_reports_same_size_checksum_change(package):
    rows = manifest.inventory(package, manifest_name="manifest.json")
    (package / "datasets/d.csv").write_bytes(b"world")
    assert manifest.verify(package, rows, manifest_name="manifest.json") == [
        {"path": "datasets/d.csv", "kind": "checksum", "expected": HELLO,
         "actual": "486ea46224d1bb4fb680f34f7c9ad96a8f24ec88be73ea8e5a6c65260e9cb8a7"},
    ]


def test_verify_reports_size_then_checksum_for_length_change(package):
    rows = manifest.inventory(package, manifest_name="manifest.json")
    (package / "findings.md").write_bytes(b"hello")
    assert manifest.verify(package, rows, manifest_name="manifest.json") == [
        {"path": "findings.md", "kind": "size", "expected": 3, "actual": 5},
        {"path": "findings.md", "kind": "checksum", "expected": ABC, "actual": HELLO},
    ]


def test_verify_checks_manifest_presence_only(package):
    rows = manifest.inventory(package, manifest_name="manifest.json")
    (package / "manifest.json").write_bytes(b'{"inventory": "written after hashing"}')
    assert manifest.verify(package, rows, manifest_name="manifest.json") == []


def test_verify_accepts_digit_string_sizes_and_reports_int_sizes(package):
    rows = manifest.inventory(package, manifest_name="manifest.json")
    for row in rows:
        if "bytes" in row:
            row["bytes"] = str(row["bytes"])
    assert manifest.verify(package, rows, manifest_name="manifest.json") == []
    (package / "findings.md").write_bytes(b"hello")
    assert manifest.verify(package, rows, manifest_name="manifest.json") == [
        {"path": "findings.md", "kind": "size", "expected": 3, "actual": 5},
        {"path": "findings.md", "kind": "checksum", "expected": ABC, "actual": HELLO},
    ]


def test_verify_rejects_incomplete_non_manifest_rows(package):
    rows = manifest.inventory(package, manifest_name="manifest.json")
    next(row for row in rows if row["path"] == "findings.md")["sha256"] = None
    with pytest.raises(ValueError, match="findings.md"):
        manifest.verify(package, rows, manifest_name="manifest.json")


@pytest.mark.parametrize("size", ["-3", 3.0, True, -3])
def test_verify_rejects_invalid_byte_sizes(package, size):
    rows = manifest.inventory(package, manifest_name="manifest.json")
    next(row for row in rows if row["path"] == "findings.md")["bytes"] = size
    with pytest.raises(ValueError, match="findings.md"):
        manifest.verify(package, rows, manifest_name="manifest.json")


def test_verify_rejects_row_without_path(package):
    with pytest.raises(ValueError, match="without a path"):
        manifest.verify(package, [{"bytes": 3, "sha256": ABC}], manifest_name="manifest.json")


def test_verify_reports_missing_manifest_as_none_even_with_recorded_digest(package):
    rows = manifest.inventory(package, manifest_name="manifest.json")
    rows[-1]["sha256"] = ABC
    (package / "manifest.json").unlink()
    assert manifest.verify(package, rows, manifest_name="manifest.json") == [
        {"path": "manifest.json", "kind": "missing", "expected": None, "actual": None},
    ]


def test_compare_trees_checks_full_copy_including_manifest(package, tmp_path):
    copy = shutil.copytree(package, tmp_path / "copy")
    assert manifest.compare_trees(package, copy) == []
    (package / "manifest.json").write_bytes(b"abc")
    (copy / "manifest.json").write_bytes(b"hello")
    assert manifest.compare_trees(str(package), str(copy)) == [
        {"path": "manifest.json", "kind": "size", "expected": 3, "actual": 5},
        {"path": "manifest.json", "kind": "checksum", "expected": ABC, "actual": HELLO},
    ]


def test_compare_trees_reports_sorted_missing_extra_and_checksum(package, tmp_path):
    copy = shutil.copytree(package, tmp_path / "copy")
    (copy / "datasets/d.csv").unlink()
    (copy / "figures/a.png").write_bytes(b"abc")
    (copy / "new.md").write_bytes(b"hello")
    (copy / "findings.md").write_bytes(b"def")
    assert manifest.compare_trees(package, copy) == [
        {"path": "datasets/d.csv", "kind": "missing", "expected": HELLO, "actual": None},
        {"path": "figures/a.png", "kind": "size", "expected": 0, "actual": 3},
        {"path": "figures/a.png", "kind": "checksum", "expected": EMPTY, "actual": ABC},
        {"path": "findings.md", "kind": "checksum", "expected": ABC,
         "actual": "cb8379ac2098aa165029e3938a51da0bcecfc008fd6795f401178647f96c5b34"},
        {"path": "new.md", "kind": "extra", "expected": None, "actual": HELLO},
    ]


@pytest.mark.parametrize("seam", SEAMS)
def test_all_seams_reject_missing_directory(tmp_path, seam):
    with pytest.raises(FileNotFoundError):
        SEAMS[seam](tmp_path / "absent")


@pytest.mark.skipif(not hasattr(os, "geteuid") or os.geteuid() == 0, reason="needs a non-root POSIX user")
def test_all_seams_raise_on_unreadable_subdirectory(package):
    (package / "figures").chmod(0)
    try:
        for seam in SEAMS.values():
            with pytest.raises(PermissionError):
                seam(package)
    finally:
        (package / "figures").chmod(0o755)
