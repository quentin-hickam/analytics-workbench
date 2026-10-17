# Kept cases:
# test_write_charts_numbers_files_in_order_and_writes_values: files are chart-1..N.csv in list order; headers and values land as given, an empty value as an empty field.
# test_write_charts_replaces_stale_chart_files: a rewrite with fewer charts removes the extra chart file and leaves other files alone.
# test_write_charts_without_charts_removes_them: an empty list removes every chart file, then the directory when nothing else is in it.
# test_write_charts_rejects_bad_input: a chart without rows, an identifier header, a blank header, or a repeated header raises and writes nothing.
# test_check_charts_clean_package_returns_no_rows: specifications and chart files match one to one.
# test_check_charts_reports_each_mismatch: misnumbered, missing, unspecified, foreign, and empty files are one row each.
# test_check_charts_spec_continuing_a_block: a specification directly under a bullet or paragraph line renders inside that block; the row says to leave a blank line.
# test_check_charts_without_directory: specifications with no charts directory each report it; no specifications and no directory is clean.
# test_charts_without_pandas: the module loads, writes, and checks charts when pandas cannot be imported.
# test_check_charts_compares_headers_as_the_data_line_renders: a header holding CO₂ matches a **Data:** role naming CO₂, both NFKC-normalized as the line renders; a header no role names, or a role no header holds, is still a row.
# test_a_blank_line_inside_a_chart_spec_names_the_chart: field-named bullets after a blank line ended a chart's fields count as slide bullets, and the outline's bullet-count row names the chart; the same fields kept together give no row.

import importlib.util
import sys
from pathlib import Path

import pytest


ASSET = Path(__file__).resolve().parents[1] / ".agents/skills/awb-package/assets/awb_draft.py"
spec = importlib.util.spec_from_file_location("awb_draft_charts", ASSET)
charts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(charts)

LATE = (["Region", "Closed late (%)"], [["North", "21.0"], ["East", "18.0"], ["West", ""]])
TREND = (["Month", "Cases"], [["Jan", "1204"], ["Feb", "1310"]])


DATA = {1: "category: Region; value: Closed late (%)", 2: "category: Month; value: Cases"}


def findings(tmp_path, *numbers):
    path = tmp_path / "findings.md"
    path.write_text("".join(f"### Finding\n\n**Chart {n}.** Horizontal bar: late share by region\n"
                            f"- **Data:** {DATA.get(n, 'category: Region; value: Cases')}\n\n"
                            for n in numbers), encoding="utf-8")
    return path


def test_write_charts_numbers_files_in_order_and_writes_values(tmp_path):
    paths = charts.write_charts(tmp_path / "charts", [LATE, TREND])
    assert [path.name for path in paths] == ["chart-1.csv", "chart-2.csv"]
    assert paths[0].read_text() == "Region,Closed late (%)\nNorth,21.0\nEast,18.0\nWest,\n"
    assert paths[1].read_text() == "Month,Cases\nJan,1204\nFeb,1310\n"


def test_write_charts_replaces_stale_chart_files(tmp_path):
    charts.write_charts(tmp_path / "charts", [LATE, TREND])
    (tmp_path / "charts/notes.txt").write_text("keep")
    charts.write_charts(tmp_path / "charts", [TREND])
    assert sorted(path.name for path in (tmp_path / "charts").iterdir()) == ["chart-1.csv", "notes.txt"]
    assert (tmp_path / "charts/chart-1.csv").read_text().startswith("Month,Cases\n")


def test_write_charts_without_charts_removes_them(tmp_path):
    charts.write_charts(tmp_path / "charts", [LATE, TREND])
    (tmp_path / "charts/notes.txt").write_text("keep")
    assert charts.write_charts(tmp_path / "charts", []) == []
    assert [path.name for path in (tmp_path / "charts").iterdir()] == ["notes.txt"]
    (tmp_path / "charts/notes.txt").unlink()
    charts.write_charts(tmp_path / "charts", [LATE])
    charts.write_charts(tmp_path / "charts", [])
    assert not (tmp_path / "charts").exists()


@pytest.mark.parametrize("frames, message", [
    ([LATE, (["Month"], [])], "Chart 2 has no rows"),
    ([(["region_code"], [["W"]])], "not a display name: region_code"),
    ([([" "], [["W"]])], "blank or non-text header"),
    ([(["Cases", "Cases"], [["1", "2"]])], "repeats a header"),
])
def test_write_charts_rejects_bad_input(tmp_path, frames, message):
    with pytest.raises(ValueError, match=message):
        charts.write_charts(tmp_path / "charts", frames)
    assert list(tmp_path.iterdir()) == []


def test_check_charts_clean_package_returns_no_rows(tmp_path):
    charts.write_charts(tmp_path / "charts", [LATE, TREND])
    assert charts.check_charts(findings(tmp_path, 1, 2), tmp_path / "charts") == []


def test_check_charts_reports_each_mismatch(tmp_path):
    directory = tmp_path / "charts"
    directory.mkdir()
    (directory / "chart-1.csv").write_text("Region,Closed late (%)\n")
    (directory / "chart-3.csv").write_text("Region,Cases\nWest,4\n")
    (directory / "chart-4.csv").write_text("Region,Cases\nWest,4\n")
    (directory / "late.png").write_bytes(b"")
    assert charts.check_charts(findings(tmp_path, 1, 3, 2), directory) == [
        {"chart": "Chart 3", "problem": "specification 2 is numbered 3"},
        {"chart": "Chart 2", "problem": "specification 3 is numbered 2"},
        {"chart": "late.png", "problem": "not a chart file"},
        {"chart": "Chart 2", "problem": "no chart file for this specification"},
        {"chart": "Chart 4", "problem": "chart file has no specification in findings"},
        {"chart": "Chart 1", "problem": "chart file has no data rows"},
    ]


@pytest.mark.parametrize("above", ["- West 12%\n- East 8%", "West had 12%."])
def test_check_charts_spec_continuing_a_block(tmp_path, above):
    # Round 4 (Opus 1): CommonMark renders the line inside the bullet or paragraph above it, so it is no
    # specification, and the row says how to make it one.
    charts.write_charts(tmp_path / "charts", [LATE])
    path = tmp_path / "findings.md"
    path.write_text(f"### H\n\n{above}\n**Chart 1.** Horizontal bar: rate by region\n- **Data:** category: Region; value: Closed late (%)\n")
    assert charts.check_charts(path, tmp_path / "charts") == [{"chart": "Chart 1", "problem": (
        "Chart 1's specification continues the paragraph or bullet above it; leave a blank line before it")}]
    path.write_text(f"### H\n\n{above}\n\n**Chart 1.** Horizontal bar: rate by region\n- **Data:** category: Region; value: Closed late (%)\n")
    assert charts.check_charts(path, tmp_path / "charts") == []


def test_check_charts_without_directory(tmp_path):
    assert charts.check_charts(findings(tmp_path, 1, 2), tmp_path / "charts") == [
        {"chart": "Chart 1", "problem": "no chart file for this specification"},
        {"chart": "Chart 2", "problem": "no chart file for this specification"},
    ]
    assert charts.check_charts(findings(tmp_path), tmp_path / "charts") == []


def test_charts_without_pandas(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "pandas", None)
    bare = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bare)
    bare.write_charts(tmp_path / "charts", [LATE])
    assert bare.check_charts(findings(tmp_path, 1), tmp_path / "charts") == []


def test_check_charts_compares_headers_as_the_data_line_renders(tmp_path):
    # The issue's probe: "CO₂" in the file never matched, since only the **Data:** line was NFKC-normalized.
    charts.write_charts(tmp_path / "charts", [(["Country", "Change in CO₂ (Mt)"], [["China", "12.5"]])])
    path = tmp_path / "findings.md"
    path.write_text("### H\n\n**Chart 1.** Horizontal bar: change by country\n"
                    "- **Data:** category: Country; value: Change in CO₂ (Mt)\n", encoding="utf-8")
    assert charts.check_charts(path, tmp_path / "charts") == []
    path.write_text("### H\n\n**Chart 1.** Horizontal bar: change by country\n"
                    "- **Data:** category: Country; value: Change in CO2 (Mt)\n", encoding="utf-8")
    assert charts.check_charts(path, tmp_path / "charts") == []  # CO₂ renders as CO2, so the plain spelling matches
    path.write_text("### H\n\n**Chart 1.** Horizontal bar: change by country\n"
                    "- **Data:** category: Country; value: Change in CH₄ (Mt)\n", encoding="utf-8")
    assert charts.check_charts(path, tmp_path / "charts") == [
        {"chart": "Chart 1", "problem": "chart-1.csv has no column 'Change in CH4 (Mt)', which **Data:** names"},
        {"chart": "Chart 1", "problem": "chart-1.csv column 'Change in CO₂ (Mt)' is named by no **Data:** role; "
                                        "name it by a role a Horizontal bar takes (category, value, series), or "
                                        "export the chart without it; if it holds interval bounds, a Horizontal bar "
                                        "draws none, so use a Bar with intervals"}]


FIELDS = ("- **Highlight:** West\n- **Axis:** percent, zero baseline\n- **Source:** claims extract, 2026\n"
          "- **Caveat:** none\n- **Alt text:** West closes most claims late.\n")


def test_a_blank_line_inside_a_chart_spec_names_the_chart(tmp_path):
    path = tmp_path / "findings.md"
    slide = ("# Claims\n\nOperations leads\n\n## Findings\n\n### West closes most claims late\n\n- West led.\n\n"
             "**Chart 1.** Horizontal bar: late share by region\n- **Data:** category: Region; value: Closed late (%)\n"
             "{gap}" + FIELDS + "\n**Notes:** West leads.\n")
    path.write_text(slide.format(gap="\n"), encoding="utf-8")
    rows = [row for row in charts.outline_problems(path) if "bullets" in row["problem"]]
    assert rows == [{"slide": "West closes most claims late", "line": 18, "problem": (
        "6 bullets; keep it to 5 and move the rest to another slide or into the notes; 5 of them open with a chart "
        "field name after Chart 1's fields ended, so they count as slide bullets: keep its fields together, with "
        "no blank line between them")}]
    path.write_text(slide.format(gap=""), encoding="utf-8")
    assert [row for row in charts.outline_problems(path) if "bullets" in row["problem"]] == []
    assert charts.read_outline(path)["slides"][0]["field_bullets"] == []
