---
name: awb-scope
description: "Start or refine an analytics workbench investigation. Use for \"let's investigate this question\", \"work through the open questions\", or \"change the population or period\"; interview the user and keep the question ledger."
---

# Scope an investigation

Interview the user until the investigation knows what it must answer, for whom, and what it still does not know. Settled decisions go in the brief; every question still open goes in the investigation's question ledger, `questions.md`, rendered from `questions.json`. Scoping writes investigation records only; data work, analysis, and packages follow on request.

## 1. Find the investigation

1. Use the project the user names, otherwise the current directory. A workbench has `src/awb.py`; without it, stop and suggest `awb-init`, which sets one up and hands the question back here. A workbench `awb-init` has just set up has no `investigations/` yet; the New branch creates it.
2. Run `python3 src/awb.py state` for the active investigation's brief, state, and open ledger questions, and `python3 src/awb.py questions list --all` for its whole ledger; pass `--investigation <name>` to either for another. When `state` reports no active investigation and none holds the question, skip the ledger listing and take the New branch.
3. Choose the branch:
   - **New**: no investigation holds this question.
   - **Sharpen**: the user wants to dig into an investigation's question or answer its open questions.
   - **Rescope**: the user changes an investigation's population, period, purpose, or question.

An expansion of the same ask to a population containing the original group is a rescope of that investigation. The same questions about an independent group start a new one, which inherits the current method, settings, and package format unless corrected, with fresh findings, progress, and ledger; read the related investigation's findings only as context for method. Ask about a genuinely ambiguous boundary rather than stretching these examples.

## 2. Interview

Cover the business question, population or scope, the decision it supports or an exploratory purpose, usefulness criteria, and material unknowns. Record any reader the user describes in the brief's Audience section; `awb-package` asks for it when a package needs it.

**Pace by dependency.** Settle the choices that constrain others first. Ask a decision alone when its answer shapes the next question; ask decisions at the same level together, at most four, each with a recommended answer and its reason. In a rescope, carry settled answers forward and ask only about the decisions the change reopens.

**Follow up before moving on.** When an answer is vague, hedged, or conflicts with an earlier one, restate it as a concrete case, such as "so a customer who downgrades but keeps paying has not churned?", and ask the user to confirm or correct it. Leave no answer recorded in a form two analysts could read differently.

**Dig into what makes an answer usable.** For each branch, push on:

- the definition of the measure and of each population term, tested with a concrete example and against source data and analytical logic when they exist;
- the comparison that gives a number meaning: baseline, period, or peer group;
- the result that would change the decision, and who acts on it;
- what is already believed, so a result that confirms or contradicts it is recognized.

**Sort every question by who can answer it.** Look facts up yourself in the repository, catalog, and source systems, and answer a question a quick lookup settles. Ask the user only for decisions and context only they hold. Record a question the data must answer through analysis with `--answerer data`, and one only someone else can answer with `--answerer stakeholder`, naming them in the question. Never put a data question to the user.

**Give each recorded question a priority and parent**: `must` when the decision cannot be made without its answer, `could` when the answer only refines it, `should` otherwise. Status counts the roots, the questions with an empty parent, as the user's own, so a root is only a question the user asked: record each one they ask, as a data question when the data answers it. Every other question, such as a stakeholder's threshold, a decision the user deferred, or a method choice, takes as parent the user's question it serves, the first of them when it serves them all.

**Record meanings where they belong.** Shared meanings go in `foundation/glossary.md`, an investigation's departure in its brief's Local terms section, dataset and view descriptions in `foundation/catalog.md`, consequential analytical decisions in its history; never in `CONTEXT.md` or ADRs.

Before writing the records, ask the user every open decision they can answer, and the context only they hold, bundling those at the same level, method choices included, as **Pace by dependency** says; record one as an open user question only when the user defers it. The interview is done when the question, population, purpose, and usefulness criteria are each settled in the brief or held open as a ledger question with its answerer, such as a usefulness threshold only a stakeholder owns or a decision the user deferred, which that brief section names by ID; every other material unknown is an open ledger question with its answerer; and no answer received is still vague. Write the records without a separate confirmation round.

## 3. Write the records

Ledger commands run from the project root; `python3 src/awb.py questions --help` gives every argument. Add each question the interview leaves open, and each answered context question that later analysis relies on, such as a stakeholder's definition:

```sh
python3 src/awb.py questions add "<one-line question>" --kind context|decision|analytical --answerer user|stakeholder|data --origin scope --priority <priority> --parent "<parent ID or empty>" --unblocks "<what an answer decides>"
python3 src/awb.py questions answer Q-NNN --text "<the answer>" --by "<the user or a named stakeholder>"
```

A settled scope or purpose decision belongs in the brief, not the ledger. A data question is answered only by a recorded result whose settings table declares it; `workbench-guides/analysis.md` says how.

- **New.** Create `investigations/<slug>/`, its slug named for the question rather than the population so a rescope keeps it right. Adapt the [brief](../awb-init/assets/workbench/investigation/brief.md), [state](../awb-init/assets/workbench/investigation/state.md), and [history](../awb-init/assets/workbench/investigation/history.md), and copy [run.py](../awb-init/assets/workbench/investigation/run.py) with its [settings.toml](../awb-init/assets/workbench/investigation/settings.toml); populate them with settled facts, and record an inherited method in the brief's Starting method section. Make it active with `python3 src/awb.py state switch <slug>`, then add the user's questions, then the other open questions under them, and write into each held-open brief section the ID `add` printed; with none, `python3 src/awb.py questions render` writes the empty ledger.
- **Sharpen.** Revise the brief sections the answers changed, add or answer ledger questions, and adjust priority and parent as roles change: `python3 src/awb.py questions edit Q-NNN --priority <priority> --parent "<parent ID or empty>"`. A root the user did not ask, which an older ledger may hold, takes as parent the user's question it serves, recorded first as a root from the brief when the ledger lacks it.
- **Rescope.** Revise the brief, the population and period in `settings.toml`, and the state to the settled scope. Write a history entry for the scope change naming the findings it supersedes. Supersede each ledger question the change invalidates, keeping its answer, and add its replacement: `python3 src/awb.py questions status Q-NNN --set superseded --reason "<the change>"`; point any brief section that named the superseded question at its replacement's ID. Adjust surviving questions' priority and parent as in Sharpen.

An investigation without `questions.json` predates the ledger: move each item of its brief's Material unknowns, and each Next steps item phrased as a question, into the ledger, then leave Material unknowns with the template's pointer line and drop the moved steps with `python3 src/awb.py state next --drop <number>`.

## 4. Report

Summarize the investigation, what was settled, the records created or changed, and the open questions grouped by who answers them: those the user deferred, to take up through `awb-scope` when they choose, each stakeholder's to collect, and the data's for `awb-explore` or analysis. When few questions stay open or the user wants to widen the inquiry, suggest `awb-brainstorm`. Suggest `awb-status` for where things stand.
