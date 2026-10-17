#!/usr/bin/env python3
"""render.py <simdir>: write SIMDIR/REFEREE.md from the kit's referee playbook."""
import json, sys
from pathlib import Path
kit = Path(__file__).resolve().parent
simdir = Path(sys.argv[1]).resolve()
cfg = json.loads((simdir / "sim.json").read_text())
c = cfg["caps"]
caps = f"{c['human_messages']} user messages or {c['hours']} hour{'s' if c['hours'] != 1 else ''} of wall-clock time, whichever comes first"
t = (kit / "referee.md").read_text()
for k, v in {"{KIT}": str(kit), "{SIMDIR}": str(simdir), "{VARIANT}": cfg["variant"], "{ID}": cfg["id"], "{CAPS}": caps}.items():
    t = t.replace(k, v)
(simdir / "REFEREE.md").write_text(t)
print(simdir / "REFEREE.md")
