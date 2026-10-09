# Kept cases:
# test_collect_standard_records_without_writes_or_other_conclusions: counts normalize flagged statuses; nothing is written; other investigations give only name and date.
# test_missing_and_custom_tables_are_unknown_not_zero: an unsupported state table or absent sources record is null with an uncertainty, never zero.
# test_malformed_table_does_not_count_partial_rows: one malformed findings row makes the counts unknown.
# test_new_flag_requires_semantic_review_and_never_claims_zero: a flag absent from the manifest goes to representation review with the methodology path.
# test_dispositions_require_current_reason: a disposition applies only while finding and reason match the state row exactly.
# test_revalidate_and_none_places_block_release: a confirmed flag with any `none` or `revalidate` place counts as lacking a disposition; `omit` and `release_with_caveat` do not.
# test_malformed_manifest_requests_targeted_fallback: invalid manifests name the manifest under uncertainties.
# test_custom_manifest_preserves_manual_fallback: a non-JSON manifest leaves dates and disposition counts null.
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
# test_representation_review_uses_methodology_identifiers: representation review points at methodology.md.
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
    write(workbench, draft + "/methodology.md", "Renewal timing is relevant, expressed with a different name.")
    write(workbench, "deliveries/churn/review/released/002/manifest.json", json.dumps({"released_at": "2026-09-29T09:00:00-04:00"}))
    return workbench / draft


def test_new_flag_requires_semantic_review_and_never_claims_zero(workbench):
    package(workbench, "none")
    result = status.collect(workbench)["packages"][0]
    assert result["draft_vs_release"] == "ahead"
    assert result["latest_release"] == "002"
    assert result["representation_review"] == [{"finding": "Renewal lag", "reason": "Q-004 correction"}]
    assert result["flags_since_draft"] == "unknown until representation review"
    assert result["review_methodology"].endswith("draft/methodology.md")


def test_dispositions_require_current_reason(workbench):
    old = {"finding": "Renewal lag", "reason": "older reason", "represented_in": [{"disposition": "release_with_caveat"}]}
    draft = package(workbench, [old])
    result = status.collect(workbench)["packages"][0]
    assert result["representation_review"]
    old["reason"] = "Q-004 correction"
    old["represented_in"].append({"disposition": "none"})
    (draft / "manifest.json").write_text(json.dumps({"revised_at": "2026-10-01T10:00:00-04:00", "revalidation_flags": [old]}))
    result = status.collect(workbench)["packages"][0]
    assert result["confirmed_without_disposition"] == 1
    assert result["representation_review"] == []


@pytest.mark.parametrize("places,blocked", [(["omit", "release_with_caveat"], False), (["release_with_caveat", "revalidate"], True), (["none"], True)])
def test_revalidate_and_none_places_block_release(workbench, places, blocked):
    flag = {"finding": "Renewal lag", "reason": "Q-004 correction", "represented_in": [{"disposition": d} for d in places]}
    package(workbench, [flag])
    result = status.collect(workbench)["packages"][0]
    assert result["confirmed_flags"] == [{"finding": "Renewal lag", "reason": "Q-004 correction", "without_disposition": blocked}]
    assert result["confirmed_without_disposition"] == int(blocked)


@pytest.mark.parametrize("content", ["not json", "[]", '{"revalidation_flags": ["bad"]}', '{"revised_at": "yesterday", "revalidation_flags": "none"}'])
def test_malformed_manifest_requests_targeted_fallback(workbench, content):
    draft = package(workbench, "none")
    (draft / "manifest.json").write_text(content)
    result = status.collect(workbench)
    assert any(u["path"].endswith("draft/manifest.json") for u in result["uncertainties"])
    assert result["packages"][0]["revised_at"] is None or result["packages"][0]["comparison_is_estimate"]


def test_custom_manifest_preserves_manual_fallback(workbench):
    draft = package(workbench, "none")
    (draft / "manifest.json").unlink()
    (draft / "manifest.yaml").write_text("revised_at: 2026-10-01T10:00:00-04:00")
    result = status.collect(workbench)
    assert result["packages"][0]["revised_at"] is None
    assert result["packages"][0]["confirmed_without_disposition"] is None
    assert any("established manifest format" in u["reason"] for u in result["uncertainties"])


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


@pytest.mark.parametrize("unreadable,unknown_field", [("investigations", "other_investigations"), ("deliveries/churn", "packages"), ("deliveries/churn/review/released", "releases"), ("deliveries/churn/review/draft", "manifest")])
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
    elif unknown_field == "releases":
        assert result["packages"][0]["release_inventory_known"] is False
        assert result["packages"][0]["latest_release"] is None
    else:
        assert result["packages"][0]["revised_at"] is None
        assert result["packages"][0]["confirmed_without_disposition"] is None


def test_representation_review_uses_methodology_identifiers(workbench):
    package(workbench, "none")
    result = status.collect(workbench)["packages"][0]
    assert result["review_methodology"].endswith("draft/methodology.md")
    assert "review_journal" not in result


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
