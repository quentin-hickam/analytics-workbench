# Figure delivery and evidence

Charts and exported diagram images use an opaque white PNG, 6.5 in wide at 200 dpi (1300 px), a caption in the containing document, and a compact Markdown table matching the figure and narrative. Use a structure table for a diagram without numerical claims; read [tables](tables.md) for formatting. A user-requested vector figure for Word or PowerPoint may add an SVG; retain PNG for Google Docs and email. Interactive files retain PNG, document caption, and table deliverables.

## Placement and provenance

- Exploratory figures go to `investigations/<name>/exploration/figures/` and may be overwritten. Evidence figures go to `investigations/<name>/figures/<slug>.png`, created on first use.
- Package figures follow `awb-package`: reuse an evidence figure that passes `check_text` and draws no caption. Re-render legacy figures with captions in the image or raw labels for presentation from the plotted numbers in their recorded tables, without running analytical code. Separate analytical work that changes the result needs a new evidence figure.
- For an evidence figure, pass its path as `figure=` to `record_evidence`. Embed the producing commit (and any uncommitted producing changes), input view or acquisition identifiers, and settings in PNG text metadata. For matplotlib use `save_figure(fig, path, provenance={"Source": ..., "Comment": ...})`; preserve equivalent metadata with other renderers. Technical identifiers belong only in metadata and the evidence file, never in image text or its caption.

## Caption and display

Write the caption in the document containing the image, never draw it inside the image. Give the full finding/comparison sentence, unit, population, period, n, source in plain words (data owner, extract, period), exclusions, interval meaning, baseline/scale notes, display thresholds, and caveat reasons as applicable. Name no view, column, setting, or file.

Write one or two sentences of alt text stating the finding and key numbers (or relationships for a structural diagram). Use it in Markdown and carry it into documents.

In chat, embed using an absolute filesystem path unless the host is known to resolve workspace-relative paths. Place an italic caption directly under the image, then a file link and table. Saved records and package documents use relative paths for portability: a record's caption sits beside the figure link; a package's italic `*Figure N. ...*` line sits directly under the embedded image in `findings.md` for M365 assembly. Use local images; remote URLs and data URIs have unconfirmed support.

## Delivery checks

Inspect the rendered image for clipping, raw labels, and legibility; verify width, full opacity, and that image, external caption, table, narrative, alt text, and evidence references agree. Matplotlib's RGBA PNG is acceptable when every alpha value is fully opaque. In a document, check the inserted width and set it to 6.5 in when needed.

If the host does not display the image, provide the caption, link, and table, then record its behavior in the [rendering notes](../assets/rendering-notes.md). Those notes contain the output rationale and dated host-support evidence; load them when diagnosing rendering or changing the output contract.
