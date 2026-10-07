# Kept cases:
# test_land_writes_complete_provenance_and_publishes_directory: provenance schema/key order, metadata-relative paths, checksums and partial rename.
# test_land_keeps_failed_fetch_unpublished: fetch failure keeps partial files and writes no provenance.
# test_publish_records_inputs_and_uncommitted_conversion: publication schema/key order, path bases, copied input checksums, no-commit state and partial rename.
# test_publish_records_resolved_head: publication conversion_commit records the producing Git HEAD.
# test_publish_keeps_rejected_validation_unpublished: raised and False validation failures keep partial files and write no publication.
# test_publish_refuses_existing_id_before_conversion: existing completed publication is refused before conversion.
# test_publish_keeps_invalid_conversion_unpublished: raised conversion failure keeps partial files and writes no publication.
# test_retain_copies_and_verifies_then_reports_existing_copy: verified copy succeeds; second call reports conflict without overwriting.
# test_retain_reports_checksum_discrepancy_without_changing_existing_copy: changed retained copy reports a discrepancy without overwriting.
# test_session_loads_views_in_name_order_without_recursing: session loads two views with the second depending on the first.
# test_session_resolves_project_paths_from_another_working_directory: session resolves project-relative paths from another working directory.
# test_session_names_failing_view_and_closes_connection: regression: failed view loading closes the session connection.
# test_land_refuses_existing_id_before_fetch: existing completed acquisition is refused before fetching.
# test_retain_requires_source_and_acquisition_directly_under_raw: regression: retain enforces source/acquisition depth under data/raw.
# test_session_refuses_a_project_root_containing_a_comma: regression: comma-containing project root is rejected before opening a connection.

import hashlib
import importlib.util
import json
import subprocess
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


def test_publish_refuses_existing_id_before_conversion(tmp_path):
    original = acquisition(tmp_path)
    existing = tmp_path / "data/parquet/events/v1"
    existing.mkdir(parents=True)
    (existing / "keep.txt").write_text("keep")
    called = []
    with pytest.raises(FileExistsError) as error:
        landing.publish(tmp_path, "events", "v1", lambda path: called.append(path),
                        acquisitions=[original])
    assert str(existing) in str(error.value)
    assert called == []
    assert (existing / "keep.txt").read_text() == "keep"
    assert not existing.with_name("v1.partial").exists()


def test_publish_keeps_invalid_conversion_unpublished(tmp_path):
    def convert(directory):
        (directory / "part.parquet").write_bytes(b"abc")
        raise LookupError("conversion failed")

    with pytest.raises(LookupError):
        landing.publish(tmp_path, "events", "v1", convert,
                        acquisitions=[acquisition(tmp_path)])
    partial = tmp_path / "data/parquet/events/v1.partial"
    assert partial.is_dir()
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


def test_land_refuses_existing_id_before_fetch(tmp_path):
    existing = tmp_path / "data/raw/api/batch-1"
    existing.mkdir(parents=True)
    (existing / "keep.txt").write_text("keep")
    called = []
    with pytest.raises(FileExistsError) as error:
        landing.land(tmp_path, "api", "batch-1", lambda path: called.append(path),
                     request="query")
    assert str(existing) in str(error.value)
    assert called == []
    assert (existing / "keep.txt").read_text() == "keep"
    assert not existing.with_name("batch-1.partial").exists()


def test_retain_requires_source_and_acquisition_directly_under_raw(tmp_path):
    root = tmp_path / "project"
    nested = landing.land(root, "api", "batch-1",
                          lambda directory: (directory / "page.json").write_bytes(b"abc"),
                          request="query")
    deeper = nested / "part" / "inner"
    deeper.mkdir(parents=True)
    (deeper / "provenance.json").write_text(json.dumps({"status": "complete"}))
    location = tmp_path / "storage"
    with pytest.raises(ValueError):
        landing.retain(root, deeper, location)
    with pytest.raises(ValueError):
        landing.retain(root, nested.parent, location)
    assert not location.exists()


def test_session_refuses_a_project_root_containing_a_comma(tmp_path, monkeypatch):
    duckdb = pytest.importorskip("duckdb")
    opened = []
    monkeypatch.setattr(duckdb, "connect", lambda: opened.append(1))
    root = tmp_path / "a,b"
    root.mkdir()
    with pytest.raises(ValueError, match="comma"):
        landing.session(root)
    assert opened == []
