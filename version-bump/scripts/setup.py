#!/usr/bin/env python3
"""Installs the version hook in a project: copies bump.py and require_bump.py to
.claude/hooks/ and adds the hook to .claude/settings.json, keeping what's already there."""
import json
import os
import shutil
import sys

HOOK = 'python3 "${CLAUDE_PROJECT_DIR}/.claude/hooks/require_bump.py"'


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    here = os.path.dirname(os.path.abspath(__file__))
    hooks = os.path.join(root, ".claude", "hooks")
    os.makedirs(hooks, exist_ok=True)
    for name in ("bump.py", "require_bump.py"):
        shutil.copy(os.path.join(here, name), os.path.join(hooks, name))

    path = os.path.join(root, ".claude", "settings.json")
    settings = {}
    if os.path.exists(path):
        try:
            settings = json.load(open(path))
        except json.JSONDecodeError as e:
            sys.exit(f"{path} isn't valid JSON ({e}). Fix it, then run this again.")
    groups = settings.setdefault("hooks", {}).setdefault("PreToolUse", [])
    if any(h.get("command") == HOOK for g in groups for h in g.get("hooks", [])):
        print("Hook already installed. Updated the scripts in .claude/hooks/.")
        return
    groups.append({"matcher": "Bash", "hooks": [{"type": "command", "command": HOOK}]})
    with open(path, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")
    print("Installed: .claude/hooks/bump.py, .claude/hooks/require_bump.py and the hook in .claude/settings.json")


if __name__ == "__main__":
    main()
