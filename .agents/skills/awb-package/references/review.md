# Draft review

`awb-package` runs this review before its final `check-draft`, and `awb-release` before `release`. The reviewer reads the draft and reports; the agent that wrote the draft repairs. Repository paths are relative to the project root.

## Launch

Start a fresh subagent, so the agent that wrote the draft does not review it. Give it the investigation, the package, the absolute project root, and the absolute path of this file, and tell it to follow **Brief**. Scope its tools by host:

- In VS Code Copilot, use `runSubagent` under the installed user-level `awb-package-reviewer` custom agent, whose definition ships at `../assets/awb-package-reviewer.agent.md`. It has only file read/search and `awb/read`; run the check with `command: "review-rules"`, `project`, `investigation`, and `package`. If the reviewer agent is unavailable, report the failure and stop; name the remedy: install the reviewer agent per the README and choose the Local session target. If its `awb/read` call is unavailable or fails, the reviewer reports `command failed` with the diagnostic and the remedy: register the `awb` server, or choose the Local session target. Never substitute an unrestricted subagent or `awb/*`.
- In Claude Code, use a subagent type without edit tools, such as the built-in `Plan`, or a custom one whose `tools` are `Read`, `Grep`, `Glob`, and `Bash`; a skill's `allowed-tools` only pre-approves tools and restricts nothing.
- In Codex, whose subagents inherit the session's sandbox and tools, start a fresh subagent all the same; the limit to read tools is then the brief's instruction alone.
- Only in a host with no subagents, follow **Brief** yourself, changing no file and running no command that writes until the report is complete, then act on it as **After the review** says. In `awb-package` that is a self-review by the agent that wrote the draft.

Bash in the Claude Code branch can still write, and Codex inherits tools, so those limits are conventions plus tool scoping where available. The Copilot custom agent has no shell or write tool.

## Brief

You review the package draft at `deliveries/<investigation>/<package>/draft/`. Report findings; never fix them, and change no file. Run no command that writes: the only `awb.py` command you run is `python3 src/awb.py review-rules check <investigation> <package>`, which writes nothing (in Copilot, use the MCP call in **Launch**), and where the host reads files only through a shell, read-only commands such as `cat`, `sed -n`, and `rg` are reads.

1. Run that command. Read `foundation/review-rules.md` when its `rules_file` is not `none recorded`, then the draft's `findings.md`, `methodology.md`, and the `revalidation_flags` in `manifest.json`.
2. Judge every rule the command lists that is not `retired`, against both narratives. A `matched` line is a candidate to judge, not a verdict; `no match`, `no pattern`, and `unchecked` rules are judged by reading.
3. Check what no command checks: both narratives carry the same qualifications and caveats; no finding is worded more strongly than its claim strength, including wording off the `claims` check's list, such as a verb of change with an agent as its subject ("the carrier raised late orders"); every `represented_in` place of each `revalidation_flags` entry carries its caveat, or its omission when the disposition is `omit`; every claim in `findings.md`, with its numbers, traces to the matching claim in `methodology.md`, since `check-draft` proves only that each number is recorded somewhere.
4. Report exactly this, and nothing else, since the caller must account for every rule verdict and diagnostic before summarizing them in chat:
   - one line per rule in the command's order: `<ID> pass`, `<ID> retired`, or `<ID> violation <severity> <file>:<line> "<short quote>"`, with the rule's `error` or `warning`, one line per violation;
   - one line per step 3 problem: `narrative <file>:<line> "<short quote>" <what is wrong>`;
   - the command's `problems` and `errors` verbatim, or `command failed` with its output when it could not complete (for an unavailable or failed `awb/read` call, include the remedy from **Launch**); and
   - a last line, `review: clean` when there is no violation, no narrative problem, and the command exited 0, or otherwise `review: <v> violations (<e> error), <n> narrative problems, <c> command problems`, where command problems count the `problems` and `errors` entries, or 1 when the command failed.

## After the review

A review is passed when its last line reports no `error` violation, no narrative problem, and no command problem, and the user has accepted every `warning` violation; anything else blocks completion and release.

In `awb-package`, repair every `error` violation, every narrative problem, and every command problem, and repair a `warning` violation or report it for the user to accept. A command problem is an unavailable or failed `awb/read` call, remedied by registering the `awb` server or choosing the Local session target; a missing or unreadable narrative, repaired in the draft; or a malformed section of `foundation/review-rules.md`, repaired in place without changing any rule ID; ask the user when a broken rule's intent is unclear. A review is stale once, after it, the narratives or `foundation/review-rules.md` change, or a `revalidation_flags` entry in `manifest.json` is added or removed or changes its finding, reason, `represented_in`, or whether its disposition is `omit`; a stale review is run again. `awb-release` repairs nothing and acts as its **2. Review** says.

When the user corrects a draft while reviewing it, decide whether later drafts could repeat the mistake. If they could, record the correction as a rule before repairing, so every later review checks it: `python3 src/awb.py review-rules add --area <area> --severity <error or warning> --rule "<what every draft must do>" --fix "<how to repair it>" [--pattern '<regex>']`. The area names what the rule governs, such as `periods` or `metric-definitions`; give a pattern when one line of text can show the violation. Report the new ID. A correction that applies to this draft only, such as a preferred wording on one slide, is an edit, not a rule.
