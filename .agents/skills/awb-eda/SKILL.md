---
name: awb-eda
description: Explore one dataset, a canonical view or publication, for the active analytics workbench investigation. One bundled scan computes grain, distributions, null patterns, date coverage, the measure by dimension and over time, and associations within the investigation's scope; the skill then guides reading it, saving follow-up queries, and recording what was learned. Use when the user asks to explore, profile, or understand a dataset for an investigation's question. EDA results are exploration, never findings.
---

# Explore a dataset for an investigation

Explore one canonical view or publication at a time, within the investigation's question, scope, and settings. The project `AGENTS.md` and `workbench-guides/analysis.md` govern analysis and records; this skill adds the EDA procedure. EDA writes only under `investigations/<name>/exploration/` and the records in step 5. It never writes findings, evidence, shared views, or preparation code.

## 1. Frame

Use the investigation the user names, otherwise the README's active one. If its `brief.md` and `state.md` are not loaded, read them in one call. Say in a sentence or two which dataset you will explore and why it bears on the question. If several datasets fit, start with the one that holds the question's measure.

## 2. Scan

From the project root, with the interpreter that runs the project's analysis:

```sh
python3 <skill-directory>/scripts/eda_scan.py <project-root> <view-or-publication> [options]
```

Execute it without reading its implementation. It loads views through the project's `session()` helper and takes scope filters, date column, measure, dimensions, and key from the investigation's settings. It writes the complete scan to `investigations/<name>/exploration/eda/<dataset>.json` and prints compact Markdown. Options override settings: `--measure`, `--dimension` (repeatable), `--where` (repeatable), `--no-scope`, and `--label <name>` for a second scope of the same dataset. Read [scan options](references/scan-options.md) for any other option, for a `not applied` line, or for settings that lack a needed key. Exit status 2 prints the fix; apply it and run again.

Scan once per dataset and scope. Do not rerun to confirm, and do not reread the JSON to restate the printed summary. Open it only for the section a follow-up needs, such as one column's `top` or one dimension's `values`.

## 3. Read the scan

Read the scan before forming explanations, and no other investigation's conclusions. Check in order:

- **Scope.** Are the rows before and after the filters plausible? Does a `not applied` line or an unread settings key mean the population differs from the brief's? If so, scan again with `--where` and say so.
- **Grain.** Do the candidate keys match the catalog's grain? Check duplicates and any declared-key violation.
- **Anomalies.** Route `awb-clean` marks a possible shared data problem; `investigation` marks an analytical matter.
- **Relationships.** Look at the variance each dimension explains, the trend, the associations, and the contrary-trend groups. Name candidate explanations, and keep patterns that cut against the expected one.

Read [reading the scan](references/reading-the-scan.md) when an anomaly kind is unfamiliar, or when a data problem and a real pattern are hard to tell apart. Show the user the trimmed tables, three to five observations labeled exploratory, candidate explanations, and contrary patterns.

## 4. Follow up with saved queries

Write each follow-up as `investigations/<name>/exploration/<topic>.sql`, applying the scan's printed filters, and run it from the project root with `python3 src/awb.py sql <path>`. Revise and rerun the same file rather than adding variants. To profile a result, run `python3 src/awb.py profile <path> --out <file under exploration/>`. Never compute a distribution, breakdown, or trend with ad hoc Python or a scratch script. Read [follow-up queries](references/follow-up-queries.md) before the first query of a session. Draw an exploratory chart only on request; it uses the host's defaults and is saved under `exploration/`. Promoting an exploratory transformation into shared views or preparation is a deliberate change under `workbench-guides/data.md`.

## 5. Record what was learned

- **State.** Start from the printed suggested `state.md` lines. Keep the ones you confirmed, edit them, and add them under Unresolved issues or Next steps, replacing items they make stale.
- **History.** Add an entry only when understanding changed under its header's rules, such as a limitation that affects the question. A routine scan gets no entry.
- **Vocabulary.** A term that data has settled goes in the glossary, or in the brief if it is a local departure. A term still open is an unresolved issue.
- **Shared data problems.** Record each as an unresolved issue naming the scan path, and hand it to `awb-clean`: "Use awb-clean on <dataset> for <problem>". Do not fix it in a view or filter it silently. If exploration must exclude affected rows, do it in a saved query, comment the exclusion, and say so.
- **Findings.** EDA produces none. To make a pattern a finding, add it to the composition entry and run that entry under the analysis guide; only then does it enter Current findings.

Report the dataset and scope, the observations, each anomaly and where it was routed, the saved query paths, the records changed, and the scan path.
