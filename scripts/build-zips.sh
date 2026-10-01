#!/bin/sh
set -e
cd "$(dirname "$0")/.."
mkdir -p downloads
for s in kick-start shadow-and-teach tournament-forge; do
  rm -f "downloads/$s.zip"
  find "$s" -exec env TZ=UTC touch -t 202601010000 {} +
  find "$s" -type f ! -path "$s/examples/*" ! -name '*.png' ! -name 'README.md' | LC_ALL=C sort | zip -qX "downloads/$s.zip" -@
done
