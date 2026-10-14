# Kept cases:
# test_land_writes_complete_provenance_and_publishes_directory: provenance schema/key order, metadata-relative paths, checksums and partial rename.
# test_land_records_upstream_validators_the_fetch_supplies: upstream fields filled during fetch are recorded per file in fixed key order, with null for absent fields and files.
# test_land_refuses_malformed_upstream_unpublished: unknown fields, blank or non-string values, unlanded files, an invalid url or an http(s) url without a host, with an invalid port, or with a space or control character, and a url with userinfo (with or without //) or credential-named query, fragment, or path parameters (each split on & or ;, names percent-decoded), session IDs, pass, and api_sig among them, keep the acquisition partial, and the refusal echoes no secret.
# test_land_records_a_url_whose_parameters_name_no_credential: an @ outside the host, path and query parameters split on & or ;, names that merely contain a credential word, an IPv6 host with a port, and an s3 URL are recorded as given.
# test_land_keeps_failed_fetch_unpublished: fetch failure keeps partial files and writes no provenance.
# test_publish_records_inputs_and_uncommitted_conversion: publication schema/key order, path bases, copied input checksums, no-commit state and partial rename.
# test_publish_records_resolved_head: publication conversion_commit records the producing Git HEAD.
# test_publish_keeps_rejected_validation_unpublished: raised and False validation failures keep partial files and write no publication.
# test_publish_refuses_existing_id_before_conversion: existing completed publication is refused before conversion.
# test_publish_keeps_invalid_conversion_unpublished: raised conversion failure keeps partial files and writes no publication.
# test_retain_copies_and_verifies_then_reports_existing_copy: verified copy succeeds and matches; a second call reports the identical existing copy as matched, not a conflict.
# test_retain_reports_checksum_discrepancy_without_changing_existing_copy: changed retained copy reports a conflict and a discrepancy, unmatched, without overwriting.
# test_session_loads_views_in_name_order_without_recursing: session loads two views with the second depending on the first.
# test_session_resolves_project_paths_from_another_working_directory: session resolves project-relative paths from another working directory.
# test_session_names_failing_view_and_closes_connection: regression: failed view loading closes the session connection.
# test_land_refuses_existing_id_before_fetch: existing completed acquisition is refused before fetching.
# test_retain_requires_source_and_acquisition_directly_under_raw: regression: retain enforces source/acquisition depth under data/raw.
# test_session_refuses_a_project_root_containing_a_comma: regression: comma-containing project root is rejected before opening a connection.
# test_cli_sql_prints_first_rows_and_total_and_writes_full_result: sql runs a project-relative query file or SQL text, prints a capped Markdown table and the total, and writes CSV or Parquet.
# test_cli_sql_reports_failures_on_one_line: SQL errors, failing view files and non-query SQL print one stderr line and return 1; a bad --out extension is a usage error.
# test_cli_land_copies_files_retains_and_writes_ledger_rows: land command copies files and directories byte for byte, retains them, writes the Acquisitions row and marks the source acquired.
# test_cli_land_skips_unusable_retention_location: unrecorded, none chosen, unreachable and non-filesystem locations skip retention and record this checkout only.
# test_cli_land_creates_a_missing_ledger_from_the_template: missing sources.md is written from the template with the row, reported as created.
# test_sources_template_matches_the_installed_register: SOURCES_TEMPLATE is byte-equal to the shipped foundation/sources.md.
# test_cli_land_reports_a_ledger_without_an_acquisitions_table: an existing sources.md without an Acquisitions table is left unchanged and exits 1.
# test_cli_land_refuses_unusable_inputs_before_landing: missing inputs, clashing names and malformed record counts exit 2 before landing.
# test_cli_retain_retains_unretained_acquisitions_and_fills_their_rows: retain command writes missing rows without a location, then retains and updates rows once one is recorded, then does nothing.
# test_cli_retain_reports_a_discrepant_existing_copy: a discrepant existing copy exits 1 and leaves the row this checkout only.
# test_cli_publish_converts_checks_and_records_the_select: publish command writes Parquet from a project-relative select, runs the check, and records SQL checksums and rows.
# test_cli_publish_view_sql_loads_through_session: the printed view_sql escapes the dataset name and loads as a view file.
# test_cli_publish_keeps_a_failed_check_or_empty_result_unpublished: check rows or an empty select keep the partial directory unpublished and print the failures.
# test_cli_publish_requires_from_to_name_exactly_what_the_select_reads: --from naming other or extra acquisitions exits 2 before conversion.
# test_cli_options_take_one_value_each_and_may_precede_positionals: repeated --records and --from flags parse in any position, as the usage line prints them.
# test_publish_records_validate_detail_and_no_checks_by_default: without declared checks publication.json records no declared check; a string validate returns is its check's detail; another dataset's declaration does not apply.
# test_declared_checks_refuse_a_malformed_declaration_before_conversion: unknown and malformed keys, an empty columns list, range bounds other than numbers or dates, a min above its max (date-times compared in UTC), an empty column name in a table form, two checks sharing a name, a column repeated within a key or unique entry, one unique column set declared twice, a non-checks key, an unknown top-level table, another dataset's malformed entry, and invalid TOML refuse before any partial directory exists.
# test_a_dotted_dataset_name_is_declared_quoted_and_refused_unquoted: [datasets.orders.v1.checks] refuses publishing orders.v1, naming the quoted spelling, before conversion; [datasets."orders.v1".checks] declares its checks.
# test_declared_checks_accept_the_shipped_template_and_its_example: the shipped commented template declares nothing, and its example, uncommented, is a valid declaration.
# test_publish_refuses_declared_checks_without_duckdb_before_conversion: declared checks without the duckdb package refuse before any partial directory exists.
# test_publish_runs_declared_checks_and_records_them: every declared check kind runs in DuckDB over the partial Parquet and is recorded by name, in the documented key order whatever the declaration order, before validate's check.
# test_publish_keeps_a_failing_declared_check_unpublished: a failing declared check raises ChecksFailed listing every check, skips validate, and leaves the partial unpublished.
# test_declared_check_failures_report_counts_not_values: each failing kind reports counts, a row count with no min from 0; a check that cannot compare its declared values fails without quoting DuckDB's message.
# test_a_timestamp_column_takes_date_time_range_bounds: date-time bounds keep a TIMESTAMP's last day inside the range, where a date max ends at its midnight.
# test_a_check_that_declares_no_values_fails_to_run_without_the_values_hint: a check that cannot run for another reason names the error's kind without pointing at declared values.
# test_declared_columns_and_types_hold_in_every_parquet_file: columns and types are checked in each Parquet file, so a second file with another type or without a declared column fails; files differing only in column order pass.
# test_a_partition_column_is_typed_from_every_path_together: a hive partition column, stored in no file, is typed as the files read together type it, so a NULL partition or mixed '1'/'A' partition values pass their declared type and another type fails.
# test_temporal_checks_compare_in_utc_whatever_the_host_zone: date and date-time bounds and values compare with plain and zoned timestamps in UTC, giving the same records under two host time zones.
# test_range_bounds_may_mix_local_and_offset_date_times: a local and an offset date-time bound one range, ordered and compared in UTC.
# test_a_null_key_is_not_also_counted_as_a_repeated_key: a key check counts rows with a null key column once, and repeats among complete keys only.
# test_unreadable_or_missing_parquet_fails_every_declared_check: a file that is not Parquet, or no Parquet file, fails every declared check with ChecksFailed rather than a DuckDB error.
# test_a_declaration_that_plans_no_check_needs_neither_duckdb_nor_parquet: empty check lists plan nothing, so publish needs no duckdb and no Parquet output.
# test_cli_publish_records_declared_checks: the publish command records declared checks with its --check outcome, counts them in its output and catalog_row (one check passes, several pass), and prints failed_checks on refusal.

import hashlib
import importlib.util
import json
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
         "records": None, "upstream": None},
        {"path": "nested/page.json", "bytes": 3, "sha256": hashlib.sha256(b"abc").hexdigest(),
         "records": 3, "upstream": None},
    ]
    for name in ("started_at", "completed_at"):
        timestamp = datetime.fromisoformat(provenance[name])
        assert timestamp.utcoffset() is not None
        assert timestamp.microsecond == 0
    assert raw.endswith("\n")
    assert raw.startswith('{\n  "source": "api",\n')


def test_land_records_upstream_validators_the_fetch_supplies(tmp_path):
    upstream = {}

    def fetch(directory):
        (directory / "a.csv").write_bytes(b"a")
        (directory / "b.csv").write_bytes(b"b")
        (directory / "c.csv").write_bytes(b"c")
        upstream["a.csv"] = {"url": "https://example.test/v;rev=2/a.csv?format=csv;page=2", "etag": '"v1"',
                             "last_modified": "Tue, 13 Oct 2026 08:00:00 GMT"}
        upstream["b.csv"] = {"url": "s3://bucket/b.csv", "version_id": "3HL4kqtJ"}
        upstream["c.csv"] = {"etag": None}

    final = landing.land(tmp_path, "api", "batch-1", fetch, request="query", upstream=upstream)
    files = json.loads((final / "provenance.json").read_text(encoding="utf-8"))["files"]
    assert [list(file) for file in files] == [["path", "bytes", "sha256", "records", "upstream"]] * 3
    assert list(files[0]["upstream"]) == ["url", "etag", "last_modified", "version_id"]
    assert [file["upstream"] for file in files] == [
        {"url": "https://example.test/v;rev=2/a.csv?format=csv;page=2", "etag": '"v1"',
         "last_modified": "Tue, 13 Oct 2026 08:00:00 GMT", "version_id": None},
        {"url": "s3://bucket/b.csv", "etag": None, "last_modified": None, "version_id": "3HL4kqtJ"},
        None,
    ]


@pytest.mark.parametrize("upstream, message", [
    ({"page.json": {"url": "https://example.test", "md5": "x"}}, "upstream fields of page.json"),
    ({"page.json": {"etag": " "}}, "nonblank strings"),
    ({"page.json": {"etag": 7}}, "nonblank strings"),
    ({"page.json": "https://example.test"}, "upstream fields of page.json"),
    ({"other.json": {"etag": '"v1"'}}, "not landed"),
    (["page.json"], "dictionary of per-file"),
    ({"page.json": {"url": "https://user:SECRET@api.example.test/x"}}, "user name or password"),
    ({"page.json": {"url": "https://SECRET@api.example.test/x"}}, "user name or password"),
    ({"page.json": {"url": "https://api.example.test/x?page=2&api_key=SECRET"}}, r"parameters \(api_key\)"),
    ({"page.json": {"url": "https://b.s3.example.test/x?X-Amz-Credential=SECRET&X-Amz-Signature=SECRET"}},
     r"parameters \(X-Amz-Credential, X-Amz-Signature\)"),
    ({"page.json": {"url": "https://a.blob.example.test/x?sv=2024&sig=SECRET"}}, r"parameters \(sig\)"),
    ({"page.json": {"url": "https://api.example.test/x#access_token=SECRET"}}, r"parameters \(access_token\)"),
    ({"page.json": {"url": "https://api.example.test/x?a=1;api_key=SECRET"}}, r"parameters \(api_key\)"),
    ({"page.json": {"url": "https://api.example.test/x;token=SECRET/page"}}, r"parameters \(token\)"),
    ({"page.json": {"url": "https://api.example.test/x#a=1;access_token=SECRET"}}, r"parameters \(access_token\)"),
    ({"page.json": {"url": "user:SECRET@api.example.test/x"}}, "user name or password"),
    ({"page.json": {"url": "https:user:SECRET@api.example.test/x"}}, "user name or password"),
    ({"page.json": {"url": "https://user:pw@api.example.test/x?api_key=SECRET"}}, "user name or password"),
    ({"page.json": {"url": "https://api.example.test/x;format=csv&access_token=SECRET"}}, r"parameters \(access_token\)"),
    ({"page.json": {"url": "https://api.example.test/x;a=1;token=SECRET"}}, r"parameters \(token\)"),
    ({"page.json": {"url": "https://api.example.test/x;jsessionid=SECRET"}}, r"parameters \(jsessionid\)"),
    ({"page.json": {"url": "https://api.example.test/x?sessionid=SECRET"}}, r"parameters \(sessionid\)"),
    ({"page.json": {"url": "https://api.example.test/x?PHPSESSID=SECRET"}}, r"parameters \(PHPSESSID\)"),
    ({"page.json": {"url": "https://api.example.test/x?sid=SECRET"}}, r"parameters \(sid\)"),
    ({"page.json": {"url": "https://api.example.test/x?jwt=SECRET"}}, r"parameters \(jwt\)"),
    ({"page.json": {"url": "https://api.example.test/x?%61pi_key=SECRET"}}, r"parameters \(api_key\)"),
    ({"page.json": {"url": "https://api.example.test/x?api%5Fkey=SECRET"}}, r"parameters \(api_key\)"),
    ({"page.json": {"url": "https://cdn.example.test/x?Expires=1&Signature=SECRET"}}, r"parameters \(Signature\)"),
    ({"page.json": {"url": "https://storage.example.test/x?X-Goog-Credential=SECRET"}}, r"parameters \(X-Goog-Credential\)"),
    ({"page.json": {"url": "https://api.example.test/x?auth_token=SECRET"}}, r"parameters \(auth_token\)"),
    # The check goes by name alone, so content parameters with credential-like names are refused too (landing.md).
    ({"page.json": {"url": "https://api.example.test/x?sortkey=date"}}, r"parameters \(sortkey\)"),
    ({"page.json": {"url": "https://api.example.test/x?primary_key=id"}}, r"parameters \(primary_key\)"),
    ({"page.json": {"url": "https://x.test/a?user=bob&pass=SECRET"}}, r"parameters \(pass\)"),
    ({"page.json": {"url": "https://x.test/a?api_sig=SECRET"}}, r"parameters \(api_sig\)"),
    ({"page.json": {"url": "https://x.test/a?apisig=SECRET"}}, r"parameters \(apisig\)"),
    ({"page.json": {"url": "https://[", "etag": '"v1"'}}, "is not a valid URL"),
    # An http(s) URL a request cannot be sent to as recorded.
    ({"page.json": {"url": "https://", "etag": '"v1"'}}, "is not a valid URL: an http.s. URL needs a host"),
    ({"page.json": {"url": "http:/nohost", "etag": '"v1"'}}, "is not a valid URL: an http.s. URL needs a host"),
    ({"page.json": {"url": "https://:443/x", "etag": '"v1"'}}, "is not a valid URL: an http.s. URL needs a host"),
    ({"page.json": {"url": "https://api.test:bad/x", "etag": '"v1"'}}, "is not a valid URL: its port"),
    ({"page.json": {"url": "https://api.test:99999/x", "etag": '"v1"'}}, "is not a valid URL: its port"),
    ({"page.json": {"url": "https://api.test/a b.csv", "etag": '"v1"'}}, "no space or control character"),
    ({"page.json": {"url": "https://api.test/a.csv\n", "etag": '"v1"'}}, "no space or control character"),
])
def test_land_refuses_malformed_upstream_unpublished(tmp_path, upstream, message):
    with pytest.raises(ValueError, match=message) as refused:
        landing.land(tmp_path, "api", "batch-1",
                     lambda directory: (directory / "page.json").write_bytes(b"abc"),
                     request="query", upstream=upstream)
    assert "SECRET" not in str(refused.value)
    assert not tmp_path.joinpath("data/raw/api/batch-1").exists()
    assert not (tmp_path / "data/raw/api/batch-1.partial/provenance.json").exists()


@pytest.mark.parametrize("url", [
    "https://registry.example.test/@scope/pkg",
    "https://api.example.test/x?q=a@b",
    "https://api.example.test/x?code=abc",
    "https://api.example.test/x;format=csv&page=2",
    "https://api.example.test/v;rev=2/x?format=csv;page=2#section=3",
    "https://api.example.test/x?monkeys=3&tokenize=yes&keyword=sky",
    "https://api.example.test/x?compass=north&passage=2&signal=1",
    "https://[::1]:8443/x",
    "s3://bucket/x.csv",
    # Only a name=value piece is a parameter (landing.md), so an anchor named like a credential is recorded.
    "https://api.example.test/x#session",
    "https://api.example.test/x?page=2#token",
])
def test_land_records_a_url_whose_parameters_name_no_credential(tmp_path, url):
    final = landing.land(tmp_path, "api", "batch-1", lambda directory: (directory / "page.json").write_bytes(b"abc"),
                         request="query", upstream={"page.json": {"url": url}})
    assert json.loads((final / "provenance.json").read_text(encoding="utf-8"))["files"][0]["upstream"]["url"] == url


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
                                "converted_at", "files", "checks", "notes"]
    assert publication["dataset"] == "events"
    assert publication["publication_id"] == "v1"
    assert publication["conversion_commit"] == "uncommitted"
    assert publication["inputs"] == [{
        "source": "api", "acquisition_id": "batch-1",
        "files": [{"path": "page.json", "sha256": hashlib.sha256(b"abc").hexdigest()}],
    }]
    assert publication["files"] == [{"path": "nested/part.parquet", "bytes": 3,
                                     "sha256": hashlib.sha256(b"abc").hexdigest()}]
    assert publication["checks"] == [
        {"name": "validate", "outcome": "pass", "detail": "The validate callable passed."}]
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
        "destination": str(destination), "copied": True, "conflict": False, "matched": True,
        "discrepancies": [],
    }
    assert sorted(path.name for path in destination.iterdir()) == ["page.json", "provenance.json"]
    assert (destination / "page.json").read_bytes() == b"abc"
    assert (destination / "provenance.json").read_bytes() == (original / "provenance.json").read_bytes()
    assert not destination.with_name("batch-1.partial").exists()
    before = {path: path.stat().st_mtime_ns for path in destination.iterdir()}
    assert landing.retain(root, original, location) == {
        "destination": str(destination), "copied": False, "conflict": False, "matched": True,
        "discrepancies": [],
    }
    assert {path: path.stat().st_mtime_ns for path in destination.iterdir()} == before


def test_retain_reports_checksum_discrepancy_without_changing_existing_copy(tmp_path):
    root = tmp_path / "project"
    original = acquisition(root)
    location = tmp_path / "storage"
    destination = location / "data/raw/api/batch-1"
    landing.retain(root, original, location)
    (destination / "page.json").write_bytes(b"changed")
    assert landing.retain(root, original, location) == {
        "destination": str(destination), "copied": False, "conflict": True, "matched": False,
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


def sql_project(root):
    views = root / "foundation/views"
    views.mkdir(parents=True)
    (views / "01_orders.sql").write_text(
        "CREATE VIEW orders AS SELECT range AS id, 'a|b' AS note FROM range(5);")
    (root / "queries").mkdir()
    (root / "queries/large.sql").write_text("SELECT id FROM orders WHERE id >= 1 ORDER BY id;\n")


def test_cli_sql_prints_first_rows_and_total_and_writes_full_result(tmp_path, monkeypatch, capsys):
    duckdb = pytest.importorskip("duckdb")
    sql_project(tmp_path)
    monkeypatch.chdir(tmp_path.parent)  # the query file and --out are project-relative
    assert landing.cli_sql(tmp_path, ["queries/large.sql", "--limit", "2",
                                      "--out", "out/large.csv"]) == 0
    assert capsys.readouterr().out == (
        "| id |\n|---|\n| 1 |\n| 2 |\n2 of 4 rows shown; full result in out/large.csv\n")
    assert (tmp_path / "out/large.csv").read_text().split() == ["id", "1", "2", "3", "4"]
    assert landing.cli_sql(tmp_path, ["SELECT note, NULL AS gap FROM orders LIMIT 1",
                                      "--out", "out/note.parquet"]) == 0
    assert capsys.readouterr().out == (
        "| note | gap |\n|---|---|\n| a\\|b | NULL |\n"
        "1 of 1 rows shown; full result in out/note.parquet\n")
    with duckdb.connect() as connection:
        assert connection.execute("SELECT * FROM read_parquet(?)",
                                  [str(tmp_path / "out/note.parquet")]).fetchall() == [("a|b", None)]


def test_cli_sql_reports_failures_on_one_line(tmp_path, capsys):
    pytest.importorskip("duckdb")
    sql_project(tmp_path)
    for query in ("SELECT * FROM absent", "CREATE TABLE t AS SELECT 1"):
        assert landing.cli_sql(tmp_path, [query]) == 1
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err.startswith("sql: ") and captured.err.count("\n") == 1
    failing = tmp_path / "foundation/views/02_invalid.sql"
    failing.write_text("CREATE VIEW invalid AS SELECT * FROM absent;")
    assert landing.cli_sql(tmp_path, ["SELECT 1"]) == 1
    error = capsys.readouterr().err
    assert str(failing) in error and "absent" in error and error.count("\n") == 1
    with pytest.raises(SystemExit) as exit:
        landing.cli_sql(tmp_path, ["SELECT 1", "--out", "result.json"])
    assert exit.value.code == 2
    assert not (tmp_path / "result.json").exists()
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
                                 "matched": True, "discrepancies": []},
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


def test_cli_land_creates_a_missing_ledger_from_the_template(tmp_path, capsys):
    (tmp_path / "orders.csv").write_bytes(b"id\n1\n")
    status, out = run(capsys, landing.cli_land, tmp_path, "orders", "r1", tmp_path / "orders.csv")
    assert status == 0
    assert (tmp_path / "data/raw/orders/r1/orders.csv").read_bytes() == b"id\n1\n"
    assert out["retention"]["skipped"] == "unrecorded"
    assert out["ledger"] == {"row": "added", "source_status": "missing", "created": True}
    text = (tmp_path / "foundation/sources.md").read_text(encoding="utf-8")
    assert text.startswith(landing.SOURCES_TEMPLATE.split("## Acquisitions")[0])
    assert [row[:2] + row[4:6] for row in acquisition_rows(tmp_path)] == [
        ["r1", "orders", "`data/raw/orders/r1/`", "this checkout only"]]
    landing.land(tmp_path, "orders", "r2", lambda output: (output / "a.csv").write_bytes(b"id\n2\n"),
                 request="second")
    status, out = run(capsys, landing.cli_retain, tmp_path)
    assert status == 0
    assert out["acted_on"][0]["ledger"] == {"row": "added", "source_status": "missing"}


def test_sources_template_matches_the_installed_register():
    assert landing.SOURCES_TEMPLATE.encode("utf-8") == (WORKBENCH / "foundation/sources.md").read_bytes()


def test_cli_land_reports_a_ledger_without_an_acquisitions_table(tmp_path, capsys):
    (tmp_path / "foundation").mkdir()
    (tmp_path / "foundation/sources.md").write_text("# Source register\n")
    (tmp_path / "orders.csv").write_bytes(b"id\n1\n")
    status, out = run(capsys, landing.cli_land, tmp_path, "orders", "r1", tmp_path / "orders.csv")
    assert status == 1
    assert (tmp_path / "data/raw/orders/r1/orders.csv").read_bytes() == b"id\n1\n"
    assert out["ledger"]["row"] == "not written"
    assert "Acquisitions" in out["ledger"]["error"]
    assert (tmp_path / "foundation/sources.md").read_text() == "# Source register\n"


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
            landing.cli_publish(root, ["orders", "v1", *(arg for a in acquisitions for arg in ("--from", a)),
                                       "--sql", "prep/orders.sql"])
        assert error.value.code == 2
        assert "--from must name exactly" in capsys.readouterr().err
    assert not (root / "data/parquet").exists()


def test_cli_options_take_one_value_each_and_may_precede_positionals(tmp_path, capsys):
    root = workbench(tmp_path / "project")
    (tmp_path / "a.csv").write_bytes(b"id\n1\n")
    (tmp_path / "b.csv").write_bytes(b"id\n2\n3\n")
    status, out = run(capsys, landing.cli_land, root, "--records", "a.csv=1", "--records", "b.csv=2",
                      "orders", "r1", tmp_path / "a.csv", tmp_path / "b.csv")
    assert status == 0 and out["files"] == 2
    provenance = json.loads((root / "data/raw/orders/r1/provenance.json").read_text())
    assert [file["records"] for file in provenance["files"]] == [1, 2]
    pytest.importorskip("duckdb")
    landing.land(root, "orders", "r2", lambda output: (output / "c.csv").write_bytes(b"id\n4\n"),
                 request="second")
    (root / "prep").mkdir()
    (root / "prep/orders.sql").write_text(
        "SELECT * FROM read_csv('data/raw/orders/r1/*.csv') UNION ALL "
        "SELECT * FROM read_csv('data/raw/orders/r2/c.csv')")
    status, out = run(capsys, landing.cli_publish, root, "--from", "data/raw/orders/r1",
                      "--from", "data/raw/orders/r2", "--sql", "prep/orders.sql", "orders", "v1")
    assert status == 0
    assert out["inputs"] == ["data/raw/orders/r1", "data/raw/orders/r2"] and out["rows"] == 4


@pytest.mark.parametrize("dataset", ["orders", "order-items", "o'brien", 'say"hi'])
def test_cli_publish_view_sql_loads_through_session(tmp_path, capsys, dataset):
    pytest.importorskip("duckdb")
    root = published_project(tmp_path, capsys)
    status, out = run(capsys, landing.cli_publish, root, dataset, "v1", "--from", "data/raw/orders/r1",
                      "--sql", "prep/orders.sql")
    assert status == 0
    name = '"' + dataset.replace('"', '""') + '"'
    location = f"data/parquet/{dataset}/v1/{dataset}.parquet".replace("'", "''")
    assert out["view_sql"] == f"CREATE VIEW {name} AS SELECT * FROM read_parquet('{location}');"
    assert list(out).index("view_sql") < list(out).index("catalog_row")
    (root / "foundation/views").mkdir()
    (root / "foundation/views/01_view.sql").write_text(out["view_sql"] + "\n", encoding="utf-8")
    with landing.session(root) as connection:
        assert connection.execute(f"SELECT * FROM {name} ORDER BY id").fetchall() == [(1, 20), (2, 40)]


def declare(root, text):
    (root / "foundation").mkdir(parents=True, exist_ok=True)
    (root / "foundation/datasets.toml").write_text(text)


def test_publish_records_validate_detail_and_no_checks_by_default(tmp_path):
    pytest.importorskip("tomllib")
    declare(tmp_path, '[datasets.other.checks]\nnot_null = ["id"]\n')

    def convert(directory):
        (directory / "part.parquet").write_bytes(b"abc")

    original = acquisition(tmp_path)
    final = landing.publish(tmp_path, "events", "v1", convert, acquisitions=[original],
                            validate=lambda directory: "  Three rows,\n all dated.  ")
    assert json.loads((final / "publication.json").read_text())["checks"] == [
        {"name": "validate", "outcome": "pass", "detail": "Three rows, all dated."}]
    final = landing.publish(tmp_path, "events", "v2", convert, acquisitions=[original])
    assert json.loads((final / "publication.json").read_text())["checks"] == []


@pytest.mark.parametrize("text, message", [
    ('[datasets.events.checks]\nnulls = ["id"]\n', "unknown check nulls"),
    ('[datasets.events.checks]\nnot_null = "id"\n', "checks.not_null is malformed"),
    ('[datasets.events.checks]\nkey = []\n', "checks.key is malformed"),
    ('[datasets.events.checks]\nrange = { amount = { low = 0 } }\n', "checks.range is malformed"),
    ('[datasets.events.checks]\nrange = { amount = { min = [0, 1] } }\n', "checks.range is malformed"),
    ('[datasets.events.checks]\nrange = { amount = { min = { at = 0 } } }\n', "checks.range is malformed"),
    ('[datasets.events.checks]\nrange = { amount = { min = "10" } }\n', "checks.range is malformed"),
    ('[datasets.events.checks]\nrange = { amount = { max = nan } }\n', "checks.range is malformed"),
    ('[datasets.events.checks]\nrange = { amount = { min = 10, max = 0 } }\n', "checks.range is malformed"),
    ('[datasets.events.checks]\nrange = { day = { min = 0, max = 2024-01-01 } }\n', "checks.range is malformed"),
    ('[datasets.events.checks]\nrange = { ts = { min = 2024-01-01, max = 2024-01-02T00:00:00 } }\n',
     "checks.range is malformed"),
    ('[datasets.events.checks]\nrange = { ts = { min = 2024-01-01T08:00:00, max = 2024-01-01T09:00:00+02:00 } }\n',
     "checks.range is malformed"),
    ('[datasets.events.checks]\ntypes = { "" = "INTEGER" }\n', "checks.types is malformed"),
    ('[datasets.events.checks]\naccepted_values = { "" = [1] }\n', "checks.accepted_values is malformed"),
    ('[datasets.events.checks]\nrange = { "" = { min = 0 } }\n', "checks.range is malformed"),
    ('[datasets.events.checks]\nrow_count = { min = -1 }\n', "checks.row_count is malformed"),
    ('[datasets.events.checks]\nrow_count = { min = 5, max = 1 }\n', "checks.row_count is malformed"),
    ('[dataset.events.checks]\nnot_null = ["id"]\n', "unknown table dataset"),
    ('[datasets.events.checks]\ntypes = { id = "INT; DROP" }\n', "checks.types is malformed"),
    ('[datasets.events]\ncheck = { key = ["id"] }\n', "holds only a checks table"),
    ('[datasets.events.checks]\ncolumns = []\n', "checks.columns is malformed"),
    ('[datasets.events.checks]\nunique = ["a,b", ["a", "b"]]\n', "more than one declared check is named unique:a,b"),
    ('[datasets.events.checks]\nnot_null = ["id", "id"]\n', "more than one declared check is named not_null:id"),
    ('[datasets.events.checks]\nkey = ["id", "id"]\n', "checks.key is malformed"),
    ('[datasets.events.checks]\nunique = [["id", "id"]]\n', "checks.unique is malformed"),
    ('[datasets.events.checks]\nunique = [["a", "b"], ["b", "a"]]\n', "checks.unique declares the columns a,b more than once"),
    ('[datasets.orders.v1.checks]\nnot_null = ["id"]\n', r'quote its name: \[datasets."orders.v1".checks\]'),
    ('[datasets.other.checks]\nnulls = ["id"]\n', r'\[datasets.other\]: unknown check nulls'),
    ('[datasets.events.checks\n', "foundation/datasets.toml"),
])
def test_declared_checks_refuse_a_malformed_declaration_before_conversion(tmp_path, text, message):
    pytest.importorskip("tomllib")
    original = acquisition(tmp_path)
    declare(tmp_path, text)
    called = []
    with pytest.raises(ValueError, match=message):
        landing.publish(tmp_path, "events", "v1", lambda path: called.append(path), acquisitions=[original])
    assert called == []
    assert not (tmp_path / "data/parquet").exists()


def test_a_dotted_dataset_name_is_declared_quoted_and_refused_unquoted(tmp_path):
    pytest.importorskip("tomllib")
    original = acquisition(tmp_path)
    declare(tmp_path, '[datasets.orders.v1.checks]\nnot_null = ["id"]\n')
    called = []
    with pytest.raises(ValueError, match=r'\[datasets.orders\] holds only a checks table; to declare checks for '
                                         r'the dataset orders.v1, quote its name: \[datasets."orders.v1".checks\]'):
        landing.publish(tmp_path, "orders.v1", "p1", called.append, acquisitions=[original])
    assert called == []
    assert not (tmp_path / "data/parquet").exists()
    declare(tmp_path, '[datasets."orders.v1".checks]\nnot_null = ["id"]\n')
    assert landing.declared_checks(tmp_path, "orders.v1") == {"not_null": ["id"]}
    assert landing.declared_checks(tmp_path, "orders") == {}


def test_declared_checks_accept_the_shipped_template_and_its_example(tmp_path):
    pytest.importorskip("tomllib")
    text = (ASSET.parent / "workbench/foundation/datasets.toml").read_text()
    declare(tmp_path, text)
    assert landing.declared_checks(tmp_path, "orders") == {}
    example = text.split("# [datasets.orders.checks]", 1)[1]
    declare(tmp_path, "[datasets.orders.checks]\n" + "\n".join(line[2:] for line in example.splitlines()))
    assert set(landing.declared_checks(tmp_path, "orders")) == set(landing.CHECK_KEYS) - {"unique"}


def test_publish_refuses_declared_checks_without_duckdb_before_conversion(tmp_path, monkeypatch):
    pytest.importorskip("tomllib")
    original = acquisition(tmp_path)
    declare(tmp_path, '[datasets.events.checks]\nnot_null = ["id"]\n')
    monkeypatch.setitem(sys.modules, "duckdb", None)  # import duckdb raises ImportError
    called = []
    with pytest.raises(ImportError, match="declared checks need the duckdb package"):
        landing.publish(tmp_path, "events", "v1", called.append, acquisitions=[original])
    assert called == []
    assert not (tmp_path / "data/parquet").exists()


def parquet_convert(duckdb, select):
    def convert(directory):
        (directory / "part").mkdir()
        duckdb.execute(f"COPY ({select}) TO '{directory / 'part/data.parquet'}' (FORMAT parquet)")
        (directory / "README.txt").write_text("not data")
    return convert


ROWS = ("SELECT * FROM (VALUES (1, 'open', 5.0, DATE '2024-01-02', 'a'), (2, 'shipped', 0.0, DATE '2024-06-30', NULL), "
        "(3, 'open', NULL, DATE '2024-03-01', NULL)) AS t(id, status, amount, day, email)")
ALL_KINDS = """
[datasets.events.checks]
row_count = { min = 1, max = 3 }
columns = ["id", "status", "amount"]
types = { id = "INT", status = "TEXT", day = "DATE" }
not_null = ["id", "day"]
key = ["id", "status"]
unique = ["email", ["status", "day"]]
accepted_values = { status = ["open", "shipped"] }
range = { amount = { min = 0 }, day = { min = 2024-01-01, max = 2024-06-30 } }
"""


def test_publish_runs_declared_checks_and_records_them(tmp_path):
    duckdb = pytest.importorskip("duckdb")
    declare(tmp_path, ALL_KINDS)
    final = landing.publish(tmp_path, "events", "v1", parquet_convert(duckdb, ROWS),
                            acquisitions=[acquisition(tmp_path)], validate=lambda directory: None)
    checks = json.loads((final / "publication.json").read_text())["checks"]
    assert [check["name"] for check in checks] == [
        "columns", "types:id", "types:status", "types:day", "not_null:id", "not_null:day", "key:id,status",
        "unique:email", "unique:status,day", "accepted_values:status", "range:amount", "range:day",
        "row_count", "validate"]
    assert {check["outcome"] for check in checks} == {"pass"}
    details = {check["name"]: check["detail"] for check in checks}
    assert details["types:id"] == "id is INTEGER."
    assert details["types:status"] == "status is VARCHAR."
    assert details["key:id,status"] == "3 rows, each key complete and unique."
    assert details["unique:email"] == "No repeated values in 3 rows; nulls are not compared."
    assert details["range:day"] == "No value outside [2024-01-01, 2024-06-30] in 3 rows."
    assert details["row_count"] == "3 rows, within [1, 3]."


def test_publish_keeps_a_failing_declared_check_unpublished(tmp_path):
    duckdb = pytest.importorskip("duckdb")
    declare(tmp_path, '[datasets.events.checks]\nnot_null = ["id", "amount"]\nrow_count = { min = 1 }\n')
    validated = []
    with pytest.raises(landing.ChecksFailed) as error:
        landing.publish(tmp_path, "events", "v1", parquet_convert(duckdb, ROWS),
                        acquisitions=[acquisition(tmp_path)], validate=validated.append)
    assert str(error.value) == "Declared checks failed: not_null:amount (1 of 3 rows are null)"
    assert isinstance(error.value, ValueError)
    assert [(check["name"], check["outcome"]) for check in error.value.checks] == [
        ("not_null:id", "pass"), ("not_null:amount", "fail"), ("row_count", "pass")]
    assert validated == []
    partial = tmp_path / "data/parquet/events/v1.partial"
    assert (partial / "part/data.parquet").is_file()
    assert not (partial / "publication.json").exists()
    assert not (tmp_path / "data/parquet/events/v1").exists()


def test_declared_check_failures_report_counts_not_values(tmp_path):
    duckdb = pytest.importorskip("duckdb")
    declare(tmp_path, """
[datasets.events.checks]
columns = ["id", "missing_a", "missing_b"]
types = { id = "VARCHAR", day = "NOT_A_TYPE", gone = "INT" }
key = ["status"]
unique = [["status"]]
accepted_values = { status = ["open"], id = ["secret-value"] }
range = { amount = { max = 1 }, status = { min = 5 } }
row_count = { max = 2 }
""")
    with pytest.raises(landing.ChecksFailed) as error:
        landing.publish(tmp_path, "events", "v1", parquet_convert(duckdb, ROWS),
                        acquisitions=[acquisition(tmp_path)])
    details = {check["name"]: (check["outcome"], check["detail"]) for check in error.value.checks}
    assert details == {
        "columns": ("fail", "Missing columns: missing_a, missing_b."),
        "types:id": ("fail", "id is INTEGER, declared VARCHAR."),
        "types:day": ("fail", "Declared type NOT_A_TYPE is not a DuckDB type."),
        "types:gone": ("fail", "Missing column: gone."),
        "key:status": ("fail", "1 of 3 rows repeat a key."),
        "unique:status": ("fail", "1 of 3 rows repeat a value."),
        "accepted_values:status": ("fail", "1 of 3 rows hold a value outside the 1 accepted."),
        "accepted_values:id": ("fail", "The check could not run (BinderException); compare its declared "
                                       "values with the column's type."),
        "range:amount": ("fail", "1 of 3 rows fall outside [-inf, 1]."),
        "range:status": details["range:status"],
        "row_count": ("fail", "3 rows, outside [0, 2]."),
    }
    assert details["range:status"][0] == "fail" and "shipped" not in details["range:status"][1]
    assert "secret-value" not in str(error.value) and "shipped" not in str(error.value)


def test_a_timestamp_column_takes_date_time_range_bounds(tmp_path):
    duckdb = pytest.importorskip("duckdb")
    rows = "SELECT * FROM (VALUES (TIMESTAMP '2024-01-01 00:00'), (TIMESTAMP '2024-06-30 23:00')) AS t(ts)"
    declare(tmp_path, "[datasets.events.checks]\n"
                      "range = { ts = { min = 2024-01-01T00:00:00, max = 2024-06-30T23:59:59 } }\n")
    original = acquisition(tmp_path)
    final = landing.publish(tmp_path, "events", "v1", parquet_convert(duckdb, rows), acquisitions=[original])
    [check] = json.loads((final / "publication.json").read_text())["checks"]
    assert check == {"name": "range:ts", "outcome": "pass",
                     "detail": "No value outside [2024-01-01 00:00:00, 2024-06-30 23:59:59] in 2 rows."}
    declare(tmp_path, "[datasets.events.checks]\nrange = { ts = { min = 2024-01-01, max = 2024-06-30 } }\n")
    with pytest.raises(landing.ChecksFailed, match=r"range:ts \(1 of 2 rows fall outside"):
        landing.publish(tmp_path, "events", "v2", parquet_convert(duckdb, rows), acquisitions=[original])


def test_a_check_that_declares_no_values_fails_to_run_without_the_values_hint(tmp_path):
    duckdb = pytest.importorskip("duckdb")
    declare(tmp_path, '[datasets.events.checks]\nnot_null = ["status"]\n')

    def convert(directory):  # status is INTEGER in the first file, so the second's value cannot be read
        duckdb.execute(f"COPY (SELECT 1::INT AS status) TO '{directory / 'a.parquet'}' (FORMAT parquet)")
        duckdb.execute(f"COPY (SELECT 2147483648::BIGINT AS status) TO '{directory / 'b.parquet'}' (FORMAT parquet)")

    with pytest.raises(landing.ChecksFailed) as error:
        landing.publish(tmp_path, "events", "v1", convert, acquisitions=[acquisition(tmp_path)])
    [check] = error.value.checks
    assert check["name"] == "not_null:status" and check["outcome"] == "fail"
    assert check["detail"].startswith("The check could not run (") and check["detail"].endswith(").")


def two_files(duckdb, first, second):
    def convert(directory):
        for name, select in (("a.parquet", first), ("b.parquet", second)):
            duckdb.execute(f"COPY ({select}) TO '{directory / name}' (FORMAT parquet)")
    return convert


def test_declared_columns_and_types_hold_in_every_parquet_file(tmp_path):
    duckdb = pytest.importorskip("duckdb")
    original = acquisition(tmp_path)
    declare(tmp_path, '[datasets.events.checks]\ncolumns = ["id"]\ntypes = { id = "INT" }\n'
                      'not_null = ["id"]\nrow_count = { min = 1 }\n')
    # A reader takes the first file's schema: these files publish as one INTEGER id column.
    final = landing.publish(tmp_path, "events", "v1", two_files(duckdb, "SELECT 1::INT AS id, 'x' AS s",
                                                                "SELECT 'y' AS s, 2::INT AS id"),
                            acquisitions=[original])
    assert [check["detail"] for check in json.loads((final / "publication.json").read_text())["checks"]] == [
        "All 1 declared columns present.", "id is INTEGER.", "No nulls in 2 rows.", "2 rows, within [1, inf]."]
    with pytest.raises(landing.ChecksFailed) as error:
        landing.publish(tmp_path, "events", "v2", two_files(duckdb, "SELECT 1::INT AS id",
                                                            "SELECT 2147483648::BIGINT AS id"),
                        acquisitions=[original])
    assert [(check["name"], check["outcome"], check["detail"]) for check in error.value.checks][:2] == [
        ("columns", "pass", "All 1 declared columns present."),
        ("types:id", "fail", "id is BIGINT in 1 of 2 Parquet files, declared INTEGER.")]
    with pytest.raises(landing.ChecksFailed) as error:
        landing.publish(tmp_path, "events", "v3", two_files(duckdb, "SELECT 1::INT AS id", "SELECT 2 AS other"),
                        acquisitions=[original])
    assert [(check["name"], check["outcome"], check["detail"]) for check in error.value.checks] == [
        ("columns", "fail", "Missing column: id (from 1 of 2 Parquet files)."),
        ("types:id", "fail", "Missing column: id (from 1 of 2 Parquet files)."),
        ("not_null:id", "fail", "Missing column: id (from 1 of 2 Parquet files)."),
        ("row_count", "pass", "2 rows, within [1, inf].")]
    assert not (tmp_path / "data/parquet/events/v2").exists() and not (tmp_path / "data/parquet/events/v3").exists()


def partitioned(duckdb, select, column):
    def convert(directory):
        duckdb.execute(f"COPY ({select}) TO '{directory / 'out'}' (FORMAT parquet, PARTITION_BY ({column}))")
    return convert


def test_a_partition_column_is_typed_from_every_path_together(tmp_path):
    duckdb = pytest.importorskip("duckdb")
    original = acquisition(tmp_path)
    # Read alone, year=__HIVE_DEFAULT_PARTITION__ would type year VARCHAR and code=1 would type code BIGINT.
    declare(tmp_path, '[datasets.events.checks]\ncolumns = ["year", "x"]\ntypes = { year = "BIGINT", x = "INT" }\n')
    final = landing.publish(tmp_path, "events", "v1", partitioned(
        duckdb, "SELECT 2024::INTEGER AS year, 1 AS x UNION ALL SELECT NULL, 2", "year"), acquisitions=[original])
    assert [check["detail"] for check in json.loads((final / "publication.json").read_text())["checks"]] == [
        "All 2 declared columns present.", "year is BIGINT.", "x is INTEGER."]
    mixed = "SELECT '1' AS code, 1 AS x UNION ALL SELECT 'A', 2"
    declare(tmp_path, '[datasets.events.checks]\ntypes = { code = "VARCHAR" }\nnot_null = ["code"]\n')
    final = landing.publish(tmp_path, "events", "v2", partitioned(duckdb, mixed, "code"), acquisitions=[original])
    assert [check["detail"] for check in json.loads((final / "publication.json").read_text())["checks"]] == [
        "code is VARCHAR.", "No nulls in 2 rows."]
    declare(tmp_path, '[datasets.events.checks]\ntypes = { code = "BIGINT" }\n')
    with pytest.raises(landing.ChecksFailed) as error:
        landing.publish(tmp_path, "events", "v3", partitioned(duckdb, mixed, "code"), acquisitions=[original])
    assert [check["detail"] for check in error.value.checks] == ["code is VARCHAR, declared BIGINT."]


class Zoned:
    """duckdb whose new connections start in zone, as on a host set to that time zone."""

    def __init__(self, duckdb, zone):
        self.duckdb, self.zone = duckdb, zone

    def __getattr__(self, name):
        return getattr(self.duckdb, name)

    def connect(self, *args, **kwargs):
        connection = self.duckdb.connect(*args, **kwargs)
        connection.execute(f"SET TimeZone = '{self.zone}'")
        return connection


def test_temporal_checks_compare_in_utc_whatever_the_host_zone(tmp_path, monkeypatch):
    duckdb = pytest.importorskip("duckdb")
    original = acquisition(tmp_path)
    rows = ("SELECT TIMESTAMP '2024-01-01 00:30' AS ts, TIMESTAMPTZ '2024-01-01 00:30:00+00:00' AS tz, "
            "TIMESTAMPTZ '2024-01-01 00:30:00+00:00' AS tz_day")
    # Each bound casts one side between a plain and a zoned timestamp; in UTC every bound holds exactly.
    declare(tmp_path, "[datasets.events.checks]\n"
                      "accepted_values = { tz = [2024-01-01T00:30:00] }\n"
                      "range = { ts = { min = 2024-01-01T00:30:00Z, max = 2024-01-01T09:30:00+09:00 }, "
                      "tz = { min = 2024-01-01T00:30:00, max = 2024-01-01T00:30:00 }, "
                      "tz_day = { min = 2024-01-01, max = 2024-01-02 } }\n")
    recorded = []
    for publication, zone in (("v1", "America/New_York"), ("v2", "Asia/Tokyo")):
        monkeypatch.setattr(landing, "_duckdb", lambda: Zoned(duckdb, zone))
        final = landing.publish(tmp_path, "events", publication, parquet_convert(duckdb, rows),
                                acquisitions=[original])
        recorded.append(json.loads((final / "publication.json").read_text())["checks"])
    assert recorded[0] == recorded[1]
    assert [check["outcome"] for check in recorded[0]] == ["pass"] * 4
    declare(tmp_path, "[datasets.events.checks]\nrange = { ts = { min = 2024-01-01T00:31:00Z } }\n")
    for publication, zone in (("v3", "America/New_York"), ("v4", "Asia/Tokyo")):
        monkeypatch.setattr(landing, "_duckdb", lambda: Zoned(duckdb, zone))
        with pytest.raises(landing.ChecksFailed, match=r"range:ts \(1 of 1 rows fall outside"):
            landing.publish(tmp_path, "events", publication, parquet_convert(duckdb, rows), acquisitions=[original])


def test_range_bounds_may_mix_local_and_offset_date_times(tmp_path):
    duckdb = pytest.importorskip("duckdb")
    original = acquisition(tmp_path)
    rows = ("SELECT * FROM (VALUES (TIMESTAMP '2024-01-01 00:30', TIMESTAMPTZ '2024-01-01 00:30:00+00:00')) "
            "AS t(ts, tz)")
    # The max reads earlier than the min on the wall clock but is 01:00 UTC, after the local min.
    bounds = "{ min = 2024-01-01T00:00:00, max = 2023-12-31T20:00:00-05:00 }"
    declare(tmp_path, f"[datasets.events.checks]\nrange = {{ ts = {bounds}, tz = {bounds} }}\n")
    final = landing.publish(tmp_path, "events", "v1", parquet_convert(duckdb, rows), acquisitions=[original])
    checks = json.loads((final / "publication.json").read_text())["checks"]
    assert [(check["name"], check["outcome"]) for check in checks] == [("range:ts", "pass"), ("range:tz", "pass")]
    declare(tmp_path, "[datasets.events.checks]\n"
                      "range = { ts = { min = 2024-01-01T00:31:00Z, max = 2024-01-02T00:00:00 } }\n")
    with pytest.raises(landing.ChecksFailed, match=r"range:ts \(1 of 1 rows fall outside"):
        landing.publish(tmp_path, "events", "v2", parquet_convert(duckdb, rows), acquisitions=[original])


def test_a_null_key_is_not_also_counted_as_a_repeated_key(tmp_path):
    duckdb = pytest.importorskip("duckdb")
    declare(tmp_path, '[datasets.events.checks]\nkey = ["id"]\n')
    rows = "SELECT * FROM (VALUES (1), (NULL), (NULL), (2), (2)) AS t(id)"
    with pytest.raises(landing.ChecksFailed) as error:
        landing.publish(tmp_path, "events", "v1", parquet_convert(duckdb, rows), acquisitions=[acquisition(tmp_path)])
    assert error.value.checks == [{"name": "key:id", "outcome": "fail",
                                   "detail": "2 of 5 rows have a null key column; 1 of 5 rows repeat a key."}]


def test_unreadable_or_missing_parquet_fails_every_declared_check(tmp_path):
    pytest.importorskip("duckdb")
    original = acquisition(tmp_path)
    declare(tmp_path, '[datasets.events.checks]\nnot_null = ["id"]\nrow_count = { min = 1 }\n')
    for publication, convert, detail in (
            ("v1", lambda directory: (directory / "x.parquet").write_bytes(b"abc"),
             "x.parquet could not be read as Parquet ("),
            ("v2", lambda directory: (directory / "x.csv").write_text("id\n1\n"),
             "The publication holds no Parquet file.")):
        with pytest.raises(landing.ChecksFailed) as error:
            landing.publish(tmp_path, "events", publication, convert, acquisitions=[original])
        assert [check["name"] for check in error.value.checks] == ["not_null:id", "row_count"]
        assert all(check["outcome"] == "fail" and check["detail"].startswith(detail)
                   for check in error.value.checks)
        assert not (tmp_path / f"data/parquet/events/{publication}").exists()


def test_a_declaration_that_plans_no_check_needs_neither_duckdb_nor_parquet(tmp_path, monkeypatch):
    pytest.importorskip("tomllib")
    declare(tmp_path, "[datasets.events.checks]\nnot_null = []\nunique = []\n")
    monkeypatch.setitem(sys.modules, "duckdb", None)  # import duckdb raises ImportError
    final = landing.publish(tmp_path, "events", "v1", lambda directory: (directory / "x.csv").write_text("id\n"),
                            acquisitions=[acquisition(tmp_path)])
    assert json.loads((final / "publication.json").read_text())["checks"] == []


def test_cli_publish_records_declared_checks(tmp_path, capsys):
    pytest.importorskip("duckdb")
    root = published_project(tmp_path, capsys)
    (root / "prep/check.sql").write_text("SELECT * FROM publication WHERE doubled IS NULL")
    declare(root, '[datasets.orders.checks]\nkey = ["id"]\nrange = { doubled = { min = 0 } }\n')
    status, out = run(capsys, landing.cli_publish, root, "orders", "v1", "--from", "data/raw/orders/r1",
                      "--sql", "prep/orders.sql", "--check", "prep/check.sql")
    assert status == 0
    assert out["checks"] == 3
    assert ("| 2 declared checks in `foundation/datasets.toml` pass; `prep/check.sql` returns no rows |"
            in out["catalog_row"])
    checks = json.loads((root / "data/parquet/orders/v1/publication.json").read_text())["checks"]
    assert [(check["name"], check["outcome"]) for check in checks] == [
        ("key:id", "pass"), ("range:doubled", "pass"), ("validate", "pass")]
    assert checks[-1]["detail"] == "The select returned 2 rows; prep/check.sql returned none."
    declare(root, '[datasets.orders.checks]\nrange = { doubled = { max = 30 } }\n')
    status, out = run(capsys, landing.cli_publish, root, "orders", "v2", "--from", "data/raw/orders/r1",
                      "--sql", "prep/orders.sql")
    assert status == 1
    assert out["published"] is False
    assert out["error"] == "ChecksFailed: Declared checks failed: range:doubled (1 of 2 rows fall outside [-inf, 30])"
    assert out["failed_checks"] == [{"name": "range:doubled", "detail": "1 of 2 rows fall outside [-inf, 30]."}]
    assert out["partial"] == "data/parquet/orders/v2.partial"
    assert not (root / "data/parquet/orders/v2").exists()
    declare(root, '[datasets.orders.checks]\nrange = { doubled = { min = 0 } }\n')
    status, out = run(capsys, landing.cli_publish, root, "orders", "v3", "--from", "data/raw/orders/r1",
                      "--sql", "prep/orders.sql")
    assert status == 0
    assert "| 1 declared check in `foundation/datasets.toml` passes; nonzero row count |" in out["catalog_row"]
