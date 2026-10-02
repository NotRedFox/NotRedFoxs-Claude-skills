#!/bin/sh
# Builds two zips per skill: <skill>.zip for Claude Code (all frontmatter fields)
# and <skill>-claude-app.zip, which keeps only the fields the Claude app accepts.
set -e
cd "$(dirname "$0")/.."
mkdir -p downloads
tmp=$(mktemp -d)
for s in auditor claim-check kick-start problem-solve research-solving shadow-and-teach tournament-forge; do
  rm -rf "$tmp/$s"
  find "$s" -type f ! -path "$s/examples/*" ! -name '*.png' ! -name 'README.md' ! -path "*/__pycache__/*" | tar cf - -T - | (cd "$tmp" && tar xf -)
  find "$tmp/$s" -exec env TZ=UTC touch -t 202601010000 {} +
  rm -f "downloads/$s.zip" "downloads/$s-claude-app.zip"
  (cd "$tmp" && find "$s" -type f | LC_ALL=C sort | zip -qX - -@) > "downloads/$s.zip"
  awk '
    NR == 1 && /^---$/ { infm = 1; print; next }
    infm && /^---$/ { infm = 0; print; next }
    infm && /^[A-Za-z_-]+:/ { key = $0; sub(/:.*/, "", key); keep = (key ~ /^(name|description|license|compatibility|metadata|allowed-tools)$/) }
    infm { if (keep) print; next }
    { print }
  ' "$s/SKILL.md" > "$tmp/$s/SKILL.md"
  env TZ=UTC touch -t 202601010000 "$tmp/$s/SKILL.md"
  (cd "$tmp" && find "$s" -type f | LC_ALL=C sort | zip -qX - -@) > "downloads/$s-claude-app.zip"
done
rm -rf "$tmp/research-workspace"
find research-workspace -type f ! -path "research-workspace/examples/*" ! -path "*/__pycache__/*" | tar cf - -T - | (cd "$tmp" && tar xf -)
find "$tmp/research-workspace" -exec env TZ=UTC touch -t 202601010000 {} +
rm -f downloads/research-workspace.zip
(cd "$tmp" && find research-workspace -type f | LC_ALL=C sort | zip -qX - -@) > downloads/research-workspace.zip
rm -rf "$tmp"
