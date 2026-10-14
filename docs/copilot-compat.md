# GitHub Copilot compatibility

Researched 2026-10-14, against VS Code 1.142 and the MCP specification revision `2026-07-28`. No Copilot host was run. Every claim below comes from primary sources: VS Code and GitHub documentation and release notes, the `microsoft/vscode` and `github/copilot-cli` repositories, and the MCP specification. Two independent research passes, by Claude Opus and by Codex, were cross-checked. The claims the design depends on were then re-read at the source. **Documented** means a primary source states the claim. **Code** means it was read from public source on `main` and is not a release guarantee. **Inferred** means neither of those settles it. **Reported** means it rests on an issue's reports and maintainer replies, not on documentation.

## Target tiers

1. **Primary: the VS Code Local harness**, the Copilot Chat agent mode built into VS Code. Design decisions are made for this host.
2. **Secondary: Claude Code and Codex.** They keep working through the same skills and the same MCP server.
3. **Tertiary: Copilot CLI, the Copilot cloud agent, and VS Code's Copilot harness.** Nothing depends on them. They are noted where they differ.

## Design decisions this research settles

| Decision | Basis |
| --- | --- |
| Helpers are exposed as MCP tools over stdio. The CLI stays as a fallback and for tests. | Hosts can confirm every terminal command. MCP tools have their own approval scopes in VS Code (below). |
| Every read-only tool carries `readOnlyHint: true`. No tool both reads and writes. | VS Code Local runs read-only tools without confirmation. |
| Write tools are few and coarse. | Each tool asks on first use unless the user trusts the whole server, and in the Copilot harness an approval lasts only one session. |
| The server speaks the legacy `2025-11-25` protocol, and answers any other method, including `server/discover`, with an immediate `-32601` error. | VS Code Local negotiates `2025-11-25`. The spec requires dual-era clients to fall back to `initialize` on any non-modern error, but Copilot CLI builds before 1.0.88 treated some `server/discover` errors as fatal ([§5](#5-protocol)). |
| The project root comes from an explicit argument, then from MCP roots, then from the working directory. It is validated as a workbench before anything is written. | Roots are deprecated in the spec. A user-level server's working directory isn't documented, and a plugin server's is its install folder. |
| Tool results are bounded text, with no `structuredContent`. | VS Code Local passes `structuredContent` to the model *instead of* the text when both are present. Copilot CLI moves a result over 20 KiB to a file and shows the model a preview. |
| Skills install once, to `~/.agents/skills`, which VS Code and Codex read. For Claude Code, each `~/.claude/skills/awb-*` entry is a symlink to that copy. | VS Code also reads `~/.claude/skills`, and loads one skill per name, from `~/.agents/skills` first, so a separate copy there would be shadowed or go stale ([§7](#7-skills)). |
| The package reviewer is a custom agent whose `tools` list holds only read tools and the server's read-only tools. | VS Code custom agents restrict tools by `server/tool` name, and a subagent run under a named custom agent takes that agent's tools. |

## 1. Harnesses

VS Code now runs agent sessions in two Copilot harnesses with different engines:

- **Local**, the original VS Code agent. Native MCP integration, approvals in `languageModelToolsConfirmationService`.
- **Copilot**, which runs the Copilot SDK in VS Code's Agent Host process. The SDK "exposes the same engine behind Copilot CLI" ([copilot-sdk](https://github.com/github/copilot-sdk)), though VS Code notes a shared runtime does not imply identical tools, permissions, or customizations (documented, [agent harnesses](https://code.visualstudio.com/docs/agents/run/agent-harnesses)).

From 1.142, Copilot is being rolled out progressively as the default harness for new sessions (documented, [1.142](https://code.visualstudio.com/updates/v1_142)). The rollout has three consequences:
- When an organization configures a nonempty managed `permissions` object, or sets `sandbox.enabled` to `true`, VS Code requires the Copilot harness for full chat sessions, and opening an existing, unarchived Local chat moves it to Copilot. An empty `permissions` object or a legacy policy alone does not trigger this.
- Administrators can keep Local with `vscode.temporaryDefaultToLocalHarness`, which also overrides that routing.
- The `ChatToolsAutoApprove` policy does not trigger the routing by itself ([manage AI settings](https://code.visualstudio.com/docs/enterprise/manage-ai-settings)).

A user picks the harness from the **Session Target** control in a new chat, which lists only the targets whose requirements are met ([agent harnesses](https://code.visualstudio.com/docs/agents/run/agent-harnesses)). The docs don't say whether Local will be retired.

**Consequence:** the package targets Local, and must not break in the Copilot harness, because users may land there without choosing it. The install guide tells users to pick Local in the Session Target control.

## 2. Tool approval

**VS Code Local**:
- **Read-only tools.** A tool marked `readOnlyHint` runs without confirmation, and every other tool shows the confirmation dialog (documented, [MCP developer guide](https://code.visualstudio.com/api/extension-guides/ai/mcp)).
- **Approval scopes.** A confirmation can approve once, for the session, for the workspace, or for all future calls. **Chat: Manage Tool Approval** can trust every tool of one server (documented, [approvals](https://code.visualstudio.com/docs/agents/run/approvals)).
- **Sandboxed servers.** A stdio server with `"sandboxEnabled": true` (macOS and Linux only) has its tool confirmations auto-approved, and can write only to the paths its `sandbox.filesystem.allowWrite` lists (documented, [configuration reference](https://code.visualstudio.com/docs/agents/reference/mcp-configuration); code). Only the VS Code-format files (`.vscode/mcp.json` and the profile `mcp.json`) support per-server sandboxing ([§3](#3-server-configuration)), so the user-level install below runs unsandboxed, and its write tools ask under the approval scopes above.

Policies that change this ([manage AI settings](https://code.visualstudio.com/docs/enterprise/manage-ai-settings), [policy reference](https://code.visualstudio.com/docs/enterprise/policies)):

| Policy | Effect on MCP tools |
| --- | --- |
| `ChatToolsTerminalEnableAutoApprove = false` | None. It governs terminal commands only, and the MCP approval path never reads it (code). |
| `ChatToolsAutoApprove = false` | Confirmations offer only one-time approval, and saved approvals aren't applied (documented). Read-only tools still skip confirmation (code). |
| `ChatToolsEligibleForAutoApproval` | A tool listed as `false` always asks and never offers auto-approval (documented). |
| `permissions.disableBypassPermissionsMode = "disable"` | Removes **Allow all**. A nonempty `permissions` object also routes sessions to the Copilot harness (documented). |

**Copilot harness**:
- **Session-only approvals.** "Allow in this Session" is the only saved scope found, in `agentHost/node/sessionPermissions.ts` (code).
- **`readOnlyHint`.** Its auto-approval path never reads annotations, so read-only tools probably still ask once per session (inferred).
- **Read-only Ask agent.** The built-in read-only **Ask** agent excludes MCP tools even when they are marked read-only ([vscode#340866](https://github.com/microsoft/vscode/pull/340866), code).
- **Known bug.** Saved approvals can override `ChatToolsEligibleForAutoApproval` ([vscode#337540](https://github.com/microsoft/vscode/issues/337540), open).

**Copilot CLI** (tertiary):
- **Every call needs permission.** "All MCP tool invocations require explicit permission", read-only ones included ([CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)).
- **Whole-server grants.** `--allow-tool='<server>'` allows a whole server for the session ([CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)), and `permissions-config.json` saves a whole-server approval per location with `"toolName": null` (documented, [configuration directory reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference)).

## 3. Server configuration

VS Code lists four places to configure a server ([MCP servers](https://code.visualstudio.com/docs/agent-customization/mcp-servers)):

| Scope | File | Top-level key | Status |
| --- | --- | --- | --- |
| User, portable | `$COPILOT_HOME/mcp-config.json`, else `~/.copilot/mcp-config.json` | `mcpServers` | Preferred for personal servers used across workspaces |
| Workspace, portable | `.mcp.json` at the workspace root | `mcpServers` | Preferred for shared servers |
| Workspace | `.vscode/mcp.json` | `servers` | Listed as deprecated; kept for VS Code-only features such as `${input:…}` |
| User profile | profile `mcp.json` | `servers` | Listed as deprecated |

- **Copilot harness.** It reads `.mcp.json` and the user-level `mcp-config.json` above directly. VS Code forwards eligible servers from other sources, except those that need interactive input (documented, same page).
- **Trust.** Workspace servers inherit Workspace Trust. A server from any other source shows a trust dialog when it first starts and whenever its configuration changes (documented, same page).
- **Stdio keys:** `type: "stdio"`, `command`, `args` and `env` in every format, and `cwd` in every format but `.mcp.json`. `envFile`, `${input:…}` variables, and `sandboxEnabled` with `sandbox` ([§2](#2-tool-approval)) work only in the VS Code-format files, not in the user-level `mcp-config.json` (documented, [configuration reference](https://code.visualstudio.com/docs/agents/reference/mcp-configuration)).
- **Copilot CLI** passes only `PATH` to a server, so every other variable must be set in its configuration (documented, [adding MCP servers](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers)).
- **Managed allowlists** match a local server by its exact command and arguments ([managed settings](https://docs.github.com/en/copilot/reference/enterprise-administrators/enterprise-managed-settings#allowedmcpservers)). An install guide should therefore produce one stable command line.

**Install target:** one user-level entry in `$COPILOT_HOME/mcp-config.json`, or `~/.copilot/mcp-config.json` when `COPILOT_HOME` is unset, which serves every workspace and both Copilot harnesses. Claude Code and Codex get their own user-level entries. The install guide requires Copilot CLI 1.0.88 or later ([§5](#5-protocol)). The entry sets variables in `env`, since `envFile` doesn't work there.

**Known limit:** the user-level entry can't be sandboxed, so VS Code Local doesn't auto-approve its write tools or restrict its writes. A sandboxed entry would need the VS Code format, which the Copilot harness gets only through forwarding, and a write list holding each project's folder, which a server shared across workspaces doesn't have.

## 4. Project root

- **VS Code Local** gives servers the workspace root folders as MCP roots (documented, [MCP developer guide](https://code.visualstudio.com/api/extension-guides/ai/mcp)), and sends `notifications/roots/list_changed` (code).
- **Working directory.** A stdio server's `cwd` defaults to the workspace folder "when run in a workspace". For a user-level server, the code passes no workspace folder, so the process probably runs in VS Code's own directory (inferred).
- **Roots are deprecated** as of `2026-07-28`, with the migration path "Pass directories or files via tool parameters, resource URIs, or server configuration". Removal can come no earlier than the first revision on or after 2027-07-28 ([deprecated features](https://modelcontextprotocol.io/specification/2026-07-28/deprecated)).
- **Copilot CLI** advertises no roots, doesn't expand `${workspaceFolder}`, and starts plugin servers in the plugin's install folder ([copilot-cli#4234](https://github.com/github/copilot-cli/issues/4234), v1.0.73).

**Resolution order:**
1. An explicit `project` argument on every tool.
2. The single MCP root.
3. The working directory.

Each candidate is accepted only if it holds `src/awb.py`, except for the tool that initializes a workbench. Several roots without an argument is an error that names them.

## 5. Protocol

- **VS Code Local** advertises `LATEST_PROTOCOL_VERSION = "2025-11-25"` (code).
- **Revision `2026-07-28`** has no handshake: every request carries its version in `_meta`, and servers must implement `server/discover`. A dual-era client probes with `server/discover` on stdio, and falls back to `initialize` on any error that is not a recognized modern error ([versioning](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning)).
- **Copilot CLI** is dual-era: it probes with `server/discover`, then falls back to `initialize` (reported). Some builds broke that fallback (reported):
  - 1.0.79-1 aborted initialization when a server answered the probe with `-32602`. A bot closed the issue as resolved in 1.0.88 ([copilot-cli#4370](https://github.com/github/copilot-cli/issues/4370)).
  - 1.0.85 and 1.0.86 recorded a `-32601` answer as a fatal server failure over HTTP, although the follow-up `initialize` succeeded. Reporters confirmed the fix in 1.0.87 ([copilot-cli#4870](https://github.com/github/copilot-cli/issues/4870)).

  The 1.0.88 minimum in the install guide follows from these two issues (inferred). The Copilot harness runs the same engine ([§1](#1-harnesses)), so a similar regression could reach it.

**Implementation scope:** `initialize`, `notifications/initialized`, `ping`, `tools/list` and `tools/call`, with an immediate JSON-RPC error for every other request, so dual-era clients fall back rather than hang. Supporting the modern era is a later hedge, not a gate.

## 6. Tools and results

- **Name length.** VS Code exposes MCP tools under a collision-resolved `mcp_` server prefix, capped at 64 characters in total (code). The CLI uses `serverName-toolName`, also capped at 64 (documented, [CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)). Short names fit both.
- **Tool cap.** VS Code allows at most 128 enabled tools per request, counting every source ([tools](https://code.visualstudio.com/docs/agents/run/tools)). A small tool set leaves room for the user's other servers.
- **Structured content.** VS Code Local appends `structuredContent` as JSON and uses it in place of the text items for the model (code). `outputSchema` enforcement by either host is not established.
- **Large output.** From 1.110, "Large tool output is written to disk instead of stuffed into context" (documented, [1.110 changelog](https://github.blog/changelog/2026-03-06-github-copilot-in-visual-studio-code-v1-110-february-release/)). The changelog doesn't say which tools this covers, so whether MCP results get it is unknown (inferred). Copilot CLI saves output from any tool, MCP tools included, to a temporary file above 20 KiB (`COPILOT_LARGE_OUTPUT_THRESHOLD_BYTES`), and gives the model the path and a preview (documented, [context management](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/context-management)).

## 7. Skills

| Surface | Project directories | User directories |
| --- | --- | --- |
| VS Code (both harnesses) | `.github/skills`, `.claude/skills`, `.agents/skills` | `~/.copilot/skills`, `~/.claude/skills`, `~/.agents/skills` |
| Copilot CLI | `.github/skills`, `.agents/skills`, `.claude/skills` | `~/.copilot/skills`, `~/.agents/skills` (no longer `~/.claude/skills`) |

Sources: [VS Code skills](https://code.visualstudio.com/docs/agent-customization/agent-skills), [GitHub skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills).

- **Same name in two locations.** VS Code Local searches `.agents/skills`, `.github/skills`, `.claude/skills`, then `~/.agents/skills`, `~/.copilot/skills`, `~/.claude/skills`, and skips any later skill whose name it has already loaded, so each name appears once ([`promptFileLocations.ts`](https://github.com/microsoft/vscode/blob/a4d6dc1d9dc15c3c92f26e94c025a93699334fa5/src/vs/workbench/contrib/chat/common/promptSyntax/config/promptFileLocations.ts#L172-L179), [`promptsServiceImpl.ts`](https://github.com/microsoft/vscode/blob/a4d6dc1d9dc15c3c92f26e94c025a93699334fa5/src/vs/workbench/contrib/chat/common/promptSyntax/service/promptsServiceImpl.ts#L1510-L1560); code). A copy in `~/.claude/skills` is therefore never what VS Code runs, and updating only that copy leaves VS Code on the old one. The Copilot harness's handling of duplicates is not established.
- **Symlinks.** A Claude Code skill entry can be a symlink to a directory elsewhere, and Claude Code loads it once (documented, [Claude Code skills](https://code.claude.com/docs/en/skills)). Per-skill links leave the user's other `~/.claude/skills` entries alone. Where symlinks aren't available, the guide copies to both locations and updates both together.
- **Enabled by default.** Skills are generally available and on by default from VS Code 1.109 (`chat.useAgentSkills`) (documented, [1.109](https://code.visualstudio.com/updates/v1_109)).
- **Names.** A skill's name must match its folder, use lowercase letters, digits and hyphens, and fit in 64 characters. "Names with invalid characters cause the skill to silently fail to load." Descriptions fit in 1,024 characters (documented, VS Code skills). Every `awb-*` name complies.
- **Frontmatter.** VS Code honors `name`, `description`, `argument-hint`, `user-invocable` (default true) and `disable-model-invocation` (default false). It does not list `allowed-tools`. Skills appear as `/name` commands (documented, VS Code skills).
- **Bundled files.** A skill can link files relative to its folder, and the agent runs bundled scripts through the terminal tool and its approval controls (documented, VS Code skills). That is why helper execution goes through MCP.

## 8. Instructions

- **Root `AGENTS.md`.** VS Code Local reads it when `chat.useAgentsMdFile` is on, which is the default. Nested `AGENTS.md` files need the experimental `chat.useNestedAgentsMdFiles`, which is off by default ([custom instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions)). The workbench's `AGENTS.md` therefore loads only when the workbench folder is the workspace root.
- **Combining with other instruction files.** Instruction sources are additive, with no general precedence, so a project with `.github/copilot-instructions.md` gets both. Conflicts between them are not resolved by order (documented, same page).

## 9. Subagents and the reviewer

- **Subagents.** VS Code Local starts subagents with `runSubagent`. A subagent inherits the main agent's instructions and tools "unless you specify a custom agent" ([subagents](https://code.visualstudio.com/docs/agents/run/subagents)). It does not inherit the conversation.
- **Custom agent locations.** Custom agents live in `.github/agents` or `.claude/agents` in the workspace, or at user level: in profile storage for Local, and in `~/.copilot/agents` for Copilot (documented, [custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents)).
- **Restricting tools.** `tools` takes individual `server/tool` names, `server/*`, or `[]` ([custom agent configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration#tools)). The list filters which tools the agent gets, and unrecognized names are ignored (documented, same page).
- **Copilot CLI subagents.** A custom agent that runs as a subagent gets no repository instruction files unless it sets `include-custom-instructions: true` (documented, [CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)).

**Reviewer:** a user-level custom agent whose `tools` list holds `read`, `search`, and the server's read-only tools, with no edit, terminal, or write tool. The reviewer reads its brief from the skill's `review.md` rather than from `AGENTS.md`.

## 10. What can block the package outright

- **`ChatStrictPluginOnlyCustomization`** blocks standalone user and workspace skills, agents, instructions, hooks, and MCP servers, while allowing plugin-provided ones ([policy reference](https://code.visualstudio.com/docs/enterprise/policies)). Agent Plugins are the packaging route through it, and are a contingency, not a current target.
- **The "MCP servers in Copilot" policy** "defines whether MCP servers can run at all across Copilot clients" (documented, [MCP management](https://docs.github.com/en/copilot/concepts/mcp-management)).
- **VS Code's own MCP policies** act on the device whatever the GitHub policy says: `ChatMCP` controls access to installed servers, `ChatAllowedMcpServers` and `ChatAllowManagedMcpServersOnly` restrict which servers may run, and `ChatDeniedMcpServers` blocks matching servers, taking precedence over any allow rule (documented, [policy reference](https://code.visualstudio.com/docs/enterprise/policies)).
- **Managed MCP allowlists** must list the server's exact command line ([§3](#3-server-configuration)).
- **A managed sandbox** with `sandboxMcpServers: true` requires local MCP servers to run in the sandbox, in Copilot CLI and VS Code's Agent Host. The sandbox's path rules may then block the server's writes to the project ([managed settings](https://docs.github.com/en/copilot/reference/enterprise-administrators/enterprise-managed-settings); documented, except that the path rules apply to MCP servers, which is inferred).

## Field-test checklist

There's no Copilot host here, so the first real run is a field test in VS Code. Report each item as pass, fail, or "different", with what happened.

1. A new chat's Session Target offers Local, and the session runs there.
2. The `awb-*` skills appear as `/` commands and load when named in plain language.
3. `AGENTS.md` is in effect: the agent follows its rules without being pointed at the file.
4. The server starts from the user-level configuration, after its trust dialog. Its tools appear under the server in the tools picker.
5. Read-only tools run without a confirmation prompt.
6. Each write tool asks once, and "Allow in this Workspace" holds across a new chat in the same workspace.
7. The server finds the project with no argument, and a deliberately wrong `project` argument is refused.
8. The reviewer runs as a subagent, cannot edit files, and returns its report.
9. With the `awb-*` skills in `~/.agents/skills` and linked from `~/.claude/skills`, each appears once in the `/` menu.
10. Optional: in a Copilot-harness session, the server's tools load, steps 5 and 6 show what it asks, and step 7 shows whether it finds the project with no argument.

## Open uncertainties

- The Copilot harness's MCP approval options beyond "Allow in this Session", and whether it ever honors `readOnlyHint`. Its runtime is closed source.
- The default working directory of a stdio server configured at user level, in every surface.
- How `${workspaceFolder}` resolves in user-level VS Code configuration in multi-root and empty windows.
- Whether VS Code Local honors a skill's `allowed-tools`.
- A formal Copilot CLI protocol support matrix.
- Whether the Copilot harness sends MCP roots. Copilot CLI advertises none ([§4](#4-project-root)), so a user-level server there may depend on the `project` argument.
