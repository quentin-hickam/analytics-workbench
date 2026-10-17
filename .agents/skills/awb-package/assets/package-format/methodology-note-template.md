# Methodology note

Everything above the second `#` heading is drafting guidance: omit it from `methodology-note.md`, which opens with that title and its subtitle line.

The note is optional. It is a short, plain-language account of how the answer was reached, written for the reader the investigation brief's **Audience** section records, such as the methods note a committee asks to see beside the deck. `methodology.md` stays the internal reference; this note is what the audience reads. It travels beside the deck, like datasets, and is not attached to the deck builder.

Write it under the translation rule in `findings-template.md`: the glossary's business terms, a source by its owner, content, and period, a filter or choice by its effect, and a coded value by its display name. Keep it within the methods note length the brief's **Audience** records, which `check-draft` compares, or to a page or two when it records none. It states nothing `methodology.md` does not support, and gives the same numbers, qualifications, and caveats; the draft review checks that.

`check-draft` reads the whole note as it reads `findings.md`: it reports internal names, numbers no represented result records, Markdown outside the subset its checks read, and causal wording above the strongest claim strength the package represents, outside **Limitations**. Describe a data problem by what happened, not by a cause ("the extract stopped for six days in June", not "June is short due to an outage").

# <What the note covers, in the audience's words, such as How we measured late claims>

<One line naming the audience, population, and period in plain words.>

## What was asked

The business question and the decision it informs, as the deck's **Answer** slide states them.

## Sources

Each source by its owner, content, and period, and how complete it is for this question.

## Definitions

The terms the answer depends on, in the glossary's business terms, with any departure from their usual meaning.

## Method

How the numbers were produced, in plain steps, and the checks that confirm them, under the package contract's **Writing rules**.

## Exclusions

Each population, period, or record left out, by its effect, with the count or share a result records ("test accounts, about 3% of volume").

## Limitations

The limitations, assumptions, and open caveats that limit interpretation, as **Limitations and open caveats** in the deck states them, each flagged finding included.
