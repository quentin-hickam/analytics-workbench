# Findings

Everything above **## Answer** is drafting guidance: omit it from findings.md, which opens with the deck-title `#` heading and subtitle line.

Write this file for the audience recorded in the investigation brief's **Audience** section: use the terms they use, assume what they already know and nothing more, and address the decision they own. It is the slide-by-slide outline of the delivered deck and the only source of its content, so reading its headings in order is reading the deck's storyline, and the user can check that storyline here before anything is built. It stands alone for that reader, with no earlier version, internal record, or follow-up conversation needed to understand it.

Write every section in the audience's words: the glossary's business terms for names, a source by its owner, content, and period ("the billing team's monthly invoice extract, January to June 2026"), a filter or choice by its effect, with any count or share a result records ("excluded test accounts, about 3% of volume"), and a coded value by its display name. Every name spelled the way the workbench spells it stays in `methodology.md`; `check-draft` flags any left here.

## Slide rules

- The file opens with a `#` heading giving the deck title in the audience's words, followed by one subtitle line naming the audience, population, and period in plain words. Together they are the title slide.
- Each `##` section below is one slide, in this order, except **Findings** and **Appendix**, which are deck sections holding one slide per `###` heading. Each section says whether it is required, conditional, or optional. The required slides are the title slide, **Answer**, at least one finding slide under **Findings**, **How we know**, and **Limitations and open caveats**, in that order, though **How we know** or **Limitations and open caveats** may move to the appendix, keeping that order when both do; `check-draft` refuses a deck that lacks one, repeats one, or puts them out of order. The deck opens with the title slide and then the **Answer** slide; the two stay separate.
- Order finding slides by the highest-priority ledger question their primary result's recorded settings `answers` identify (`must`, `should`, `could`), the primary result being the first one the methodology section cites, then that question's depth-first position in the ledger tree, whose siblings sort by priority then ID. Findings answering no ledger question go last and are named in the draft report. Finding slides in the main sequence and those under **Appendix** each follow this order. It is the order proposed at the headline step: an order the user approves instead is recorded in the manifest's `presentation_order`, which then decides the order of every finding slide.
- A slide's headline is one sentence of at most 15 words stating its point with its key number, never a topic label; a longer one stands only when the user accepts it. A finding slide's `###` heading is its headline; every other slide opens with a `**Headline:**` line.
- The slide body is at most five bullets, each one claim with its number written exactly as the slide should show it. **Open questions** is exempt from the bullet limit so it can list every required question. Other content that does not fit goes to another slide or into the notes, though every part of each question the deck answers stays in a headline, bullet, or chart. A slide holds nothing besides its headline, bullets, chart, and notes; the title slide holds only its subtitle line.
- Word each finding no more strongly than its claim strength in the investigation's state. Below causal, say what moved together or differed ("stores offering the discount had 4 points fewer late orders"), never that one thing drives, causes, or leads to another; `check-draft` refuses such wording anywhere on the slide, its headline and **Caveat:** bullets included.
- A caveat sits on the slide of the claim it qualifies, as a bullet beginning **Caveat:**. A caveat on a flagged conclusion begins **Awaiting revalidation:** followed by the reason in plain words, on every slide where that conclusion appears.
- Each slide after the title slide ends with a `**Notes:**` paragraph, the speaker notes: what a presenter needs to explain the slide, such as the fuller reasoning, the plain-language method behind this point, and context the bullets compress. Notes add no claim the bullets and the methodology do not support.
- A slide may carry one chart, specified in the form below. Number charts in order of appearance across the file. Each chart's plotted values are the package's chart file for Chart N, which carries exactly those values; the specification names the form and how to read the file's columns, leaving the numbers to the file. Choose one form: Horizontal bar (ranking categories), Bar with intervals (estimates with lower and upper columns), Line (change over time, a few series), Column (a few short-label categories, or counts by period), Stacked bar (part-to-whole), Scatter (two measures; a fitted line only when the file carries it), or Table (about six numbers or fewer, or a two-way grid). The **Data:** line names every column of the file by the roles `package-format/deck-rules.md` lists for the form, each header as the file writes it (`deck-rules.md` says how a role matches a header). The specification's fields are the bullets directly under its line, each one paragraph with nothing nested under it, with no blank line between fields, and one blank line after the last field: a blank line ends the fields, so a field after it counts as a slide bullet.

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

*Required: the first slide after the title slide.*

**Headline:** <the answer to the question, with its key number>

- The business question and the decision it informs.
- Two to four key findings with their numbers, in the order of the finding slides.
- The qualification that matters most to the decision.

**Notes:** <why this is the answer, in a few sentences>

## Findings

*Required: at least one finding slide stays in this section.*

### State the finding as a one-sentence headline with its number

Give one `###` slide per finding slide, which may present several recorded results. Use the same heading text for the matching section of the methodology. Present the evidence as bullets with their numbers, add the chart that shows it, and keep any result that complicates or contradicts it on the same slide.

## Implications

*Optional.*

**Headline:** <what the findings mean for the decision>

Connect the findings to the decision or exploratory purpose. Keep recommendations and next steps within the evidence.

## How we know

*Required; it may move to the appendix.*

**Headline:** <why the answer can be trusted, in one sentence>

Give the method in plain language: the definitions the answer depends on; the sources, described by owner, content, and period; each exclusion and analytical choice, described by its effect on the population or result; and the validation performed, in plain terms ("every month's total matches the finance ledger exactly"). Put what the audience needs on the slide and the rest in the notes, a check's tolerance included, stated only when the brief or the result's settings recorded it before the result, as `methodology.md` cites; a tolerance chosen after seeing the result is not a tolerance.

## Limitations and open caveats

*Required; it may move to the appendix.*

**Headline:** <the limitation that matters most to the decision>

List the source limitations, assumptions, and unresolved issues that limit interpretation. List each flagged finding as unresolved, with its reason.

## Open questions

*Conditional: required when unanswered `must` questions, or questions marked `show`, exist, and omitted otherwise. It follows **Limitations and open caveats**; when that slide moves to the appendix, it follows the last finding, **Implications**, or **How we know** slide.*

**Headline:** <what remains unanswered for the decision>

List exactly the unanswered `must` ledger questions and those marked `show`, one per top-level bullet, using each question's exact `audience` wording when set, otherwise its question `text`, with no question IDs or extra commentary. Set audience wording in the ledger before packaging when the text is not in the audience's words, and show that wording with the headlines for approval. Normal inline Markdown formatting is allowed; nested bullets are not. Include open and parked questions and answered data questions displaying **answered (awaiting recheck)** or **answered (provisional, awaiting recheck)** because any answering finding is flagged or superseded. Declined or superseded questions are set aside and excluded. Omit the whole slide when no required questions remain. Include every required question even when there are more than five, and report that count.

**Notes:** <why the unanswered questions matter to the decision>

## What changed since the last version

*Conditional: required for every version after the first.*

**Headline:** <the most material change>

For a later version, describe material changes to scope, sources, method, findings, caveats, or supporting datasets since the last delivered version, referring to that version by its delivery date. Omit this slide for the first version.

## Supporting datasets

*Conditional: required when datasets are selected; it may move to the appendix.*

**Headline:** <what the attached data lets the reader check or explore>

Describe each audience-facing dataset delivered beside the deck in business terms: what a row represents, the population and period, the measures it carries in the audience's terms, and any caveat on the dataset or one of its fields. Omit this slide when no dataset is selected.

## Appendix

*Optional: slides kept for reference after the main sequence, such as those that would take the deck past the length the brief's **Audience** section records.*

Give one `###` slide per appendix slide under this one `## Appendix`, after every other section. A `###` slide headed **How we know**, **Limitations and open caveats**, or **Supporting datasets** is that slide moved here and keeps its **Headline:** line; every other `###` slide is a finding slide moved here, under the finding rules, its claim strength included. **Answer**, **Implications**, **Open questions**, and **What changed since the last version** stay in the main sequence. The builder opens the appendix with a divider slide titled Appendix.
