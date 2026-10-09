# Charts and plotted figures

Choose the form from the comparison the reader must make. State the finding neutrally with its number in a one-line title of at most 65 characters; put the full comparison sentence in the document caption. All image text uses glossary display names and plain business language.

## Analysis and placement

Figure functions take analytical results and draw them. Plot precomputed estimates and intervals for findings so the figure, companion table, and record agree. Library aggregation and bootstrap are for exploration; seed any bootstrap. Shared builders belong in `src/presentation/`, while display-only classifications belong in the investigation's figure script and document caption.

On the first project figure, copy [awb_style.py](../assets/awb_style.py) to `src/presentation/style.py` and import from the project module. That module is authoritative for dimensions, DPI, fonts, palette values, and other implemented defaults; change defaults there once per project. Consult [plotting recipes](plotting-recipes.md) when calling its helpers or choosing library calls. Read [figure delivery](figure-delivery.md) before delivery and [tables](tables.md) for the companion table.

## Form and style

- Use sorted horizontal bars for categories, dots and intervals for estimates, lines for time, histograms/ECDFs/boxes for distributions, scatter for relationships, and annotated heatmaps for grids. Use small multiples for the same view across groups.
- For part-to-whole beyond three parts, use bars. Place a second measure in a separate panel; keep marks two-dimensional.
- Keep the shared page width. Use `TALL_HEIGHT_IN` for many row labels; a row of small multiples can use 2.6–3.0 in height. Nothing is below 9 pt at full page width; panel titles use 11 pt.
- Use `ACCENT` for the message and `GREY_CONTEXT` for context; `CONTRAST` highlights a second group. Use at most six categorical hues from `SUPPORT`; group additional categories as Other with disclosure or use small multiples. Color must not be the only cue.
- Direct labels replace legends for four series or fewer. Remove gridlines when values are directly labeled; otherwise use a light grid on the value axis only.
- Map raw codes to display names before plotting. Explicitly set both axis labels, using an empty label when ticks speak for themselves; name measures and units. Rename automatic legend titles and facet titles. Every title, tick, legend entry, facet, and annotation must use business language, including short codes that automated checks cannot recognize.
- Label focal marks, or every mark when there are six or fewer. Allow at most one short annotation per caveated value; explain its reason in the document caption. Draw no caption, source line, or notes in the image. See [figure delivery](figure-delivery.md) for caption content and placement.

## Honest display and verification

Here, “caption” means the caption in the document containing the image. Before delivery, confirm:

1. The form supports the short title's comparison; title, labels, and table match analytical values and narrative rounding.
2. Bars start at zero. A non-zero line baseline or unequal small-multiple scales are disclosed in the caption. Log scales are labeled; there are no dual axes or 3D marks.
3. Every estimated interval is visible and identified in the caption. Contrary categories, periods, and outliers returned by the analysis remain visible or are explicitly noted with reasons for exclusions or caps.
4. Caveats appear beside affected values as short annotations or marked labels explained in the caption.
5. `save_figure`'s `check_text` passes. Inspect the rendered image for column names or raw codes in all text elements, including single-word names and short codes the check cannot detect. Confirm legibility, font sizes, hue limits, a second cue for color, and no caption inside the image.
6. The document caption is complete and the [figure-delivery checks](figure-delivery.md) pass, including the companion table and evidence metadata when applicable.
