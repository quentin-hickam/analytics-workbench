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
# test_a_preview_only_draft_reports_the_preview_not_a_missing_manifest: a draft holding only .preview/headlines.md reports draft_stage "headline preview written, not yet exported" and no uncertainty; without the preview, a missing manifest is uncertain again.
# test_draft_without_manifest_json_is_an_uncertainty: a draft manifest in another format is not read; the draft is named under uncertainties.
# test_unusable_release_manifest_is_uncertain: an absent, non-JSON, undated, or unreadable release manifest leaves released_at null and records one uncertainty.
# test_unreadable_draft_manifest_is_unknown: an unreadable draft manifest leaves dates and counts null with an uncertainty.
# test_git_no_commits_dated_state_and_no_index_writes: no-commit wording; a dated state and a change on its day are "saved the same day as the latest change", a later day out of date; the index is untouched.
# test_commit_out_of_date_state_and_undated_deletion: a later commit makes the state out of date; a deleted file is an undated change.
# test_results_recorded_before_the_first_commit_are_listed_for_a_rerun: once the repository has a commit, evidence whose producing_commit is uncommitted, unknown, or unreadable is listed under git.uncommitted_evidence (unreadable with an uncertainty), and evidence naming a commit is not; before any commit, or with no evidence folder, nothing is listed.
# test_ledger_writes_leave_the_state_current: a later questions.json or questions.md change, uncommitted or committed, leaves the state current; a later brief change does not.
# test_a_state_written_after_the_latest_change_on_the_same_day_is_up_to_date: a timestamped state orders changes by time, a change in its own second not after it, a Z time read as an instant.
# test_a_state_time_without_its_offset_or_malformed_is_uncertain: a time without its offset, a space separator, fractional seconds, an impossible hour, or prose is an uncertainty and leaves the status unknown.
# test_committed_changes_are_ordered_by_their_own_times: a commit after the state does not date its changes; a file rewritten after its commit, or deleted, has only the commit's time and leaves the order unknown in plain words; one committed before the state is not after it.
# test_a_committed_path_git_quotes_is_dated_only_by_its_commit: a committed path Git prints quoted is dated by its commit alone, so a commit after the state leaves the order unknown.
# test_findings_are_grouped_by_question: each root counts the findings answering it or a question under it by status, with its origin; findings no question names, under a missing parent or without an evidence link, are counted apart.
# test_unreadable_findings_leave_the_counts_by_question_unknown: an unreadable findings table makes the counts by question and the caveats null, never empty.
# test_every_findings_caveat_is_reported: every finding with a caveat cell is listed with it, flagged or not, check segments included.
# test_acquisitions_and_storage_risks: checkout-only and blank retained copies count; a declined landed-data line reads none chosen.
# test_sources_assessed_from_documentation_need_a_reference: a source whose Relevance and fitness begins from documentation is listed, with a reason, unless a Notes clause opens with reference: directly followed by one of the kept-copy forms foundation/sources.md defines, a link in its stated grammar or a backticked location with its sha256, in plain text outside code, HTML, emphasis, strikethrough, links and brackets; REFERENCE_PROBES holds every reviewer probe in both directions; a landed-records basis mentioning documentation later is not listed; an assessment without a leading basis is an uncertainty; an unsupported Sources table is null with an uncertainty.
# test_an_access_note_is_a_known_limitation_not_a_missing_reference: a reference: clause giving `read at <URL> on <date>, not kept: <reason>` lists the source under documentation_access_notes and not documentation_without_reference; with a kept-copy form beside it the source is in neither; a malformed note (no date, no reason, no URL scheme, inside code) is listed as without reference.
# test_reasons_say_why_a_source_lacks_a_reference: no reference: clause, a label followed by none of the forms (as `not yet retained`), a label that opens no plain-text clause, and reading stopped by raw HTML or emphasis each give their reason.
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
# test_latest_release_in_storage_reads_the_storage_layout: with reachable release storage, a package's latest release counts as stored only at <location>/<investigation>/<package>/<n>/, not under an earlier released/ folder; unrecorded or unreachable storage leaves it null.
# test_upstream_probe_reports_each_file_changed_unchanged_or_unknown_without_writes: land()'s upstream fields drive one HEAD per probeable file; ETag wins over Last-Modified unless only the ETag changed, a weak ETag and an equal date in another form match, HTTP and network errors are unknown, and nothing is written.
# test_an_unusable_server_validator_is_unknown_and_the_probe_continues: a blank ETag or a Last-Modified that does not parse (including an overflowing year or offset) gives no evidence of change; the other validator decides if usable, else the file is unknown; two unparseable dates are compared as text; later files are still probed.
# test_a_relanded_url_is_checked_only_in_its_latest_acquisition: after a changed upstream is landed again, only the newest acquisition of that source and URL is probed and the earlier one counts as superseded, even when the newer one records no validator.
# test_the_latest_acquisition_is_ordered_by_completed_at_then_acquisition_id: completed_at instants are compared across offsets, not by ID, and acquisitions completed in the same second are ordered by acquisition ID, so exactly one stays current.
# test_a_host_that_times_out_is_not_requested_again: after a connect or read timeout, the remaining files at that host and port are unknown without a request, and other hosts, and the same host on another port, are still probed.
# test_a_redirect_target_that_times_out_is_not_requested_again: through urllib's own redirect processing, the host that timed out after a redirect is the one suppressed, for direct and redirected requests alike, and the redirecting host is still requested.
# test_status_without_probe_counts_probeable_files_and_sends_nothing: without --probe-upstream no request is made; only the probeable count is reported.
# test_a_source_without_validators_is_reported_once_as_not_checkable: without the probe, a source whose latest files record an HTTP URL with no ETag or Last-Modified is named once under not_checkable, however many files or acquisitions; a source with validators, or with no URL, is not.
# test_unreadable_provenance_is_an_uncertainty_and_leaves_the_count_unknown: a missing, unparseable, or malformed provenance.json, including any upstream field land() refuses (by land()'s own check: an invalid, hostless, bad-port, or credential-bearing URL among them) and a repeated file path, is named under uncertainties with or without the probe and makes probeable_files null, nothing is requested for it, the readable acquisitions are still probed, and partial acquisitions and stray files are skipped.
# test_provenance_without_upstream_keys_counts_as_without_upstream: a file entry with no upstream key, or an upstream with no field set ({} or all null, which land() records as null), is valid and counts as without upstream.
# test_unreadable_acquisition_inventory_is_unknown_not_zero: an unreadable data/raw or source directory is an uncertainty and makes probeable_files null, never zero.
# test_probe_follows_redirects_only_to_http_and_only_as_head: through urllib's own redirect processing, a redirect to ftp or file is refused before any FTP or file access, a redirect loop, a redirect without a Location, and a redirect to an invalid port are unknown with a reason naming why, and an https redirect is followed as HEAD.
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
    text = state.read_text().replace("| --- | --- | --- | --- | --- |", "| --- | --- | --- | --- | --- |\n| Renewal lag | evidence.json | revalidation-needed (was supported) | association | Q-004 correction |\n| Pricing | evidence.json | supported | causal (experiment: randomized price test) | |")
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
    assert result["sources"] == {"count": 0, "documentation_without_reference": [], "documentation_access_notes": []}
    assert result["packages"] == []
    assert result["uncertainties"] == []
    assert before == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in workbench.rglob("*") if p.is_file()}


@pytest.mark.parametrize("claim", ["", "strong", "causal", "causal (survey)", "causal (experiment:  )", "Association"])
def test_absent_or_unrecognized_claim_strength_fails_the_status_check(workbench, claim):
    path = workbench / "investigations/churn/state.md"
    path.write_text(path.read_text().replace("| supported | causal (experiment: randomized price test) |",
                                             f"| supported | {claim} |"))
    result = status.collect(workbench)
    assert result["uncertainties"] == [{"path": "investigations/churn/state.md",
                                        "reason": "Missing or unrecognized finding claim strength; interpret manually"}]
    assert {"finding": "Pricing", "status": "supported", "claim": claim, "reason": ""} in result["active"]["findings"]


def test_table_without_claim_column_is_unsupported(workbench):
    path = workbench / "investigations/churn/state.md"
    text = path.read_text().replace("| Status | Claim |", "| Status |").replace("| --- | --- | --- | --- | --- |", "| --- | --- | --- | --- |")
    path.write_text(text.replace("| association |", "|").replace("| causal (experiment: randomized price test) |", "|"))
    result = status.collect(workbench)
    assert result["active"]["counts"] is None
    assert {"path": "investigations/churn/state.md", "reason": "Unsupported or missing table: Finding, Evidence, Status, "
            "Claim, Revalidation reason or caveat"} in result["uncertainties"]


def test_missing_and_custom_tables_are_unknown_not_zero(workbench):
    (workbench / "investigations/churn/state.md").write_text("Updated: today\nFindings: none")
    (workbench / "foundation/sources.md").unlink()
    result = status.collect(workbench)
    assert result["active"]["counts"] is None
    assert result["acquisitions"] is None and result["sources"] is None
    assert {u["path"] for u in result["uncertainties"]} == {"investigations/churn/state.md", "foundation/sources.md"}


def test_malformed_table_does_not_count_partial_rows(workbench):
    with (workbench / "investigations/churn/state.md").open("a") as stream:
        stream.write("\n")
    path = workbench / "investigations/churn/state.md"
    path.write_text(path.read_text().replace("| Pricing | evidence.json | supported | causal (experiment: randomized price test) | |", "| Pricing | too few |"))
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


def test_a_preview_only_draft_reports_the_preview_not_a_missing_manifest(workbench):
    draft = package(workbench, "none")
    for path in list(draft.iterdir()):
        shutil.rmtree(path) if path.is_dir() else path.unlink()
    write(workbench, "deliveries/churn/review/draft/.preview/headlines.md", "# Churn\n\n- West churn is highest\n")
    result = status.collect(workbench)
    entry = result["packages"][0]
    assert entry["draft_stage"] == "headline preview written, not yet exported" and entry["revised_at"] is None
    assert result["uncertainties"] == []
    # Once export writes the manifest the draft is past the preview, and a missing manifest is uncertain again.
    (draft / ".preview/headlines.md").unlink()
    result = status.collect(workbench)
    assert result["packages"][0]["draft_stage"] is None
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


def test_git_no_commits_dated_state_and_no_index_writes(workbench):
    git(workbench, "init")
    file = write(workbench, "investigations/churn/query.sql", "select 1")
    epoch = __import__("datetime").datetime(2026, 10, 1, 12).timestamp()
    os.utime(file, (epoch, epoch))
    # Align all active files so their default fixture mtimes do not obscure the scenario.
    set_mtimes(workbench, epoch)
    git(workbench, "add", ".")
    index = workbench / ".git/index"
    before = (index.read_bytes(), index.stat().st_mtime_ns)
    result = status.collect(workbench)["git"]
    assert result["has_commits"] is False
    assert result["commit_comparison"] == "no commits yet; all work uncommitted"
    # A Last updated date without a time cannot be ordered against a change on its day: said in plain words.
    assert result["state_status"] == "saved the same day as the latest change"
    assert "days_after_state" not in result
    assert before == (index.read_bytes(), index.stat().st_mtime_ns)
    os.utime(file, (epoch + 2 * 86400, epoch + 2 * 86400))
    result = status.collect(workbench)["git"]
    assert result["state_status"] == "out of date"
    assert result["days_after_state"] == 2


def test_results_recorded_before_the_first_commit_are_listed_for_a_rerun(workbench):
    git(workbench, "init")
    evidence = workbench / "investigations/churn/evidence"
    write(workbench, "investigations/churn/evidence/early.json", json.dumps({"producing_commit": "uncommitted"}))
    assert "uncommitted_evidence" not in status.collect(workbench)["git"]  # no commit yet: nothing to rerun for
    git(workbench, "add", ".")
    git(workbench, "-c", "user.name=Test", "-c", "user.email=test@example.test", "commit", "-qm", "first")
    head = git(workbench, "rev-parse", "HEAD").stdout.strip()
    write(workbench, "investigations/churn/evidence/late.json", json.dumps({"producing_commit": head}))
    write(workbench, "investigations/churn/evidence/no-git.json",
          json.dumps({"producing_commit": {"unknown": "not a git repository"}}))
    write(workbench, "investigations/churn/evidence/broken.json", "{not json")
    write(workbench, "investigations/churn/evidence/notes.txt", "not evidence")
    result = status.collect(workbench)
    assert result["git"]["uncommitted_evidence"] == ["broken", "early", "no-git"]
    assert {"path": "investigations/churn/evidence/broken.json",
            "reason": "Cannot read result evidence; its producing commit is unknown"} in result["uncertainties"]
    for path in evidence.iterdir():
        path.unlink()
    evidence.rmdir()
    assert status.collect(workbench)["git"]["uncommitted_evidence"] == []


def test_ledger_writes_leave_the_state_current(workbench):
    datetime = __import__("datetime").datetime
    saved = datetime(2026, 10, 1, 11, 30).astimezone()
    stamp_state(workbench, saved)
    set_mtimes(workbench, saved.timestamp() - 1800)
    git(workbench, "init")
    day = lambda d: {**os.environ, "GIT_AUTHOR_DATE": f"2026-10-{d:02}T12:00:00", "GIT_COMMITTER_DATE": f"2026-10-{d:02}T12:00:00"}
    commit = lambda d: git(workbench, "-c", "user.name=Test", "-c", "user.email=test@example.test", "commit", "-qm", "work", env=day(d))
    git(workbench, "add", ".")
    commit(1)
    assert status.collect(workbench)["git"]["state_status"] == "up to date"
    later = datetime(2026, 10, 5, 11).timestamp()
    for name in ("questions.json", "questions.md"):
        os.utime(write(workbench, f"investigations/churn/{name}", "ledger\n"), (later, later))
    assert status.collect(workbench)["git"]["state_status"] == "up to date"
    git(workbench, "add", ".")
    commit(5)
    assert status.collect(workbench)["git"]["state_status"] == "up to date"
    os.utime(write(workbench, "investigations/churn/brief.md", "changed\n"), (later, later))
    result = status.collect(workbench)["git"]
    assert (result["state_status"], result["days_after_state"]) == ("out of date", 4)


def test_commit_out_of_date_state_and_undated_deletion(workbench):
    git(workbench, "init")
    # Files written the day after the dated state, then committed.
    epoch = __import__("datetime").datetime(2026, 10, 2, 11).timestamp()
    set_mtimes(workbench, epoch)
    git(workbench, "add", ".")
    env = {**os.environ, "GIT_AUTHOR_DATE": "2026-10-02T12:00:00", "GIT_COMMITTER_DATE": "2026-10-02T12:00:00"}
    git(workbench, "-c", "user.name=Test", "-c", "user.email=test@example.test", "commit", "-m", "fixture", env=env)
    result = status.collect(workbench)["git"]
    assert result["state_status"] == "out of date"
    assert result["days_after_state"] == 1
    (workbench / "investigations/churn/brief.md").unlink()
    result = status.collect(workbench)
    assert result["git"]["undated_changes"] == ["investigations/churn/brief.md"]
    assert any("mtime" in u["reason"] for u in result["uncertainties"])


def stamp_state(workbench, when):
    """Write a state time, as state writers record it, into the fixture's Last updated line."""
    path = workbench / "investigations/churn/state.md"
    path.write_text(path.read_text().replace("Last updated: 2026-10-01", f"Last updated: {when.isoformat(timespec='seconds')}"))


def set_mtimes(workbench, epoch):
    for path in (workbench / "investigations/churn").rglob("*"):
        os.utime(path, (epoch, epoch))


def test_a_state_written_after_the_latest_change_on_the_same_day_is_up_to_date(workbench):
    datetime = __import__("datetime").datetime
    saved = datetime(2026, 10, 1, 15).astimezone()
    stamp_state(workbench, saved)
    git(workbench, "init")
    file = write(workbench, "investigations/churn/query.sql", "select 1")
    set_mtimes(workbench, saved.timestamp() - 3600)
    result = status.collect(workbench)["git"]
    assert result["state_status"] == "up to date" and "days_after_state" not in result
    assert result["latest_change"]["source"] in {"investigations/churn/query.sql", "investigations/churn/brief.md"}
    # A change within the state's own second is not after it: records written with the state share it.
    os.utime(file, (saved.timestamp() + 0.5, saved.timestamp() + 0.5))
    assert status.collect(workbench)["git"]["state_status"] == "up to date"
    os.utime(file, (saved.timestamp() + 1, saved.timestamp() + 1))
    result = status.collect(workbench)["git"]
    assert (result["state_status"], result["days_after_state"]) == ("out of date", 0)
    assert result["latest_change"] == {"date": "2026-10-01", "time": datetime.fromtimestamp(saved.timestamp() + 1)
                                       .astimezone().isoformat(timespec="seconds"), "source": "investigations/churn/query.sql"}
    # The state's own Last updated, written with Z or an offset, is read as an instant.
    utc = saved.astimezone(__import__("datetime").timezone.utc)
    path = workbench / "investigations/churn/state.md"
    path.write_text(path.read_text().replace(saved.isoformat(timespec="seconds"), utc.strftime("%Y-%m-%dT%H:%M:%SZ")))
    assert status.collect(workbench)["git"]["state_status"] == "out of date"
    os.utime(file, (saved.timestamp() - 1, saved.timestamp() - 1))
    assert status.collect(workbench)["git"]["state_status"] == "up to date"


@pytest.mark.parametrize("value", ["2026-10-01T15:00:00", "2026-10-01 15:00:00+00:00", "2026-10-01T15:00:00.5+00:00",
                                   "2026-10-01T25:00:00+00:00", "yesterday"])
def test_a_state_time_without_its_offset_or_malformed_is_uncertain(workbench, value):
    path = workbench / "investigations/churn/state.md"
    path.write_text(path.read_text().replace("Last updated: 2026-10-01", f"Last updated: {value}"))
    git(workbench, "init")
    result = status.collect(workbench)
    assert result["git"]["state_status"] == "unknown"
    assert {"path": "investigations/churn/state.md",
            "reason": "Last updated is not an ISO date, or a time with its UTC offset"} in result["uncertainties"]


def test_committed_changes_are_ordered_by_their_own_times(workbench):
    datetime = __import__("datetime").datetime
    saved = datetime(2026, 10, 1, 15).astimezone()
    stamp_state(workbench, saved)
    git(workbench, "init")
    note = write(workbench, "investigations/churn/notes.md", "note\n")
    set_mtimes(workbench, saved.timestamp() - 3600)

    def commit(epoch):
        when = datetime.fromtimestamp(epoch).astimezone().isoformat()
        git(workbench, "add", "-A")
        git(workbench, "-c", "user.name=Test", "-c", "user.email=test@example.test", "commit", "-qm", "work",
            env={**os.environ, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when})

    # Committing after the state is the usual order: the commit is later, the changes it records are not.
    commit(saved.timestamp() + 60)
    result = status.collect(workbench)["git"]
    assert result["uncommitted_paths"] == 0 and result["state_status"] == "up to date"
    # A checkout rewrites a file after its commit, so only the commit's time is known, an upper bound.
    os.utime(note, (saved.timestamp() + 600, saved.timestamp() + 600))
    result = status.collect(workbench)["git"]
    assert result["state_status"] == "saved before a later commit, which does not record when its changes were made"
    assert result["latest_change"]["source"] == "investigations/churn/notes.md"
    # A file changed after the state and committed later is out of date by its own time.
    write(workbench, "investigations/churn/notes.md", "edited\n")
    os.utime(note, (saved.timestamp() + 30, saved.timestamp() + 30))
    commit(saved.timestamp() + 90)
    result = status.collect(workbench)["git"]
    assert (result["state_status"], result["latest_change"]["source"]) == ("out of date", "investigations/churn/notes.md")
    # A deleted file has only its commit's time; one committed before the state is not after it.
    note.unlink()
    commit(saved.timestamp() + 120)
    assert status.collect(workbench)["git"]["state_status"].startswith("saved before a later commit")
    stamp = (workbench / "investigations/churn/state.md")
    stamp.write_text(stamp.read_text().replace(saved.isoformat(timespec="seconds"),
                                               datetime.fromtimestamp(saved.timestamp() + 300).astimezone().isoformat(timespec="seconds")))
    os.utime(workbench / "investigations/churn/brief.md", (saved.timestamp() + 900, saved.timestamp() + 900))
    commit(saved.timestamp() + 200)
    assert status.collect(workbench)["git"]["state_status"] == "up to date"


def test_a_committed_path_git_quotes_is_dated_only_by_its_commit(workbench):
    datetime = __import__("datetime").datetime
    saved = datetime(2026, 10, 1, 15).astimezone()
    stamp_state(workbench, saved)
    git(workbench, "init")
    write(workbench, 'investigations/churn/a"b.sql', "select 1")
    set_mtimes(workbench, saved.timestamp() - 3600)
    when = datetime.fromtimestamp(saved.timestamp() + 60).astimezone().isoformat()
    git(workbench, "add", "-A")
    git(workbench, "-c", "user.name=Test", "-c", "user.email=test@example.test", "commit", "-qm", "work",
        env={**os.environ, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when})
    # Its own mtime would place it before the state, but the quoted name is never read back, so the order is unknown.
    result = status.collect(workbench)["git"]
    assert result["state_status"] == "saved before a later commit, which does not record when its changes were made"
    assert result["latest_change"]["source"].startswith('"')


def test_acquisitions_and_storage_risks(workbench):
    path = workbench / "foundation/sources.md"
    path.write_text(path.read_text() + "\n| a1 | s1 | today | request | data/raw/a | this checkout only | check | | |\n| a2 | s1 | today | request | data/raw/b | | check | | |\n")
    result = status.collect(workbench)
    assert result["acquisitions"] == {"count": 2, "without_retained_copy": 2}
    assert result["landed_data_storage"] == {"location": "none chosen", "availability": "none chosen"}
    assert result["release_storage"]["availability"] == "unrecorded"


SHA = "ab12" * 16
# Notes probes for the two reference forms foundation/sources.md defines: (source ID, Notes, whether
# it counts as a reference, where the probe came from). Every reviewer probe from PR 38 rounds 1-7
# is a row, in both directions; rows marked "limit" pin Markdown that renders as a reference but is
# outside the grammar foundation/sources.md states, or what a syntax-only check cannot tell apart.
REFERENCE_PROBES = [
    # The link form.
    ("link", "reference: [dictionary](references/link/dictionary.pdf)", True, "template example"),
    ("link-after-period", "Owner confirmed. Reference: [codebook](references/link-after-period/codebook.pdf)", True, "worker r1"),
    ("link-after-br", "Owner confirmed<br>reference: [codebook](references/link-after-br/codebook.pdf)", True, "Opus r2 #2 (p6)"),
    ("link-after-br-slash", "Owner confirmed<br/>reference: [codebook](references/link-after-br-slash/codebook.pdf)", True, "worker r3"),
    ("link-parens", "reference: [codebook](references/link-parens/manual(v1).pdf)", True, "worker r3"),
    ("link-parens-2", "reference: [manual](references/link-parens-2/manual(v1(2026)).pdf)", True, "Codex r4 #1"),
    ("link-parens-3", "reference: [manual](references/link-parens-3/manual(v1(2026(a))).pdf)", True, "worker r4"),
    ("link-parens-escaped", "reference: [manual](references/link-parens-escaped/manual\\(v1.pdf)", False, "worker r4; limit: a bare destination has no \\"),
    ("link-escaped-backslash", "reference: [manual](references/link-escaped-backslash/manual(v1\\\\).pdf)", False, "worker r4; limit: a bare destination has no \\"),
    ("link-lt-in-bare", "reference: [dd](references/link-lt-in-bare/a<b.pdf)", False, "Opus r5 #1; limit: a bare destination has no <"),
    ("link-text-brackets", "reference: [HR dictionary [2024]](references/link-text-brackets/dd.pdf)", False, "Opus r5 #1; limit: link text has no brackets"),
    ("link-text-escaped", "reference: [dd \\[v2\\]](references/link-text-escaped/dd.pdf)", False, "Opus r5 #1; limit: link text has no brackets or \\"),
    ("link-angle-escaped-end", "reference: [manual](<references/link-angle-escaped-end/manual.pdf\\>)", False, "Codex r5 #1"),
    ("link-angle-escaped", "reference: [manual](<references/link-angle-escaped/manual\\>v1.pdf>)", False, "Codex r5 #1; limit: an angle destination has no \\"),
    ("link-angle", "reference: [codebook](<references/link-angle/data dictionary.pdf>)", True, "template example"),
    ("link-angle-parens-2", "reference: [manual](<references/link-angle-parens-2/manual(v1(2026)).pdf>)", True, "Codex r4 #1"),
    ("link-unclosed", "reference: [codebook](references/link-unclosed/codebook.pdf", False, "Codex r2 #1"),
    ("link-unclosed-parens", "reference: [codebook](references/link-unclosed-parens/manual(v1).pdf", False, "Codex r3 #1"),
    ("link-unclosed-parens-2", "reference: [manual](references/link-unclosed-parens-2/manual(v1(2026).pdf)", False, "worker r4"),
    ("link-unclosed-parens-3", "reference: [manual](references/link-unclosed-parens-3/manual(v1(2026(a)).pdf)", False, "worker r4"),
    ("link-extra-open", "reference: [manual](references/link-extra-open/manual((v1).pdf)", False, "worker r4"),
    ("link-extra-close", "reference: [manual](references/link-extra-close/manual(v1)).pdf)", True, "limit: CommonMark ends the destination at the first unmatched )"),
    ("link-unclosed-angle", "reference: [codebook](<references/link-unclosed-angle/manual.pdf)", False, "Codex r3 #1"),
    ("link-spaced-bare", "reference: [codebook](references/link-spaced-bare/data dictionary.pdf)", False, "worker r3"),
    ("link-in-code", "reference: `[codebook](references/link-in-code/codebook.pdf)`", False, "worker r3"),
    ("link-titled", 'reference: [codebook](references/link-titled/codebook.pdf "Codebook")', False, "limit: link titles are not read"),
    ("link-placeholder", "reference: [none](none)", True, "limit: syntax only"),
    ("link-empty-text", "reference: [](references/link-empty-text/manual.pdf)", False, "Opus r6 #1; limit: link text is not empty"),
    # What the label sits in: a clause counts only in plain text, outside code, HTML, emphasis,
    # strikethrough, links and brackets.
    ("code-span-after", "Owner `HR`; reference: [codebook](references/code-span-after/codebook.pdf)", True, "worker r5"),
    ("code-span-label", "No reference kept. Attempted note: `status pending; reference: [manual](references/code-span-label/manual.pdf)`", False, "Codex r5 #2"),
    ("code-span-double", "``draft; reference: [manual](references/code-span-double/manual.pdf)``", False, "worker r5"),
    ("code-span-escaped", "\\`draft; reference: [manual](references/code-span-escaped/manual.pdf)", True, "worker r5: an escaped backtick opens no code span"),
    ("code-span-after-escape", "\\`a` b; reference: [manual](references/code-span-after-escape/manual.pdf)`", False, "worker r5"),
    ("html-attribute", "<span title='draft; reference: [manual](references/html-attribute/manual.pdf)'>x</span>", False, "worker r5"),
    ("html-comment", "<!-- draft; reference: [manual](references/html-comment/manual.pdf) -->", False, "worker r5"),
    ("html-code", "<code>draft; reference: [manual](references/html-code/manual.pdf)</code>", False, "Codex r6 #1"),
    ("html-hidden", "<span hidden>draft; reference: [manual](references/html-hidden/manual.pdf)</span>", False, "Codex r6 #1"),
    ("html-del", "<del>old; reference: [manual](references/html-del/manual.pdf)</del>", False, "Opus r6 closure"),
    ("html-before", "<b>Owner</b>; reference: [manual](references/html-before/manual.pdf)", False, "worker r6; limit: reading stops at raw HTML other than <br>"),
    ("strikethrough", "~~old note; reference: [manual](references/strikethrough/manual.pdf)~~", False, "Opus r6 #3"),
    ("emphasis", "*draft; reference: [manual](references/emphasis/manual.pdf)*", False, "Opus r6 #3"),
    ("emphasis-underscore", "_draft; reference: [manual](references/emphasis-underscore/manual.pdf)_", False, "worker r6"),
    ("emphasis-before", "**Owner**: HR; reference: [manual](references/emphasis-before/manual.pdf)", True, "worker r6"),
    ("emphasis-unclosed", "*draft; reference: [manual](references/emphasis-unclosed/manual.pdf)", True, "worker r6: an unclosed * is literal"),
    ("emphasis-after", "reference: [manual](references/emphasis-after/manual.pdf); *draft*", True, "worker r6"),
    ("emphasis-around", "**Owner**; reference: [manual](references/emphasis-around/manual.pdf). **Checked**", False, "worker r6; limit: reading stops at emphasis that may hold a bracket"),
    ("emphasis-escaped-closer", "*_draft\\*; reference: [manual](references/emphasis-escaped-closer/manual.pdf)_", False, "Codex r7 #1: an escaped * closes nothing"),
    ("emphasis-nested-opener", "_~~__; reference: [manual](references/emphasis-nested-opener/manual.pdf)~~", False, "worker r7 (Codex r7 #1 fix): the ~~ inside the skipped _ span closes after the clause"),
    ("emphasis-nested-before", "**Owner _HR_**; reference: [manual](references/emphasis-nested-before/manual.pdf)", False, "worker r7; limit: reading stops at emphasis holding another opening delimiter"),
    ("emphasis-intraword-before", "**Owner**: HR_name; reference: [manual](references/emphasis-intraword-before/manual.pdf)", True, "worker r7"),
    ("underscore-intraword", "Owner hr_team; reference: [manual](references/hr_data/underscore-intraword.pdf)", True, "worker r6: an intraword _ opens no emphasis"),
    ("autolink-before", "Owner <https://example.org/hr>; reference: [manual](references/autolink-before/manual.pdf)", True, "worker r5"),
    ("entity-before", "AT&amp;T; reference: [manual](references/entity-before/manual.pdf)", True, "worker r5"),
    ("image-alt", "![scan; reference: [manual](references/image-alt/manual.pdf)](scan.png)", False, "worker r5"),
    ("in-destination", "[draft](notes;reference:[manual](references/in-destination/manual.pdf))", False, "worker r5"),
    ("in-brackets", "[draft; reference: [manual](references/in-brackets/manual.pdf)]", False, "worker r5; limit: a clause inside brackets is not read"),
    ("after-titled-link", '[owner](https://example.org "HR"); reference: [manual](references/after-titled-link/manual.pdf)', False, "worker r5; limit: a clause after a link outside form 1 is not read"),
    ("after-other-link", "[owner [HR]](https://example.org/hr); reference: [manual](references/after-other-link/manual.pdf)", True, "worker r5"),
    # The retained-location form.
    ("kept", f"reference: `/secure/kept/manual.pdf`, sha256 {SHA}", True, "template example"),
    ("kept-spaced", f"reference: `OneDrive - Contoso/Docs/kept-spaced/manual.pdf`, sha256 {SHA}", True, "Opus r3 #1"),
    ("kept-spelled", f"reference: `/secure/kept-spelled/manual.pdf`, SHA-256 {SHA}", True, "Opus r2 #2 (p4)"),
    ("kept-digest", f"reference: `/secure/kept-digest/manual.pdf`, sha256:{SHA}", True, "Opus r2 #2 (p5)"),
    ("kept-bare", f"reference: /secure/kept-bare/manual.pdf, sha256 {SHA}", False, "Opus r2 closure, Opus r3 #1 (the old template example)"),
    ("kept-spaced-bare", f"reference: OneDrive - Contoso/Docs/kept-spaced-bare/manual.pdf, sha256 {SHA}", False, "Opus r3 #1"),
    ("kept-none", f"reference: none, sha256 {SHA}", False, "Codex r3 #2"),
    ("kept-pending", f"reference: pending, sha256 {SHA}", False, "Codex r3 #2"),
    ("kept-none-kept", f"reference: none kept, sha256 {SHA}", False, "Opus r3 closure"),
    ("kept-short", "reference: `/secure/kept-short/manual.pdf`, sha256 ab12", False, "worker r1"),
    ("kept-long", f"reference: `/secure/kept-long/manual.pdf`, sha256 {SHA}a", False, "worker r3"),
    ("kept-letter", f"reference: `/secure/kept-letter/manual.pdf`, sha256 {SHA}g", False, "Codex r6 #2, Opus r6 #2"),
    ("kept-suffix", f"reference: `/secure/kept-suffix/manual.pdf`, sha256 {SHA}xyz123", False, "Codex r6 #2"),
    ("kept-underscore", f"reference: `/secure/kept-underscore/manual.pdf`, sha256 {SHA}_v2", False, "worker r6"),
    ("kept-unicode-letter", f"reference: `/secure/kept-unicode-letter/manual.pdf`, sha256 {SHA}\u00e9", False, "Codex r7 #2"),
    ("kept-fullwidth-digit", f"reference: `/secure/kept-fullwidth-digit/manual.pdf`, sha256 {SHA}\uff19", False, "Codex r7 #2"),
    ("kept-arabic-digit", f"reference: `/secure/kept-arabic-digit/manual.pdf`, sha256 {SHA}\u0663", False, "Opus r7 #1"),
    ("kept-then-text", f"reference: `/secure/kept-then-text/manual.pdf`, sha256 {SHA}. Verified", True, "worker r6"),
    ("kept-escape-after", f"reference: `/secure/kept-escape-after/manual.pdf`, sha256 {SHA}\\_v2", False, "worker r6 (renders an attached _)"),
    ("kept-entity-after", f"reference: `/secure/kept-entity-after/manual.pdf`, sha256 {SHA}&#x67;", False, "worker r6 (renders an attached g)"),
    ("kept-no-sum", "reference: `/secure/kept-no-sum/manual.pdf`", False, "worker r3"),
    ("kept-no-comma", f"reference: `/secure/kept-no-comma/manual.pdf` sha256 {SHA}", False, "worker r3"),
    ("kept-placeholder", f"reference: `none`, sha256 {SHA}", True, "limit: syntax only"),
    # Placeholders, labels, and what follows them.
    ("blank", "reference:", False, "Codex r1 #1"),
    ("pending", "reference: not yet retained", False, "Codex r1 #1"),
    ("negated", "no reference: vendor publishes none", False, "Opus r1 #3"),
    ("unlabelled", f"kept at /secure/unlabelled/manual.pdf, sha256 {SHA}", False, "Opus r1 #1"),
    ("later-thread", "reference: pending. Owner notes in [thread](https://chat.example/t/1)", False, "Opus r2 #1 (p1)"),
    ("later-link", "reference: not yet retained. Owner: [HR](https://example.org/hr)", False, "Codex r2 #1"),
    ("later-comma", "reference: not yet retained, see [request](https://tickets.example/42)", False, "Opus r2 #1 (p2)"),
    ("later-sum", f"reference: none kept. Landing checked against /data/raw/later-sum, sha256 {SHA}", False, "Opus r2 #1 (p3)"),
    ("label-backticked", "`reference:` [schema](references/label-backticked/schema.json)", False, "worker r1, now outside the forms"),
    ("label-bold", "**reference:** [schema](references/label-bold/schema.json)", False, "Opus r3 verified"),
    ("label-prefixed", "Docs: reference: [schema](references/label-prefixed/schema.json)", False, "Opus r3 verified"),
]


def test_sources_assessed_from_documentation_need_a_reference(workbench):
    path = workbench / "foundation/sources.md"
    probes = [f"| {source} | X | x | y | z | from documentation: fit | candidate | {notes} |" for source, notes, _, _ in REFERENCE_PROBES]
    rows = "\n".join(probes + [
        "| hr | HRIS | employees, one row each | HR ops | export | From documentation: has tenure | candidate | owner confirmed |",
        "| pay | Payroll | pay lines | Finance | API | `from documentation`; fit | acquired | reference: [dictionary](references/pay/dictionary.pdf) |",
        "| crm | CRM | accounts | Sales | export | from landed records: sparse | rejected | |",
        "| erp | ERP | orders | Finance | export | from landed records: verified field absent from documentation | acquired | |",
        "| new | New | x | y | z | | candidate | |",
        "| loose | Loose | x | y | z | not from documentation; from landed records | candidate | |"])
    path.write_text(path.read_text().replace("| --- | --- | --- | --- | --- | --- | --- | --- |\n", "| --- | --- | --- | --- | --- | --- | --- | --- |\n" + rows + "\n", 1))
    result = status.collect(workbench)
    listed = [entry["source"] for entry in result["sources"]["documentation_without_reference"]]
    assert [(source, source not in listed, origin) for source, _, _, origin in REFERENCE_PROBES] == [(source, counted, origin) for source, _, counted, origin in REFERENCE_PROBES]
    assert listed == [source for source, _, counted, _ in REFERENCE_PROBES if not counted] + ["hr"]
    assert result["sources"]["count"] == len(REFERENCE_PROBES) + 6 and result["sources"]["documentation_access_notes"] == []
    assert all(entry["reason"] for entry in result["sources"]["documentation_without_reference"])
    assert result["acquisitions"] == {"count": 0, "without_retained_copy": 0}
    assert result["uncertainties"] == [{"path": "foundation/sources.md", "reason": "Source loose: Relevance and fitness does not begin with its basis"}]
    path.write_text(path.read_text().replace("| Relevance and fitness |", "| Fitness |", 1))
    result = status.collect(workbench)
    assert result["sources"] is None
    assert [u["path"] for u in result["uncertainties"]] == ["foundation/sources.md"]


def sources_with(root, notes):
    """Write one from-documentation Sources row per (source, notes) pair."""
    path = root / "foundation/sources.md"
    rows = "\n".join(f"| {source} | X | x | y | z | from documentation: fit | candidate | {cell} |" for source, cell in notes)
    path.write_text(path.read_text().replace("| --- | --- | --- | --- | --- | --- | --- | --- |\n", "| --- | --- | --- | --- | --- | --- | --- | --- |\n" + rows + "\n", 1))
    return status.collect(root)["sources"]


def test_an_access_note_is_a_known_limitation_not_a_missing_reference(workbench):
    note = "reference: read at https://example.org/tlc/dictionary.pdf on 2026-10-16, not kept: the server refused downloads (HTTP 403)"
    sources = sources_with(workbench, [
        ("tlc", note),
        ("angled", "Owner TLC; reference: read at <https://example.org/a b.pdf> on 2026-10-16, not kept: HTTP 403"),
        ("angled-url", "reference: Read at <https://example.org/dictionary.pdf> on 2026-10-16, Not kept: HTTP 403"),
        ("revised", note + "; dictionary revised 2024, after the 2019 data"),
        ("both", note + "; reference: [codebook](references/both/codebook.pdf)"),
        ("kept-first", f"reference: [codebook](references/kept-first/codebook.pdf); {note}"),
        ("no-date", "reference: read at https://example.org/d.pdf, not kept: HTTP 403"),
        ("no-reason", "reference: read at https://example.org/d.pdf on 2026-10-16, not kept:"),
        ("no-scheme", "reference: read at example.org/d.pdf on 2026-10-16, not kept: HTTP 403"),
        ("in-code", f"`{note}`"),
        ("unlabelled", "read at https://example.org/d.pdf on 2026-10-16, not kept: HTTP 403"),
    ])
    assert sources["documentation_access_notes"] == ["tlc", "angled-url", "revised"]
    listed = [entry["source"] for entry in sources["documentation_without_reference"]]
    assert listed == ["angled", "no-date", "no-reason", "no-scheme", "in-code", "unlabelled"]


def test_reasons_say_why_a_source_lacks_a_reference(workbench):
    sources = sources_with(workbench, [
        ("none", "owner confirmed"),
        ("pending", "reference: not yet retained"),
        ("negated", "no reference: vendor publishes none"),
        ("html", "<b>Owner</b>; reference: [manual](references/html/manual.pdf)"),
        ("emphasis", "**Owner**; reference: [manual](references/emphasis/manual.pdf). **Checked**"),
    ])
    assert {entry["source"]: entry["reason"] for entry in sources["documentation_without_reference"]} == {
        "none": "Notes hold no reference: clause",
        "pending": "what follows reference: is in none of the forms",
        "negated": "reference: does not open a clause in plain text",
        "html": "reading stopped at raw HTML before a reference in one of the forms",
        "emphasis": "reading stopped at emphasis or strikethrough before a reference in one of the forms",
    }


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
    assert result["latest_change"] == {"date": "2026-10-03", "source": "investigations/churn/query.sql",
                                       "time": __import__("datetime").datetime.fromtimestamp(epoch).astimezone().isoformat()}
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


def test_latest_release_in_storage_reads_the_storage_layout(workbench, tmp_path_factory):
    package(workbench, "none")
    assert status.collect(workbench)["packages"][0]["latest_release_in_storage"] is None  # storage unrecorded
    store = tmp_path_factory.mktemp("store")
    readme = workbench / "README.md"
    readme.write_text(readme.read_text().replace("not yet recorded", f"`{store}`"))
    result = status.collect(workbench)
    assert result["release_storage"]["availability"] == "reachable"
    assert result["packages"][0]["latest_release_in_storage"] is False
    (store / "churn/review/released/002").mkdir(parents=True)  # an earlier layout's copy is not read
    assert status.collect(workbench)["packages"][0]["latest_release_in_storage"] is False
    (store / "churn/review/002").mkdir(parents=True)
    result = status.collect(workbench)
    assert result["packages"][0]["latest_release_in_storage"] is True and result["uncertainties"] == []
    readme.write_text(readme.read_text().replace(str(store), str(store / "gone")))
    result = status.collect(workbench)
    assert result["release_storage"]["availability"] == "unreachable"
    assert result["packages"][0]["latest_release_in_storage"] is None


def test_status_reads_rendered_table_with_json_present(workbench):
    write(workbench, "investigations/churn/findings.json", json.dumps({"schema": "awb-findings/1", "findings": []}))
    before = {p: p.read_bytes() for p in workbench.rglob("*") if p.is_file()}
    result = status.collect(workbench)
    assert result["active"]["counts"] == {"revalidation-needed": 1, "supported": 1}
    assert {"finding": "Renewal lag", "status": "revalidation-needed", "claim": "association",
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
                                            "the recorded Last-Modified is not a date to compare with the server's"),
        "j2-recorded-text-blank-etag.csv": ({"etag": '"abc"', "last_modified": "build 7"},
                                            {"ETag": "", "Last-Modified": date}, "unknown",
                                            "the server's ETag is not a usable validator, and "
                                            "the recorded Last-Modified is not a date to compare with the server's"),
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
                                              (("a.csv", "slow.test:8443"), ("b.csv", "slow.test:8443"),
                                               ("c.csv", "fast.test"), ("d.csv", "slow.test"))})
    server = FakeServer({"https://slow.test:8443/a.csv": error, "https://fast.test/c.csv": {"ETag": '"v1"'},
                         "https://slow.test/d.csv": {"ETag": '"v1"'}})
    serve(monkeypatch, server)
    files = status.collect(workbench, probe_upstream=True)["upstream"]["files"]
    assert [(file["path"], file["result"], file.get("reason")) for file in files] == [
        ("a.csv", "unknown", f"no response from slow.test:8443 within {status.PROBE_TIMEOUT} s"),
        ("b.csv", "unknown", "not requested: an earlier request to slow.test:8443 timed out"),
        ("c.csv", "unchanged", None),
        ("d.csv", "unchanged", None)]
    assert [url for _, url, _ in server.requests] == [
        "https://slow.test:8443/a.csv", "https://fast.test/c.csv", "https://slow.test/d.csv"]


def test_each_spelling_of_a_timed_out_host_is_not_requested_again(workbench, monkeypatch):
    import urllib.error
    land_with_upstream(workbench, "batch-1", {name: {"url": url, "etag": '"v1"'} for name, url in (
        ("a.csv", "https://%73low.test/a"), ("b.csv", "https://SLOW.test/b"), ("c.csv", "https://slow.test:443/c"),
        ("d.csv", "https://bücher.test/d"), ("e.csv", "https://xn--bcher-kva.test/e"))})
    timed_out = urllib.error.URLError(TimeoutError("timed out"))
    server = FakeServer({"https://%73low.test/a": timed_out, "https://xn--bcher-kva.test/d": timed_out})
    serve(monkeypatch, server)
    files = status.collect(workbench, probe_upstream=True)["upstream"]["files"]
    assert [(file["path"], file["reason"]) for file in files] == [
        ("a.csv", f"no response from slow.test:443 within {status.PROBE_TIMEOUT} s"),
        ("b.csv", "not requested: an earlier request to slow.test:443 timed out"),
        ("c.csv", "not requested: an earlier request to slow.test:443 timed out"),
        ("d.csv", f"no response from xn--bcher-kva.test:443 within {status.PROBE_TIMEOUT} s"),
        ("e.csv", "not requested: an earlier request to xn--bcher-kva.test:443 timed out")]
    assert [url for _, url, _ in server.requests] == ["https://%73low.test/a", "https://xn--bcher-kva.test/d"]


def test_a_non_ascii_url_is_requested_percent_encoded(workbench, monkeypatch):
    land_with_upstream(workbench, "batch-1", {
        "a.csv": {"url": "https://example.test/données/a.csv?q=café", "etag": '"v1"'},
        "b.csv": {"url": "https://example.test/x?q=caf%C3%A9", "etag": '"v1"'}})
    server = FakeServer({"https://example.test/donn%C3%A9es/a.csv?q=caf%C3%A9": {"ETag": '"v1"'},
                         "https://example.test/x?q=caf%C3%A9": {"ETag": '"v1"'}})
    serve(monkeypatch, server)
    files = status.collect(workbench, probe_upstream=True)["upstream"]["files"]
    assert [(file["path"], file["result"]) for file in files] == [("a.csv", "unchanged"), ("b.csv", "unchanged")]
    assert [url for _, url, _ in server.requests] == [
        "https://example.test/donn%C3%A9es/a.csv?q=caf%C3%A9", "https://example.test/x?q=caf%C3%A9"]


def test_status_without_probe_counts_probeable_files_and_sends_nothing(workbench, monkeypatch):
    monkeypatch.setattr(status, "head_opener", refuse_network)
    assert status.collect(workbench)["upstream"] == {"probeable_files": 0}
    land_with_upstream(workbench, "batch-1", {"a.csv": {"url": "https://example.test/a", "etag": '"v1"'},
                                              "b.csv": {"url": "s3://bucket/b", "version_id": "1"}})
    assert status.collect(workbench)["upstream"] == {"probeable_files": 1}


def test_a_source_without_validators_is_reported_once_as_not_checkable(workbench, monkeypatch):
    monkeypatch.setattr(status, "head_opener", refuse_network)
    land_with_upstream(workbench, "batch-1", {"a.csv": {"url": "https://archive.example.test/a.zip"},
                                              "b.csv": {"url": "https://archive.example.test/b.zip"}}, source="uci")
    land_with_upstream(workbench, "batch-2", {"c.csv": {"url": "http://archive.example.test/c.zip"}}, source="uci")
    land_with_upstream(workbench, "batch-1", {"d.csv": {"url": "https://example.test/d", "etag": '"v1"'}})
    land_with_upstream(workbench, "batch-1", {"e.csv": {"url": "s3://bucket/e", "version_id": "1"}}, source="lake")
    assert status.collect(workbench)["upstream"] == {"probeable_files": 1, "not_checkable": ["uci"]}


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
          ({"url": "https://example.test/a?user=bob&pass=SECRET", "etag": '"v1"'},
           "upstream url of a.csv carries credential parameters (pass); record it without credentials"),
          ({"url": "https://example.test/a?api_sig=SECRET", "etag": '"v1"'},
           "upstream url of a.csv carries credential parameters (api_sig); record it without credentials"),
          ({"url": "https://", "etag": '"v1"'},
           "upstream url of a.csv is not a valid URL: an http(s) URL needs a host and no space or control character"),
          ({"url": "https://api.test:bad/x", "etag": '"v1"'},
           "upstream url of a.csv is not a valid URL: its port is not a number from 0 to 65535"),
      ]],
    # A repeated path would leave an entry unchecked: the first entry's upstream is never validated.
    *[(json.dumps({"status": "complete", "completed_at": "2026-10-13T08:00:00+00:00",
                   "files": [{"path": "x.csv", "upstream": first},
                             {"path": "x.csv", "upstream": {"url": "https://example.test/x", "etag": '"v1"'}}]}),
       "Malformed acquisition provenance: a file path is repeated")
      for first in ["broken", {"url": "https://example.test/x?api_key=SECRET", "etag": '"v1"'}]],
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


@pytest.mark.parametrize("upstream", ["absent", {}, {"url": None, "etag": None, "last_modified": None, "version_id": None}])
def test_provenance_without_upstream_keys_counts_as_without_upstream(workbench, monkeypatch, upstream):
    entry = {"path": "a.csv", "bytes": 1, "sha256": "0", "records": None}
    if upstream != "absent":
        entry["upstream"] = upstream
    write(workbench, "data/raw/api/old/provenance.json", json.dumps(
        {"status": "complete", "completed_at": "2026-10-13T08:00:00+00:00", "files": [entry]}))
    monkeypatch.setattr(status, "head_opener", refuse_network)
    result = status.collect(workbench)
    assert result["uncertainties"] == [] and result["upstream"] == {"probeable_files": 0}
    server = FakeServer({})
    serve(monkeypatch, server)
    result = status.collect(workbench, probe_upstream=True)
    assert result["upstream"] == {"probeable_files": 0, "files": [], "not_probeable": [], "superseded": 0,
                                  "without_upstream": 1}
    assert server.requests == []


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
        "https://example.test/file": (302, {"Location": "file:///etc/hosts"}),
        "https://example.test/loop": (302, {"Location": "/loop"}),
        "https://example.test/nowhere": (302, {}),
        "https://example.test/badport": (307, {"Location": "https://example.test:bad/x"}),
        "https://example.test/old": (301, {"Location": "https://example.test/new"}),
        "https://example.test/new": (200, {"ETag": '"v1"'}),
    }
    requests, ftp, local = [], [], []

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
    monkeypatch.setattr(urllib.request.FileHandler, "file_open", lambda handler, request: local.append(request.full_url))
    land_with_upstream(workbench, "batch-1", {f"{name}.csv": {"url": f"https://example.test/{name}", "etag": '"v1"'}
                                              for name in ("badport", "file", "ftp", "loop", "nowhere", "old")})
    files = status.collect(workbench, probe_upstream=True)["upstream"]["files"]
    assert [(file["path"], file["result"], file.get("reason")) for file in files] == [
        ("badport.csv", "unknown", "redirected to an invalid URL, not followed"),
        ("file.csv", "unknown", "redirected to a URL other than http(s), not followed"),
        ("ftp.csv", "unknown", "redirected to a URL other than http(s), not followed"),
        ("loop.csv", "unknown", "HTTP 302: redirected in a loop or too many times, not followed"),
        ("nowhere.csv", "unknown", "HTTP 302: not a redirect the probe follows"),
        ("old.csv", "unchanged", None),
    ]
    assert ftp == [] and local == []
    assert requests == [("HEAD", "https://example.test/badport"), ("HEAD", "https://example.test/file"),
                        ("HEAD", "https://example.test/ftp"),
                        *[("HEAD", "https://example.test/loop")] * (urllib.request.HTTPRedirectHandler.max_repeats + 1),
                        ("HEAD", "https://example.test/nowhere"),
                        ("HEAD", "https://example.test/old"), ("HEAD", "https://example.test/new")]


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
        ("a.csv", "unknown", f"no response from slow.test:443 within {status.PROBE_TIMEOUT} s"),
        ("b.csv", "unknown", "not requested: an earlier request to slow.test:443 timed out"),
        ("c.csv", "unknown", "redirected to slow.test:443, not followed: an earlier request to slow.test:443 timed out"),
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


@pytest.mark.parametrize("unsettled", ["revalidation-needed", "revalidation-needed (was supported)",
                                       "revalidation-needed (was provisional)", "revalidation-needed (was superseded)", "superseded"])
def test_question_status_json_derives_recheck_from_any_answer(workbench, unsettled):
    write(workbench, "investigations/churn/state.md", f'''# State
Last updated: 2026-10-01

## Current findings
| Finding | Evidence | Status | Claim | Revalidation reason or caveat |
| --- | --- | --- | --- | --- |
| Regional cut | [r1](evidence/r1.json) | {unsettled} | association | |
| Overall cut | [r2](evidence/r2.json) | supported | association | |
''')
    questions = []
    for qid, answerer, stored, results in [
        ("Q-001", "data", "answered", ["r1", "r2"]),
        ("Q-002", "data", "answered", ["r2"]),
        ("Q-003", "user", "answered", []),
        ("Q-004", "stakeholder", "open", []),
        ("Q-005", "data", "superseded", ["r1"]),
    ]:
        questions.append(dict(id=qid, text="Which regions?", answerer=answerer, status=stored,
                              results=results, kind="context", answer="Confirmed" if answerer == "user" else "",
                              by="user" if answerer == "user" else "", parent="", priority="should",
                              unblocks="", origin="scope", reason="Scope changed" if stored == "superseded" else "",
                              updated="2026-10-01"))
    path = write(workbench, "investigations/churn/questions.json", json.dumps({"schema": "awb-questions/1", "questions": questions}))
    before = path.read_bytes()
    output = status.collect(workbench)["active"]["questions"]
    assert output["counts"] == {"answered (awaiting recheck)": 1, "answered": 2, "open": 1, "superseded": 1}
    assert output["awaiting_recheck"] == [f"Q-001 answered (awaiting recheck) [data, context] Which regions? -> r1 ({unsettled}); r2 (supported)"]
    assert output["open"] == ["Q-004 [stakeholder, context] Which regions?"]
    assert "answered_by_unsettled" not in output
    assert path.read_bytes() == before


@pytest.mark.parametrize("unrecognized", ["flagged", "revalidation-needed (review pending)", "superseded (was supported)", "revalidation-needed (was unknown)"])
def test_recheck_status_refuses_unsupported_finding_status_text(workbench, unrecognized):
    path = workbench / "investigations/churn/state.md"
    path.write_text(path.read_text().replace("evidence.json | revalidation-needed (was supported)",
                                            f"[r1](evidence/r1.json) | {unrecognized}"))
    write(workbench, "investigations/churn/questions.json", json.dumps({"schema": "awb-questions/1", "questions": [
        {"id": "Q-001", "text": "Which regions?", "status": "answered", "answerer": "data", "kind": "analytical",
         "answer": "", "by": "", "results": ["r1"], "parent": "", "priority": "must", "origin": "scope",
         "reason": "", "unblocks": "", "updated": "2026-10-01"}]}))
    result = status.collect(workbench)
    assert result["active"]["questions"]["awaiting_recheck"] == []
    assert any("Unrecognized finding status" in row["reason"] for row in result["uncertainties"])


def test_root_and_must_questions_are_counted_apart_from_the_totals(workbench):
    # Five questions the user asked, as roots, and twelve sub-questions under them: the report
    # leads with the user's five, so they are counted apart from the ledger's totals.
    def question(qid, parent, priority, status):
        person = status == "answered"
        return dict(id=qid, text="Which regions?", answerer="user", status=status, results=[], kind="context",
                    answer="Confirmed" if person else "", by="user" if person else "", parent=parent,
                    priority=priority, unblocks="", origin="scope",
                    reason="Scope changed" if status == "superseded" else "", updated="2026-10-01")
    roots = [question(f"Q-00{n}", "", "must" if n < 4 else "should", "answered") for n in range(1, 6)]
    children = [question(f"Q-0{n}", "Q-001", priority, status) for n, (priority, status) in enumerate([
        ("must", "answered"), ("must", "answered"), ("must", "open"), ("should", "answered"),
        ("should", "answered"), ("should", "open"), ("could", "answered"), ("could", "open"),
        ("should", "answered"), ("should", "superseded"), ("could", "answered"), ("should", "open")], start=10)]
    # A grandchild is a sub-question too.
    children[-1]["parent"] = "Q-010"
    write(workbench, "investigations/churn/questions.json",
          json.dumps({"schema": "awb-questions/1", "questions": roots + children}))
    output = status.collect(workbench)["active"]["questions"]
    assert output["roots"] == {"answered": 5}
    assert output["must_subquestions"] == {"answered": 2, "open": 1}
    assert output["counts"] == {"answered": 12, "open": 4, "superseded": 1}


def test_findings_are_grouped_by_question(workbench):
    # Nine findings beside five questions told the user nothing: each root lists the findings that
    # answer it or any question under it, and the findings no question names are counted apart.
    write(workbench, "investigations/churn/state.md", """# State
Last updated: 2026-10-01

## Current findings
| Finding | Evidence | Status | Claim | Revalidation reason or caveat |
| --- | --- | --- | --- | --- |
| Lag by region | [r1](evidence/r1.json) | supported | association | |
| Lag by plan | [r2](evidence/r2.json) | provisional | association | |
| Seasonal dip | [r3](evidence/r3.json) | revalidation-needed (was supported) | descriptive | DQ-001 correction |
| Both questions | [r4](evidence/r4.json) | supported | descriptive | |
| Side result | [r5](evidence/r5.json) | provisional | descriptive | |
| No evidence link | none | provisional | descriptive | |
""")

    def question(qid, parent, results, origin="scope"):
        return dict(id=qid, text=f"Question {qid}?", answerer="data", status="answered" if results else "open",
                    results=results, kind="analytical", answer="", by="", parent=parent, priority="should",
                    unblocks="", origin=origin, reason="", updated="2026-10-01")

    questions = [question("Q-001", "", ["r1", "r4"]), question("Q-002", "Q-001", ["r2"]),
                 question("Q-003", "Q-002", ["r3"]), question("Q-004", "", ["r4"]),
                 question("Q-005", "", [], origin="eda"), question("Q-006", "Q-404", ["r5"])]
    write(workbench, "investigations/churn/questions.json", json.dumps({"schema": "awb-questions/1", "questions": questions}))
    output = status.collect(workbench)["active"]["questions"]
    assert output["by_question"] == [
        {"id": "Q-001", "text": "Question Q-001?", "status": "answered", "origin": "scope",
         "findings": {"supported": 2, "provisional": 1, "revalidation-needed": 1}},
        {"id": "Q-004", "text": "Question Q-004?", "status": "answered", "origin": "scope", "findings": {"supported": 1}},
        # A root the agent added keeps its origin, so the report can label it.
        {"id": "Q-005", "text": "Question Q-005?", "status": "open", "origin": "eda", "findings": {}}]
    # Under a missing parent, or with no evidence link, a finding answers none of the user's questions.
    assert output["findings_without_question"] == {"provisional": 2}


def test_unreadable_findings_leave_the_counts_by_question_unknown(workbench):
    path = workbench / "investigations/churn/state.md"
    path.write_text(path.read_text().replace("| Pricing | evidence.json | supported | causal (experiment: randomized price test) | |", "| Pricing | too few |"))
    write(workbench, "investigations/churn/questions.json", json.dumps({"schema": "awb-questions/1", "questions": [
        {"id": "Q-001", "text": "Which regions?", "status": "open", "answerer": "data", "kind": "analytical",
         "answer": "", "by": "", "results": [], "parent": "", "priority": "must", "origin": "scope",
         "reason": "", "unblocks": "", "updated": "2026-10-01"}]}))
    active = status.collect(workbench)["active"]
    assert active["questions"]["by_question"][0]["findings"] is None
    assert active["questions"]["findings_without_question"] is None
    assert active["caveats"] is None


def test_every_findings_caveat_is_reported(workbench):
    # A status that listed only flagged findings' caveats said "none open" with caveats on unflagged ones.
    path = workbench / "investigations/churn/state.md"
    path.write_text(path.read_text().replace(
        "| supported | causal (experiment: randomized price test) | |",
        "| supported | causal (experiment: randomized price test) | Excludes December 2011 |\n"
        "| Steady base | [r3](evidence/r3.json) | provisional | descriptive | not assessed: joins |\n"
        "| Plain | [r4](evidence/r4.json) | provisional | descriptive | |"))
    assert status.collect(workbench)["active"]["caveats"] == [
        {"finding": "Renewal lag", "status": "revalidation-needed", "caveat": "Q-004 correction"},
        {"finding": "Pricing", "status": "supported", "caveat": "Excludes December 2011"},
        {"finding": "Steady base", "status": "provisional", "caveat": "not assessed: joins"}]


@pytest.mark.parametrize("field", ["parent", "priority"])
def test_ledger_without_parent_or_priority_is_unreadable(workbench, field):
    entry = {"id": "Q-001", "text": "Which regions?", "status": "open", "answerer": "user", "kind": "context",
             "answer": "", "by": "", "results": [], "parent": "", "priority": "must", "origin": "scope",
             "reason": "", "unblocks": "", "updated": "2026-10-01"}
    del entry[field]
    write(workbench, "investigations/churn/questions.json",
          json.dumps({"schema": "awb-questions/1", "questions": [entry]}))
    result = status.collect(workbench)
    assert result["active"]["questions"] is None
    assert any("Unreadable question ledger" in row["reason"] for row in result["uncertainties"])
