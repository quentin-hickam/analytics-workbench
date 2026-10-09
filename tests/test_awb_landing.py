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
# test_cli_land_copies_files_retains_and_writes_ledger_rows: land command copies files and directories byte for byte, retains them, writes the Acquisitions row and marks the source acquired.
# test_cli_land_skips_unusable_retention_location: unrecorded, none chosen, unreachable and non-filesystem locations skip retention and record this checkout only.
# test_cli_land_lands_without_a_ledger_and_reports_the_missing_row: missing sources.md still lands and exits 1 naming the unwritten row.
# test_cli_land_refuses_unusable_inputs_before_landing: missing inputs, clashing names and malformed record counts exit 2 before landing.
# test_cli_retain_retains_unretained_acquisitions_and_fills_their_rows: retain command writes missing rows without a location, then retains and updates rows once one is recorded, then does nothing.
# test_cli_retain_reports_a_discrepant_existing_copy: a discrepant existing copy exits 1 and leaves the row this checkout only.
# test_cli_publish_converts_checks_and_records_the_select: publish command writes Parquet from a project-relative select, runs the check, and records SQL checksums and rows.
# test_cli_publish_keeps_a_failed_check_or_empty_result_unpublished: check rows or an empty select keep the partial directory unpublished and print the failures.
# test_cli_publish_requires_from_to_name_exactly_what_the_select_reads: --from naming other or extra acquisitions exits 2 before conversion.

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


WORKBENCH = ASSET.parent / "workbench"


def workbench(root, location="not yet recorded"):
    """A project holding the template README and sources register, with one candidate source."""
    (root / "foundation").mkdir(parents=True)
    readme = (WORKBENCH / "README.md").read_text(encoding="utf-8")
    (root / "README.md").write_text(readme.replace(
        "Landed data is kept at: not yet recorded", f"Landed data is kept at: {location}"))
    sources = (WORKBENCH / "foundation/sources.md").read_text(encoding="utf-8")
    delimiter = "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
    (root / "foundation/sources.md").write_text(sources.replace(
        delimiter, delimiter + "| orders | ERP | one row per order | Ann | file | fit | candidate | |\n", 1))
    return root


def run(capsys, command, root, *argv):
    status = command(root, [str(arg) for arg in argv])
    return status, json.loads(capsys.readouterr().out)


def acquisition_rows(root):
    lines = (root / "foundation/sources.md").read_text().split("## Acquisitions")[1].splitlines()
    rows = [line for line in lines if line.startswith("|")][2:]
    return [[cell.strip() for cell in row.strip("|").split("|")] for row in rows]


def test_cli_land_copies_files_retains_and_writes_ledger_rows(tmp_path, capsys):
    storage = tmp_path / "storage"
    storage.mkdir()
    root = workbench(tmp_path / "project", storage)
    received = tmp_path / "received"
    (received / "pages").mkdir(parents=True)
    (received / "orders.csv").write_bytes(b"id\r\n1\r\n2\r\n")
    (received / "pages/1.json").write_bytes(b"{}")
    status, out = run(capsys, landing.cli_land, root, "orders", "r1", received / "orders.csv",
                      received / "pages", "--request", "email from Ann", "--records", "orders.csv=2",
                      "--notes", "a|b")
    assert status == 0
    acquired = root / "data/raw/orders/r1"
    destination = storage / "data/raw/orders/r1"
    assert out == {"landed": "data/raw/orders/r1/", "files": 2, "bytes": 12,
                   "retention": {"destination": str(destination), "copied": True, "conflict": False,
                                 "discrepancies": []},
                   "ledger": {"row": "added", "source_status": "acquired"}}
    assert (acquired / "orders.csv").read_bytes() == b"id\r\n1\r\n2\r\n"
    assert (destination / "pages/1.json").read_bytes() == b"{}"
    provenance = json.loads((acquired / "provenance.json").read_text())
    assert provenance["request"] == "email from Ann"
    assert [file["records"] for file in provenance["files"]] == [2, None]
    # The escaped pipe in Notes splits under this test's naive parser.
    assert acquisition_rows(root) == [[
        "r1", "orders", provenance["completed_at"], "email from Ann", "`data/raw/orders/r1/`",
        f"`{destination}`",
        "2 files, 12 bytes; SHA-256 per file in provenance.json; records: orders.csv 2", "", "a\\",
        "b"]]
    assert "| orders | ERP | one row per order | Ann | file | fit | acquired |  |" in (
        root / "foundation/sources.md").read_text()


@pytest.mark.parametrize("location, skipped", [("not yet recorded", "unrecorded"),
                                               ("none chosen", "none chosen"),
                                               ("`../absent`", "unreachable"),
                                               ("s3://bucket/raw", "not a filesystem path")])
def test_cli_land_skips_unusable_retention_location(tmp_path, capsys, location, skipped):
    root = workbench(tmp_path, location)
    (tmp_path / "orders.csv").write_bytes(b"id\n1\n")
    status, out = run(capsys, landing.cli_land, root, "orders", "r1", tmp_path / "orders.csv")
    assert status == 0
    assert out["retention"]["skipped"] == skipped
    assert acquisition_rows(root)[0][3:6] == [
        f"copied from {(tmp_path / 'orders.csv').resolve()}", "`data/raw/orders/r1/`",
        "this checkout only"]


def test_cli_land_lands_without_a_ledger_and_reports_the_missing_row(tmp_path, capsys):
    (tmp_path / "orders.csv").write_bytes(b"id\n1\n")
    status, out = run(capsys, landing.cli_land, tmp_path, "orders", "r1", tmp_path / "orders.csv")
    assert status == 1
    assert (tmp_path / "data/raw/orders/r1/orders.csv").read_bytes() == b"id\n1\n"
    assert out["retention"]["skipped"] == "unrecorded"
    assert out["ledger"]["row"] == "not written"
    assert "sources.md" in out["ledger"]["error"]


def test_cli_land_refuses_unusable_inputs_before_landing(tmp_path, capsys):
    (tmp_path / "a").mkdir()
    (tmp_path / "a/x.csv").write_bytes(b"1")
    (tmp_path / "x.csv").write_bytes(b"2")
    for argv in ([tmp_path / "missing.csv"], [tmp_path / "x.csv", tmp_path / "a/x.csv"],
                 [tmp_path / "x.csv", "--records", "x.csv=many"]):
        with pytest.raises(SystemExit) as error:
            landing.cli_land(tmp_path, ["orders", "r1", *map(str, argv)])
        assert error.value.code == 2
    assert not (tmp_path / "data").exists()


def test_cli_retain_retains_unretained_acquisitions_and_fills_their_rows(tmp_path, capsys):
    root = workbench(tmp_path / "project")
    (tmp_path / "orders.csv").write_bytes(b"id\n1\n")
    run(capsys, landing.cli_land, root, "orders", "r1", tmp_path / "orders.csv")
    landing.land(root, "orders", "r2", lambda output: (output / "page.json").write_bytes(b"{}"),
                 request={"page": 1})
    (root / "data/raw/orders/r3.partial").mkdir()
    status, out = run(capsys, landing.cli_retain, root)
    assert status == 0
    assert out["location"]["skipped"] == "unrecorded"
    assert out["acted_on"] == [{"acquisition": "data/raw/orders/r2/",
                                "ledger": {"row": "added", "source_status": "acquired"}}]
    assert out["still_this_checkout_only"] == 1
    storage = tmp_path / "storage"
    storage.mkdir()
    readme = root / "README.md"
    readme.write_text(readme.read_text().replace("kept at: not yet recorded", "kept at: ../storage", 1))
    status, out = run(capsys, landing.cli_retain, root)
    assert status == 0
    assert [(item["acquisition"], item["retention"]["copied"], item["ledger"]["row"])
            for item in out["acted_on"]] == [("data/raw/orders/r1/", True, "updated"),
                                             ("data/raw/orders/r2/", True, "updated")]
    rows = acquisition_rows(root)
    storage = storage.resolve()
    assert [row[5] for row in rows] == [f"`{storage / 'data/raw/orders/r1'}`",
                                        f"`{storage / 'data/raw/orders/r2'}`"]
    assert rows[1][3] == '{"page": 1}'
    status, out = run(capsys, landing.cli_retain, root)
    assert (status, out["acted_on"], out["already_retained"]) == (0, [], 2)


def test_cli_retain_reports_a_discrepant_existing_copy(tmp_path, capsys):
    storage = tmp_path / "storage"
    root = workbench(tmp_path / "project", storage)
    (tmp_path / "orders.csv").write_bytes(b"id\n1\n")
    run(capsys, landing.cli_land, root, "orders", "r1", tmp_path / "orders.csv")
    (storage / "data/raw/orders/r1").mkdir(parents=True)
    status, out = run(capsys, landing.cli_retain, root)
    assert status == 1
    assert out["acted_on"][0]["retention"]["discrepancies"] == [
        "missing at destination: orders.csv", "missing at destination: provenance.json"]
    assert out["acted_on"][0]["ledger"]["row"] == "unchanged"
    assert acquisition_rows(root)[0][5] == "this checkout only"


def published_project(tmp_path, capsys):
    root = workbench(tmp_path / "project")
    (tmp_path / "orders.csv").write_bytes(b"id,amount\n1,10\n2,20\n")
    run(capsys, landing.cli_land, root, "orders", "r1", tmp_path / "orders.csv")
    (root / "prep").mkdir()
    (root / "prep/orders.sql").write_text(
        "SELECT id, amount * 2 AS doubled FROM read_csv('data/raw/orders/r1/orders.csv');\n")
    return root


def test_cli_publish_converts_checks_and_records_the_select(tmp_path, capsys, monkeypatch):
    duckdb = pytest.importorskip("duckdb")
    root = published_project(tmp_path, capsys)
    (root / "prep/check.sql").write_text("SELECT * FROM publication WHERE doubled IS NULL")
    monkeypatch.chdir(tmp_path)
    status, out = run(capsys, landing.cli_publish, root, "orders", "v1", "--from", "data/raw/orders/r1",
                      "--sql", "prep/orders.sql", "--check", "prep/check.sql", "--notes", "first")
    assert status == 0
    final = root / "data/parquet/orders/v1"
    assert out["published"] == "data/parquet/orders/v1/"
    assert out["rows"] == 2
    assert out["inputs"] == ["data/raw/orders/r1"]
    assert out["catalog_row"] == ("| orders | Parquet publication |  | `data/raw/orders/r1/` | "
                                  "`data/parquet/orders/v1/` | `prep/orders.sql` | "
                                  "`prep/check.sql` returns no rows |  |")
    assert duckdb.sql(f"SELECT * FROM '{final / 'orders.parquet'}' ORDER BY id").fetchall() == [
        (1, 20), (2, 40)]
    publication = json.loads((final / "publication.json").read_text())
    assert [file["path"] for file in publication["files"]] == ["orders.parquet"]
    assert publication["inputs"][0]["acquisition_id"] == "r1"
    assert publication["notes"] == {
        "select": "prep/orders.sql",
        "select_sha256": hashlib.sha256((root / "prep/orders.sql").read_bytes()).hexdigest(),
        "check": "prep/check.sql",
        "check_sha256": hashlib.sha256((root / "prep/check.sql").read_bytes()).hexdigest(),
        "rows": 2, "comment": "first"}


@pytest.mark.parametrize("check, failing", [("SELECT * FROM publication WHERE doubled > 30", 1),
                                            (None, 0)])
def test_cli_publish_keeps_a_failed_check_or_empty_result_unpublished(tmp_path, capsys, check, failing):
    pytest.importorskip("duckdb")
    root = published_project(tmp_path, capsys)
    argv = ["orders", "v1", "--from", "data/raw/orders/r1", "--sql", "prep/orders.sql"]
    if check:
        (root / "prep/check.sql").write_text(check)
        argv += ["--check", "prep/check.sql"]
    else:
        (root / "prep/orders.sql").write_text(
            "SELECT * FROM read_csv('data/raw/orders/r1/orders.csv') WHERE id > 5")
    status, out = run(capsys, landing.cli_publish, root, *argv)
    assert status == 1
    assert out["published"] is False
    assert out["partial"] == "data/parquet/orders/v1.partial"
    assert out.get("failing_rows", 0) == failing
    if failing:
        assert out["first"] == [{"id": 2, "doubled": 40}]
    assert not (root / "data/parquet/orders/v1").exists()
    assert not (root / "data/parquet/orders/v1.partial/publication.json").exists()


def test_cli_publish_requires_from_to_name_exactly_what_the_select_reads(tmp_path, capsys):
    root = published_project(tmp_path, capsys)
    landing.land(root, "orders", "r2", lambda output: (output / "orders.csv").write_bytes(b"id\n3\n"),
                 request="second")
    for acquisitions in (["data/raw/orders/r2"], ["data/raw/orders/r1", "data/raw/orders/r2"]):
        with pytest.raises(SystemExit) as error:
            landing.cli_publish(root, ["orders", "v1", "--from", *acquisitions,
                                       "--sql", "prep/orders.sql"])
        assert error.value.code == 2
        assert "--from must name exactly" in capsys.readouterr().err
    assert not (root / "data/parquet").exists()
