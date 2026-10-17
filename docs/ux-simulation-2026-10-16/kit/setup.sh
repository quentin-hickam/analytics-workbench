#!/bin/sh
# Build one simulation sandbox.  usage: setup.sh <dataset> <variant A|B> [run-id] [max-human-messages] [max-hours]
#   A = Claude (Opus) human, Codex agent      B = Codex human, Claude (Opus) agent
# Both roles are headless CLI sessions driven by relay.py (claude -p / codex exec).
# Changes from 2026-10-15 (harness fixes, found in the shakedown):
#   - Codex homes get a .zprofile/.zshrc putting a Python 3.13 first on PATH (the
#     login shell under a fake HOME otherwise resolved /usr/bin/python3 3.9.6).
#   - Codex's bundled system skills and image generation are turned off, so it
#     lists only the awb-* skills.
#   - The awb MCP server is registered with `codex mcp add` (the README's route)
#     and its tools are auto-approved, standing in for a user who clicks Allow:
#     non-interactive exec cannot prompt, so approval_policy=never used to deny
#     every MCP write call.
#   - <project>/.git is an extra writable root: workspace-write keeps .git
#     read-only, which blocked `git init` (an interactive user would approve it).
set -eu
SIM="$(cd "$(dirname "$0")/.." && pwd)"
ds="$1"; v="$2"; id="${3:-$ds-$v}"; maxh="${4:-45}"; maxt="${5:-8}"
d="$SIM/$id"
rm -rf "$d"
mkdir -p "$d/project" "$d/storage/landed" "$d/storage/releases" "$d/human" "$d/feedback" "$d/relay" "$d/inbox" "$d/prompts"
# --- the human's folder: the release README (dist copy) and the brief
cp "$SIM/release/analytics-workbench-skills/README.md" "$d/human/README.md"
{ cat "$SIM/kit/personas/$ds.md"; cat "$SIM/kit/human-rules.md"; } | sed "s|{SIMDIR}|$d|g" > "$d/human/BRIEF.md"
if [ "$ds" = taxi ]; then cp "$SIM/datasets/taxi/"* "$d/inbox/"; fi

codex_home() {  # $1 = home dir, $2 = reasoning effort
  h="$1"
  mkdir -p "$h/.codex"
  printf 'export PATH="<python-prefix>/bin:<homebrew>/bin:$PATH"\n' > "$h/.zprofile"
  cp "$h/.zprofile" "$h/.zshrc"; cp "$h/.zprofile" "$h/.bash_profile"
  ln -sf "$HOME/.codex/auth.json" "$h/.codex/auth.json"
  cat > "$h/.codex/config.toml" <<EOF
model = "gpt-6.1-sol"
model_reasoning_effort = "$2"
approval_policy = "never"
sandbox_mode = "workspace-write"

[features]
apps = false
plugins = false
in_app_browser = false
browser_use = false
computer_use = false
image_generation = false

[skills.bundled]
enabled = false
EOF
}
# workspace-write would otherwise make all of /tmp writable, and the sims live under it
tmp_excl='exclude_slash_tmp = true
exclude_tmpdir_env_var = true'


# --- the agent's home: released skills at user level, the downloaded release, a git identity
ah="$d/agent-home"
mkdir -p "$ah/.agents/skills" "$ah/Downloads" "$ah/.cache" "$ah/.local"
cp -R "$SIM/release/analytics-workbench-skills/"awb-* "$ah/.agents/skills/"
cp -R "$SIM/release/analytics-workbench-skills" "$ah/Downloads/"
printf '[user]\n\tname = Sim Analyst\n\temail = analyst@example.com\n[init]\n\tdefaultBranch = main\n' > "$ah/.gitconfig"
if [ "$v" = A ]; then
  codex_role=agent
  codex_home "$ah" high
  cat >> "$ah/.codex/config.toml" <<EOF

[sandbox_workspace_write]
network_access = true
$tmp_excl
writable_roots = ["$d/storage", "$d/feedback", "$d/project/.git", "$ah/.cache", "$ah/.local"]
EOF
  (cd "$d/project" && HOME="$ah" CODEX_HOME="$ah/.codex" codex mcp add awb -- <python-prefix>/bin/python3 "$ah/.agents/skills/awb-init/assets/awb_mcp.py" >/dev/null)
  python3 - "$ah/.codex/config.toml" <<'EOF'
import sys
p = sys.argv[1]; t = open(p).read()
assert '[mcp_servers.awb]\n' in t, 'awb MCP registration missing'
open(p, 'w').write(t.replace('[mcp_servers.awb]\n', '[mcp_servers.awb]\ndefault_tools_approval_mode = "approve"\n', 1))
EOF
else
  codex_role=human
  codex_home "$d/human-home" medium
  mkdir -p "$d/human-home/.cache"
  cat >> "$d/human-home/.codex/config.toml" <<EOF

[sandbox_workspace_write]
$tmp_excl
writable_roots = ["$d/human-home/.cache"]
EOF
  # Claude Code agent: skills linked into ~/.claude/skills as the README says, awb MCP registered for the session
  mkdir -p "$ah/.claude/skills"
  for s in "$ah/.agents/skills/"awb-*; do ln -s "$s" "$ah/.claude/skills/$(basename "$s")"; done
  # awb as the README registers it, plus the harness's permission-prompt answerer (stands in for a user clicking Allow)
  printf '{"mcpServers": {"awb": {"type": "stdio", "command": "<python-prefix>/bin/python3", "args": ["%s"], "env": {"HOME": "%s"}}, "simperm": {"type": "stdio", "command": "<python-prefix>/bin/python3", "args": ["%s", "%s"], "env": {}}}}\n' \
    "$ah/.agents/skills/awb-init/assets/awb_mcp.py" "$ah" "$SIM/kit/approver_mcp.py" "$d/relay/permission-prompts.jsonl" > "$ah/claude-mcp.json"
  sed "s|{SIMDIR}|$d|g" "$SIM/kit/claude-agent-system.md" > "$d/prompts/claude-agent-system.md"
fi
cat > "$d/sim.json" <<EOF
{"id": "$id", "dataset": "$ds", "variant": "$v", "codex_role": "$codex_role", "simdir": "$d", "caps": {"human_messages": $maxh, "hours": $maxt}, "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"}
EOF
echo "built $d (codex plays $codex_role)"
