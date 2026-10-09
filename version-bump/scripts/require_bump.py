#!/usr/bin/env python3
"""PreToolUse hook for Bash: a git commit must raise the version in VERSION.

Only acts in projects that have a VERSION file. Lets the commit through when VERSION is
higher than in the last commit and will be part of this commit, when the message has
[no bump], and for --amend. If the hook can't read its input, it lets the command run.
"""
import json
import os
import re
import shlex
import subprocess
import sys

LEVELS = """Raise exactly one number, the highest that applies:
  major  1.0.0.0  breaks how people use it: removed or renamed commands, options, files or settings, or data that needs migrating
  minor  0.1.0.0  something new people can use, with nothing old broken
  patch  0.0.1.0  fixes something that worked wrongly
  tweak  0.0.0.1  no change in behaviour: docs, comments, typos, formatting, tests only, refactors"""


def git(root, *args):
    return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True)


def parse(text):
    m = re.fullmatch(r"v?(\d+(?:\.\d+){0,3})", (text or "").strip())
    if not m:
        return None
    parts = [int(p) for p in m.group(1).split(".")]
    return parts + [0] * (4 - len(parts))


def runs_bump(part):
    """Whether this part of the command runs bump.py with a level, which raises VERSION before the commit."""
    try:
        tokens = shlex.split(part)
    except ValueError:
        tokens = part.split()
    for i, t in enumerate(tokens[:-1]):
        if os.path.basename(t) == "bump.py" and tokens[i + 1] in ("major", "minor", "patch", "tweak"):
            return True
    return False


def segments(command):
    """Splits a command into the parts the shell runs one after another, skipping heredoc text."""
    lines, end = [], None
    for line in command.split("\n"):
        if end is not None:
            if line.strip() == end:
                end = None
            continue
        m = re.search(r"<<-?\s*['\"]?(\w+)['\"]?", line)
        if m:
            end = m.group(1)
        lines.append(line)
    return [p.strip() for p in re.split(r"&&|\|\||;|\||\n", "\n".join(lines)) if p.strip()]


def git_args(part):
    """Returns the arguments after 'git' with global options such as -C dir removed, or None."""
    try:
        tokens = shlex.split(part)
    except ValueError:
        tokens = part.split()
    while tokens and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[0]):
        tokens = tokens[1:]
    if not tokens or os.path.basename(tokens[0]) != "git":
        return None
    rest = tokens[1:]
    while rest and rest[0].startswith("-"):
        rest = rest[2:] if rest[0] in ("-C", "-c") else rest[1:]
    return rest


def adds_version(args):
    """Whether a 'git add' or a 'git commit' with -a will include a changed VERSION."""
    if args[0] == "add":
        files = [a for a in args[1:] if not a.startswith("-")]
        flags = [a for a in args[1:] if a.startswith("-")]
        return bool({"-A", "--all", "-u", "--update"} & set(flags)) or any(
            f in (".", "VERSION", "./VERSION", ":/") for f in files)
    if args[0] == "commit":
        return "--all" in args or any(re.fullmatch(r"-[A-Za-z]*a[A-Za-z]*", a) for a in args[1:])
    return False


def main():
    try:
        event = json.load(sys.stdin)
        command = (event.get("tool_input") or {}).get("command", "")
        root = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd()
    except Exception:
        return
    pieces = segments(command)
    parsed = [git_args(p) for p in pieces]
    at = next((i for i, a in enumerate(parsed) if a and a[0] == "commit"), None)
    commit = parsed[at] if at is not None else None
    if commit is None or "--amend" in commit or "[no bump]" in command:
        return
    path = os.path.join(root, "VERSION")
    if not os.path.exists(path):
        return

    current = parse(open(path).read())
    head = git(root, "show", "HEAD:VERSION")
    before = parse(head.stdout) if head.returncode == 0 else None
    staged = git(root, "show", ":VERSION")
    in_index = parse(staged.stdout) if staged.returncode == 0 else None

    adds = any(a and adds_version(a) for a in parsed[:at]) or adds_version(commit)
    if any(runs_bump(p) for p in pieces[:at]) and adds:
        return
    will_include = in_index == current or adds
    if current is not None and will_include and (before is None or current > before):
        return

    shown = ".".join(map(str, before or current or [0, 0, 0, 0]))
    if current is not None and before is not None and current > before and not will_include:
        reason = "VERSION was raised but isn't staged. Run git add VERSION CHANGELOG.md, then commit again."
    else:
        reason = (f"This commit doesn't raise the version (now {shown}). Look at what this commit changes, then run:\n"
                  f"  python3 .claude/hooks/bump.py <major|minor|patch|tweak> \"what changed, in one line\"\n"
                  f"then git add VERSION CHANGELOG.md and commit again.\n{LEVELS}\n"
                  f"Say which level you picked and why.")
    print(reason, file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
