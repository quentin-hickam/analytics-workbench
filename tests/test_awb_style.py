# Kept cases:
# test_clean_figure_passes_and_saves: display-language figure returns no problems and saves a 1300 px PNG.
# test_snake_case_tick_label_fails: raw snake_case category codes in tick labels are flagged.
# test_seaborn_default_axis_label_and_legend_title_fail: seaborn's column-name axis label and legend title are flagged.
# test_facet_default_title_fails_and_count_annotation_passes: `region = West` facet titles fail, `n = 1,204` passes, set_titles("{col_name}") clears it.
# test_text_over_65_characters_fails: a caption drawn with fig.supxlabel or fig.text is flagged by length.
# test_title_clipped_at_figure_edge_fails: regression: a 65-character axes title pushed right by long tick labels is reported as clipped.
# test_save_figure_raises_and_writes_nothing_on_failure: ValueError lists the problem; no file or directory is written.
# test_save_figure_writes_provenance_metadata: provenance keys land in PNG text metadata on success.

import importlib.util
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import pytest  # noqa: E402
import seaborn as sns  # noqa: E402
from PIL import Image  # noqa: E402


ASSET = Path(__file__).resolve().parents[1] / ".agents/skills/awb-visualize/assets/awb_style.py"
spec = importlib.util.spec_from_file_location("awb_style", ASSET)
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)

REGIONS = pd.DataFrame({"region": ["West", "East", "North"], "late_rate": [0.12, 0.18, 0.21]})


@pytest.fixture(autouse=True)
def _style():
    style.apply_style()
    yield
    plt.close("all")


def clean_figure():
    fig, ax = plt.subplots()
    sns.barplot(REGIONS, y="region", x="late_rate", saturation=1, ax=ax)
    ax.set_title("West closes 12% of cases late")
    ax.set_xlabel("Cases closed late (%)")
    ax.set_ylabel("")
    return fig


def test_clean_figure_passes_and_saves(tmp_path):
    fig = clean_figure()
    assert style.check_text(fig) == []
    path = style.save_figure(fig, tmp_path / "figures" / "late")
    assert path == tmp_path / "figures" / "late.png"
    with Image.open(path) as image:
        assert image.size[0] == 1300


def test_snake_case_tick_label_fails():
    fig, ax = plt.subplots()
    codes = REGIONS.assign(region=["west_region", "east_region", "north_region"])
    sns.barplot(codes, y="region", x="late_rate", saturation=1, ax=ax)
    ax.set_xlabel("Cases closed late (%)")
    ax.set_ylabel("")
    problems = style.check_text(fig)
    assert len(problems) == 3
    assert all(p.startswith("y tick label") and "snake_case" in p for p in problems)


def test_seaborn_default_axis_label_and_legend_title_fail():
    fig, ax = plt.subplots()
    df = pd.DataFrame({"days_open": [3, 9, 14], "late_rate": [0.1, 0.2, 0.3], "case_type": ["Billing", "Repair", "Repair"]})
    sns.scatterplot(df, x="days_open", y="late_rate", hue="case_type", ax=ax)
    problems = style.check_text(fig)
    assert any(p.startswith("x-axis label 'days_open'") for p in problems)
    assert any(p.startswith("y-axis label 'late_rate'") for p in problems)
    assert any(p.startswith("legend title 'case_type'") for p in problems)


@pytest.mark.filterwarnings("ignore:The figure layout has changed to tight")
def test_facet_default_title_fails_and_count_annotation_passes():
    df = pd.DataFrame({"region": ["West", "West", "East", "East"], "week": [1, 2, 1, 2], "rate": [0.1, 0.2, 0.3, 0.2]})
    g = sns.FacetGrid(df, col="region")
    g.map_dataframe(sns.lineplot, x="week", y="rate")
    g.set_axis_labels("Week", "Cases closed late (%)")
    g.axes.flat[0].annotate("n = 1,204", xy=(1, 0.1))
    problems = style.check_text(g.figure)
    assert any("'region = West'" in p and "facet title" in p for p in problems)
    assert not any("n = 1,204" in p for p in problems)
    g.set_titles("{col_name}")
    assert style.check_text(g.figure) == []


@pytest.mark.parametrize("draw", [
    lambda fig, text: fig.supxlabel(text, x=0.0, ha="left", fontsize=9),
    lambda fig, text: fig.text(0.01, 0.01, text, fontsize=9),
])
def test_text_over_65_characters_fails(draw):
    fig = clean_figure()
    caption = "Share of cases closed after target, by region; all closed cases, Jan to Jun 2026."
    draw(fig, caption)
    problems = style.check_text(fig)
    assert len(problems) == 1
    assert f"{len(caption)} characters, over 65" in problems[0]


def test_title_clipped_at_figure_edge_fails():
    fig, ax = plt.subplots()
    sns.barplot(REGIONS.assign(region=["Northwest Pacific", "East", "North"]), y="region", x="late_rate", saturation=1, ax=ax)
    ax.set(xlabel="Cases closed late (%)", ylabel="")
    title = "West closes 12% of cases late, the second-lowest rate of any area"
    ax.set_title(title)
    assert style.check_text(fig) == [f"title {title!r}: runs past the figure edge and is clipped"]
    ax.set_title("")
    fig.suptitle(title, x=0.02, ha="left")
    assert style.check_text(fig) == []


def test_save_figure_raises_and_writes_nothing_on_failure(tmp_path):
    fig = clean_figure()
    fig.axes[0].set_xlabel("late_rate")
    target = tmp_path / "figures" / "late.png"
    with pytest.raises(ValueError, match="x-axis label 'late_rate'"):
        style.save_figure(fig, target, svg=True)
    assert not (tmp_path / "figures").exists()


def test_save_figure_writes_provenance_metadata(tmp_path):
    provenance = {"Source": "v_case_closures; commit abc1234", "Comment": "settings: late_days=5"}
    path = style.save_figure(clean_figure(), tmp_path / "late.png", provenance=provenance)
    with Image.open(path) as image:
        assert image.text["Source"] == provenance["Source"]
        assert image.text["Comment"] == provenance["Comment"]
