#!/usr/bin/env python3
"""Writes BRIEF.md: a short map of a git repo with no code bodies, for reading or asking about on your phone."""
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import date

MAX_CHARS = 40_000
SKIP_DIRS = {"node_modules", "dist", "build", ".venv", "venv", "__pycache__", "downloads"}
SECRET_FILES = re.compile(r"(^|/)(\.env[^/]*|.*\.(pem|key|p12)|id_rsa[^/]*|credentials[^/]*|secrets?\.[^/]*)$", re.I)
SECRET_TEXT = re.compile(r"(sk-[A-Za-z0-9_-]{16,}|AIza[0-9A-Za-z_-]{30,}|gh[pousr]_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,})")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
CODE = {".py", ".js", ".mjs", ".ts", ".tsx", ".jsx", ".sh", ".go", ".rs", ".java", ".rb", ".swift", ".kt", ".c", ".cpp", ".h", ".cs", ".php"}
DEFS = [
    re.compile(r"^\s*(?:async\s+)?def\s+(\w+)\s*\(([^)]*)\)"),
    re.compile(r"^\s*class\s+(\w+)"),
    re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\*?\s+(\w+)\s*\(([^)]*)\)"),
    re.compile(r"^\s*(?:export\s+)?const\s+(\w+)\s*(?::[^=]+)?=\s*(?:async\s*)?\(([^)]*)\)\s*=>"),
    re.compile(r"^\s*(?:export\s+)?(?:interface|type)\s+(\w+)"),
    re.compile(r"^\s*func\s+(?:\([^)]*\)\s*)?(\w+)\s*\(([^)]*)\)"),
    re.compile(r"^\s*(?:pub\s+)?fn\s+(\w+)\s*\(([^)]*)\)"),
    re.compile(r"^\s*(\w+)\s*\(\)\s*\{"),
]


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout.strip()


def clean(text):
    return EMAIL.sub("[email]", SECRET_TEXT.sub("[secret]", text))


def purpose(lines, ext):
    """The file's first comment or docstring line, which usually says what it is for."""
    for line in lines[:15]:
        s = line.strip()
        if not s or s.startswith("#!") or s.startswith("import ") or s.startswith("from "):
            continue
        m = re.match(r'^(?:#|//|/\*+|\*|"""|\'\'\'|--)\s*(.+?)\s*(?:\*/|"""|\'\'\')?$', s)
        if m and len(m.group(1)) > 3:
            return m.group(1)[:140].rstrip(".,;: ")
        if ext not in {".py", ".sh"}:
            break
    return ""


def describe(path):
    ext = os.path.splitext(path)[1].lower()
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except (UnicodeDecodeError, OSError):
        return None
    if ext == ".md":
        heads = [l.lstrip("# ").strip() for l in lines if re.match(r"^#{1,2} ", l)]
        return f"{len(lines)} lines. Sections: " + ", ".join(heads[:8]) if heads else f"{len(lines)} lines"
    if ext not in CODE:
        return f"{len(lines)} lines"
    names = []
    for line in lines:
        for d in DEFS:
            m = d.match(line)
            if m:
                args = m.group(2).strip() if m.lastindex and m.lastindex >= 2 else None
                names.append(f"{m.group(1)}({args[:40]})" if args is not None else m.group(1))
                break
    out = f"{len(lines)} lines"
    p = purpose(lines, ext)
    if p:
        out += f". {p}"
    if names:
        out += ". Defines: " + ", ".join(names[:12]) + (f" and {len(names) - 12} more" if len(names) > 12 else "")
    return out


def main():
    root = git("rev-parse", "--show-toplevel")
    if not root:
        sys.exit("Run this inside a git repo.")
    os.chdir(root)
    files = [f for f in git("ls-files").splitlines()
             if not SECRET_FILES.search(f) and not set(f.split("/")[:-1]) & SKIP_DIRS and f != "BRIEF.md"]

    out = [f"# Brief: {os.path.basename(root)}", "",
           f"Made {date.today()} on branch {git('branch', '--show-current') or '(none)'}. "
           "This is a map of the repo with no code bodies: file purposes, function names, recent commits and TODOs.", ""]

    out += ["## Recent commits", ""]
    out += [f"- {clean(l)}" for l in git("log", "-15", "--date=short", "--format=%ad %s").splitlines()] or ["- none"]

    count = int(git("rev-list", "--count", "HEAD") or 0)
    changed = git("diff", "--stat=100", f"HEAD~{min(5, count - 1)}", "HEAD") if count > 1 else ""
    rows = [re.sub(r"\s+", " ", l.strip()) for l in changed.splitlines()[:-1] if not set(l.split("|")[0].strip().split("/")[:-1]) & SKIP_DIRS]
    if rows:
        out += ["", "## Files changed in the last 5 commits", ""] + [f"- {r}" for r in rows[:30]]

    dirty = git("status", "--short")
    out += ["", "## Not committed yet", ""]
    out += [f"- {l}" for l in dirty.splitlines()[:30]] or ["- nothing"]

    out += ["", "## Files", ""]
    by_dir = defaultdict(list)
    for f in files:
        by_dir[os.path.dirname(f) or "."].append(f)
    for d in sorted(by_dir):
        out += [f"### {d}", ""]
        for f in by_dir[d]:
            info = describe(f)
            out.append(f"- `{os.path.basename(f)}`" + (f": {clean(info)}" if info else " (binary)"))
        out.append("")

    todos = []
    for f in files:
        if os.path.splitext(f)[1].lower() not in CODE:
            continue
        try:
            for n, line in enumerate(open(f, encoding="utf-8"), 1):
                m = re.search(r"\b(TODO|FIXME|HACK|XXX)\b[:\s]*(.*)", line)
                if m:
                    todos.append(f"- {f}:{n} {m.group(1)} {clean(m.group(2).strip())[:120]}")
        except (UnicodeDecodeError, OSError):
            pass
    out += ["## TODOs", ""] + (todos[:40] or ["- none"])

    text = "\n".join(out) + "\n"
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + "\n\n(Cut off at the size limit.)\n"
    with open("BRIEF.md", "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Wrote BRIEF.md: {len(text):,} characters, about {len(text) // 4:,} tokens.")


if __name__ == "__main__":
    main()
