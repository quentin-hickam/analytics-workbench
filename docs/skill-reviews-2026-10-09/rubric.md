# Review rubric: writing for agents

Derived from the `writing-for-agents` skill (source: the `writing-for-agents` skill in mattpocock/skills, its SKILL.md and SKILL-MECHANICS.md). Read both source files first; this rubric is the checklist, they are the authority.

Apply every check below to every agent-facing Markdown file in scope. Python helpers count only where an agent reads them (docstrings, `--help`, output an agent interprets).

## R1. Description as context pointer (SKILL.md frontmatter)
- States what the skill is, then one trigger per distinct branch. Synonyms that rename one branch are duplication.
- Leading word front-loaded.
- Cuts identity the body already carries; every word is paid on every turn.
- Invocation choice fits: model-invoked only if the agent or another skill must reach it unprompted.

## R2. In-body context pointers
- Every link to a reference/asset states what it is and the condition (branch) for reading it.
- Must-have material behind a weakly worded pointer is a variance bug. Flag where the condition is vague ("when relevant") or where the agent cannot tell whether it is on that branch.

## R3. Information hierarchy and progressive disclosure
- Steps (ordered actions) are visible and not buried under reference.
- Inline what every branch needs; disclose behind a pointer what only some branches reach.
- Flag over-disclosure: material every run needs pushed into a file anyway (extra hop, risk it is skipped).
- Flag under-disclosure: branch-specific reference inlined in the main file.

## R4. Co-location
- One concept's definition, rules, and caveats sit under one heading. Flag a meaning fragmented across sections or files.

## R5. Sprawl
- A file that is too long even if every line is live. Estimate what could move down the ladder or be cut.

## R6. Completion criteria
- Every step ends on a criterion the agent can check (clarity) and that demands the right amount of legwork (demand: "every X accounted for").
- Flag vague bounds that invite premature completion, and steps with no stated end.

## R7. Splitting
- By sequence: later steps visible enough to tempt rushing an earlier, fuzzy step.
- By invocation: content that should be (or should not be) its own model-invoked skill.

## R8. Leading words
- Restatements (triads, repeated multi-word phrases, sentences gesturing at one idea) that a single pretrained word would retire. Propose the word.
- Coined terms that cost definition tokens where a pretrained word exists.
- Leading words too weak to beat the model's default.

## R9. Negation
- Steering by prohibition ("never", "do not", "no X") where the positive target could be stated. Keep only hard guardrails that cannot be phrased positively, and then check they are paired with the positive target.

## R10. Single source of truth / duplication
- The same meaning stated in more than one place, within this skill or across sibling skills, project templates, and references. Name the authoritative home.

## R11. Environment as source of truth (cache)
- Restating what the agent can cheaply look up (file layouts, helper signatures visible in code, `--help`). Keep only expensive-to-find knowledge: unwritten conventions, reasons, gotchas.

## R12. Relevance and sediment
- Lines that never bear on the task (exposition, history, rationale the agent does not act on) or have gone stale (contradict current files, name things that no longer exist).

## R13. No-ops
- Sentences the model already obeys by default. Delete the whole sentence. Model-relative: judge against a capable current model's default behaviour.

## Severity
- high: likely to change agent behaviour run-to-run (variance), cause a wrong or skipped action, or stale/contradictory instruction.
- medium: material load or legibility cost; clear duplication; weak pointer to useful material.
- low: polish, small token savings.
