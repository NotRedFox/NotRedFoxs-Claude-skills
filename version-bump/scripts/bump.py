#!/usr/bin/env python3
"""Raises the four-part version in VERSION and adds a CHANGELOG.md entry.

  python3 bump.py major "Renamed the config file"    1.4.2.7 -> 2.0.0.0
  python3 bump.py minor "Added CSV export"           1.4.2.7 -> 1.5.0.0
  python3 bump.py patch "Fixed totals on empty carts" 1.4.2.7 -> 1.4.3.0
  python3 bump.py tweak "Fixed typos in the README"  1.4.2.7 -> 1.4.2.8
  python3 bump.py show
  python3 bump.py init 0.1.0.0
"""
import os
import re
import subprocess
import sys
from datetime import date

LEVELS = ["major", "minor", "patch", "tweak"]


def project_root():
    root = os.environ.get("CLAUDE_PROJECT_DIR")
    if root:
        return root
    found = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    return found or os.getcwd()


def parse(text):
    """Reads 1 to 4 numbers separated by dots and pads to four, so 1.2.3 becomes 1.2.3.0."""
    m = re.fullmatch(r"v?(\d+(?:\.\d+){0,3})", text.strip())
    if not m:
        raise ValueError(f"'{text.strip()}' isn't a version like 1.2.3.4")
    parts = [int(p) for p in m.group(1).split(".")]
    return parts + [0] * (4 - len(parts))


def show(parts):
    return ".".join(str(p) for p in parts)


def raise_level(parts, level):
    i = LEVELS.index(level)
    return parts[:i] + [parts[i] + 1] + [0] * (3 - i)


def add_changelog(root, version, note):
    path = os.path.join(root, "CHANGELOG.md")
    entry = f"## {version} ({date.today()})\n\n- {note}\n"
    old = open(path, encoding="utf-8").read() if os.path.exists(path) else "# Changelog\n"
    head, sep, rest = old.partition("\n## ")
    if sep:
        new = head.rstrip("\n") + "\n\n" + entry + "\n## " + rest
    else:
        new = old.rstrip("\n") + "\n\n" + entry
    with open(path, "w", encoding="utf-8") as f:
        f.write(new)


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    root = project_root()
    path = os.path.join(root, "VERSION")
    command = args[0].lower()

    if command == "init":
        if os.path.exists(path):
            sys.exit(f"VERSION already exists: {open(path).read().strip()}")
        start = show(parse(args[1] if len(args) > 1 else "0.1.0.0"))
        with open(path, "w") as f:
            f.write(start + "\n")
        print(f"Created VERSION at {start}")
        return

    if not os.path.exists(path):
        sys.exit("No VERSION file. Run: python3 bump.py init 0.1.0.0")
    try:
        current = parse(open(path).read())
    except ValueError as e:
        sys.exit(f"VERSION is broken: {e}")

    if command == "show":
        print(show(current))
        return
    if command not in LEVELS:
        sys.exit(f"Level must be one of: {', '.join(LEVELS)}")
    note = " ".join(args[1:]).strip()
    if not note:
        sys.exit('Say what changed, for example: python3 bump.py patch "Fixed totals on empty carts"')

    new = show(raise_level(current, command))
    with open(path, "w") as f:
        f.write(new + "\n")
    add_changelog(root, new, note)
    print(f"{show(current)} -> {new} ({command})")


if __name__ == "__main__":
    main()
