"""Scan links beside the Markdown quality record; a row's prose is read only to build a missing link."""

import hashlib
import json
import re
from pathlib import Path

SCHEMA = "awb-quality-links/1"
ACTIVE = "## Active limitations and issues"
OBJECT, OBSERVATION = "Affected source or catalog object", "Observation and evidence"
MARKER = re.compile(r"`([A-Za-z0-9][A-Za-z0-9._@-]*)#([^`]+)`")


def position(columns, name, default):
    """The column headed `name`, else the template's position for it."""
    return columns.index(name) if name in columns else default


def link_key(scan, key):
    return hashlib.sha256(f"{scan}\n{key}".encode("utf-8")).hexdigest()


def _cells(line):
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def _cell(cells, at):
    return cells[at] if 0 <= at < len(cells) else ""


class ActiveRows:
    """Active rows by ID and by the scan markers in their observation cells.

    A column is found by its template header, else by the template's position, so renamed and
    reordered tables both work. Repeated IDs or markers are kept, not refused: they only stop
    the links they touch from counting.
    """

    def __init__(self, lines):
        self.lines, self.columns, self.ids, self.markers = lines, [], {}, {}
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
        self.id_at, self.observation_at = position(self.columns, "ID", 0), position(self.columns, OBSERVATION, 2)
        self.status_at = position(self.columns, "Status", len(self.columns) - 1)
        for i in range(index + 2, len(lines)):
            if not lines[i].strip().startswith("|"):
                break
            cells = _cells(lines[i])
            self.ids.setdefault(_cell(cells, self.id_at), []).append(i)
            for marker in set(MARKER.findall(self.observation(i))):
                self.markers.setdefault(marker, []).append(i)

    def observation(self, line):
        return _cell(_cells(self.lines[line]), self.observation_at).replace("\\|", "|")

    def qid(self, line):
        return _cell(_cells(self.lines[line]), self.id_at)

    def status(self, line):
        return _cell(_cells(self.lines[line]), self.status_at)

    def row(self, qid):
        """The one row with this ID, else None."""
        lines = self.ids.get(qid, []) if qid else []
        return lines[0] if len(lines) == 1 else None


class QualityLinks:
    def __init__(self, root, lines):
        self.active = ActiveRows(lines)
        self.path = Path(root) / "foundation/quality.json"
        self.saved = self.path.read_text(encoding="utf-8") if self.path.exists() else None
        if self.saved is not None:
            self.document = json.loads(self.saved)
            if self.document.get("schema") != SCHEMA or not isinstance(self.document.get("links"), dict):
                raise ValueError(f"foundation/quality.json: expected {SCHEMA}")
        else:
            self.document = {"schema": SCHEMA, "links": {}}
            for scan, key in self.active.markers:
                if self.marked(scan, key) is not None:
                    self._from_row(scan, key)

    def marked(self, scan, key):
        """The one row carrying this marker, when its ID is also unique, else None."""
        lines = self.active.markers.get((scan, key), [])
        if len(lines) == 1 and self.active.row(self.active.qid(lines[0])) == lines[0]:
            return lines[0]
        return None

    def _from_row(self, scan, key):
        """Build a link from the row's observation prose: its count, total, and marker date."""
        line = self.marked(scan, key)
        observation = self.active.observation(line)
        count = re.search(r"\((\d+) of (\d+)\)", observation)
        observed = re.search(r"`" + re.escape(f"{scan}#{key}")
                             + r"`(?: scanned| in \[scan\]\([^)]*\)) (\d{4}-\d{2}-\d{2})", observation)
        self.set(scan, key, self.active.qid(line), int(count[1]) if count else None,
                 int(count[2]) if count else None, observed[1] if observed else None)
        return self.document["links"][link_key(scan, key)]

    def resolve(self, scan, key):
        """(line, link) for an issue's row, else None.

        A stored link counts while exactly one row has its ID and that row carries the marker. With
        none, a marker on exactly one row with a unique ID is relinked from that row's prose.
        """
        link = self.document["links"].get(link_key(scan, key))
        if link and link.get("scan") == scan:
            line = self.active.row(link.get("id"))
            if line is not None and line in self.active.markers.get((scan, key), []):
                return line, link
        line = self.marked(scan, key)
        return None if line is None else (line, self._from_row(scan, key))

    def discard(self, scan, key):
        self.document["links"].pop(link_key(scan, key), None)

    def set(self, scan, key, qid, count, of, observed_at):
        self.document["links"][link_key(scan, key)] = {
            "id": qid, "scan": scan, "recorded_count": count, "recorded_of": of,
            "observed_at": observed_at}

    def text(self):
        return json.dumps(self.document, indent=2, sort_keys=True, ensure_ascii=False) + "\n"

    def changed(self):
        """Whether the file on disk differs; a missing file with no links needs no write."""
        if self.saved is None:
            return bool(self.document["links"])
        return self.text() != self.saved
