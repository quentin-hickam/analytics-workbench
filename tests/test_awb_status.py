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
# test_sources_assessed_from_documentation_need_a_reference: a source whose Relevance and fitness begins from documentation is listed unless a Notes clause opens with reference: directly followed by one of the two forms foundation/sources.md defines, a link in its stated grammar or a backticked location with its sha256, in plain text outside code, HTML, emphasis, strikethrough, links and brackets; REFERENCE_PROBES holds every reviewer probe in both directions; a landed-records basis mentioning documentation later is not listed; an assessment without a leading basis is an uncertainty; an unsupported Sources table is null with an uncertainty.
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

"""Status observations stay read-only and conservative when records need interpretation."""
import importlib.util
import json
import os
from pathlib import Path
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
    assert result["sources"] == {"count": 0, "documentation_without_reference": []}
    assert result["packages"] == []
    assert result["uncertainties"] == []
    assert before == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in workbench.rglob("*") if p.is_file()}


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
    listed = result["sources"]["documentation_without_reference"]
    assert [(source, source not in listed, origin) for source, _, _, origin in REFERENCE_PROBES] == [(source, counted, origin) for source, _, counted, origin in REFERENCE_PROBES]
    assert result["sources"] == {"count": len(REFERENCE_PROBES) + 6, "documentation_without_reference": [source for source, _, counted, _ in REFERENCE_PROBES if not counted] + ["hr"]}
    assert result["acquisitions"] == {"count": 0, "without_retained_copy": 0}
    assert result["uncertainties"] == [{"path": "foundation/sources.md", "reason": "Source loose: Relevance and fitness does not begin with its basis"}]
    path.write_text(path.read_text().replace("| Relevance and fitness |", "| Fitness |", 1))
    result = status.collect(workbench)
    assert result["sources"] is None
    assert [u["path"] for u in result["uncertainties"]] == ["foundation/sources.md"]


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
