"""Attribute each exec_command in a Codex rollout to its own `: task=N` tag."""
import json, re, sys, collections
def counts(path):
    c = collections.Counter()
    for l in open(path):
        p = json.loads(l).get("payload", {})
        if p.get("type") not in ("custom_tool_call", "function_call"):
            continue
        text = p.get("input") or p.get("arguments") or ""
        segs = re.split(r"exec_command\(", text)[1:] or [text]
        for s in segs:
            m = re.search(r":\s*task=([A-Za-z0-9_-]+)", s)
            c[m.group(1) if m else "untagged"] += 1
    return c
a, b = counts(sys.argv[1]), counts(sys.argv[2])
keys = sorted(set(a) | set(b), key=lambda k: (0, int(k)) if k.isdigit() else (1, k))
print("task\tbaseline\tfixed\tdelta")
for k in keys: print(f"{k}\t{a[k]}\t{b[k]}\t{b[k]-a[k]:+d}")
print(f"TOTAL\t{sum(a.values())}\t{sum(b.values())}\t{sum(b.values())-sum(a.values()):+d}")
