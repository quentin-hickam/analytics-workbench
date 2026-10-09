"""Write and check the chart data of an analytics workbench package.

Copy this file to `src/packaging/charts.py`; do not import it from the skill folder.
`write_charts` needs pandas; `check_charts` needs only the standard library.

A package's `charts/` directory holds one CSV per chart that `findings.md` specifies, named
`chart-N.csv` in the order the specifications appear, each holding a header row of display
names and the plotted values, nothing else. M365 Copilot draws each chart from its file.
"""

import os
import re
from pathlib import Path

_SPEC = re.compile(r"\*\*Chart (\d+)\.\*\*")
_FILE = re.compile(r"chart-([1-9]\d*)\.csv")
# An underscore or a dot between letters marks a column name or code, not a display name.
_IDENTIFIER = re.compile(r"[A-Za-z0-9]_[A-Za-z0-9]|[A-Za-z]\.[A-Za-z]")


def _check_frame(number, frame):
    import pandas as pd

    if not isinstance(frame, pd.DataFrame):
        raise TypeError(f"Chart {number} is not a DataFrame")
    if frame.empty:
        raise ValueError(f"Chart {number} has no rows")
    headers = list(frame.columns)
    if not all(isinstance(header, str) and header.strip() for header in headers):
        raise ValueError(f"Chart {number} has a blank or non-text header")
    if len(set(headers)) != len(headers):
        raise ValueError(f"Chart {number} repeats a header")
    for header in headers:
        if _IDENTIFIER.search(header):
            raise ValueError(f"Chart {number} header is not a display name: {header}")


def write_charts(charts_dir: str | os.PathLike, charts: list) -> list[Path]:
    """Replace the directory's chart files with chart-1.csv, chart-2.csv, ... in list order."""
    if not charts:
        raise ValueError("No charts: a package without charts has no charts directory")
    for number, frame in enumerate(charts, start=1):
        _check_frame(number, frame)
    directory = Path(charts_dir)
    directory.mkdir(parents=True, exist_ok=True)
    for stale in directory.iterdir():
        if _FILE.fullmatch(stale.name):
            stale.unlink()
    paths = []
    for number, frame in enumerate(charts, start=1):
        path = directory / f"chart-{number}.csv"
        frame.to_csv(path, index=False, lineterminator="\n")
        paths.append(path)
    return paths


def check_charts(findings_path: str | os.PathLike, charts_dir: str | os.PathLike) -> list[dict]:
    """Match the chart specifications in findings.md with the chart files."""
    numbers = [int(match.group(1)) for match in _SPEC.finditer(
        Path(findings_path).read_text(encoding="utf-8"))]
    rows = []
    for position, number in enumerate(numbers, start=1):
        if number != position:
            rows.append({"chart": f"Chart {number}",
                         "problem": f"specification {position} is numbered {number}"})
    directory = Path(charts_dir)
    files = {}
    if directory.is_dir():
        for path in directory.iterdir():
            match = _FILE.fullmatch(path.name)
            if match:
                files[int(match.group(1))] = path
            else:
                rows.append({"chart": path.name, "problem": "not a chart file"})
    specified = set(numbers)
    for number in sorted(specified - files.keys()):
        rows.append({"chart": f"Chart {number}", "problem": "no chart file for this specification"})
    for number in sorted(files.keys() - specified):
        rows.append({"chart": f"Chart {number}", "problem": "chart file has no specification in findings"})
    for number in sorted(specified & files.keys()):
        with files[number].open(encoding="utf-8") as stream:
            lines = [line for line, _ in zip(stream, range(2)) if line.strip()]
        if len(lines) < 2:
            rows.append({"chart": f"Chart {number}", "problem": "chart file has no data rows"})
    return rows
