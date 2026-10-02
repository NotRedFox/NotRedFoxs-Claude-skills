#!/usr/bin/env python3
"""Tests for the workspace hooks. Run: python3 .claude/hooks/test_hooks.py"""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def run(hook, payload, root):
    data = payload if isinstance(payload, str) else json.dumps(payload)
    env = dict(os.environ, CLAUDE_PROJECT_DIR=root)
    return subprocess.run([sys.executable, os.path.join(HERE, hook)], input=data,
                          capture_output=True, text=True, env=env)


class ChecksDir(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.root, "checks"))

    def blocked(self, command):
        return run("require_checks_dir.py", {"tool_input": {"command": command}}, self.root).returncode == 2

    def test_blocks_inline_and_outside_code(self):
        for command in [
            'python3 -c "print(1)"',
            "node -e 1",
            "python3 /tmp/a.py",
            "python3 scratch.py",
            "python3 checks/../evil.py",
            'python3 -c "1" > checks/out.txt',
            "echo 'print(1)' | python3",
            "echo hi | python3 -",
            "python3 - <<'X'\nprint(1)\nX",
            "uv run scratch.py",
            "npx tsx scratch.ts",
            "deno run scratch.ts",
            "FOO=1 python3 scratch.py",
            "cd /tmp && python3 checks/a.py",
        ]:
            with self.subTest(command=command):
                self.assertTrue(self.blocked(command))

    def test_allows_saved_checks_and_tools(self):
        for command in [
            "python3 checks/count.py",
            "python3 checks/count.py --rows=3",
            "cd checks && python3 count.py",
            "uv run checks/count.py",
            "node checks/count.mjs",
            "bash checks/fetch.sh",
            "python3 -m pip install requests",
            "python3 -m json.tool data.json",
            "python3 --version",
            "git clone --depth 1 https://github.com/a/b",
            "curl -s https://example.com | head",
            "npm install",
            "FOO=1 python3 checks/count.py",
        ]:
            with self.subTest(command=command):
                self.assertFalse(self.blocked(command))

    def test_bad_input_does_not_block(self):
        self.assertEqual(run("require_checks_dir.py", "not json", self.root).returncode, 0)


class LogAction(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()

    def log(self):
        with open(os.path.join(self.root, "logs", "actions.log")) as f:
            return f.read()

    def test_one_line_per_call(self):
        run("log_action.py", {"tool_name": "Bash", "tool_input": {"command": "ls\n-la"}}, self.root)
        run("log_action.py", {"tool_name": "WebFetch", "tool_input": {"url": "https://a.b"}}, self.root)
        lines = self.log().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertIn("Bash: ls -la", lines[0])
        self.assertIn("WebFetch: https://a.b", lines[1])

    def test_failed_calls_are_marked(self):
        run("log_action.py", {"hook_event_name": "PostToolUseFailure", "tool_name": "Bash",
                              "tool_input": {"command": "false"}}, self.root)
        self.assertIn("Bash FAILED: false", self.log())

    def test_secrets_are_redacted(self):
        secrets = ["sk-live-abc123def456ghi789", "ghp_" + "a" * 30, "AKIAABCDEFGHIJKLMNOP",
                   "hunter2pass", "eyJhbGciOiJIUzI1NiJ9tok"]
        command = (f'curl -H "Authorization: Bearer {secrets[4]}" -d key={secrets[0]} '
                   f"https://x?token={secrets[1]} && export AWS={secrets[2]} password={secrets[3]}")
        run("log_action.py", {"tool_name": "Bash", "tool_input": {"command": command}}, self.root)
        text = self.log()
        for secret in secrets:
            self.assertNotIn(secret, text)
        self.assertIn("<SECRET>", text)

    def test_bad_input_is_ignored(self):
        self.assertEqual(run("log_action.py", "not json", self.root).returncode, 0)


class Report(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.src = os.path.join(self.root, "sources", "topic")
        os.makedirs(self.src)
        os.makedirs(os.path.join(self.root, "reports"))

    def write(self, rel, text):
        with open(os.path.join(self.root, rel), "w") as f:
            f.write(text)

    def decision(self, payload=None):
        out = run("require_report.py", payload or {}, self.root).stdout.strip()
        return json.loads(out)["reason"] if out else None

    def test_nothing_to_do_without_sources(self):
        self.write("sources/topic/BRIEF.md", "brief")
        self.assertIsNone(self.decision())

    def test_source_without_link_blocks(self):
        self.write("sources/topic/a.md", "claim from memory\nVerified: yes")
        self.assertIn("no link", self.decision())

    def test_unverified_source_blocks(self):
        self.write("sources/topic/a.md", "Link: https://a.b")
        self.assertIn("verifier", self.decision())

    def test_missing_or_old_report_blocks(self):
        self.write("reports/topic.md", "old")
        time.sleep(1.1)
        self.write("sources/topic/a.md", "Link: https://a.b\nVerified: yes")
        self.assertIn("report", self.decision())

    def test_verified_and_reported_passes(self):
        self.write("sources/topic/a.md", "Link: https://a.b\nVerified: corrected (date)")
        time.sleep(1.1)
        self.write("reports/topic.md", "report")
        self.assertIsNone(self.decision())

    def test_never_blocks_twice_in_a_row(self):
        self.write("sources/topic/a.md", "Link: https://a.b")
        self.assertIsNone(self.decision({"stop_hook_active": True}))


if __name__ == "__main__":
    unittest.main(verbosity=1)
