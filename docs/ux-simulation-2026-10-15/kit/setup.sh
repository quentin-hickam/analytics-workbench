#!/bin/sh
# Build one simulation sandbox.  usage: setup.sh <dataset> <variant A|B>
#   A = Opus human, Codex agent      B = Codex human, Opus agent
set -eu
SIM="$(cd "$(dirname "$0")/.." && pwd)"
ds="$1"; v="$2"
id="$ds-$v"
d="$SIM/$id"
rm -rf "$d"
mkdir -p "$d/project" "$d/storage/landed" "$d/storage/releases" "$d/human" "$d/feedback" "$d/relay" "$d/inbox"
# --- the human's folder: the release README (dist copy) and the brief
cp "$SIM/release/analytics-workbench-skills/README.md" "$d/human/README.md"
{ cat "$SIM/kit/personas/$ds.md"; cat "$SIM/kit/human-rules.md"; } | sed "s|{SIMDIR}|$d|g" > "$d/human/BRIEF.md"
if [ "$ds" = taxi ]; then cp "$SIM/datasets/taxi/"* "$d/inbox/"; fi
# --- the agent's home: released skills at user level, the downloaded release, a git identity
ah="$d/agent-home"
mkdir -p "$ah/.agents/skills" "$ah/Downloads" "$ah/.cache"
cp -R "$SIM/release/analytics-workbench-skills/"awb-* "$ah/.agents/skills/"
cp -R "$SIM/release/analytics-workbench-skills" "$ah/Downloads/"
printf '[user]\n\tname = Sim Analyst\n\temail = analyst@example.com\n[init]\n\tdefaultBranch = main\n' > "$ah/.gitconfig"
if [ "$v" = A ]; then
  codex_role=agent
  mkdir -p "$ah/.codex"
  ln -sf "$HOME/.codex/auth.json" "$ah/.codex/auth.json"
  cat > "$ah/.codex/config.toml" <<EOF
model = "gpt-6.1-sol"
model_reasoning_effort = "high"
approval_policy = "never"
sandbox_mode = "workspace-write"

[features]
apps = false
plugins = false
in_app_browser = false
browser_use = false
computer_use = false

[sandbox_workspace_write]
network_access = true
writable_roots = ["$d/storage", "$d/feedback", "$ah/.cache", "$ah/.local"]

EOF
  HOME="$ah" <python-prefix>/bin/python3 "$ah/.agents/skills/awb-init/scripts/install_helpers.py" --mcp-config codex 2>/dev/null >> "$ah/.codex/config.toml"
  mkdir -p "$ah/.local"
else
  codex_role=human
  hh="$d/human-home"
  mkdir -p "$hh/.codex"
  ln -sf "$HOME/.codex/auth.json" "$hh/.codex/auth.json"
  cat > "$hh/.codex/config.toml" <<EOF
model = "gpt-6.1-sol"
model_reasoning_effort = "medium"
approval_policy = "never"
sandbox_mode = "workspace-write"

[features]
apps = false
plugins = false
in_app_browser = false
browser_use = false
computer_use = false
EOF
fi
cat > "$d/sim.json" <<EOF
{"id": "$id", "dataset": "$ds", "codex_role": "$codex_role", "simdir": "$d", "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"}
EOF
echo "built $d (codex plays $codex_role)"
