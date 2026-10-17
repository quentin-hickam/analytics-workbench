# Deck rules

`findings.md` is the slide-by-slide outline of the deck and the authoritative source of every word and number on it; the files in `charts/` hold every plotted value. Both are already written for the deck's audience, in their terms. Whoever builds the deck from them, a person, an agent, or a script, follows these rules and preserves every slide, claim, value, qualification, and caveat. A builder's own steps, such as how to attach the files or which chart objects to use, are in its file under `assembly/`; where that file and these rules differ on content, these rules govern.

## Before you start

You have `findings.md`, every `charts/` file, `methodology.md`, these rules, and your builder's assembly file; datasets, and `methodology-note.md` when the package has one, travel beside the deck and are not attached.

## Using methodology.md

Use `methodology.md` to understand reasoning, or to answer the requester's question about a decision in plain language; its sections for each finding use the same headings as the finding slides. Slides and notes use only the outline's words, so never quote it or copy its identifiers, file names, settings, or code terms. A method point only it holds is a gap: raise it as in **Ask before building**.

## Ask before building

Before building the deck, check for the conditions below. When one holds, ask the requester before building. Put every question in one message, keep each to a sentence or two, and propose a default the requester can accept with a yes. A builder that cannot ask, such as a script, reports each condition it finds instead.

- **Audience or decision differs.** The requester names readers or a decision that differ from the deck's subtitle line and **Answer** slide. Example: "The deck is written for regional operations managers deciding on staffing. Is it for them, or for the finance committee? Default: regional operations managers."
- **A slide will not fit.** A slide's bullets and chart cannot fit at the minimum text sizes below. Example: "The third finding slide has five bullets and a chart and will not fit at 18 pt. Should I split it into two slides with the same headline continued? Default: yes, split it."
- **A chart cannot be drawn as specified.** Its chart file lacks a column the specification names, the form cannot show those columns, or a Stacked bar's file holds a part below zero. Example: "Chart 2 asks for intervals but its file has no interval columns, so I cannot draw it as specified. Default: build the rest, leave Chart 2 as a marked placeholder, and report the deck as incomplete until the analyst corrects the package."
- **A caveat's effect on a headline is ambiguous.** It is unclear whether a caveat narrows, weakens, or leaves intact the headline it sits under. Example: "The late-closure headline carries a caveat about missing March records. Keep the headline as written with the caveat bullet beneath it? Default: yes."
- **A slide needs method context that only `methodology.md` has.** A reader could not trust or interpret the slide from the outline alone. Example: "The second finding depends on how repeat cases are counted, which only the internal notes explain. Should I flag this for the analyst to add? Default: yes, and build now from what the outline says, with the gap noted to you."

When none holds, build without asking.

## Build the deck

- **One slide per outline slide.** The `#` heading and subtitle line make the title slide. Each `##` section is one slide, except **Findings** and **Appendix**, each of which becomes a section of the deck holding one slide per `###` heading. Start the appendix with a divider slide titled "Appendix". Keep the outline's order; add no slide but that divider, and drop none.
- **Headlines verbatim.** A finding slide's `###` heading, or the text after a slide's **Headline:**, goes in the slide's title as written.
- **Bullets verbatim.** Every bullet, number, rounding, unit, and qualifier as written; tighten wording only where no claim, number, or qualifier changes.
- **Caveats stay on their slide.** A **Caveat:** or **Awaiting revalidation:** bullet stays on the slide of the claim it qualifies, visible on the slide, not only in the notes.
- **Notes.** The **Notes:** paragraph goes into the slide's speaker notes, unchanged in substance.
- **Nothing new.** Add no claim, metric, comparison, recommendation, or summary slide that the outline does not make. The **Answer** slide is the executive summary.

## Charts

Draw each chart as an editable chart whose data is its file in `charts/`, not as a picture. Chart data verbatim: plot every row of its file, in the file's order, at the file's values. The file's numbers arrive rounded, and a percent column already holds percents (21.3, not 0.213): plot them as written, never multiplying a percent by 100 again. When a chart cannot be drawn from its file, or its data does not match the file, say so to the requester and name the slide; never substitute an image or estimated values.

### Chart forms

The specification names one of these forms. Its **Data:** line names every column of the file by role, each as `role: column header` with the header as the file writes it, separated by semicolons, such as `category: Region; value: Closed late (%)`. A role names the column whose header reads the same once both are NFKC-normalized with zero-width characters dropped, as `check-draft` compares them, since the line renders `CO₂` as `CO2`: find each column that way, and label it with the file's header text.

| Form | Use for | Data roles | Build |
| --- | --- | --- | --- |
| Horizontal bar | Ranking or comparing categories | `category`, one or more `value`, or one `value` with a `series` | Clustered bar, categories in the file's order, bars from zero |
| Bar with intervals | Estimates with intervals across groups | `category`, `value`, `lower`, `upper` | Clustered bar with custom error bars from the file's lower and upper columns |
| Line | Change over time, a few series | `category` (the period), one or more `value`, or one `value` with a `series` | Line chart, time on the horizontal axis; label line ends instead of a legend when there are four series or fewer |
| Column | A few categories with short labels, or counts by period | `category`, one or more `value`, or one `value` with a `series` | Clustered column, columns from zero |
| Stacked bar | Part-to-whole across categories, each part zero or more | `category`, one or more `value`, or one `value` with a `series` | 100% stacked bar; use instead of a pie whenever there are more than three parts |
| Scatter | Relationship between two measures | `x`, `y`, and optionally `label` and `fit` | Scatter chart; a fitted line only when the file carries its values |
| Table | About six numbers or fewer, or a two-way grid of values | one `column` per table column, in order | Table, numbers right-aligned, units in the header row, optional color fill in one hue by value |

A `series` column splits one `value` column into a series per distinct entry, in the order each first appears in the file. Only Bar with intervals takes `lower` and `upper` columns and draws intervals; a Table may show the bounds as columns of their own. Never use 3D, a second value axis, or decorative effects. Put a second measure in its own chart rather than on a second axis.

### Style

- **Title:** none on the chart; the slide headline states the finding.
- **Axis titles:** the measure and its unit, from the file's header in the audience's words; omit one only when the category labels speak for themselves.
- **Labels:** categories, series names, and legend entries exactly as the file writes them.
- **Color:** the theme's accent `#0072B2` marks the **Highlight** group and grey `#A6A6A6` the rest; `#D55E00` marks a second highlighted group. With no highlight, color series with at most six hues from `#0072B2`, `#E69F00`, `#009E73`, `#D55E00`, `#CC79A7`, `#56B4E9`, and any further series grey, each still labeled; never combine series or categories. Text is `#333333`. When the organization's theme is applied, keep one accent for the highlight and grey for context in its palette. Never rely on color alone: the headline or a data label names the highlighted group.
- **Text size:** no chart text below 12 pt; data labels and axis labels 12 to 14 pt.
- **Data labels:** on the highlighted marks, or on every mark when there are six or fewer, in the number format the slide uses (thousands separators, the same decimals). When values are labeled, remove gridlines; otherwise keep light `#E5E5E5` gridlines on the value axis only.
- **Furniture:** no chart border, no top or right axis line, no shadows.

### Source, caveat, and alt text

- Put the **Source:** text in a small line (10 to 12 pt) directly under the chart.
- For a **Caveat:**, mark the affected value with an asterisk on its data label or category, and put the reason after the source line, beginning with an asterisk. The caveat bullet on the slide stays.
- Set the chart's alt text from **Alt text:**.

### Honest display

- Bars and columns start at zero. A Horizontal bar, Bar with intervals, Column, or Line value axis spans zero and every value and interval bound in the file, negative values included, unless a line chart's **Axis:** says `non-zero baseline` and gives the reason; keep that reason in the source line. Any other wording keeps zero on the axis. A Stacked bar's axis runs from 0 to 100%, so each part is zero or more.
- Draw intervals whenever the file carries them, and state what they mean in the source line from **Interval:**.
- Keep every category, period, and outlier the file holds, including results that contradict the headline.
- Charts across the deck that show the same measure use the same scale unless **Axis:** says otherwise.

## Supporting datasets

Deliver each dataset file beside the deck as supplied; the **Supporting datasets** slide is its only presence in the deck. Deliver `methodology-note.md`, when the package has one, beside the deck unchanged; it adds no slide.

## Theme and accessibility

Apply the organization's approved template, typography, and page furniture when available. Keep every headline in its slide's title so the reading order and slide titles stay correct, keep body text at 18 pt or larger, and check the deck's accessibility with the tools the builder has.

## Revision boundary

When a requested change affects the storyline, wording, findings, numbers, charts, scope, or dataset contents, do not make it in the deck: tell the requester that it needs a revised package from the workbench, and build the deck again from the refreshed package. Layout, theme, and visual polish within the rules above are made in the deck; they are not carried back to the workbench.

## Before handing back

Confirm: one slide per outline slide, in order, with the appendix divider when the outline has an appendix; every chart drawn from its file; every **Caveat:** and **Awaiting revalidation:** bullet visible on its slide; and what your builder's assembly file adds.
