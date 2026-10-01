#!/bin/sh
set -e
cd "$(dirname "$0")/.."
mkdir -p downloads
tmp=$(mktemp -d)
for s in kick-start shadow-and-teach tournament-forge; do
  rm -f "downloads/$s.zip"
  find "$s" -type f ! -path "$s/examples/*" ! -name '*.png' ! -name 'README.md' | tar cf - -T - | (cd "$tmp" && tar xf -)
  find "$tmp/$s" -exec env TZ=UTC touch -t 202601010000 {} +
  (cd "$tmp" && find "$s" -type f | LC_ALL=C sort | zip -qX - -@) > "downloads/$s.zip"
done
rm -rf "$tmp"
