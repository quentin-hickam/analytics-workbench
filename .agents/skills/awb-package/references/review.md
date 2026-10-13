# Draft review

`awb-package` runs this review before its final `check-draft`, and `awb-release` before `release`. The reviewer reads the draft and reports; the agent that wrote the draft repairs. Repository paths are relative to the project root.

## Launch

Start a fresh subagent with only read tools: `Read`, `Grep`, `Glob`, and `Bash` for the one command below. In Claude Code, use a subagent type without edit tools, such as the built-in `Plan`, or a custom one whose `tools` are `Read, Grep, Glob, Bash`; a skill's `allowed-tools` only pre-approves tools and restricts nothing. Bash can still write, so this is a convention plus tool scoping, not isolation. Give it the investigation, the package, the project root, and the path of this file, and tell it to follow **Brief**.

In Codex, whose subagents inherit the session's sandbox and tools, or in any host without a read-only subagent, follow **Brief** yourself: edit nothing and run only the command below until the report is complete, then repair.

## Brief

You review the package draft at `deliveries/<investigation>/<package>/draft/`. Report findings; never fix them, and change no file. Run only `python3 src/awb.py review-rules check <investigation> <package>`, which writes nothing.

1. Run that command. Read `foundation/review-rules.md` when its `rules_file` is not `none recorded`, then the draft's `findings.md`, `methodology.md`, and the `revalidation_flags` in `manifest.json`.
2. Judge every rule the command lists that is not `retired`, against both narratives. A `matched` line is a candidate to judge, not a verdict; `no match` and `no pattern` rules are judged by reading.
3. Check what no command checks: both narratives carry the same numbers, qualifications, and caveats; every `represented_in` place of each `revalidation_flags` entry carries its caveat, or its omission when the disposition is `omit`; every claim in `findings.md` traces to `methodology.md`.
4. Report, and nothing else:
   - one line per rule in the command's order: `<ID> pass`, `<ID> retired`, or `<ID> violation <file>:<line> "<short quote>"` with the rule's severity, one line per violation;
   - one line per step 3 problem: `narrative <file>:<line> "<short quote>" <what is wrong>`;
   - the command's `problems` and `errors` verbatim; and
   - a last line, `review: clean` or `review: <n> violations (<e> error)`.

## After the review

In `awb-package`, repair every `error` violation and every narrative problem, and repair a `warning` violation or report it for the user to accept; a repair that changes the narratives gets a fresh review. `awb-release` repairs nothing and acts as its **2. Review** says.

When the user corrects a draft while reviewing it, record the correction as a rule before repairing, so every later review checks it: `python3 src/awb.py review-rules add --area <area> --severity <error or warning> --rule "<what every draft must do>" --fix "<how to repair it>" [--pattern '<regex>']`. The area names what the rule governs, such as `periods` or `metric-definitions`; give a pattern when one line of text can show the violation. A correction that applies to one slide only, such as a preferred wording, is an edit, not a rule. Report the new ID.
