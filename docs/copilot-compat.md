# GitHub Copilot compatibility

Researched 2026-10-14, against VS Code 1.142 and the MCP specification revision `2026-07-28`. No Copilot host was run. Every claim below comes from primary sources: VS Code and GitHub documentation and release notes, the `microsoft/vscode` and `github/copilot-cli` repositories, and the MCP specification. Two independent research passes, by Claude Opus and by Codex, were cross-checked. The claims the design depends on were then re-read at the source. **Documented** means a primary source states the claim. **Code** means it was read from public source on `main` and is not a release guarantee. **Inferred** means neither of those settles it.

## Target tiers

1. **Primary: the VS Code Local harness**, the Copilot Chat agent mode built into VS Code. Design decisions are made for this host.
2. **Secondary: Claude Code and Codex.** They keep working through the same skills and the same MCP server.
3. **Tertiary: Copilot CLI, the Copilot cloud agent, and VS Code's Copilot harness.** Nothing depends on them. They are noted where they differ.

## Design decisions this research settles

| Decision | Basis |
| --- | --- |
| Helpers are exposed as MCP tools over stdio. The CLI stays as a fallback and for tests. | Hosts can confirm every terminal command. MCP tools have their own approval scopes in VS Code (below). |
| Every read-only tool carries `readOnlyHint: true`. No tool both reads and writes. | VS Code Local runs read-only tools without confirmation. |
| Write tools are few and coarse. | Each tool needs its own approval, and in the Copilot harness that approval lasts only one session. |
| The server speaks the legacy `2025-11-25` protocol, and answers any other method, including `server/discover`, with an immediate `-32601` error. | VS Code Local negotiates `2025-11-25`. Dual-era clients fall back to `initialize` on any non-modern error. |
| The project root comes from an explicit argument, then from MCP roots, then from the working directory. It is validated as a workbench before anything is written. | Roots are deprecated in the spec. A user-level server's working directory isn't documented, and a plugin server's is its install folder. |
| Tool results are bounded text, with no `structuredContent`. | VS Code Local passes `structuredContent` to the model *instead of* the text when both are present. Large results spill to disk or are truncated. |
| Skills install to `~/.agents/skills` (VS Code and Codex) or `~/.claude/skills` (Claude Code). | Discovery locations below. |
| The package reviewer is a custom agent whose `tools` list holds only read tools and the server's read-only tools. | VS Code custom agents restrict tools by `server/tool` name, and a subagent run under a named custom agent takes that agent's tools. |

## 1. Harnesses

VS Code now runs agent sessions in two Copilot harnesses with different engines:

- **Local**, the original VS Code agent. Native MCP integration, approvals in `languageModelToolsConfirmationService`.
- **Copilot**, which runs the Copilot SDK in VS Code's Agent Host process. It shares its runtime with Copilot CLI.

From 1.142, Copilot is being rolled out progressively as the default harness for new sessions (documented, [1.142](https://code.visualstudio.com/updates/v1_142)). The rollout has four consequences:
- Opening an existing, unarchived Local chat moves it to Copilot.
- When an organization configures a nonempty managed `permissions` object, or sets `sandbox.enabled` to `true`, VS Code requires the Copilot harness for full chat sessions.
- Administrators can keep Local with `vscode.temporaryDefaultToLocalHarness`, which also overrides that routing.
- The `ChatToolsAutoApprove` policy does not trigger the routing by itself ([manage AI settings](https://code.visualstudio.com/docs/enterprise/manage-ai-settings)).

A user picks the harness from the **Session Target** control in a new chat, which lists only the targets whose requirements are met ([agent harnesses](https://code.visualstudio.com/docs/agents/run/agent-harnesses)). The docs don't say whether Local will be retired.

**Consequence:** the package targets Local, and must not break in the Copilot harness, because users may land there without choosing it. The install guide tells users to pick Local in the Session Target control.

## 2. Tool approval

**VS Code Local**:
- **Read-only tools.** A tool marked `readOnlyHint` runs without confirmation, and every other tool shows the confirmation dialog (documented, [MCP developer guide](https://code.visualstudio.com/api/extension-guides/ai/mcp)).
- **Approval scopes.** A confirmation can approve once, for the session, for the workspace, or for all future calls. **Chat: Manage Tool Approval** can trust every tool of one server (documented, [approvals](https://code.visualstudio.com/docs/agents/run/approvals)).

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
- **Whole-server grants.** `--allow-tool='<server>'` allows a whole server for the session, and `permissions-config.json` saves a whole-server approval per location with `"toolName": null` ([allowing tools](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/allowing-tools)).

## 3. Server configuration

VS Code lists four places to configure a server ([MCP servers](https://code.visualstudio.com/docs/agent-customization/mcp-servers)):

| Scope | File | Top-level key | Status |
| --- | --- | --- | --- |
| User, portable | `$COPILOT_HOME/mcp-config.json`, else `~/.copilot/mcp-config.json` | `mcpServers` | Preferred for personal servers used across workspaces |
| Workspace, portable | `.mcp.json` at the workspace root | `mcpServers` | Preferred for shared servers |
| Workspace | `.vscode/mcp.json` | `servers` | Listed as deprecated; kept for VS Code-only features such as `${input:…}` |
| User profile | profile `mcp.json` | `servers` | Listed as deprecated |

- **Copilot harness.** It reads `.mcp.json` and `~/.copilot/mcp-config.json` directly. VS Code forwards eligible servers from other sources, except those that need interactive input.
- **Trust.** Workspace servers inherit Workspace Trust. A server from any other source shows a trust dialog when it first starts and whenever its configuration changes.
- **Stdio keys:** `type: "stdio"`, `command`, `args`, `env`, `envFile`, `cwd` ([configuration reference](https://code.visualstudio.com/docs/agents/reference/mcp-configuration)).
- **Copilot CLI** passes only `PATH` to a server, so every other variable must be set in its configuration.
- **Managed allowlists** match a local server by its exact command and arguments ([managed settings](https://docs.github.com/en/copilot/reference/enterprise-administrators/enterprise-managed-settings#allowedmcpservers)). An install guide should therefore produce one stable command line.

**Install target:** one user-level entry in `~/.copilot/mcp-config.json`, which serves every workspace and both Copilot harnesses. Claude Code and Codex get their own user-level entries.

## 4. Project root

- **VS Code Local** gives servers the workspace root folders as MCP roots, and sends `notifications/roots/list_changed` (documented, [MCP developer guide](https://code.visualstudio.com/api/extension-guides/ai/mcp); code).
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
- **Copilot CLI** has sent modern requests since 1.0.93 ([copilot-cli#5079](https://github.com/github/copilot-cli/issues/5079)).

**Implementation scope:** `initialize`, `notifications/initialized`, `ping`, `tools/list` and `tools/call`, with an immediate JSON-RPC error for every other request, so dual-era clients fall back rather than hang. Supporting the modern era is a later hedge, not a gate.

## 6. Tools and results

- **Name length.** VS Code exposes MCP tools under a collision-resolved `mcp_` server prefix, capped at 64 characters in total (code). The CLI uses `serverName-toolName`, also capped at 64 (documented). Short names fit both.
- **Tool cap.** VS Code allows at most 128 enabled tools per request, counting every source ([tools](https://code.visualstudio.com/docs/agents/run/tools)). A small tool set leaves room for the user's other servers.
- **Structured content.** VS Code Local appends `structuredContent` as JSON and uses it in place of the text items for the model (code). `outputSchema` enforcement by either host is not established.
- **Large output.** Large tool output is written to disk in VS Code 1.110 and later. The CLI caps output sent straight to the model at 20 KiB, and truncates very long single lines.

## 7. Skills

| Surface | Project directories | User directories |
| --- | --- | --- |
| VS Code (both harnesses) | `.github/skills`, `.claude/skills`, `.agents/skills` | `~/.copilot/skills`, `~/.claude/skills`, `~/.agents/skills` |
| Copilot CLI | `.github/skills`, `.agents/skills`, `.claude/skills` | `~/.copilot/skills`, `~/.agents/skills` (no longer `~/.claude/skills`) |

Sources: [VS Code skills](https://code.visualstudio.com/docs/agent-customization/agent-skills), [GitHub skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills).

- **Enabled by default.** Skills are generally available and on by default from VS Code 1.109 (`chat.useAgentSkills`).
- **Names.** A skill's name must match its folder, use lowercase letters, digits and hyphens, and fit in 64 characters. "Names with invalid characters cause the skill to silently fail to load." Descriptions fit in 1,024 characters. Every `awb-*` name complies.
- **Frontmatter.** VS Code honors `name`, `description`, `argument-hint`, `user-invocable` (default true) and `disable-model-invocation` (default false). It does not list `allowed-tools`. Skills appear as `/name` commands.
- **Bundled files.** A skill can link files relative to its folder and tell the agent to run bundled scripts. Running a script still goes through terminal approval, which is why helper execution goes through MCP.

## 8. Instructions

- **Root `AGENTS.md`.** VS Code Local reads it when `chat.useAgentsMdFile` is on, which is the default. Nested `AGENTS.md` files need the experimental `chat.useNestedAgentsMdFiles`, which is off by default ([custom instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions)). The workbench's `AGENTS.md` therefore loads only when the workbench folder is the workspace root.
- **Combining with other instruction files.** Instruction sources are additive, with no general precedence, so a project with `.github/copilot-instructions.md` gets both. Conflicts between them are not resolved by order.

## 9. Subagents and the reviewer

- **Subagents.** VS Code Local starts subagents with `runSubagent`. A subagent inherits the main agent's instructions and tools "unless you specify a custom agent" ([subagents](https://code.visualstudio.com/docs/agents/run/subagents)). It does not inherit the conversation.
- **Custom agent locations.** Custom agents live in `.github/agents` or `.claude/agents` in the workspace, or at user level: in profile storage for Local, and in `~/.copilot/agents` for Copilot.
- **Restricting tools.** `tools` takes individual `server/tool` names, `server/*`, or `[]` ([custom agent configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration#tools)). In the Copilot harness, the SDK enforces the list as an allowlist.
- **Copilot CLI custom agents** skip repository instructions unless they set `include-custom-instructions: true`.

**Reviewer:** a user-level custom agent whose `tools` list holds `read`, `search`, and the server's read-only tools, with no edit, terminal, or write tool. The reviewer reads its brief from the skill's `review.md` rather than from `AGENTS.md`.

## 10. What can block the package outright

- **`ChatStrictPluginOnlyCustomization`** blocks standalone user and workspace skills, agents, instructions, hooks, and MCP servers, while allowing plugin-provided ones ([policy reference](https://code.visualstudio.com/docs/enterprise/policies)). Agent Plugins are the packaging route through it, and are a contingency, not a current target.
- **The "MCP servers in Copilot" organization policy** must allow MCP.
- **Managed MCP allowlists** must list the server's exact command line.

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
9. Optional: steps 5 and 6 repeated in a Copilot-harness session, to see what it asks.

## Open uncertainties

- The Copilot harness's MCP approval options beyond "Allow in this Session", and whether it ever honors `readOnlyHint`. Its runtime is closed source.
- The default working directory of a stdio server configured at user level, in every surface.
- How `${workspaceFolder}` resolves in user-level VS Code configuration in multi-root and empty windows.
- Whether VS Code Local honors a skill's `allowed-tools`.
- A formal Copilot CLI protocol support matrix.
