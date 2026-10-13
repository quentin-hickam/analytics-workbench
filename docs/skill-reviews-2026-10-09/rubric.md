# Review rubric: writing for agents

This rubric comes from the `writing-for-agents` skill (source: the `writing-for-agents` skill in mattpocock/skills, its SKILL.md and SKILL-MECHANICS.md). Read the two source files first. This rubric is the checklist, and the two source files are the authority.

Apply every check below to every agent-facing Markdown file in the scope. Python helpers are in the scope only where an agent reads them (docstrings, `--help`, output that an agent interprets).

## R1. Description as context pointer (SKILL.md frontmatter)
- The description states what the skill is. Then it gives one trigger for each distinct branch. Synonyms that rename one branch are duplication.
- The leading word is at the start.
- The description cuts identity that the body already carries. Each word has a cost on every turn.
- The invocation choice is correct: the skill is model-invoked only if the agent or another skill must reach it without a prompt.

## R2. In-body context pointers
- Every link to a reference or asset states what the file is and the condition (branch) in which to read it.
- If must-have material is behind a weakly worded pointer, that is a variance bug. Flag each place where the condition is vague ("when relevant"). Also flag each place where the agent cannot tell if it is on that branch.

## R3. Information hierarchy and progressive disclosure
- Steps (ordered actions) are visible. Reference material does not bury them.
- Put inline the material that every branch needs. Put behind a pointer the material that only some branches reach.
- Flag over-disclosure: material that every run needs, but that is pushed into a file anyway. This adds an extra hop and a risk that the agent skips it.
- Flag under-disclosure: branch-specific reference material that is inline in the main file.

## R4. Co-location
- The definition, rules, and caveats of one concept are under one heading. Flag a meaning that is in fragments across sections or files.

## R5. Sprawl
- A file that is too long, even if every line is live. Estimate which material can move down the ladder, and which material can be cut.

## R6. Completion criteria
- Every step ends on a criterion that the agent can check (clarity). The criterion also demands the right quantity of work (demand: "every X accounted for").
- Flag vague bounds that encourage completion too early. Also flag steps that have no stated end.

## R7. Splitting
- By sequence: later steps are visible enough to tempt the agent to rush an earlier, fuzzy step.
- By invocation: content that it is better to make its own model-invoked skill, or better not to make its own model-invoked skill.

## R8. Leading words
- Restatements that one pretrained word can retire: triads, repeated multi-word phrases, and sentences that point at one idea. Propose the word.
- Coined terms that cost definition tokens where a pretrained word exists.
- Leading words that are too weak to win against the default of the model.

## R9. Negation
- Prohibitions ("never", "do not", "no X") that steer the agent where the text can state the positive target. Keep only hard guardrails that cannot be phrased positively. Then check that each of these guardrails is paired with the positive target.

## R10. Single source of truth / duplication
- The same meaning stated in more than one place: in this skill, or across sibling skills, project templates, and references. Name the authoritative home.

## R11. Environment as source of truth (cache)
- Text that restates what the agent can look up at a low cost (file layouts, helper signatures that are visible in code, `--help`). Keep only knowledge that is expensive to find: unwritten conventions, reasons, and gotchas.

## R12. Relevance and sediment
- Lines that never bear on the task (exposition, history, rationale that the agent does not act on). Also lines that are stale (they contradict current files, or they name things that no longer exist).

## R13. No-ops
- Sentences that the model already obeys by default. Delete the whole sentence. This check is model-relative: compare with the default behaviour of a capable current model.

## Severity
- high: the issue probably changes agent behaviour run-to-run (variance), causes a wrong or skipped action, or is a stale or contradictory instruction.
- medium: a material cost in load or legibility, a clear duplication, or a weak pointer to useful material.
- low: polish, or small token savings.
