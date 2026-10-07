import importlib.util
import json
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


@pytest.fixture
def package(tmp_path):
    draft = tmp_path / "draft"
    draft.mkdir()
    (draft / "journal.md").write_bytes(b"abc")
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

    assert manifest.inventory(package, manifest_name="manifest.json") == [
        {"path": ".hidden", "bytes": 5, "sha256": HELLO},
        {"path": "datasets/d.csv", "bytes": 5, "sha256": HELLO},
        {"path": "figures/a.png", "bytes": 0, "sha256": EMPTY},
        {"path": "journal.md", "bytes": 3, "sha256": ABC},
        {"path": "manifest.json"},
    ]


@pytest.mark.parametrize("seam", ["inventory", "verify"])
@pytest.mark.parametrize("name", ["/manifest.json", "../manifest.json", "meta/../manifest.json"])
def test_rejects_absolute_or_parent_manifest_paths(package, name, seam):
    with pytest.raises(ValueError, match="manifest"):
        if seam == "inventory":
            manifest.inventory(package, manifest_name=name)
        else:
            manifest.verify(package, [], manifest_name=name)


@pytest.mark.parametrize("target", ["journal.md", "empty", "absent"])
def test_inventory_rejects_file_directory_and_dangling_symlinks(package, target):
    link = package / "link"
    try:
        link.symlink_to(package / target, target_is_directory=target == "empty")
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are not supported")
    with pytest.raises(ValueError, match="link"):
        manifest.inventory(package, manifest_name="manifest.json")


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


@pytest.mark.parametrize("removed_path, digest", [("journal.md", ABC), ("manifest.json", None)])
def test_verify_reports_missing_file_or_manifest(package, removed_path, digest):
    rows = manifest.inventory(package, manifest_name="manifest.json")
    (package / removed_path).unlink()
    assert manifest.verify(package, rows, manifest_name="manifest.json") == [
        {"path": removed_path, "kind": "missing", "expected": digest, "actual": None},
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
    (package / "journal.md").write_bytes(b"hello")
    assert manifest.verify(package, rows, manifest_name="manifest.json") == [
        {"path": "journal.md", "kind": "size", "expected": 3, "actual": 5},
        {"path": "journal.md", "kind": "checksum", "expected": ABC, "actual": HELLO},
    ]


@pytest.mark.parametrize("change_manifest", [False, True])
def test_verify_checks_manifest_presence_only(package, change_manifest):
    rows = manifest.inventory(package, manifest_name="manifest.json")
    if change_manifest:
        (package / "manifest.json").write_bytes(b'{"inventory": "written after hashing"}')
    assert manifest.verify(package, rows, manifest_name="manifest.json") == []


def test_verify_accepts_digit_string_sizes_and_reports_int_sizes(package):
    rows = manifest.inventory(package, manifest_name="manifest.json")
    for row in rows:
        if "bytes" in row:
            row["bytes"] = str(row["bytes"])
    assert manifest.verify(package, rows, manifest_name="manifest.json") == []
    (package / "journal.md").write_bytes(b"hello")
    assert manifest.verify(package, rows, manifest_name="manifest.json") == [
        {"path": "journal.md", "kind": "size", "expected": 3, "actual": 5},
        {"path": "journal.md", "kind": "checksum", "expected": ABC, "actual": HELLO},
    ]


def test_verify_compares_recorded_digests_case_insensitively(package):
    rows = manifest.inventory(package, manifest_name="manifest.json")
    for row in rows:
        if "sha256" in row:
            row["sha256"] = row["sha256"].upper()
    assert manifest.verify(package, rows, manifest_name="manifest.json") == []


@pytest.mark.parametrize("field", ["bytes", "sha256"])
@pytest.mark.parametrize("file_exists", [True, False])
def test_verify_rejects_incomplete_non_manifest_rows(package, field, file_exists):
    rows = manifest.inventory(package, manifest_name="manifest.json")
    journal_row = next(row for row in rows if row["path"] == "journal.md")
    del journal_row[field]
    if not file_exists:
        (package / "journal.md").unlink()
    with pytest.raises(ValueError, match="journal.md"):
        manifest.verify(package, rows, manifest_name="manifest.json")


@pytest.mark.parametrize("path", ["journal.md", "manifest.json"])
def test_verify_rejects_duplicate_inventory_paths(package, path):
    rows = manifest.inventory(package, manifest_name="manifest.json")
    rows.append(dict(next(row for row in rows if row["path"] == path)))
    with pytest.raises(ValueError, match=path):
        manifest.verify(package, rows, manifest_name="manifest.json")


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
    (copy / "journal.md").write_bytes(b"def")
    assert manifest.compare_trees(package, copy) == [
        {"path": "datasets/d.csv", "kind": "missing", "expected": HELLO, "actual": None},
        {"path": "figures/a.png", "kind": "size", "expected": 0, "actual": 3},
        {"path": "figures/a.png", "kind": "checksum", "expected": EMPTY, "actual": ABC},
        {"path": "journal.md", "kind": "checksum", "expected": ABC,
         "actual": "cb8379ac2098aa165029e3938a51da0bcecfc008fd6795f401178647f96c5b34"},
        {"path": "new.md", "kind": "extra", "expected": None, "actual": HELLO},
    ]


@pytest.mark.parametrize("seam", ["inventory", "verify", "compare_trees"])
def test_all_seams_reject_symlink_root(package, tmp_path, seam):
    link = tmp_path / "linked-draft"
    try:
        link.symlink_to(package, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are not supported")
    with pytest.raises(ValueError, match="linked-draft"):
        if seam == "inventory":
            manifest.inventory(link, manifest_name="manifest.json")
        elif seam == "verify":
            manifest.verify(link, [], manifest_name="manifest.json")
        else:
            manifest.compare_trees(package, link)


@pytest.mark.parametrize("seam", ["verify", "compare_trees"])
def test_verify_and_compare_trees_reject_nested_symlink(package, tmp_path, seam):
    copy = shutil.copytree(package, tmp_path / "copy")
    rows = manifest.inventory(package, manifest_name="manifest.json")
    try:
        (copy / "figures/link").symlink_to(package / "journal.md")
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are not supported")
    with pytest.raises(ValueError, match="link"):
        if seam == "verify":
            manifest.verify(copy, rows, manifest_name="manifest.json")
        else:
            manifest.compare_trees(package, copy)
