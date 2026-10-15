# Methodology

This file is the internal reference for the analysis this package represents. It lets the deck builder and analysts look up the logic behind a specific decision, so it uses the workbench's own vocabulary: view and table names, settings keys, result IDs, evidence paths, and release numbers are expected here. It stays internal to the package. It stands on its own, without earlier releases or the investigation records. An account of method written for the audience is the optional `methodology-note.md`, from `methodology-note-template.md`; it states nothing this file does not support.

## Package context

- **Investigation:**
- **Package:**
- **Business question:**
- **Decision or exploratory purpose:**
- **Population and period:**
- **Audience:**
- **What makes the answer useful:**

## Scope and definitions

Describe included and excluded populations, periods, local terminology, and material assumptions, with the settings keys that set them. Explain any departure from the shared glossary.

## Sources and data quality

Identify each input by source, acquisition or publication identifier, and the views read, and summarize its fitness for this analysis. Include source limitations, known data errors, and corrections that affect interpretation, citing their entries in the quality record.

## Method and settings

Explain the analytical approach and the settings needed to understand the results, by key and value. Distinguish canonical preparation from investigation-specific filters or assumptions.

## Validation checks

State the validation checks performed on the results presented, with their outcomes and where each is recorded.

## Findings

### Use the same heading text as the finding in findings.md

Give one `###` section per finding in `findings.md`, its heading identical to that finding's heading. Open it with `**Claim strength:** <claim>`: the weakest Claim in `state.md` among its results; a causal claim copies its results' Claim cell, design basis included. Record the reasoning that supports the finding, its result IDs and evidence paths, the question each result answers exactly as the manifest's `results` records it, the chart file each of its charts reads with the result it serializes and the source column of each header, the settings it depends on, and the results that complicate or contradict it.

## Methodological corrections

Record each methodological mistake that changed a finding or explains why an earlier conclusion was wrong: what was wrong, how it was found, and what it changed. Routine debugging, coding mistakes, and abandoned execution attempts that changed no understanding stay out, as in `history.md`. Otherwise state **None**.
