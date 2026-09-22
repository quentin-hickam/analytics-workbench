#!/usr/bin/env sh
# Rebuild dist/analytics-workbench-skills.zip from an explicit allowlist of
# tracked files. Ignored and untracked files, and any other installed skill
# such as grilling, never enter the archive.
set -eu
root="$(cd "$(dirname "$0")/.." && pwd)"
name="$(basename "$root")"
out="$root/dist/analytics-workbench-skills.zip"
allowlist="
.agents/skills/workbench-init
.agents/skills/workbench-package
docs
scripts
.gitignore
CONTEXT.md
README.md
"
cd "$root"
for path in $allowlist; do
  [ -e "$path" ] || { echo "missing allowlisted path: $path" >&2; exit 1; }
done
mkdir -p dist
rm -f "$out"
# shellcheck disable=SC2086
git ls-files -- $allowlist | sed "s|^|$name/|" > dist/.manifest
(cd .. && zip -q "$out" -@ < "$root/dist/.manifest")
rm -f dist/.manifest
echo "wrote $out"
unzip -l "$out" | tail -1
