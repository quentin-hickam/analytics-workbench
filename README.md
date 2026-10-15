# Analytics workbench skills

A portable, agent-agnostic workflow for shared data preparation, distinct investigations, and repeatable delivery packages. Git tracks analytical code; GitHub hosting is not required.

You work with an AI agent that has these skills installed, such as GitHub Copilot in VS Code, Claude Code, or OpenAI Codex. You bring a business question and data. The agent prepares the data, answers your questions with numbers it records and checks, and writes the files a slide deck is built from.

## What you get

The end product is a delivery package: a folder of files that a deck is built from. It is not a .pptx. Nothing in the workbench draws slides.

- `findings.md`: the deck outline, slide by slide. After the title slide, each slide has a one-sentence headline, up to five bullets, caveats on the slide they qualify, speaker notes, and at most one chart's specification. A headline carries the slide's key number where it has one, and **Open questions** may run past five bullets to list every question the decision needs. The **Answer** slide is the executive summary.
- `charts/`: one data file per chart, holding exactly the rows the chart plots, rounded as the slide shows them and labeled in your audience's terms.
- `datasets/`: any tables you chose to send with the deck. You are asked, and none is a fine answer.
- `methodology-note.md`: an optional short methods note for your audience, in their terms: method, sources, definitions, exclusions, and limitations.
- `methodology.md`: the internal methodology reference, the full account of the analysis in the workbench's own names and IDs. The builder may consult it; your audience does not get it.
- `deck-rules.md` and `assembly/m365.md`: builder instructions. The deck rules say what any builder does with the outline and chart files; the assembly file holds the steps for the PowerPoint agent in Microsoft 365 Copilot.
- `START-HERE.md`: which files to send your audience, which to attach to the builder with the one-line prompt to send it, and which stay internal.
- `manifest.json`: the internal record of what the package holds and what produced it.

The deck always has a title slide, the **Answer** slide, at least one finding, **How we know**, and **Limitations and open caveats**. Other slides appear when they apply, such as **Open questions** while questions the decision needs are unanswered, or when you want them, such as **Implications**. When you agree, **How we know**, **Limitations and open caveats**, and individual findings can move to an appendix at the end.

To build the deck:

- **With Microsoft 365 Copilot.** In a Copilot app chat, add the PowerPoint agent, attach the files `START-HERE.md` lists, and send its prompt. The agent builds each slide from the outline, draws each chart as an editable chart from its data file, and asks you when something is unclear.
- **By hand.** A person can build the deck by hand from the same files: one slide per outline slide from `findings.md`, and each chart drawn from its file in `charts/`, following `deck-rules.md`. Another tool can work from them the same way.

A Microsoft 365 Copilot license is needed only for the Copilot route.

Each time you mark the package delivered, it becomes the next numbered release: 001, then 002, and so on. A release is frozen: it never changes, and later edits go into the next one. Each release is copied to the folder you name for releases; when the agent cannot reach that folder, it tells you what to copy there.

Along the way, answers come in chat, and the project folder keeps the record: for each investigation, its brief, its findings, its question ledger, and a history of decisions, with the saved queries and checked data behind them. A later session picks up from these files.

## Quick-start for analysts

### Before you start

- The skills must be installed in your agent host. If someone else installs your tools, [Install and administer](#install-and-administer) is for them.
- The computer needs Python 3.10 or later. Setup stops on an older Python and says so; ask whoever installs your tools for a newer one.
- Git keeps the project's code history on your computer. No GitHub account is needed. Without Git, the work still runs; the agent says so once and makes no commits.
- Open your agent in an empty folder, or in the folder that will hold the project.

### What to say first

Name the skill and give your question. The more you put in the first message, the fewer questions follow:

> Use awb-init to set up this project. The question is why overtime rose in Q3. The operations board decides next month whether to change rostering; they need about 8 slides and a one-page methods note. The data is in `inbox/`. Keep the original files in `/shared/analytics/landed/` and released packages in `/shared/analytics/releases/`.

Useful things to include:

- the business question, and the specific questions under it;
- who will see the result, the decision they own, and about how many slides;
- where the data is: files, a folder, or a web address;
- where to keep a copy of the original data, and where to keep released packages;
- whether you want to see the slide headlines before the full draft, as the checkpoint below describes.

Without a question, `awb-init` asks for one in a line. With no question yet, say so, and it sets up the project alone.

### What you will be asked

The agent asks in plain words, with its recommendation and the alternative.

1. **A scoping round.** Right after setup, the decisions only you can make, such as who counts in the population, the period, how a measure is defined, and what result would change the decision. They come up to four at a time, and a vague answer gets a follow-up with a concrete case. Facts the data or the files can settle, the agent looks up itself. You can put a decision off; it then waits in the question ledger.
2. **Installing Python packages.** When the project has its own Python environment, setup installs what the helpers need there and tells you in one line. It asks before installing anywhere else.
3. **Storage locations.** Before the agent first brings in data, where to keep a copy of the original files; before the first release, where to keep released packages. Data and releases stay out of the project's Git history, so these folders hold the lasting copies. Naming them in your first message usually saves the question within that session. Answer "none", and the agent warns that this computer holds the only copy.
4. **Audience and length**, when you first ask for a package, unless you said them earlier: who will see the deck, what they already know, the decision they own, their terms, and any length you want. The agent also asks which tables to send with the deck and, when you mention a methods note, whether your audience needs one. Otherwise the draft's report offers a methods note.
5. **The headline checkpoint.** You approve or reorder the slide headlines before the deck is built, in one of two modes:
   - **preview-and-wait**: you see the title and every headline first, and the full slides follow once you approve or reorder them.
   - **draft-then-review**: the agent writes the whole draft, then shows its headlines, marked provisional, for you to approve or reorder.

   A request that names a mode gets it, and one that gives the storyline or asks for the full draft gets draft-then-review. Otherwise the agent uses the mode you chose before, or preview-and-wait. With the headlines it reports the slide count against your length and, when there are too many, proposes what moves to the appendix. You can reorder the findings without changing which questions matter most. In either mode, a choice still open that would change the deck, such as wording for your audience you have not approved, stops the draft and is asked with the headlines.
6. **Release questions**, when you mark the package delivered: whether any draft label left in the deck's title or headings, such as DRAFT, should stay, and whether to accept any warning the final review raises.

You are asked for a disposition only when a finding the draft shows is flagged, while drafting or at release. With no flagged findings, the question never comes up.

### The usual requests, in order

Naming the skill tells the host which instructions to follow. Follow-ups such as "go ahead" need no skill name.

1. **Set up.** "Use awb-init to set up this project. The question is …" Setup hands your question straight to `awb-scope`, which asks the scoping round.
2. **Scope.** Bring later questions, open questions you can now answer, and changes of scope: "Use awb-scope to start an investigation into why sick leave rose in Q4." or "Use awb-scope — let's work through the open questions."
3. **Clean.** First ask the agent to bring your data in, unless it already has: "Bring in the files in `inbox/`." It keeps the original files unchanged, records where they came from, and converts them into checked tables. Then: "Use awb-clean to clean the orders data." Cleaning checks one dataset for errors such as duplicate rows, placeholder values, and inconsistent labels, decides with you where a fix would change meaning, and corrects the shared data once, so every investigation gets the fix. It helps before you analyze a dataset nobody has checked, and whenever a result looks wrong because of the data.
4. **Explore.** "Use awb-explore to explore the shifts data." It profiles one dataset within your question's scope: coverage, distributions, and patterns worth testing. It records what it learned and the questions it raises, but no findings. It helps when the data is new to you or the question is open-ended.
5. **Analyze.** No skill name is needed: "Answer question 2." or "Go ahead with the analysis." The agent computes each answer with saved queries, checks it, and records it as a finding. An untested explanation comes back as a question, not an answer.
6. **Status.** "Use awb-status — where are we?" One screen: your questions answered and open, the findings, anything at risk, and up to five requests you can type next.
7. **Package.** "Use awb-package to prepare a draft for the active investigation." It writes the one working draft, and later requests revise it. Corrections you make while reviewing it go through the same skill.
8. **Release.** "Use awb-release — mark the package delivered." It freezes the draft as the next numbered release and copies it to your release folder. If you ask for a change in the same message, you see the changed slides first. Its report lists every caveat the release still carries.

`awb-status` suggests clean and explore when they fit. When most of your questions are answered and only one or two stay open, or you want to widen the inquiry, ask "Use awb-brainstorm — what else should we ask?" It proposes new questions from those already asked and answered, the findings, and the data; you keep, park, or decline each.

### How many exchanges to expect

Six simulated first-time runs each took five questions on a public dataset from an empty folder to a first release. Counting each message the user sent that the agent answered, from the first message to the release, the runs took 6 to 11 exchanges, plus one closing message accepting the release. Each run took one to two and a quarter hours, most of it the agent's own work, since the simulated users replied within a minute or two. The longest replies, such as writing the full draft, took up to about half an hour.

Most of those users gave their questions, audience, length, and storage folders in the first message, so a shorter first message means more questions. The runs came before later changes, such as draft-then-review, so take the range as a guide, not a promise.

<!-- dist:exclude -->
The [UX simulation synthesis](docs/ux-simulation-2026-10-15/README.md) has each run's counts and transcript.
<!-- /dist:exclude -->

### Words you will meet

- **Finding**: a checked result the investigation records, with a status and how strongly the evidence supports it: descriptive, association, or causal. A slide never words a finding more strongly than that.
- **Canonical view**: the shared, agreed version of a dataset that every investigation reads. It reads the checked copy of your data, and cleaning corrects errors through it, so the original files never change and every investigation sees the same fix. Shared does not mean flawless: known limits are kept in the project's quality record.
- **Question ledger**: the investigation's list of every question it has raised, answered or not, with who can answer each: you, a stakeholder, or the data. Your own questions come first, and questions raised along the way sit under the one they serve. You can read it in the investigation's `questions.md`; ask the agent to change it rather than editing that file, which is rewritten from its record. A question about the data is answered only by a recorded result.
- **Receipt**: `.awb-receipt.json`, a file setup writes listing each file it installed with a checksum, so a later repair replaces only the copies nobody changed. You never need to open it.
- **Disposition**: your decision on a flagged finding the draft shows: recheck it, which pauses the release until the analysis is rerun; leave it out; or release it with its caveat stated. A finding is flagged when a later correction to the shared data, or a changed input, may affect it.
- **Review rule**: a numbered rule, such as `R-periods-001`, recorded from a correction you make to a draft that later drafts could repeat. Every later review of a draft checks it. A one-off edit, such as a preferred wording on one slide, is not a rule. The rules are kept in `foundation/review-rules.md`.
- **Release**: a frozen, numbered copy of the package, made only when you mark it delivered.

### Good to know

- A turn that changed the project's records ends with one plain line: what changed for your questions, if anything, and the next step.
- The agent commits code only when you ask, and reminds you at most once a session. Say "commit as you go" to switch.
- Your host may ask you to approve a command or tool call. That is the host's own prompt, not the workbench's.
- Setup may suggest, in one line, registering the workbench's `awb` tool server with your host. It cuts down those approvals, and the work runs without it; [Install and administer](#install-and-administer) covers it.
- The checks have limits. The package check confirms that every number in the narratives traces to a recorded result or is listed, with its reason, as coming from elsewhere, such as a fact you gave or a figure from an earlier release. A separate read-only reviewer reads the wording against your review rules and the evidence. Neither redoes the analysis, so read the headlines and caveats yourself.

## Included skills

Every skill name carries the `awb-` prefix, so typing `awb-` in a host that lists skills as commands shows every workbench action.

- [awb-init](.agents/skills/awb-init/SKILL.md): initialize a project for a first business question, or repair it and bring it up to date after installing newer skills. Its [project AGENTS.md template](.agents/skills/awb-init/assets/workbench/AGENTS.md) governs everyday analysis and recordkeeping.
- [awb-scope](.agents/skills/awb-scope/SKILL.md): start an investigation, dig into its business question and context through an interview, or change its scope. Every question left open goes into the investigation's question ledger, with who can answer it.
- [awb-brainstorm](.agents/skills/awb-brainstorm/SKILL.md): propose new questions from those already asked and answered, the findings, and the cataloged data; the ones you keep, park, or decline go into the ledger.
- [awb-clean](.agents/skills/awb-clean/SKILL.md): clean one dataset at the shared foundation level: scan it for candidate issues in one call, decide with you where meaning changes, correct them through canonical views, and record the quality rows and catalog cells and flag affected findings in one call.
- [awb-explore](.agents/skills/awb-explore/SKILL.md): explore one dataset for the active investigation with one scan within the investigation's scope and settings, follow up with saved queries, and record what was learned; shared data problems go to `awb-clean`, and a confirmed coverage gap becomes an open row in `foundation/quality.md`; exploration records no findings.
- [awb-status](.agents/skills/awb-status/SKILL.md): read-only report of where the project stands and the requests that fit right now.
- [awb-package](.agents/skills/awb-package/SKILL.md): create or revise a delivery package's working draft.
- [awb-release](.agents/skills/awb-release/SKILL.md): preserve a frozen, numbered release when you mark a package delivered, and copy releases to the project's recorded storage location.

## How it works

`awb-init` hands the question to `awb-scope`, which interviews you about it and creates the investigation. Each investigation keeps a question ledger, `questions.md`, of every question it has raised and who can answer it. A question about the data is answered only by a recorded result that declares it.

Analytical work follows the generated AGENTS.md instructions. The default data flow is independent source landing, validated Parquet datasets, and DuckDB views loaded into separate analytical sessions. Data gathering never writes directly into the canonical database as its only retained representation.

`awb-init` installs the project helpers under `src/` with its installer, `scripts/install_helpers.py`, records the interpreter it runs under on the project README's `Project interpreter` line, which `src/awb.py` reruns itself under, and writes a `requirements.txt` when the project declares no dependencies; it records what it installs in a receipt, `.awb-receipt.json`, so its `--upgrade` can bring unmodified earlier copies up to date. Mechanical work then runs as single commands whose outcomes the agent summarizes in plain words, and computation runs as saved queries rather than scratch scripts: `python3 src/awb.py --help` lists the commands (`sql`, `profile`, `land`, `retain`, `publish`, `state`, `questions`, `stale`, `export`, `review-rules`, `check-draft`, `release`, `copy-releases`). Each investigation's run script, `run.py`, produces, validates, and records its results in one run and writes their `state.md` rows; `state` prints the active investigation's brief and state to resume, and records finding wording and status, with history where due, and issues and next steps.

`awb-package` asks which datasets to include. Subsequent requests revise the same draft. Drafting never releases it. Before the draft's final check, and again before a release, a fresh reviewer subagent limited to read tools checks the narratives and every rule in `foundation/review-rules.md` and reports without fixing anything; only an agent host with no subagents has the drafting agent follow the same read-only review itself. Each correction you make while reviewing a draft that later drafts could repeat is appended there as a numbered rule, `R-<area>-NNN`, that every later review checks; a one-off edit, such as a preferred wording on one slide, is not.

`awb-release` preserves the next numbered release, frozen from then on. When the draft represents a flagged finding whose disposition is not yet chosen, it first asks you to choose one. Releases live under `deliveries/`, which the generated ignore rules exclude from Git, so before the first release `awb-release` asks where released packages are kept, records it in the project README, and copies each release there, as `<location>/<investigation>/<package>/<n>/`, when the location is reachable; `python3 src/awb.py copy-releases` copies existing releases when the location is recorded or changed later. M365 receives the audience-facing findings, written as a slide-by-slide deck outline, an internal methodology reference, one data file per chart, the deck rules any builder follows, and the Microsoft 365 assembly file; the datasets you chose, and the methods note when there is one, travel beside the deck and are not attached. In the Microsoft 365 Copilot app, the PowerPoint agent builds the deck from the outline, draws each chart as a native chart from its data file under the deck rules, and asks you when something is unclear. `check-draft` checks the outline against the slide rules, each chart specification against its file, and each chart file against its result's table under the rows, rounding, and labels `export` recorded, and writes `START-HERE.md` beside them: what to send your audience, the files and prompt that build the deck, and what stays internal. Checking the storyline means reading the outline's headings before anything is built.

Landed source data gets the same treatment. `data/raw/` is also excluded from Git, and a landed original often cannot be fetched again, so before the first acquisition is landed the agent asks where landed originals are kept outside the checkout, records it on the project README's `Landed data is kept at` line, and copies each completed landing there when the location is reachable. `awb-status` reports landed data that exists only in the checkout.

The third-party documentation a source assessment relies on, such as a data dictionary or codebook, is kept under `foundation/references/<source-id>/` and suggested for commit; material whose license or confidentiality bars committing it stays outside the checkout, recorded by location and checksum. `awb-status` reports a source assessed from documentation with no recorded reference.

## Install and administer

This section is for whoever installs the skills and sets up the agent host. An analyst working in an installed workbench can skip it.

### Requirements

- For package chart files, the chart helper that `awb-package` ships needs Python 3.10 or later and pandas.
- The project helpers need Python 3.10 or later (3.11 or later, or `tomli`, for TOML settings). `awb-init`'s installer declares and checks their packages: pandas for validation and charts, and `duckdb` for sessions, queries, and publication. `land()`, `publish()`, and `retain()` themselves use only the standard library, except that `publish()` needs `duckdb` to run a dataset's declared checks and, on Python 3.10, `tomli` to read an existing `foundation/datasets.toml`.
- For result validation under the project `AGENTS.md`, the analysis project's Python environment needs Python 3.10 or later and pandas. The shared validation file was tested with pandas 2.2.
- The `awb-clean` and `awb-explore` scans need Python 3.10 or later and the `duckdb` package in the project's interpreter (TOML settings need 3.11 or later, or `tomli`); the `awb-clean` record script needs only the standard library.
- The read-only status collector needs Python 3.10 or later and the standard library; unsupported project record formats use targeted manual reads.
<!-- dist:exclude -->
- pytest is needed only to run this repository's own tests under `tests/`; they exercise the shipped helper files and are not part of the distributed archive. The reference deck renderer in `tests/`, which proves the deck contract can be built from without Microsoft 365, also needs python-pptx; its tests skip without it.
<!-- /dist:exclude -->

### Install

Download `analytics-workbench-skills-vX.Y.Z.zip` from the repository's GitHub releases and unzip it anywhere. It unpacks to one folder, `analytics-workbench-skills/`, holding the eight `awb-*` skill folders beside this README, `LICENSE`, and `CHANGELOG.md`. Install those folders once in `~/.agents/skills/`, replacing earlier copies. Delete an `awb-update` folder left by an earlier release: its job now belongs to `awb-init`. Do not unzip the archive into the skills directory itself: a host looks for `<skills directory>/<skill name>/SKILL.md`, and the extra folder level hides the skills. In a clone of this repository, the same eight folders are under `.agents/skills/`.

The skills serve every project from the user-level directory; projects need no local copies.

After installing a newer release of the skills, bring each existing workbench up to date with `awb-init`'s repair:

> Use awb-init to repair this workbench.

Repair runs the helper installer with `--upgrade`. It installs missing helpers, guides, and the `foundation/references/` README and replaces only unmodified copies of earlier shipped helpers, package formats, workbench guides, and that README, which it recognizes from the checksum receipt it writes at each install; it reports customized copies for you to decide and removes retired files only when you ask. The agent then reconciles the project's adapted `AGENTS.md`, `README.md`, and `.gitignore` against the current templates.

#### Shared skills

- VS Code Copilot and OpenAI Codex read `~/.agents/skills/`. Codex also scans `.agents/skills/` in each directory from the working directory up to the repository root. See [VS Code skills](https://code.visualstudio.com/docs/agent-customization/agent-skills) and [Codex agent skills](https://developers.openai.com/codex/skills).
- For Claude Code, create one symlink per installed `awb-*` folder in `~/.claude/skills/`, pointing to its absolute path in `~/.agents/skills/`. Claude Code loads these directory symlinks. Preserve unrelated skills, and replace any earlier independent `awb-*` copies with the links after retaining local customizations. See [Claude Code skills](https://code.claude.com/docs/en/skills).
- Where symlinks are unavailable, copy the eight folders to both locations and update both together on every upgrade. VS Code prefers a successfully loaded copy in `~/.agents/skills/` over one of the same name in `~/.claude/skills/`.
- Other hosts: each `awb-*` folder follows the agent skills convention of a folder holding a `SKILL.md` with `name` and `description` frontmatter. Check the host's documentation for its user-level skills directory.

#### MCP server

After installing the skills, run this with a stable Python 3.10+ interpreter outside a project virtual environment to launch the server, replacing `<host>` with `copilot`, `claude`, or `codex`:

```sh
python3 ~/.agents/skills/awb-init/scripts/install_helpers.py --mcp-config <host>
```

The option prints the exact `awb` entry on stdout. On stderr it prints the host's own registration command, ready to paste into a POSIX shell such as bash or zsh, and then the entry's merge destination as the fallback. Before the command, it warns on stderr if the interpreter is older than Python 3.10 or runs inside a virtual environment, and still prints both. It runs no command and writes no configuration or project files.

Prefer the host's command: it adds the `awb` entry to the host's user-level configuration and keeps the rest. This matters most for Claude Code, which rewrites `~/.claude.json` with its own state while it runs, so a hand edit can be lost. The command quotes both paths, and Claude Code's JSON, for POSIX shells. In PowerShell or cmd, where quoting differs, or when the host's command is not installed, merge the printed entry into the existing file instead, preserving other servers and settings; do not replace the whole file with the snippet. For Claude Code, close every Claude Code session before that edit, so the edit is not lost. Use these user-level registrations:

| Host | Registration command | File | Printed format |
| --- | --- | --- | --- |
| VS Code Copilot | `copilot mcp add awb -- <python> <server>` (Copilot CLI) | `$COPILOT_HOME/mcp-config.json`, falling back to `~/.copilot/mcp-config.json` | JSON, top-level `mcpServers.awb`, `type: "stdio"` |
| Claude Code | `claude mcp add-json --scope user awb '<entry>'` | `$CLAUDE_CONFIG_DIR/.claude.json`, falling back to `~/.claude.json` | JSON, top-level `mcpServers.awb` (user scope, outside `projects`) |
| Codex | `codex mcp add awb -- <python> <server>` | `$CODEX_HOME/config.toml`, falling back to `~/.codex/config.toml` | TOML, `[mcp_servers.awb]` |

VS Code Local reads the same `mcp-config.json` as Copilot CLI, so `copilot mcp add` registers `awb` for both Copilot harnesses. Without Copilot CLI, merge the printed entry. Do not use `code --add-mcp`: it writes the VS Code profile `mcp.json`, a location VS Code lists as deprecated and Copilot CLI does not list among its server sources. The commands were checked on 2026-10-15 against `claude mcp add-json --help` in Claude Code 2.1.300, the Codex CLI source ([`mcp_cmd.rs`](https://github.com/openai/codex/blob/0003732489a514748e61a0f76a652ac992a5f4f5/codex-rs/cli/src/mcp_cmd.rs), which writes `$CODEX_HOME/config.toml`), [adding MCP servers to Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers#using-the-copilot-mcp-add-subcommand), and [VS Code's command-line install](https://code.visualstudio.com/docs/agent-customization/mcp-servers).

<!-- dist:exclude -->
[GitHub Copilot compatibility](docs/copilot-compat.md#3-server-configuration) has the details.
<!-- /dist:exclude -->

To replace an existing `awb` registration, for example after moving the interpreter or the skills installation, run `claude mcp remove --scope user awb` before Claude Code's command, which refuses a name that is already registered. `copilot mcp add` also refuses a name that is already registered (exit 1), so run `copilot mcp remove awb` before it (Copilot CLI 1.0.98, observed). `codex mcp add` replaces the existing entry.

The entry's command and server argument are absolute paths to the chosen interpreter and the installed server. Keep that command line stable when a managed allowlist matches command and arguments; policies may also match server names or URLs. The server stays in the shared skills installation. It runs each project's helpers under the interpreter its README's `Project interpreter` line records, else the project's `.venv` or `venv` interpreter, falling back to its own, unless `AWB_PYTHON` is set. Put needed variables directly in the entry's `env` object/table: Copilot user configuration does not support `envFile`, and Copilot CLI passes only `PATH` through by default. With the host's command, pass each variable as `--env KEY=VALUE` before `--` (Copilot CLI, Codex) or in the JSON's `env` (Claude Code). The printed `env` is empty; `--mcp-config` does not copy credentials from the environment. See [VS Code MCP configuration](https://code.visualstudio.com/docs/agents/reference/mcp-configuration), [Claude Code MCP scopes](https://code.claude.com/docs/en/mcp#mcp-installation-scopes), and [Codex MCP](https://developers.openai.com/codex/mcp).

Restart or reconnect the host's `awb` server after registration. When it is available, the project's instruction rule uses MCP tools; the skills retain their CLI commands for hosts without it. Each MCP call passes the absolute project root as `project`, so registration is reusable across projects. `awb-init` offers the printed registration command in one line when the host has no `awb` server registered, with the entry and its destination as the fallback. Copilot CLI requires version 1.0.88 or later for the legacy MCP handshake fallback.

#### VS Code Local and package reviewer

1. In a new Copilot chat, choose **Local** in **Session Target**. A policy can limit available targets, server access, or approval scopes; use the controls the host offers.
2. Open the workbench folder itself as the workspace root. VS Code reads root `AGENTS.md` by default; nested instructions and discovery in parent repositories require separate opt-ins.
3. Start the `awb` server and accept its initial trust prompt. For its write tools, choose **Allow in this Workspace** when offered. Read-only tools need no pre-call approval in Local; `awb/read` declares `openWorldHint`, so result review can still appear.
4. Install the [package reviewer definition](.agents/skills/awb-package/assets/awb-package-reviewer.agent.md) at user level: with **Local** selected, run **Chat: New Custom Agent**, choose the user/profile location, name it `awb-package-reviewer`, and replace the created file's contents with the shipped definition. Local reads user agents from **VS Code profile storage**, whose location the command selects; `~/.copilot/agents/` is the Copilot harness's user directory. Keep this file out of generated workbenches. Update it from the shipped definition on upgrades. See [custom agent locations](https://code.visualstudio.com/docs/agent-customization/custom-agents#custom-agent-file-locations).
5. Confirm that a reviewer subagent receives its four explicit file read/search tools and `awb/read`, successfully calls its review-rules check, and has no edit, terminal, or write tool. The definition uses individual file tools because the broad `read` tool set includes terminal-output readers; see the [VS Code tools reference](https://code.visualstudio.com/docs/agents/reference/tools-reference). VS Code names an MCP tool `<registration key>/<tool>` and silently ignores unknown names, so keep the server registered as `awb`. The definition deliberately uses only `awb/read`: never broaden it to `awb/*`. If the exact tool is unavailable, the review reports failure and completion stays blocked. See [custom agent tools](https://docs.github.com/en/copilot/reference/custom-agents-configuration#tools). Copilot end-to-end behavior remains a field test.

#### Project instructions in AGENTS.md

`awb-init` writes a compact project `AGENTS.md` and copies the conditional procedures into `workbench-guides/`. Keep those guides with the project; the root instructions say when to read each. Scoping is self-contained and requires no external interview skill. Hosts differ in when they read `AGENTS.md`.

- Claude Code reads a project `AGENTS.md` starting with version 2.1.277, and by default only when no `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` exists in the working directory or any directory above it. When one does, Claude Code reads the `CLAUDE.md` files and skips `AGENTS.md`. Your own `~/.claude/CLAUDE.md` does not count for this check. See [How Claude remembers your project](https://code.claude.com/docs/en/memory#agents-md).
- So a workbench created inside a repository or folder that already has a `CLAUDE.md` loses the workbench rules in Claude Code without any warning from the host. `awb-init` reports such a file when it finds one but never edits it. To load the rules, add an import line to that file giving the path from it to the project's `AGENTS.md`, since Claude Code resolves imports relative to the file that contains them: `@AGENTS.md` in a `CLAUDE.md` beside it, `@../AGENTS.md` in `.claude/CLAUDE.md`, and the relative path down into the project in an ancestor directory's `CLAUDE.md`, or set Project instructions in `/config` to `claude-md-and-agents-md`, which reads both files. See [import additional files](https://code.claude.com/docs/en/memory#import-additional-files). On Claude Code versions before 2.1.277, use the import.
- OpenAI Codex reads `AGENTS.md` from its home directory (`~/.codex` by default) and then from each directory from the Git root down to the working directory, preferring an `AGENTS.override.md` in the same directory. See [Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md).

<!-- dist:exclude -->
## Design and validation

The [specification](docs/workbench-spec.md) defines the workflow and acceptance scenarios. The [design notes](docs/workbench-design.md) preserve the decisions behind it. Backend exceptions and exact cache-retention mechanics remain project-specific choices.

Historical validation of the `awb-*` skills, run 2026-10-07 by four isolated agents on separate fixture projects with synthetic data. Each agent read the skills from this repository and followed them as written, playing both the analyst and the agent, so the scoping-interview transcripts are self-simulated and are weak evidence; every other check rests on files the agent produced. Every expected-behavior bullet of acceptance scenarios 1 through 6 passed; none failed. The runs exercised:

- `awb-init` on an empty directory with a business question: one question at a time with a recommended answer, Git initialized without a commit, foundation records created only where their conditions had fired, the host instruction-file check, and the landed-data location question before the first landing.
- Scenario 1 and 2: an expansion from 120 to 900 employees stayed in the same investigation, revised its settings and state, reused the preparation and neutral operations unchanged, and kept superseded findings in history; a pivot to an independent group started a new investigation that inherited method and settings, asked only about the decisions the pivot reopened, and used the earlier findings as method context only.
- Scenario 3: an email-alias correction was assessed locally, implemented through shared preparation and view definitions, documented in the quality record, and flagged two findings with reasons while leaving conclusions, the draft, and the numbered release byte-identical; a second release attempt stopped to ask for a disposition per affected conclusion.
- Scenario 4: one stable package with an asked-for dataset selection, release `001` only on the explicit milestone, a narrative-only revision to the same draft, release `002` after a flag raised since drafting was given a release-with-caveat disposition, manifests recording the producing commit separately from the packaging checkout, and each release copied to the recorded storage location and compared by file list and bytes.
- Scenario 5: a candidate source was assessed only far enough to reject it, the reason recorded, and nothing converted, cached, or exported for it.
- Scenario 6: paged API and extract acquisitions landed with provenance before conversion and copied to the recorded location; a failed partial acquisition stayed unpublished; a conversion failure was retried from landed files without reacquisition; two reader processes queried published Parquet through Git-managed views while a third process prepared a new publication, with no shared DuckDB file.
- `awb-status` after each run: the report shape, the landed-data and release storage lines, the `none chosen` risk path, and the request menu.

The runs also surfaced places where the instructions were silent or conflicted, including the order of verification and revalidation dispositions in `awb-release`, the manifest field names `awb-status` reads, the landing and publication layout, where acquisition and settings code lives, and how an expansion is scoped. Those were corrected in the skills afterwards; the corrected wording has not itself been rerun. No API acquisition, production data conversion, or M365 assembly was performed. The runs used the earlier package format, a `journal.md` and an `executive-summary.md` written in the workbench, with captions drawn into figure images; the `findings.md` and `methodology.md` format that replaced it, the findings check, the slide-outline format, and the chart files were not exercised in those historical runs. Current helper and recipe checks are recorded in the efficiency validation below; real M365 assembly remains untested.

The token-efficiency revision separates conditional procedures, adds a read-only status collector, and narrows revision reads. [Efficiency validation](docs/token-efficiency.md) describes how to compare instruction load and full agent runs without confusing file size with token usage.
<!-- /dist:exclude -->

## Versioning

Releases are Git tags `vX.Y.Z`, each with a zip asset named `analytics-workbench-skills-vX.Y.Z.zip`. Changes are listed in [CHANGELOG.md](CHANGELOG.md).

<!-- dist:exclude -->
`scripts/build-dist.sh` builds the archive as `dist/analytics-workbench-skills.zip`; add the version when attaching it to the release. The archive carries the skills, this README without its design, validation, and build notes, `LICENSE`, and `CHANGELOG.md`; `docs/` and `CONTEXT.md` stay in the repository.
<!-- /dist:exclude -->

## License

MIT. See [LICENSE](LICENSE).
