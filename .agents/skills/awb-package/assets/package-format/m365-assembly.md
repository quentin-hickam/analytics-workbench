# M365 assembly instructions

`findings.md` is the slide-by-slide outline of the deck and the authoritative source of every word and number on it; the files in `charts/` hold every plotted value. Both are already written for the audience below, in their terms. In the Microsoft 365 Copilot app, use the PowerPoint agent to build the deck from them and improve its presentation, while preserving every slide, claim, value, qualification, and caveat.

## Audience

The draft replaces this section with the investigation brief's **Audience** section:

- **Readers:** who will see or present the deck.
- **What they already know:**
- **Decision they own:**
- **Terms they use:**

## Files in this package

The draft replaces this list with every file it includes, one path per line relative to the package directory. Write **None** under charts or datasets when the package has none.

- `findings.md`: the deck outline; the source of all slide content.
- `methodology.md`: internal reference for the reasoning behind decisions; never shown.
- `m365-assembly.md`: these instructions; never shown.
- `manifest.<format>`: provenance record; never shown.
- Charts: `charts/chart-N.csv`, one file per chart, `chart-1.csv` holding the data for the specification **Chart 1.** in `findings.md`, and so on.
- Datasets: `datasets/<dataset>.<format>`, each described on the **Supporting datasets** slide; delivered beside the deck, never charted.

## Before you start

The requester starts a chat in the Microsoft 365 Copilot app, adds the PowerPoint agent to the prompt, and attaches `findings.md`, every file in `charts/`, `methodology.md`, and these instructions; the datasets are not attached. The prompt asks for a deck built under these instructions.

## Using methodology.md

Consult `methodology.md` to understand why a decision was made, or to answer the requester's question about one in plain language. Its sections for each finding use the same headings as the finding slides. Never quote it, and never copy its identifiers, file names, settings, or code terms onto a slide or into notes. If a slide needs a method point that only `methodology.md` has, do not add it: raise it with the requester as a gap to fix upstream in the workbench.

## Ask before building

Before building the deck, check for the conditions below. When one holds, ask the requester before building. Put every question in one message, keep each to a sentence or two, and propose a default the requester can accept with a yes.

- **Audience or decision differs.** The **Audience** section above is blank, or the requester names readers or a decision that differ from it. Example: "The deck is written for regional operations managers deciding on staffing. Is it for them, or for the finance committee? Default: regional operations managers."
- **A slide will not fit.** A slide's bullets and chart cannot fit at the minimum text sizes below. Example: "The third finding slide has five bullets and a chart and will not fit at 18 pt. Should I split it into two slides with the same headline continued? Default: yes, split it."
- **A chart cannot be drawn as specified.** Its chart file lacks a column the specification names, or the form cannot show those columns. Example: "Chart 2 asks for intervals but its file has no interval columns. Should I draw it without intervals and flag it to the analyst? Default: yes."
- **A caveat's effect on a headline is ambiguous.** It is unclear whether a caveat narrows, weakens, or leaves intact the headline it sits under. Example: "The late-closure headline carries a caveat about missing March records. Keep the headline as written with the caveat bullet beneath it? Default: yes."
- **A slide needs method context that only `methodology.md` has.** A reader could not trust or interpret the slide from the outline alone. Example: "The second finding depends on how repeat cases are counted, which only the internal notes explain. Should I flag this for the analyst to add? Default: yes, and build now from what the outline says, with the gap noted to you."

When none holds, build without asking.

## Build the deck

- **One slide per outline slide.** The `#` heading and subtitle line make the title slide. Each `##` section is one slide, except **Findings**, which becomes a PowerPoint section holding one slide per `###` finding. Keep the outline's order; add no slide, and drop none.
- **Headlines verbatim.** The `###` heading, or the text after **Headline:**, goes in the slide's title placeholder as written.
- **Bullets as written.** Keep every bullet, number, rounding, unit, and qualifier exactly as the outline gives them; never re-round, recompute, or combine them. You may tighten wording only where no claim, number, or qualifier changes.
- **Caveats stay on their slide.** A **Caveat:** or **Awaiting revalidation:** bullet stays on the slide of the claim it qualifies, visible on the slide, not only in the notes.
- **Notes.** The **Notes:** paragraph goes into the slide's speaker notes, unchanged in substance.
- **Nothing new.** Add no claim, metric, comparison, recommendation, or summary slide that the outline does not make. The **Answer** slide is the executive summary.
- **No internal names** on slides, in notes, or in alt text: no file names, paths, or internal names of any kind.

## Charts

Build each chart as a native, editable PowerPoint chart whose data is its file in `charts/`, not as a picture. Plot every row of the file in the file's order, and never retype, recompute, round, aggregate, filter, or re-sort the values. When a chart cannot be built as a native chart from its file, or its data does not match the file, say so to the requester and name the slide, so they can insert the chart in PowerPoint and paste the file's values into its data; never substitute an image or estimated values.

### Chart forms

The specification names one of these forms.

| Form | Use for | Build |
| --- | --- | --- |
| Horizontal bar | Ranking or comparing categories | Clustered bar, categories in the file's order, value axis from zero |
| Bar with intervals | Estimates with intervals across groups | Clustered bar with custom error bars from the file's lower and upper columns |
| Line | Change over time, a few series | Line chart, time on the horizontal axis; label line ends instead of a legend when there are four series or fewer |
| Column | A few categories with short labels, or counts by period | Clustered column, value axis from zero |
| Stacked bar | Part-to-whole across categories | 100% stacked bar; use instead of a pie whenever there are more than three parts |
| Scatter | Relationship between two measures | Scatter chart; a fitted line only when the file carries its values |
| Table | About six numbers or fewer, or a two-way grid of values | PowerPoint table, numbers right-aligned, units in the header row, optional color fill in one hue by value |

Never use 3D, a second value axis, or decorative effects. Put a second measure in its own chart rather than on a second axis.

### Style

- **Title:** none on the chart; the slide headline states the finding.
- **Axis titles:** the measure and its unit, from the file's header in the audience's words; omit one only when the category labels speak for themselves.
- **Labels:** categories, series names, and legend entries exactly as the file writes them.
- **Color:** the theme's accent `#0072B2` marks the **Highlight** group and grey `#A6A6A6` the rest; `#D55E00` marks a second highlighted group. With no highlight, use at most six hues from `#0072B2`, `#E69F00`, `#009E73`, `#D55E00`, `#CC79A7`, `#56B4E9`, and group the rest as Other. Text is `#333333`. When the organization's theme is applied, keep one accent for the highlight and grey for context in its palette. Never rely on color alone: the headline or a data label names the highlighted group.
- **Text size:** no chart text below 12 pt; data labels and axis labels 12 to 14 pt.
- **Data labels:** on the highlighted marks, or on every mark when there are six or fewer, in the number format the slide uses (thousands separators, the same decimals). When values are labeled, remove gridlines; otherwise keep light `#E5E5E5` gridlines on the value axis only.
- **Furniture:** no chart border, no top or right axis line, no shadows.

### Source, caveat, and alt text

- Put the **Source:** text in a small line (10 to 12 pt) directly under the chart.
- For a **Caveat:**, mark the affected value with an asterisk on its data label or category, and put the reason after the source line, beginning with an asterisk. The caveat bullet on the slide stays.
- Set the chart's alt text from **Alt text:**.

### Honest display

- Bars and columns start at zero. A line chart uses a non-zero baseline only when **Axis:** says so; keep the reason in the source line.
- Draw intervals whenever the file carries them, and state what they mean in the source line from **Interval:**.
- Keep every category, period, and outlier the file holds, including results that contradict the headline.
- Charts across the deck that show the same measure use the same scale unless **Axis:** says otherwise.

## Supporting datasets

Deliver each dataset file beside the deck as supplied. Do not chart it, summarize it on slides, or build workbooks from it; the **Supporting datasets** slide describes it.

## Theme and accessibility

Apply the organization's approved template, typography, and page furniture when available. Keep every headline in its slide's title placeholder so the reading order and slide titles stay correct, keep body text at 18 pt or larger, and run PowerPoint's accessibility checker before handing the deck back.

## Revision boundary

When a requested change affects the storyline, wording, findings, numbers, charts, scope, or dataset contents, make that revision in the upstream workbench draft, send the refreshed package forward, and build the deck again. Deck edits are not synchronized back into the workbench. Layout, theme, and visual polish within the rules above are made here.
