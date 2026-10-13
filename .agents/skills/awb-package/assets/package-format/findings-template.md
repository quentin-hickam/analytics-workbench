# Findings

Everything above **## Answer** is drafting guidance. Do not include it in findings.md. findings.md opens with the deck-title `#` heading and the subtitle line.

Write this file for the audience that is recorded in the **Audience** section of the investigation brief:

- Use the terms that they use.
- Assume what they already know and nothing more.
- Address the decision that they own.

This file is the slide-by-slide outline of the delivered deck and the only source of its content. For this reason, its headings in order give the storyline of the deck. The user can check that storyline here before M365 builds anything. The file stands alone for that reader. The reader does not need an earlier version, an internal record, or a follow-up conversation to understand it.

Write every section in the words of the audience:

- For names, use the business terms of the glossary.
- Give a source by its owner, content, and period ("the billing team's monthly invoice extract, January to June 2026").
- Give a filter or choice by its effect ("excluded test accounts, about 3% of volume").
- Give a coded value by its display name.

Every name that is spelled the way the workbench spells it stays in `methodology.md`. `check-draft` flags any such name that stays in this file.

## Slide rules

- The file opens with a `#` heading that gives the deck title in the words of the audience. One subtitle line follows it and names the audience, population, and period in plain words. Together they are the title slide.
- Each `##` section below is one slide, in this order. The exception is **Findings**, which is a deck section that holds one slide for each `###` finding. Order the finding slides by relevance to the decision. That order is the storyline.
- The headline of a slide is one sentence of at most 15 words. It states the point of the slide with its key number. It is never a topic label. The `###` heading of a finding slide is its headline. Every other slide opens with a `**Headline:**` line.
- The slide body has at most five bullets. Each bullet is one claim, with its number written exactly as the slide must show it. Content that does not fit goes to another slide or into the notes.
- A caveat is on the slide of the claim that it qualifies, as a bullet that begins with **Caveat:**. A caveat on a flagged conclusion begins with **Awaiting revalidation:**, followed by the reason in plain words. This caveat is on every slide where that conclusion appears.
- Each slide ends with a `**Notes:**` paragraph, which holds the speaker notes. The notes give what a presenter needs to explain the slide. Examples are the fuller reasoning, the plain-language method behind this point, and context that the bullets compress. Notes add no claim that the bullets and the methodology do not support.
- A slide can carry one chart, specified in the form below. Number the charts in the order in which they appear in the file. The plotted values of each chart are the package's chart file for Chart N, which carries exactly those values. The specification names the form and how to read the columns of the file. The numbers stay in the file. Choose one form:
  - Horizontal bar (to rank categories).
  - Bar with intervals (estimates with lower and upper columns).
  - Line (change over time, a few series).
  - Column (a few short-label categories, or counts by period).
  - Stacked bar (part-to-whole).
  - Scatter (two measures, and a fitted line only when the file carries it).
  - Table (about six numbers or fewer, or a two-way grid).

```markdown
**Chart N.** <form>: <the comparison the reader makes, in plain words>
- **Data:** <which column is the category, value, series, or interval, by its header>
- **Highlight:** <the group the headline is about, or none>
- **Axis:** <unit, and zero baseline or the reason for another>
- **Interval:** <what the interval columns mean, or none>
- **Source:** <source in plain words, population, period, n, exclusions>
- **Caveat:** <the value it affects and the reason, or none>
- **Alt text:** <the finding and its key numbers, one or two sentences>
```

## Answer

**Headline:** <the answer to the question, with its key number>

- The business question and the decision that it informs.
- Two to four key findings with their numbers, in the order of the finding slides.
- The qualification that matters most to the decision.

**Notes:** <why this is the answer, in a few sentences>

## Findings

### State the finding as a one-sentence headline with its number

Give one `###` slide for each finding. Use the same heading text for the matching section of the methodology. Present the evidence as bullets with their numbers. Add the chart that shows it. Keep any result that complicates or contradicts it on the same slide.

## Implications

**Headline:** <what the findings mean for the decision>

Connect the findings to the decision or exploratory purpose. Keep recommendations and next steps within the evidence.

## How we know

**Headline:** <why the answer can be trusted, in one sentence>

Give the method in plain language:

- The definitions that the answer depends on.
- The sources, described by owner, content, and period.
- Each exclusion and analytical choice, described by its effect on the population or result.
- The validation that was done, in plain terms ("totals reconcile to the finance ledger within 0.5%").

Put what the audience needs on the slide, and the rest in the notes.

## Limitations and open caveats

**Headline:** <the limitation that matters most to the decision>

List the source limitations, assumptions, and unresolved issues that limit interpretation. List each flagged finding as unresolved, with its reason.

## What changed since the last version

**Headline:** <the most material change>

For a later version, describe material changes since the last delivered version to scope, sources, method, findings, caveats, or supporting datasets. Refer to that version by its delivery date. Do not include this slide for the first version.

## Supporting datasets

**Headline:** <what the attached data lets the reader check or explore>

Describe in business terms each audience-facing dataset that is delivered beside the deck:

- What a row represents.
- The population and period.
- The measures that it carries, in the terms of the audience.
- Any caveat on the dataset or on one of its fields.

If no dataset is selected, do not include this slide.
