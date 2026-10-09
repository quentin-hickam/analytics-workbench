"""Read-only status facts for standard workbench Markdown records and manifest.json files.

Run with Python 3.10+: collect_status.py [PROJECT_ROOT]. Emits compact JSON;
uncertainties identify records requiring targeted agent interpretation.
"""

import argparse
from collections import Counter
from datetime import date, datetime
import json
import os
from pathlib import Path
import re
import subprocess

DISPOSITIONS = {"none", "revalidate", "omit", "release_with_caveat"}
BLOCKING = {"none", "revalidate"}


def collect(root):
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

    def manifest(directory, *, frozen=False):
        """Read manifest.json; a frozen release's is tolerated when absent, unreadable, or not JSON."""
        path = directory / "manifest.json"
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(obj, dict):
                return obj
            raise ValueError
        except FileNotFoundError:
            if not frozen:
                uncertain(directory, "Draft lacks manifest.json; awb-package rewrites it on the next revision")
        except (OSError, UnicodeError, ValueError) as error:
            if not frozen:
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
            # Frozen releases are read only for released_at; an earlier format leaves it unknown.
            released = timestamp(manifest(latest, frozen=True), "released_at") if latest else None
            entry = {"name": directory.name, "draft_exists": draft.is_dir(), "revised_at": revised.isoformat() if revised else None,
                     "release_inventory_known": release_dirs is not None, "latest_release": latest.name if latest else None, "released_at": released.isoformat() if released else None,
                     "draft_vs_release": ("ahead" if revised > released else "same_or_older") if revised and released else None}
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
    args = parser.parse_args()
    print(json.dumps(collect(args.root), ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
