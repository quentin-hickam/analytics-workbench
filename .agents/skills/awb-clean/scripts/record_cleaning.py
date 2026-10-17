#!/usr/bin/env python3
"""Write the records of one cleaning pass in one call: quality rows, catalog cells, and flagged findings.

Run with Python 3.10+ (standard library only):
    record_cleaning.py PROJECT_ROOT SCAN_NAME [--dry-run] < decisions.json
SCAN_NAME names foundation/scans/<SCAN_NAME>.json written by scan_dataset.py. Decisions on stdin:
    {"date": "YYYY-MM-DD",                                        optional, default today
     "issues": {"S1": {"impact", "treatment", "status",           judgment columns, required for a new row
                       "correction", "change",                    both or neither: a correction row
                       "findings", "object",                      optional overrides
                       "check": {"publication", "name"},          optional: a publication check to cite
                       "amend": {"observation", "reason"}}},      optional, on a recorded row only
     "new": [{"object", "observation", "evidence",                an issue the scan did not report
              "impact", "treatment", "status",                    judgment columns, required
              "correction", "change", "findings", "check"}],      optional, as for issues
     "findings": "...",                                           correction rows' findings when no flags
     "flags": [{"investigation", "result", "reason"}],            findings to flag
     "catalog": {"name", "cells": {column: text}}}                catalog cells to set
Any other key is refused. Text may name an issue as {S1}, {N1} (the first new entry), or {DQ-004};
it becomes the issue's quality ID. A recorded quality ID, such as DQ-004, also works as a key: it
revises only judgment cells, keeps the observation and link, and its correction carries no rescan
suffix. An amend on a recorded row, by either key, replaces its observation with the new text
followed by `; amended <date>: <reason>; was: <the observation it replaces>`, so the withdrawn text
and its scan marker stay in the row; the same amendment again, on any day, changes nothing. New rows' IDs continue the prefix and numbering the Active table already uses, DQ-001 in a
record without IDs. A check names a publication directory, data/parquet/<dataset>/<publication-id>/
relative to PROJECT_ROOT or absolute inside it, and one of the checks its publication.json records;
the citation, with the check's outcome and the root-relative path, is appended to the row's Current
treatment once.

A new entry is an issue the analyst found that the scan did not report. Its evidence is one line of
text, its runs of whitespace read as one space. Evidence that ends in .sql, in any case, after one
pair of surrounding backticks is set aside, or that ends in .sql followed by a backtick, cites a
saved query: it must be that query's path alone, relative to PROJECT_ROOT, without spaces or
backticks, naming a file inside the project, and is written as one code span of its normalized
path. Any other text, such as a reference and page, is written as given. Evidence citing a saved
query that is missing, outside the project, or inside a sentence is refused. Its row gets the next
ID, the observation followed by `; evidence <evidence>`, and no scan marker or quality.json link.
An Active row with the same object and observation is that entry already recorded, as when a call
is run again: its judgment cells are set instead.

Quality issue rows get the next ID, the scan's counts and examples, and the marker
`<scan>#<key>` with its scan date. foundation/quality.json holds hashed scan links and recorded
counts and dates, built from a row's prose when a link is missing; a marker on several rows, or on a
row whose ID repeats, refuses a decision on that issue. A baseline observation supplies both
counts and date; otherwise the current scan does. Reopening updates the link and judgment cells,
keeping the observation. Correction rows carry the rescan's before and after counts; a row
identical to one already recorded is not appended again but listed as corrections_unchanged. A
flag goes through the project's provenance helper and sets the finding's status to `revalidation-needed (was <status>)`, adds the reason, and updates
`Last updated`. All versions are checked before writing: A replaces links, Active rows, and
catalog; B writes flags; C appends corrections. Failures report completed phases and replaced
files. --dry-run prints the rows that would change and writes nothing. Prints compact JSON.

foundation/quality.md and catalog.md are read as Markdown sections: a heading line, then the lines
up to the next line starting with `#`. Each section the script reads (## Active limitations and
issues, ## Correction record, and the catalog's ## Published datasets and views) holds one table:
its first line starting with `|` is the header, the next is its `| --- |` separator, and the rows
are the `|` lines directly under that. A header without a separator, or a `|` line elsewhere in the
section, such as a row added after prose that follows the table, refuses the call with its line
number before anything is written; a header and separator there start a second table, which belongs
under its own heading. Every call also reads the Correction record, when quality.md has one, so its
heading keeps its table even while that table has no rows: each of its rows has the header's number
of cells and a YYYY-MM-DD Date, so an issue row added at the end of the file, directly under that
table, is refused with its line rather than read as a correction. A new row's ID is never one
already in the first cell of a table row anywhere in quality.md.
"""

import argparse
import importlib.util
import json
import os
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from quality_links import OBJECT, OBSERVATION, QualityLinks, position

TEMPLATES = Path(__file__).resolve().parents[2] / "awb-init/assets/workbench/foundation"
ACTIVE = "## Active limitations and issues"
CORRECTIONS = "## Correction record"
DATASETS = "## Published datasets and views"


class RecordError(ValueError):
    pass


def _cells(line):
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def _row(cells):
    return "| " + " | ".join(cells) + " |"


def _cell(text):
    return re.sub(r"\s*\n\s*", " ", str(text)).replace("|", r"\|").strip()


def _separator(line):
    return line.strip().startswith("|") and all(re.fullmatch(r":?-+:?", cell) for cell in _cells(line))


class Table:
    """The one Markdown table in a heading's section, edited in place within the file's lines; the
    module docstring gives the grammar."""

    def __init__(self, lines, heading, path):
        try:
            start = next(i for i, line in enumerate(lines) if line.strip() == heading)
        except StopIteration:
            raise RecordError(f"{path}: no '{heading}' section; record this by hand") from None
        index = start + 1
        while index < len(lines) and not lines[index].strip().startswith("|"):
            if lines[index].startswith("#"):
                raise RecordError(f"{path}: no table under '{heading}'")
            index += 1
        if index + 1 >= len(lines):
            raise RecordError(f"{path}: no table under '{heading}'")
        if not _separator(lines[index + 1]):
            raise RecordError(f"{path}: line {index + 1} under '{heading}' has no | --- | separator line under it; "
                              "the table's header must come first, with rows directly under the separator")
        self.lines, self.path, self.header = lines, path, index
        self.columns = _cells(lines[index])
        self.end = index + 2
        while self.end < len(lines) and lines[self.end].strip().startswith("|"):
            self.end += 1
        section = next((i for i in range(self.end, len(lines)) if lines[i].startswith("#")), len(lines))
        outside = [i for i in range(self.end, section) if lines[i].strip().startswith("|")]
        if outside:
            second = next((i for i in outside if i + 1 < len(lines) and _separator(lines[i + 1])), None)
            if second is not None:
                raise RecordError(f"{path}: line {second + 1} starts a second table under '{heading}', whose table "
                                  f"ends at line {self.end}; a section holds one table, so put the second under "
                                  "its own heading or outside the section, then rerun")
            where = " and ".join(f"line {i + 1} ({_cells(lines[i])[0] or 'no ID'})" for i in outside)
            many = len(outside) > 1
            width = len(self.columns)
            if all(len(_cells(lines[i])) == width for i in outside):
                advice = f"move {'them' if many else 'it'} directly under its last row"
            else:
                # A row with another table's columns belongs in that table, not under this one's last row.
                advice = (f"{'they do not all have' if many else 'it does not have'} this table's {width} columns; "
                          f"move {'each' if many else 'it'} to the table whose columns it has")
            raise RecordError(f"{path}: {'rows at' if many else 'a row at'} {where} {'sit' if many else 'sits'} outside "
                              f"the table under '{heading}', whose rows end at line {self.end}; {advice}, then rerun")

    def rows(self):
        return [(i, _cells(self.lines[i])) for i in range(self.header + 2, self.end)]

    def column(self, name):
        if name not in self.columns:
            raise RecordError(f"{self.path}: table lacks the column '{name}'")
        return self.columns.index(name)

    def append(self, values):
        cells = [_cell(values.get(c, "")) for c in self.columns]
        self.lines.insert(self.end, _row(cells))
        self.end += 1
        return self.lines[self.end - 1]

    def set(self, line_index, values):
        cells = _cells(self.lines[line_index])
        cells += [""] * (len(self.columns) - len(cells))
        for name, value in values.items():
            cells[self.column(name)] = _cell(value)
        self.lines[line_index] = _row(cells)
        return self.lines[line_index]


def _load(root, relative, template=None):
    path = root / relative
    if path.is_file():
        return path.read_text(encoding="utf-8").splitlines()
    if template is None or not (TEMPLATES / template).is_file():
        raise RecordError(f"{relative} does not exist")
    return (TEMPLATES / template).read_text(encoding="utf-8").splitlines()


ID = r"([A-Za-z]+-?)(\d+)"


def _next_ids(table):
    """Yield new IDs continuing the table's prefix and numbering, DQ-001 by default: the ledger's
    questions are Q-NNN. An ID in the first cell of any table row in the file, such as an issue row
    misplaced under another table, is skipped, so no new row repeats it."""
    at = position(table.columns, "ID", 0)
    found = [re.fullmatch(ID, cells[at]) for _, cells in table.rows()]
    found = [m for m in found if m]
    prefix = Counter(m.group(1) for m in found).most_common(1)[0][0] if found else "DQ-"
    width = max((len(m.group(2)) for m in found), default=3)
    number = max((int(m.group(2)) for m in found), default=0)
    first = (re.fullmatch(ID, _cells(line)[0]) for line in table.lines if line.strip().startswith("|"))
    used = {(m.group(1), int(m.group(2))) for m in first if m}

    def ids(number):
        while True:
            number += 1
            if (prefix, number) not in used:
                yield f"{prefix}{number:0{width}d}"
    return ids(number)


def _check_corrections(table):
    """Refuse a Correction record row that is not one: another cell count or no YYYY-MM-DD Date."""
    date_at = position(table.columns, "Date", 0)
    for line_index, cells in table.rows():
        wrong = []
        if len(cells) != len(table.columns):
            wrong.append(f"{len(cells)} cells where the table has {len(table.columns)}")
        if not (date_at < len(cells) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", cells[date_at])):
            wrong.append("no YYYY-MM-DD date in its Date cell")
        if wrong:
            raise RecordError(f"{table.path}: line {line_index + 1} ({cells[0] or 'no ID'}) under '{CORRECTIONS}' "
                              f"is not a correction row: it has {' and '.join(wrong)}; an issue row belongs under "
                              f"the last row of the table under '{ACTIVE}', so move it there, then rerun")


def _fill(text, ids, prefixes=("S",)):
    """Replace {S1}, {N1}, or {DQ-004} with its quality ID; an unknown name with a known prefix is an error."""
    def replace(match):
        name = match.group(1)
        if name in ids:
            return ids[name]
        if re.fullmatch(ID, name).group(1) in prefixes:
            raise RecordError(f"{{{name}}} names no issue recorded in this call or earlier")
        return match.group(0)
    return re.sub(r"\{([A-Za-z]+-?\d+)\}", replace, str(text))


def _load_provenance(root):
    path = root / "src/provenance.py"
    if not path.is_file():
        raise RecordError("src/provenance.py is missing; run awb-init repair: install_helpers.py --upgrade")
    spec = importlib.util.spec_from_file_location("awb_clean_project_provenance", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "flag_findings"):
        raise RecordError("src/provenance.py predates findings.json; run awb-init repair: install_helpers.py --upgrade")
    return module


def _code(text):
    """text as one single-line Markdown code span, its characters JSON-escaped so distinct texts stay distinct."""
    escaped = "".join(c if c.isprintable() else json.dumps(c)[1:-1] for c in json.dumps(text, ensure_ascii=False)[1:-1])
    fence = "`" * (max(map(len, re.findall("`+", escaped)), default=0) + 1)
    pad = " " if escaped.startswith("`") or escaped.endswith("`") else ""
    return f"{fence}{pad}{escaped}{pad}{fence}"


def _citation(root, check):
    """Return the text citing a check that a publication's publication.json records."""
    if (not isinstance(check, dict) or set(check) != {"publication", "name"}
            or not all(isinstance(check[k], str) and check[k].strip() for k in check)):
        raise RecordError('check needs {"publication": "data/parquet/<dataset>/<publication-id>/", "name": "<check>"}')
    # One spelling per publication, root-relative, so a citation is appended once and names no local path.
    # normpath keeps a symlinked data/parquet; resolve() admits an absolute path through a symlinked root.
    given = Path(os.path.normpath(root / check["publication"].strip()))
    directory = given if given.is_relative_to(root) else given.resolve()
    parts = directory.relative_to(root).parts if directory.is_relative_to(root) else ()
    if len(parts) != 4 or parts[:2] != ("data", "parquet") or parts[3].endswith(".partial"):
        raise RecordError(f"check publication {check['publication']!r} is not a "
                          "data/parquet/<dataset>/<publication-id>/ directory in this project")
    publication = "/".join(parts)
    path = directory / "publication.json"
    try:
        recorded = json.loads(path.read_text(encoding="utf-8")).get("checks") or []
    except (OSError, ValueError, AttributeError) as error:
        raise RecordError(f"no publication.json at {publication}/ to cite a check from") from error
    found = [c for c in recorded if isinstance(c, dict) and c.get("name") == check["name"]]
    if not found:
        names = ", ".join(str(c.get("name")) for c in recorded if isinstance(c, dict)) or "none"
        raise RecordError(f"{publication}/publication.json records no check {check['name']}; it records {names}")
    # A name may hold any character a column can: render it faithfully on one line, as the dedupe compares it.
    return f"check {_code(check['name'])} {found[0].get('outcome')} in `{publication}/publication.json`"


DECISION_KEYS = ("date", "issues", "new", "findings", "flags", "catalog")
NEW_REQUIRED = ("object", "observation", "evidence", "impact", "treatment", "status")
NEW_OPTIONAL = ("correction", "change", "findings", "check")


def _new_entries(root, new):
    """The decisions' `new` list, checked against the module docstring's rules: [(name, entry, evidence)]."""
    if not isinstance(new, list) or not all(isinstance(entry, dict) for entry in new):
        raise RecordError("new must be a list of issue objects, each with " + ", ".join(NEW_REQUIRED))
    checked = []
    for number, entry in enumerate(new, 1):
        name = f"N{number}"
        unknown = sorted(set(entry) - set(NEW_REQUIRED) - set(NEW_OPTIONAL))
        if unknown:
            raise RecordError(f"{name} has unknown keys: {', '.join(unknown)}")
        missing = [k for k in NEW_REQUIRED if not (isinstance(entry.get(k), str) and entry[k].strip())]
        if missing:
            raise RecordError(f"{name} needs {', '.join(missing)} for a new quality row")
        if bool(entry.get("correction")) != bool(entry.get("change")):
            raise RecordError(f"{name}: give both correction and change, or neither")
        evidence = " ".join(entry["evidence"].split())
        # A path in backticks is the same citation as a bare one, so it is checked the same way.
        bare = evidence[1:-1].strip() if len(evidence) > 1 and evidence[0] == evidence[-1] == "`" else evidence
        if re.search(r"\.sql`?$", bare, re.IGNORECASE):
            path = Path(os.path.normpath(root / bare))
            if (Path(bare).is_absolute() or "`" in bare or " " in bare
                    or not path.is_relative_to(root) or not path.is_file()):
                raise RecordError(f"{name} evidence names no saved query: {evidence}; evidence ending in .sql must "
                                  "be a saved query's path alone, relative to the project root and naming a file "
                                  "in it; otherwise give a reference in words that does not end in .sql")
            evidence = f"`{path.relative_to(root).as_posix()}`"
        checked.append((name, entry, evidence))
    return checked


def record(project_root, scan_name, decisions, *, dry_run=False, today=None):
    """Validate DECISIONS, then write A (records), B (flags), C (corrections)."""
    root = Path(project_root).resolve()
    unknown_keys = sorted(set(decisions) - set(DECISION_KEYS))
    if unknown_keys:
        raise RecordError(f"decisions have unknown keys: {', '.join(unknown_keys)}; expected {', '.join(DECISION_KEYS)}")
    new = _new_entries(root, decisions.get("new") or [])
    scan_path = root / "foundation/scans" / f"{scan_name}.json"
    try:
        scan = json.loads(scan_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise RecordError(f"no scan at foundation/scans/{scan_name}.json; run scan_dataset.py first") from error
    day = decisions.get("date") or (today or date.today()).isoformat()
    marker = f"{scan['name']}#"
    baseline = (scan.get("baseline") or {}).get("issues") or []
    by_id = {issue["id"]: issue for issue in scan["issues"]}
    by_id.update({issue["id"]: issue for issue in baseline})  # the original observation wins
    observed_at = {issue["id"]: scan["scanned_at"][:10] for issue in scan["issues"]}
    observed_at.update({issue["id"]: scan["baseline"]["scanned_at"][:10] for issue in baseline})
    delta = {d["id"]: d for d in (scan.get("delta") or {}).get("issues", [])}
    target = scan["target"]
    subject = target["path"] or scan["name"]

    files, changed = {}, {}
    quality = files["foundation/quality.md"] = _load(root, "foundation/quality.md", "quality.md")
    active = Table(quality, ACTIVE, "foundation/quality.md")
    if any(line.strip() == CORRECTIONS for line in quality):
        _check_corrections(Table(quality, CORRECTIONS, "foundation/quality.md"))
    issues = decisions.get("issues") or {}
    by_qid = {}
    id_at, object_at, observation_at = (position(active.columns, "ID", 0), position(active.columns, OBJECT, 1),
                                        position(active.columns, OBSERVATION, 2))
    for line_index, cells in active.rows():
        if re.fullmatch(ID, cells[id_at]):
            by_qid.setdefault(cells[id_at], []).append(line_index)
    revised = {k: by_qid[k] for k in issues if k not in by_id and k in by_qid}
    unknown = sorted(set(issues) - set(by_id) - set(revised))
    if unknown:
        raise RecordError(f"issues not in the scan or the quality record: {', '.join(unknown)}")
    for qid, lines in revised.items():
        if len(lines) > 1:
            raise RecordError(f"foundation/quality.md: {len(lines)} active rows have the ID {qid}")
        revised[qid] = lines[0]
        observation = _cells(quality[lines[0]])[observation_at]
        markers = set(re.findall(r"`([^`\s#]+)#[^`]+`", observation))
        if markers and scan["name"] not in markers:
            raise RecordError(f"{qid} is recorded from scan {', '.join(sorted(markers))}, "
                              f"not {scan['name']}; pass that scan to revise it")

    try:
        links = QualityLinks(root, quality)
    except ValueError as error:
        raise RecordError(str(error)) from error
    recorded = {}
    decided = {by_id[k]["key"] for k in issues if k in by_id}
    for issue in scan["issues"] + baseline:
        key = issue["key"]
        resolved = links.resolve(scan["name"], key)
        if resolved:
            recorded[key] = (resolved[0], resolved[1]["id"])
            continue
        links.discard(scan["name"], key)
        carriers = links.active.markers.get((scan["name"], key), [])
        if key in decided and carriers:
            raise RecordError(f"marker `{marker}{key}` is on rows {', '.join(links.active.qid(i) or '(no ID)' for i in carriers)} "
                              "with no single row and ID to link; give the rows distinct IDs and one marker, "
                              "or revise a row by its quality ID")

    # Allocate IDs first so {S1}, {N1}, and {DQ-004} placeholders resolve anywhere in the decisions.
    ids, new_ids, named = {}, _next_ids(active), {}
    for issue_id in issues:
        if issue_id in revised:
            ids[issue_id], line_index = issue_id, revised[issue_id]
        else:
            key = by_id[issue_id]["key"]
            ids[issue_id] = recorded[key][1] if key in recorded else next(new_ids)
            line_index = recorded[key][0] if key in recorded else None
        if line_index is None:
            continue
        if line_index in named:
            raise RecordError(f"{named[line_index]} and {issue_id} both name {ids[issue_id]}; "
                              "give one decision per issue")
        named[line_index] = issue_id
    for issue in scan["issues"] + baseline:
        if issue["key"] in recorded and issue["id"] not in ids:
            ids[issue["id"]] = recorded[issue["key"]][1]
    for qid in [*by_qid, *ids.values()]:
        ids.setdefault(qid, qid)
    prefixes = {"S", "N", "Q-", "DQ-"} | {re.fullmatch(ID, qid).group(1) for qid in by_qid}
    fill = lambda text: _fill(text, ids, prefixes)

    # A new entry names its own row: an Active row with its object and observation, else a new ID.
    # IDs are allocated in order, so an entry's text may name an earlier entry.
    by_text = {}
    for line_index, cells in active.rows():
        if max(object_at, observation_at) < len(cells):
            by_text.setdefault((cells[object_at], cells[observation_at]), []).append(line_index)
    found = {}
    for name, entry, evidence in new:
        obj, observation = fill(entry["object"]), f"{fill(entry['observation'])}; evidence {evidence}"
        lines = by_text.get((_cell(obj), _cell(observation)), [])
        if len(lines) > 1:
            raise RecordError(f"{name} is recorded on {len(lines)} active rows; give them distinct IDs or remove one")
        if lines:
            qid = _cells(quality[lines[0]])[id_at]
            if not re.fullmatch(ID, qid) or len(by_qid.get(qid, [])) != 1:
                raise RecordError(f"{name} is recorded on a row without a unique ID; give that row one")
            if lines[0] in named:
                raise RecordError(f"{named[lines[0]]} and {name} both name {qid}; give one decision per issue")
            named[lines[0]] = name
        else:
            qid = next(new_ids)
        ids[name] = ids[qid] = qid
        found[name] = (lines[0] if lines else None, obj, observation)

    flags = decisions.get("flags") or []
    by_investigation = {}
    for flag in flags:
        if not all(flag.get(k) for k in ("investigation", "result", "reason")):
            raise RecordError("each flag needs investigation, result, and reason")
        by_investigation.setdefault(flag["investigation"], []).append(flag["result"])
    default_findings = ("; ".join(f"{inv}: {', '.join(results)}" for inv, results in by_investigation.items())
                        or decisions.get("findings"))

    added, updated, corrections, rows, amended = [], [], [], [], []
    judged = {key: active.columns[position(active.columns, name, default)] for key, name, default in (
        ("impact", "Analytical impact", 3), ("treatment", "Current treatment", 4),
        ("status", "Status", len(active.columns) - 1))}
    entries = {name: entry for name, entry, _ in new}
    for issue_id, decision in [*issues.items(), *entries.items()]:
        issue = by_id.get(issue_id)
        qid = ids[issue_id]
        values = {judged[k]: fill(decision[k]) for k in judged if decision.get(k)}
        if decision.get("check") is not None:
            citation = _citation(root, decision["check"])
            treatment = judged["treatment"]
            line_index = found[issue_id][0] if issue_id in found else revised.get(issue_id) if issue is None else (
                recorded[issue["key"]][0] if issue["key"] in recorded else None)
            current = values.get(treatment)
            if current is None and line_index is not None:
                cells = _cells(quality[line_index])
                at = active.column(treatment)
                current = cells[at].replace("\\|", "|") if at < len(cells) else ""  # set() escapes again
            if current is not None and citation not in current:
                values[treatment] = f"{current}; {citation}" if current else citation
        if decision.get("amend") is not None:
            amend = decision["amend"]
            if (not isinstance(amend, dict) or set(amend) != {"observation", "reason"}
                    or not all(isinstance(amend[k], str) and amend[k].strip() for k in amend)):
                raise RecordError(f'{issue_id}: amend needs {{"observation": "<new text>", "reason": "<why>"}}')
            line_index = revised.get(issue_id) if issue is None else (
                recorded[issue["key"]][0] if issue["key"] in recorded else None)
            if line_index is None:
                raise RecordError(f"{issue_id}: amend changes a recorded row's observation; this issue has no row yet")
            plain = lambda text: _cell(text).replace("\\|", "|")  # set() escapes again
            current = _cells(quality[line_index])[observation_at].replace("\\|", "|")
            text, reason = plain(fill(amend["observation"])), plain(fill(amend["reason"]))
            # The same amendment recorded on any day is already there; only a new one chains.
            if not re.match(re.escape(f"{text}; amended ") + "[^:]*" + re.escape(f": {reason}; was: "), current):
                values[active.columns[observation_at]] = f"{text}; amended {day}: {reason}; was: {current}"
                amended.append(qid)
        if issue_id in found:  # a new entry: its row, else a new one without a scan marker or link
            line_index, obj, observation = found[issue_id]
            if line_index is not None:
                rows.append(active.set(line_index, values))
                updated.append(qid)
            else:
                rows.append(active.append({active.columns[id_at]: qid, active.columns[object_at]: obj,
                                           active.columns[observation_at]: observation, **values}))
                added.append(qid)
        elif issue is None:  # a quality-ID key: judgment cells only; the observation stays
            if values:
                rows.append(active.set(revised[issue_id], values))
                updated.append(qid)
        elif issue["key"] in recorded:
            if values:
                line_index = recorded[issue["key"]][0]
                rows.append(active.set(line_index, values))
                updated.append(qid)
        else:
            missing = [k for k in judged if not decision.get(k)]
            if missing:
                raise RecordError(f"{issue_id} needs {', '.join(missing)} for a new quality row")
            examples = ", ".join(json.dumps(e["value"], ensure_ascii=False)[:40] + f" ({e['count']})"
                                 for e in issue["examples"][:3])
            observation = (f"{issue['summary']} ({issue['count']} of {issue['of']})"
                           + (f"; e.g. {examples}" if examples else "")
                           + f"; `{marker}{issue['key']}` scanned {observed_at[issue_id]}")
            column = f", column `{issue['column']}`" if issue["column"] else ""
            obj = decision.get("object") or f"{target['kind']} `{subject}`{column}"
            rows.append(active.append({active.columns[id_at]: qid, active.columns[object_at]: fill(obj),
                                       active.columns[observation_at]: observation, **values}))
            added.append(qid)
        if issue is not None:
            links.set(scan["name"], issue["key"], qid, issue["count"], issue["of"], observed_at[issue_id])
        if bool(decision.get("correction")) != bool(decision.get("change")):
            raise RecordError(f"{issue_id}: give both correction and change, or neither")
        if decision.get("correction"):
            findings = decision.get("findings") or default_findings
            if not findings:
                raise RecordError("a correction needs flags, or findings text saying what stale reported (e.g. 'none')")
            change = fill(decision["change"])
            if issue_id in delta:
                d = delta[issue_id]
                change += f"; rescan {d['before']} -> {d['after']}"
            corrections.append((qid, [day, qid, fill(decision["correction"]), change, fill(findings)]))
    quality_active = quality.copy()
    appended, repeated = [], []
    if corrections:
        table = Table(quality, CORRECTIONS, "foundation/quality.md")
        for qid, cells in corrections:
            if [_cell(c) for c in cells] in [row for _, row in table.rows()]:
                repeated.append(qid)  # already recorded, as when a finished call is run again
                continue
            rows.append(table.append(dict(zip(table.columns, cells))))
            appended.append(qid)
        if appended:
            changed["foundation/quality.md"] = True
    if added or updated:
        changed["foundation/quality.md"] = True

    catalog_result = None
    if decisions.get("catalog"):
        entry = decisions["catalog"]
        if not entry.get("name") or not isinstance(entry.get("cells"), dict) or not entry["cells"]:
            raise RecordError("catalog needs name and cells")
        catalog = files["foundation/catalog.md"] = _load(root, "foundation/catalog.md", "catalog.md")
        table = Table(catalog, DATASETS, "foundation/catalog.md")
        cells = {name: fill(value) for name, value in entry["cells"].items()}
        for name in cells:
            table.column(name)
        named = [(i, row) for i, row in table.rows() if row[0].strip("`") == entry["name"]]
        matches = [i for i, _ in named]
        if len(matches) > 1:
            # A publication's printed catalog_row shares its dataset's name with the canonical view,
            # and cleaning corrects the view, so a single view row among them is the one to set.
            kind = table.column("Kind") if "Kind" in table.columns else None
            views = [i for i, row in named if kind is not None and "view" in row[kind].lower()]
            if len(views) != 1:
                raise RecordError(f"foundation/catalog.md: several rows are named {entry['name']}")
            matches = views
        if matches:
            rows.append(table.set(matches[0], cells))
            catalog_result = f"updated {entry['name']}"
        else:
            rows.append(table.append({table.columns[0]: f"`{entry['name']}`", **cells}))
            catalog_result = f"added {entry['name']}"
        changed["foundation/catalog.md"] = True

    flag_statuses, batches = {}, {}
    provenance = _load_provenance(root) if flags else None
    for flag in flags:
        batches.setdefault(flag["investigation"], []).append({"result": flag["result"], "reason": fill(flag["reason"])})
    for investigation, batch in batches.items():
        try:
            preview = provenance.flag_findings(root, investigation, batch, check=True)
        except (ValueError, OSError) as error:
            raise RecordError(str(error)) from error
        rows.extend(preview.get("rows", []))
        for flag in preview["flags"]:
            flag_statuses[investigation, flag["result"]] = flag["status"]
        # Keep the output shape for flags already present, without rewriting the records.
        if preview["unchanged"]:
            state_rows = provenance.finding_rows(root / "investigations" / investigation / "state.md")
            for result in preview["unchanged"]:
                status = _cells(state_rows[result][0])[2]
                flag_statuses[investigation, result] = status
    flagged = [{"investigation": f["investigation"], "result": f["result"],
                "status": flag_statuses[f["investigation"], f["result"]]} for f in flags]

    versions = {relative: "\n".join(files[relative]) + "\n" for relative in changed}
    if links.changed():
        versions["foundation/quality.json"] = links.text()
    active_text = "\n".join(quality_active) + "\n"
    for text in [*versions.values(), active_text]:
        text.encode("utf-8")

    written, phases, partials, flagged_investigations = [], [], {}, []
    def prepare(relative, text):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        partial = path.with_name(path.name + ".tmp")
        partials[relative] = partial
        partial.write_text(text, encoding="utf-8")
        return partial

    def replace(relative, partial):
        os.replace(partial, root / relative)
        partials.pop(relative, None)
        if relative not in written:
            written.append(relative)

    if not dry_run:
        try:
            phase_a = {"foundation/quality.json": versions["foundation/quality.json"]} \
                if "foundation/quality.json" in versions else {}
            if "foundation/quality.md" in changed:
                phase_a["foundation/quality.md"] = active_text
            if "foundation/catalog.md" in changed:
                phase_a["foundation/catalog.md"] = versions["foundation/catalog.md"]
            for relative, partial in [(r, prepare(r, text)) for r, text in phase_a.items()]:
                replace(relative, partial)
            phases.append("A")
            for investigation, batch in batches.items():
                outcome = provenance.flag_findings(root, investigation, batch)
                flagged_investigations.append(investigation)
                if outcome["flags"]:
                    written += [f"investigations/{investigation}/findings.json", f"investigations/{investigation}/state.md"]
            phases.append("B")
            if appended:
                relative = "foundation/quality.md"
                replace(relative, prepare(relative, versions[relative]))
            phases.append("C")
        except (OSError, ValueError) as error:
            for partial in partials.values():  # a partial quality.md quotes source values
                partial.unlink(missing_ok=True)
            for path in getattr(error, "replaced", []):
                relative = Path(path).relative_to(root).as_posix()
                if relative not in written:
                    written.append(relative)
            failure = RecordError(f"{error}; investigations already flagged: "
                                  + (", ".join(flagged_investigations) or "none"))
            failure.phases, failure.written = phases, written
            raise failure from error
    result = {"quality_ids": {k: ids[k] for k in [*issues, *entries]}, "added": added, "updated": updated,
              "corrections": appended, "catalog": catalog_result,
              "flags": flagged, "written": written}
    if amended:
        result["amended"] = amended
    if repeated:
        result["corrections_unchanged"] = repeated
    if dry_run:
        result["rows"] = rows
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("root", help="workbench root")
    parser.add_argument("scan", help="scan name: foundation/scans/<scan>.json")
    parser.add_argument("--dry-run", action="store_true", help="print the rows that would change; write nothing")
    args = parser.parse_args(argv)
    try:
        decisions = json.load(sys.stdin)
        if not isinstance(decisions, dict):
            raise RecordError("decisions must be a JSON object")
        result = record(args.root, args.scan, decisions, dry_run=args.dry_run)
    except (RecordError, ValueError, KeyError, OSError) as error:
        print(json.dumps({"error": f"{type(error).__name__}: {error}",
                          "phases": getattr(error, "phases", []),
                          "written": getattr(error, "written", [])}), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
