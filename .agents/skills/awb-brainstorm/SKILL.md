---
name: awb-brainstorm
description: "Propose questions from an analytics workbench investigation's questions, findings, and available data. Use for \"what else should we ask?\", \"what else could we investigate?\", or when open questions run out."
---

# Brainstorm questions for an investigation

Propose questions; the user chooses. This skill reads records, runs no queries, and writes only the ledger rows the user's choices produce.

## 1. Read

Use the investigation the user names, otherwise the README's active one; for one other than the active one, pass `--investigation <name>` to every `awb.py state` and `awb.py questions` command in this skill. From the project root:

```sh
python3 src/awb.py state
python3 src/awb.py questions list --all
```

The first gives the brief, the state with its findings, and the open questions; the second every ledger question, each answered one with its linked findings' current status and each parked or declined one with its reason. Read `foundation/catalog.md` for the datasets and views available, and the `open` rows of `foundation/quality.md` for coverage gaps. Leave other investigations' conclusions unread unless the user asks.

## 2. Propose

Draw candidates from each of these:

- **Answers.** What each answer implies next: the segment, mechanism, or comparison that would test or extend a finding, and an answer resting on a provisional or flagged finding.
- **Findings.** Contrary patterns and caveats that no question addresses.
- **Open questions.** A broad question split into parts that can be answered, and a question no one can answer reframed into one that can.
- **The brief.** Definitions, baselines, and the result that would change the decision when no question yet tests them.
- **Data.** A cataloged dataset or view the investigation has not used that bears on the question.

Keep a candidate only when it passes every test:

- It is not already in the ledger in any status. Propose a declined or parked question again only when you can name what changed since its recorded reason.
- It names what prompted it (question and result IDs), who can answer it (user, a named stakeholder, or the data, naming the dataset or view), and the decision or usefulness criterion it serves; cut one that serves neither.
- Its placement is clear: within the current scope; needing a scope change, which `awb-scope` handles; or a separate investigation. Most belong in scope.
- A question asking why from observational data can be answered as an association at most; say so beside it.

Present five to eight, numbered and ranked by how much an answer could change the decision, one line each with its prompt, answerer, and placement. Ask which to keep, park, or decline.

## 3. Record the choices

From the project root, with `--origin brainstorm`, the priority the ranking implies (`must` when the decision cannot be made without the answer, `could` when the answer only refines it, `should` otherwise), and the question it serves as parent, empty for a root.

- **Kept, in scope**: `python3 src/awb.py questions add "<question>" --kind <kind> --answerer <answerer> --origin brainstorm --priority <priority> --parent "<parent ID or empty>" --unblocks "<what it serves>"`. A re-proposed parked or declined question the user keeps is reopened instead, keeping its ID: `python3 src/awb.py questions status Q-NNN --set open`, then `python3 src/awb.py questions edit Q-NNN --priority <priority> --parent "<parent ID or empty>"`.
- **Parked or declined**: the same command with `--status parked` or `--status declined` and `--reason "<the user's reason>"`. A re-proposed question keeps its ID: change its status with `python3 src/awb.py questions status Q-NNN --set parked|declined --reason "<the user's reason>"`, or leave it as it is when its status does not change. Record every in-scope proposal the user did not keep as declined with the reason `not chosen`, so later brainstorms do not repeat it, and say so in the report.
- **Needing a scope change or a new investigation**: add nothing; suggest `awb-scope` with the question.

## 4. Report

Report the questions added, the counts parked and declined, and what comes next: data questions through `awb-explore` or analysis, questions for the user or a stakeholder through `awb-scope`, and each scope change through `awb-scope`.
