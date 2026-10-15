### Added

- Print-only `install_helpers.py --mcp-config copilot|claude|codex` entries for user-level MCP registration, with absolute interpreter and server paths, host-native JSON or TOML, and a separate merge destination. Unsupported hosts and mixed install/registration arguments are refused without writes.
- A user-level VS Code package reviewer with only file read/search and `awb/read` tools, plus a Copilot subagent launch branch that reports unavailable tools as a failed review.

### Changed

- Generated workbench instructions map CLI operations to the seven merged MCP tools when available, retain the CLI fallback, and pass the absolute project root explicitly.
- Installation uses shared skills in `~/.agents/skills`, per-skill Claude Code symlinks with a copy-both fallback, per-host server registration, and VS Code Local workspace and approval steps. `awb-init` reports registration output when the host has no registered `awb` server.
- Design notes record the user-level reviewer as a deliberate vendor-specific exception that is never generated into projects.

### Fixed

- Copilot compatibility research resolves issue #50's source labels and pinned citations, instruction discovery settings, sandbox and approval precision, managed allowlist matchers, skill shadowing limits, and reviewer tool-name verification checklist.
