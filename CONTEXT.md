# Analytics Workbench

Terms to organize analytical work around shared data and separate business questions.

## Language

**Project**:
A workspace that contains a shared data foundation and the investigations that use it. Investigations are created when business questions occur.

**Data foundation**:
The shared data, reusable definitions, and knowledge about data preparation and quality that are available to investigations in a project.

**Canonical data**:
The shared, authoritative representation of source data under documented preparation rules. Canonical status does not mean that the data has no limitations or that it is suitable for every investigation.

**Landed data**:
Source records that are captured durably and independently of the canonical analytical store, with provenance that links them to their acquisition. Landed data is the input to preparation. It does not state that the data is clean or fit for analysis.

**Acquisition**:
One completed capture of records from a source. It is landed under `data/raw/<source>/<acquisition-id>/` with a provenance file that records its request, timing, and file checksums. An incomplete acquisition stays unpublished.

**Publication**:
A validated Parquet version of a dataset, converted from named acquisitions. It is written one time under `data/parquet/<dataset>/<publication-id>/`, with a publication file that records its inputs and conversion commit. Canonical views read publications. A correction adds a view definition or a new publication, and leaves the existing publications as they are.

**Canonical database**:
The logical collection of approved datasets and shared views that are available to investigations. It can refer to data that is stored independently. It does not have to contain a second physical copy of that data.

**Data preparation**:
The normalization, quality assessment, and documented correction of source data into canonical data. Analytical needs drive preparation, and preparation can change when exploration shows issues.

**Data cleaning**:
The part of data preparation that handles errors and inconsistencies under explicit correction rules. Exclusions for a specific question are analytical choices, not general cleaning rules.

**Exploratory data analysis (EDA)**:
The examination of data distributions, relationships, and quality to develop or assess questions and explanations. EDA uses canonical data and local exploratory transformations. It does not implicitly change the shared preparation rules.

**Exploratory transformation**:
A temporary selection or transformation that is used to examine data in an investigation. It stays local unless it is deliberately adopted as a shared preparation rule.

**Analytical operation**:
A neutral, reusable computation that produces measurements or comparisons independently of a desired narrative or conclusion.

**Investigation**:
An inquiry into a business question that uses the project's data foundation. It has its own scope, analytical choices, progress, and findings. It combines analytical operations and interprets their results for that question.

**Run script**:
An investigation's `run.py`. It is the thin entry point that composes shared operations under the investigation's settings. In one run, it produces, validates, and records its results.

**Finding**:
A validated result that an investigation records as a row of `state.md`, with a status and a link to its result evidence. The row is rendered from the investigation's `findings.json`. Only the provenance helper writes that file. Exploration notes are recorded separately and are not findings.

**Flagged**:
Awaiting revalidation: a finding that a shared correction or changed input can affect. It is marked with the reason, and its previous status stays visible in the status value, as in `revalidation-needed (was supported)`. Scan output is an anomaly in EDA and an issue in cleaning. Scan output is never a flag.

**Stale**:
A finding whose result evidence no longer matches the current producing code, view definitions, input publications and acquisitions, or resolved settings. The `stale` comparison reports this condition. An export refuses a stale result. A record whose date is behind recent work is out of date, not stale.

**Delivery package**:
A collection of audience-facing outputs, with an internal methodology reference, that represents an investigation at a specific point. Its provenance identifies the code, inputs, and analytical parameters that produced it.

**Package format**:
The shared conventions for package structure and presentation. These include the audience-facing findings document, written as a deck outline. They also include the internal methodology reference, the chart files, and the M365 assembly instructions. M365 builds the PowerPoint deck under these assembly instructions. The package format is independent of the scope, narrative, and results of an investigation.

**Cache**:
A stored result that is kept to prevent expensive recomputation of an analysis or data preparation step.

**Working draft**:
The current editable revision of a delivery package. It is updated until it is explicitly marked as delivered.

**Release**:
A preserved, numbered revision of a delivery package. It is created from its working draft at an explicit delivery milestone.

**Frozen**:
The condition of every release: its files, results, and provenance stay exactly as released. Corrections, flags, and revisions after the milestone go to the working draft and the next release.

**Disposition**:
The user's choice for a flagged finding that a draft represents: revalidate it, omit it, or release it with its caveat. A new or changed flag opens the choice again. A release continues only when each place where the finding appears is omitted or released with its caveat. Revalidation pauses the release for separate analytical work.

**Investigation state**:
The current understanding of an investigation. It includes its active question, findings, unresolved issues, and next steps.

**Investigation history**:
The record of meaningful findings, analytical decisions, and relevant data limitations that accumulate during an investigation. The record also includes superseded conclusions. It keeps methodological mistakes that changed a finding or that explain why an earlier conclusion was wrong. It excludes routine debugging, coding mistakes, and abandoned attempts that changed no understanding.

**Result evidence**:
For one result, the record of what produced a finding. It contains:

- The producing commit or `uncommitted` state, with checksums.
- The inputs, with the checksums that their provenance or publication files record.
- The view definitions that were read.
- The resolved settings.
- The validation checks.

It is written to `investigations/<name>/evidence/<result-id>.json`, and the finding's row in `state.md` links to it. It records provenance for one result. The investigation history records how understanding changed.
