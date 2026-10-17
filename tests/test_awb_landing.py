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
# test_sql_param_values_read_as_settings_values: a --param value is read as a one-line TOML value, so a date, number, boolean, quoted string, or array keeps its type, and other text, a value spanning lines included, is the string as given.
# test_sql_param_refuses_what_a_query_cannot_name: a --param without =, or whose name is not letters, digits, and _, is a usage error.
# test_cli_sql_binds_parameters_from_param_and_settings: with and without --read-only, --settings binds an investigation's [parameters] and --param wins over them, each statement getting only the names it uses with their types kept, writing nothing; a missing, unreadable, or misnamed settings investigation fails on one line, and a bad --param exits 2.
# test_cli_sql_plan_failures_name_the_fix_and_keep_read_only: under --read-only, an unbound parameter, an ambiguous column, and another binder error return DuckDB's error on one line with its likely fix and never suggest dropping --read-only; without it, an unbound parameter gets the same fix; profile, which binds none, answers an unbound parameter with a fix it can take.
# test_cli_sql_and_profile_report_a_missing_query_file: one line ending in .sql, in any case, relative or absolute, that names no file is a missing query file for sql and profile, and whitespace around one that names a file is ignored; SQL text over several lines or not ending in .sql still runs; a table named sql in a schema is the known limit.
# test_cli_sql_read_only_runs_select_and_refuses_every_write: --read-only prints SELECT results and refuses COPY, ATTACH, INSTALL, LOAD, EXPORT, SET, a setting PRAGMA, CALL, CREATE, and INSERT, and a SELECT calling a table function that writes (enable_profiling, enable_logging, checkpoint), directly or through a view, macro, subquery, or query(), and any call of query, query_table, json_execute_serialized_sql, or a table macro calling one (histogram_values, histogram) as a table function, however named or quoted, before any statement runs, and refuses --out, leaving the project unchanged; profile --read-only does the same; a read-only PRAGMA, SHOW, SUMMARIZE, PIVOT with IN, information_schema, a column or CTE named query, and the histogram() aggregate still run, through sql and profile.
# test_read_only_sql_refuses_a_plan_that_differs_at_the_run: a query() whose SQL reads range(1) under EXPLAIN and enables profiling at the run is refused before any statement runs; no file is written, the session's profiling stays off, and the session still answers.
# test_profile_runs_with_a_landing_helper_older_than_read_only: profile without --read-only calls session(root) alone, so a landing helper without the read_only keyword still profiles.
# test_read_only_session_checks_view_files_before_any_runs_and_locks_configuration: a read-only session refuses a view file holding anything but CREATE and SELECT (a writable or READ_ONLY ATTACH, ATTACH then DETACH, COPY) before any statement runs, and a CREATE or SELECT whose plan calls a writing table function or cannot be checked (a PIVOT without IN), or that calls query, query_table, or a macro calling one (the histogram table macro included, and a scalar macro calling query), or calls a dynamic name before its body, or whose body does not parse alone and so is checked by token (a macro with two bodies, CREATE TABLE ... WITH NO DATA, refusing the histogram() aggregate there with a message saying so), each dynamic row refused for the name it calls, creating and changing no file, while the default session still loads them; a PIVOT view with IN loads; the loaded session's configuration is locked and spills go to a private directory outside the project.
# test_read_only_session_runs_the_histogram_aggregate_from_view_files: a view, temp view with a column list, table, table macro, scalar macro, or scalar macro holding a subquery whose body uses the histogram() aggregate loads in a read-only session and its query runs, as does one naming histogram(orders, id) only in a comment or a string, writing nothing.
# test_create_body_splits_only_the_create_statements_its_grammar_accepts: _create_body's closed grammar splits a CREATE VIEW, TABLE, MACRO, or FUNCTION at its first AS outside parentheses into the text before it, the body, and whether the body is a query or an expression, and returns None for a CREATE TYPE or SEQUENCE, a table without AS, an AS with no body, a SELECT, and empty text.
# test_read_only_session_refuses_a_macro_whose_catalog_body_calls_dynamic_sql: a view file's CREATE MACRO whose text check reads no call is refused, after it runs and before the session opens, when DuckDB's catalog shows its body calling dynamic SQL (a table macro calling query_table or histogram(), a scalar macro replaced by one calling query()), writing nothing; one calling only the histogram() aggregate loads.
# test_read_only_sql_matches_a_scalar_macro_calling_dynamic_sql_anywhere: a scalar macro calling query(), directly or through another scalar macro, is refused in any position, a table macro calling query_table as a table function, while a scalar macro over an aggregate and histogram() run.
# test_read_list_holds_read_xlsx_and_its_plan_passes_without_the_extension: read_xlsx is on the read list as the excel extension's function, so a plan calling it passes the check while another extension's table function is refused; runs without the extension.
# test_read_only_sql_without_the_excel_extension_says_how_to_install_it: without the excel extension, read_xlsx or FROM 'book.xlsx' in a query, or read_xlsx in a view file, fails on one line saying it is not installed and how to install it once without --read-only, writing nothing; skipped where the extension is installed.
# test_read_only_sql_reads_a_landed_excel_file_through_a_view: with the excel extension installed, sql and profile --read-only read a landed .xlsx through a view and directly, loading the extension without installing it, also when no view loaded it before the configuration locked, refuse COPY to xlsx, and write nothing; skipped where the extension cannot be loaded.
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
# test_gitignore_template_tracks_env_example: in a fresh repository with the template .gitignore, .env.example is tracked while .env and .env.local stay ignored.
# test_repair_check_ignore_follows_the_env_rules_the_project_keeps: repair's check-ignore command agrees with each kept .env rule for the template and for each declined restoration of .env, .env.*, or !.env.example, and disagrees when !.env.example precedes .env.*; repair asks once before adding any missing template rule and reports each one declined.
# test_guides_state_the_credentials_convention: the data guide and landing reference state where credentials live, where they never go, that records name the variable, and that land() records request and notes unchecked.
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

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import types
from datetime import date, datetime
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


@pytest.mark.parametrize("text, expected", [
    ("start=2026-01-01", ("start", date(2026, 1, 1))),
    ("n=5", ("n", 5)),
    ("rate=0.25", ("rate", 0.25)),
    ("on=true", ("on", True)),
    ('code="5"', ("code", "5")),
    ("regions=['a', 'b']", ("regions", ["a", "b"])),
    ("region=west", ("region", "west")),  # no TOML value: the text as given
    ("code=007", ("code", "007")),
    ("flag=True", ("flag", "True")),
    ("empty=", ("empty", "")),
    ("pair=a=b", ("pair", "a=b")),
    ("two=1\nother = 2", ("two", "1\nother = 2")),  # never read as TOML across lines
])
def test_sql_param_values_read_as_settings_values(text, expected):
    assert landing._parameter(text) == expected


@pytest.mark.parametrize("text", ["start", "=5", "the-start=5", "$start=5", "a b=5"])
def test_sql_param_refuses_what_a_query_cannot_name(text):
    with pytest.raises(argparse.ArgumentTypeError, match="name=value"):
        landing._parameter(text)


def test_cli_sql_binds_parameters_from_param_and_settings(tmp_path, capsys):
    pytest.importorskip("duckdb")
    sql_project(tmp_path)
    (tmp_path / "investigations/churn").mkdir(parents=True)
    (tmp_path / "investigations/churn/settings.toml").write_text(
        "[parameters]\nfirst = 2\nlast = 3\nunused = 2026-01-01\n")
    (tmp_path / "queries/window.sql").write_text("SELECT id FROM orders WHERE id BETWEEN $first AND $last ORDER BY id;\n")
    before = _files(tmp_path)
    for read_only in ([], ["--read-only"]):
        # settings bind every name a statement uses, and --param wins over them
        assert landing.cli_sql(tmp_path, read_only + ["--settings", "churn", "queries/window.sql"]) == 0
        assert capsys.readouterr().out == "| id |\n|---|\n| 2 |\n| 3 |\n2 of 2 rows shown\n"
        assert landing.cli_sql(tmp_path, read_only + ["--settings", "churn", "--param", "last=4",
                                                      "--param", "first=4", "queries/window.sql"]) == 0
        assert capsys.readouterr().out == "| id |\n|---|\n| 4 |\n1 of 1 rows shown\n"
        # each statement gets the names it uses; a date, a number, and a list keep their types
        assert landing.cli_sql(tmp_path, read_only + [
            "--param", "n=2", "--param", "day=2026-01-01", "--param", "ids=[1, 3]",
            "SELECT $n + 1 AS x; SELECT $day + INTERVAL 1 DAY AS d, list_contains($ids, 3) AS has FROM range($n)"]) == 0
        assert capsys.readouterr().out == ("| d | has |\n|---|---|\n| 2026-01-02 00:00:00 | True |\n"
                                           "| 2026-01-02 00:00:00 | True |\n2 of 2 rows shown\n")
    assert _files(tmp_path) == before
    # a missing or unreadable settings file fails on one line; a bad --param is a usage error
    assert landing.cli_sql(tmp_path, ["--settings", "absent", "SELECT 1"]) == 1
    assert "investigations/absent/settings.toml does not exist" in capsys.readouterr().err
    (tmp_path / "investigations/churn/settings.toml").write_text("[parameters\n")
    assert landing.cli_sql(tmp_path, ["--read-only", "--settings", "churn", "SELECT 1"]) == 1
    assert capsys.readouterr().err.startswith("sql: investigations/churn/settings.toml: ")
    assert landing.cli_sql(tmp_path, ["--settings", "../churn", "SELECT 1"]) == 1
    assert "needs an investigation name" in capsys.readouterr().err
    with pytest.raises(SystemExit) as exit:
        landing.cli_sql(tmp_path, ["--param", "first", "SELECT 1"])
    assert exit.value.code == 2


def test_cli_sql_plan_failures_name_the_fix_and_keep_read_only(tmp_path, capsys):
    pytest.importorskip("duckdb")
    sql_project(tmp_path)
    for query, fix in (("SELECT id FROM orders WHERE id > $cohort_end", "bind each $name with --param name=value"),
                       ("SELECT id FROM orders a, orders b", "qualify the column"),
                       ("SELECT absent FROM orders", "fix the statement, or for a PIVOT list its values with IN (...)")):
        assert landing.cli_sql(tmp_path, ["--read-only", query]) == 1, query
        error = capsys.readouterr().err
        assert error.startswith("sql: read-only: refused a statement DuckDB cannot plan (") and fix in error, error
        assert "without --read-only" not in error and error.count("\n") == 1, error
    # without --read-only, an unbound parameter gets the same fix
    assert landing.cli_sql(tmp_path, ["SELECT id FROM orders WHERE id > $cohort_end"]) == 1
    error = capsys.readouterr().err
    assert "bind each $name with --param name=value" in error and error.count("\n") == 1
    # profile binds no parameters, so its fix names what it can do instead, with or without --read-only
    validate_spec = importlib.util.spec_from_file_location("awb_validate_unbound", ASSET.parent / "awb_validate.py")
    validate = importlib.util.module_from_spec(validate_spec)
    validate_spec.loader.exec_module(validate)
    (tmp_path / "src/preparation").mkdir(parents=True)
    shutil.copyfile(ASSET, tmp_path / "src/preparation/landing.py")
    (tmp_path / "queries/window.sql").write_text("SELECT id FROM orders WHERE id > $first")
    for read_only in (["--read-only"], []):
        assert validate.cli_profile(tmp_path, read_only + ["queries/window.sql"]) == 1
        error = capsys.readouterr().err
        assert error.startswith("profile: ") and error.count("\n") == 1, error
        assert ("first" in error) == bool(read_only), error  # DuckDB names it only under EXPLAIN
        assert error.endswith("; profile binds no parameters: write each $name's value into the query, or run it "
                              "with `python3 src/awb.py sql --param name=value` (over MCP, the read tool's sql "
                              "with params)\n"), error
        assert "--settings" not in error and "without --read-only" not in error, error


def test_cli_sql_and_profile_report_a_missing_query_file(tmp_path, capsys):
    pytest.importorskip("duckdb")
    sql_project(tmp_path)
    validate_spec = importlib.util.spec_from_file_location("awb_validate_missing", ASSET.parent / "awb_validate.py")
    validate = importlib.util.module_from_spec(validate_spec)
    validate_spec.loader.exec_module(validate)
    (tmp_path / "src/preparation").mkdir(parents=True)
    shutil.copyfile(ASSET, tmp_path / "src/preparation/landing.py")
    for path in ("queries/absent.sql", "investigations/x/exploration/topic.SQL", " queries/absent.sql ",
                 str(tmp_path / "absent.sql")):
        for read_only in ([], ["--read-only"]):
            assert landing.cli_sql(tmp_path, read_only + [path]) == 1, path
            assert capsys.readouterr().err == \
                f"sql: no query file {' '.join(path.split())}; a relative path is read from the project root\n"
            assert validate.cli_profile(tmp_path, read_only + [path]) == 1, path
            assert "no query file" in capsys.readouterr().err
    # whitespace around a path that names a file is ignored, so the file runs
    for read_only in ([], ["--read-only"]):
        assert landing.cli_sql(tmp_path, read_only + [" queries/large.sql "]) == 0
        assert capsys.readouterr().out.endswith("4 of 4 rows shown\n")
    # SQL text spanning lines, or not ending in .sql, is still SQL text
    for query in ("SELECT 1 AS n\n-- from queries/old.sql", "SELECT 'queries/absent.sql' AS n", "SELECT 1 AS sql"):
        assert landing.cli_sql(tmp_path, ["--read-only", query]) == 0, query
    capsys.readouterr()
    # Known limit: one line ending in .sql names a file, so a table named sql in schema s is read as one.
    assert landing.cli_sql(tmp_path, ["SELECT * FROM s.sql"]) == 1
    assert "no query file" in capsys.readouterr().err
def _files(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def bypass(target):
    """A SELECT whose query() reads range(1) under EXPLAIN and enables profiling to target when it runs."""
    return ("FROM query(CASE WHEN current_query() LIKE 'EXPLAIN%' THEN 'FROM range(1)' ELSE "
            f"'FROM enable_profiling(format := ''json'', save_location := ''{target}'')' END); "
            "SELECT count(*) FROM orders")


def test_read_only_sql_refuses_a_plan_that_differs_at_the_run(tmp_path):
    pytest.importorskip("duckdb")
    sql_project(tmp_path)
    before = _files(tmp_path)
    with landing.session(tmp_path, read_only=True) as connection:
        with pytest.raises(ValueError, match=r"read-only: refused query\(\)"):
            landing.read_only_sql(connection, bypass(tmp_path / "p.json"))
        assert landing.read_only_sql(connection, "SELECT count(*) FROM orders").fetchall() == [(5,)]
        settings = dict(connection.execute("SELECT name, value FROM duckdb_settings() "
                                           "WHERE name IN ('enable_profiling', 'profiling_output')").fetchall())
    assert settings["enable_profiling"] in (None, "") and settings["profiling_output"] == ""
    assert _files(tmp_path) == before


def test_cli_sql_read_only_runs_select_and_refuses_every_write(tmp_path, capsys):
    pytest.importorskip("duckdb")
    sql_project(tmp_path)
    validate_spec = importlib.util.spec_from_file_location("awb_validate_read_only", ASSET.parent / "awb_validate.py")
    validate = importlib.util.module_from_spec(validate_spec)
    validate_spec.loader.exec_module(validate)
    (tmp_path / "src/preparation").mkdir(parents=True)
    shutil.copyfile(ASSET, tmp_path / "src/preparation/landing.py")
    (tmp_path / "foundation/views/02_writers.sql").write_text(  # loads; reading through either is refused
        f"CREATE VIEW profiled AS FROM enable_profiling(save_location := '{tmp_path / 'v.json'}'); "
        f"CREATE MACRO logged() AS TABLE FROM enable_logging(storage := 'file', storage_path := '{tmp_path / 'm'}');")
    before = _files(tmp_path)
    assert landing.cli_sql(tmp_path, ["--read-only", "queries/large.sql", "--limit", "1"]) == 0
    assert capsys.readouterr().out == "| id |\n|---|\n| 1 |\n1 of 4 rows shown\n"
    assert landing.cli_sql(tmp_path, ["--read-only", "WITH a AS (SELECT 1 AS x) SELECT * FROM a; FROM orders"]) == 0
    capsys.readouterr()
    writes = [f"COPY (SELECT 1) TO '{tmp_path / 'copy.csv'}'", f"ATTACH '{tmp_path / 'new.duckdb'}' AS extra",
              "INSTALL httpfs", "LOAD httpfs", f"EXPORT DATABASE '{tmp_path / 'export'}'",
              f"SET temp_directory = '{tmp_path / 'spill'}'", "PRAGMA enable_profiling", "CALL checkpoint()",
              "CREATE TABLE t AS SELECT 1", "SELECT 1; CREATE TABLE t AS SELECT 1; SELECT 2",
              "CREATE TABLE t (x INT); INSERT INTO t VALUES (1); SELECT * FROM t",
              # SELECTs whose table functions write files, directly or through a view, macro, or query()
              f"FROM enable_profiling(format := 'json', save_location := '{tmp_path / 'p.json'}'); FROM orders",
              f"FROM enable_logging(storage := 'file', storage_path := '{tmp_path / 'logdir'}')",
              f"SELECT (SELECT count(*) FROM enable_profiling(save_location := '{tmp_path / 'p.txt'}'))",
              f"FROM query('FROM enable_logging(storage := ''file'', storage_path := ''{tmp_path / 'logdir'}'')')",
              "FROM profiled", "FROM logged()", "FROM checkpoint()", "FROM truncate_duckdb_logs()",
              # dynamic SQL, whose plan at the run can differ from the plan checked, and macros calling it
              bypass(tmp_path / "p.json"), "FROM query('FROM orders')", "FROM query_table('orders')",
              "SELECT * FROM system.main.QUERY('FROM orders')", "FROM \"Query\"('FROM orders')",
              "SELECT (SELECT count(*) FROM query('FROM orders'))", "FROM histogram_values(orders, id)",
              "FROM histogram(orders, id)", "SELECT histogram(id) AS h FROM histogram(orders, id)",
              "FROM json_execute_serialized_sql(json_serialize_sql('SELECT 1'))"]
    for query in writes:
        assert landing.cli_sql(tmp_path, ["--read-only", query]) == 1, query
        captured = capsys.readouterr()
        assert captured.out == "" and "read-only: refused" in captured.err, query
        assert validate.cli_profile(tmp_path, ["--read-only", query]) == 1, query
        assert "read-only: refused" in capsys.readouterr().err, query
    for command in (landing.cli_sql, validate.cli_profile):
        with pytest.raises(SystemExit) as exit:
            command(tmp_path, ["--read-only", "SELECT 1", "--out", "out.csv"])
        assert exit.value.code == 2
    capsys.readouterr()
    assert validate.cli_profile(tmp_path, ["--read-only", "orders"]) == 0
    assert "rows: 5" in capsys.readouterr().out
    for query in ("PRAGMA table_info('orders')", "SHOW TABLES", "SUMMARIZE orders", "SELECT 'é' AS query",
                  "PIVOT orders ON note IN ('a|b') USING count(*)", "FROM information_schema.columns",
                  "WITH query AS (FROM orders) SELECT count(*) FROM query",
                  # the histogram aggregate shares its name with a table macro that calls query_table
                  "SELECT histogram(id) AS h FROM orders", "SELECT note, histogram(id) AS h FROM orders GROUP BY note"):
        assert landing.cli_sql(tmp_path, ["--read-only", query]) == 0, query
    assert "| {0: 1, 1: 1, 2: 1, 3: 1, 4: 1} |" in capsys.readouterr().out
    assert validate.cli_profile(tmp_path, ["--read-only", "SELECT histogram(id) AS h FROM orders"]) == 0
    capsys.readouterr()
    assert _files(tmp_path) == before


def test_profile_runs_with_a_landing_helper_older_than_read_only(tmp_path, monkeypatch, capsys):
    pytest.importorskip("duckdb")
    sql_project(tmp_path)
    spec = importlib.util.spec_from_file_location("awb_validate_older_landing", ASSET.parent / "awb_validate.py")
    validate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validate)
    older = types.SimpleNamespace(**{**vars(landing), "session": lambda root: landing.session(root)})
    monkeypatch.setattr(validate, "_landing", lambda root: older)
    assert validate.cli_profile(tmp_path, ["orders"]) == 0
    assert "rows: 5" in capsys.readouterr().out


def test_read_only_session_checks_view_files_before_any_runs_and_locks_configuration(tmp_path):
    duckdb = pytest.importorskip("duckdb")
    sql_project(tmp_path)
    with duckdb.connect(str(tmp_path / "side.duckdb")) as side:
        side.execute("CREATE TABLE extra AS SELECT 7 AS n")
    view = tmp_path / "foundation/views/02_side.sql"
    side, cache = tmp_path / "side.duckdb", tmp_path / "cache.duckdb"
    token = "(this CREATE's calls were checked by token, in any position, which also refuses the histogram()"
    dynamic = {  # each refused for the dynamic name it calls
        "CREATE VIEW extra AS FROM histogram(orders, id);": "refused histogram()",
        "CREATE OR REPLACE TEMP VIEW extra (h) AS SELECT histogram(id) FROM orders, histogram(orders, id);":
            "refused histogram(), which builds SQL",
        "CREATE MACRO extra(t) AS TABLE FROM histogram(t, id);": "refused histogram()",
        "CREATE MACRO extra() AS (SELECT count(*) FROM query('FROM orders'));": "refused query()",
        "CREATE TEMP TABLE extra AS FROM query_table('orders');": "refused query_table()",
        # a call before the body
        "CREATE MACRO extra(t := query_table('orders')) AS TABLE SELECT 1 AS n;": "refused query_table()",
        # a body that cannot be parsed alone is checked by token, so the aggregate is refused there
        "CREATE MACRO extra(a) AS histogram(a), (a, b) AS histogram(b);": f"refused histogram() {token}",
        "CREATE TABLE extra AS SELECT histogram(id) AS h FROM orders WITH NO DATA;": f"refused histogram() {token}",
        # a comment glued to AS hides neither it nor the table function call after the alias in the body
        "CREATE MACRO extra() AS/**/TABLE SELECT * FROM orders AS a, query_table('orders');":
            "refused query_table(), which builds SQL",
        "CREATE MACRO extra() AS--c\nTABLE SELECT * FROM orders AS a, histogram(orders, id);":
            "refused histogram(), which builds SQL",
        "CREATE VIEW extra AS/**/SELECT * FROM orders AS a, query_table('orders');":
            "refused query_table(), which builds SQL"}
    for text in (f"ATTACH '{side}' AS side; CREATE VIEW extra AS SELECT * FROM side.extra;",
                 f"ATTACH '{side}' AS side (READ_ONLY); CREATE VIEW extra AS SELECT * FROM side.extra;",
                 f"ATTACH '{tmp_path / 'new.duckdb'}' AS new; CREATE VIEW extra AS SELECT 7 AS n;",
                 f"ATTACH '{cache}' AS cache; CREATE TABLE cache.saved AS SELECT 7 AS n; DETACH cache;",
                 # statements of an allowed kind whose plan writes, or cannot be checked
                 f"CREATE TABLE t AS FROM enable_profiling(save_location := '{tmp_path / 'p.json'}'); SELECT 1;",
                 f"SELECT * FROM enable_logging(storage := 'file', storage_path := '{tmp_path / 'logdir'}');",
                 "PIVOT orders ON note USING count(*);",  # run as CREATE TYPE, then SELECT
                 # dynamic SQL in a view or macro body, or in a view file's SELECT
                 "CREATE VIEW extra AS FROM query('SELECT 7 AS n');",
                 "CREATE MACRO extra(t) AS TABLE FROM query_table(t);",
                 "CREATE VIEW extra AS FROM histogram_values(orders, id);",
                 *dynamic,
                 bypass(tmp_path / "v.json") + ";",
                 f"CREATE VIEW extra AS SELECT 7 AS n; COPY (SELECT 1) TO '{tmp_path / 'copy.csv'}';"):
        view.write_text(text)
        before = _files(tmp_path)
        with pytest.raises(RuntimeError, match="02_side.sql") as refused:
            landing.session(tmp_path, read_only=True)
        assert dynamic.get(text, "read-only: refused") in str(refused.value.__cause__), text
        assert _files(tmp_path) == before, text
    with landing.session(tmp_path) as connection:  # the default session keeps loading them
        assert connection.sql("SELECT n FROM extra").fetchall() == [(7,)]
    view.write_text("CREATE VIEW wide AS PIVOT orders ON note IN ('a|b') USING count(*);")
    with landing.session(tmp_path, read_only=True) as connection:
        settings = dict(connection.execute(
            "SELECT name, value FROM duckdb_settings() WHERE name IN ('lock_configuration', "
            "'autoinstall_known_extensions', 'allow_persistent_secrets', 'temp_directory')").fetchall())
        with pytest.raises(duckdb.Error, match="locked"):
            connection.execute("SET threads = 1")
        with pytest.raises(ValueError, match=r"refused statement kind EXPLAIN \(only SELECT.*PIVOT.*IN \(\.\.\.\)"):
            landing.read_only_sql(connection, "EXPLAIN SELECT 1")
    assert settings["lock_configuration"] == "true" and settings["autoinstall_known_extensions"] == "false"
    assert settings["allow_persistent_secrets"] == "false"
    spill = Path(settings["temp_directory"]).parent
    assert not spill.resolve().is_relative_to(tmp_path.resolve()) and spill.name.startswith("awb-duckdb-")
    assert spill.stat().st_mode & 0o777 == 0o700


def test_read_only_session_runs_the_histogram_aggregate_from_view_files(tmp_path):
    pytest.importorskip("duckdb")
    sql_project(tmp_path)
    view = tmp_path / "foundation/views/02_extra.sql"
    for text, query in (
            ("CREATE VIEW extra AS SELECT histogram(id) AS h FROM orders;", "SELECT h FROM extra"),
            ("CREATE OR REPLACE TEMP VIEW extra (h) AS SELECT histogram(id) FROM orders;", "SELECT h FROM extra"),
            ("CREATE TABLE extra AS SELECT histogram(id) AS h FROM orders;", "SELECT h FROM extra"),
            ("CREATE MACRO extra(t) AS TABLE SELECT histogram(id) AS h FROM orders;", "SELECT h FROM extra(1)"),
            ("CREATE MACRO extra(x) AS histogram(x);", "SELECT extra(id) AS h FROM orders"),
            ("CREATE MACRO extra(x) AS (SELECT histogram(id) FROM orders WHERE id < x);",
             "SELECT extra(5) AS h"),
            ("-- histogram(orders, id) in a comment\nCREATE VIEW extra AS SELECT histogram(id) AS h, "
             "'FROM histogram(orders, id)' AS note FROM orders;", "SELECT h FROM extra"),
            ("CREATE VIEW extra AS/**/SELECT histogram(id) AS h FROM orders;", "SELECT h FROM extra")):
        view.write_text(text)
        before = _files(tmp_path)
        with landing.session(tmp_path, read_only=True) as connection:
            assert landing.read_only_sql(connection, query).fetchall() == [({0: 1, 1: 1, 2: 1, 3: 1, 4: 1},)], text
        assert _files(tmp_path) == before, text


def test_create_body_splits_only_the_create_statements_its_grammar_accepts():
    pytest.importorskip("duckdb")
    for text, split in (
            ("CREATE VIEW v (a, b) AS SELECT 1, 2", ("CREATE VIEW v (a, b) ", "SELECT 1, 2", "select")),
            ("CREATE OR REPLACE TEMP VIEW v AS WITH x AS (SELECT 1) FROM x",
             ("CREATE OR REPLACE TEMP VIEW v ", "WITH x AS (SELECT 1) FROM x", "select")),
            ("CREATE TABLE IF NOT EXISTS t AS (FROM x)", ("CREATE TABLE IF NOT EXISTS t ", "(FROM x)", "select")),
            ('-- c\nCREATE TABLE "as" AS FROM x', ('-- c\nCREATE TABLE "as" ', "FROM x", "select")),
            ("CREATE MACRO m(a := CAST(1 AS INT)) AS TABLE /* c */ FROM t",
             ("CREATE MACRO m(a := CAST(1 AS INT)) ", "FROM t", "select")),
            ("create function f(x) as table select x", ("create function f(x) ", "select x", "select")),
            ("CREATE MACRO m(x) AS x + 1", ("CREATE MACRO m(x) ", "x + 1", "expression")),
            # a comment glued to a token is not part of its word, for AS and for parentheses alike
            ("CREATE MACRO m() AS/**/TABLE SELECT * FROM t AS a, query_table('t')",
             ("CREATE MACRO m() ", "SELECT * FROM t AS a, query_table('t')", "select")),
            ("CREATE VIEW v AS--c\nSELECT 1 AS a", ("CREATE VIEW v ", "SELECT 1 AS a", "select")),
            ("CREATE MACRO m(a := (/*)*/1)) AS a", ("CREATE MACRO m(a := (/*)*/1)) ", "a", "expression")),
            ("CREATE MACRO m(a := (/*(*/1)) AS a", ("CREATE MACRO m(a := (/*(*/1)) ", "a", "expression")),
            # refused: no kind before the first AS outside parentheses, no AS, or no body
            ("CREATE TYPE t AS ENUM ('a')", None), ("CREATE SEQUENCE s", None),
            ("CREATE TABLE t (x INT GENERATED ALWAYS AS (1))", None), ("CREATE TABLE t AS", None),
            ("CREATE MACRO m(x) AS TABLE", None), ("SELECT 1 AS x", None), ("", None)):
        assert landing._create_body(text) == split, text


def test_read_only_session_refuses_a_macro_whose_catalog_body_calls_dynamic_sql(tmp_path, monkeypatch):
    pytest.importorskip("duckdb")
    sql_project(tmp_path)
    view = tmp_path / "foundation/views/02_extra.sql"
    # a CREATE whose text check reads no call, as a misread split would, is checked again from the catalog
    monkeypatch.setattr(landing, "_create_calls", lambda connection, text, dynamic: (set(), set(), False))
    for text, name in (("CREATE MACRO extra() AS TABLE FROM query_table('orders');", "extra"),
                       ("CREATE MACRO extra(t) AS TABLE SELECT * FROM histogram(t, id);", "extra"),
                       ("CREATE MACRO plain(x) AS x + 1; CREATE OR REPLACE MACRO plain() AS "
                        "(SELECT count(*) FROM query('FROM orders'));", "plain")):
        view.write_text(text)
        before = _files(tmp_path)
        with pytest.raises(RuntimeError, match="02_extra.sql") as refused:
            landing.session(tmp_path, read_only=True)
        assert f"read-only: refused {name}(), a macro just created that calls dynamic SQL" in str(
            refused.value.__cause__), text
        assert _files(tmp_path) == before, text
    view.write_text("CREATE MACRO extra(x) AS histogram(x);")  # calls no dynamic SQL, so it loads
    with landing.session(tmp_path, read_only=True) as connection:
        assert landing.read_only_sql(connection, "SELECT extra(id) FROM orders").fetchall() == [
            ({0: 1, 1: 1, 2: 1, 3: 1, 4: 1},)]


def test_read_only_sql_matches_a_scalar_macro_calling_dynamic_sql_anywhere():
    duckdb = pytest.importorskip("duckdb")
    with duckdb.connect() as connection:
        connection.execute("CREATE VIEW orders AS SELECT range AS id FROM range(5)")
        connection.execute("CREATE MACRO counted() AS (SELECT count(*) FROM query('FROM orders'))")
        connection.execute("CREATE MACRO doubled(x) AS counted() * x")  # through another scalar macro
        connection.execute("CREATE MACRO summed(x) AS sum(x)")
        connection.execute("CREATE MACRO rows_of(t) AS TABLE FROM query_table(t)")
        for query in ("SELECT counted()", "SELECT doubled(2)", "SELECT id FROM orders WHERE id < doubled(1)",
                      "FROM rows_of('orders')", "SELECT * FROM orders, rows_of('orders')"):
            with pytest.raises(ValueError, match=r"read-only: refused (counted|doubled|rows_of)\(\)"):
                landing.read_only_sql(connection, query)
        assert landing.read_only_sql(connection, "SELECT summed(id), histogram(id) FROM orders").fetchall() == [
            (10, {0: 1, 1: 1, 2: 1, 3: 1, 4: 1})]


def excel_loads():
    """Whether DuckDB's excel extension is installed here, so a session can load it without installing."""
    duckdb = pytest.importorskip("duckdb")
    try:
        with duckdb.connect(config={"autoinstall_known_extensions": False}) as connection:
            connection.execute("LOAD excel")
        return True
    except duckdb.Error:
        return False


class Planned:
    """A connection whose EXPLAIN shows one table function node; every other call reaches DuckDB."""

    def __init__(self, connection, function):
        self.connection, self.function = connection, function

    def execute(self, text, *parameters):
        if text.startswith("EXPLAIN"):
            plan = [{"name": self.function, "children": [], "extra_info": {"Function": self.function}}]
            return types.SimpleNamespace(fetchall=lambda: [("physical_plan", json.dumps(plan))])
        return self.connection.execute(text, *parameters)


def test_read_list_holds_read_xlsx_and_its_plan_passes_without_the_extension():
    duckdb = pytest.importorskip("duckdb")
    assert "read_xlsx" in landing.READ_TABLE_FUNCTIONS
    assert landing.EXTENSION_READ_FUNCTIONS == {"read_xlsx": "excel"}
    statement = duckdb.extract_statements("SELECT * FROM read_xlsx('data/raw/books/a1/book.xlsx')")[0]
    with duckdb.connect() as connection:
        landing._refuse_writing_plan(Planned(connection, "READ_XLSX"), statement)
        with pytest.raises(ValueError, match="refused table function read_gsheet"):
            landing._refuse_writing_plan(Planned(connection, "READ_GSHEET"), statement)


def test_read_only_sql_without_the_excel_extension_says_how_to_install_it(tmp_path, capsys):
    pytest.importorskip("duckdb")
    if excel_loads():
        pytest.skip("the excel extension is installed here")
    sql_project(tmp_path)
    before = _files(tmp_path)
    hint = "install it once without --read-only"
    for query in ("FROM read_xlsx('data/raw/books/a1/book.xlsx')", "FROM 'data/raw/books/a1/book.xlsx'"):
        assert landing.cli_sql(tmp_path, ["--read-only", query]) == 1
        error = capsys.readouterr().err
        assert "read_xlsx needs DuckDB's excel extension, which is not installed" in error and hint in error, query
        assert 'src/awb.py sql "INSTALL excel; SELECT 1"' in error and error.count("\n") == 1
    assert _files(tmp_path) == before
    (tmp_path / "foundation/views/02_book.sql").write_text(
        "CREATE VIEW book AS FROM read_xlsx('data/raw/books/a1/book.xlsx');")
    before = _files(tmp_path)
    with pytest.raises(RuntimeError, match="02_book.sql") as refused:
        landing.session(tmp_path, read_only=True)
    assert hint in str(refused.value.__cause__)
    assert _files(tmp_path) == before


def test_read_only_sql_reads_a_landed_excel_file_through_a_view(tmp_path, capsys):
    duckdb = pytest.importorskip("duckdb")
    if not excel_loads():
        pytest.skip("needs DuckDB's excel extension installed")
    sql_project(tmp_path)
    book = tmp_path / "data/raw/books/a1/book.xlsx"
    book.parent.mkdir(parents=True)
    with duckdb.connect() as connection:
        connection.execute("LOAD excel")  # COPY's xlsx format does not load it on its own
        connection.execute(f"COPY (SELECT range AS id, 'r' || range AS region FROM range(3)) TO '{book}' "
                           "(FORMAT xlsx, HEADER true)")
    (tmp_path / "foundation/views/02_book.sql").write_text(
        "CREATE VIEW book AS FROM read_xlsx('data/raw/books/a1/book.xlsx');")
    spec = importlib.util.spec_from_file_location("awb_validate_excel", ASSET.parent / "awb_validate.py")
    validate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validate)
    (tmp_path / "src/preparation").mkdir(parents=True)
    shutil.copyfile(ASSET, tmp_path / "src/preparation/landing.py")
    before = _files(tmp_path)
    assert landing.cli_sql(tmp_path, ["--read-only", "SELECT region FROM book ORDER BY id"]) == 0
    assert capsys.readouterr().out == "| region |\n|---|\n| r0 |\n| r1 |\n| r2 |\n3 of 3 rows shown\n"
    assert landing.cli_sql(tmp_path, ["--read-only", "SELECT count(*) FROM read_xlsx('data/raw/books/a1/book.xlsx')"]) == 0
    assert "| 3 |" in capsys.readouterr().out
    assert validate.cli_profile(tmp_path, ["--read-only", "book"]) == 0
    assert "rows: 3" in capsys.readouterr().out
    assert landing.cli_sql(tmp_path, ["--read-only", f"COPY (FROM book) TO '{tmp_path / 'copy.xlsx'}' (FORMAT xlsx)"]) == 1
    assert "read-only: refused" in capsys.readouterr().err
    assert _files(tmp_path) == before
    (tmp_path / "foundation/views/02_book.sql").unlink()  # no view loads the extension before the lock
    before = _files(tmp_path)
    for query in ("SELECT count(*) FROM read_xlsx('data/raw/books/a1/book.xlsx')",
                  "SELECT count(*) FROM 'data/raw/books/a1/book.xlsx'"):
        with landing.session(tmp_path, read_only=True) as connection:
            assert connection.execute("SELECT loaded FROM duckdb_extensions() WHERE extension_name = 'excel'"
                                      ).fetchall() == [(False,)], query
            assert landing.read_only_sql(connection, query).fetchall() == [(3,)], query
    assert _files(tmp_path) == before


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


# Git commands in the .gitignore tests see only the project's rules, not the developer's global excludes.
GIT_ENV = {**os.environ, "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.excludesFile",
           "GIT_CONFIG_VALUE_0": os.devnull}


@pytest.mark.skipif(shutil.which("git") is None, reason="git is not installed")
def test_gitignore_template_tracks_env_example(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, env=GIT_ENV)
    (tmp_path / ".gitignore").write_bytes((WORKBENCH / ".gitignore").read_bytes())
    for name in (".env", ".env.local", ".env.example"):
        (tmp_path / name).write_text("ACME_TOKEN=\n")
    status = subprocess.run(["git", "-C", str(tmp_path), "status", "--porcelain", "--ignored",
                             "--untracked-files=all"], check=True, capture_output=True, text=True, env=GIT_ENV)
    assert sorted(status.stdout.splitlines()) == [
        "!! .env", "!! .env.local", "?? .env.example", "?? .gitignore"]


@pytest.mark.skipif(shutil.which("git") is None, reason="git is not installed")
def test_repair_check_ignore_follows_the_env_rules_the_project_keeps(tmp_path):
    repair = (ASSET.parents[1] / "references/repair.md").read_text(encoding="utf-8")
    command = re.search(r"run `(git check-ignore --no-index [^`]+)`\. Its output must agree with each of "
                        r"these rules the project keeps: ", repair).group(1)
    for fact in ("List every [ignore rule](../assets/workbench/.gitignore) the project's `.gitignore` lacks and "
                 "ask the user once, naming them all, whether to add each",
                 "each rule the user declines stays dropped, and report it as an exception"):
        assert fact in repair
    assert "git log" not in repair.split("\n3. ")[1].split("\n4. ")[0]
    assert "step 3's `git check-ignore` output agrees with each `.env` rule the project keeps" in repair
    # Each kept rule: the file it decides, and whether the check must print that file.
    rules = {".env": (".env", True), ".env.*": (".env.local", True), "!.env.example": (".env.example", False)}
    for rule, (name, printed) in rules.items():
        assert f"{'prints' if printed else 'omits'} `{name}` if the `{rule}` rule is kept" in repair
    template = (WORKBENCH / ".gitignore").read_text(encoding="utf-8").splitlines()
    misplaced = ["!.env.example"] + [line for line in template if line != "!.env.example"]
    layouts = [(template, [".env", ".env.local"], True),
               (misplaced, [".env.example", ".env", ".env.local"], False)]
    # A restoration the user declines leaves that rule out; the check still passes on the rest.
    for dropped, expected in ((".env.*", [".env"]), ("!.env.example", [".env.example", ".env", ".env.local"]),
                              (".env", [".env.local"])):
        layouts.append(([line for line in template if line != dropped], expected, True))
    for lines, expected, done in layouts:
        subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, env=GIT_ENV)
        (tmp_path / ".gitignore").write_text("\n".join(lines) + "\n", encoding="utf-8")
        output = subprocess.run(shlex.split(command), cwd=tmp_path, capture_output=True, text=True, env=GIT_ENV)
        assert output.stdout.splitlines() == expected
        agrees = all((name in expected) == printed for rule, (name, printed) in rules.items() if rule in lines)
        assert agrees == done


def test_guides_state_the_credentials_convention():
    guide = (WORKBENCH / "workbench-guides/data.md").read_text(encoding="utf-8")
    rule = guide.split("## Assess and acquire")[1].split("\n## ")[0]
    for fact in ("environment variables", "gitignored `.env`", "tracked `.env.example`",
                 "Secrets never go in `settings.toml`, saved SQL, `request` or `notes` values, or "
                 "foundation ledger rows", "Saved SQL names no credential at all",
                 "the others record the variable's name instead, as `$NAME`"):
        assert fact in rule
    reference = (ASSET.parents[1] / "references/landing.md").read_text(encoding="utf-8")
    for fact in ("environment variables", "gitignored `.env`", "`workbench-guides/data.md` (**Assess and acquire**)",
                 "refers to a credential, it names the variable, as `$NAME`, never its value",
                 "`land()` records both as given, without checking them"):
        assert fact in reference


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
