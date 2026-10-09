# Kept cases:
# test_clean_prose_returns_no_rows: ordinary prose with numbers, n = 1,204, a date, a hyphenated word, abbreviations, currency, a fraction and _emphasis_ is clean.
# test_reports_each_kind_with_exact_text: one row per kind, each naming the offending token without surrounding punctuation.
# test_rows_are_ordered_by_line_then_column: several findings on one line keep column order across kinds.
# test_link_and_image_targets_are_excluded_but_text_and_alt_are_scanned: targets are skipped; link text and alt text are not.
# test_fenced_block_reports_once_at_opening_line: a fenced block is one code row at its fence; following lines are scanned again.
# test_html_comments_are_ignored: single-line and multi-line comments are dropped without shifting line numbers.
# test_names_match_whole_tokens_case_sensitively: names, including a hyphenated slug, match only as whole tokens and in exact case.
# test_name_takes_precedence_over_other_kinds: a given name reports once as a name, not again as an identifier.
# test_digit_only_fractions_are_not_paths: 3/4 and 6/30/2026 are numbers; a slash between letters is still a path.

import importlib.util
from pathlib import Path

import pytest


ASSET = Path(__file__).resolve().parents[1] / ".agents/skills/awb-package/assets/awb_findings.py"
spec = importlib.util.spec_from_file_location("awb_findings", ASSET)
findings = importlib.util.module_from_spec(spec)
spec.loader.exec_module(findings)


@pytest.fixture
def write(tmp_path):
    def write(text):
        path = tmp_path / "findings.md"
        path.write_text(text, encoding="utf-8")
        return path
    return write


def test_clean_prose_returns_no_rows(write):
    path = write(
        "## Answer\n"
        "\n"
        "West closes 12.5% of cases late (n = 1,204), the second-lowest rate since 2026-06-30.\n"
        "Revenue rose to $1.2M. The U.S. teams, e.g. Denver, cut delays by about 3/4.\n"
        "\n"
        "*Figure 1. Share of cases closed late, Q3 2026, _all_ regions.*\n"
    )
    assert findings.check(path) == []


def test_reports_each_kind_with_exact_text(write):
    path = write(
        "Run `make report` first.\n"
        "Data came from src/packaging.\n"
        "See ../notes for detail.\n"
        "The table lives in orders.parquet.\n"
        "We filtered on (late_close_flag).\n"
        "The source is sales.daily_orders, built at a1b2c3d.\n"
        "This is the churn-q3 package.\n"
    )
    assert findings.check(str(path), names=["churn-q3"]) == [
        {"line": 1, "kind": "code", "text": "`make report`"},
        {"line": 2, "kind": "path", "text": "src/packaging"},
        {"line": 3, "kind": "path", "text": "../notes"},
        {"line": 4, "kind": "file", "text": "orders.parquet"},
        {"line": 5, "kind": "identifier", "text": "late_close_flag"},
        {"line": 6, "kind": "identifier", "text": "sales.daily_orders"},
        {"line": 6, "kind": "sha", "text": "a1b2c3d"},
        {"line": 7, "kind": "name", "text": "churn-q3"},
    ]


def test_rows_are_ordered_by_line_then_column(write):
    path = write("ok\ncase_id beside `code` and report.csv before R-17.\n")
    assert findings.check(path, names=["R-17"]) == [
        {"line": 2, "kind": "identifier", "text": "case_id"},
        {"line": 2, "kind": "code", "text": "`code`"},
        {"line": 2, "kind": "file", "text": "report.csv"},
        {"line": 2, "kind": "name", "text": "R-17"},
    ]


def test_link_and_image_targets_are_excluded_but_text_and_alt_are_scanned(write):
    path = write(
        "![West closes 12% late](figures/late-share.png)\n"
        "\n"
        "*Figure 1. Share closed late.*\n"
        "See [the regional view](https://example.org/a_b/c.md) and [region_view](notes/x.md).\n"
        "![alt from late_view.sql](figures/y.png)\n"
    )
    assert findings.check(path) == [
        {"line": 4, "kind": "identifier", "text": "region_view"},
        {"line": 5, "kind": "file", "text": "late_view.sql"},
    ]


def test_fenced_block_reports_once_at_opening_line(write):
    path = write(
        "Before.\n"
        "```python\n"
        "df = load('orders.csv')\n"
        "df.groupby('region_id')\n"
        "```\n"
        "After with region_id.\n"
        "~~~\n"
        "unclosed_block runs to the end\n"
    )
    assert findings.check(path) == [
        {"line": 2, "kind": "code", "text": "```python"},
        {"line": 6, "kind": "identifier", "text": "region_id"},
        {"line": 7, "kind": "code", "text": "~~~"},
    ]


def test_html_comments_are_ignored(write):
    path = write(
        "Clean <!-- from late_view.sql --> line.\n"
        "<!--\n"
        "evidence: results/r1.json\n"
        "-->\n"
        "Then case_id.\n"
    )
    assert findings.check(path) == [
        {"line": 5, "kind": "identifier", "text": "case_id"},
    ]


def test_names_match_whole_tokens_case_sensitively(write):
    path = write(
        "The q3-churn-review package.\n"
        "Not q3-churn-review-v2 or Q3-Churn-Review.\n"
        "Region West, not Westerly.\n"
    )
    assert findings.check(path, names=("q3-churn-review", "West", "")) == [
        {"line": 1, "kind": "name", "text": "q3-churn-review"},
        {"line": 3, "kind": "name", "text": "West"},
    ]


def test_name_takes_precedence_over_other_kinds(write):
    path = write("Built from daily_orders.\n")
    assert findings.check(path, names=["daily_orders"]) == [
        {"line": 1, "kind": "name", "text": "daily_orders"},
    ]


def test_digit_only_fractions_are_not_paths(write):
    path = write("About 3/4 of cases on 6/30/2026 were late; open/closed status differed.\n")
    assert findings.check(path) == [
        {"line": 1, "kind": "path", "text": "open/closed"},
    ]
