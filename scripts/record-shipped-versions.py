#!/usr/bin/env python3
"""Regenerate awb-init's record of every committed version of the files skills copy into projects.

Run from anywhere in the repository after changing a copied asset and committing it:
    python3 scripts/record-shipped-versions.py
Writes .agents/skills/awb-init/assets/shipped-versions.json, which
`install_helpers.py --upgrade` reads. `--check` exits 1 when the
file is out of date instead of writing it.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".agents/skills/awb-init/assets/shipped-versions.json"
SKILLS = ".agents/skills/"
FORMAT = "assets/package-format/"

# project path -> (current asset relative to the skills directory or None when retired,
#                  every repository path the file has shipped from)
COPIED = {
    "package-format/findings-template.md": "awb-package/" + FORMAT + "findings-template.md",
    "package-format/methodology-template.md": "awb-package/" + FORMAT + "methodology-template.md",
    "package-format/m365-assembly.md": "awb-package/" + FORMAT + "m365-assembly.md",
    "package-format/manifest-template.md": "awb-package/" + FORMAT + "manifest-template.md",
    "src/packaging/manifest.py": "awb-package/assets/awb_manifest.py",
    "src/packaging/findings.py": "awb-package/assets/awb_findings.py",
    "src/packaging/charts.py": "awb-package/assets/awb_charts.py",
    "src/packaging/draft.py": "awb-package/assets/awb_draft.py",
    "src/awb.py": "awb-init/assets/awb_cli.py",
    "src/provenance.py": "awb-init/assets/awb_provenance.py",
    "src/preparation/landing.py": "awb-init/assets/awb_landing.py",
    "src/exploration/validate.py": "awb-init/assets/awb_validate.py",
    "workbench-guides/data.md": "awb-init/assets/workbench/workbench-guides/data.md",
    "workbench-guides/analysis.md": "awb-init/assets/workbench/workbench-guides/analysis.md",
}
RETIRED = {
    "package-format/journal-template.md": ["awb-package/" + FORMAT + "journal-template.md",
                                           "workbench-package/" + FORMAT + "journal-template.md"],
    "package-format/executive-summary-template.md": [
        "awb-package/" + FORMAT + "executive-summary-template.md",
        "workbench-package/" + FORMAT + "executive-summary-template.md"],
    "src/presentation/style.py": ["awb-visualize/assets/awb_style.py"],
}
# Earlier repository paths of files that are still shipped.
EARLIER = {
    "package-format/m365-assembly.md": ["workbench-package/" + FORMAT + "m365-assembly.md"],
    "package-format/manifest-template.md": ["workbench-package/" + FORMAT + "manifest-template.md"],
}


def git(*args, binary=False):
    result = subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True)
    return result.stdout if binary else result.stdout.decode()


def committed_hashes(paths):
    """SHA-256 of every blob committed at these paths in HEAD's history, sorted."""
    blobs = set()
    for path in paths:
        for line in git("log", "HEAD", "--format=", "--raw", "--no-abbrev", "--", SKILLS + path).splitlines():
            fields = line.split()
            if line.startswith(":") and len(fields) >= 5 and set(fields[3]) != {"0"}:
                blobs.add(fields[3])
    return sorted(hashlib.sha256(git("cat-file", "blob", blob, binary=True)).hexdigest() for blob in blobs)


def build():
    copied = []
    for project_path, asset in COPIED.items():
        if not (ROOT / SKILLS / asset).is_file():
            # A mapped asset that has not landed on this branch yet; it is recorded once it exists.
            print(f"skipped {project_path}: {SKILLS}{asset} does not exist", file=sys.stderr)
            continue
        current = hashlib.sha256((ROOT / SKILLS / asset).read_bytes()).hexdigest()
        known = committed_hashes([asset, *EARLIER.get(project_path, [])])
        copied.append({"path": project_path, "asset": asset,
                       "previous": [digest for digest in known if digest != current]})
    retired = [{"path": project_path, "shipped": committed_hashes(sources)}
               for project_path, sources in RETIRED.items()]
    return {"copied": copied, "retired": retired}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="exit 1 when the recorded file is out of date")
    args = parser.parse_args()
    text = json.dumps(build(), indent=2) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text() != text:
            print(f"out of date: {OUT.relative_to(ROOT)}; run scripts/record-shipped-versions.py", file=sys.stderr)
            sys.exit(1)
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text)
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
