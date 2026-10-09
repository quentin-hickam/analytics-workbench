"""Shared figure style for an analytics workbench project (matplotlib + seaborn only).

Copy this file into the project's shared presentation module; do not import it from the skill folder.
Presentation only: plot results computed by neutral operations, never compute findings here.
"""

import re
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
TALL_HEIGHT_IN = 5.0  # single-panel maximum when many row labels need the height
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


MAX_TEXT_CHARS = 65  # one-line headline; longer text is a caption or sentence that belongs in the document

_SNAKE = re.compile(r"\w*[A-Za-z0-9]_[A-Za-z0-9]\w*")
_DOTTED = re.compile(r"(?<![\w.])[A-Za-z_]\w+(?:\.[A-Za-z_]\w+)+(?!\w)")  # schema.table; not e.g. or U.S.
_FILE = re.compile(
    r"(?<![\w.])[\w./-]*\w\.(?:md|py|csv|parquet|json|sql|png|svg|duckdb|db|xlsx|yaml|yml|toml|txt|ipynb)(?!\w)",
    re.IGNORECASE,
)
_FACET = re.compile(r"(?:^|\| )([a-z][a-z0-9_]+) = ")


def _figure_texts(fig):
    """Yield (role, Text) once per text element a reader can see, after formatters have run."""
    seen = set()
    for role, t in _all_texts(fig):
        if id(t) not in seen:
            seen.add(id(t))
            yield role, t


def _all_texts(fig):
    figs = [fig]
    while figs:
        f = figs.pop()
        figs.extend(getattr(f, "subfigs", []))
        for role, attr in (("figure title", "_suptitle"), ("figure x label", "_supxlabel"),
                           ("figure y label", "_supylabel")):
            if getattr(f, attr, None) is not None:
                yield role, getattr(f, attr)
        for t in f.texts:
            yield "figure text", t
        for leg in f.legends:
            if leg.get_visible():
                yield "legend title", leg.get_title()
                for t in leg.get_texts():
                    yield "legend entry", t
    for ax in dict.fromkeys(fig.get_axes()):
        if not ax.get_visible():
            continue
        for attr in ("title", "_left_title", "_right_title"):
            yield "title", getattr(ax, attr)
        if ax.axison:
            for name, axis in (("x", ax.xaxis), ("y", ax.yaxis)):
                if not axis.get_visible():
                    continue
                yield f"{name}-axis label", axis.label
                yield f"{name}-axis offset", axis.get_offset_text()
                # Axis.draw draws only the ticks _update_ticks returns (those in view, labels formatted);
                # get_ticklabels would also return off-view ticks that never reach the image.
                for tick in axis._update_ticks():
                    yield f"{name} tick label", tick.label1
                    yield f"{name} tick label", tick.label2
        for t in ax.texts:
            yield "annotation", t
        leg = ax.get_legend()
        if leg is not None and leg.get_visible():
            yield "legend title", leg.get_title()
            for t in leg.get_texts():
                yield "legend entry", t


def _problems(text: str) -> list[str]:
    found = []
    files = [m.group() for m in _FILE.finditer(text)]
    if files:
        found.append("file name " + ", ".join(repr(x) for x in dict.fromkeys(files)))
    snake = [m.group() for m in _SNAKE.finditer(text) if not any(m.group() in f for f in files)]
    if snake:
        found.append("snake_case identifier " + ", ".join(repr(x) for x in dict.fromkeys(snake)))
    dotted = [m.group() for m in _DOTTED.finditer(text) if not any(m.group() in f for f in files)]
    if dotted:
        found.append("dotted identifier " + ", ".join(repr(x) for x in dict.fromkeys(dotted)))
    if _FACET.search(text):
        found.append('"col = value" facet title (use g.set_titles("{col_name}"))')
    if len(text) > MAX_TEXT_CHARS:
        found.append(f"{len(text)} characters, over {MAX_TEXT_CHARS} (captions and sentences go in the document)")
    return found


def check_text(fig) -> list[str]:
    """Draw the figure and return one message per visible text element that is not plain display language.

    Flags snake_case and dotted identifiers, file names, seaborn "col = value" facet titles, any text
    longer than 65 characters, and text clipped at the figure edge. An empty list means the figure's text passes.
    """
    fig.canvas.draw()  # run tick formatters and layout so tick labels hold their displayed strings
    messages = []
    for role, t in _figure_texts(fig):
        text = t.get_text().strip()
        if not text or not t.get_visible():
            continue
        problems = _problems(text)
        box = t.get_window_extent()
        if box.x0 < -1 or box.y0 < -1 or box.x1 > fig.bbox.width + 1 or box.y1 > fig.bbox.height + 1:
            problems.append("runs past the figure edge and is clipped")
        if problems:
            shown = text if len(text) <= 70 else text[:67] + "..."
            messages.append(f"{role} {shown!r}: " + "; ".join(problems))
    return list(dict.fromkeys(messages))


def save_figure(fig, path, *, provenance: dict | None = None, svg: bool = False) -> Path:
    """Check the figure's text, then write an opaque white PNG at the house size; optionally an SVG beside it.

    Raises ValueError listing each problem from check_text before writing anything; the figure stays open
    for repair. Provenance (source identifiers, commit, settings, comment) goes into PNG text metadata,
    never into the image. Closes the figure after writing.
    """
    problems = check_text(fig)
    if problems:
        raise ValueError("figure text fails check_text:\n- " + "\n- ".join(problems))
    path = Path(path).with_suffix(".png")
    path.parent.mkdir(parents=True, exist_ok=True)
    meta = {str(k): str(v) for k, v in (provenance or {}).items()}
    fig.savefig(path, dpi=DPI, facecolor="white", metadata=meta)
    if svg:
        fig.savefig(path.with_suffix(".svg"), facecolor="white", metadata={"Date": None})
    plt.close(fig)
    return path
