# ASD-STE100 rewrite and semantic-drift audit, 2026-10-13

This folder records the rewrite of the prose files of this repository into ASD-STE100 Simplified Technical English (STE). It also records the audit that compared each rewritten file with its original for semantic drift. The original files are at commit `6ebca3a`.

## Scope

The rewrite covers all 52 Markdown files that existed at `6ebca3a`:

- the six skills, their references, and the templates that `awb-init` and `awb-package` copy into projects
- `README.md`, `CONTEXT.md`, and `CHANGELOG.md`
- every document under `docs/`

The rewrite does not cover these files:

- `LICENSE`. It is the MIT license text. A reworded license is a different legal text.
- The `.txt` and `.tsv` files under `docs/tool-call-audit-2026-10-11/`. They are measurement data and transcript extracts, not prose.
- Python docstrings and comments. They are code, not prose files.

One non-Markdown file changed: `SOURCES_TEMPLATE` in `.agents/skills/awb-init/assets/awb_landing.py`. A test keeps it byte-equal to `foundation/sources.md`, so it changes with that file.

## Method

1. A rule set, [ste-guide.md](ste-guide.md), gave the STE writing rules and the invariants for every rewrite. The main rule is that the rewrite keeps the meaning. Each requirement keeps its strength. A recommendation ("should") does not become a requirement ("must").
2. Nine agents rewrote the files in nine batches.
3. A structural check, [tools/audit.py](tools/audit.py), compared each file with `6ebca3a`. It fails when a heading, code block, code span, link, number, table header, HTML comment, or protected literal changes. Code parses or tests the protected literals in [tools/protected.json](tools/protected.json). [tools/protected.py](tools/protected.py) makes that list from the string literals in the Python files. The check only finds structural changes. It does not find a change of meaning.
4. For the semantic-drift audit, separate agents (not the agents that did the rewrite) read each original and each rewrite completely. They compared them one unit at a time (paragraph, list item, table cell, frontmatter description), and recorded each drift with a category and a severity:
   - HIGH: the drift changes what an agent or a user does, a requirement, or a factual claim.
   - MEDIUM: the drift loses nuance or a reason that a reader needs.
   - LOW: the drift is a small change of shading.
5. The auditors fixed every HIGH and MEDIUM finding, and most LOW findings. Then the structural check, the test suite, and `scripts/build-dist.sh` ran again.

## Results

| Measure | Value |
| --- | --- |
| Files audited | 52 |
| Units compared | 1957 |
| Drift findings | 38 (3 HIGH, 5 MEDIUM, 30 LOW) |
| Findings fixed | 32 (all HIGH and MEDIUM) |
| Findings kept, with a reason | 6 (all LOW) |
| Structural check | 0 errors in 52 files |
| Tests | 319 passed, 1 skipped (the same as at `6ebca3a`) |
| Mean sentence length | 15.9 words before, 11.0 words after |
| Sentences over 25 words | 507 before, 157 after |
| Semicolons in sentences | 728 before, 72 after |

The categories of the 38 findings are: scope 10, term 9, actor 9, modal 3, condition 2, sequence 2, omission 1, addition 1, quote 1. [findings.tsv](findings.tsv) lists each finding with the original text, the drifted text, and the resolution. [units.tsv](units.tsv) gives the number of units and findings for each file.

The three HIGH findings were these:

- `awb-clean/SKILL.md`: "every in-scope `S<n>`, including any past stdout's 25, has a class" became a sentence about the issues of "each earlier stdout". The original means the issues after the first 25, which stdout does not show. With the drift, an agent could skip those issues. The fix restores the meaning.
- `CONTEXT.md` and `CHANGELOG.md`: "Awaiting revalidation" became "Pending revalidation". The package templates use the label `**Awaiting revalidation:**`, so the glossary must use the same words. The fix restores the term.

Most drift came from three causes:

- Scope (10 findings): a sentence split or a new word order moved the scope of "only", "each", or "whether or not".
- Actor (9 findings): a description became an instruction, or the rewrite gave a subject that the original did not give.
- Term (9 findings): a word changed to a word with a different or less exact meaning, for example "distinct" to "different".

In many of these findings, the rewriter chose one reading of an ambiguous original. The fix keeps the original ambiguity.

## Limits

- The rewriters did not have the licensed ASD-STE100 dictionary. The rewrite applies the STE writing rules and a set of well-known word replacements. It is not a certified STE text, and some words are not in the STE dictionary.
- These items keep their original wording:
  - headings, because code parses some of them and links use them as anchors
  - text that the code parses
  - verbatim quotes
  - the `description` lines in the frontmatter of the six skills. Hosts compare requests with these lines to select a skill, so a change of words can change which skill runs.
- 157 sentences are still longer than 25 words. Most are verbatim quotes or proposed replacement text in the review records. Some are a bold label that the sentence counter joins to the next sentence.
- The audit is a model-based reading, not a proof. Each file had one independent auditor.

## Decision for the owner

The rewrite also changed records that were verbatim before:

- `docs/tool-call-audit-2026-10-11/blind-rerun/BRIEF.template.md` is the prompt that the two recorded blind runs received. The audit found that its meaning is the same, but it is no longer the exact prompt. A rerun that must be comparable with the recorded runs must use the original text. To get it, run `git show 6ebca3a:docs/tool-call-audit-2026-10-11/blind-rerun/BRIEF.template.md`.
- The two Codex reports, the two PR-review records, and the dated skill reviews are now STE versions of what their authors wrote. The quotes in them are still verbatim.

If these files must stay verbatim, restore them from `6ebca3a`.

## Reproduce the structural check

From the repository root:

```sh
python3 docs/ste-rewrite-2026-10-13/tools/audit.py --base 6ebca3a -v $(git ls-files '*.md' ':!docs/ste-rewrite-2026-10-13')
```
