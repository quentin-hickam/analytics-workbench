"""Read-only status facts for standard workbench Markdown records and manifest.json files.

Run with Python 3.10+: collect_status.py [PROJECT_ROOT] [--probe-upstream]. Emits compact JSON;
uncertainties identify records requiring targeted agent interpretation. Only --probe-upstream
touches the network: HEAD requests for the landed files upstream() selects, comparing their recorded
validators, and a redirect is followed only to an http(s) URL and only as another HEAD request.
It writes nothing.
"""

import argparse
from collections import Counter
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
from email.utils import parsedate_to_datetime
import http.client
import urllib.error
import urllib.parse
import urllib.request

DISPOSITIONS = {"none", "revalidate", "omit", "release_with_caveat"}
BLOCKING = {"none", "revalidate"}


PROBE_TIMEOUT = 10
# The fields land() records per file as upstream, each null or a nonblank string (awb_landing.py).
UPSTREAM_FIELDS = ("url", "etag", "last_modified", "version_id")


def collect(root, *, probe_upstream=False):
    root = Path(root).resolve()
    uncertainties = []

    def relative(path):
        return str(path.relative_to(root))

    def uncertain(path, reason):
        item = {"path": relative(path), "reason": reason}
        if item not in uncertainties:
            uncertainties.append(item)

    def read(path):
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            uncertain(path, f"Cannot read record: {type(error).__name__}")
            return None

    def entries(path, *, directories=False):
        try:
            paths = sorted(path.iterdir())
            return [p for p in paths if p.is_dir()] if directories else paths
        except FileNotFoundError:
            return []
        except OSError as error:
            uncertain(path, f"Cannot enumerate directory: {type(error).__name__}")
            return None

    def field(text, label, path, *, optional=False):
        matches = re.findall(rf"^{re.escape(label)}:[ \t]*([^\n]*)$", text or "", re.M)
        if len(matches) == 1 and matches[0].strip():
            return matches[0].strip()
        if optional and len(matches) <= 1:
            return None
        uncertain(path, f"Missing, blank, or repeated {label} field")
        return None

    def section(text, title, path):
        matches = list(re.finditer(rf"^## {re.escape(title)}\s*$", text or "", re.M))
        if len(matches) != 1:
            uncertain(path, f"Missing or repeated {title} section")
            return None
        rest = text[matches[0].end():]
        return re.split(r"^##? ", rest, maxsplit=1, flags=re.M)[0].strip()

    def table(text, columns, path):
        if text is None:
            return None
        lines = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
        rows = [[cell.strip() for cell in re.split(r"(?<!\\)\|", line.strip("|"))] for line in lines]
        if len(rows) < 2 or rows[0] != columns or len(rows[1]) != len(columns) or not all(re.fullmatch(r":?-+:?", c) for c in rows[1]):
            uncertain(path, "Unsupported or missing table: " + ", ".join(columns))
            return None
        if any(len(row) != len(columns) for row in rows[2:]):
            uncertain(path, "Malformed table row: " + columns[0])
            return None
        return [dict(zip(columns, row)) for row in rows[2:]]

    def iso_date(value, path):
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value or ""):
                raise ValueError
            return date.fromisoformat(value)
        except ValueError:
            uncertain(path, "Last updated is not an ISO calendar date")
            return None

    def storage(value):
        cleaned = (value or "").strip().strip("`").strip()
        # A declined location is the user's recorded decision, distinct from a line never recorded.
        if cleaned.lower() in {"none", "none chosen"}:
            return {"location": value, "availability": "none chosen"}
        if not cleaned or cleaned.lower() in {"not yet recorded", "unknown"}:
            return {"location": value, "availability": "unrecorded"}
        # A URI or prose needs its established connector, never a speculative network call.
        if "://" in cleaned or not (cleaned.startswith(("/", "~", "./", "../"))):
            return {"location": value, "availability": "unknown"}
        path = Path(cleaned).expanduser()
        if not path.is_absolute():
            path = root / path
        try:
            availability = "reachable" if path.is_dir() else "unreachable"
        except OSError:
            availability = "unknown"
        return {"location": value, "availability": availability}

    readme_path = root / "README.md"
    readme = read(readme_path)
    workbench = bool(re.search(r"^Active investigation:", readme or "", re.M) or (root / "foundation").is_dir() or (root / "investigations").is_dir())
    result = {"workbench": workbench, "uncertainties": uncertainties}
    if not workbench:
        return result
    slug = field(readme, "Active investigation", readme_path)
    pointer = re.fullmatch(r"\[[^\]]+\]\(([^)]+)\)", slug or "")
    if pointer:
        slug = pointer[1]
    pointer = re.fullmatch(r"(?:\./)?investigations/([A-Za-z0-9][A-Za-z0-9_-]*)/state\.md", (slug or "").strip("`"))
    if pointer:
        slug = pointer[1]
    if slug == "none":
        slug = None
    elif slug and (not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", slug)):
        uncertain(readme_path, "Customized active investigation pointer; resolve manually")
        slug = None
    result["active"] = None
    findings = None
    state_date = None
    if slug:
        investigation = root / "investigations" / slug
        state_path = investigation / "state.md"
        state = read(state_path)
        updated = field(state, "Last updated", state_path)
        state_date = iso_date(updated, state_path)
        findings = table(section(state, "Current findings", state_path), ["Finding", "Evidence", "Status", "Revalidation reason or caveat"], state_path)
        counts = Counter()
        visible_findings = []
        if findings is not None:
            for row in findings:
                status = row["Status"]
                status = "revalidation-needed" if status.startswith("revalidation-needed") else status
                if status not in {"supported", "provisional", "superseded", "revalidation-needed"}:
                    uncertain(state_path, "Unrecognized finding status; interpret manually")
                counts[status] += 1
                visible_findings.append({"finding": row["Finding"], "status": status, "reason": row["Revalidation reason or caveat"]})
        brief_path = investigation / "brief.md"
        brief = read(brief_path)
        result["active"] = {"name": slug, "last_updated": updated, "counts": dict(counts) if findings is not None else None, "findings": visible_findings if findings is not None else None,
                            "question": section(brief, "Business question", brief_path), "material_unknowns": section(brief, "Material unknowns", brief_path),
                            "unresolved_issues": section(state, "Unresolved issues", state_path), "next_steps": section(state, "Next steps", state_path)}
    others = []
    investigations_path = root / "investigations"
    investigation_dirs = entries(investigations_path, directories=True)
    if investigation_dirs is None:
        others = None
    else:
        for directory in investigation_dirs:
            if directory.name == slug:
                continue
            path = directory / "state.md"
            updated = None
            # Stream only the preamble. Never load another investigation's conclusions.
            try:
                with path.open(encoding="utf-8") as stream:
                    for line in stream:
                        if line.startswith("## "):
                            break
                        if line.startswith("Last updated:"):
                            updated = line.split(":", 1)[1].strip()
                            iso_date(updated, path)
                            break
            except (OSError, UnicodeError) as error:
                uncertain(path, f"Cannot read state date: {type(error).__name__}")
            if updated is None:
                uncertain(path, "Last updated absent from state preamble; inspect date only")
            others.append({"name": directory.name, "last_updated": updated})
    result["other_investigations"] = others
    sources_path = root / "foundation/sources.md"
    sources = read(sources_path)
    acquisitions = table(section(sources, "Acquisitions", sources_path), ["Acquisition ID", "Source ID", "Acquired at", "Source version, query, or request", "Landed directory", "Retained copy", "Integrity or completeness check", "Restrictions", "Notes"], sources_path)
    result["acquisitions"] = None if acquisitions is None else {"count": len(acquisitions), "without_retained_copy": sum(not row["Retained copy"] or row["Retained copy"].strip("`").strip().lower() == "this checkout only" for row in acquisitions)}
    result["landed_data_storage"] = storage(field(readme, "Landed data is kept at", readme_path, optional=True))
    result["release_storage"] = storage(field(readme, "Released packages are kept at", readme_path, optional=True))
    result["upstream"] = upstream(root, probe_upstream, uncertain)

    def manifest(directory, *, release=False):
        """Read manifest.json, recording an uncertainty when it is absent, unreadable, or not a JSON object."""
        path = directory / "manifest.json"
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(obj, dict):
                return obj
            raise ValueError
        except FileNotFoundError:
            uncertain(directory, "Release lacks manifest.json" if release else
                      "Draft lacks manifest.json; awb-package rewrites it on the next revision")
        except (OSError, UnicodeError, ValueError) as error:
            uncertain(path, f"Cannot read JSON manifest object: {type(error).__name__}")
        return None

    def timestamp(obj, key, path=None):
        if obj is None:
            return None
        try:
            parsed = datetime.fromisoformat(obj[key].replace("Z", "+00:00"))
            if parsed.utcoffset() is None:
                raise ValueError
            return parsed
        except (KeyError, ValueError, TypeError, AttributeError):
            if path is not None:
                uncertain(path, f"Missing or invalid {key}; requires ISO timestamp with UTC offset")
            return None

    def rerun_since(obj, revised):
        """Represented results whose evidence was recorded after the draft's last revision, or None if unknown."""
        # `results` lists every represented result; a manifest from before it was recorded is unknown.
        checks = obj.get("results") if obj is not None else None
        if revised is None or not isinstance(checks, list):
            return None
        rerun = []
        for check in checks:
            evidence = check.get("evidence") if isinstance(check, dict) else None
            path = (root / evidence).resolve() if isinstance(evidence, str) else None
            if path is None or not path.is_relative_to(root.resolve()):
                return None
            try:
                recorded = timestamp(json.loads(path.read_text(encoding="utf-8")), "recorded_at")
            except (OSError, UnicodeError, ValueError):
                uncertain(path, "Cannot read result evidence; reruns since the draft unknown")
                return None
            if recorded is None:
                return None
            if recorded > revised:
                rerun.append(check.get("result_id"))
        return rerun

    def valid_flag(flag):
        if not (isinstance(flag, dict) and isinstance(flag.get("finding"), str) and isinstance(flag.get("reason"), str)):
            return False
        places = flag.get("represented_in")
        if places == "none":  # Represented nowhere: no disposition is needed.
            return flag.get("disposition", "none") in DISPOSITIONS
        return isinstance(places, list) and bool(places) and all(isinstance(p, str) and p.strip() for p in places) and flag.get("disposition") in DISPOSITIONS

    flagged = [row for row in findings or [] if row["Status"].startswith("revalidation-needed")]
    packages = []
    deliveries = root / "deliveries" / slug if slug else None
    package_dirs = entries(deliveries, directories=True) if deliveries else []
    if package_dirs is None:
        packages = None
    else:
        for directory in package_dirs:
            draft = directory / "draft"
            obj = manifest(draft) if draft.is_dir() else None
            revised = timestamp(obj, "revised_at", draft / "manifest.json")
            release_dirs = entries(directory / "released", directories=True)
            releases = [p for p in release_dirs or [] if p.name.isascii() and p.name.isdigit()]
            latest = max(releases, key=lambda p: int(p.name)) if releases else None
            # A frozen release is read only for released_at.
            released = timestamp(manifest(latest, release=True), "released_at", latest / "manifest.json") if latest else None
            entry = {"name": directory.name, "draft_exists": draft.is_dir(), "revised_at": revised.isoformat() if revised else None,
                     "release_inventory_known": release_dirs is not None, "latest_release": latest.name if latest else None, "released_at": released.isoformat() if released else None,
                     "draft_vs_release": ("ahead" if revised > released else "same_or_older") if revised and released else None}
            # A result rerun after the draft's last revision leaves the package showing its earlier run.
            entry["rerun_since_draft"] = rerun_since(obj, revised) if draft.is_dir() else None
            flags = obj.get("revalidation_flags") if obj is not None else None
            flags = [] if flags == "none" else flags
            valid_flags = isinstance(flags, list) and all(valid_flag(f) for f in flags)
            if obj is not None and not valid_flags:
                uncertain(draft / "manifest.json", "Missing or malformed revalidation_flags; disposition counts unknown")
            if findings is None and draft.is_dir():
                uncertain(draft, "Current findings unknown; flag comparison requires state review")
            confirmed = []
            for finding in flagged:
                matches = [f for f in flags if f["finding"] == finding["Finding"] and f["reason"] == finding["Revalidation reason or caveat"]] if valid_flags else []
                if matches:
                    # `none` and `revalidate` block a release; a flag represented nowhere blocks nothing.
                    confirmed.append({"finding": finding["Finding"], "reason": finding["Revalidation reason or caveat"],
                                      "without_disposition": any(f["represented_in"] != "none" and f["disposition"] in BLOCKING for f in matches)})
            # A draft compares its recorded flags; a release-only package records none. Unknown inputs stay null.
            known = findings is not None and (valid_flags if draft.is_dir() else True)
            entry["confirmed_flags"] = confirmed
            entry["confirmed_without_disposition"] = sum(f["without_disposition"] for f in confirmed) if known and draft.is_dir() else None
            # Whether the package represents an unmatched flag is awb-package's call, never inferred here.
            entry["unmatched_flags"] = (len(flagged) - len(confirmed) if known else None) if draft.is_dir() or latest else 0
            packages.append(entry)
    result["packages"] = packages
    result["git"] = git_status(root, slug, state_date, uncertain)
    return result


def upstream(root, probe, uncertain):
    """Count landed files a HEAD request can check; with probe, check each and report the rest.

    Only the latest acquisition of a source to record a URL is checked, by completed_at: a file of
    an earlier acquisition of the same source and URL counts as superseded, since landing again is
    how a changed upstream is taken up. probeable_files is null when an acquisition directory or
    provenance.json could not be read; an uncertainty names each one, and the files that were read
    are still counted and probed.
    """
    recorded_files, latest, without, complete = [], {}, 0, True

    def directories(path):
        nonlocal complete
        try:
            return sorted(p for p in path.iterdir() if p.is_dir())
        except FileNotFoundError:
            return []
        except OSError as error:
            uncertain(path, f"Cannot enumerate directory: {type(error).__name__}")
            complete = False
            return []

    for source in directories(root / "data/raw"):
        for directory in directories(source):
            if directory.name.endswith(".partial"):
                continue
            acquisition = acquisition_files(directory / "provenance.json", uncertain)
            if acquisition is None:
                complete = False
                continue
            completed_at, files = acquisition
            for file in files:
                recorded = file.get("upstream")
                if recorded is None:
                    without += 1
                    continue
                entry = {"source": source.name, "acquisition_id": directory.name, "path": file["path"]}
                recorded_files.append((entry, recorded, completed_at))
                if recorded.get("url") is not None:
                    key = (source.name, recorded["url"])
                    latest[key] = max(latest.get(key, completed_at), completed_at)
    probeable, not_probeable, superseded = [], [], 0
    for entry, recorded, completed_at in recorded_files:
        url = recorded.get("url")
        if url is not None and completed_at < latest[(entry["source"], url)]:
            superseded += 1
        elif not (isinstance(url, str) and url.split(":", 1)[0].lower() in {"http", "https"}):
            not_probeable.append({**entry, "reason": "no HTTP URL recorded"})
        elif not any(isinstance(recorded.get(name), str) for name in ("etag", "last_modified")):
            not_probeable.append({**entry, "reason": "no ETag or Last-Modified recorded"})
        else:
            probeable.append((entry, recorded))
    report = {"probeable_files": len(probeable) if complete else None}
    if probe:
        opener = head_opener()
        report.update(files=[{**entry, **probe_file(recorded, opener)} for entry, recorded in probeable],
                      not_probeable=not_probeable, superseded=superseded, without_upstream=without)
    return report


def acquisition_files(path, uncertain):
    """Return a completed acquisition's completed_at and its file entries sorted by path,
    else record an uncertainty and return None."""
    try:
        provenance = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        uncertain(path, "Missing acquisition provenance")
        return None
    except (OSError, UnicodeError, ValueError) as error:
        uncertain(path, f"Cannot read acquisition provenance: {type(error).__name__}")
        return None
    files = provenance.get("files") if isinstance(provenance, dict) else None
    completed_at = timestamp(provenance.get("completed_at")) if isinstance(provenance, dict) else None
    if not isinstance(provenance, dict):
        defect = "not a JSON object"
    elif provenance.get("status") != "complete":
        defect = "status is not complete"
    elif completed_at is None:
        defect = "completed_at is not an ISO timestamp with a UTC offset"
    elif not isinstance(files, list):
        defect = "files is not a list"
    elif not all(isinstance(f, dict) and isinstance(f.get("path"), str) and f["path"] for f in files):
        defect = "a file entry has no path"
    elif not all(f.get("upstream") is None or isinstance(f["upstream"], dict) for f in files):
        defect = "a file's upstream is not an object or null"
    elif not all(set(f.get("upstream") or {}) <= set(UPSTREAM_FIELDS) for f in files):
        defect = f"a file's upstream has a field other than {', '.join(UPSTREAM_FIELDS)}"
    elif not all(value is None or (isinstance(value, str) and value.strip())
                 for f in files for value in (f.get("upstream") or {}).values()):
        defect = "a file's upstream field is not null or a nonblank string"
    else:
        return completed_at, sorted(files, key=lambda f: f["path"])
    uncertain(path, f"Malformed acquisition provenance: {defect}")
    return None


def timestamp(value):
    """Parse land()'s completed_at, an ISO timestamp with a UTC offset, else return None."""
    try:
        parsed = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed.tzinfo else None


class RedirectRefused(urllib.error.URLError):
    """A redirect to a URL other than http(s), which the probe does not follow."""


class HeadRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Follow a redirect only to an http(s) URL, and only as another HEAD request."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urllib.parse.urlsplit(newurl).scheme.lower() not in {"http", "https"}:
            raise RedirectRefused("redirect to a URL other than http(s)")
        request = super().redirect_request(req, fp, code, msg, headers, newurl)
        if request is not None:
            request.method = "HEAD"
        return request


def head_opener():
    return urllib.request.build_opener(HeadRedirectHandler)


def probe_file(recorded, opener):
    """HEAD the recorded URL and compare its ETag, else its Last-Modified, with the recorded value."""
    try:
        request = urllib.request.Request(recorded["url"], method="HEAD")
        with opener.open(request, timeout=PROBE_TIMEOUT) as response:
            headers = response.headers
    except urllib.error.HTTPError as error:
        return {"result": "unknown", "reason": f"HTTP {error.code}"}
    except RedirectRefused:
        return {"result": "unknown", "reason": "redirected to a URL other than http(s), not followed"}
    except (OSError, ValueError, http.client.HTTPException) as error:
        return {"result": "unknown", "reason": f"{type(error).__name__}: {error}"}
    compared = {}
    for name, header in (("etag", "ETag"), ("last_modified", "Last-Modified")):
        before, now = recorded.get(name), headers.get(header)
        if not isinstance(before, str) or now is None:
            continue
        if name == "etag":
            # An ETag is opaque, chosen by the server; compare weakly, ignoring a W/ prefix.
            same = before.strip().removeprefix("W/") == now.strip().removeprefix("W/")
        else:
            try:
                same = http_date(before) == http_date(now)
            except (TypeError, ValueError, OverflowError):
                # An out-of-range year overflows the parser; such a date is compared as text.
                same = before.strip() == now.strip()
        compared[name] = (same, before, now)
    if not compared:
        return {"result": "unknown", "reason": "the server sent neither recorded validator"}
    name = "etag" if "etag" in compared else "last_modified"
    same, before, now = compared[name]
    if same:
        return {"result": "unchanged", "compared": name}
    if name == "etag" and compared.get("last_modified", (False,))[0]:
        # Servers vary an ETag by content encoding (Apache appends -gzip), so an ETag change
        # with an unchanged Last-Modified does not establish a content change.
        return {"result": "unknown", "reason": "the ETag differs but Last-Modified is unchanged"}
    return {"result": "changed", "compared": name, "recorded": before, "current": now}


def http_date(value):
    """Parse an HTTP date; one without a zone is read as GMT, as HTTP dates are."""
    parsed = parsedate_to_datetime(value)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def git_status(root, slug, state_date, uncertain):
    env = {**os.environ, "GIT_OPTIONAL_LOCKS": "0"}
    git_root = root

    def git(*args):
        return subprocess.run(["git", "-C", str(git_root), *args], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)

    try:
        repo = git("rev-parse", "--show-toplevel")
        if repo.returncode:
            return {"available": False, "reason": "Project is not inside a Git repository"}
        git_root = Path(repo.stdout.strip()).resolve()
        try:
            project = root.relative_to(git_root).as_posix()
        except ValueError:
            return {"available": False, "reason": "Cannot resolve project within Git repository"}
        project_prefix = "" if project == "." else project + "/"
        has_head = git("rev-parse", "--verify", "-q", "HEAD").returncode == 0
        scope = ("--", ":(top,literal)" + project_prefix) if project_prefix else ()
        status = git("status", "--porcelain=v1", "-z", "--untracked-files=all", *scope)
    except OSError as error:
        return {"available": False, "reason": type(error).__name__}
    if status.returncode:
        return {"available": False, "reason": "git status failed"}
    chunks = iter(status.stdout.split("\0"))
    changed = []
    for chunk in chunks:
        if not chunk:
            continue
        code, path = chunk[:2], chunk[3:]
        changed.append(path)
        if "R" in code or "C" in code:
            changed.append(next(chunks, ""))
    changed = [p[len(project_prefix):] for p in changed if p.startswith(project_prefix)]
    result = {"available": True, "has_commits": has_head, "uncommitted_paths": len(set(changed)), "mtime_date_basis": "host local timezone; Git dates use recorded commit timezone"}
    if not has_head:
        result["commit_comparison"] = "no commits yet; all work uncommitted"
    if not slug:
        return result
    prefix = f"investigations/{slug}/"
    dates = []
    missing = []
    for name in sorted(set(changed)):
        if name.startswith(prefix) and name != prefix + "state.md":
            path = root / name
            try:
                dates.append((date.fromtimestamp(path.stat().st_mtime), name))
            except OSError:
                missing.append(name)
    if missing:
        result["undated_changes"] = missing
        for name in missing:
            uncertain(root / name, "Uncommitted change lacks a readable mtime (for example deletion); state date check uncertain")
    if has_head:
        repo_prefix = project_prefix + prefix
        log = git("log", "-1", "--format=%cs", "--", ":(top,literal)" + repo_prefix, ":(top,exclude,literal)" + repo_prefix + "state.md")
        if log.returncode:
            uncertain(root / prefix, "Cannot read Git commit date")
        elif log.stdout.strip():
            commit_date = date.fromisoformat(log.stdout.strip())
            result["latest_commit_date"] = commit_date.isoformat()
            dates.append((commit_date, "latest investigation commit"))
    if dates:
        newest, source = max(dates)
        result["latest_change"] = {"date": newest.isoformat(), "source": source}
        if state_date:
            difference = (newest - state_date).days
            result["days_after_state"] = difference
            result["state_status"] = "out of date" if difference > 0 else "indeterminate at date precision" if difference == 0 else "unknown" if missing else "up to date"
    if "state_status" not in result:
        result["state_status"] = "unknown" if missing or state_date is None else "no newer dated change found"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="Workbench root (default: current directory)")
    parser.add_argument("--probe-upstream", action="store_true", help="HEAD the latest landed file of each recorded HTTP URL with recorded validators and report it changed, unchanged, or unknown")
    args = parser.parse_args()
    print(json.dumps(collect(args.root, probe_upstream=args.probe_upstream), ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
