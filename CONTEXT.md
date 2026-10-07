# Analytics Workbench

Language for organizing analytical work around shared data and distinct business questions.

## Language

**Project**:
A workspace containing a shared data foundation and investigations that use it; investigations are created as business questions arise.

**Data foundation**:
The shared data, reusable definitions, and knowledge about data preparation and quality available to investigations within a project.

**Canonical data**:
The shared, authoritative representation of source data under documented preparation rules. Canonical status does not imply that the data is free of limitations or suitable for every investigation.

**Landed data**:
Source records durably captured independently of the canonical analytical store, with provenance linking them to their acquisition. Landed data is the input to preparation, not an assertion of cleanliness or analytical fitness.

**Canonical database**:
The logical collection of approved datasets and shared views available to investigations. It may reference independently stored data rather than contain a second physical copy.

**Data preparation**:
The normalization, quality assessment, and documented correction of source data into canonical data. Preparation is driven by analytical needs and can evolve as exploration reveals issues.

**Data cleaning**:
The part of data preparation that addresses errors and inconsistencies under explicit correction rules. Question-specific exclusions are analytical choices rather than general cleaning rules.

**Exploratory data analysis (EDA)**:
The examination of data distributions, relationships, and quality to develop or assess questions and explanations. EDA uses canonical data and local exploratory transformations without implicitly changing the shared preparation rules.

**Exploratory transformation**:
A temporary selection or transformation used to examine data within an investigation. It remains local unless deliberately adopted as a shared preparation rule.

**Analytical operation**:
A neutral, reusable computation that produces measurements or comparisons independently of a desired narrative or conclusion.

**Investigation**:
An inquiry into a business question, with its own scope, analytical choices, progress, and findings, that draws on the project's data foundation. It combines analytical operations and interprets their results for that question.

**Delivery package**:
A collection of audience-facing outputs representing an investigation at a particular point, with provenance identifying the code, inputs, and analytical parameters that produced it.

**Package format**:
The shared conventions for package structure and presentation, including the journal, executive summary, and M365 assembly instructions. It is independent of an investigation's scope, narrative, and results.

**Cache**:
A stored result retained to avoid expensive recomputation of an analysis or data preparation step.

**Working draft**:
The current editable revision of a delivery package, updated until it is explicitly marked as delivered.

**Delivery**:
A preserved, numbered revision of a delivery package created at an explicit delivery milestone.

**Investigation state**:
The current understanding of an investigation, including its active question, findings, unresolved issues, and next steps.

**Investigation history**:
The record of meaningful findings, analytical decisions, and relevant data limitations accumulated during an investigation, including superseded conclusions. It excludes execution mistakes and routine debugging.
