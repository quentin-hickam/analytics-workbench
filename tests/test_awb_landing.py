import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest


ASSET = Path(__file__).resolve().parents[1] / ".agents/skills/awb-init/assets/awb_landing.py"
spec = importlib.util.spec_from_file_location("awb_landing", ASSET)
landing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(landing)


def test_land_writes_complete_provenance_and_publishes_directory(tmp_path):
    records = {}

    def fetch(directory):
        (directory / "nested").mkdir()
        (directory / "nested/page.json").write_bytes(b"abc")
        (directory / "empty.csv").write_bytes(b"")
        records["nested/page.json"] = 3

    final = landing.land(str(tmp_path), "api", "batch-1", fetch,
                         request={"page": 1}, records=records, notes="café")

    assert final == tmp_path / "data/raw/api/batch-1"
    assert final.is_dir()
    assert not final.with_name("batch-1.partial").exists()
    raw = (final / "provenance.json").read_text(encoding="utf-8")
    provenance = json.loads(raw)
    assert list(provenance) == ["source", "acquisition_id", "request", "started_at",
                                "completed_at", "status", "files", "notes"]
    assert provenance["source"] == "api"
    assert provenance["acquisition_id"] == "batch-1"
    assert provenance["request"] == {"page": 1}
    assert provenance["status"] == "complete"
    assert provenance["notes"] == "café"
    assert provenance["files"] == [
        {"path": "empty.csv", "bytes": 0, "sha256": hashlib.sha256(b"").hexdigest(),
         "records": None},
        {"path": "nested/page.json", "bytes": 3, "sha256": hashlib.sha256(b"abc").hexdigest(),
         "records": 3},
    ]
    for name in ("started_at", "completed_at"):
        timestamp = datetime.fromisoformat(provenance[name])
        assert timestamp.utcoffset() is not None
        assert timestamp.microsecond == 0
    assert raw.endswith("\n")
    assert raw.startswith('{\n  "source": "api",\n')


def test_land_keeps_failed_fetch_unpublished(tmp_path):
    def fetch(directory):
        (directory / "page.json").write_bytes(b"abc")
        raise LookupError("page 2 failed")

    with pytest.raises(LookupError, match="page 2 failed"):
        landing.land(tmp_path, "api", "batch-1", fetch, request="query")
    partial = tmp_path / "data/raw/api/batch-1.partial"
    assert (partial / "page.json").read_bytes() == b"abc"
    assert not (partial / "provenance.json").exists()
    assert not tmp_path.joinpath("data/raw/api/batch-1").exists()


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def acquisition(root):
    return landing.land(root, "api", "batch-1",
                        lambda directory: (directory / "page.json").write_bytes(b"abc"),
                        request="user-supplied file")


def test_publish_records_inputs_and_uncommitted_conversion(tmp_path):
    git(tmp_path, "init")
    original = acquisition(tmp_path)
    validated = []

    def convert(directory):
        (directory / "nested").mkdir()
        (directory / "nested/part.parquet").write_bytes(b"abc")

    final = landing.publish(str(tmp_path), "events", "v1", convert,
                            acquisitions=[original.relative_to(tmp_path)],
                            validate=lambda path: validated.append(path), notes="converted")
    assert final == tmp_path / "data/parquet/events/v1"
    assert not final.with_name("v1.partial").exists()
    assert validated == [final.with_name("v1.partial")]
    raw = (final / "publication.json").read_text(encoding="utf-8")
    publication = json.loads(raw)
    assert list(publication) == ["dataset", "publication_id", "inputs", "conversion_commit",
                                "converted_at", "files", "notes"]
    assert publication["dataset"] == "events"
    assert publication["publication_id"] == "v1"
    assert publication["conversion_commit"] == "uncommitted"
    assert publication["inputs"] == [{
        "source": "api", "acquisition_id": "batch-1",
        "files": [{"path": "page.json", "sha256": hashlib.sha256(b"abc").hexdigest()}],
    }]
    assert publication["files"] == [{"path": "nested/part.parquet", "bytes": 3,
                                     "sha256": hashlib.sha256(b"abc").hexdigest()}]
    assert publication["notes"] == "converted"
    converted_at = datetime.fromisoformat(publication["converted_at"])
    assert converted_at.utcoffset() is not None
    assert converted_at.microsecond == 0
    assert raw.endswith("\n")
    assert raw.startswith('{\n  "dataset": "events",\n')


def test_publish_records_resolved_head(tmp_path):
    git(tmp_path, "init")
    (tmp_path / "conversion.py").write_text("# conversion\n")
    git(tmp_path, "add", "conversion.py")
    git(tmp_path, "-c", "user.name=t", "-c", "user.email=t@example.invalid",
        "commit", "-m", "conversion")
    expected = git(tmp_path, "rev-parse", "HEAD")
    final = landing.publish(tmp_path, "events", "v1",
                            lambda directory: (directory / "part.parquet").write_bytes(b"abc"),
                            acquisitions=[acquisition(tmp_path)])
    assert json.loads((final / "publication.json").read_text())["conversion_commit"] == expected


@pytest.mark.parametrize("rejection", ["raises", "false"])
def test_publish_keeps_rejected_validation_unpublished(tmp_path, rejection):
    def validate(directory):
        assert (directory / "part.parquet").read_bytes() == b"abc"
        if rejection == "raises":
            raise LookupError("validation failed")
        return False

    error = LookupError if rejection == "raises" else ValueError
    with pytest.raises(error):
        landing.publish(tmp_path, "events", "v1",
                        lambda directory: (directory / "part.parquet").write_bytes(b"abc"),
                        acquisitions=[acquisition(tmp_path)], validate=validate)
    partial = tmp_path / "data/parquet/events/v1.partial"
    assert (partial / "part.parquet").read_bytes() == b"abc"
    assert not (partial / "publication.json").exists()
    assert not tmp_path.joinpath("data/parquet/events/v1").exists()


@pytest.mark.parametrize("invalid", ["empty", "missing", "partial", "incomplete", "malformed", "non-object"])
def test_publish_rejects_incomplete_acquisitions_before_creating_output(tmp_path, invalid):
    original = tmp_path / "data/raw/api/batch-1"
    if invalid == "partial":
        original = original.with_name("batch-1.partial")
    original.mkdir(parents=True)
    if invalid in {"partial", "incomplete"}:
        (original / "provenance.json").write_text(json.dumps({"status": "pending"}))
    elif invalid == "malformed":
        (original / "provenance.json").write_text("invalid json")
    elif invalid == "non-object":
        (original / "provenance.json").write_text("[]")
    called = []
    with pytest.raises(ValueError):
        landing.publish(tmp_path, "events", "v1", lambda path: called.append(path),
                        acquisitions=[] if invalid == "empty" else [original])
    assert called == []
    assert not (tmp_path / "data/parquet").exists()


@pytest.mark.parametrize("field", ["dataset", "publication_id"])
@pytest.mark.parametrize("value", ["", ".", "..", "a/b", "a\\b", "v1.partial"])
def test_publish_rejects_invalid_identifiers_before_conversion(tmp_path, field, value):
    names = {"dataset": "events", "publication_id": "v1"}
    names[field] = value
    called = []
    with pytest.raises(ValueError):
        landing.publish(tmp_path, **names, convert=lambda path: called.append(path),
                        acquisitions=[acquisition(tmp_path)])
    assert called == []
    assert not (tmp_path / "data/parquet").exists()


@pytest.mark.parametrize("suffix", ["", ".partial"])
def test_publish_refuses_existing_id_before_conversion(tmp_path, suffix):
    original = acquisition(tmp_path)
    existing = tmp_path / f"data/parquet/events/v1{suffix}"
    existing.mkdir(parents=True)
    (existing / "keep.txt").write_text("keep")
    called = []
    with pytest.raises(FileExistsError) as error:
        landing.publish(tmp_path, "events", "v1", lambda path: called.append(path),
                        acquisitions=[original])
    assert str(existing) in str(error.value)
    assert called == []
    assert (existing / "keep.txt").read_text() == "keep"
    if not suffix:
        assert not existing.with_name("v1.partial").exists()


@pytest.mark.parametrize("output", ["empty", "reserved", "raises"])
def test_publish_keeps_invalid_conversion_unpublished(tmp_path, output):
    def convert(directory):
        if output == "reserved":
            (directory / "publication.json").write_text("caller metadata")
        elif output == "raises":
            (directory / "part.parquet").write_bytes(b"abc")
            raise LookupError("conversion failed")

    error = LookupError if output == "raises" else ValueError
    with pytest.raises(error):
        landing.publish(tmp_path, "events", "v1", convert,
                        acquisitions=[acquisition(tmp_path)])
    partial = tmp_path / "data/parquet/events/v1.partial"
    assert partial.is_dir()
    if output == "reserved":
        assert (partial / "publication.json").read_text() == "caller metadata"
    else:
        assert not (partial / "publication.json").exists()
    assert not tmp_path.joinpath("data/parquet/events/v1").exists()


def test_publish_without_git_still_records_uncommitted(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", str(tmp_path / "no-executables"))
    final = landing.publish(tmp_path, "events", "v1",
                            lambda directory: (directory / "part.parquet").write_bytes(b"abc"),
                            acquisitions=[acquisition(tmp_path)])
    assert json.loads((final / "publication.json").read_text())["conversion_commit"] == "uncommitted"


def test_publish_removes_its_metadata_when_rename_fails(tmp_path, monkeypatch):
    original = acquisition(tmp_path)

    def fail_rename(source, destination):
        raise OSError("rename failed")

    monkeypatch.setattr("os.rename", fail_rename)
    with pytest.raises(OSError, match="rename failed"):
        landing.publish(tmp_path, "events", "v1",
                        lambda directory: (directory / "part.parquet").write_bytes(b"abc"),
                        acquisitions=[original])
    partial = tmp_path / "data/parquet/events/v1.partial"
    assert (partial / "part.parquet").read_bytes() == b"abc"
    assert not (partial / "publication.json").exists()
    assert not tmp_path.joinpath("data/parquet/events/v1").exists()


def test_retain_copies_and_verifies_then_reports_existing_copy(tmp_path):
    root = tmp_path / "project"
    original = acquisition(root)
    location = tmp_path / "storage"
    destination = location / "data/raw/api/batch-1"
    assert landing.retain(str(root), original.relative_to(root), str(location)) == {
        "destination": str(destination), "copied": True, "conflict": False, "discrepancies": [],
    }
    assert sorted(path.name for path in destination.iterdir()) == ["page.json", "provenance.json"]
    assert (destination / "page.json").read_bytes() == b"abc"
    assert (destination / "provenance.json").read_bytes() == (original / "provenance.json").read_bytes()
    assert not destination.with_name("batch-1.partial").exists()
    assert landing.retain(root, original, location) == {
        "destination": str(destination), "copied": False, "conflict": True, "discrepancies": [],
    }


def test_retain_reports_checksum_discrepancy_without_changing_existing_copy(tmp_path):
    root = tmp_path / "project"
    original = acquisition(root)
    location = tmp_path / "storage"
    destination = location / "data/raw/api/batch-1"
    landing.retain(root, original, location)
    (destination / "page.json").write_bytes(b"changed")
    assert landing.retain(root, original, location) == {
        "destination": str(destination), "copied": False, "conflict": True,
        "discrepancies": ["sha256 differs: page.json"],
    }
    assert (destination / "page.json").read_bytes() == b"changed"


def test_retain_compares_full_recursive_lists_including_provenance(tmp_path):
    root = tmp_path / "project"
    original = acquisition(root)
    (original / "nested").mkdir()
    (original / "nested/extra-local.txt").write_bytes(b"abc")
    location = tmp_path / "storage"
    destination = location / "data/raw/api/batch-1"
    landing.retain(root, original, location)
    (destination / "nested/extra-local.txt").unlink()
    (destination / "nested/extra-destination.txt").write_text("extra")
    (destination / "provenance.json").write_text("changed")
    report = landing.retain(root, original, location)
    assert set(report["discrepancies"]) == {
        "missing at destination: nested/extra-local.txt",
        "extra at destination: nested/extra-destination.txt",
        "sha256 differs: provenance.json",
    }
    assert not (destination / "nested/extra-local.txt").exists()
    assert (destination / "nested/extra-destination.txt").read_text() == "extra"
    assert (destination / "provenance.json").read_text() == "changed"


@pytest.mark.parametrize("invalid", ["outside", "partial", "missing-provenance", "pending", "symlink", "non-object"])
def test_retain_requires_completed_acquisition_under_resolved_raw_directory(tmp_path, invalid):
    root = tmp_path / "project"
    original = tmp_path / "elsewhere/api/batch-1" if invalid == "outside" else root / "data/raw/api/batch-1"
    if invalid == "partial":
        original = original.with_name("batch-1.partial")
    original.mkdir(parents=True)
    (original / "page.json").write_bytes(b"abc")
    if invalid == "non-object":
        (original / "provenance.json").write_text("null")
    elif invalid != "missing-provenance":
        (original / "provenance.json").write_text(json.dumps({
            "status": "pending" if invalid == "pending" else "complete",
        }))
    if invalid == "symlink":
        outside = tmp_path / "outside"
        original.rename(outside)
        original.symlink_to(outside, target_is_directory=True)
    location = tmp_path / "storage"
    with pytest.raises(ValueError):
        landing.retain(root, original, location)
    assert not location.exists()


def test_retain_refuses_leftover_partial_without_touching_it(tmp_path):
    root = tmp_path / "project"
    original = acquisition(root)
    location = tmp_path / "storage"
    partial = location / "data/raw/api/batch-1.partial"
    partial.mkdir(parents=True)
    (partial / "keep.txt").write_text("keep")
    with pytest.raises(FileExistsError) as error:
        landing.retain(root, original, location)
    assert str(partial) in str(error.value)
    assert (partial / "keep.txt").read_text() == "keep"
    assert not partial.with_name("batch-1").exists()


def test_retain_reports_a_broken_destination_symlink_as_a_conflict(tmp_path):
    root = tmp_path / "project"
    original = acquisition(root)
    location = tmp_path / "storage"
    destination = location / "data/raw/api/batch-1"
    destination.parent.mkdir(parents=True)
    target = tmp_path / "absent"
    destination.symlink_to(target, target_is_directory=True)
    report = landing.retain(root, original, location)
    assert report == {
        "destination": str(destination), "copied": False, "conflict": True,
        "discrepancies": ["missing at destination: page.json", "missing at destination: provenance.json"],
    }
    assert destination.is_symlink()
    assert destination.readlink() == target


def test_retain_refuses_destination_created_during_copy(tmp_path, monkeypatch):
    root = tmp_path / "project"
    original = acquisition(root)
    location = tmp_path / "storage"
    destination = location / "data/raw/api/batch-1"
    copytree = shutil.copytree

    def copy_while_destination_appears(source, partial):
        copytree(source, partial)
        destination.mkdir()

    monkeypatch.setattr("shutil.copytree", copy_while_destination_appears)
    with pytest.raises(FileExistsError) as error:
        landing.retain(root, original, location)
    assert str(destination) in str(error.value)
    assert list(destination.iterdir()) == []
    partial = destination.with_name("batch-1.partial")
    assert (partial / "page.json").read_bytes() == b"abc"
    assert (partial / "provenance.json").read_bytes() == (original / "provenance.json").read_bytes()


def test_session_explains_missing_duckdb_dependency(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "duckdb", None)
    with pytest.raises(ImportError, match=r"session\(\).*duckdb.*package"):
        landing.session(tmp_path)


def test_session_loads_views_in_name_order_without_recursing(tmp_path):
    pytest.importorskip("duckdb")
    views = tmp_path / "foundation/views"
    views.mkdir(parents=True)
    (views / "02_derived.sql").write_text("CREATE VIEW derived AS SELECT n * 2 AS doubled FROM base;")
    (views / "01_base.sql").write_text("CREATE VIEW base AS SELECT 3 AS n UNION ALL SELECT 5;")
    (views / "ignored.txt").write_text("invalid SQL")
    (views / "nested").mkdir()
    (views / "nested/03_unused.sql").write_text("invalid SQL")
    with landing.session(tmp_path) as connection:
        assert connection.execute("SELECT doubled FROM derived ORDER BY doubled").fetchall() == [(6,), (10,)]


def test_session_resolves_project_paths_from_another_working_directory(tmp_path, monkeypatch):
    pytest.importorskip("duckdb")
    root = tmp_path / "project's data"
    views = root / "foundation/views"
    views.mkdir(parents=True)
    (root / "data").mkdir()
    (root / "data/x.csv").write_text("n\n7\n9\n")
    (views / "01_numbers.sql").write_text("CREATE VIEW numbers AS SELECT * FROM read_csv('data/x.csv');")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    with landing.session(str(root)) as connection:
        assert connection.execute("SELECT n FROM numbers ORDER BY n").fetchall() == [(7,), (9,)]


def test_session_names_failing_view_and_closes_connection(tmp_path, monkeypatch):
    duckdb = pytest.importorskip("duckdb")
    views = tmp_path / "foundation/views"
    views.mkdir(parents=True)
    failing = views / "01_invalid.sql"
    failing.write_text("CREATE VIEW invalid AS SELECT * FROM absent;")
    connection = duckdb.connect()
    monkeypatch.setattr(duckdb, "connect", lambda: connection)
    with pytest.raises(RuntimeError) as error:
        landing.session(tmp_path)
    assert str(failing) in str(error.value)
    assert isinstance(error.value.__cause__, duckdb.Error)
    with pytest.raises(duckdb.Error, match="closed"):
        connection.execute("SELECT 1")


def test_session_with_missing_views_directory_opens_an_empty_session(tmp_path):
    pytest.importorskip("duckdb")
    with landing.session(tmp_path) as connection:
        assert connection.execute("SELECT 42").fetchall() == [(42,)]
        assert connection.execute("SHOW TABLES").fetchall() == []


@pytest.mark.parametrize("absolute", [False, True])
def test_session_accepts_custom_views_directory(tmp_path, absolute):
    pytest.importorskip("duckdb")
    views = tmp_path / "custom"
    views.mkdir()
    (views / "01_answer.sql").write_text("CREATE VIEW answer AS SELECT 42 AS n;")
    with landing.session(tmp_path, views_dir=views if absolute else "custom") as connection:
        assert connection.execute("SELECT n FROM answer").fetchall() == [(42,)]


@pytest.mark.parametrize("records", [[3], {"page.json": "3"}, {"page.json": None}])
def test_land_requires_a_dictionary_of_integer_record_counts(tmp_path, records):
    with pytest.raises(ValueError):
        landing.land(tmp_path, "api", "batch-1",
                     lambda directory: (directory / "page.json").write_bytes(b"abc"),
                     request="query", records=records)
    partial = tmp_path / "data/raw/api/batch-1.partial"
    assert partial.is_dir()
    assert not (partial / "provenance.json").exists()


def test_land_refuses_destination_created_during_fetch(tmp_path):
    final = tmp_path / "data/raw/api/batch-1"

    def fetch(directory):
        (directory / "page.json").write_bytes(b"abc")
        final.mkdir()

    with pytest.raises(FileExistsError):
        landing.land(tmp_path, "api", "batch-1", fetch, request="query")
    assert list(final.iterdir()) == []
    partial = tmp_path / "data/raw/api/batch-1.partial"
    assert (partial / "page.json").read_bytes() == b"abc"
    assert not (partial / "provenance.json").exists()


def test_land_removes_its_provenance_when_rename_fails(tmp_path, monkeypatch):
    def fail_rename(source, destination):
        raise OSError("rename failed")

    monkeypatch.setattr("os.rename", fail_rename)
    with pytest.raises(OSError, match="rename failed"):
        landing.land(tmp_path, "api", "batch-1",
                     lambda directory: (directory / "page.json").write_bytes(b"abc"),
                     request="query")
    partial = tmp_path / "data/raw/api/batch-1.partial"
    assert (partial / "page.json").read_bytes() == b"abc"
    assert not (partial / "provenance.json").exists()
    assert not tmp_path.joinpath("data/raw/api/batch-1").exists()


@pytest.mark.parametrize("suffix", ["", ".partial"])
def test_land_refuses_existing_id_before_fetch(tmp_path, suffix):
    existing = tmp_path / f"data/raw/api/batch-1{suffix}"
    existing.mkdir(parents=True)
    (existing / "keep.txt").write_text("keep")
    called = []
    with pytest.raises(FileExistsError) as error:
        landing.land(tmp_path, "api", "batch-1", lambda path: called.append(path),
                     request="query")
    assert str(existing) in str(error.value)
    assert called == []
    assert (existing / "keep.txt").read_text() == "keep"
    if not suffix:
        assert not existing.with_name("batch-1.partial").exists()


@pytest.mark.parametrize("field", ["source", "acquisition_id"])
@pytest.mark.parametrize("value", ["", ".", "..", "a/b", "a\\b", "batch.partial"])
def test_land_rejects_invalid_identifiers_before_fetch(tmp_path, field, value):
    names = {"source": "api", "acquisition_id": "batch-1"}
    names[field] = value
    called = []
    with pytest.raises(ValueError):
        landing.land(tmp_path, **names, fetch=lambda path: called.append(path), request="query")
    assert called == []
    assert not (tmp_path / "data").exists()


@pytest.mark.parametrize("bad_output", ["empty", "reserved", "unknown-records"])
def test_land_rejects_invalid_output_without_provenance(tmp_path, bad_output):
    def fetch(directory):
        if bad_output == "reserved":
            (directory / "provenance.json").write_text("caller metadata")
        elif bad_output == "unknown-records":
            (directory / "page.json").write_bytes(b"abc")

    with pytest.raises(ValueError):
        landing.land(tmp_path, "api", "batch-1", fetch, request="query",
                     records={"absent.json": 1} if bad_output == "unknown-records" else None)
    partial = tmp_path / "data/raw/api/batch-1.partial"
    assert partial.is_dir()
    if bad_output == "reserved":
        assert (partial / "provenance.json").read_text() == "caller metadata"
    else:
        assert not (partial / "provenance.json").exists()
    assert not tmp_path.joinpath("data/raw/api/batch-1").exists()
