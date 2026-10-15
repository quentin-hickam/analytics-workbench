# Kept cases:
# test_parse_outline_derives_the_deck: the title slide, one slide per ## section but Findings and per ### finding, with section, headline, bullets and nested bullets, notes, and chart; every chart with its form, comparison, fields, and slide; nothing is written.
# test_parse_outline_reads_as_it_renders: a comment hides a bullet, a fence is no bullet, a chart's fields end at a blank line so a later Caveat bullet stays on the slide, a list-item specification is a chart, a field already given is a bullet, and a wrapped bullet is one bullet, a block quote inside it included; a paragraph back at a bullet's depth after its nested chart joins no field.
# test_outline_problems_clean_deck: a deck following every slide rule, its required slides included, has no rows; a 15-word headline and five bullets pass.
# test_outline_problems_rows: each slide rule broken gives its row with slide, line, and problem, a block quote outside a list being a paragraph of its own, as is a paragraph back at a bullet's depth after a deeper item, and the title slide's notes counted too; a deck without its # heading also has its subtitle on no slide, and one without ## Findings has each finding outside it.
# test_outline_passes_without_implications: a deck without Implications passes, and one with it passes too.
# test_outline_requires_its_slides_in_order: a deck without How we know, Limitations, or Answer, with Answer not first, without a finding slide in the main sequence, with How we know before a finding or Limitations before How we know, or with a required slide repeated gives one row for each, a missing slide's line null.
# test_appendix_slides_parse_in_order_and_count_separately: ## Appendix ### slides parse in order, a template slide's name making that slide rather than a finding, are marked appendix and counted apart from the main sequence, and a required slide there still counts.
# test_appendix_rows: text before the appendix's first slide, a ## slide after it, a main-sequence slide placed in it, an empty appendix, an appendix slide without its headline, every finding moved into it, a ### finding slide under a ## Findings reopened after it, a second ## Appendix, and Limitations before How we know in it give their rows.
# test_chart_data_reads_roles: role: header pairs in order, case-insensitive roles, headers kept whole, colons in a header kept.
# test_check_charts_every_form_passes: a specification in each of the seven forms, its Data line naming that form's roles, and a file with those columns passes.
# test_check_charts_spec_rows: an unknown or missing form, a missing Data line, a malformed entry, a role the form does not take, a repeated single role, a missing needed role, a series with two values, a column the file lacks, and a file column no role names give one row each; an interval role on a form without intervals says only a Bar with intervals draws them, and an unnamed column there says so if it holds interval bounds.
# test_chart_fields_read_past_a_nested_item: an item nested under a field is kept out of the fields and the bullets and reported, and the fields after it still count; a blank line before the nested item changes none of this; a later paragraph in a field is reported, after a nested item too, and the fields after it still count; a paragraph at a nested specification's own depth is outside the fields; a field-named item back at a shallower depth is a bullet.
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

## Limitations and open caveats

**Headline:** March records are incomplete in every region

- **Caveat:** March counts may rise once the records are complete.

**Notes:** The claims team expects the full March file in July.
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
        ("How we know", False, "Totals reconcile to the finance ledger", None),
        ("Limitations and open caveats", False, "March records are incomplete in every region", None)]
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


HOW = DECK[DECK.index("## How we know"):DECK.index("## Limitations")]
LIMITS = DECK[DECK.index("## Limitations"):]
ANSWER_SLIDE = DECK[DECK.index("## Answer"):DECK.index("## Findings")]
FINDING_SLIDES = DECK[DECK.index("### West"):DECK.index("## How we know")]
CONTEXT = "## Context\n\n**Headline:** Claims rose this year in every region\n\n**Notes:** Context first.\n\n"
APPENDIX = """
## Appendix

### Late claims fell in the north

- North closed 4% of claims late.

**Notes:** The north is the smallest region.

""" + HOW.replace("## How we know", "### How we know")
# DECK with How we know moved under ## Appendix, after one more finding slide.
MOVED = DECK.replace(HOW, "") + APPENDIX
NEXT_STEPS = "\n## Next steps\n\n**Headline:** Staff the west queue first\n\n**Notes:** The queue is the decision.\n"
SOUTH = "\n### Late claims fell in the south\n\n- South closed 3% of claims late.\n\n**Notes:** The south is small.\n"


def line_of(text, marker, occurrence=1):
    index = -1
    for _ in range(occurrence):
        index = text.index(marker, index + 1)
    return text.count("\n", 0, index) + 1


def test_outline_passes_without_implications(tmp_path):
    # Implications is optional; DECK has none, and adding one keeps the deck clean too.
    assert "Implications" not in DECK and draft.outline_problems(package(tmp_path)) == []
    implications = "## Implications\n\n**Headline:** Staffing the west queue cuts late claims\n\n" \
                   "**Notes:** Within the evidence.\n\n"
    text = DECK.replace("## How we know", implications + "## How we know")
    assert draft.outline_problems(package(tmp_path, text)) == []


# The required slides are the title, Answer, at least one finding in the main sequence, How we know, and
# Limitations and open caveats, in that order; How we know and Limitations may move to the appendix.
@pytest.mark.parametrize("text, expected", [
    (DECK.replace(HOW, ""),
     [("How we know", None, "no How we know slide; add it after the finding slides, or under ## Appendix")]),
    (DECK.replace("\n" + LIMITS, ""),
     [("Limitations and open caveats", None, "no Limitations and open caveats slide; add it after the finding "
                                             "slides, or under ## Appendix")]),
    (DECK.replace(HOW, "").replace("\n" + LIMITS, ""),
     [("How we know", None, "no How we know slide; add it after the finding slides, or under ## Appendix"),
      ("Limitations and open caveats", None, "no Limitations and open caveats slide; add it after the finding "
                                             "slides, or under ## Appendix")]),
    (DECK.replace(ANSWER_SLIDE, ""),
     [("Answer", None, "no ## Answer slide; open the deck with it, right after the title slide")]),
    (DECK.replace("## Answer", CONTEXT + "## Answer"),
     [("Answer", line_of(DECK.replace("## Answer", CONTEXT + "## Answer"), "## Answer"),
       "the Answer slide comes first after the title slide; move it there")]),
    (DECK.replace("## Findings\n\n" + FINDING_SLIDES, ""),
     [("Findings", None, "no ### finding slide in the main sequence; keep at least one under ## Findings")]),
    (DECK.replace(HOW, "").replace("## Findings", HOW + "## Findings"),
     [("How we know", line_of(DECK.replace(HOW, "").replace("## Findings", HOW + "## Findings"), "## How we know"),
       "How we know comes after the finding slides; move it below them")]),
    (DECK.replace(HOW, "") + "\n" + HOW,
     [("Limitations and open caveats", line_of(DECK, "## Limitations") - HOW.count("\n"),
       "Limitations and open caveats comes after the finding slides and How we know; move it below them")]),
    (DECK + "\n" + HOW,
     [("How we know", line_of(DECK + "\n" + HOW, "## How we know", 2), "2 How we know slides; keep one")]),
], ids=["no how we know", "no limitations", "neither", "no answer", "answer not first", "no finding",
        "how we know before findings", "limitations before how we know", "repeated"])
def test_outline_requires_its_slides_in_order(tmp_path, text, expected):
    rows = draft.outline_problems(package(tmp_path, text))
    assert [(r["slide"], r["line"], r["problem"]) for r in rows] == expected


def test_appendix_slides_parse_in_order_and_count_separately(tmp_path):
    text = MOVED
    outline = draft.read_outline(package(tmp_path, text))
    assert [(s["section"], s["finding"], s["appendix"], s["heading"], s["headline"]) for s in outline["slides"]] == [
        ("Answer", False, False, "Answer", "West claims close late four times as often as the east"),
        ("Findings", True, False, "West claims closed late 21% of the time", "West claims closed late 21% of the time"),
        ("Findings", True, False, "Late claims rose each month in the west", "Late claims rose each month in the west"),
        ("Limitations and open caveats", False, False, "Limitations and open caveats",
         "March records are incomplete in every region"),
        ("Appendix", True, True, "Late claims fell in the north", "Late claims fell in the north"),
        ("Appendix", False, True, "How we know", "Totals reconcile to the finance ledger")]
    assert outline["counts"] == {"main": 5, "appendix": 2}
    assert outline["appendix"] == [{"line": line_of(text, "## Appendix"), "slides": 2}]
    assert [b["text"] for b in outline["slides"][-1]["bullets"]] == ["Claims are counted once."]
    # How we know counts as present from the appendix, so the deck passes.
    assert draft.outline_problems(package(tmp_path, text)) == []
    assert draft.read_outline(package(tmp_path))["counts"] == {"main": 6, "appendix": 0}


@pytest.mark.parametrize("text, expected", [
    (MOVED.replace("## Appendix\n", "## Appendix\n\nBackup slides follow.\n"),
     [("under Appendix before its first slide", "Backup slides follow.",
       "text under Appendix before its first slide is on no slide; move it onto a slide")]),
    (MOVED + NEXT_STEPS,
     [("Next steps", "## Next steps",
       "a ## slide after ## Appendix; the appendix ends the deck, so move this slide before it")]),
    (MOVED + "\n### Implications\n\n**Headline:** Staff the west queue first\n\n**Notes:** N.\n",
     [("Implications", "### Implications",
       "Implications stays in the main sequence; make it a ## slide before ## Appendix")]),
    (DECK + "\n## Appendix\n",
     [("Appendix", "## Appendix", "## Appendix holds no slide; add ### slides under it or remove it")]),
    (MOVED.replace("**Headline:** Totals reconcile to the finance ledger\n\n", ""),
     [("How we know", "### How we know", "no **Headline:** line; open the slide with one")]),
    (DECK.replace("## Findings\n\n" + FINDING_SLIDES, "") + "\n## Appendix\n\n" + FINDING_SLIDES,
     [("Findings", None, "no ### finding slide in the main sequence; keep at least one under ## Findings")]),
    (MOVED + "\n## Findings\n" + SOUTH,
     [("Late claims fell in the south", "### Late claims fell in the south",
       "a ### finding slide after ## Appendix; the appendix ends the deck, so move it under ## Findings before "
       "## Appendix, or under ## Appendix")]),
    (MOVED + "\n## Appendix\n" + SOUTH,
     [("Appendix", "## Appendix\n\n### Late claims fell in the south",
       "a second ## Appendix; the deck has one appendix, so merge them")]),
    (DECK.replace(HOW, "").replace("\n" + LIMITS, "") + "\n## Appendix\n\n"
     + LIMITS.replace("## Limitations", "### Limitations") + "\n" + HOW.replace("## How we know", "### How we know"),
     [("Limitations and open caveats", "### Limitations",
       "Limitations and open caveats comes after How we know under ## Appendix; move it below How we know")]),
], ids=["text before first slide", "slide after appendix", "main-only section", "empty", "section without headline",
        "every finding moved", "finding after appendix", "second appendix", "limitations before how we know"])
def test_appendix_rows(tmp_path, text, expected):
    rows = draft.outline_problems(package(tmp_path, text))
    assert [(r["slide"], r["line"], r["problem"]) for r in rows] == [
        (slide, line_of(text, marker) if marker else None, problem) for slide, marker, problem in expected]


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
    # A paragraph back at the field's depth after a nested item renders inside the field too, so it is reported
    # and the fields go on; one at the depth of a nested specification's own item is outside the fields.
    after = draft.parse_outline("# T\nSub\n\n## A\n\n**Headline:** H\n\n**Chart 1.** Line: x\n"
                                "- **Data:** category: M; value: C\n  - Cases are counted at closure.\n\n"
                                "  More on the data.\n- **Source:** s\n- **Alt text:** a\n\n- West.\n"
                                "  - **Chart 2.** Table: grid\n    - **Data:** column: Region\n"
                                "      - Regions as filed.\n\n      More on the regions.\n    - **Alt text:** Grid.\n\n"
                                "    Under the specification.\n\n**Notes:** N\n")
    first, second = after["charts"]
    assert first["fields"] == {"Data": "category: M; value: C", "Source": "s", "Alt text": "a"}
    assert first["inside"] == [{"line": 10, "field": "Data", "kind": "item"},
                               {"line": 12, "field": "Data", "kind": "paragraph"}]
    assert second["fields"] == {"Data": "column: Region", "Alt text": "Grid."}
    assert second["inside"] == [{"line": 19, "field": "Data", "kind": "item"},
                                {"line": 21, "field": "Data", "kind": "paragraph"}]
    assert after["slides"][0]["bullets"] == [{"line": 16, "text": "West.", "sub": []}]
    assert after["slides"][0]["extra"] == [{"line": 24, "text": "Under the specification."}]
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
