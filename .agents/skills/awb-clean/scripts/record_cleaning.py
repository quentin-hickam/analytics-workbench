#!/usr/bin/env python3
"""Write the records of one cleaning pass in one call: quality rows, catalog cells, and flagged findings.

Run with Python 3.10+ (standard library only):
    record_cleaning.py PROJECT_ROOT SCAN_NAME [--dry-run] < decisions.json
SCAN_NAME names foundation/scans/<SCAN_NAME>.json written by scan_dataset.py. Decisions on stdin:
    {"date": "YYYY-MM-DD",                                        optional, default today
     "issues": {"S1": {"impact", "treatment", "status",           judgment columns, required for a new row
                       "correction", "change",                    both or neither: a correction row
                       "findings", "object"}},                    optional overrides
     "findings": "...",                                           correction rows' findings when no flags
     "flags": [{"investigation", "result", "reason"}],            findings to flag
     "catalog": {"name", "cells": {column: text}}}                catalog cells to set
Text may name an issue as {S1}; it becomes the issue's quality ID.

Quality issue rows get the next ID, the scan's counts and examples, and the marker
`<scan>#<key>` with its scan date; later scans use the marker to report the issue as recorded. An
issue already recorded has its judgment cells updated instead, and its observation takes this
scan's count and date, so later scans compare with the reopened state. Correction rows carry the rescan's before and after
counts. A flag sets the finding's status to `revalidation-needed (was <status>)`, adds the reason,
and updates `Last updated`. Everything is checked before any file is written; --dry-run prints the
rows that would change and writes nothing. Prints compact JSON.
"""

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parents[2] / "awb-init/assets/workbench/foundation"
ACTIVE = "## Active limitations and issues"
CORRECTIONS = "## Correction record"
DATASETS = "## Published datasets and views"
FINDINGS = "## Current findings"


class RecordError(ValueError):
    pass


def _cells(line):
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def _row(cells):
    return "| " + " | ".join(cells) + " |"


def _cell(text):
    return re.sub(r"\s*\n\s*", " ", str(text)).replace("|", r"\|").strip()


class Table:
    """The first Markdown table under a heading, edited in place within the file's lines."""

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
        self.lines, self.path, self.header = lines, path, index
        self.columns = _cells(lines[index])
        self.end = index + 2
        while self.end < len(lines) and lines[self.end].strip().startswith("|"):
            self.end += 1

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


def _next_ids(table):
    """Yield new IDs continuing the table's prefix and numbering, Q-001 by default."""
    found = [re.fullmatch(r"([A-Za-z]+-?)(\d+)", cells[0]) for _, cells in table.rows()]
    found = [m for m in found if m]
    prefix = Counter(m.group(1) for m in found).most_common(1)[0][0] if found else "Q-"
    width = max((len(m.group(2)) for m in found), default=3)
    number = max((int(m.group(2)) for m in found), default=0)
    while True:
        number += 1
        yield f"{prefix}{number:0{width}d}"


def _fill(text, ids):
    def replace(match):
        if match.group(1) not in ids:
            raise RecordError(f"{{{match.group(1)}}} names no issue recorded in this call or earlier")
        return ids[match.group(1)]
    return re.sub(r"\{(S\d+)\}", replace, str(text))


def record(project_root, scan_name, decisions, *, dry_run=False, today=None):
    """Apply DECISIONS for scan SCAN_NAME; return the compact result. Writes nothing on error."""
    root = Path(project_root).resolve()
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
    delta = {d["id"]: d for d in (scan.get("delta") or {}).get("issues", [])}
    target = scan["target"]
    subject = target["path"] or scan["name"]

    files, changed = {}, {}
    quality = files["foundation/quality.md"] = _load(root, "foundation/quality.md", "quality.md")
    active = Table(quality, ACTIVE, "foundation/quality.md")
    recorded = {}
    for line_index, cells in active.rows():
        for key in re.findall(r"`" + re.escape(marker) + r"([^`]+)`", quality[line_index]):
            recorded[key.replace("\\|", "|")] = (line_index, cells[0])
    issues = decisions.get("issues") or {}
    unknown = sorted(set(issues) - set(by_id))
    if unknown:
        raise RecordError(f"issues not in the scan: {', '.join(unknown)}")

    # Allocate IDs first so {S1} placeholders resolve anywhere in the decisions.
    ids, new_ids = {}, _next_ids(active)
    for issue_id in issues:
        key = by_id[issue_id]["key"]
        ids[issue_id] = recorded[key][1] if key in recorded else next(new_ids)
    for issue in scan["issues"] + baseline:
        if issue.get("recorded") and issue["id"] not in ids:
            ids[issue["id"]] = issue["recorded"]["id"]

    flags = decisions.get("flags") or []
    by_investigation = {}
    for flag in flags:
        if not all(flag.get(k) for k in ("investigation", "result", "reason")):
            raise RecordError("each flag needs investigation, result, and reason")
        by_investigation.setdefault(flag["investigation"], []).append(flag["result"])
    default_findings = ("; ".join(f"{inv}: {', '.join(results)}" for inv, results in by_investigation.items())
                        or decisions.get("findings"))

    added, updated, corrections, rows = [], [], [], []
    judged = {"impact": "Analytical impact", "treatment": "Current treatment", "status": "Status"}
    for issue_id, decision in issues.items():
        issue = by_id[issue_id]
        qid = ids[issue_id]
        values = {judged[k]: _fill(decision[k], ids) for k in judged if decision.get(k)}
        if issue["key"] in recorded:
            if values:
                line_index = recorded[issue["key"]][0]
                observation = _cells(quality[line_index])[2]
                if f"`{marker}" in observation:  # a reopened issue records this scan's count and date
                    observation = re.sub(r"\(\d+ of \d+\)", f"({issue['count']} of {issue['of']})", observation, count=1)
                    # The date follows the marker: "scanned <date>", or "in [scan](scans/...) <date>" in older rows.
                    observation = re.sub(r"(`" + re.escape(marker) + r"[^`]+`(?: scanned| in \[scan\]\([^)]*\))) \d{4}-\d{2}-\d{2}",
                                         rf"\g<1> {scan['scanned_at'][:10]}", observation, count=1)
                    values[active.columns[2]] = observation.replace("\\|", "|")
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
                           + f"; `{marker}{issue['key']}` scanned {scan['scanned_at'][:10]}")
            column = f", column `{issue['column']}`" if issue["column"] else ""
            obj = decision.get("object") or f"{target['kind']} `{subject}`{column}"
            rows.append(active.append({active.columns[0]: qid, active.columns[1]: _fill(obj, ids),
                                       active.columns[2]: observation, **values}))
            added.append(qid)
        if bool(decision.get("correction")) != bool(decision.get("change")):
            raise RecordError(f"{issue_id}: give both correction and change, or neither")
        if decision.get("correction"):
            findings = decision.get("findings") or default_findings
            if not findings:
                raise RecordError("a correction needs flags, or findings text saying what stale reported (e.g. 'none')")
            change = _fill(decision["change"], ids)
            if issue_id in delta:
                d = delta[issue_id]
                change += f"; rescan {d['before']} -> {d['after']}"
            corrections.append((qid, [day, qid, _fill(decision["correction"], ids), change, _fill(findings, ids)]))
    if corrections:
        table = Table(quality, CORRECTIONS, "foundation/quality.md")
        for qid, cells in corrections:
            rows.append(table.append(dict(zip(table.columns, cells))))
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
        cells = {name: _fill(value, ids) for name, value in entry["cells"].items()}
        for name in cells:
            table.column(name)
        matches = [i for i, row in table.rows() if row[0].strip("`") == entry["name"]]
        if len(matches) > 1:
            raise RecordError(f"foundation/catalog.md: several rows are named {entry['name']}")
        if matches:
            rows.append(table.set(matches[0], cells))
            catalog_result = f"updated {entry['name']}"
        else:
            rows.append(table.append({table.columns[0]: f"`{entry['name']}`", **cells}))
            catalog_result = f"added {entry['name']}"
        changed["foundation/catalog.md"] = True

    flagged = []
    for flag in flags:
        relative = f"investigations/{flag['investigation']}/state.md"
        lines = files.setdefault(relative, _load(root, relative))
        table = Table(lines, FINDINGS, relative)
        result = flag["result"]
        evidence, status_at = table.column("Evidence"), table.column("Status")
        reason_at = table.column("Revalidation reason or caveat")
        matches = [(i, row) for i, row in table.rows()
                   if f"evidence/{result}.json" in row[evidence] or f"[{result}]" in row[evidence]
                   or row[0] == result]
        if len(matches) != 1:
            raise RecordError(f"{relative}: {len(matches)} findings match {result}")
        line_index, row = matches[0]
        status = row[status_at]
        if not status.startswith("revalidation-needed"):
            status = f"revalidation-needed (was {status})" if status else "revalidation-needed"
        reason = _fill(flag["reason"], ids)
        existing = row[reason_at] if reason_at < len(row) else ""
        if existing and reason not in existing:
            reason = f"{existing}; {reason}"
        rows.append(table.set(line_index, {"Status": status, "Revalidation reason or caveat": reason}))
        for i, line in enumerate(lines):
            if line.startswith("Last updated:"):
                lines[i] = f"Last updated: {day}"
                break
        changed[relative] = True
        flagged.append({"investigation": flag["investigation"], "result": result, "status": status})

    written = []
    if not dry_run:
        for relative in changed:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            partial = path.with_name(path.name + ".tmp")
            partial.write_text("\n".join(files[relative]) + "\n", encoding="utf-8")
            os.replace(partial, path)
            written.append(relative)
    result = {"quality_ids": {k: ids[k] for k in issues}, "added": added, "updated": updated,
              "corrections": [qid for qid, _ in corrections], "catalog": catalog_result,
              "flags": flagged, "written": written}
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
        print(json.dumps({"error": f"{type(error).__name__}: {error}", "written": []}), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
