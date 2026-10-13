"""Count tool calls (model round trips) and shell commands per `: task=N` tag in a Codex rollout."""
import json, re, sys, collections
calls, cmds, fails = collections.Counter(), collections.Counter(), collections.Counter()
outputs = {}
rows = [json.loads(l) for l in open(sys.argv[1])]
for o in rows:
    p = o.get("payload", {})
    if p.get("type") in ("custom_tool_call_output", "function_call_output"):
        outputs[p.get("call_id")] = str(p.get("output", ""))
for o in rows:
    p = o.get("payload", {})
    if p.get("type") not in ("custom_tool_call", "function_call"):
        continue
    text = p.get("input") or p.get("arguments") or ""
    tags = re.findall(r":\s*task=([A-Za-z0-9_-]+)", text)
    n = max(len(re.findall(r"exec_command\(", text)), 1)
    key = tags[0] if len(set(tags)) == 1 else ("+".join(sorted(set(tags))) if tags else "untagged")
    calls[key] += 1; cmds[key] += n
    out = outputs.get(p.get("call_id"), "")
    if re.search(r"exit(?: code|_code)?[\"':= ]+[12]\b|Traceback|\"refused\"|\"passed\": false|\"released\": false", out):
        fails[key] += 1
def order(k):
    m = re.match(r"\d+", k); return (0, int(m.group())) if m else (1, k)
print("task\tcalls\tcommands\tcalls_with_failure_signal")
for k in sorted(calls, key=order):
    print(f"{k}\t{calls[k]}\t{cmds[k]}\t{fails[k]}")
print(f"TOTAL\t{sum(calls.values())}\t{sum(cmds.values())}\t{sum(fails.values())}")
