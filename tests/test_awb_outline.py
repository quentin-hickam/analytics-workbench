# Kept cases:
# test_parse_outline_derives_the_deck: the title slide, one slide per ## section but Findings and per ### finding, with section, headline, bullets and nested bullets, notes, and chart; every chart with its form, comparison, fields, and slide; nothing is written.
# test_parse_outline_reads_as_it_renders: a comment hides a bullet, a fence is no bullet, a chart's fields end at a blank line so a later Caveat bullet stays on the slide, a list-item specification is a chart, a field already given is a bullet, and a wrapped bullet is one bullet, a block quote inside it included; a paragraph back at a bullet's depth after its nested chart joins no field.
# test_outline_problems_clean_deck: a deck following every slide rule has no rows; a 15-word headline and five bullets pass.
# test_outline_problems_rows: each slide rule broken gives its row with slide, line, and problem, a block quote outside a list being a paragraph of its own, as is a paragraph back at a bullet's depth after a deeper item, and the title slide's notes counted too; a deck without its # heading also has its subtitle on no slide, and one without ## Findings has each finding outside it.
# test_chart_data_reads_roles: role: header pairs in order, case-insensitive roles, headers kept whole, colons in a header kept.
# test_check_charts_every_form_passes: a specification in each of the seven forms, its Data line naming that form's roles, and a file with those columns passes.
# test_check_charts_spec_rows: an unknown or missing form, a missing Data line, a malformed entry, a role the form does not take, a repeated single role, a missing needed role, a series with two values, a column the file lacks, and a file column no role names give one row each; an interval role on a form without intervals says only a Bar with intervals draws them, and an unnamed column there says so if it holds interval bounds.
# test_chart_fields_read_past_a_nested_item: an item nested under a field is kept out of the fields and the bullets and reported, and the fields after it still count; a blank line before the nested item changes none of this; a later paragraph in a field is reported; a field-named item back at a shallower depth is a bullet.
# test_check_draft_help_lists_every_chart_row: the check-draft --help epilog names the unnamed-column and field-list chart rows.

import importlib.util
from pathlib import Path

import pytest

ASSET = Path(__file__).resolve().parents[1] / ".agents/skills/awb-package/assets/awb_draft.py"
spec = importlib.util.spec_from_file_location("awb_draft_outline", ASSET)
draft = importlib.util.module_from_spec(spec)
spec.loader.exec_module(draft)

DECK = """# Late claims in the west
Regional operations managers, claims closed in the first half of the year

## Answer

**Headline:** West claims close late four times as often as the east

- The west closed 21% of claims late, the east 5%.
- Staffing the west queue is the decision.

**Notes:** The west rate is the
highest of the four regions.

## Findings

### West claims closed late 21% of the time

- West 21% late, east 5%.
- **Caveat:** March records are incomplete.

**Chart 1.** Bar with intervals: late share by region
- **Data:** category: Region; value: Closed late (%); lower: Lower (%); upper: Upper (%)
- **Highlight:** West
- **Axis:** percent, zero baseline
- **Interval:** 95% interval
- **Source:** the claims team's extract
- **Caveat:** none
- **Alt text:** West 21%, east 5%.

**Notes:** Intervals are wide in the north.

### Late claims rose each month in the west

- Rose from 15% to 21%.
  - January was the lowest month.

**Chart 2.** Line: monthly late share
- **Data:** category: Month; series: Region; value: Closed late (%)

**Notes:** Monthly counts are small.

## How we know

**Headline:** Totals reconcile to the finance ledger

- Claims are counted once.

**Notes:** The ledger is the finance team's.
"""
CSV = {1: "Region,Closed late (%),Lower (%),Upper (%)\nWest,21,18,24\nEast,5,4,6\n",
       2: "Month,Region,Closed late (%)\nJan,West,15\nJan,East,5\nFeb,West,21\nFeb,East,5\n"}


def package(tmp_path, text=DECK, files=CSV):
    path = tmp_path / "findings.md"
    path.write_text(text, encoding="utf-8")
    (tmp_path / "charts").mkdir(exist_ok=True)
    for number, content in files.items():
        (tmp_path / "charts" / f"chart-{number}.csv").write_text(content, encoding="utf-8")
    return path


def test_parse_outline_derives_the_deck(tmp_path):
    path = package(tmp_path)
    before = sorted(p.name for p in tmp_path.rglob("*"))
    outline = draft.read_outline(path)
    assert sorted(p.name for p in tmp_path.rglob("*")) == before
    title = outline["title"]
    assert (title["text"], title["subtitle"], title["notes"]) == (
        "Late claims in the west", "Regional operations managers, claims closed in the first half of the year", None)
    slides = outline["slides"]
    assert [(s["section"], s["finding"], s["headline"], s["chart"]) for s in slides] == [
        ("Answer", False, "West claims close late four times as often as the east", None),
        ("Findings", True, "West claims closed late 21% of the time", 1),
        ("Findings", True, "Late claims rose each month in the west", 2),
        ("How we know", False, "Totals reconcile to the finance ledger", None)]
    assert [b["text"] for b in slides[0]["bullets"]] == [
        "The west closed 21% of claims late, the east 5%.", "Staffing the west queue is the decision."]
    assert slides[0]["notes"] == "The west rate is the highest of the four regions."
    assert [b["text"] for b in slides[1]["bullets"]] == ["West 21% late, east 5%.",
                                                         "Caveat: March records are incomplete."]
    assert slides[2]["bullets"] == [{"line": 34, "text": "Rose from 15% to 21%.",
                                     "sub": ["January was the lowest month."]}]
    assert outline["stray"] == []
    first, second = outline["charts"]
    assert (first["number"], first["form"], first["comparison"], first["slide"], first["line"]) == (
        1, "Bar with intervals", "late share by region", 1, 21)
    assert first["fields"] == {
        "Data": "category: Region; value: Closed late (%); lower: Lower (%); upper: Upper (%)",
        "Highlight": "West", "Axis": "percent, zero baseline", "Interval": "95% interval",
        "Source": "the claims team's extract", "Caveat": "none", "Alt text": "West 21%, east 5%."}
    assert (second["form"], second["slide"], list(second["fields"])) == ("Line", 2, ["Data"])


def test_parse_outline_reads_as_it_renders():
    outline = draft.parse_outline("""# T
Sub

## Answer

**Headline:** H

- Shown <!-- hidden --> bullet
<!--
- Hidden bullet
-->

```
- Code, not a bullet
```

**Chart 1.** Column: counts
- **Data:** category: Month; value: Cases

- **Caveat:** a slide caveat after the blank line
- A bullet that wraps
onto a second line

  > A quote in the bullet

- **Chart 2.** Table: the grid
  - **Data:** column: Month; column: Cases
  - **Data:** a second Data is a bullet

**Notes:** N
""")
    slide = outline["slides"][0]
    assert [b["text"] for b in slide["bullets"]] == [
        "Shown bullet", "Caveat: a slide caveat after the blank line",
        "A bullet that wraps onto a second line A quote in the bullet"]
    assert slide["bullets"][-1]["sub"] == ["Data: a second Data is a bullet"]
    assert [(c["number"], c["form"], c["fields"]) for c in outline["charts"]] == [
        (1, "Column", {"Data": "category: Month; value: Cases"}),
        (2, "Table", {"Data": "column: Month; column: Cases"})]
    assert slide["extra"] == [] and slide["notes"] == "N"
    # A paragraph back at the bullet's depth after a nested chart's fields joins neither the bullet nor a field.
    nested = draft.parse_outline("# T\nSub\n\n## A\n\n- West.\n  - **Chart 1.** Table: grid\n"
                                 "    - **Alt text:** Grid.\n\n  **Caveat:** March.\n")
    slide = nested["slides"][0]
    assert ([b["text"] for b in slide["bullets"]], nested["charts"][0]["fields"], slide["extra"]) == (
        ["West."], {"Alt text": "Grid."}, [{"line": 10, "text": "Caveat: March."}])


def test_outline_problems_clean_deck(tmp_path):
    assert draft.outline_problems(package(tmp_path)) == []
    fifteen = " ".join(["word"] * 14) + " 21%"
    five = "".join(f"- Point {n}.\n" for n in range(5))
    text = DECK.replace("Totals reconcile to the finance ledger", fifteen).replace("- Claims are counted once.\n", five)
    assert draft.outline_problems(package(tmp_path, text)) == []


ANSWER = "## Answer\n\n**Headline:** West claims close late four times as often as the east\n"
NOTES = "**Notes:** The ledger is the finance team's.\n"
LONG = " ".join(["word"] * 15) + " 21%"


@pytest.mark.parametrize("old, new, expected", [
    ("# Late claims in the west\n", "", [("title", 1, "findings.md has no # deck title heading; open it with one "
                                                     "and its subtitle line"),
                                          ("before the deck title", 1, "text before the deck title is on no slide; "
                                                                       "move it onto a slide")]),
    ("Regional operations managers, claims closed in the first half of the year\n", "",
     ("title", 1, "the title slide has no subtitle line under the # heading")),
    ("first half of the year\n", "first half of the year\n\n- A bullet on the title slide\n",
     ("title", 4, "the title slide holds only the # heading, its subtitle line, and notes; move this to a slide")),
    ("# Late claims", "Before the title.\n\n# Late claims",
     ("before the deck title", 1, "text before the deck title is on no slide; move it onto a slide")),
    ("## How we know", "# A second title\n\n## How we know",
     ("a second # heading", 42, "a second # heading; the deck has one title slide, so make this a ## slide or "
                                "remove it")),
    ("## Findings\n", "## Findings\n\nAn introduction.\n",
     ("under Findings before its first finding slide", 16,
      "text under Findings before its first finding slide is on no slide; move it onto a slide")),
    ("## Findings\n\n### West", "### West",
     [(heading, line, "a ### finding slide outside the ## Findings section; move it under ## Findings")
      for heading, line in (("West claims closed late 21% of the time", 14),
                            ("Late claims rose each month in the west", 30))]),
    ("### West claims closed late 21% of the time\n", "### West claims closed late 21% of the time\n\n"
                                                      "**Headline:** West again\n",
     ("West claims closed late 21% of the time", 18, "a finding slide's ### heading is its headline; remove the "
                                                     "**Headline:** line")),
    ("**Headline:** Totals reconcile to the finance ledger\n", "",
     ("How we know", 42, "no **Headline:** line; open the slide with one")),
    ("**Headline:** Totals reconcile to the finance ledger\n",
     "**Headline:** Totals reconcile to the finance ledger\n\n**Headline:** A second\n",
     ("How we know", 46, "2 **Headline:** lines; keep one")),
    ("**Headline:** Totals reconcile to the finance ledger", "**Headline:**",
     ("How we know", 42, "the headline is empty; state the slide's point with its key number")),
    ("Totals reconcile to the finance ledger", LONG, ("How we know", 42, "the headline has 16 words; keep it to 15")),
    ("- Claims are counted once.\n", "".join(f"- Point {n}.\n" for n in range(6)),
     ("How we know", 51, "6 bullets; keep it to 5 and move the rest to another slide or into the notes")),
    ("- Claims are counted once.\n", "- Claims are counted once.\n\n**Chart 3.** Table: a\n\n**Chart 4.** Table: b\n",
     ("How we know", 50, "2 charts; a slide carries at most one")),
    ("- Claims are counted once.\n", "- Claims are counted once.\n\nA loose paragraph.\n",
     ("How we know", 48, "text outside the headline, bullets, chart, and notes; make it a bullet or move it into "
                         "the notes")),
    ("first half of the year\n", "first half of the year\n> Draft for discussion, not for circulation\n",
     ("title", 3, "the title slide holds only the # heading, its subtitle line, and notes; move this to a slide")),
    ("**Headline:** Totals reconcile to the finance ledger\n",
     "**Headline:** Totals reconcile to the finance ledger\n\n> A quoted remark.\n",
     ("How we know", 46, "text outside the headline, bullets, chart, and notes; make it a bullet or move it into "
                         "the notes")),
    (NOTES, NOTES + '\n> "We are always behind in March." Regional manager\n',
     ("How we know", 50, "text outside the headline, bullets, chart, and notes; make it a bullet or move it into "
                         "the notes")),
    (NOTES, NOTES + "\n> **Caveat:** March records are incomplete.\n",
     ("How we know", 50, "text outside the headline, bullets, chart, and notes; make it a bullet or move it into "
                         "the notes")),
    (NOTES, "", ("How we know", 42, "no **Notes:** paragraph; end the slide with one")),
    (NOTES, NOTES + "\n**Notes:** More.\n", ("How we know", 50, "2 **Notes:** paragraphs; merge them into one")),
    (NOTES, NOTES + "\n- A bullet after the notes.\n",
     ("How we know", 50, "text after the **Notes:** paragraph; the notes end the slide")),
    ("first half of the year\n", "first half of the year\n\n**Notes:** Introduce.\n\n**Notes:** More.\n",
     ("title", 6, "2 **Notes:** paragraphs; merge them into one")),
    ("  - January was the lowest month.\n",
     "  - January was the lowest month.\n\n  **Caveat:** March records are incomplete.\n",
     ("Late claims rose each month in the west", 37, "text outside the headline, bullets, chart, and notes; make it a "
                                                     "bullet or move it into the notes")),
    ("- Claims are counted once.\n", "- Claims are counted once.\n  - **Chart 3.** Table: the grid\n"
                                     "    - **Data:** column: Region\n    - **Alt text:** Regional grid.\n\n"
                                     "  **Caveat:** March records are incomplete.\n",
     ("How we know", 51, "text outside the headline, bullets, chart, and notes; make it a bullet or move it into "
                         "the notes")),
])
def test_outline_problems_rows(tmp_path, old, new, expected):
    assert old in DECK
    rows = draft.outline_problems(package(tmp_path, DECK.replace(old, new, 1)))
    assert [(r["slide"], r["line"], r["problem"]) for r in rows] == (expected if isinstance(expected, list)
                                                                     else [expected])


def test_chart_data_reads_roles():
    chart = {"form": "Scatter", "fields": {"Data": "X: Spend ($, thousands); y: Ratio: late to all;  label : Store ;"}}
    assert draft.chart_data(chart) == (
        [("x", "Spend ($, thousands)"), ("y", "Ratio: late to all"), ("label", "Store")], [])


SPECS = {
    "Horizontal bar": ("category: Region; value: Cases; value: Late", "Region,Cases,Late\nWest,4,1\n"),
    "Bar with intervals": ("category: Region; value: Rate; lower: Low; upper: High", "Region,Rate,Low,High\nW,2,1,3\n"),
    "Line": ("category: Month; series: Region; value: Cases", "Month,Region,Cases\nJan,West,4\n"),
    "Column": ("category: Month; value: Cases", "Month,Cases\nJan,4\n"),
    "Stacked bar": ("category: Region; value: Late; value: On time", "Region,Late,On time\nWest,1,3\n"),
    "Scatter": ("x: Spend; y: Late; label: Store; fit: Fitted", "Store,Spend,Late,Fitted\nA,1,2,2.1\n"),
    "Table": ("column: Region; column: Cases", "Region,Cases\nWest,4\n"),
}


def chart_package(tmp_path, specs):
    text = "".join(f"### Slide {n}\n\n**Chart {n}.** {form}: a comparison\n- **Data:** {data}\n\n"
                   for n, (form, data, _) in enumerate(specs, start=1))
    return package(tmp_path, text, {n: content for n, (_, _, content) in enumerate(specs, start=1)})


def test_check_charts_every_form_passes(tmp_path):
    path = chart_package(tmp_path, [(form, *spec) for form, spec in SPECS.items()])
    assert draft.check_charts(path, tmp_path / "charts") == []
    assert [c["form"] for c in draft.read_outline(path)["charts"]] == list(draft.CHART_FORMS)


@pytest.mark.parametrize("form, data, content, problem", [
    ("Pie", "category: Region; value: Cases", "Region,Cases\nW,1\n",
     "names no chart form (Pie); open the specification with one of: Horizontal bar, Bar with intervals, Line, "
     "Column, Stacked bar, Scatter, Table"),
    ("Column", None, "Region,Cases\nW,1\n", "no **Data:** line under the specification"),
    ("Column", "category: Region; value: Cases; Cases", "Region,Cases\nW,1\n",
     "**Data:** entry 'Cases' is not role: column header"),
    ("Column", "category: Region; value: Cases; lower: Low", "Region,Cases,Low\nW,1,0\n",
     "**Data:** role lower is not one a Column takes (category, value, series); a Column draws no intervals, so "
     "interval columns need a Bar with intervals"),
    ("Line", "category: Month; value: Rate (%); lower: Lower (%); upper: Upper (%)",
     "Month,Rate (%),Lower (%),Upper (%)\nJan,2,1,3\n",
     ["**Data:** role lower is not one a Line takes (category, value, series); a Line draws no intervals, so "
      "interval columns need a Bar with intervals",
      "**Data:** role upper is not one a Line takes (category, value, series); a Line draws no intervals, so "
      "interval columns need a Bar with intervals"]),
    ("Line", "category: Month; value: Rate (%)", "Month,Rate (%),Lower (%)\nJan,2,1\n",
     "chart-1.csv column 'Lower (%)' is named by no **Data:** role; name it by a role a Line takes (category, value, "
     "series), or export the chart without it; if it holds interval bounds, a Line draws none, so use a Bar with "
     "intervals"),
    ("Scatter", "x: Spend; y: Late", "Spend,Late,Store\n1,2,A\n",
     "chart-1.csv column 'Store' is named by no **Data:** role; name it by a role a Scatter takes (x, y, label, "
     "fit), or export the chart without it"),
    ("Line", "category: Month; category: Region; value: Cases", "Month,Region,Cases\nJan,W,1\n",
     "**Data:** names more than one category column"),
    ("Bar with intervals", "category: Region; value: Rate; lower: Low", "Region,Rate,Low\nW,2,1\n",
     "**Data:** names no upper column, which a Bar with intervals needs"),
    ("Stacked bar", "category: Region; series: Kind; value: A; value: B", "Region,Kind,A,B\nW,x,1,2\n",
     "**Data:** names a series column and more than one value column; name one value with a series, or drop the "
     "series"),
    ("Table", "column: Region; column: Late (%)", "Region\nW\n",
     "chart-1.csv has no column 'Late (%)', which **Data:** names"),
    ("Horizontal bar", "category: Region; value: Closed late (%)", "Region,Closed late (%),Orders (n)\nW,21,90\n",
     "chart-1.csv column 'Orders (n)' is named by no **Data:** role; name it by a role a Horizontal bar takes "
     "(category, value, series), or export the chart without it; if it holds interval bounds, a Horizontal bar "
     "draws none, so use a Bar with intervals"),
])
def test_check_charts_spec_rows(tmp_path, form, data, content, problem):
    text = f"### Slide\n\n**Chart 1.** {form}: a comparison\n" + (f"- **Data:** {data}\n" if data else "")
    path = package(tmp_path, text, {1: content})
    assert draft.check_charts(path, tmp_path / "charts") == [
        {"chart": "Chart 1", "problem": text} for text in (problem if isinstance(problem, list) else [problem])]
    if form == "Pie":
        package(tmp_path, text.replace("Pie: a comparison", "a comparison"), {1: content})
        assert draft.check_charts(path, tmp_path / "charts")[0]["problem"].startswith("names no chart form (a "
                                                                                      "comparison)")


def test_chart_fields_read_past_a_nested_item(tmp_path):
    text = ("### Slide\n\n- West.\n\n**Chart 1.** Line: monthly cases\n- **Data:** category: Month; value: Cases\n"
            "  - Cases are counted at closure.\n- **Source:** the claims team\n- **Alt text:** Cases rose.\n\n"
            "  **Caveat:** March is partial.\n\n**Notes:** N\n")
    path = package(tmp_path, text, {1: "Month,Cases\nJan,4\n"})
    outline = draft.read_outline(path)
    (chart,), (slide,) = outline["charts"], outline["slides"]
    assert chart["fields"] == {"Data": "category: Month; value: Cases", "Source": "the claims team",
                               "Alt text": "Cases rose. Caveat: March is partial."}
    assert chart["inside"] == [{"line": 7, "field": "Data", "kind": "item"},
                               {"line": 11, "field": "Alt text", "kind": "paragraph"}]
    assert [b["text"] for b in slide["bullets"]] == ["West."] and slide["extra"] == []
    assert draft.check_charts(path, tmp_path / "charts") == [
        {"chart": "Chart 1", "problem": "an item at line 7 is nested under the **Data:** field; a field is one "
                                        "paragraph, so join it to the field or move it below the specification as a "
                                        "slide bullet, after a blank line"},
        {"chart": "Chart 1", "problem": "a paragraph at line 11 continues the **Alt text:** field; a field is one "
                                        "paragraph, so join it to the field or move it below the specification as a "
                                        "slide bullet, after a blank line"}]
    # After a blank line a nested item still renders inside the field, so it is reported and the fields go on.
    loose = draft.parse_outline("# T\nSub\n\n## A\n\n**Headline:** H\n\n- West.\n\n**Chart 1.** Line: x\n"
                                "- **Data:** category: M; value: C\n\n  - Cases are counted at closure.\n"
                                "- **Source:** s\n- **Alt text:** a\n\n**Notes:** N\n")
    assert loose["charts"][0]["fields"] == {"Data": "category: M; value: C", "Source": "s", "Alt text": "a"}
    assert loose["charts"][0]["inside"] == [{"line": 13, "field": "Data", "kind": "item"}]
    assert loose["slides"][0]["bullets"] == [{"line": 8, "text": "West.", "sub": []}]
    # A field-named item back at a shallower depth renders outside the specification, so it is a bullet.
    nested = draft.parse_outline("# T\nSub\n\n## A\n\n- West.\n  - **Chart 1.** Table: grid\n"
                                 "    - **Data:** column: Region\n      - Regions as filed.\n"
                                 "    - **Alt text:** Grid.\n- **Source:** the claims team\n")
    slide = nested["slides"][0]
    assert nested["charts"][0]["fields"] == {"Data": "column: Region", "Alt text": "Grid."}
    assert nested["charts"][0]["inside"] == [{"line": 9, "field": "Data", "kind": "item"}]
    assert [b["text"] for b in slide["bullets"]] == ["West.", "Source: the claims team"]


def test_check_draft_help_lists_every_chart_row(tmp_path, capsys):
    with pytest.raises(SystemExit):
        draft.cli_check_draft(tmp_path, ["--help"])
    help_text = " ".join(capsys.readouterr().out.split())
    assert "a column of the file that it names by no role" in help_text
    assert "an item nested under a field or a second paragraph in one" in help_text
