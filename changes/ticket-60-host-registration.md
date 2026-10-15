### Changed

- `install_helpers.py --mcp-config copilot|claude|codex` also prints, on stderr, the host's own user-level registration command, ready to paste into a POSIX shell with both absolute paths and the JSON shell-quoted: `copilot mcp add awb -- …`, `claude mcp add-json --scope user awb '…'`, or `codex mcp add awb -- …`. The printed entry and its merge destination stay as the fallback for PowerShell, cmd, or a host without that command. The script still runs nothing and writes nothing.
- `awb-init` offers the host's registration command in its report when no `awb` server is registered, with the entry and destination as the fallback, so Claude Code users no longer hand-edit `~/.claude.json` while Claude Code rewrites it.
- The README's MCP server section and `docs/copilot-compat.md` record each host's registration command with the source and version checked, and why `code --add-mcp` is not used: it writes the deprecated VS Code profile `mcp.json`.
