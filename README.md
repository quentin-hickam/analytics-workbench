# Analytics workbench skills

A portable, agent-agnostic workflow for shared data preparation, distinct investigations, and repeatable delivery packages. Git tracks analytical code; GitHub hosting is not required.

You work with an AI agent that has these skills installed, such as GitHub Copilot in VS Code, Claude Code, or OpenAI Codex. You bring a business question and data. The agent prepares the data, answers your questions with numbers it records and checks, and writes the files a slide deck is built from.

Installing the skills or setting up an agent host? [Install and administer](#install-and-administer) is for you.

## What you get

The end product is a delivery package: a folder of files that a deck is built from. It is not a .pptx. Nothing in the workbench draws slides.

- `findings.md`: the deck outline, slide by slide. After the title slide, each slide has a headline of one sentence and at most 15 words, unless you keep a longer one, up to five bullets, caveats on the slide they qualify, speaker notes, and at most one chart's specification. A headline carries the slide's key number where it has one, and **Open questions** may run past five bullets to list every question the decision needs. The **Answer** slide is the executive summary.
- `charts/`: one data file per chart, holding exactly the rows the chart plots, rounded as the slide shows them and labeled in your audience's terms.
- `datasets/`: any tables you chose to send with the deck, which a **Supporting datasets** slide then describes. You are asked, and none is a fine answer.
- `methodology-note.md`: an optional short methods note for your audience, in their terms: method, sources, definitions, exclusions, and limitations.
- `methodology.md`: the internal methodology reference, the full account of the analysis in the workbench's own names and IDs. The builder may consult it; your audience does not get it.
- `deck-rules.md` and `assembly/m365.md`: builder instructions. The deck rules say what any builder does with the outline and chart files; the assembly file holds the steps for the PowerPoint agent in Microsoft 365 Copilot.
- `START-HERE.md`: which files to send your audience, which to attach to the builder with the one-line prompt to send it, and which stay internal.
- `manifest.json`: the internal record of what the package holds and what produced it.

The deck always has a title slide, the **Answer** slide, at least one finding, **How we know**, and **Limitations and open caveats**. Other slides appear when they apply, such as **Supporting datasets** when you send tables, **Open questions** while questions the decision needs are unanswered or you ask to show one, and **What changed since the last version** after the first release, or when you want them, such as **Implications**. When you agree, **How we know**, **Limitations and open caveats**, **Supporting datasets**, and individual findings can move to an appendix at the end.

To build the deck:

- **With Microsoft 365 Copilot.** In a Copilot app chat, add the PowerPoint agent, attach the files `START-HERE.md` lists, and send its prompt. The agent builds each slide from the outline, draws each chart as an editable chart from its data file, and asks you when something is unclear.
- **By hand.** A person can build the deck by hand from the same files: one slide per outline slide from `findings.md`, and each chart drawn from its file in `charts/`, following `deck-rules.md`. Another tool can work from them the same way.

A Microsoft 365 Copilot license is needed only for the Copilot route.

Each time you mark the package delivered, it becomes the next numbered release: 001, then 002, and so on. A release is frozen: it never changes, and later edits go into the next one. The project keeps it at `deliveries/<investigation>/<package>/released/001/`, and the agent copies it to the folder you name for releases, at `<that folder>/<investigation>/<package>/001/`, and reports the copy's full path. When the agent cannot reach that folder, it tells you what to copy where.

Along the way, answers come in chat, and the project folder keeps the record: for each investigation, its brief, its findings, its question ledger, and a history of decisions, with the saved queries and checked data behind them. A later session picks up from these files.

## Quick-start for analysts

### Before you start

- The skills must be installed in your agent host. If someone else installs your tools, [Install and administer](#install-and-administer) is for them.
- The computer needs Python 3.10 or later; Python 3.12 is the default when installed. Setup stops on an older Python and says so; ask whoever installs your tools for a newer one.
- Git keeps the project's code history on your computer. No GitHub account is needed. Without Git, the work still runs; the agent says so once and makes no commits.
- Open your agent in an empty folder, or in the folder that will hold the project.

### What to say first

Name the skill and give your question. The more you put in the first message, the fewer questions follow:

> Use awb-init to set up this project. The question is why overtime rose in Q3. The operations board decides next month whether to change rostering; they need about 8 slides and a one-page methods note. The data is in `inbox/`. Keep the original files in `/shared/analytics/landed/` and released packages in `/shared/analytics/releases/`.

Useful things to include:

- the business question, and the specific questions under it;
- who will see the result, the decision they own, and about how many slides;
- where the data is: files, a folder, or a web address. Setup and the scoping round bring no data in; the agent downloads data from a web address when you ask it to bring the data in;
- where to keep a copy of the original data, and where to keep released packages;
- whether you want to see the slide headlines before the full draft, as the checkpoint below describes.

Without a question, `awb-init` asks for one in a line. With no question yet, say so, and it sets up the project alone.

### What you will be asked

The agent asks in plain words, with its recommendation and the alternative.

1. **A scoping round.** Right after setup, the decisions only you can make, such as who counts in the population, the period, how a measure is defined, and what result would change the decision. They come up to four at a time, and a vague answer gets a follow-up with a concrete case. The agent looks up facts the data or files can settle. You can put a decision off; it then waits in the question ledger.
2. **Python environment.** Unless you name a Python or the project has an environment of its own, setup creates `.venv` in the project folder, with Python 3.12 when installed, and the packages the helpers need, and says which Python it recorded. You are asked only if that fails, or before installing into a Python outside the project.
3. **Storage locations.** Before the agent first brings in data, where to keep a copy of the original files; before the first release, where to keep released packages. The original data files and releases stay out of the project's Git history, so these folders hold the lasting copies. Folders named in your first message are recorded at setup. The agent copies to a full path or one starting with `~`, `./`, or `../`; for anything else, such as a web address, it tells you what to copy where. Answer "none", and the agent warns that this computer holds the only copy.
4. **Data and analysis choices.** You decide whether identical rows shared by files or sheets are copies or separate records, unless the source says they are re-extracts; when cleaning, what a placeholder means, the canonical label, and which duplicate wins; and any threshold, minimum, or exclusion your brief leaves open, proposed before the agent sees which rows lead.
5. **Audience and length**, when you first ask for a package, unless you said them earlier: who will see the deck, what they already know, the decision they own, their terms, and any length you want. The agent also asks which tables to send with the deck and, when you mention a methods note, whether your audience needs one; otherwise the draft's report offers one. A methods note length, such as "one page", is recorded in the brief as a word count, about 500 to a page. The package check reports a note more than 10% over it, and the agent shortens it or tells you its length; with no length recorded, the note runs a page or two.
6. **The headline checkpoint.** You approve or reorder the slide headlines, in one of two modes. In **preview-and-wait** you see the title and every headline first, and the full slides follow your approval. In **draft-then-review** the agent writes the whole draft, then shows its headlines, marked as awaiting your approval. A request that names a mode gets it, and one that gives the storyline or asks for the full draft gets draft-then-review; otherwise the agent uses the mode you chose before, or preview-and-wait. With the headlines it reports the slide count against your length and proposes what could move to the appendix. Before shortening a headline over 15 words that you wrote or approved, the agent asks: you choose the shorter wording or keep yours, and your reason is recorded. A choice still open that would change the deck, such as wording for your audience you have not approved, is asked with the headlines, and the full slides wait for your answer in either mode.
7. **Review problems.** A fresh reviewer, told only to read, checks each draft against your brief, the evidence, and your review rules; in a host without reviewers, the agent reviews its own draft. The first review reads the whole draft, and each later one reads only what changed since. A conflict between two rules comes to you, as can a warning you may accept with a reason. When a second review in one request still finds problems, the agent starts no third review. It makes small repairs that change no number, no finding beyond narrowing to its evidence, and no wording you wrote or approved, and lists them in one note for the next scoped review. You decide the other problems from its recommended fixes; any acceptances are recorded before repairs with your answer. A break of a rule kept as an error is always fixed. The draft is stable once the package check passes and the last review passed with nothing changed since; a release then needs no new review.
8. **Release questions**, when you mark the package delivered: whether a draft label left in the deck's title or headings, such as DRAFT, should stay; whether to accept any problem a review raises, with your reason; whether to release with a workbench helper or package format that changed since it was installed; and, when a repair was needed, the changed slides before the release, unless you say to release without seeing them.

A finding is flagged when a later correction to the shared data may affect it. A rerun or a changed input flags nothing; `awb-status` reports it and offers to revise the draft. You are asked about a flagged finding only when the draft shows it, while drafting or at release: recheck it, which pauses the release until the analysis is rerun; leave it out; or release it with its caveat stated.

### The usual requests

Naming the skill tells the host which instructions to follow. Follow-ups such as "go ahead" need no skill name.

1. **Set up.** "Use awb-init to set up this project. The question is …" Setup hands your question straight to `awb-scope`, which asks the scoping round.
2. **Scope.** Bring later questions, open questions you can now answer, and changes of scope: "Use awb-scope to start an investigation into why sick leave rose in Q4." or "Use awb-scope — let's work through the open questions."
3. **Bring the data in.** "Bring in the files in `inbox/`." or "Download the data from the address I gave." The agent keeps the original files unchanged, records where they came from, and converts them into checked tables.
4. **Clean and explore, both optional.** "Use awb-clean to clean the orders data." checks one dataset for errors such as duplicate rows, placeholder values, and inconsistent labels, decides with you where a fix would change meaning, and corrects the shared data once, so every investigation gets the fix. "Use awb-explore to explore the shifts data." profiles one dataset within your question's scope and records what it learned and the questions it raises, but no findings. Cleaning helps before you analyze a dataset nobody has checked, or when a result looks wrong because of the data; exploring helps when the data is new to you or the question is open-ended. The agent may fold these checks into bringing the data in or into the analysis instead of running them as steps, so ask "Was the orders data cleaned?" when you want to know.
5. **Analyze.** No skill name is needed: "Answer question 2." or "Go ahead with the analysis." The agent computes each answer with saved queries, checks it, and records it as a provisional finding until you approve its wording. An untested explanation comes back as a question, not an answer.
6. **Status.** "Use awb-status — where are we?" One screen: each of your questions with its findings, every open caveat, anything at risk, and up to five requests you can type next. The report changes nothing; other requests in the same message, such as "where are we? Then reword question 3.", are carried out after it.
7. **Package.** "Use awb-package to prepare a draft for the active investigation." It writes the one working draft, and later requests revise it. Corrections you make while reviewing it go through the same skill.
8. **Release.** "Use awb-release — mark the package delivered." It freezes the draft as the next numbered release and copies it to your release folder. If you ask for a change in the same message, you see the changed slides first, unless you say to release without seeing them. Its report lists every caveat the release still carries.

`awb-status` suggests clean and explore when they fit. When only one or two of your questions stay open, or you want to widen the inquiry, ask "Use awb-brainstorm — what else should we ask?" It proposes new questions from those asked and answered, the findings, and the data; you keep, park, or decline each.

### How many exchanges to expect

Six simulated first-time runs each took five questions on a public dataset from an empty folder to a first release. Counting each message the user sent that the agent answered, the runs took 6 to 11 exchanges, plus one closing message accepting the release. Each run took one to two and a quarter hours, most of it the agent's own work; the longest replies, such as writing the full draft, took up to about half an hour. Most of those users gave their questions, audience, length, and storage folders in the first message. The runs came before later changes, such as draft-then-review, so take the range as a guide, not a promise.

<!-- dist:exclude -->
The [UX simulation synthesis](docs/ux-simulation-2026-10-15/README.md) has each run's counts and transcript.
<!-- /dist:exclude -->

### Words you will meet

- **Finding**: a checked result the investigation records, with a status and how strongly the evidence supports it: descriptive, association, or causal. A slide never words a finding more strongly than that.
- **Provisional**: a finding not yet promoted to supported. The agent promotes it once its checks are recorded and you have approved its headline or wording, such as at the headline checkpoint; until then, a question it answers counts as provisional, not answered.
- **Question ledger**: the investigation's list of every question it has raised, answered or not, with who can answer each: you, a stakeholder, or the data. Your own questions come first, and questions raised along the way sit under the one they serve. You can read it in the investigation's `questions.md`; ask the agent to change it rather than editing that file, which is rewritten from its record. A question about the data is answered only by a recorded result.
- **Review rule**: a numbered rule, such as `R-periods-001`, recorded from a correction you make to a draft that later drafts could repeat, once you agree to keep it. Every later review of a draft checks it, or of one package's drafts when you keep it for that package. A one-off edit, such as a preferred wording on one slide, is not a rule. The rules are kept in `foundation/review-rules.md`.
- **Release**: a frozen, numbered copy of the package, made only when you mark it delivered.

### Good to know

- A turn that changed the project's records ends with one plain line: what changed for your questions, if anything, and the next step.
- A commit saves the project's code and records, such as its queries and findings, as a point in its history on this computer that you can go back to. It uploads nothing. Data files and packages stay out of it, but results and the example values exploration and cleaning record are saved. The agent commits only when you ask; say "commit as you go" to switch.
- Your host may ask you to approve a command or tool call; that prompt is the host's, not the workbench's. Setup may suggest, in one line, registering the workbench's `awb` tool server with your host, which cuts those approvals; the work runs without it.
- The checks have limits. The package check confirms that every number in the deck outline, the methodology reference, and any methods note traces to a recorded result or is listed, with its reason, as coming from elsewhere, such as a fact you gave or a figure from an earlier release. The reviewer reads the wording against your brief, your review rules, and the evidence. Neither redoes the analysis, so read the headlines and caveats yourself.

## Included skills

Every skill name carries the `awb-` prefix, so typing `awb-` in a host that lists skills as commands shows every workbench action.

- [awb-init](.agents/skills/awb-init/SKILL.md): set up a project for a first business question, or repair it after installing newer skills. Its [project AGENTS.md template](.agents/skills/awb-init/assets/workbench/AGENTS.md) governs everyday analysis and recordkeeping.
- [awb-scope](.agents/skills/awb-scope/SKILL.md): start an investigation, interview you about its question and context, or change its scope; every open question goes into the question ledger.
- [awb-brainstorm](.agents/skills/awb-brainstorm/SKILL.md): propose new questions from those asked and answered, the findings, and the cataloged data.
- [awb-clean](.agents/skills/awb-clean/SKILL.md): find and correct errors in one shared dataset, deciding with you where a fix changes meaning, and flag the findings a correction affects.
- [awb-explore](.agents/skills/awb-explore/SKILL.md): profile one dataset within the active investigation's scope and record what was learned, without findings.
- [awb-status](.agents/skills/awb-status/SKILL.md): read-only report of where the project stands and the requests that fit right now.
- [awb-package](.agents/skills/awb-package/SKILL.md): create or revise a delivery package's working draft.
- [awb-release](.agents/skills/awb-release/SKILL.md): freeze the draft as a numbered release when you mark it delivered, and copy it to the recorded storage location.

## Install and administer

This section is for whoever installs the skills and sets up the agent host. An analyst working in an installed workbench can skip it.

### Requirements

- Python 3.10 or later for every helper and script (3.11 or later, or `tomli`, to read TOML settings). Python 3.12 is the default when installed: setup builds a new project's `.venv` with it, and the MCP server registration below runs under it. The project's interpreter also needs pandas and `duckdb`, which `awb-init`'s installer declares and checks; result validation was tested with pandas 2.2. The status collector and the cleaning record script need only the standard library.
<!-- dist:exclude -->
- pytest is needed only to run this repository's own tests under `tests/`; they exercise the shipped helper files and are not part of the distributed archive. The reference deck renderer in `tests/`, which proves the deck contract can be built from without Microsoft 365, also needs python-pptx; its tests skip without it.
<!-- /dist:exclude -->

### Install

Download `analytics-workbench-skills-vX.Y.Z.zip` from the repository's GitHub releases and unzip it anywhere. It unpacks to one folder, `analytics-workbench-skills/`, holding the eight `awb-*` skill folders beside this README, `LICENSE`, and `CHANGELOG.md`. Install those folders in `~/.agents/skills/`, replacing earlier copies, and delete any `awb-update` folder an earlier release left. Do not unzip the archive into the skills directory itself: a host looks for `<skills directory>/<skill name>/SKILL.md`, and the extra folder level hides the skills. In a clone of this repository, the same folders are under `.agents/skills/`. Projects need no local copies.

After installing newer skills, bring each existing workbench up to date:

> Use awb-init to repair this workbench.

Repair installs missing helpers and guides and replaces only the unmodified copies its checksum receipt recognizes; it reports customized copies for you to decide, removes retired files only when you ask, and reconciles the project's `AGENTS.md` and `README.md` with the current templates. It asks before adding a missing `.gitignore` rule, and updates each investigation's `run.py`, rerunning any result whose code changes.

#### Shared skills

- VS Code Copilot and OpenAI Codex read `~/.agents/skills/`; Codex also scans `.agents/skills/` from the working directory up to the repository root. See [VS Code skills](https://code.visualstudio.com/docs/agent-customization/agent-skills) and [Codex agent skills](https://developers.openai.com/codex/skills).
- For Claude Code, link each installed `awb-*` folder into `~/.claude/skills/` with a symlink to its absolute path in `~/.agents/skills/`, keeping unrelated skills and replacing earlier `awb-*` copies once local customizations are kept. See [Claude Code skills](https://code.claude.com/docs/en/skills).
- Without symlinks, copy the folders to both locations and upgrade both together. VS Code prefers a loaded copy in `~/.agents/skills/` over one of the same name in `~/.claude/skills/`.
- Other hosts: each `awb-*` folder is a `SKILL.md` with `name` and `description` frontmatter under the agent skills convention; check the host's documentation for its user-level skills directory.

#### MCP server

After installing the skills, run this with Python 3.12 when it is installed (`python3.12`, or `py -3.12` on Windows, in place of `python3`), else a stable Python 3.10+ interpreter, outside any project virtual environment, replacing `<host>` with `copilot`, `claude`, or `codex`:

```sh
python3 ~/.agents/skills/awb-init/scripts/install_helpers.py --mcp-config <host>
```

It prints the `awb` entry on stdout and, on stderr, the host's registration command for a POSIX shell such as bash or zsh, then the file to merge the entry into as the fallback, with a warning first when the interpreter is older than 3.10 or inside a virtual environment. It runs nothing and writes nothing.

Prefer the host's command: it adds the entry to the host's user-level configuration and keeps the rest, which matters most for Claude Code, since it rewrites `~/.claude.json` while it runs. In PowerShell or cmd, or without the host's command, merge the printed entry into the existing file, keeping other servers and settings; for Claude Code, close every session first.

| Host | Registration command | File | Printed format |
| --- | --- | --- | --- |
| VS Code Copilot | `copilot mcp add awb -- <python> <server>` (Copilot CLI) | `$COPILOT_HOME/mcp-config.json`, falling back to `~/.copilot/mcp-config.json` | JSON, top-level `mcpServers.awb`, `type: "stdio"` |
| Claude Code | `claude mcp add-json --scope user awb '<entry>'` | `$CLAUDE_CONFIG_DIR/.claude.json`, falling back to `~/.claude.json` | JSON, top-level `mcpServers.awb` (user scope, outside `projects`) |
| Codex | `codex mcp add awb -- <python> <server>` | `$CODEX_HOME/config.toml`, falling back to `~/.codex/config.toml` | TOML, `[mcp_servers.awb]` |

VS Code Local reads the same `mcp-config.json` as Copilot CLI, so `copilot mcp add` registers `awb` for both; without Copilot CLI, merge the printed entry. Do not use `code --add-mcp`: it writes the VS Code profile `mcp.json`, which VS Code lists as deprecated and Copilot CLI does not read. Sources, checked 2026-10-15: `claude mcp add-json --help` in Claude Code 2.1.300, the Codex CLI source ([`mcp_cmd.rs`](https://github.com/openai/codex/blob/0003732489a514748e61a0f76a652ac992a5f4f5/codex-rs/cli/src/mcp_cmd.rs)), [adding MCP servers to Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers#using-the-copilot-mcp-add-subcommand), and [VS Code's command-line install](https://code.visualstudio.com/docs/agent-customization/mcp-servers).

<!-- dist:exclude -->
[GitHub Copilot compatibility](docs/copilot-compat.md#3-server-configuration) has the details.
<!-- /dist:exclude -->

To replace a registration, for example after moving the interpreter or the skills, run `claude mcp remove --scope user awb` or `copilot mcp remove awb` first, since both hosts refuse a name already registered (Copilot CLI 1.0.98, observed); `codex mcp add` replaces the entry.

The entry runs the chosen interpreter and the installed server by absolute path; keep that command line stable where a managed allowlist matches it. The server runs each project's helpers under the interpreter its README's `Project interpreter` line records, else the project's `.venv` or `venv`, else its own, unless `AWB_PYTHON` is set. Put needed variables in the entry's `env`, passed as `--env KEY=VALUE` before `--` to Copilot CLI and Codex: Copilot user configuration does not support `envFile`, and Copilot CLI passes only `PATH` through by default. The printed `env` is empty and copies no credentials. See [VS Code MCP configuration](https://code.visualstudio.com/docs/agents/reference/mcp-configuration), [Claude Code MCP scopes](https://code.claude.com/docs/en/mcp#mcp-installation-scopes), and [Codex MCP](https://developers.openai.com/codex/mcp).

Restart or reconnect the host's `awb` server after registration. The skills then use its tools, passing the absolute project root on every call, so one registration serves every project; without it they run the same helpers as terminal commands. Copilot CLI needs version 1.0.88 or later for the legacy MCP handshake fallback.

#### VS Code Local and package reviewer

1. In a new Copilot chat, choose **Local** in **Session Target**. A policy can limit targets, server access, or approval scopes; use the controls the host offers.
2. Open the workbench folder itself as the workspace root: VS Code reads root `AGENTS.md` by default, and nested or parent instructions need separate opt-ins.
3. Start the `awb` server and accept its trust prompt. For its write tools, choose **Allow in this Workspace** when offered. Read-only tools need no approval in Local, though `awb/read` declares `openWorldHint`, so result review can still appear.
4. Install the [package reviewer definition](.agents/skills/awb-package/assets/awb-package-reviewer.agent.md) at user level: with **Local** selected, run **Chat: New Custom Agent**, choose the user/profile location, name it `awb-package-reviewer`, and replace the created file's contents with the shipped definition. Local reads user agents from VS Code profile storage, not `~/.copilot/agents/`. Keep it out of generated workbenches and update it on upgrades. See [custom agent locations](https://code.visualstudio.com/docs/agent-customization/custom-agents#custom-agent-file-locations).
5. Confirm that a reviewer subagent gets its four file read/search tools and `awb/read`, calls its review-rules check, and has no edit, terminal, or write tool. VS Code names an MCP tool `<registration key>/<tool>` and silently ignores unknown names, so keep the server registered as `awb`, and never broaden the definition to `awb/*`; without `awb/read`, the review reports failure and the draft cannot finish. See the [VS Code tools reference](https://code.visualstudio.com/docs/agents/reference/tools-reference) and [custom agent tools](https://docs.github.com/en/copilot/reference/custom-agents-configuration#tools). Copilot end-to-end behavior remains a field test.

#### Cost per request

Every tool call sends the whole chat to the model again, so a request costs more with each tool call and as the chat grows.

- Start a new chat when the task changes.
- Everyday questions rarely need the largest model or the highest reasoning effort; keep those for scoping and packaging. Findings still come only from the investigation's `run.py`, whichever model runs it.

#### Project instructions in AGENTS.md

`awb-init` writes a compact project `AGENTS.md` and copies the conditional procedures into `workbench-guides/`, which stay with the project. Hosts differ in when they read `AGENTS.md`.

- Claude Code reads a project `AGENTS.md` from version 2.1.277, and by default only when no `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` exists in the working directory or above it; your own `~/.claude/CLAUDE.md` does not count. See [How Claude remembers your project](https://code.claude.com/docs/en/memory#agents-md).
- So a workbench inside a folder with a `CLAUDE.md` loses the workbench rules in Claude Code without warning. `awb-init` reports such a file but never edits it. Add an import of the project's `AGENTS.md` to it, relative to that file (`@AGENTS.md` beside it, `@../AGENTS.md` in `.claude/CLAUDE.md`), or set Project instructions in `/config` to `claude-md-and-agents-md`. Before 2.1.277, use the import. See [import additional files](https://code.claude.com/docs/en/memory#import-additional-files).
- OpenAI Codex reads `AGENTS.md` from its home directory (`~/.codex` by default), then from each directory from the Git root down to the working directory, preferring an `AGENTS.override.md`. See [Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md).

## How it works

`awb-init` installs the helpers under `src/` and the guides under `workbench-guides/`, records the Python that runs them on the project README's `Project interpreter` line, and keeps a checksum receipt, `.awb-receipt.json`, so a repair replaces only unmodified copies. `python3 src/awb.py --help` lists the helper commands.

Data is landed unchanged under `data/raw/`, published as validated Parquet, and read through shared DuckDB views in `foundation/views/`, so every investigation sees the same corrections. Each investigation's `run.py` runs its saved queries, validates each result, and records its evidence; only such a result can become a finding. Third-party documentation a source assessment relies on is kept under `foundation/references/<source-id>/`.

`awb-package` exports each chart file from a recorded result, has a fresh reviewer check the narratives, and ends with `check-draft`, which checks the outline's slide rules, every number against the recorded results, and each chart file, and writes `START-HERE.md`. The builder gets the outline, the methodology reference, the chart files, the deck rules, and the assembly file; the chosen datasets and any methods note travel beside the deck and are not attached. `awb-release` copies the draft to `deliveries/<investigation>/<package>/released/<n>/` and to the release storage folder. `data/raw/` and `deliveries/` are excluded from Git, which is why the agent asks where to keep their copies.

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
