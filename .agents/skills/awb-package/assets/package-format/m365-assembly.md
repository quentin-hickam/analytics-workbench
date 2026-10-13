# M365 assembly instructions

`findings.md` is the slide-by-slide outline of the deck and the authoritative source of every word and number on it. The files in `charts/` hold every plotted value. Both are already written for the audience of the deck, in their terms. In the Microsoft 365 Copilot app, use the PowerPoint agent to build the deck from them and to improve its presentation. Keep every slide, claim, value, qualification, and caveat.

## Before you start

You have `findings.md`, every `charts/` file, `methodology.md`, and these instructions. Datasets travel beside the deck and are not attached.

## Using methodology.md

Use `methodology.md` to understand reasoning, or to answer a question from the requester about a decision in plain language. Its sections for each finding use the same headings as the finding slides. Slides and notes use only the words of the outline. For this reason, never quote `methodology.md`, and never copy its identifiers, file names, settings, or code terms. If only `methodology.md` holds a method point, that point is a gap. Raise it as in **Ask before building**.

## Ask before building

Before you build the deck, check for the conditions below. If one condition is true, ask the requester before you build. Put every question in one message. Keep each question to one or two sentences. Propose a default that the requester can accept with a yes.

- **Audience or decision differs.** The requester names readers or a decision that are different from the subtitle line and **Answer** slide of the deck. Example: "The deck is written for regional operations managers deciding on staffing. Is it for them, or for the finance committee? Default: regional operations managers."
- **A slide will not fit.** The bullets and chart of a slide cannot fit at the minimum text sizes below. Example: "The third finding slide has five bullets and a chart and will not fit at 18 pt. Should I split it into two slides with the same headline continued? Default: yes, split it."
- **A chart cannot be drawn as specified.** Its chart file does not have a column that the specification names, or the form cannot show those columns. Example: "Chart 2 asks for intervals but its file has no interval columns, so I cannot draw it as specified. Default: build the rest, leave Chart 2 as a marked placeholder, and report the deck as incomplete until the analyst corrects the package."
- **A caveat's effect on a headline is ambiguous.** It is not clear if a caveat narrows, weakens, or does not change the headline that it is under. Example: "The late-closure headline carries a caveat about missing March records. Keep the headline as written with the caveat bullet beneath it? Default: yes."
- **A slide needs method context that only `methodology.md` has.** A reader cannot trust or interpret the slide from the outline alone. Example: "The second finding depends on how repeat cases are counted, which only the internal notes explain. Should I flag this for the analyst to add? Default: yes, and build now from what the outline says, with the gap noted to you."

If no condition is true, build the deck and do not ask.

## Build the deck

- **One slide per outline slide.** The `#` heading and the subtitle line make the title slide. Each `##` section is one slide, except **Findings**. **Findings** becomes a PowerPoint section that holds one slide for each `###` finding. Keep the order of the outline. Do not add a slide, and do not remove a slide.
- **Headlines verbatim.** The `###` heading, or the text after **Headline:**, goes in the title placeholder of the slide, as written.
- **Bullets verbatim.** Use every bullet, number, rounding, unit, and qualifier as written. You can tighten the wording only where no claim, number, or qualifier changes.
- **Caveats stay on their slide.** A **Caveat:** or **Awaiting revalidation:** bullet stays on the slide of the claim that it qualifies. It is visible on the slide, not only in the notes.
- **Notes.** The **Notes:** paragraph goes into the speaker notes of the slide. Do not change its substance.
- **Nothing new.** Do not add a claim, metric, comparison, recommendation, or summary slide that the outline does not make. The **Answer** slide is the executive summary.

## Charts

Build each chart as a native, editable PowerPoint chart, not as a picture. The data of the chart is its file in `charts/`. Chart data verbatim: plot every row of its file, in the order of the file, at the values in the file. If you cannot build a chart as a native chart from its file, or if its data does not match the file, tell the requester and name the slide. Then the requester can insert the chart in PowerPoint and paste the values of the file into its data. Never use an image or estimated values as a replacement.

### Chart forms

The specification names one of these forms.

| Form | Use for | Build |
| --- | --- | --- |
| Horizontal bar | To rank or compare categories | Clustered bar, categories in the file's order, value axis from zero |
| Bar with intervals | Estimates with intervals across groups | Clustered bar with custom error bars from the file's lower and upper columns |
| Line | Change over time, a few series | Line chart, time on the horizontal axis. If there are four series or fewer, label the line ends instead of a legend |
| Column | A few categories with short labels, or counts by period | Clustered column, value axis from zero |
| Stacked bar | Part-to-whole across categories | 100% stacked bar. If there are more than three parts, use it instead of a pie |
| Scatter | Relationship between two measures | Scatter chart, with a fitted line only when the file carries its values |
| Table | About six numbers or fewer, or a two-way grid of values | PowerPoint table, numbers right-aligned, units in the header row, optional color fill in one hue by value |

Never use 3D, a second value axis, or decorative effects. Put a second measure in its own chart, not on a second axis.

### Style

- **Title:** none on the chart. The slide headline states the finding.
- **Axis titles:** the measure and its unit, from the header of the file, in the words of the audience. Omit an axis title only when the category labels are clear without it.
- **Labels:** categories, series names, and legend entries exactly as the file writes them.
- **Color:** the accent `#0072B2` of the theme marks the **Highlight** group, and grey `#A6A6A6` marks the rest. `#D55E00` marks a second highlighted group. If there is no highlight, color the series with at most six hues from `#0072B2`, `#E69F00`, `#009E73`, `#D55E00`, `#CC79A7`, `#56B4E9`. Color any more series grey, and still label each series. Never combine series or categories. Text is `#333333`. When the theme of the organization is applied, keep one accent for the highlight and grey for context in its palette. Never use color as the only indicator: the headline or a data label names the highlighted group.
- **Text size:** no chart text below 12 pt. Data labels and axis labels are 12 to 14 pt.
- **Data labels:** on the highlighted marks, or on every mark when there are six marks or fewer. Use the number format that the slide uses (thousands separators, the same decimals). When values are labeled, remove gridlines. If values are not labeled, keep light `#E5E5E5` gridlines on the value axis only.
- **Furniture:** no chart border, no top or right axis line, no shadows.

### Source, caveat, and alt text

- Put the **Source:** text in a small line (10 to 12 pt) directly under the chart.
- For a **Caveat:**, mark the affected value with an asterisk on its data label or category. Put the reason after the source line, and start it with an asterisk. The caveat bullet on the slide stays.
- Set the alt text of the chart from **Alt text:**.

### Honest display

- Bars and columns start at zero. A line chart uses a non-zero baseline only when **Axis:** says so. Keep the reason in the source line.
- If the file carries intervals, always draw them. State what they mean in the source line, from **Interval:**.
- Keep every category, period, and outlier that the file holds. This includes results that contradict the headline.
- Charts across the deck that show the same measure use the same scale unless **Axis:** says otherwise.

## Supporting datasets

Deliver each dataset file beside the deck, as supplied. The **Supporting datasets** slide is the only place where the datasets are in the deck.

## Theme and accessibility

When they are available, apply the approved template, typography, and page furniture of the organization. Keep every headline in the title placeholder of its slide, so that the reading order and slide titles stay correct. Keep body text at 18 pt or larger. Run the PowerPoint accessibility checker.

## Revision boundary

If a requested change affects the storyline, wording, findings, numbers, charts, scope, or dataset contents, do these steps:

- Make that revision in the upstream workbench draft.
- Send the refreshed package forward.
- Build the deck again.

Deck edits stay in the deck. Make the layout, theme, and visual polish here, within the rules above.

## Before handing back

Confirm these items:

- There is one slide for each outline slide, in order.
- Every chart is native, from its file.
- Every **Caveat:** and **Awaiting revalidation:** bullet is visible on its slide.
- The accessibility checker is clean.
