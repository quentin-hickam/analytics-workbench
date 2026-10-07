"""Shared figure style for an analytics workbench project (matplotlib + seaborn only).

Copy this file into the project's shared presentation module; do not import it from the skill folder.
Presentation only: plot results computed by neutral operations, never compute findings here.
"""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

# Okabe-Ito colorblind-safe hues. Use ACCENT for the message, greys for context.
ACCENT = "#0072B2"     # blue: the series or category the title is about
CONTRAST = "#D55E00"   # vermillion: a second highlighted group, or below-target values
SUPPORT = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00"]  # max six categories
GREY_TEXT = "#333333"  # titles, labels, direct value labels
GREY_CONTEXT = "#A6A6A6"  # non-focal bars, lines, reference series
GREY_GRID = "#E5E5E5"  # light gridlines and reference lines

WIDTH_IN = 6.5   # Word text width on Letter or A4 with ~1 in margins
HEIGHT_IN = 4.0  # 6.5 x 4.0 in at 200 dpi -> 1300 x 800 px
TALL_HEIGHT_IN = 5.0  # single-panel maximum when row labels or a multi-line caption need it
DPI = 200        # below Word's 220 ppi default compression target at full text width


def apply_style() -> None:
    """Set the seaborn theme and rcParams once per process, before creating figures."""
    sns.set_theme(style="white", palette=SUPPORT)
    mpl.rcParams.update({
        "figure.figsize": (WIDTH_IN, HEIGHT_IN),
        "figure.dpi": 100,
        "figure.facecolor": "white",
        "figure.constrained_layout.use": True,
        "savefig.dpi": DPI,
        "savefig.facecolor": "white",
        "savefig.transparent": False,
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
        "font.size": 10,
        "figure.titlesize": 13,
        "figure.titleweight": "bold",
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "legend.frameon": False,
        "text.color": GREY_TEXT,
        "axes.labelcolor": GREY_TEXT,
        "axes.edgecolor": GREY_CONTEXT,
        "xtick.color": GREY_TEXT,
        "ytick.color": GREY_TEXT,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
        "grid.color": GREY_GRID,
        "grid.linewidth": 0.8,
        "lines.linewidth": 2.0,
        "svg.fonttype": "none",  # keep SVG text as text
        "svg.hashsalt": "awb",   # stable SVG ids across reruns
    })


def add_caption(fig, text: str) -> None:
    """Put units, population, period, source, and caveats in a 9 pt line below the axes (uses supxlabel)."""
    fig.supxlabel(text, x=0.0, ha="left", fontsize=9, color=GREY_TEXT, wrap=True)


def save_figure(fig, path, *, provenance: dict | None = None, svg: bool = False) -> Path:
    """Write an opaque white PNG at the house size; optionally an SVG beside it. Closes the figure."""
    path = Path(path).with_suffix(".png")
    path.parent.mkdir(parents=True, exist_ok=True)
    meta = {str(k): str(v) for k, v in (provenance or {}).items()}
    fig.savefig(path, dpi=DPI, facecolor="white", metadata=meta)
    if svg:
        fig.savefig(path.with_suffix(".svg"), facecolor="white", metadata={"Date": None})
    plt.close(fig)
    return path
