# Findings

Write this file for the audience recorded in the investigation brief's **Audience** section: use the terms they use, assume what they already know and nothing more, and address the decision they own. It is the only source of content for the delivered documents, so it stands alone for that reader, with no earlier version, internal record, or follow-up conversation needed to understand it.

Write every section under the translation rule. Name things the way the audience and the glossary's business terms do. Never write repository paths or file names, view, table, or column names, settings keys, result or evidence IDs, investigation or package names in their workbench spelling, commit SHAs, release numbers, code identifiers, or backticked code. Describe a source by its owner, content, and period ("the billing team's monthly invoice extract, January to June 2026"), a filter or choice by its effect ("excluded test accounts, about 3% of volume"), and a coded value by its display name. The one exception is the relative link target of an embedded figure, `figures/<slug>.png`.

Put a caveat beside the claim it qualifies. Begin a caveat on a conclusion awaiting revalidation with **Awaiting revalidation:** followed by the reason in plain words, wherever that conclusion appears.

## Context

State the business question, the decision it supports or the exploratory purpose, and the population and period in plain words.

## Answer

Give the clearest evidence-supported answer to the question in a short paragraph, with its key number and the qualification that matters most.

## Findings

### State the finding as a plain-language headline

Give one `###` section per finding, its heading stating the finding. Use the same heading text for the matching section of the methodology. Present the evidence with its numbers, embed the figure that supports it, and state any result that complicates or contradicts it.

Embed each figure exactly in this form, numbering figures in order of first appearance across this file:

```markdown
![<alt text: the finding and its key numbers, 1-2 sentences>](figures/<slug>.png)

*Figure N. <caption: unit, population, period, n, source in plain words, exclusions, interval meaning, non-zero baseline or scale notes, display thresholds, caveat reasons>*
```

The italic paragraph immediately after the image is the caption: leave one blank line between them and write the caption as a single paragraph. It is the figure's only caption, since nothing is drawn in the image. A caveat on a value the figure shows goes in the caption and the alt text.

## Implications

Connect the findings to the decision or exploratory purpose. Keep recommendations and next steps within the evidence.

## How we know

Explain the method in plain language: the definitions the answer depends on; the sources, described by owner, content, and period; each exclusion and analytical choice, described by its effect on the population or result; and the validation performed, in plain terms ("totals reconcile to the finance ledger within 0.5%"). Give as much as the audience needs to trust the answer.

## Limitations and open caveats

List the source limitations, assumptions, and unresolved issues that limit interpretation. List each finding awaiting revalidation as unresolved, with its reason.

## What changed since the last version

For a later version, describe material changes to scope, sources, method, findings, caveats, or supporting datasets since the last delivered version, referring to that version by its delivery date. For the first version, state that there is no earlier version.

## Supporting datasets

Describe each audience-facing dataset in business terms: what a row represents, the population and period, the measures it carries in the audience's terms, and any caveat on the dataset or one of its fields. Otherwise state **None**.
