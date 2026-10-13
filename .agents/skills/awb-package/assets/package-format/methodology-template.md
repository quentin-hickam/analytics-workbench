# Methodology

This file is the internal reference for the analysis that this package represents. The M365 agent and analysts can use it to look up the logic behind a specific decision. For this reason, it uses the workbench's own vocabulary: view and table names, settings keys, result IDs, evidence paths, and release numbers are expected here. It stays internal to the package. It stands on its own, without earlier releases or the investigation records.

## Package context

- **Investigation:**
- **Package:**
- **Business question:**
- **Decision or exploratory purpose:**
- **Population and period:**
- **Audience:**
- **What makes the answer useful:**

## Scope and definitions

Describe the included and excluded populations, periods, local terminology, and material assumptions, with the settings keys that set them. Explain any difference from the shared glossary.

## Sources and data quality

Identify each input by its source, its acquisition or publication identifier, and the views that were read. Summarize how fit each input is for this analysis. Include the source limitations, known data errors, and corrections that affect interpretation. Cite their entries in the quality record.

## Method and settings

Explain the analytical approach, and the settings (by key and value) that are necessary to understand the results. Make a clear distinction between canonical preparation and investigation-specific filters or assumptions.

## Validation checks

State the validation checks that were done on the presented results. Give their outcomes and the location where each check is recorded.

## Findings

### Use the same heading text as the finding in findings.md

Give one `###` section for each finding in `findings.md`. Make its heading identical to the heading of that finding. Record these items:

- The reasoning that supports the finding.
- Its result IDs and evidence paths.
- The chart file that each of its charts reads, with the result that the chart file serializes and the source column of each header.
- The settings that it depends on.
- The results that complicate or contradict it.

## Methodological corrections

Record each methodological mistake that changed a finding or that explains why an earlier conclusion was wrong. For each mistake, record what was wrong, how it was found, and what it changed. Routine debugging, coding mistakes, and abandoned execution attempts that changed no understanding stay out, as in `history.md`. If there is no such mistake, state **None**.
