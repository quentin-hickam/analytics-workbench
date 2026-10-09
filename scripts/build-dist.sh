#!/usr/bin/env sh
# Rebuild dist/analytics-workbench-skills.zip from an explicit allowlist of
# tracked files. Ignored and untracked files, and any other installed skill
# such as grilling, never enter the archive.
#
# Archive layout, independent of the checkout directory's name:
#   analytics-workbench-skills/
#     awb-clean/ awb-eda/ awb-init/ awb-package/ awb-release/ awb-status/
#     CHANGELOG.md LICENSE README.md
# The skill folders sit at the top level so they can be copied as-is into a
# host's user-level skills directory. README links into .agents/skills/ are
# rewritten to match. Internal documentation (docs/, CONTEXT.md) stays in the
# repository, and README blocks between <!-- dist:exclude --> and
# <!-- /dist:exclude --> lines are dropped from the archive copy.
set -eu
root="$(cd "$(dirname "$0")/.." && pwd)"
top="analytics-workbench-skills"
out="$root/dist/$top.zip"
skills_prefix=".agents/skills/"
allowlist="
.agents/skills/awb-clean
.agents/skills/awb-eda
.agents/skills/awb-init
.agents/skills/awb-package
.agents/skills/awb-release
.agents/skills/awb-status
CHANGELOG.md
LICENSE
README.md
"
cd "$root"
for path in $allowlist; do
  [ -n "$(git ls-files -- "$path")" ] || {
    echo "allowlisted path has no tracked files: $path" >&2
    exit 1
  }
done
stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT INT TERM
# shellcheck disable=SC2086
git ls-files -- $allowlist | while IFS= read -r file; do
  case "$file" in
    grilling/* | */grilling/*)
      echo "refusing to package grilling: $file" >&2
      exit 1
      ;;
  esac
  dest="$stage/$top/${file#"$skills_prefix"}"
  mkdir -p "$(dirname "$dest")"
  cp -p "$file" "$dest"
done
sed -e '/^<!-- dist:exclude -->$/,/^<!-- \/dist:exclude -->$/d' \
  -e "s|](\.agents/skills/|](|g" README.md | cat -s > "$stage/$top/README.md"
if grep -n -e "](docs/" -e "dist:exclude" "$stage/$top/README.md" >&2; then
  echo "archive README links internal documentation or has unbalanced markers" >&2
  exit 1
fi
mkdir -p dist
rm -f "$out"
(cd "$stage" && zip -q -r -X "$out" "$top")
echo "wrote $out"
unzip -l "$out" | tail -1
