#!/usr/bin/env sh
# Rebuild dist/analytics-workbench-skills.zip from the working tree.
set -eu
root="$(cd "$(dirname "$0")/.." && pwd)"
out="$root/dist/analytics-workbench-skills.zip"
mkdir -p "$root/dist"
rm -f "$out"
cd "$root/.."
zip -qr "$out" "$(basename "$root")" \
  -x "*/.git/*" "*/dist/*" "*/.DS_Store" "*/__pycache__/*" "*/.env" "*/.env.*"
echo "wrote $out"
unzip -l "$out" | tail -1
