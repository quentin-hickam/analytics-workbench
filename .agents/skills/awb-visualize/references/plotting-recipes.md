# Plotting recipes and helper interface

Use seaborn 0.13 for tidy-frame statistical/categorical plots and matplotlib for layout, annotation, formatting, and saving. seaborn accepts pandas and polars. `seaborn.objects` is experimental; keep it out of shared figure code. Use interactive libraries only for an explicitly requested interactive file, with PNG, document caption, and table delivery retained.

## Shared style helper

Copy [awb_style.py](../assets/awb_style.py) once to `src/presentation/style.py`; use the project module thereafter. Its constants and rcParams are authoritative. Call `apply_style()` before `plt.subplots()` so shared size and constrained layout apply.

Run from the project root with the copied style module. This function draws precomputed, display-named values; write its caption separately in the containing document.

```python
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from src.presentation.style import ACCENT, apply_style, save_figure


def draw_rates(display_names, rates, title, output_path, provenance):
    apply_style()
    fig, ax = plt.subplots()
    ax.barh(display_names, rates, color=ACCENT)
    ax.invert_yaxis()
    ax.set(title=title, xlabel="Cases closed late (%)", ylabel="")
    ax.xaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
    ax.grid(axis="x")
    return save_figure(fig, output_path, provenance=provenance)
```

- `apply_style()` configures the theme and rcParams once per process.
- `check_text(fig)` draws the figure and returns problems: snake_case/dotted identifiers, filenames, automatic `col = value` facets, text over 65 characters, and edge clipping. An empty list passes; visual inspection is still required for raw codes and single-word identifiers.
- `save_figure(fig, path, *, provenance=None, svg=False)` runs `check_text` first. Failure raises `ValueError` before writing anything and leaves the figure open for repair. Success creates parent directories, writes `.png` with stringified metadata, optionally adds `.svg`, closes the figure, and returns its PNG `Path`. It preserves current dimensions rather than resizing a manually resized figure.
- Import constants such as `WIDTH_IN`, `HEIGHT_IN`, `TALL_HEIGHT_IN`, `DPI`, `ACCENT`, `CONTRAST`, `SUPPORT`, and `GREY_CONTEXT` when needed; inspect the module only to modify or debug it.

## Display labels

Map codes before plotting, for example `df.assign(region=df["region_code"].map(REGION_NAMES))`. Set both labels explicitly with `ax.set(xlabel="Cases closed late (%)", ylabel="")`. Rename an automatic legend title with `ax.get_legend().set_title("Case type")` or use `legend=False` with direct labels. For facets call `g.set_titles("{col_name}")` (or `"{row_name} | {col_name}"`) and `g.set_axis_labels(...)`. All names come from the business glossary.

If long tick labels push a left-aligned axes title past the edge, use `fig.suptitle(title, x=0.02, ha="left")` instead. Keep the title one line, at most 65 characters; captions, source lines, and notes live in the containing document.

## Calls by comparison

Use `con.sql(query).df()` or `.pl()` to pass analytical frames directly. The snippets below assume those results are already computed.

| Comparison | Call |
| --- | --- |
| Categories | `sns.barplot(df, y=cat, x=val, order=sorted_cats, errorbar=None, saturation=1)`; `ax.bar_label(container, fmt="{:,.0f}", padding=3)` |
| Estimates and intervals | `sns.pointplot(..., errorbar=None, linestyle="none")` plus `ax.errorbar` from computed bounds |
| Time | `sns.lineplot(df, x=date, y=val, hue=series, estimator=None, errorbar=None)`; annotate line ends |
| Distribution | `sns.histplot`, `sns.ecdfplot`, `sns.boxplot` |
| Relationship | `sns.scatterplot(alpha=0.5)`; draw fitted lines from analysis results |
| Grid | `sns.heatmap(pivot, annot=True, fmt=",.0f", cmap="Blues")`; `"RdBu_r", center=0` for signed change |
| Small multiples | `plt.subplots(1, n, sharey=True)` and axes-level calls; exploratory `sns.relplot`/`sns.catplot` use `height`/`aspect` and tight layout |

For findings, ensure one estimate per plotted group and draw precomputed uncertainty with `ax.errorbar` or `ax.fill_between`. For exploration, `errorbar=` accepts `("ci", 95)`, `"se"`, or `("pi", 50)`; seed bootstraps. `ci=` is the pre-0.12 spelling. Palettes require `hue`; use `saturation=1` for exact bar colors. A focus highlight can use `hue=is_focus, palette={True: ACCENT, False: GREY_CONTEXT}, legend=False`.

For numeric ticks use `PercentFormatter(xmax=1, decimals=0)` for proportions, `StrMethodFormatter("{x:,.0f}")` for counts, `FuncFormatter(lambda v, _: f"{v / 1e6:.1f}M")` for large values, and `mdates.ConciseDateFormatter` for dates. Match narrative rounding. Set small-multiple titles with `ax.set_title(name, fontsize=11)` and a value-axis grid with `ax.grid(axis="x")` when needed.
