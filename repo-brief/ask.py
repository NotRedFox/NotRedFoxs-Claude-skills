#!/usr/bin/env python3
"""Asks Gemini a question about your repo using only BRIEF.md, never your code."""
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
RULES = ("You answer questions about a software project using only the brief below. "
         "The brief has file purposes, function names, commits and TODOs, but no code bodies. "
         "If the answer needs code that isn't in the brief, say so and say which file to look at. "
         "Keep answers short and plain.")


def main():
    if len(sys.argv) < 2:
        sys.exit('Usage: python3 ask.py "what changed this week?"   (add --dry-run to see what would be sent)')
    dry = "--dry-run" in sys.argv
    question = " ".join(a for a in sys.argv[1:] if a != "--dry-run")
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or "."
    path = os.path.join(root, "BRIEF.md")
    if not os.path.exists(path):
        sys.exit("No BRIEF.md yet. Run brief.py first.")
    brief = open(path, encoding="utf-8").read()
    body = {"systemInstruction": {"parts": [{"text": RULES}]},
            "contents": [{"role": "user", "parts": [{"text": f"{brief}\n\nQuestion: {question}"}]}]}
    if dry:
        print(f"Would send {len(brief):,} characters of BRIEF.md and your question. Nothing else.")
        return
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("Set GEMINI_API_KEY first. Get a key at https://aistudio.google.com/apikey")
    print("Note: on Gemini's free tier, Google may use what you send to improve its products, and people may read it.\n", file=sys.stderr)
    req = urllib.request.Request(API.format(model=os.environ.get("GEMINI_MODEL", "gemini-flash-latest")),
                                 data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Gemini returned {e.code}: {e.read().decode()[:500]}")
    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    print("".join(p.get("text", "") for p in parts).strip() or json.dumps(data)[:500])
    usage = data.get("usageMetadata", {})
    if usage:
        print(f"\n({usage.get('promptTokenCount', '?')} tokens in, {usage.get('candidatesTokenCount', '?')} out)", file=sys.stderr)


if __name__ == "__main__":
    main()
