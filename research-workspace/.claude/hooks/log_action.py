#!/usr/bin/env python3
"""PostToolUse and PostToolUseFailure hook: append a one-line record of every tool call,
including failed ones, to logs/actions.log.

Secrets that appear in commands (API keys, tokens, passwords) are replaced with <SECRET>.
The hook never blocks or fails the tool call: any error is ignored.
"""
import datetime
import json
import os
import re
import sys

SECRET_PATTERNS = [
    r"\b(?:sk|pk|rk)-[A-Za-z0-9_-]{10,}",
    r"\bgh[pousr]_[A-Za-z0-9]{20,}",
    r"\bgithub_pat_[A-Za-z0-9_]{20,}",
    r"\bxox[abpr]-[A-Za-z0-9-]{10,}",
    r"\bAKIA[0-9A-Z]{16}\b",
    r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{8,}",
    r"(?i)\b(?:api[_-]?key|access[_-]?token|token|secret|password|passwd)\s*[=:]\s*['\"]?[^\s'\"&]{4,}",
]


def redact(text):
    for pattern in SECRET_PATTERNS:
        text = re.sub(pattern, "<SECRET>", text)
    return text


def main():
    event = json.load(sys.stdin)
    root = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or "."
    args = event.get("tool_input") or {}
    detail = args.get("command") or args.get("url") or args.get("query") or args.get("file_path") or ""
    detail = redact(" ".join(str(detail).split()))[:300]
    who = event.get("agent_type")
    label = f"{event.get('tool_name', '?')}" + (f" ({who})" if who else "")
    if event.get("hook_event_name") == "PostToolUseFailure":
        label += " FAILED"
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs(os.path.join(root, "logs"), exist_ok=True)
    with open(os.path.join(root, "logs", "actions.log"), "a", encoding="utf-8") as f:
        f.write(f"{stamp} {label}: {detail}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
