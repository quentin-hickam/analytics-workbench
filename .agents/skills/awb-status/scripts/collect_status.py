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
import string
import subprocess
import unicodedata

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
    registered = table(section(sources, "Sources", sources_path), ["Source ID", "System or provider", "Contents and grain", "Owner or contact", "Acquisition method", "Relevance and fitness", "Status", "Notes"], sources_path)

    def documentation_basis(row):
        """Whether Relevance and fitness begins with the `from documentation` basis; an unlabelled assessment is uncertain."""
        basis = re.match(r"\s*`?from (documentation|landed records)\b", row["Relevance and fitness"], re.I)
        if basis is None and row["Relevance and fitness"]:
            uncertain(sources_path, f"Source {row['Source ID']}: Relevance and fitness does not begin with its basis")
        return basis is not None and basis.group(1).lower() == "documentation"

    # The two reference forms foundation/sources.md defines, exactly as it states them; any other
    # spelling, valid Markdown or not, counts as no reference. Form 1 is `[text](destination)`: non-empty
    # text without `[`, `]`, `\`, `<` or a backtick, then a destination in angle brackets without `<`, `>`,
    # `\` or a line break, or a bare one without whitespace, control characters, `<` or `\` whose
    # parentheses balance at any depth. Form 2 is a location in single backticks, a comma, then
    # `sha256` (also `SHA-256`, `sha256:`) and exactly 64 hex digits with no letter, digit, `_`, `\` or `&`
    # after, which an escape or entity could render as one.
    link_text = re.compile(r"\[[^\[\]\\<`]+\]\(")
    angle_destination = re.compile(r"<[^<>\\\n]+>\)")
    retained = re.compile(r"`[^`\n]*[^`\s][^`\n]*`,\s*sha-?256:?\s*[0-9a-f]{64}(?![0-9A-Za-z_\\&])", re.I)
    label = re.compile(r"\s*reference:\s*", re.I)
    line_break = re.compile(r"<br\s*/?>", re.I)
    entity = re.compile(r"&(?:#[0-9]{1,7}|#[xX][0-9a-fA-F]{1,6}|[A-Za-z][A-Za-z0-9]{1,31});")
    # Raw HTML and autolinks, which CommonMark reads before code spans and links. These patterns are
    # looser than CommonMark's and markdown-it's: reading stops at anything that may be raw HTML other
    # than `<br>`, and an autolink is never read shorter than a renderer reads it.
    attribute = r"""\s+[\w:.-]+(?:\s*=\s*(?:[^"'=<>`\x00-\x20]+|'[^']*'|"[^"]*"))?"""
    html = [re.compile(pattern, re.S) for pattern in (
        rf"</?\w[\w-]*(?:{attribute})*\s*/?>", r"<!---?>", r"<!--.*?-->", r"<!--(?:[^-]|-[^-]|--[^>])*-->",
        r"<\?.*?\?>", r"<!\[CDATA\[.*?\]\]>", r"<![A-Za-z][^>]*>")]
    autolink = re.compile(r"<[^<>\x00-\x20]*[:@][^<>\x00-\x20]*>")

    def flanking(notes, start, end):
        """Whether the delimiter run notes[start:end] is left- and right-flanking, and the characters around it."""
        before, after = notes[start - 1:start] or " ", notes[end:end + 1] or " "
        punctuation = lambda char: char in string.punctuation or unicodedata.category(char)[0] in "PS"
        left = not after.isspace() and (not punctuation(after) or before.isspace() or punctuation(before))
        right = not before.isspace() and (not punctuation(before) or after.isspace() or punctuation(after))
        return left, right, punctuation(before), punctuation(after)

    def can_open(notes, start, end):
        left, right, before, _ = flanking(notes, start, end)
        return left and (notes[start] != "_" or not right or before)

    def can_close(notes, start, end):
        left, right, _, after = flanking(notes, start, end)
        return right and (notes[start] != "_" or not left or after)

    def bare_destination(notes, start):
        """Where the link's `)` closes a bare destination starting at `start`, or None."""
        depth = 0
        for position in range(start, len(notes)):
            char = notes[position]
            if char.isspace() or char in "<\\\x7f" or char < " ":
                return None
            if char == "(":
                depth += 1
            elif char == ")":
                if depth == 0:
                    return position + 1 if position > start else None
                depth -= 1
        return None

    def destination(notes, start):
        """Where `)` closes an angle or bare destination starting at `start`, or None."""
        angled = angle_destination.match(notes, start)
        return angled.end() if angled else bare_destination(notes, start)

    def link(notes, start):
        """Where a form-1 link starting at `start` ends, or None."""
        opened = link_text.match(notes, start)
        return opened and destination(notes, opened.end())

    def referenced(notes):
        """Whether a Notes clause in plain text opens with `reference:` directly followed by one of the two forms."""
        # Read left to right as CommonMark does. A clause opens the cell or follows `;`, `,`, `.` or a
        # `<br>`, outside code spans, raw HTML, autolinks, emphasis, strikethrough, links and brackets;
        # only what directly follows the label counts, so `reference: pending. See [x](y)` records no
        # reference. Where a clause could sit inside an element (any raw HTML but `<br>`, or emphasis or
        # strikethrough that may hold a backtick, bracket or `<`) or the reading is uncertain (a
        # backtick, bracket or `<` inside an autolink, or a link whose destination this does not
        # read), the rest of the cell counts as no reference.
        position, clause, brackets = 0, True, 0
        last_closer = {char: max((found.span() for found in re.finditer(rf"\{char}+", notes)
                                  if can_close(notes, *found.span())), default=(0, 0)) for char in "*_~"}
        while position < len(notes):
            labelled = clause and not brackets and label.match(notes, position)
            if labelled and (retained.match(notes, labelled.end()) or link(notes, labelled.end())):
                return True
            clause = False
            char = notes[position]
            if char == "\\" and notes[position + 1:position + 2] in tuple(string.punctuation):
                position += 2
            elif char == "`":
                run = re.match(r"`+", notes[position:]).group()
                closer = re.compile(rf"(?<!`){run}(?!`)").search(notes, position + len(run))
                position = closer.end() if closer else position + len(run)
            elif char == "<":
                broken = line_break.match(notes, position)
                if not broken and any(pattern.match(notes, position) for pattern in html):
                    return False  # Where the element ends, and so whether a clause is inside it, is not read.
                linked = autolink.match(notes, position)
                end = broken.end() if broken else linked and linked.end()
                if end and any(inner in "`[]<" for inner in notes[position + 1:end]):
                    return False  # Renderers may split this construct differently.
                position = end or position + 1
                clause = bool(broken)
            elif char in "*_~":
                # Emphasis or strikethrough: whatever this run opens closes by the last run of the same
                # character that can close, so the span to there is skipped, unless it may hold a clause.
                end = re.compile(rf"\{char}+").match(notes, position).end()
                closer_start, closer_end = last_closer[char]
                if closer_start >= end and can_open(notes, position, end):
                    if any(inner in "`[]<" for inner in notes[position:closer_end]):
                        return False
                    end = closer_end
                position = end
            elif char == "[":
                closed = link(notes, position)
                brackets += closed is None
                position = closed or position + 1
            elif char == "]" and brackets:
                brackets -= 1
                if notes.startswith("(", position + 1):
                    closed = destination(notes, position + 2)
                    if closed is None:
                        return False
                    position = closed
                else:
                    position += 1
            elif entity.match(notes, position):
                position = entity.match(notes, position).end()  # Its `;` ends the entity, not a clause.
            else:
                clause = char in ";,."
                position += 1
        return False

    # foundation/sources.md states the basis and reference forms these read.
    result["sources"] = None if registered is None else {"count": len(registered), "documentation_without_reference": [
        row["Source ID"] for row in registered if documentation_basis(row) and not referenced(row["Notes"])]}
    result["landed_data_storage"] = storage(field(readme, "Landed data is kept at", readme_path, optional=True))
    result["release_storage"] = storage(field(readme, "Released packages are kept at", readme_path, optional=True))

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
