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

**Acquisition**:
One completed capture of records from a source, landed under `data/raw/<source>/<acquisition-id>/` with a provenance file recording its request, timing, and file checksums. An incomplete acquisition stays unpublished.

**Publication**:
A validated Parquet version of a dataset converted from named acquisitions, written once under `data/parquet/<dataset>/<publication-id>/` with a publication file recording its inputs and conversion commit. Canonical views read publications; a correction adds a view definition or a new publication and leaves existing publications as they are.

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

**Run script**:
An investigation's `run.py`, the thin entry point that composes shared operations under the investigation's settings and produces, validates, and records its results in one run.

**Finding**:
A validated result an investigation records as a row of `state.md`, with a status and a link to its result evidence. Exploration notes are recorded separately and are not findings.

**Flagged**:
Awaiting revalidation: a finding that a shared correction or changed input may affect, marked with the reason and with its prior status kept visible in the status value, as in `revalidation-needed (was supported)`. Scan output is an anomaly in EDA and an issue in cleaning, never a flag.

**Stale**:
A finding whose result evidence no longer matches the current producing code, view definitions, input publications and acquisitions, or resolved settings, as the `stale` comparison reports. An export refuses a stale result. A record whose date lags recent work is out of date, not stale.

**Delivery package**:
A collection of audience-facing outputs, with an internal methodology reference, representing an investigation at a particular point, with provenance identifying the code, inputs, and analytical parameters that produced it.

**Package format**:
The shared conventions for package structure and presentation, including the audience-facing findings document written as a deck outline, the internal methodology reference, the chart files, and the M365 assembly instructions under which M365 builds the PowerPoint deck. It is independent of an investigation's scope, narrative, and results.

**Cache**:
A stored result retained to avoid expensive recomputation of an analysis or data preparation step.

**Working draft**:
The current editable revision of a delivery package, updated until it is explicitly marked as delivered.

**Release**:
A preserved, numbered revision of a delivery package created from its working draft at an explicit delivery milestone.

**Frozen**:
The condition of every release: its files, results, and provenance stay exactly as released. Corrections, flags, and revisions after the milestone go to the working draft and the next release.

**Disposition**:
The user's choice for a flagged finding that a draft represents: revalidate it, omit it, or release it with its caveat. A new or changed flag reopens the choice. A release proceeds only when every place the finding appears is omitted or released with its caveat; revalidation pauses it for separate analytical work.

**Investigation state**:
The current understanding of an investigation, including its active question, findings, unresolved issues, and next steps.

**Investigation history**:
The record of meaningful findings, analytical decisions, and relevant data limitations accumulated during an investigation, including superseded conclusions. It retains methodological mistakes that changed a finding or explain why an earlier conclusion was wrong, and excludes routine debugging, coding mistakes, and abandoned attempts that changed no understanding.

**Result evidence**:
The per-result record of what produced a finding: the producing commit or `uncommitted` state with checksums, the inputs with the checksums their provenance or publication files record, the view definitions read, the resolved settings, and the validation checks. It is written to `investigations/<name>/evidence/<result-id>.json` and linked from the finding's row in `state.md`. It records provenance for one result; the investigation history records how understanding changed.
