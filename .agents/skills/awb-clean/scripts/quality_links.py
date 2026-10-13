"""Scan links beside the Markdown quality record; legacy prose is read only for backfill."""

import hashlib
import json
import re
from pathlib import Path

SCHEMA = "awb-quality-links/1"
ACTIVE = "## Active limitations and issues"
MARKER = re.compile(r"`([A-Za-z0-9][A-Za-z0-9._@-]*)#([^`]+)`")


def link_key(scan, key):
    return hashlib.sha256(f"{scan}\n{key}".encode("utf-8")).hexdigest()


def _cells(line):
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


class ActiveRows:
    """Index Active rows by Markdown ID, refusing ambiguous IDs or scan markers."""

    def __init__(self, lines):
        self.rows, self.markers, self.columns = {}, {}, []
        start = next((i for i, line in enumerate(lines) if line.strip() == ACTIVE), None)
        if start is None:
            return
        index = start + 1
        while index < len(lines) and not lines[index].strip().startswith("|"):
            if lines[index].startswith("#"):
                return
            index += 1
        if index + 1 >= len(lines):
            return
        self.columns = _cells(lines[index])
        id_at = self.column("ID")
        for i in range(index + 2, len(lines)):
            if not lines[i].strip().startswith("|"):
                break
            cells = _cells(lines[i])
            if id_at >= len(cells):
                raise ValueError("foundation/quality.md: row lacks its ID cell")
            qid = cells[id_at]
            if qid in self.rows:
                raise ValueError(f"foundation/quality.md: duplicate ID {qid}")
            self.rows[qid] = (i, cells, lines[i].replace("\\|", "|"))
            for scan, key in set(MARKER.findall(lines[i].replace("\\|", "|"))):
                if (scan, key) in self.markers:
                    raise ValueError(f"foundation/quality.md: marker `{scan}#{key}` appears on two rows")
                self.markers[scan, key] = qid

    def column(self, name):
        if name not in self.columns:
            raise ValueError(f"foundation/quality.md: table lacks the column '{name}'")
        return self.columns.index(name)


class QualityLinks:
    def __init__(self, root, lines):
        self.active = ActiveRows(lines)
        path = Path(root) / "foundation/quality.json"
        if path.exists():
            self.document = json.loads(path.read_text(encoding="utf-8"))
            if self.document.get("schema") != SCHEMA or not isinstance(self.document.get("links"), dict):
                raise ValueError(f"foundation/quality.json: expected {SCHEMA}")
        else:
            self.document = {"schema": SCHEMA, "links": {}}
            for (scan, key), qid in self.active.markers.items():
                _, cells, _ = self.active.rows[qid]
                observation = cells[self.active.column("Observation and evidence")]
                count = re.search(r"\((\d+) of (\d+)\)", observation)
                observed = re.search(r"`" + re.escape(f"{scan}#{key}")
                                     + r"`(?: scanned| in \[scan\]\([^)]*\)) (\d{4}-\d{2}-\d{2})",
                                     observation.replace("\\|", "|"))
                self.set(scan, key, qid, int(count[1]) if count else None,
                         int(count[2]) if count else None, observed[1] if observed else None)

    def get(self, scan, key):
        link = self.document["links"].get(link_key(scan, key))
        if not link or link.get("scan") != scan:
            return None
        row = self.active.rows.get(link.get("id"))
        if not row or f"`{scan}#{key}`" not in row[2]:
            return None
        return link

    def discard(self, scan, key):
        self.document["links"].pop(link_key(scan, key), None)

    def set(self, scan, key, qid, count, of, observed_at):
        self.document["links"][link_key(scan, key)] = {
            "id": qid, "scan": scan, "recorded_count": count, "recorded_of": of,
            "observed_at": observed_at}

    def text(self):
        return json.dumps(self.document, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
