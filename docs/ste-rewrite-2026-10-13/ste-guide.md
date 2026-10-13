# ASD-STE100 rewrite guide for this repository

You rewrite prose in Markdown files into ASD-STE100 Simplified Technical English (STE).
The rewrite changes how sentences are written and nothing else. Every fact, condition,
exception, number, requirement and its strength must survive. These files are often
instructions that AI agents follow, so a changed condition or modal changes behavior.

After you finish, a separate auditor compares every paragraph, list item and table cell of
your rewrite with the original and reports each case of SEMANTIC DRIFT: a changed requirement
strength, a dropped or added condition or exception, a changed scope ("only", "unless",
"before"), a dropped or added fact, example or caveat, a changed actor (who does what), or a
term replaced by a word with a different meaning. The audit script below only checks
structure (markup, code, numbers, links). Passing it does not prove that the meaning is the
same, so check meaning yourself, item by item.

## A. Invariants: keep these byte-identical (the audit script fails on any change)

1. YAML frontmatter keys, and the `name:` line. You may rewrite the `description:` value
   into STE, but keep it on one line, keep valid YAML, and keep every trigger phrase and
   skill name it lists (hosts match requests against it).
2. Every heading line (`#`..`######`), exactly. Do not reword, add or remove headings.
3. Every fenced code block, exactly.
4. Every inline code span (`like this`). Do not add, drop or alter code spans. The SET must
   stay the same; a count can change only when a sentence split needs it.
5. Every link target `](...)` and every URL. Link text can change.
6. Every number (including percentages and version numbers) outside code. The set must stay
   the same.
7. Every HTML comment (`<!-- ... -->`), including `<!-- dist:exclude -->` markers.
8. Tables: keep the header row, the separator row and the number of rows. You can rewrite
   prose inside body cells. Keep cells that hold only code, IDs, statuses or numbers.
9. Text in quotation marks that quotes something verbatim (a user's words, a tool message, an
   error string, a prompt) stays verbatim.
10. Glossary terms and technical names stay as they are: Project, Data foundation, Canonical
    data, Landed data, Acquisition, Publication, Investigation, Run script, Finding, Flagged,
    Stale, Delivery package, Package format, Working draft, Release, Frozen, Disposition,
    Investigation state, EDA, and the names of skills, files, commands, statuses and products.
    Technical names (for example "data cleaning", "landing") can keep an -ing form.
11. Extra protected literals: any string listed for your file in
    `tools/protected.json` must still occur in the file exactly. Code parses or tests
    many of them (marker lines such as `Active investigation:`, `Keep this a short list.`).
12. Never use the phrase "load-bearing" or its derivatives.

## B. STE writing rules to apply

Words
- Use simple, common words with one meaning. Use the same word for the same thing every time.
- Replace: ensure -> make sure; utilize -> use; prior to -> before; in order to -> to;
  via -> through / with; e.g. -> for example; i.e. -> that is; etc. -> list the items or
  delete; whether -> if; since (cause) -> because; while (contrast) -> but;
  once (=after) -> after / when; require -> need / must have; obtain -> get;
  perform -> do / make; additional -> more / other; sufficient -> enough;
  appropriate -> correct / applicable; approximately -> approximately is OK but prefer "about";
  thus/hence/therefore -> thus is not approved, use "then" / "as a result" / "for this reason".
- No contractions. Do not omit articles ("the", "a") to make sentences shorter.
- Noun clusters: max 3 nouns. Break longer ones with "of", "for", "in".

Verbs
- Active voice. Passive is acceptable in descriptive text only when the agent is unknown or
  not important.
- Simple tenses only: present, simple past, future (will). No perfect or progressive
  tenses where a simple tense says the same thing.
- No -ing forms (gerunds, present participles) except in technical names.
- Past participles only as adjectives or in a passive with is/are/was/were.

Modals: KEEP THE STRENGTH. This is the main risk of drift.
- Requirement (must, have to, need to, is required, never, always): use an imperative
  ("Do X." / "Do not do X.") or "must". Keep "never" and "always" when the original has them.
- Recommendation (should, it is best, prefer): do NOT turn it into must. Write
  "If possible, do X." or "We recommend that you do X." or "It is better to do X than Y."
- Prediction ("this should pass", "will likely"): "this will pass" / "this usually passes".
- Permission or possibility (may, might, could): "can" / "possibly" / "it is possible that".
- "only", "unless", "except", "not", "no", "at least", "at most", "before", "after":
  keep every one with the same scope. "Only X does Y" is not "X does only Y".

Sentences
- One topic per sentence. One instruction per sentence (unless two actions happen together).
- Max 20 words in a procedural sentence (an instruction), max 25 in a descriptive sentence.
  A code span, a link, a number or a hyphenated word counts as one word.
- Put a condition before the instruction: "If X, do Y." / "When X, do Y."
- Use a vertical list when a sentence holds a series of steps, conditions or 3+ items.
  Adding list items is acceptable; keep the order of steps.
- No semicolons. Make two sentences or a list. Do not use dashes (— or --) to insert
  clauses; use parentheses, a new sentence or a comma. A colon before a list or a
  definition is OK.
- Paragraphs: max 6 sentences, one topic, the first sentence gives the topic.

Procedures and warnings
- Write instructions as commands (imperative), addressed to the reader ("you" if needed).
- A warning or caution starts with a clear command.

## C. What not to do

- Do not add facts, examples, advice or explanations that are not in the original.
- Do not delete facts, cross-references, caveats or examples.
- Do not restructure the document, move sections, or merge sections.
- Do not "fix" content you think is wrong. Report it in your final message instead.
- Do not touch non-Markdown files, except where this guide or your task says so.

## D. Process for each file

1. Read the whole original file.
2. Rewrite it paragraph by paragraph, list item by list item, table cell by table cell.
   For a long file, write it in sections with several Edit calls if one Write is too large.
3. Run the audit for your files from the repository root:
   `python3 docs/ste-rewrite-2026-10-13/tools/audit.py --base 6ebca3a -v <files>`
   Fix every ERROR. Read every WARN and fix it unless the change is a correct STE rewrite
   with the same meaning (for example "should" became "If possible, ..."). Reduce
   `>25` and `';'` to zero or close to zero, and `>20` as far as the content allows.
4. Re-read the original and your rewrite side by side for each paragraph. Confirm that
   every condition, exception, number, negation and modal strength is the same.
