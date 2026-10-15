# Findings

Everything above **## Answer** is drafting guidance: omit it from findings.md, which opens with the deck-title `#` heading and subtitle line.

Write this file for the audience recorded in the investigation brief's **Audience** section: use the terms they use, assume what they already know and nothing more, and address the decision they own. It is the slide-by-slide outline of the delivered deck and the only source of its content, so reading its headings in order is reading the deck's storyline, and the user can check that storyline here before anything is built. It stands alone for that reader, with no earlier version, internal record, or follow-up conversation needed to understand it.

Write every section in the audience's words: the glossary's business terms for names, a source by its owner, content, and period ("the billing team's monthly invoice extract, January to June 2026"), a filter or choice by its effect, with any count or share a result records ("excluded test accounts, about 3% of volume"), and a coded value by its display name. Every name spelled the way the workbench spells it stays in `methodology.md`; `check-draft` flags any left here.

## Slide rules

- The file opens with a `#` heading giving the deck title in the audience's words, followed by one subtitle line naming the audience, population, and period in plain words. Together they are the title slide.
- Each `##` section below is one slide, in this order, except **Findings**, which is a deck section holding one slide per `###` finding. Order finding slides by the highest-priority ledger question their results' recorded settings `answers` identify (`must`, `should`, `could`), then that question's depth-first position in the ledger tree, whose siblings sort by priority then ID. Findings answering no ledger question go last and are named in the draft report.
- A slide's headline is one sentence of at most 15 words stating its point with its key number, never a topic label. A finding slide's `###` heading is its headline; every other slide opens with a `**Headline:**` line.
- The slide body is at most five bullets, each one claim with its number written exactly as the slide should show it. **Open questions** is exempt from the bullet limit so it can list every required question. Other content that does not fit goes to another slide or into the notes. A slide holds nothing besides its headline, bullets, chart, and notes; the title slide holds only its subtitle line.
- Word each finding no more strongly than its claim strength in the investigation's state. Below causal, say what moved together or differed ("stores offering the discount had 4 points fewer late orders"), never that one thing drives, causes, or leads to another; `check-draft` refuses such wording anywhere on the slide, its headline and **Caveat:** bullets included.
- A caveat sits on the slide of the claim it qualifies, as a bullet beginning **Caveat:**. A caveat on a flagged conclusion begins **Awaiting revalidation:** followed by the reason in plain words, on every slide where that conclusion appears.
- Each slide after the title slide ends with a `**Notes:**` paragraph, the speaker notes: what a presenter needs to explain the slide, such as the fuller reasoning, the plain-language method behind this point, and context the bullets compress. Notes add no claim the bullets and the methodology do not support.
- A slide may carry one chart, specified in the form below. Number charts in order of appearance across the file. Each chart's plotted values are the package's chart file for Chart N, which carries exactly those values; the specification names the form and how to read the file's columns, leaving the numbers to the file. Choose one form: Horizontal bar (ranking categories), Bar with intervals (estimates with lower and upper columns), Line (change over time, a few series), Column (a few short-label categories, or counts by period), Stacked bar (part-to-whole), Scatter (two measures; a fitted line only when the file carries it), or Table (about six numbers or fewer, or a two-way grid). The **Data:** line names every column of the file by the roles `package-format/deck-rules.md` lists for the form, each header exactly as the file writes it. The specification's fields are the bullets directly under its line, each one paragraph with nothing nested under it, so leave a blank line between them and the slide's next bullet.

```markdown
**Chart N.** <form>: <the comparison the reader makes, in plain words>
- **Data:** <role: column header pairs separated by semicolons, such as category: Region; value: Closed late (%)>
- **Highlight:** <the group the headline is about, or none>
- **Axis:** <unit, and zero baseline, or for a Line: non-zero baseline and the reason>
- **Interval:** <what the interval columns mean, or none>
- **Source:** <source in plain words, population, period, n, exclusions>
- **Caveat:** <the value it affects and the reason, or none>
- **Alt text:** <the finding and its key numbers, one or two sentences>
```

## Answer

**Headline:** <the answer to the question, with its key number>

- The business question and the decision it informs.
- Two to four key findings with their numbers, in the order of the finding slides.
- The qualification that matters most to the decision.

**Notes:** <why this is the answer, in a few sentences>

## Findings

### State the finding as a one-sentence headline with its number

Give one `###` slide per finding. Use the same heading text for the matching section of the methodology. Present the evidence as bullets with their numbers, add the chart that shows it, and keep any result that complicates or contradicts it on the same slide.

## Implications

**Headline:** <what the findings mean for the decision>

Connect the findings to the decision or exploratory purpose. Keep recommendations and next steps within the evidence.

## How we know

**Headline:** <why the answer can be trusted, in one sentence>

Give the method in plain language: the definitions the answer depends on; the sources, described by owner, content, and period; each exclusion and analytical choice, described by its effect on the population or result; and the validation performed, in plain terms ("totals reconcile to the finance ledger within 0.5%"). Put what the audience needs on the slide and the rest in the notes.

## Limitations and open caveats

**Headline:** <the limitation that matters most to the decision>

List the source limitations, assumptions, and unresolved issues that limit interpretation. List each flagged finding as unresolved, with its reason.

## Open questions

**Headline:** <what remains unanswered for the decision>

List exactly the unanswered `must` ledger questions, one per top-level bullet, using each question's exact `audience` wording when set, otherwise its question `text`, with no question IDs or extra commentary. Set audience wording in the ledger before packaging when the text is not in the audience's words, and show that wording with the headlines for approval. Normal inline Markdown formatting is allowed; nested bullets are not. Include open and parked questions and answered data questions displaying **answered (awaiting recheck)** because any answering finding is flagged or superseded. Declined or superseded questions are set aside and excluded. Omit the whole slide when no required questions remain. Include every required question even when there are more than five, and report that count.

**Notes:** <why the unanswered questions matter to the decision>

## What changed since the last version

**Headline:** <the most material change>

For a later version, describe material changes to scope, sources, method, findings, caveats, or supporting datasets since the last delivered version, referring to that version by its delivery date. Omit this slide for the first version.

## Supporting datasets

**Headline:** <what the attached data lets the reader check or explore>

Describe each audience-facing dataset delivered beside the deck in business terms: what a row represents, the population and period, the measures it carries in the audience's terms, and any caveat on the dataset or one of its fields. Omit this slide when no dataset is selected.
