# Kept cases:
# test_status_reads_rendered_table_with_json_present: status keeps reading the rendered Markdown even if JSON disagrees, and writes nothing.
# test_collect_standard_records_without_writes_or_other_conclusions: counts normalize flagged statuses; nothing is written; other investigations give only name and date.
# test_missing_and_custom_tables_are_unknown_not_zero: an unsupported state table or absent sources record is null with an uncertainty, never zero.
# test_malformed_table_does_not_count_partial_rows: one malformed findings row makes the counts unknown.
# test_unmatched_flags_are_counted_for_awb_package: a flag absent from the manifest is counted in unmatched_flags; no methodology review or mtime estimate keys remain.
# test_rerun_since_draft_lists_results_recorded_after_the_draft: a represented result whose evidence is newer than the draft is listed, including one a narrative-only package never serialized; an empty list lists none; a manifest without results, or escaping or unreadable evidence, is unknown, an unreadable one an uncertainty.
# test_release_only_package_counts_every_flag_unmatched: with no draft, every flagged finding is unmatched and nothing is uncertain.
# test_dispositions_require_current_reason: a disposition applies only while finding and reason match the state row exactly.
# test_revalidate_and_none_dispositions_block_release: a confirmed flag whose disposition is `none` or `revalidate` lacks a disposition; `omit` and `release_with_caveat` do not.
# test_flag_the_draft_does_not_represent_needs_no_disposition: a flag recorded with represented_in "none" needs no disposition and blocks nothing.
# test_malformed_flag_shape_leaves_counts_unknown: a missing or unknown disposition, empty or non-string places, or the per-place shape is malformed; counts are null.
# test_malformed_manifest_requests_targeted_fallback: invalid manifests or timestamps name the manifest under uncertainties, with no mtime estimate.
# test_draft_without_manifest_json_is_an_uncertainty: a draft manifest in another format is not read; the draft is named under uncertainties.
# test_unusable_release_manifest_is_uncertain: an absent, non-JSON, undated, or unreadable release manifest leaves released_at null and records one uncertainty.
# test_unreadable_draft_manifest_is_unknown: an unreadable draft manifest leaves dates and counts null with an uncertainty.
# test_git_no_commits_dirty_date_precision_and_no_index_writes: no-commit wording, same-day indeterminate, later change out of date; the index is untouched.
# test_commit_out_of_date_state_and_undated_deletion: a later commit makes the state out of date; a deleted file is an undated change.
# test_acquisitions_and_storage_risks: checkout-only and blank retained copies count; a declined landed-data line reads none chosen.
# test_absent_project_and_unsafe_active_pointer: a missing project is not a workbench; an unsafe pointer is an uncertainty.
# test_standard_active_state_pointer: link, path, and backticked pointer forms resolve to the investigation.
# test_other_state_reader_stops_before_conclusions: another investigation's state is read only up to its first section.
# test_blank_fields_do_not_capture_following_lines: a blank field is missing, never the next line's text.
# test_backticked_checkout_only_is_missing_retained_copy: a backticked `this checkout only` counts as no retained copy.
# test_optional_storage_fields_absent_before_use_are_not_uncertainties: absent storage lines are unrecorded without uncertainties.
# test_nested_repository_status_scopes_changes_and_preserves_index: Git facts are scoped to a project inside a larger repository.
# test_unreadable_enumeration_is_unknown_not_empty: an unreadable directory yields unknown, never an empty inventory.
# test_none_chosen_is_a_recorded_decision: `none chosen`, backticked or bare `none`, reports availability none chosen, not unrecorded.
# test_absent_storage_remains_actionable_when_acquisitions_and_releases_exist: absent lines read unrecorded alongside acquisitions and releases.
# test_upstream_probe_reports_each_file_changed_unchanged_or_unknown_without_writes: land()'s upstream fields drive one HEAD per probeable file; ETag wins over Last-Modified unless only the ETag changed, a weak ETag and an equal date in another form match, HTTP and network errors are unknown, and nothing is written.
# test_an_unusable_server_validator_is_unknown_and_the_probe_continues: a blank ETag or a Last-Modified that does not parse (including an overflowing year or offset) gives no evidence of change; the other validator decides if usable, else the file is unknown; two unparseable dates are compared as text; later files are still probed.
# test_a_relanded_url_is_checked_only_in_its_latest_acquisition: after a changed upstream is landed again, only the newest acquisition of that source and URL is probed and the earlier one counts as superseded, even when the newer one records no validator.
# test_the_latest_acquisition_is_ordered_by_completed_at_then_acquisition_id: completed_at instants are compared across offsets, not by ID, and acquisitions completed in the same second are ordered by acquisition ID, so exactly one stays current.
# test_a_host_that_times_out_is_not_requested_again: after a connect or read timeout, the host's remaining files are unknown without a request, and other hosts are still probed.
# test_a_redirect_target_that_times_out_is_not_requested_again: through urllib's own redirect processing, the host that timed out after a redirect is the one suppressed, for direct and redirected requests alike, and the redirecting host is still requested.
# test_status_without_probe_counts_probeable_files_and_sends_nothing: without --probe-upstream no request is made; only the probeable count is reported.
# test_unreadable_provenance_is_an_uncertainty_and_leaves_the_count_unknown: a missing, unparseable, or malformed provenance.json, including any upstream field land() refuses (by land()'s own check: an invalid or credential-bearing URL among them), is named under uncertainties with or without the probe and makes probeable_files null, nothing is requested for it, the readable acquisitions are still probed, and partial acquisitions and stray files are skipped.
# test_provenance_without_upstream_keys_counts_as_without_upstream: a file entry with no upstream key is valid and counts as without upstream.
# test_unreadable_acquisition_inventory_is_unknown_not_zero: an unreadable data/raw or source directory is an uncertainty and makes probeable_files null, never zero.
# test_probe_follows_redirects_only_to_http_and_only_as_head: through urllib's own redirect processing, a redirect to ftp is refused before any FTP call and an https redirect is followed as HEAD.
# test_probe_upstream_flag_reaches_the_probe: the command-line flag runs the probe and prints its results.

"""Status observations stay read-only and conservative when records need interpretation."""
import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/awb-status/scripts/collect_status.py"
spec = importlib.util.spec_from_file_location("awb_status", SCRIPT)
status = importlib.util.module_from_spec(spec)
spec.loader.exec_module(status)
TEMPLATES = ROOT / ".agents/skills/awb-init/assets/workbench"


def write(root, path, text):
    file = root / path
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(text)
    return file


@pytest.fixture
def workbench(tmp_path):
    write(tmp_path, "README.md", "Active investigation: churn\nLanded data is kept at: none chosen\nReleased packages are kept at: not yet recorded\n")
    for source, target in [("investigation/state.md", "investigations/churn/state.md"), ("investigation/brief.md", "investigations/churn/brief.md"), ("foundation/sources.md", "foundation/sources.md")]:
        text = (TEMPLATES / source).read_text().replace("<!-- use an ISO date -->", "2026-10-01")
        write(tmp_path, target, text)
    state = tmp_path / "investigations/churn/state.md"
    text = state.read_text().replace("| --- | --- | --- | --- |", "| --- | --- | --- | --- |\n| Renewal lag | evidence.json | revalidation-needed (was supported) | Q-004 correction |\n| Pricing | evidence.json | supported | |")
    state.write_text(text)
    return tmp_path


def test_collect_standard_records_without_writes_or_other_conclusions(workbench):
    other = write(workbench, "investigations/pricing/state.md", "# State\nLast updated: 2026-08-01\n\n## Current findings\nPRIVATE CONCLUSION")
    before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in workbench.rglob("*") if p.is_file()}
    result = status.collect(workbench)
    assert result["active"]["counts"] == {"revalidation-needed": 1, "supported": 1}
    assert result["other_investigations"] == [{"name": "pricing", "last_updated": "2026-08-01"}]
    assert "PRIVATE CONCLUSION" not in json.dumps(result)
    assert result["acquisitions"] == {"count": 0, "without_retained_copy": 0}
    assert result["packages"] == []
    assert result["uncertainties"] == []
    assert before == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in workbench.rglob("*") if p.is_file()}


def test_missing_and_custom_tables_are_unknown_not_zero(workbench):
    (workbench / "investigations/churn/state.md").write_text("Updated: today\nFindings: none")
    (workbench / "foundation/sources.md").unlink()
    result = status.collect(workbench)
    assert result["active"]["counts"] is None
    assert result["acquisitions"] is None
    assert {u["path"] for u in result["uncertainties"]} == {"investigations/churn/state.md", "foundation/sources.md"}


def test_malformed_table_does_not_count_partial_rows(workbench):
    with (workbench / "investigations/churn/state.md").open("a") as stream:
        stream.write("\n")
    path = workbench / "investigations/churn/state.md"
    path.write_text(path.read_text().replace("| Pricing | evidence.json | supported | |", "| Pricing | too few |"))
    assert status.collect(workbench)["active"]["counts"] is None


def package(workbench, flags):
    draft = "deliveries/churn/review/draft"
    write(workbench, draft + "/manifest.json", json.dumps({"revised_at": "2026-10-01T10:00:00-04:00", "revalidation_flags": flags}))
    write(workbench, "deliveries/churn/review/released/002/manifest.json", json.dumps({"released_at": "2026-09-29T09:00:00-04:00"}))
    return workbench / draft


def flag(disposition, places=("findings text",), reason="Q-004 correction"):
    return {"finding": "Renewal lag", "reason": reason, "represented_in": list(places), "disposition": disposition}


def test_unmatched_flags_are_counted_for_awb_package(workbench):
    package(workbench, "none")
    result = status.collect(workbench)["packages"][0]
    assert result["draft_vs_release"] == "ahead"
    assert result["latest_release"] == "002"
    assert result["unmatched_flags"] == 1
    assert result["confirmed_without_disposition"] == 0
    assert not {"representation_review", "review_methodology", "flags_since_draft", "comparison_is_estimate"} & result.keys()


def test_rerun_since_draft_lists_results_recorded_after_the_draft(workbench):
    draft = package(workbench, "none")
    evidence = {"r-001": "2026-10-01T09:00:00-04:00", "r-002": "2026-10-02T09:00:00-04:00"}
    for result_id, recorded_at in evidence.items():
        write(workbench, f"investigations/churn/evidence/{result_id}.json", json.dumps({"recorded_at": recorded_at}))
    manifest = json.loads((draft / "manifest.json").read_text())
    # A narrative-only package serializes nothing (export_checks none) yet still represents its results.
    manifest["export_checks"] = "none"
    manifest["results"] = [{"result_id": r, "evidence": f"investigations/churn/evidence/{r}.json"} for r in evidence]
    (draft / "manifest.json").write_text(json.dumps(manifest))
    result = status.collect(workbench)
    assert result["packages"][0]["rerun_since_draft"] == ["r-002"] and result["uncertainties"] == []
    manifest["results"] = []
    (draft / "manifest.json").write_text(json.dumps(manifest))
    assert status.collect(workbench)["packages"][0]["rerun_since_draft"] == []
    # Unknown, never empty: a manifest from before `results`, or an escaping or unreadable evidence path.
    del manifest["results"]
    (draft / "manifest.json").write_text(json.dumps(manifest))
    assert status.collect(workbench)["packages"][0]["rerun_since_draft"] is None
    manifest["results"] = [{"result_id": "r-003", "evidence": "../outside.json"}]
    (draft / "manifest.json").write_text(json.dumps(manifest))
    result = status.collect(workbench)
    assert result["packages"][0]["rerun_since_draft"] is None and result["uncertainties"] == []
    manifest["results"] = [{"result_id": "r-003", "evidence": "investigations/churn/evidence/missing.json"}]
    (draft / "manifest.json").write_text(json.dumps(manifest))
    result = status.collect(workbench)
    assert result["packages"][0]["rerun_since_draft"] is None
    assert [u["path"] for u in result["uncertainties"]] == ["investigations/churn/evidence/missing.json"]


def test_release_only_package_counts_every_flag_unmatched(workbench):
    package(workbench, "none")
    __import__("shutil").rmtree(workbench / "deliveries/churn/review/draft")
    result = status.collect(workbench)
    assert result["packages"][0]["unmatched_flags"] == 1
    assert result["packages"][0]["confirmed_without_disposition"] is None
    assert result["uncertainties"] == []


def test_dispositions_require_current_reason(workbench):
    draft = package(workbench, [flag("release_with_caveat", reason="older reason")])
    result = status.collect(workbench)["packages"][0]
    assert (result["unmatched_flags"], result["confirmed_flags"]) == (1, [])
    (draft / "manifest.json").write_text(json.dumps({"revised_at": "2026-10-01T10:00:00-04:00", "revalidation_flags": [flag("none")]}))
    result = status.collect(workbench)["packages"][0]
    assert (result["unmatched_flags"], result["confirmed_without_disposition"]) == (0, 1)


@pytest.mark.parametrize("disposition,blocked", [("omit", False), ("release_with_caveat", False), ("revalidate", True), ("none", True)])
def test_revalidate_and_none_dispositions_block_release(workbench, disposition, blocked):
    package(workbench, [flag(disposition, places=["findings: Renewal lag rose", "chart 1"])])
    result = status.collect(workbench)["packages"][0]
    assert result["confirmed_flags"] == [{"finding": "Renewal lag", "reason": "Q-004 correction", "without_disposition": blocked}]
    assert result["confirmed_without_disposition"] == int(blocked)


def test_flag_the_draft_does_not_represent_needs_no_disposition(workbench):
    package(workbench, [{"finding": "Renewal lag", "reason": "Q-004 correction", "represented_in": "none"}])
    result = status.collect(workbench)
    assert result["packages"][0]["confirmed_flags"] == [{"finding": "Renewal lag", "reason": "Q-004 correction", "without_disposition": False}]
    assert result["packages"][0]["confirmed_without_disposition"] == 0
    assert result["uncertainties"] == []


@pytest.mark.parametrize("bad", [flag(None), flag("waive"), flag("omit", places=[]), flag("omit", places=[""]), flag("omit", places=[{"chart": "1"}]),
                                 {"finding": "Renewal lag", "reason": "Q-004 correction", "represented_in": [{"disposition": "omit"}]},
                                 {"finding": "Renewal lag", "reason": "Q-004 correction", "represented_in": "none", "disposition": "waive"}])
def test_malformed_flag_shape_leaves_counts_unknown(workbench, bad):
    package(workbench, [bad])
    result = status.collect(workbench)
    assert result["packages"][0]["confirmed_without_disposition"] is None
    assert result["packages"][0]["unmatched_flags"] is None
    assert any("revalidation_flags" in u["reason"] for u in result["uncertainties"])


@pytest.mark.parametrize("content", ["not json", "[]", '{"revalidation_flags": ["bad"]}', '{"revised_at": "yesterday", "revalidation_flags": "none"}'])
def test_malformed_manifest_requests_targeted_fallback(workbench, content):
    draft = package(workbench, "none")
    (draft / "manifest.json").write_text(content)
    result = status.collect(workbench)
    assert any(u["path"].endswith("draft/manifest.json") for u in result["uncertainties"])
    assert result["packages"][0]["revised_at"] is None
    assert result["packages"][0]["draft_vs_release"] is None


def test_draft_without_manifest_json_is_an_uncertainty(workbench):
    draft = package(workbench, "none")
    (draft / "manifest.json").unlink()
    (draft / "manifest.yaml").write_text("revised_at: 2026-10-01T10:00:00-04:00")
    result = status.collect(workbench)
    assert result["packages"][0]["revised_at"] is None
    assert result["packages"][0]["confirmed_without_disposition"] is None
    assert [u["path"] for u in result["uncertainties"]] == ["deliveries/churn/review/draft"]


@pytest.mark.parametrize("change", ["remove", "yaml", "not json", "no date", "unreadable"])
def test_unusable_release_manifest_is_uncertain(workbench, monkeypatch, change):
    package(workbench, "none")
    release = workbench / "deliveries/churn/review/released/002/manifest.json"
    if change in {"remove", "yaml"}:
        release.unlink()
        if change == "yaml":
            write(workbench, "deliveries/churn/review/released/002/manifest.yaml", "released_at: 2026-09-29")
    elif change == "unreadable":
        original = Path.read_text
        monkeypatch.setattr(Path, "read_text", lambda path, *a, **k: (_ for _ in ()).throw(PermissionError()) if path == release else original(path, *a, **k))
    else:
        release.write_text("not json" if change == "not json" else "{}")
    result = status.collect(workbench)
    assert result["packages"][0]["latest_release"] == "002"
    assert result["packages"][0]["released_at"] is None
    assert result["packages"][0]["draft_vs_release"] is None
    assert [u["path"] for u in result["uncertainties"]] == [
        "deliveries/churn/review/released/002" if change in {"remove", "yaml"}
        else "deliveries/churn/review/released/002/manifest.json"]


def test_unreadable_draft_manifest_is_unknown(workbench, monkeypatch):
    draft = package(workbench, "none")
    original = Path.read_text
    monkeypatch.setattr(Path, "read_text", lambda path, *a, **k: (_ for _ in ()).throw(PermissionError()) if path == draft / "manifest.json" else original(path, *a, **k))
    result = status.collect(workbench)
    assert result["packages"][0]["revised_at"] is None
    assert result["packages"][0]["confirmed_without_disposition"] is None
    assert any(u["path"].endswith("draft/manifest.json") and "PermissionError" in u["reason"] for u in result["uncertainties"])


def git(root, *args, env=None):
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True, env=env)


def test_git_no_commits_dirty_date_precision_and_no_index_writes(workbench):
    git(workbench, "init")
    file = write(workbench, "investigations/churn/query.sql", "select 1")
    epoch = __import__("datetime").datetime(2026, 10, 1, 12).timestamp()
    os.utime(file, (epoch, epoch))
    # Align all active files so their default fixture mtimes do not obscure the scenario.
    for path in (workbench / "investigations/churn").iterdir():
        os.utime(path, (epoch, epoch))
    git(workbench, "add", ".")
    index = workbench / ".git/index"
    before = (index.read_bytes(), index.stat().st_mtime_ns)
    result = status.collect(workbench)["git"]
    assert result["has_commits"] is False
    assert result["commit_comparison"] == "no commits yet; all work uncommitted"
    assert result["state_status"] == "indeterminate at date precision"
    assert before == (index.read_bytes(), index.stat().st_mtime_ns)
    os.utime(file, (epoch + 2 * 86400, epoch + 2 * 86400))
    result = status.collect(workbench)["git"]
    assert result["state_status"] == "out of date"
    assert result["days_after_state"] == 2


def test_commit_out_of_date_state_and_undated_deletion(workbench):
    git(workbench, "init")
    git(workbench, "add", ".")
    env = {**os.environ, "GIT_AUTHOR_DATE": "2026-10-02T12:00:00Z", "GIT_COMMITTER_DATE": "2026-10-02T12:00:00Z"}
    git(workbench, "-c", "user.name=Test", "-c", "user.email=test@example.test", "commit", "-m", "fixture", env=env)
    result = status.collect(workbench)["git"]
    assert result["state_status"] == "out of date"
    assert result["days_after_state"] == 1
    (workbench / "investigations/churn/brief.md").unlink()
    result = status.collect(workbench)
    assert result["git"]["undated_changes"] == ["investigations/churn/brief.md"]
    assert any("mtime" in u["reason"] for u in result["uncertainties"])


def test_acquisitions_and_storage_risks(workbench):
    path = workbench / "foundation/sources.md"
    path.write_text(path.read_text() + "\n| a1 | s1 | today | request | data/raw/a | this checkout only | check | | |\n| a2 | s1 | today | request | data/raw/b | | check | | |\n")
    result = status.collect(workbench)
    assert result["acquisitions"] == {"count": 2, "without_retained_copy": 2}
    assert result["landed_data_storage"] == {"location": "none chosen", "availability": "none chosen"}
    assert result["release_storage"]["availability"] == "unrecorded"


def test_absent_project_and_unsafe_active_pointer(tmp_path, workbench):
    assert status.collect(tmp_path / "missing")["workbench"] is False
    (workbench / "README.md").write_text("Active investigation: ../../outside\n")
    result = status.collect(workbench)
    assert result["active"] is None
    assert any("pointer" in u["reason"] for u in result["uncertainties"])


@pytest.mark.parametrize("pointer", ["[Churn investigation](investigations/churn/state.md)", "investigations/churn/state.md", "`investigations/churn/state.md`", "[Churn](./investigations/churn/state.md)"])
def test_standard_active_state_pointer(workbench, pointer):
    path = workbench / "README.md"
    path.write_text(path.read_text().replace("Active investigation: churn", "Active investigation: " + pointer))
    result = status.collect(workbench)
    assert result["active"]["name"] == "churn"
    assert result["active"]["counts"]["supported"] == 1
    assert result["uncertainties"] == []


def test_other_state_reader_stops_before_conclusions(workbench, monkeypatch):
    other = write(workbench, "investigations/pricing/state.md", "irrelevant on-disk fixture")
    original_open = Path.open

    class PreambleOnly:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def __iter__(self):
            yield "# State\n"
            yield "Last updated: 2026-08-01\n"
            raise AssertionError("Collector attempted to read another investigation's conclusions")

    def guarded_open(path, *args, **kwargs):
        return PreambleOnly() if path == other else original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded_open)
    assert status.collect(workbench)["other_investigations"] == [{"name": "pricing", "last_updated": "2026-08-01"}]


def test_blank_fields_do_not_capture_following_lines(workbench):
    path = workbench / "README.md"
    path.write_text("Active investigation: \nLanded data is kept at: \nReleased packages are kept at: /tmp\n")
    result = status.collect(workbench)
    assert result["active"] is None
    assert result["landed_data_storage"] == {"location": None, "availability": "unrecorded"}
    assert result["release_storage"]["location"] == "/tmp"
    assert any("Active investigation" in u["reason"] for u in result["uncertainties"])
    path.write_text(path.read_text().replace("Active investigation: \n", "Active investigation: churn\n"))
    state = workbench / "investigations/churn/state.md"
    state.write_text(state.read_text().replace("Last updated: 2026-10-01", "Last updated: "))
    result = status.collect(workbench)
    assert result["active"]["last_updated"] is None
    assert any("Last updated" in u["reason"] for u in result["uncertainties"])


def test_backticked_checkout_only_is_missing_retained_copy(workbench):
    path = workbench / "foundation/sources.md"
    path.write_text(path.read_text() + "\n| a1 | s1 | today | request | data/raw/a | `this checkout only` | check | | |\n")
    result = status.collect(workbench)
    assert result["acquisitions"]["without_retained_copy"] == 1


def test_optional_storage_fields_absent_before_use_are_not_uncertainties(workbench):
    (workbench / "README.md").write_text("Active investigation: churn\n")
    result = status.collect(workbench)
    assert result["landed_data_storage"]["availability"] == "unrecorded"
    assert result["release_storage"]["availability"] == "unrecorded"
    assert result["uncertainties"] == []


def test_nested_repository_status_scopes_changes_and_preserves_index(workbench, tmp_path):
    repository = workbench
    nested = repository / "nested"
    nested.mkdir()
    for path in list(repository.iterdir()):
        if path != nested:
            path.rename(nested / path.name)
    workbench = nested
    git(repository, "init")
    git(repository, "add", ".")
    env = {**os.environ, "GIT_AUTHOR_DATE": "2026-09-29T12:00:00Z", "GIT_COMMITTER_DATE": "2026-09-29T12:00:00Z"}
    git(repository, "-c", "user.name=Test", "-c", "user.email=test@example.test", "commit", "-m", "fixture", env=env)
    # A later commit outside this project must not advance this investigation's date.
    write(repository, "investigations/churn/outside.sql", "select 'outside'")
    git(repository, "add", ".")
    env.update(GIT_AUTHOR_DATE="2026-10-08T12:00:00Z", GIT_COMMITTER_DATE="2026-10-08T12:00:00Z")
    git(repository, "-c", "user.name=Test", "-c", "user.email=test@example.test", "commit", "-m", "outside", env=env)
    inside = write(workbench, "investigations/churn/query.sql", "select 1")
    outside = write(repository, "investigations/churn/uncommitted.sql", "select 2")
    epoch = __import__("datetime").datetime(2026, 10, 3, 12).timestamp()
    os.utime(inside, (epoch, epoch))
    os.utime(outside, (epoch + 5 * 86400, epoch + 5 * 86400))
    index = repository / ".git/index"
    before = (index.read_bytes(), index.stat().st_mtime_ns)
    result = status.collect(workbench)["git"]
    assert result["available"] is True
    assert result["uncommitted_paths"] == 1
    assert result["latest_commit_date"] == "2026-09-29"
    assert result["latest_change"] == {"date": "2026-10-03", "source": "investigations/churn/query.sql"}
    assert result["days_after_state"] == 2
    assert before == (index.read_bytes(), index.stat().st_mtime_ns)


@pytest.mark.parametrize("unreadable,unknown_field", [("investigations", "other_investigations"), ("deliveries/churn", "packages"), ("deliveries/churn/review/released", "releases")])
def test_unreadable_enumeration_is_unknown_not_empty(workbench, monkeypatch, unreadable, unknown_field):
    package(workbench, "none")
    blocked = workbench / unreadable
    original_iterdir, original_glob = Path.iterdir, Path.glob

    def checked_iterdir(path):
        if path == blocked:
            raise PermissionError("fixture directory unreadable")
        return original_iterdir(path)

    def checked_glob(path, *args, **kwargs):
        if path == blocked:
            raise PermissionError("fixture directory unreadable")
        return original_glob(path, *args, **kwargs)

    monkeypatch.setattr(Path, "iterdir", checked_iterdir)
    monkeypatch.setattr(Path, "glob", checked_glob)
    result = status.collect(workbench)
    assert any(u["path"] == unreadable and "enumerat" in u["reason"].lower() for u in result["uncertainties"])
    if unknown_field in {"other_investigations", "packages"}:
        assert result[unknown_field] is None
    else:
        assert result["packages"][0]["release_inventory_known"] is False
        assert result["packages"][0]["latest_release"] is None


@pytest.mark.parametrize("value", ["`none chosen`", "None chosen", "none"])
def test_none_chosen_is_a_recorded_decision(workbench, value):
    path = workbench / "README.md"
    path.write_text(path.read_text().replace("Landed data is kept at: none chosen", "Landed data is kept at: " + value).replace("not yet recorded", value))
    result = status.collect(workbench)
    assert result["landed_data_storage"] == {"location": value, "availability": "none chosen"}
    assert result["release_storage"] == {"location": value, "availability": "none chosen"}


def test_absent_storage_remains_actionable_when_acquisitions_and_releases_exist(workbench):
    (workbench / "README.md").write_text("Active investigation: churn\n")
    sources = workbench / "foundation/sources.md"
    sources.write_text(sources.read_text() + "\n| a1 | s1 | today | request | data/raw/a | this checkout only | check | | |\n")
    package(workbench, "none")
    result = status.collect(workbench)
    assert result["acquisitions"] == {"count": 1, "without_retained_copy": 1}
    assert result["packages"][0]["latest_release"] == "002"
    assert result["landed_data_storage"]["availability"] == "unrecorded"
    assert result["release_storage"]["availability"] == "unrecorded"
    assert result["uncertainties"] == []


def test_status_reads_rendered_table_with_json_present(workbench):
    write(workbench, "investigations/churn/findings.json", json.dumps({"schema": "awb-findings/1", "findings": []}))
    before = {p: p.read_bytes() for p in workbench.rglob("*") if p.is_file()}
    result = status.collect(workbench)
    assert result["active"]["counts"] == {"revalidation-needed": 1, "supported": 1}
    assert {"finding": "Renewal lag", "status": "revalidation-needed",
            "reason": "Q-004 correction"} in result["active"]["findings"]
    assert before == {p: p.read_bytes() for p in workbench.rglob("*") if p.is_file()}


LANDING = ROOT / ".agents/skills/awb-init/assets/awb_landing.py"
landing_spec = importlib.util.spec_from_file_location("awb_landing_for_status", LANDING)
landing = importlib.util.module_from_spec(landing_spec)
landing_spec.loader.exec_module(landing)


def land_with_upstream(root, acquisition_id, upstream, source="api"):
    def fetch(directory):
        for name in upstream:
            (directory / name).write_bytes(name.encode())
    return landing.land(root, source, acquisition_id, fetch, request="query",
                        upstream={name: fields for name, fields in upstream.items() if fields})


class FakeServer:
    """Answers HEAD requests from a table of URL to headers or exception; records each request."""

    def __init__(self, answers):
        self.answers, self.requests = answers, []

    def __call__(self, request, timeout):
        import email.message
        self.requests.append((request.get_method(), request.full_url, timeout))
        answer = self.answers[request.full_url]
        if isinstance(answer, Exception):
            raise answer
        headers = email.message.Message()
        for name, value in answer.items():
            headers[name] = value

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False
        response = Response()
        response.headers = headers
        return response


def serve(monkeypatch, server):
    """Replace the probe's opener with server, which answers request and timeout."""
    monkeypatch.setattr(status, "head_opener", lambda: SimpleNamespace(open=server))


def refuse_network():
    raise AssertionError("status built an opener without --probe-upstream")


def test_upstream_probe_reports_each_file_changed_unchanged_or_unknown_without_writes(workbench, monkeypatch):
    import urllib.error
    url = "https://example.test/"
    land_with_upstream(workbench, "batch-1", {
        "same.csv": {"url": url + "same", "etag": '"v1"'},
        "weak.csv": {"url": url + "weak", "etag": 'W/"v1"'},
        "moved.csv": {"url": url + "moved", "etag": '"v1"', "last_modified": "Tue, 13 Oct 2026 08:00:00 GMT"},
        "dated.csv": {"url": url + "dated", "last_modified": "Tue, 13 Oct 2026 08:00:00 GMT"},
        "fallback.csv": {"url": url + "fallback", "etag": '"v1"', "last_modified": "Tue, 13 Oct 2026 08:00:00 GMT"},
        "regzipped.csv": {"url": url + "regzipped", "etag": '"v1-gzip"', "last_modified": "Tue, 13 Oct 2026 08:00:00 GMT"},
        "silent.csv": {"url": url + "silent", "etag": '"v1"'},
        "gone.csv": {"url": url + "gone", "etag": '"v1"'},
        "down.csv": {"url": url + "down", "last_modified": "Tue, 13 Oct 2026 08:00:00 GMT"},
        "s3.csv": {"url": "s3://bucket/s3.csv", "version_id": "3HL4kqtJ"},
        "bare.csv": {"url": url + "bare"},
        "local.csv": None,
    })
    write(workbench, "data/raw/api/batch-2.partial/provenance.json", "not read")
    server = FakeServer({
        url + "same": {"ETag": '"v1"'},
        url + "weak": {"ETag": '"v1"'},
        url + "moved": {"ETag": '"v2"', "Last-Modified": "Tue, 13 Oct 2026 09:00:00 GMT"},
        url + "regzipped": {"ETag": '"v1"', "Last-Modified": "Tue, 13 Oct 2026 08:00:00 GMT"},
        url + "dated": {"Last-Modified": "Tuesday, 13-Oct-26 08:00:00 GMT"},
        url + "fallback": {"Last-Modified": "Wed, 14 Oct 2026 09:30:00 GMT"},
        url + "silent": {},
        url + "gone": urllib.error.HTTPError(url + "gone", 404, "Not Found", None, None),
        url + "down": urllib.error.URLError("connection refused"),
    })
    serve(monkeypatch, server)
    before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in workbench.rglob("*") if p.is_file()}
    result = status.collect(workbench, probe_upstream=True)["upstream"]
    assert before == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in workbench.rglob("*") if p.is_file()}
    assert sorted(server.requests) == sorted(("HEAD", url + name, status.PROBE_TIMEOUT) for name in
                                             ("same", "weak", "moved", "regzipped", "dated", "fallback", "silent", "gone", "down"))
    assert result["probeable_files"] == 9
    file = {"source": "api", "acquisition_id": "batch-1"}
    assert result["files"] == [
        {**file, "path": "dated.csv", "result": "unchanged", "compared": "last_modified"},
        {**file, "path": "down.csv", "result": "unknown", "reason": "URLError: <urlopen error connection refused>"},
        {**file, "path": "fallback.csv", "result": "changed", "compared": "last_modified",
         "recorded": "Tue, 13 Oct 2026 08:00:00 GMT", "current": "Wed, 14 Oct 2026 09:30:00 GMT"},
        {**file, "path": "gone.csv", "result": "unknown", "reason": "HTTP 404"},
        {**file, "path": "moved.csv", "result": "changed", "compared": "etag", "recorded": '"v1"', "current": '"v2"'},
        {**file, "path": "regzipped.csv", "result": "unknown", "reason": "the ETag differs but Last-Modified is unchanged"},
        {**file, "path": "same.csv", "result": "unchanged", "compared": "etag"},
        {**file, "path": "silent.csv", "result": "unknown", "reason": "the server sent neither recorded validator"},
        {**file, "path": "weak.csv", "result": "unchanged", "compared": "etag"},
    ]
    assert result["not_probeable"] == [
        {**file, "path": "bare.csv", "reason": "no ETag or Last-Modified recorded"},
        {**file, "path": "s3.csv", "reason": "no HTTP URL recorded"},
    ]
    assert result["superseded"] == 0
    assert result["without_upstream"] == 1


def test_an_unusable_server_validator_is_unknown_and_the_probe_continues(workbench, monkeypatch):
    date, url = "Wed, 21 Oct 2015 07:28:00 GMT", "https://example.test/"
    both = {"etag": '"abc"', "last_modified": date}
    cases = {  # path: (recorded, served, expected result, expected reason or compared)
        "a-empty-etag.csv": (both, {"ETag": ""}, "unknown", "the server's ETag is not a usable validator"),
        "b-garbage-date.csv": (both, {"Last-Modified": "garbage"}, "unknown",
                               "the server's Last-Modified is not a usable validator"),
        "c-both-unusable.csv": (both, {"ETag": " ", "Last-Modified": "garbage"}, "unknown",
                                "the server's ETag and Last-Modified are not usable validators"),
        "d-empty-etag-same-date.csv": (both, {"ETag": "", "Last-Modified": date}, "unchanged", "last_modified"),
        "e-garbage-date-same-etag.csv": (both, {"ETag": '"abc"', "Last-Modified": "garbage"}, "unchanged", "etag"),
        "f-overflowing-year.csv": ({"last_modified": date}, {"Last-Modified": "Tue, 13 Oct 9999999999 08:00:00 GMT"},
                                   "unknown", "the server's Last-Modified is not a usable validator"),
        "g-overflowing-offset.csv": ({"last_modified": date}, {"Last-Modified": "Tue, 13 Oct 2026 08:00:00 +99999999"},
                                     "unknown", "the server's Last-Modified is not a usable validator"),
        "h-text-dates-same.csv": ({"last_modified": "build 7"}, {"Last-Modified": "build 7"}, "unchanged", "last_modified"),
        "i-text-dates-differ.csv": ({"last_modified": "build 7"}, {"Last-Modified": "build 8"}, "changed", "last_modified"),
        "j-recorded-text-served-date.csv": ({"last_modified": "build 7"}, {"Last-Modified": date}, "unknown",
                                            "the server's Last-Modified is not a usable validator"),
        "k-next.csv": ({"last_modified": date}, {"Last-Modified": date}, "unchanged", "last_modified"),
    }
    land_with_upstream(workbench, "batch-1", {path: {"url": url + path, **recorded}
                                              for path, (recorded, _, _, _) in cases.items()})
    server = FakeServer({url + path: served for path, (_, served, _, _) in cases.items()})
    serve(monkeypatch, server)
    files = status.collect(workbench, probe_upstream=True)["upstream"]["files"]
    assert [(file["path"], file["result"], file.get("reason") or file.get("compared")) for file in files] == [
        (path, result, detail) for path, (_, _, result, detail) in cases.items()]
    assert len(server.requests) == len(cases)


def test_a_relanded_url_is_checked_only_in_its_latest_acquisition(workbench, monkeypatch):
    times = iter(f"2026-10-13T08:00:0{second}+02:00" for second in range(10))
    monkeypatch.setattr(landing, "_timestamp", lambda: next(times))
    url = "https://example.test/"
    land_with_upstream(workbench, "batch-1", {"data.csv": {"url": url + "data", "etag": '"v1"'},
                                              "page.csv": {"url": url + "page", "etag": '"p1"'}})
    land_with_upstream(workbench, "batch-1", {"data.csv": {"url": url + "data", "etag": '"v1"'}}, source="mirror")
    server = FakeServer({url + "data": {"ETag": '"v2"'}, url + "page": {"ETag": '"p2"'}})
    serve(monkeypatch, server)
    changed = status.collect(workbench, probe_upstream=True)["upstream"]
    assert [(f["source"], f["path"], f["result"]) for f in changed["files"]] == [
        ("api", "data.csv", "changed"), ("api", "page.csv", "changed"), ("mirror", "data.csv", "changed")]
    # Land again as the re-land request row says; page.csv is now recorded without a validator.
    land_with_upstream(workbench, "batch-2", {"data.csv": {"url": url + "data", "etag": '"v2"'},
                                              "page.csv": {"url": url + "page"}})
    server.requests.clear()
    result = status.collect(workbench, probe_upstream=True)["upstream"]
    assert result["probeable_files"] == 2
    assert [(f["source"], f["acquisition_id"], f["path"], f["result"]) for f in result["files"]] == [
        ("api", "batch-2", "data.csv", "unchanged"), ("mirror", "batch-1", "data.csv", "changed")]
    assert result["not_probeable"] == [{"source": "api", "acquisition_id": "batch-2", "path": "page.csv",
                                        "reason": "no ETag or Last-Modified recorded"}]
    assert result["superseded"] == 2
    assert sorted(url for _, url, _ in server.requests) == [url + "data", url + "data"]


@pytest.mark.parametrize("completed, checked", [
    ({"batch-1": "2026-10-13T08:00:00+00:00", "batch-2": "2026-10-13T09:00:00+00:00"}, "batch-2"),
    ({"z-old": "2026-10-13T10:00:00+02:00", "a-new": "2026-10-13T08:30:00+00:00"}, "a-new"),
    ({"a1": "2026-10-13T08:00:00+00:00", "a2": "2026-10-13T08:00:00+00:00"}, "a2"),
    ({"a2": "2026-10-13T08:00:00+00:00", "a1": "2026-10-13T10:00:00+02:00"}, "a2"),
])
def test_the_latest_acquisition_is_ordered_by_completed_at_then_acquisition_id(workbench, monkeypatch, completed, checked):
    url = "https://example.test/data"
    for etag, (acquisition_id, at) in enumerate(completed.items(), start=1):
        monkeypatch.setattr(landing, "_timestamp", lambda at=at: at)
        land_with_upstream(workbench, acquisition_id, {"data.csv": {"url": url, "etag": f'"v{etag}"'}})
    server = FakeServer({url: {"ETag": '"v2"'}})
    serve(monkeypatch, server)
    result = status.collect(workbench, probe_upstream=True)["upstream"]
    assert (result["probeable_files"], result["superseded"]) == (1, 1)
    assert [(file["acquisition_id"], file["result"]) for file in result["files"]] == [
        (checked, "unchanged" if list(completed).index(checked) == 1 else "changed")]
    assert [request_url for _, request_url, _ in server.requests] == [url]


@pytest.mark.parametrize("timeout", ["connect", "read"])
def test_a_host_that_times_out_is_not_requested_again(workbench, monkeypatch, timeout):
    import urllib.error
    error = urllib.error.URLError(TimeoutError("timed out")) if timeout == "connect" else TimeoutError("timed out")
    land_with_upstream(workbench, "batch-1", {name: {"url": f"https://{host}/{name}", "etag": '"v1"'} for name, host in
                                              (("a.csv", "slow.test"), ("b.csv", "slow.test"), ("c.csv", "fast.test"))})
    server = FakeServer({"https://slow.test/a.csv": error, "https://fast.test/c.csv": {"ETag": '"v1"'}})
    serve(monkeypatch, server)
    files = status.collect(workbench, probe_upstream=True)["upstream"]["files"]
    assert [(file["path"], file["result"], file.get("reason")) for file in files] == [
        ("a.csv", "unknown", f"no response from slow.test within {status.PROBE_TIMEOUT} s"),
        ("b.csv", "unknown", "not requested: an earlier request to slow.test timed out"),
        ("c.csv", "unchanged", None)]
    assert [url for _, url, _ in server.requests] == ["https://slow.test/a.csv", "https://fast.test/c.csv"]


def test_status_without_probe_counts_probeable_files_and_sends_nothing(workbench, monkeypatch):
    monkeypatch.setattr(status, "head_opener", refuse_network)
    assert status.collect(workbench)["upstream"] == {"probeable_files": 0}
    land_with_upstream(workbench, "batch-1", {"a.csv": {"url": "https://example.test/a", "etag": '"v1"'},
                                              "b.csv": {"url": "s3://bucket/b", "version_id": "1"}})
    assert status.collect(workbench)["upstream"] == {"probeable_files": 1}


@pytest.mark.parametrize("text, reason", [
    ("[1, 2]", "Malformed acquisition provenance: not a JSON object"),
    ("{", "Cannot read acquisition provenance: JSONDecodeError"),
    ("{}", "Malformed acquisition provenance: status is not complete"),
    ('{"status": "complete", "files": []}',
     "Malformed acquisition provenance: completed_at is not an ISO timestamp with a UTC offset"),
    ('{"status": "complete", "completed_at": "2026-10-13T08:00:00", "files": []}',
     "Malformed acquisition provenance: completed_at is not an ISO timestamp with a UTC offset"),
    ('{"status": "complete", "completed_at": "2026-10-13T08:00:00+00:00", "files": {}}', "Malformed acquisition provenance: files is not a list"),
    ('{"status": "complete", "completed_at": "2026-10-13T08:00:00+00:00", "files": [{"path": 7, "upstream": null}]}',
     "Malformed acquisition provenance: a file entry has no path"),
    ('{"status": "complete", "completed_at": "2026-10-13T08:00:00+00:00", "files": ["a.csv"]}', "Malformed acquisition provenance: a file entry has no path"),
    *[(json.dumps({"status": "complete", "completed_at": "2026-10-13T08:00:00+00:00",
                   "files": [{"path": "a.csv", "upstream": upstream}]}), "Malformed acquisition provenance: " + reason)
      for upstream, reason in [
          ("https://example.test/a", "upstream fields of a.csv must be a dictionary of url, etag, last_modified, version_id"),
          ({"url": "https://example.test/a", "lastModified": "x"},
           "upstream fields of a.csv must be a dictionary of url, etag, last_modified, version_id"),
          ({"url": "https://example.test/a", "etag": 7}, "upstream fields of a.csv must be nonblank strings or None"),
          ({"url": "https://example.test/a", "etag": " "}, "upstream fields of a.csv must be nonblank strings or None"),
          ({"url": "https://[", "etag": '"v1"'}, "upstream url of a.csv is not a valid URL"),
          ({"url": "https://example.test/d?api_key=SECRET", "etag": '"v1"'},
           "upstream url of a.csv carries credential parameters (api_key); record it without credentials"),
          ({"url": "https://example.test/x;format=csv&access_token=SECRET", "etag": '"v1"'},
           "upstream url of a.csv carries credential parameters (access_token); record it without credentials"),
          ({"url": "user:SECRET@example.test/x", "etag": '"v1"'},
           "upstream url of a.csv carries a user name or password; record it without credentials"),
      ]],
    (None, "Missing acquisition provenance"),
])
def test_unreadable_provenance_is_an_uncertainty_and_leaves_the_count_unknown(workbench, monkeypatch, text, reason):
    land_with_upstream(workbench, "batch-1", {"a.csv": {"url": "https://example.test/a", "etag": '"v1"'}})
    if text is None:
        write(workbench, "data/raw/api/broken/a.csv", "a")
    else:
        write(workbench, "data/raw/api/broken/provenance.json", text)
    write(workbench, "data/raw/api/batch-2.partial/provenance.json", "{")
    write(workbench, "data/raw/api/notes.txt", "not an acquisition")
    server = FakeServer({"https://example.test/a": {"ETag": '"v1"'}})
    serve(monkeypatch, server)
    uncertainties = [{"path": "data/raw/api/broken/provenance.json", "reason": reason}]
    default = status.collect(workbench)
    assert (default["uncertainties"], default["upstream"]) == (uncertainties, {"probeable_files": None})
    result = status.collect(workbench, probe_upstream=True)
    assert result["uncertainties"] == uncertainties
    assert result["upstream"] == {
        "probeable_files": None,
        "files": [{"source": "api", "acquisition_id": "batch-1", "path": "a.csv", "result": "unchanged", "compared": "etag"}],
        "not_probeable": [], "superseded": 0, "without_upstream": 0}
    assert [url for _, url, _ in server.requests] == ["https://example.test/a"]
    assert "SECRET" not in json.dumps(result)


def test_provenance_without_upstream_keys_counts_as_without_upstream(workbench, monkeypatch):
    monkeypatch.setattr(status, "head_opener", refuse_network)
    write(workbench, "data/raw/api/old/provenance.json", json.dumps(
        {"status": "complete", "completed_at": "2026-10-13T08:00:00+00:00",
         "files": [{"path": "a.csv", "bytes": 1, "sha256": "0", "records": None}]}))
    result = status.collect(workbench)
    assert result["uncertainties"] == [] and result["upstream"] == {"probeable_files": 0}


@pytest.mark.parametrize("blocked", ["data/raw", "data/raw/api"])
def test_unreadable_acquisition_inventory_is_unknown_not_zero(workbench, monkeypatch, blocked):
    land_with_upstream(workbench, "batch-1", {"a.csv": {"url": "https://example.test/a", "etag": '"v1"'}})
    land_with_upstream(workbench, "batch-1", {"w.csv": {"url": "https://example.test/w", "etag": '"v1"'}}, source="web")
    original_iterdir = Path.iterdir

    def checked_iterdir(path):
        if path == workbench / blocked:
            raise PermissionError("fixture directory unreadable")
        return original_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", checked_iterdir)
    serve(monkeypatch, FakeServer({"https://example.test/w": {"ETag": '"v1"'}}))
    result = status.collect(workbench, probe_upstream=True)
    assert {"path": blocked, "reason": "Cannot enumerate directory: PermissionError"} in result["uncertainties"]
    assert result["upstream"]["probeable_files"] is None
    assert [file["path"] for file in result["upstream"]["files"]] == ([] if blocked == "data/raw" else ["w.csv"])


def test_probe_follows_redirects_only_to_http_and_only_as_head(workbench, monkeypatch):
    """Runs urllib's own redirect processing; only the HTTPS and FTP connections are replaced."""
    import email.message
    import io
    import urllib.request
    import urllib.response
    answers = {
        "https://example.test/ftp": (302, {"Location": "ftp://example.test/source.csv"}),
        "https://example.test/old": (301, {"Location": "https://example.test/new"}),
        "https://example.test/new": (200, {"ETag": '"v1"'}),
    }
    requests, ftp = [], []

    def https_open(handler, request):
        requests.append((request.get_method(), request.full_url))
        code, fields = answers[request.full_url]
        headers = email.message.Message()
        for name, value in fields.items():
            headers[name] = value
        response = urllib.response.addinfourl(io.BytesIO(b""), headers, request.full_url, code)
        response.msg = "Redirect" if code != 200 else "OK"
        return response

    monkeypatch.setattr(urllib.request.HTTPSHandler, "https_open", https_open)
    monkeypatch.setattr(urllib.request.FTPHandler, "ftp_open", lambda handler, request: ftp.append(request.full_url))
    land_with_upstream(workbench, "batch-1", {"ftp.csv": {"url": "https://example.test/ftp", "etag": '"v1"'},
                                              "old.csv": {"url": "https://example.test/old", "etag": '"v1"'}})
    files = status.collect(workbench, probe_upstream=True)["upstream"]["files"]
    assert [(file["path"], file["result"], file.get("reason")) for file in files] == [
        ("ftp.csv", "unknown", "redirected to a URL other than http(s), not followed"),
        ("old.csv", "unchanged", None),
    ]
    assert ftp == []
    assert requests == [("HEAD", "https://example.test/ftp"), ("HEAD", "https://example.test/old"),
                        ("HEAD", "https://example.test/new")]


@pytest.mark.parametrize("timeout", ["connect", "read"])
def test_a_redirect_target_that_times_out_is_not_requested_again(workbench, monkeypatch, timeout):
    """Runs urllib's own redirect processing; only the HTTPS connections are replaced."""
    import email.message
    import io
    import urllib.error
    import urllib.parse
    import urllib.request
    import urllib.response
    answers = {
        "https://one.test/a": (302, {"Location": "https://slow.test/a"}),
        "https://two.test/c": (307, {"Location": "https://slow.test/c"}),
        "https://one.test/d": (200, {"ETag": '"v1"'}),
    }
    requests = []

    def https_open(handler, request):
        requests.append((request.get_method(), request.full_url))
        if urllib.parse.urlsplit(request.full_url).hostname == "slow.test":
            raise urllib.error.URLError(TimeoutError("timed out")) if timeout == "connect" else TimeoutError("timed out")
        code, fields = answers[request.full_url]
        headers = email.message.Message()
        for name, value in fields.items():
            headers[name] = value
        response = urllib.response.addinfourl(io.BytesIO(b""), headers, request.full_url, code)
        response.msg = "Redirect" if code != 200 else "OK"
        return response

    monkeypatch.setattr(urllib.request.HTTPSHandler, "https_open", https_open)
    land_with_upstream(workbench, "batch-1", {"a.csv": {"url": "https://one.test/a", "etag": '"v1"'},
                                              "b.csv": {"url": "https://slow.test/b", "etag": '"v1"'},
                                              "c.csv": {"url": "https://two.test/c", "etag": '"v1"'},
                                              "d.csv": {"url": "https://one.test/d", "etag": '"v1"'}})
    files = status.collect(workbench, probe_upstream=True)["upstream"]["files"]
    assert [(file["path"], file["result"], file.get("reason")) for file in files] == [
        ("a.csv", "unknown", f"no response from slow.test within {status.PROBE_TIMEOUT} s"),
        ("b.csv", "unknown", "not requested: an earlier request to slow.test timed out"),
        ("c.csv", "unknown", "redirected to slow.test, not followed: an earlier request to slow.test timed out"),
        ("d.csv", "unchanged", None),
    ]
    assert requests == [("HEAD", "https://one.test/a"), ("HEAD", "https://slow.test/a"),
                        ("HEAD", "https://two.test/c"), ("HEAD", "https://one.test/d")]


def test_probe_upstream_flag_reaches_the_probe(workbench, monkeypatch, capsys):
    land_with_upstream(workbench, "batch-1", {"a.csv": {"url": "https://example.test/a", "etag": '"v1"'}})
    serve(monkeypatch, FakeServer({"https://example.test/a": {"ETag": '"v2"'}}))
    monkeypatch.setattr("sys.argv", ["collect_status.py", str(workbench), "--probe-upstream"])
    status.main()
    files = json.loads(capsys.readouterr().out)["upstream"]["files"]
    assert [(file["path"], file["result"]) for file in files] == [("a.csv", "changed")]
