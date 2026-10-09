---
name: awb-visualize
description: Create analytics workbench charts, figures, diagrams, and formatted results tables. Use whenever a visual or a results table is produced for chat, an investigation record, or a delivery package.
---

# Visualize workbench results

Present analytical results so they remain legible in chat and documents. Resolve project paths from the repository root and bundled paths relative to this skill.

## Choose the output

Read only the branches needed for the requested output:

- **Tables:** read [tables](references/tables.md), including for a chart's companion table. Prefer a table when there are about six numbers or fewer, exact values matter more than shape, or readers need lookup.
- **Charts and plotted figures:** read [charts](references/charts.md) for analytical boundaries, honest display, style, and verification. For library calls or style-helper usage, consult [plotting recipes](references/plotting-recipes.md).
- **Diagrams:** read [diagrams](references/diagrams.md) for process, lineage, and relationship diagrams, including document export and fallback.
- **Image delivery:** before showing or saving a chart or exported diagram, read [figure delivery](references/figure-delivery.md) for PNG, document caption, and table output, placement, accessibility, and evidence provenance.
- **Rendering problems:** consult the dated [rendering notes](assets/rendering-notes.md) for host support, rationale, and fallbacks; update them when observed behavior changes.

## Shared contract

Presentation consumes results from neutral analytical operations in `src/exploration/`; it computes no finding, analytical filter, or exclusion. Keep display-only classifications in the investigation's presentation code and explain them beside the result. Pass frames in memory from canonical DuckDB views or in-process results, rather than creating CSV intermediates.

Use the analysis's estimates, intervals, categories, periods, and outliers. Every displayed number must match the analytical result and the narrative's rounding. Keep contrary results visible; explain any exclusion or cap, and place caveats beside the values they affect. Round only for display.

Produce visuals for the analytical request or authorized package work. Additional formats, galleries, and documents require an explicit request. Completion means the selected branch's checks pass and any evidence figure is recorded with provenance.
