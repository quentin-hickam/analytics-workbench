#!/bin/sh
# One line per simulation sandbox: phase, outcome, counts, what is running, last transcript entry.
S="$(cd "$(dirname "$0")/.." && pwd)"
for j in "$S"/*/sim.json; do
  python3 - "$(dirname "$j")" <<'PY'
import json, re, sys
from pathlib import Path
d = Path(sys.argv[1])
sf = d / "relay/state.json"
st = json.loads(sf.read_text()) if sf.exists() else {}
t = (d / "transcript.md").read_text() if (d / "transcript.md").exists() else ""
last = (re.findall(r"^## \[(.*?)\] (.*)$", t, re.M) or [("", "")])[-1]
print(f"{d.name:16} {st.get('phase', '-'):12} {str(st.get('outcome') or ''):9} user={st.get('human_messages', 0):<3}"
      f" agent={st.get('agent_replies', 0):<3} running={st.get('running') or '-'} | last: {last[0]} {last[1][:48]}")
PY
done
