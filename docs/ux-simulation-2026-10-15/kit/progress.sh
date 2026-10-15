#!/bin/sh
S="$(cd "$(dirname "$0")/.." && pwd)"
for d in taxi-A taxi-B co2-A co2-B retail-A retail-B; do
  t=$S/$d/transcript.md
  h=$(grep -c -E '^## \[.*\] HUMAN' $t 2>/dev/null); a=$(grep -c -E '^## \[.*\] AGENT' $t 2>/dev/null)
  last=$(grep '^## \[' $t 2>/dev/null | tail -1 | sed 's/^## //' | cut -c1-60)
  st=$(grep -h -o 'STATUS: [A-Z]*' $t 2>/dev/null | tail -1)
  fb=$(ls $S/$d/feedback 2>/dev/null | tr '\n' ' ')
  printf '%-9s human=%-3s agent=%-3s %-14s last=%s | fb: %s\n' $d "$h" "$a" "$st" "$last" "$fb"
done
