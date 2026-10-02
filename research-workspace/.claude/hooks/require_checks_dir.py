#!/usr/bin/env python3
"""PreToolUse hook for Bash: code that checks something must be saved in checks/ before it runs.

Blocks inline code (python -c, node -e, heredocs, code piped into an interpreter) and scripts
outside checks/. Allows tool commands that don't run your own code, such as python -m pip,
--version, git, curl and npm install. If the hook can't read its input, it lets the command run.
"""
import json
import os
import re
import shlex
import sys

INTERPRETERS = re.compile(r"^(python(\d+(\.\d+)?)?|node|nodejs|deno|bun|tsx|ts-node|ruby|perl|Rscript|php)$")
WRAPPERS = {("uv", "run"), ("npx", None), ("pnpm", "exec"), ("poetry", "run"), ("pipenv", "run")}
SCRIPT_FILE = re.compile(r"\.(py|js|mjs|cjs|ts|mts|rb|pl|R|php)$")
INLINE_FLAGS = {"-c", "-e", "--eval", "-p", "--print", "-r", "-E"}
SAFE_FLAGS = {"--version", "-V", "--help", "-h"}
MESSAGE = ("Save this code in checks/ first, then run it from there "
           "(for example: python3 checks/count_rows.py). Every check has to be kept.")


def segments(command):
    """Split a shell command on && || ; | while remembering whether each part reads from a pipe."""
    parts, piped = [], False
    for chunk in re.split(r"(&&|\|\||;|\|(?!\|))", command):
        if chunk in ("&&", "||", ";"):
            piped = False
        elif chunk == "|":
            piped = True
        elif chunk.strip():
            parts.append((chunk.strip(), piped))
    return parts


def strip_wrapper(tokens):
    if len(tokens) >= 2 and (tokens[0], tokens[1]) in WRAPPERS:
        return tokens[2:]
    if tokens and (tokens[0], None) in WRAPPERS:
        return [t for t in tokens[1:] if not t.startswith("-")]
    if tokens[:2] in (["deno", "run"], ["bun", "run"]):
        return [tokens[0]] + tokens[2:]
    return tokens


def violation(command, root):
    if "<<" in command and re.search(r"\b(python\d*|node|deno|bun|tsx|ruby|perl)\b[^|;&]*<<", command):
        return True
    cwd = root
    checks = os.path.realpath(os.path.join(root, "checks"))
    for part, piped in segments(command):
        try:
            tokens = shlex.split(part)
        except ValueError:
            tokens = part.split()
        while tokens and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[0]):
            tokens = tokens[1:]
        if not tokens:
            continue
        if tokens[0] == "cd" and len(tokens) > 1:
            cwd = os.path.realpath(os.path.join(cwd, os.path.expanduser(tokens[1])))
            continue
        wrapped = strip_wrapper(tokens)
        if wrapped is not tokens and wrapped and SCRIPT_FILE.search(wrapped[0]):
            wrapped = ["python3"] + wrapped
        tokens = wrapped
        if not tokens or not INTERPRETERS.match(os.path.basename(tokens[0])):
            continue
        args = tokens[1:]
        if any(a in SAFE_FLAGS for a in args) or "-m" in args:
            continue
        if any(a in INLINE_FLAGS for a in args) or "-" in args:
            return True
        script = next((a for a in args if not a.startswith("-")), None)
        if script is None:
            if piped:
                return True
            continue
        path = os.path.realpath(os.path.join(cwd, os.path.expanduser(script)))
        if not (path == checks or path.startswith(checks + os.sep)):
            return True
    return False


def main():
    try:
        event = json.load(sys.stdin)
        command = (event.get("tool_input") or {}).get("command", "")
        root = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd()
    except Exception:
        return
    if violation(command, root):
        print(MESSAGE, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
