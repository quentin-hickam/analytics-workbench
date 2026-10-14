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
import string
import subprocess
import unicodedata
from email.utils import parsedate_to_datetime
import http.client
import importlib.util
import urllib.error
import urllib.parse
import urllib.request

DISPOSITIONS = {"none", "revalidate", "omit", "release_with_caveat"}
BLOCKING = {"none", "revalidate"}


PROBE_TIMEOUT = 10
# land()'s own module from the awb-init skill beside this one: an upstream field it refuses to
# record is malformed provenance here, by the same check.
_LANDING = importlib.util.spec_from_file_location(
    "awb_status_landing", Path(__file__).resolve().parents[2] / "awb-init/assets/awb_landing.py")
landing = importlib.util.module_from_spec(_LANDING)
_LANDING.loader.exec_module(landing)


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
    retained = re.compile(r"`[^`\n]*[^`\s][^`\n]*`,\s*sha-?256:?\s*[0-9a-f]{64}(?![\w\\&])", re.I)
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
        # strikethrough that may hold a backtick, bracket or `<`, or holds an opening run of another
        # delimiter character) or the reading is uncertain (a backtick, bracket or `<` inside an
        # autolink, or a link whose destination this does not read), the rest of the cell counts as
        # no reference.
        position, clause, brackets = 0, True, 0
        # A backslash escapes the punctuation after it, read left to right as the loop below reads it,
        # and an escaped delimiter is literal, so only the unescaped rest of a run opens or closes.
        escaped = {found.end() - 1 for found in re.finditer(rf"\\[{re.escape(string.punctuation)}]", notes)}
        runs = [(start, found.end()) for found in re.finditer(r"\*+|_+|~+", notes)
                for start in [found.start() + (found.start() in escaped)] if start < found.end()]
        last_closer = {char: max((run for run in runs if notes[run[0]] == char and can_close(notes, *run)), default=(0, 0)) for char in "*_~"}
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
                # character that can close, so the span to there is skipped, unless it may hold a clause
                # or holds a run of another of the three characters that can open, which may close later.
                end = re.compile(rf"\{char}+").match(notes, position).end()
                closer_start, closer_end = last_closer[char]
                if closer_start >= end and can_open(notes, position, end):
                    if any(inner in "`[]<" for inner in notes[position:closer_end]) or any(
                            end <= start < closer_start and notes[start] != char and can_open(notes, start, stop) for start, stop in runs):
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
    result["upstream"] = upstream(root, probe_upstream, uncertain, entries)

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


def upstream(root, probe, uncertain, entries):
    """Count landed files a HEAD request can check; with probe, check each and report the rest.

    Only the latest acquisition of a source to record a URL is checked, by completed_at and then,
    for acquisitions completed in the same second, by the greater acquisition ID: a file of an
    earlier acquisition of the same source and URL counts as superseded, since landing again is how
    a changed upstream is taken up. probeable_files is null when an acquisition directory or
    provenance.json could not be read; an uncertainty names each one, and the files that were read
    are still counted and probed. entries is collect()'s directory listing, None when unreadable.
    """
    recorded_files, latest, without, complete = [], {}, 0, True

    def directories(path):
        nonlocal complete
        found = entries(path, directories=True)
        complete = complete and found is not None
        return found or []

    for source in directories(root / "data/raw"):
        for directory in directories(source):
            if directory.name.endswith(".partial"):
                continue
            acquisition = acquisition_files(directory / "provenance.json", uncertain)
            if acquisition is None:
                complete = False
                continue
            # land() records completed_at to the second; the acquisition ID orders a tie.
            order = (acquisition[0], directory.name)
            for file in acquisition[1]:
                recorded = file.get("upstream")
                # land() records an upstream whose fields are all None as null.
                if recorded is None or all(value is None for value in recorded.values()):
                    without += 1
                    continue
                entry = {"source": source.name, "acquisition_id": directory.name, "path": file["path"]}
                recorded_files.append((entry, recorded, order))
                if recorded.get("url") is not None:
                    key = (source.name, recorded["url"])
                    latest[key] = max(latest.get(key, order), order)
    probeable, not_probeable, superseded = [], [], 0
    for entry, recorded, order in recorded_files:
        url = recorded.get("url")
        if url is not None and order < latest[(entry["source"], url)]:
            superseded += 1
        elif url is None or urllib.parse.urlsplit(url).scheme not in {"http", "https"}:
            not_probeable.append({**entry, "reason": "no HTTP URL recorded"})
        elif not any(isinstance(recorded.get(name), str) for name in ("etag", "last_modified")):
            not_probeable.append({**entry, "reason": "no ETag or Last-Modified recorded"})
        else:
            probeable.append((entry, recorded))
    report = {"probeable_files": len(probeable) if complete else None}
    if probe:
        # One timeout per host and port bounds the run when a host is unreachable (VPN off, firewall).
        opener, unresponsive = head_opener(), set()
        results = [{**entry, **probe_file(recorded, opener, unresponsive)} for entry, recorded in probeable]
        report.update(files=results, not_probeable=not_probeable, superseded=superseded, without_upstream=without)
    return report


def acquisition_files(path, uncertain):
    """Return a completed acquisition's completed_at and its file entries sorted by path,
    else record an uncertainty and return None. An upstream field is checked by land()'s own
    check, so what land() refuses to record is malformed here."""
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
    elif len({f["path"] for f in files}) != len(files):
        # land() lists each file once; a repeated path would leave an entry unchecked below.
        defect = "a file path is repeated"
    else:
        try:
            # land()'s refusals name the file and parameter, never a value.
            landing._upstream({f["path"]: f["upstream"] for f in files if f.get("upstream") is not None},
                              [f["path"] for f in files])
        except ValueError as error:
            defect = str(error)
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
    """A redirect the probe does not follow: to a URL other than http(s), to an invalid URL, or to a
    host and port that timed out."""


def endpoint(url):
    """Return the host and port an http(s) URL is requested from as host:port, the scheme's port
    when none is given. The host is the one urllib connects to: percent-decoded, lowercased, and
    IDNA-encoded, so each spelling of one host gives one endpoint.

    Raise ValueError for any other URL, without a host, with an invalid port, or with a host IDNA
    cannot encode; land() refuses an http(s) URL without a host or with an invalid port.
    """
    parts = urllib.parse.urlsplit(url)
    default = {"http": 80, "https": 443}.get(parts.scheme)
    # urllib percent-decodes the host and port before it connects.
    decoded = urllib.parse.urlsplit("//" + urllib.parse.unquote(parts.netloc))
    host, port = decoded.hostname, decoded.port
    if default is None or not host:
        raise ValueError("not an http(s) URL with a host")
    if not host.isascii():
        host = host.encode("idna").decode("ascii")
    host = f"[{host}]" if ":" in host else host
    return f"{host}:{default if port is None else port}"


def sendable(url):
    """Return url as a request can send it: a non-ASCII host IDNA-encoded, and non-ASCII characters
    in the path, query, and fragment percent-encoded as UTF-8. An ASCII url is returned as recorded.

    Raise ValueError for a host IDNA cannot encode.
    """
    if url.isascii():
        return url
    parts = urllib.parse.urlsplit(url)
    netloc = parts.netloc
    if not netloc.isascii():
        host = parts.hostname.encode("idna").decode("ascii")
        netloc = host if parts.port is None else f"{host}:{parts.port}"
    return urllib.parse.urlunsplit((parts.scheme, netloc, *(urllib.parse.quote(part, safe=string.punctuation)
                                                            for part in (parts.path, parts.query, parts.fragment))))


class HeadRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Follow a redirect only to an http(s) URL, and only as another HEAD request.

    A request from probe_file carries endpoints, the host:port endpoints its chain has requested
    in order, and unresponsive, the endpoints that timed out; a redirect to an unresponsive
    endpoint is not followed.
    """

    # urllib raises an HTTPError with this reason, plus the last status message, on a redirect loop.
    inf_msg = "redirect loop: "

    def http_error_302(self, req, fp, code, msg, headers):
        # Checked before urllib's own check, which lets ftp through and names the URL it refuses.
        location = headers.get("location", headers.get("uri"))
        try:
            scheme = urllib.parse.urlsplit(location).scheme if location is not None else ""
        except ValueError:
            raise RedirectRefused("redirected to an invalid URL, not followed") from None
        if scheme not in {"", "http", "https"}:
            raise RedirectRefused("redirected to a URL other than http(s), not followed")
        return super().http_error_302(req, fp, code, msg, headers)

    http_error_301 = http_error_303 = http_error_307 = http_error_308 = http_error_302

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        try:
            target = endpoint(newurl)
        except ValueError:
            raise RedirectRefused("redirected to an invalid URL, not followed") from None
        if target in getattr(req, "unresponsive", ()):
            raise RedirectRefused(f"redirected to {target}, not followed: an earlier request to {target} timed out")
        request = super().redirect_request(req, fp, code, msg, headers, newurl)
        if request is not None:
            request.method = "HEAD"
            request.unresponsive = getattr(req, "unresponsive", set())
            request.endpoints = getattr(req, "endpoints", [])
            request.endpoints.append(target)
        return request


def head_opener():
    return urllib.request.build_opener(HeadRedirectHandler)


def probe_file(recorded, opener, unresponsive):
    """HEAD the recorded URL and compare its ETag, else its Last-Modified, with the recorded value.

    unresponsive holds the host:port endpoints a request timed out on, shared across a run: the
    endpoint whose request timed out, after any redirects, is added, and no request is sent to one
    already in it. Another port on the same host is still requested.
    """
    # land() refuses an http(s) URL without a host or with an invalid port; what is left to raise
    # is a host IDNA cannot encode, or one whose percent-encoding decodes to an invalid port.
    try:
        url = sendable(recorded["url"])
        target = endpoint(url)
    except ValueError as error:
        return {"result": "unknown", "reason": f"not a URL a request can be sent to: {error}"}
    if target in unresponsive:
        return {"result": "unknown", "reason": f"not requested: an earlier request to {target} timed out"}
    request = urllib.request.Request(url, method="HEAD")
    request.unresponsive, request.endpoints = unresponsive, [target]
    try:
        with opener.open(request, timeout=PROBE_TIMEOUT) as response:
            headers = response.headers
    except urllib.error.HTTPError as error:
        if 300 <= error.code < 400:
            loop = str(error.reason).startswith(HeadRedirectHandler.inf_msg)
            return {"result": "unknown", "reason": f"HTTP {error.code}: " + (
                "redirected in a loop or too many times, not followed" if loop else "not a redirect the probe follows")}
        return {"result": "unknown", "reason": f"HTTP {error.code}"}
    except RedirectRefused as error:
        return {"result": "unknown", "reason": error.reason}
    except (OSError, ValueError, http.client.HTTPException) as error:
        if isinstance(error, TimeoutError) or isinstance(getattr(error, "reason", None), TimeoutError):
            unresponsive.add(request.endpoints[-1])
            return {"result": "unknown", "reason": f"no response from {request.endpoints[-1]} within {PROBE_TIMEOUT} s"}
        return {"result": "unknown", "reason": f"{type(error).__name__}: {error}"}
    compared, unusable, recorded_undated = {}, [], False
    for name, header in (("etag", "ETag"), ("last_modified", "Last-Modified")):
        before, now = recorded.get(name), headers.get(header)
        if not isinstance(before, str) or now is None:
            continue
        if not now.strip():
            # A blank header is no evidence of change; nor, below, is a date that does not parse
            # compared with one that does.
            unusable.append(header)
            continue
        if name == "etag":
            # An ETag is opaque, chosen by the server; compare weakly, ignoring a W/ prefix.
            same = before.strip().removeprefix("W/") == now.strip().removeprefix("W/")
        else:
            then, current = http_date(before), http_date(now)
            if then is None and current is None:
                # A recorded value that is not a date is compared as text with one that is not either.
                same = before.strip() == now.strip()
            elif then is None:
                recorded_undated = True
                continue
            elif current is None:
                unusable.append(header)
                continue
            else:
                same = then == current
        compared[name] = (same, before, now)
    if not compared and (unusable or recorded_undated):
        reasons = []
        if unusable:
            verb = "is not a usable validator" if len(unusable) == 1 else "are not usable validators"
            reasons.append(f"the server's {' and '.join(unusable)} {verb}")
        if recorded_undated:
            reasons.append("the recorded Last-Modified is not a date to compare with the server's")
        return {"result": "unknown", "reason": ", and ".join(reasons)}
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
    """Parse an HTTP date, one without a zone read as GMT as HTTP dates are, else return None."""
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError):
        return None
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
