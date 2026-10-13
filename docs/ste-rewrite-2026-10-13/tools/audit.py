#!/usr/bin/env python3
"""Structural guard for an STE rewrite: compare with the original (git BASE).

ERROR  = a structural invariant broke (must be fixed).
WARN   = a signal that meaning may have drifted (review by hand).
STE    = residual ASD-STE100 rule violations in the rewritten text (style metrics).

usage: audit.py [--base REV] [--json OUT] FILE...
"""
import argparse, json, re, subprocess, sys
from collections import Counter
from pathlib import Path

PROTECTED = Path(__file__).with_name("protected.json")

FENCE = re.compile(r"^(\s*)(```+|~~~+)")
CODE = re.compile(r"(`+)(.+?)\1")
LINK = re.compile(r"\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
URL = re.compile(r"https?://[^\s)>\]`]+")
HEAD = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
COMMENT = re.compile(r"<!--.*?-->", re.S)
NUM = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?%?")
MODALS = {
    "must": r"\bmust\b", "must not": r"\bmust not\b", "never": r"\bnever\b", "always": r"\balways\b",
    "only": r"\bonly\b", "do not": r"\b(?:do not|don't|does not|doesn't)\b", "not": r"\bnot\b|n't\b",
    "no": r"\bno\b", "unless": r"\bunless\b", "if": r"\bif\b", "should": r"\bshould\b",
    "may": r"\bmay\b", "can": r"\bcan(?:not)?\b", "optional": r"\boptional(?:ly)?\b",
    "refuse": r"\brefus\w*", "stop": r"\bstop\w*",
}
# Words ASD-STE100 does not approve (or approves with another meaning); a small, well-known subset.
UNAPPROVED = r"""should|shall|may|might|would|utili[sz]e\w*|ensure\w*|via|prior to|in order to|e\.g\.|i\.e\.|etc\.?|
whether|whilst|thus|hence|therefore|whereas|wherein|leverage\w*|facilitat\w*|perform\w*|commence\w*|
terminat\w*|obtain\w*|require\w*|appropriate|sufficient|numerous|additional|approximately|regarding|load-bearing""".replace("\n", "")
UNAPPROVED_RE = re.compile(r"\b(?:%s)\b" % UNAPPROVED, re.I)
ING = re.compile(r"\b[a-z]{3,}ing\b")
ING_OK = {"string", "thing", "nothing", "something", "anything", "everything", "during", "bring", "king",
          "ring", "spring", "swing", "wing", "sing", "ceiling", "evening", "morning", "spring", "wiring",
          "building", "heading", "headings", "setting", "settings", "missing", "existing", "following",
          "remaining", "pending", "landing", "cleaning", "packaging", "routing", "tracking", "scoping",
          "timing", "warning", "warnings", "rounding", "encoding", "listing", "mapping", "staging"}


def git_show(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def split(text):
    """Return (frontmatter, fences, prose_lines) where prose lines exclude fenced blocks."""
    lines = text.split("\n")
    fm, i = [], 0
    if lines and lines[0] == "---":
        j = lines.index("---", 1)
        fm, i = lines[1:j], j + 1
    fences, prose, cur, marker = [], [], None, None
    for line in lines[i:]:
        m = FENCE.match(line)
        if cur is None and m:
            cur, marker = [line], m.group(2)[0] * 3
        elif cur is not None:
            cur.append(line)
            if line.strip().startswith(marker) and line.strip().strip(marker[0]) == "":
                fences.append("\n".join(cur)); cur = None
        else:
            prose.append(line)
    if cur is not None:
        fences.append("\n".join(cur))
    return fm, fences, prose


def tables(prose):
    out, cur = [], []
    for line in prose + [""]:
        if line.lstrip().startswith("|"):
            cur.append(line)
        elif cur:
            out.append(cur); cur = []
    return out


def strip_code(s):
    return CODE.sub(" CODE ", s)


def sentences(prose):
    text, buf = [], []
    for line in prose:
        s = line.strip()
        if not s or HEAD.match(s) or s.startswith("|") or s.startswith("<!--"):
            if buf: text.append(" ".join(buf)); buf = []
            continue
        if re.match(r"^([-*+]|\d+\.)\s", s):
            if buf: text.append(" ".join(buf)); buf = []
            s = re.sub(r"^([-*+]|\d+\.)\s+", "", s)
        buf.append(s)
    if buf: text.append(" ".join(buf))
    sents = []
    for para in text:
        para = strip_code(COMMENT.sub("", para))
        para = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", para)
        for s in re.split(r"(?<=[.!?])\s+(?=[A-Z*\"(])", para):
            if s.strip(): sents.append(s.strip())
    return sents


def words(s):
    return [w for w in re.split(r"\s+", s) if re.search(r"\w", w)]


def facts(text):
    fm, fences, prose = split(text)
    p = "\n".join(prose)
    pc = COMMENT.sub("", p)
    fm_keys = [l.split(":", 1)[0] for l in fm if re.match(r"^[A-Za-z_-]+:", l)]
    fm_name = [l for l in fm if l.startswith("name:")]
    return {
        "frontmatter_keys": fm_keys, "frontmatter_name": fm_name,
        "fences": fences,
        "headings": [l.rstrip() for l in prose if HEAD.match(l)],
        "comments": COMMENT.findall(p),
        "code": Counter(m.group(2) for m in CODE.finditer(pc)),
        "links": Counter(LINK.findall(pc)),
        "urls": Counter(URL.findall(pc)),
        "numbers": Counter(NUM.findall(strip_code(LINK.sub("]()", pc)))),
        "tables": [(t[0].strip(), len(t)) for t in tables(prose)],
        "modals": {k: len(re.findall(v, strip_code(pc), re.I)) for k, v in MODALS.items()},
        "sentences": sentences(prose),
        "text": p,
    }


def audit(path, base, protected):
    new_text = Path(path).read_text()
    old_text = git_show(base, path)
    res = {"file": path, "errors": [], "warnings": [], "ste": {}}
    if old_text is None:
        res["warnings"].append("no base version")
        return res
    o, n = facts(old_text), facts(new_text)
    E, W = res["errors"].append, res["warnings"].append
    for key in ("frontmatter_keys", "frontmatter_name", "fences", "headings", "comments"):
        if o[key] != n[key]:
            E(f"{key} changed: -{[x for x in o[key] if x not in n[key]][:5]} +{[x for x in n[key] if x not in o[key]][:5]}")
    for key in ("code", "links", "urls", "numbers"):
        lost = set(o[key]) - set(n[key]); gained = set(n[key]) - set(o[key])
        if lost or gained:
            E(f"{key} set changed: lost {sorted(lost)[:8]} gained {sorted(gained)[:8]}")
        else:
            moved = {k: (o[key][k], n[key][k]) for k in o[key] if o[key][k] != n[key][k]}
            if moved: W(f"{key} counts changed: {dict(list(moved.items())[:8])}")
    if [h for h, _ in o["tables"]] != [h for h, _ in n["tables"]]:
        E(f"table headers changed: {[h for h, _ in o['tables']]} -> {[h for h, _ in n['tables']]}")
    elif o["tables"] != n["tables"]:
        E(f"table row counts changed: {[r for _, r in o['tables']]} -> {[r for _, r in n['tables']]}")
    for lit in protected.get(path, []):
        if lit in old_text and lit not in new_text:
            E(f"protected literal missing: {lit!r}"[:200])
    om, nm = o["modals"], n["modals"]
    for k in ("must", "must not", "never", "always", "only", "do not", "unless", "refuse", "optional", "no"):
        if om[k] and nm[k] < om[k] * 0.5 or (om[k] == 0 and nm[k] >= 3):
            W(f"modal/negation '{k}': {om[k]} -> {nm[k]}")
    neg_o = om["not"] + om["no"] + om["never"]; neg_n = nm["not"] + nm["no"] + nm["never"]
    if neg_o and abs(neg_n - neg_o) / neg_o > 0.35:
        W(f"negation total: {neg_o} -> {neg_n}")
    if om["should"] + om["may"] and nm["must"] - om["must"] > (om["should"] + om["may"]) * 0.6:
        W(f"possible strengthening: should/may {om['should']}+{om['may']} gone, must {om['must']} -> {nm['must']}")
    ow, nw = len(words(o["text"])), len(words(n["text"]))
    if ow > 40 and not 0.75 <= nw / ow <= 1.6:
        W(f"length ratio {nw}/{ow} = {nw/ow:.2f}")
    sents = n["sentences"]
    lens = [len(words(s)) for s in sents]
    res["ste"] = {
        "sentences": len(sents),
        "mean_len": round(sum(lens) / len(lens), 1) if lens else 0,
        "over_20": sum(l > 20 for l in lens), "over_25": sum(l > 25 for l in lens),
        "semicolons": sum(s.count(";") for s in sents),
        "dashes": sum(len(re.findall(r" — | -- |—", s)) for s in sents),
        "unapproved": Counter(m.group(0).lower() for s in sents for m in UNAPPROVED_RE.finditer(s)),
        "ing": Counter(w for s in sents for w in ING.findall(s.lower()) if w not in ING_OK),
        "old_mean_len": round(sum(len(words(s)) for s in o["sentences"]) / max(1, len(o["sentences"])), 1),
        "old_over_25": sum(len(words(s)) > 25 for s in o["sentences"]),
        "longest": sorted(sents, key=lambda s: -len(words(s)))[:3],
    }
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="6ebca3a")
    ap.add_argument("--json")
    ap.add_argument("--verbose", "-v", action="store_true")
    ap.add_argument("files", nargs="+")
    a = ap.parse_args()
    protected = json.loads(PROTECTED.read_text()) if PROTECTED.exists() else {}
    results = [audit(f, a.base, protected) for f in a.files]
    bad = 0
    for r in results:
        s = r["ste"]
        print(f"== {r['file']}: {len(r['errors'])} errors, {len(r['warnings'])} warnings; "
              f"mean sentence {s.get('old_mean_len')}->{s.get('mean_len')} words, >25: {s.get('old_over_25')}->{s.get('over_25')}, "
              f">20: {s.get('over_20')}, ';': {s.get('semicolons')}, unapproved: {sum(s.get('unapproved', {}).values())}, -ing: {sum(s.get('ing', {}).values())}")
        for e in r["errors"]: print("  ERROR", e)
        for w in r["warnings"]: print("  WARN ", w)
        if a.verbose and s:
            print("  unapproved:", dict(s["unapproved"]), "\n  -ing:", dict(s["ing"].most_common(15)))
            for l in s["longest"]: print("  long:", l[:300])
        bad += bool(r["errors"])
    if a.json:
        Path(a.json).write_text(json.dumps(results, indent=1, default=dict))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
