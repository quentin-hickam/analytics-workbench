#!/usr/bin/env python3
"""Plan, and optionally apply, the file-level update of a workbench to the installed skills.

Run with Python 3.10+:
    plan_update.py PROJECT_ROOT                      # read-only plan
    plan_update.py PROJECT_ROOT --apply              # replace unmodified earlier copies
    plan_update.py PROJECT_ROOT --replace PATH ...   # also replace these customized copies
    plan_update.py PROJECT_ROOT --remove-retired     # delete unmodified retired copies
Emits compact JSON. Only files the skills copy verbatim are compared; adapted records such as
AGENTS.md and README.md are left to the skill's migration steps.
"""

import argparse
import hashlib
import json
import shutil
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]
VERSIONS = SKILLS / "awb-update/assets/shipped-versions.json"


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _old_format_drafts(root):
    drafts = []
    for draft in sorted(root.glob("deliveries/*/*/draft")):
        findings = draft / "findings.md"
        reasons = []
        if (draft / "figures").is_dir():
            reasons.append("figures directory")
        if findings.is_file() and "**Headline:**" not in findings.read_text(encoding="utf-8", errors="replace"):
            reasons.append("findings.md is not a slide outline")
        for name in ("journal.md", "executive-summary.md"):
            if (draft / name).exists():
                reasons.append(name)
        if reasons:
            drafts.append({"path": draft.relative_to(root).as_posix(), "reasons": reasons})
    return drafts


def plan(root, *, apply=False, replace=(), remove_retired=False):
    root = Path(root).resolve()
    if not any((root / name).exists() for name in ("AGENTS.md", "foundation", "investigations")):
        return {"project": str(root), "workbench": False}
    versions = json.loads(VERSIONS.read_text())
    replace = set(replace)
    unknown = replace - {entry["path"] for entry in versions["copied"]}
    if unknown:
        raise SystemExit(f"--replace names files the skills do not copy: {sorted(unknown)}")
    files, retired = [], []
    for entry in versions["copied"]:
        target, asset = root / entry["path"], SKILLS / entry["asset"]
        if not target.is_file():
            files.append({"path": entry["path"], "status": "absent", "action": "none"})
            continue
        digest = _sha256(target)
        if digest == _sha256(asset):
            status, action = "current", "none"
        elif digest in entry["previous"]:
            status, action = "earlier", "replace" if apply else "replace with --apply"
        else:
            status, action = "customized", "replace" if entry["path"] in replace else "ask"
        if action == "replace":
            shutil.copyfile(asset, target)
            action = "replaced"
        files.append({"path": entry["path"], "status": status, "action": action,
                      **({"asset": str(asset)} if status == "customized" else {})})
    for entry in versions["retired"]:
        target = root / entry["path"]
        if not target.is_file():
            continue
        if _sha256(target) in entry["shipped"]:
            status, action = "unmodified", "remove with --remove-retired"
            if remove_retired:
                target.unlink()
                if target.parent != root and not any(target.parent.iterdir()):
                    target.parent.rmdir()
                action = "removed"
        else:
            status, action = "customized", "ask"
        retired.append({"path": entry["path"], "status": status, "action": action})
    return {"project": str(root), "workbench": True, "files": files, "retired": retired,
            "old_format_drafts": _old_format_drafts(root)}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument("--apply", action="store_true", help="replace unmodified earlier copies")
    parser.add_argument("--replace", nargs="+", default=[], metavar="PATH",
                        help="also replace these customized copies, by project path")
    parser.add_argument("--remove-retired", action="store_true", help="delete unmodified retired copies")
    args = parser.parse_args()
    print(json.dumps(plan(args.project_root, apply=args.apply, replace=args.replace,
                          remove_retired=args.remove_retired)))


if __name__ == "__main__":
    main()
