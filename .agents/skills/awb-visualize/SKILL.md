---
name: awb-visualize
description: Create analytics workbench charts, figures, diagrams, and formatted results tables. Use whenever a visual or a results table is produced for chat, an investigation record, or a delivery package.
---

# Visualize workbench results

Make each figure once so it reads in chat and still reads after it is pasted into a Word, Outlook, or Google Docs document. Resolve repository paths from the project root and bundled asset paths relative to this `SKILL.md`. Rendering claims below rest on the dated [rendering notes](assets/rendering-notes.md); when a host behaves differently, follow the fallback and update those notes.

## Output contract

Every figure is an opaque white PNG, 6.5 in wide at 200 dpi (1300 px), plus a compact Markdown table of the numbers the figure claims. Those two together are the deliverable in chat and the unit that travels into documents.

- **Why PNG**: Google Docs rejects SVG, Microsoft 365 accepts it, and VS Code Copilot Chat displays a generated PNG inline (user-confirmed). PNG is the one format every destination accepts.
- **Why 6.5 in at 200 dpi**: 6.5 in is the text width of a Letter or A4 page with about 1 in margins, so the figure fits the page at 100% and fonts keep their stated point sizes; if Word inserts it at another size, set the width to 6.5 in. 200 ppi stays under Microsoft 365's default 220 ppi compression, so Word keeps the pixels. Shown at half size in a narrow chat panel, 10 pt text is still about 14 px tall, and the chat image viewer zooms to full size.
- **Why opaque white**: a transparent background puts dark text on a dark chat theme and changes with every document background. White reads the same on both.
- **Why the table**: it carries the result where an image does not display (other hosts, screen readers, plain-text email), and it makes every plotted claim checkable. Values match the figure and the narrative exactly.
- Write an SVG beside the PNG only when the user wants a vector figure for Word or PowerPoint. Keep PNG for Google Docs and email.
- In chat, embed the image in the form the current host displays: an absolute filesystem path unless the host is known to resolve workspace-relative paths, since some hosts display local images only from absolute paths. Also give the path as a link, then show the table. When the image does not display, rely on the link and table and record the host's behavior in the rendering notes. Use local files; remote image URLs and data URIs are not confirmed to render.
- In saved records and package documents, link figures by paths relative to that document so the files stay portable.
- Generate figures in answer to an analytical request or for package work. Write additional formats, galleries, or documents only on explicit request.

## Workbench placement

- Figure code is presentation. Neutral operations in `src/exploration/` return data; figure functions take those results and draw them. A figure function computes no finding, filter, or exclusion of its own. A classification made only for display, such as a highlight threshold, lives in the investigation's figure script, not in shared builders, and the caption states it.
- Plot from canonical DuckDB views or in-process results: `con.sql(query).df()` for pandas or `.pl()` for polars, then plot. Pass frames in memory; never write a CSV for a figure to read.
- Plot the estimates and intervals the analysis computed. seaborn's built-in aggregation and bootstrap (`estimator`, `errorbar`) suit exploration; a figure supporting a finding draws precomputed values (`errorbar=None` with `ax.errorbar` or `ax.fill_between`) so the figure, the table, and the record agree. When seaborn bootstraps, pass `seed=`.
- Shared style lives in one place, created the first time a project figure needs it: copy [awb_style.py](assets/awb_style.py) to `src/presentation/style.py` and import it from there. Reusable figure builders join it in `src/presentation/`. Never import from the skill folder.
- Exploratory figures go to `investigations/<name>/exploration/figures/` and may be overwritten. A figure cited as evidence for a finding goes to `investigations/<name>/figures/<slug>.png`, created on first use. Package figures follow `awb-package`; they reuse the evidence figure unless separate analytical work changed the result.
- For an evidence figure, pass its path as `figure=` to `record_evidence` so the finding's evidence file records it, and embed the producing commit (and any uncommitted producing changes), input view or acquisition identifiers, and settings with `save_figure(fig, path, provenance={"Source": ..., "Comment": ...})`, which writes PNG text metadata.

## Tools

- **seaborn 0.13** for statistical and categorical plots from tidy frames; it accepts pandas and polars. Use `errorbar=` (`None`, `("ci", 95)`, `"se"`, `("pi", 50)`); `ci=` is the pre-0.12 spelling. A palette applies only with `hue` assigned. Pass `saturation=1` to `barplot` so palette colors render exactly.
- **matplotlib** for layout, annotation, tick formatting, and saving. Create figures with `fig, ax = plt.subplots()` so the shared size and constrained layout apply, and close each with `plt.close(fig)` (done by `save_figure`).
- `seaborn.objects` is documented as experimental; keep it out of shared figure code.
- Interactive libraries (plotly, altair, bokeh) produce HTML or JavaScript. VS Code chat renders HTML only through an extension's output renderer and documents cannot run it, and static export needs extra engines. Use them only when the user asks for an interactive file, and still deliver the PNG and table.

## Chart form

Choose the form from the comparison the reader must make, then state that comparison in the title.

| Comparison | Form | Call |
| --- | --- | --- |
| Rank or compare categories | Sorted horizontal bars | `sns.barplot(df, y=cat, x=val, order=sorted_cats, saturation=1)` then `ax.bar_label(c, fmt="{:,.0f}", padding=3)` per container |
| Estimates with intervals across groups | Dots and interval lines | `sns.pointplot(..., errorbar=None, linestyle="none")` plus `ax.errorbar` from computed bounds |
| Change over time | Lines, few series | `sns.lineplot(df, x=date, y=val, hue=series)`; label line ends with `ax.annotate` |
| Distribution | Histogram, ECDF, or boxes by group | `sns.histplot`, `sns.ecdfplot`, `sns.boxplot` |
| Relationship | Scatter | `sns.scatterplot(alpha=0.5)`; draw fitted lines from analysis results, not `regplot` |
| Two-way grid of values | Annotated heatmap | `sns.heatmap(pivot, annot=True, fmt=",.0f", cmap="Blues")`; diverging `"RdBu_r"` with `center=0` for signed change |
| Same view across groups | Small multiples | `plt.subplots(1, n, sharey=True)` with axes-level calls; `sns.relplot`/`sns.catplot` for exploration (sized by `height` and `aspect`, and they switch to tight layout) |

Use bars for part-to-whole beyond three parts rather than pies. Put a second measure in its own panel instead of a second y axis. Keep every mark two-dimensional.

## Style defaults

`apply_style()` in the shared style module sets these; change them there, once, for the project.

- **Size**: 6.5 x 4.0 in for a single panel, up to 6.5 x 5.0 in (`TALL_HEIGHT_IN`) when row labels or a multi-line caption need the height; 6.5 x 2.6 to 3.0 in for a row of small multiples. Keep the 6.5 in width so figures in one document line up.
- **Type**: sans-serif (Arial, falling back to Helvetica, Liberation Sans, DejaVu Sans). Title 13 pt bold, left-aligned; axis labels 11 pt; ticks, legend, and value labels 10 pt; caption 9 pt; panel titles 11 pt via `ax.set_title(name, fontsize=11)`. Nothing smaller than 9 pt at 6.5 in.
- **Color**: Okabe-Ito hues. One accent `#0072B2` marks what the title is about; non-focal marks are `#A6A6A6`; text is `#333333`; gridlines are `#E5E5E5`. Add `#D55E00` for a second highlighted group. Use at most six categorical hues (`SUPPORT`); beyond that, group the remainder as Other or use small multiples. Highlight with `hue=is_focus, palette={True: ACCENT, False: GREY_CONTEXT}, legend=False`.
- **Furniture**: top and right spines off; no gridlines when values are labeled directly, otherwise a light grid on the value axis only (`ax.grid(axis="x")`). Direct labels replace legends when there are four series or fewer.
- **Numbers**: format ticks with `matplotlib.ticker`: `PercentFormatter(xmax=1, decimals=0)` for proportions, `StrMethodFormatter("{x:,.0f}")` for counts, `FuncFormatter(lambda v, _: f"{v / 1e6:.1f}M")` for large values, and `mdates.ConciseDateFormatter` for dates. Use the same rounding as the narrative.
- **Text**: the title states the finding neutrally in a sentence with the number ("West closes 12% of cases late, the second-lowest rate"), not a topic ("Late closures by region"). Axis labels name the measure and unit in plain words, never a column name. `add_caption(fig, text)` writes the 9 pt line below the axes: unit, population, period, n, source view, and exclusions.

## Honest display

- Bars start at zero. A line chart may use a non-zero baseline when the caption says so. Small multiples share scales unless the caption says otherwise. Label any log scale.
- Show uncertainty whenever the analysis estimated it, and say in the caption what the interval is.
- Keep results that contradict the expected explanation visible: plot every category, period, and outlier the analysis returned. When something is excluded or capped, say what and why in the caption.
- Put a caveat beside the value it affects (an annotation or a marked label with the reason in the caption), not only in surrounding prose.
- Write alt text for every image: one or two sentences giving the finding and its key numbers, not the chart type alone. The same text goes in the Markdown alt and travels with the figure into documents.

## Tables in chat

- Prefer a table to a chart when there are about six numbers or fewer, when exact values matter more than shape, or when the reader will look values up.
- Keep chat tables to about six columns and fifteen rows; split or summarize wider results and point to the full result.
- Right-align numeric columns (`---:`), put units in headers, use thousands separators, and give a percentage column one decimal precision throughout. Round only for display, with the same rounding as the narrative and the figure.
- Order rows by the comparison (descending value, or time), include n where rates are shown, and mark caveated cells with a footnote marker explained under the table.
- For a document, copy the rendered table rather than its Markdown source, and verify the paste; raw Markdown pasted into desktop Word stays literal text. Package tables reach Word through the M365 assembly.

## Diagrams

- Mermaid renders in VS Code chat (1.109 and later) and in Visual Studio 2022 17.14 and later; use it there for process, lineage, and relationship diagrams. Elsewhere, including github.com chat, treat rendering as unconfirmed and keep the source in a fenced `mermaid` block.
- Documents do not render Mermaid. For a diagram headed into a document, export a PNG with mermaid-cli (`mmdc -i diagram.mmd -o diagram.png -w 1300 -b white`) when it is installed or the user approves installing it; otherwise give the structure as a list or table.

## Pre-delivery checklist

Run this against each figure before showing or packaging it; every item is yes.

1. PNG is 1300 px wide, opaque white, and nothing is clipped at the edges. Matplotlib writes RGBA PNGs; with the white facecolor every alpha value is fully opaque, which satisfies this item.
2. The title states the finding in a sentence, and the chart form makes that comparison directly.
3. Every number in the title, labels, and table matches the analytical result and the narrative's rounding.
4. No text is below 9 pt at 6.5 in; axis labels carry units in plain words.
5. One accent color marks the message; categorical hues number six or fewer; nothing relies on color alone.
6. Bars start at zero, small multiples share scales, and no dual axes or 3D appear.
7. Caption gives unit, population, period, n, source, and any exclusion; caveats sit beside affected values; intervals are shown and explained when estimated.
8. Contrary results and outliers the analysis returned are visible or explicitly noted.
9. Alt text states the finding and key numbers; a Markdown table of the plotted numbers accompanies the image.
10. Evidence figures have provenance in the finding's evidence file and PNG metadata.
