#!/usr/bin/env python3
"""Stop hook: before Claude finishes, sources must be verified and written up.

1. Every source file in sources/ needs a link and a "Verified:" line from the verifier.
2. reports/ needs a report newer than the newest source.
If either is missing, Claude is asked to fix it before stopping. Runs once per stop, so it can't loop.
"""
import glob
import json
import os
import re
import sys

SKIP = {"brief.md", "readme.md", ".gitkeep"}


def block(reason):
    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        return
    if event.get("stop_hook_active"):
        return
    root = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or "."
    sources = [p for p in glob.glob(os.path.join(root, "sources", "**", "*"), recursive=True)
               if os.path.isfile(p) and os.path.basename(p).lower() not in SKIP]
    if not sources:
        return
    unverified, no_link = [], []
    for path in sources:
        text = open(path, encoding="utf-8", errors="replace").read()
        rel = os.path.relpath(path, root)
        if not re.search(r"https?://\S+", text):
            no_link.append(rel)
        if not re.search(r"(?mi)^\s*verified:", text):
            unverified.append(rel)
    if no_link:
        block("These source files have no link, so they can't be checked: " + ", ".join(no_link)
              + ". Add the link, or delete the file if it came from memory.")
    if unverified:
        block("Run the verifier on these sources before finishing: " + ", ".join(unverified)
              + ". Each needs a line starting 'Verified:'.")
    newest_source = max(os.path.getmtime(p) for p in sources)
    reports = glob.glob(os.path.join(root, "reports", "*.md"))
    if not reports or newest_source > max(os.path.getmtime(p) for p in reports):
        block("Sources changed since the last report. Write or update reports/<topic>.md: what was found, "
              "why it matters, ranked things to try with a first test each, and what was dropped. "
              "Cite only sources marked 'Verified: yes' or 'Verified: corrected'. Then add one line to logs/notes.log.")


if __name__ == "__main__":
    main()
