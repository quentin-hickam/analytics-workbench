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
One completed capture of records from a source, landed under `data/raw/<source>/<acquisition-id>/` with a provenance file recording its request, timing, file checksums, and any upstream validators (URL, ETag, Last-Modified, version ID) the fetch received. An incomplete acquisition stays unpublished.

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
An investigation's `run.py`, the thin entry point that composes shared operations under the investigation's settings and produces, validates, and records its results in one run. A result that needs more than its query has a producer module, `producers/<result-id>.py`, which the run script loads by result ID.

**Finding**:
A validated result an investigation records as a row of `state.md`, with a status, a claim strength, and a link to its result evidence. The row is rendered from the investigation's `findings.json`, which the provenance helper alone writes. The agent promotes a provisional finding to supported once its checks are recorded and the user approves its headline or text. Exploration notes are recorded separately and are not findings.

**Claim strength**:
The strongest wording a finding supports: descriptive, association, or causal. Causal requires a stated design basis, an experiment or an identified natural experiment; exploration supports association at most. A delivered narrative never words a finding above it.

**Flagged**:
Awaiting revalidation: a finding that a shared correction or changed input may affect, marked with the reason and with its prior status kept visible in the status value, as in `revalidation-needed (was supported)`. Scan output is an anomaly in EDA and an issue in cleaning, never a flag.

**Stale**:
A finding whose result evidence no longer matches the current producing code, view definitions, input publications and acquisitions, or the settings it reads, as the `stale` comparison reports. Producing code is only what can compute that result: the run script, its queries and producer module, the files its settings table declares, the investigation's shared SQL in `views/`, which every result session loads, and the analytical code under `src/`; a note or another result's code never makes it stale. An export refuses a stale result. A record whose date lags recent work is out of date, not stale. A changed Python, platform, or package version is a runtime mismatch, which `stale` reports as a warning, not stale.

**Delivery package**:
A collection of audience-facing outputs, with an internal methodology reference, representing an investigation at a particular point, with provenance identifying the code, inputs, and analytical parameters that produced it. Its audience-facing outputs are the deck outline, the chart files, any selected datasets, and an optional methodology note. Its start-here note sorts its files into what goes to the audience, what builds the deck, and what stays internal.

**Package format**:
The shared conventions for package structure and presentation, including the audience-facing findings document written as a deck outline with its required slides and an optional appendix, the internal methodology reference, the methodology note template, the chart files, the deck rules any builder follows to build the deck from the outline, and the assembly file for each builder, such as Microsoft 365 Copilot's PowerPoint agent. It is independent of an investigation's scope, narrative, and results.

**Methodology note**:
The optional audience-facing account of a package's method, sources, definitions, exclusions, and limitations, written in the audience's terms and delivered beside the deck. The methodology reference stays internal; the note states nothing the reference does not support.

**Cache**:
A stored result retained to avoid expensive recomputation of an analysis or data preparation step.

**Working draft**:
The current editable revision of a delivery package, updated until it is explicitly marked as delivered.

**Release**:
A preserved, numbered revision of a delivery package created from its working draft at an explicit delivery milestone.

**Frozen**:
The condition of every release: its files, results, and provenance stay exactly as released. Corrections, flags, and revisions after the milestone go to the working draft and the next release.

**Helper drift**:
A helper or package-format file in a project that differs from the checksum the installer recorded for it. Those files decide whether a draft passes, so a release proceeds only once the user confirms each drifted file at its current checksum.

**Disposition**:
The user's choice for a flagged finding that a draft represents: revalidate it, omit it, or release it with its caveat. A new or changed flag reopens the choice. A release proceeds only when every place the finding appears is omitted or released with its caveat; revalidation pauses it for separate analytical work.

**Review rule**:
A numbered rule, `R-<area>-NNN`, recorded from a correction the user made while reviewing a package draft, once the user agrees to keep it, which every later review of a draft checks, or of one package's drafts when it names that package. Its ID is never renumbered or reused. Its scope, `line` by default, `slide`, or `document`, is what one violation covers. An `error` rule wins over a `warning` rule it conflicts with; a conflict the review cannot settle goes to the user.

**Review receipt**:
The record of a package draft's last review, kept beside the draft: the report, the problems the user accepted with their reasons, and a copy of what the review read, the investigation's brief, the glossary, the source register, and the quality record included. It is current while that review passed and nothing it read has changed; the next review is scoped against it, and a release needs it current.

**Question ledger**:
An investigation's record of every question it has raised, answered or not, with who can answer each: the user, a stakeholder, or the data. It lives in `questions.json`, rendered whole to `questions.md`. A data question is answered only by a recorded result whose settings declare it; a question is never deleted, and a scope change supersedes an answered one. Questions form a tree: each has a parent question or is a root, and a priority of must, should, or could. The roots are the questions the user asked, and every other question, a stakeholder's or a decision the user deferred included, names the question it serves as its parent, so status and the turn footer count the roots, in the user's terms, before any sub-question. A package proposes its finding slide order from that tree; an order the user approves instead is the package's presentation order, which leaves the tree unchanged. The package's **Open questions** slide lists the unanswered must questions, and those the ledger marks to show whatever their priority, each in its audience wording when set and its text otherwise. Data problems, actions, and settled decisions are not questions and stay in the state and brief.

**Awaiting recheck**:
The derived display status `answered (awaiting recheck)` of an answered data question with at least one flagged or superseded answering finding and one supported, or supported before its flag; with none, it is `answered (provisional, awaiting recheck)`. It is computed from the current findings each time it is shown; the question's stored status stays answered. It describes the question; in records a flagged finding itself is awaiting revalidation, though chat calls it awaiting recheck too.

**Provisional answer**:
The derived display status `answered (provisional)` of an answered data question none of whose answering findings is promoted to supported yet, and none flagged or superseded. Like awaiting recheck it is computed each time it is shown while the stored status stays answered; the turn footer and status count it as provisional, not answered. `answered (provisional, awaiting recheck)` counts as provisional too.

**Investigation state**:
The current understanding of an investigation, including its active question, findings, unresolved issues, and next steps.

**Investigation history**:
The record of meaningful findings, analytical decisions, and relevant data limitations accumulated during an investigation, including superseded conclusions. It retains methodological mistakes that changed a finding or explain why an earlier conclusion was wrong, and excludes routine debugging, coding mistakes, and abandoned attempts that changed no understanding.

**Project interpreter**:
The Python interpreter that runs a project's helpers and `run.py`, recorded on the project README's `Project interpreter` line by the helper installer. `python3` in every documented workbench command means it, and `src/awb.py` reruns itself under it when another interpreter starts it. The installer records the interpreter it runs under, which the MCP `setup` tool takes as `interpreter`, and never one outside the project that lacks the helpers' packages.

**Code history**:
The Git history of a project's analytical code, which evidence and manifests cite by commit. A project without Git records `Code history: none (<reason>)` on its README line; it then has no commits, and evidence records file checksums instead.

**Result evidence**:
The per-result record of what produced a finding and why: the question it answers in the user's words, the producing commit or `uncommitted` state with checksums, which a result recorded before the first commit keeps until it is rerun, the inputs with the checksums their provenance or publication files record, the view definitions read, the settings it reads, the runtime (Python, platform, and package versions), and the validation checks. It is written to `investigations/<name>/evidence/<result-id>.json` and linked from the finding's row in `state.md`. It records provenance for one result; the investigation history records how understanding changed.
