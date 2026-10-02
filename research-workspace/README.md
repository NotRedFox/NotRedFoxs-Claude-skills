# Research Workspace

A ready-made Claude Code project folder for research, as an alternative to the [research-solving](../research-solving/) skill. Everything lives in one folder, nothing gets added to your normal projects, and hooks make sure the rules are followed instead of only asking.

## What's inside

| Path | What it does |
|---|---|
| `CLAUDE.md` | Short rules: the folder layout, how a research run goes, never cite from memory |
| `.claude/agents/code-scout.md` | Finds open-source projects and saves what it reads to `sources/` |
| `.claude/agents/paper-scout.md` | Finds papers and datasets, saves the supporting sentences |
| `.claude/agents/sideways-scout.md` | Finds ideas from unrelated fields and rates them High, Medium, Low or Hype |
| `.claude/agents/verifier.md` | Re-opens each source and checks the numbers before anything goes in a report |
| `.claude/hooks/log_action.py` | Logs every command, search, fetch and file write as one line, including the ones that fail, in `logs/actions.log`, with API keys, tokens and passwords replaced by `<SECRET>` |
| `.claude/hooks/require_checks_dir.py` | Blocks code that isn't saved in `checks/` first (inline `python -c`, `node -e`, heredocs, piped code, `uv run`, `npx tsx`, `deno run` and scripts elsewhere), so every check is kept. Tools like `pip`, `git` and `curl` aren't affected. |
| `.claude/hooks/require_report.py` | Won't let Claude finish until every source has a link and has been checked by the verifier, and the report is newer than the sources |
| `.claude/hooks/test_hooks.py` | Tests for the three hooks. Run `python3 .claude/hooks/test_hooks.py` |
| `sources/`, `checks/`, `reports/`, `logs/` | Where the work goes |

## Use

1. Download [research-workspace.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/research-workspace.zip), unzip it, and rename the folder if you like.
2. Open a terminal in it and start Claude Code (`claude`).
3. Ask a research question, for example "research how to detect when a page's main content has loaded, for a browser extension".

Claude starts the three scouts in parallel, then the verifier, then writes the report. You'll find the sources it read in `sources/`, every script it ran in `checks/`, the step-by-step log in `logs/`, and the write-up in `reports/`.

Needs Claude Code and `python3` (the hooks are small Python scripts).

## Test run

Tested with real Claude Code sessions, and the hooks have their own tests (`python3 .claude/hooks/test_hooks.py`, 13 test groups covering about 35 cases). In the live sessions:

- **Unsaved code blocked:** asked to run `python3 -c 'print(6*7)'` with no CLAUDE.md to warn it, Claude was blocked, saved the script as `checks/multiply.py`, ran it from there, and said why.
- **Verifier required:** with a source saved but not verified, Claude was stopped from finishing until it was.
- **Everything logged, secrets hidden:** a command containing a fake API key was logged with the key replaced by `<SECRET>`, and a command that failed was logged and marked FAILED.

[examples/page-load-detection](examples/page-load-detection/reports/page-load-detection.md) is a full research run on "how to detect when a web page's main content has finished loading, for a browser extension". It cost $0.75.

- The three scouts saved 7 sources to [sources/](examples/page-load-detection/sources/page-load-detection/).
- The verifier confirmed 1 exactly, corrected 2 and couldn't open 4. Each source file ends with its `Verified:` line.
- The [report](examples/page-load-detection/reports/page-load-detection.md) rests only on the 3 confirmed sources, and says so at the top.
- The [action log](examples/page-load-detection/logs/actions.log) shows every step, including 13 failed attempts, mostly sites that were blocked where it ran. Long sandbox paths in it were shortened for readability.

## Credit

The idea came from a commenter on Reddit who runs a similar setup at work: a separate project for research, specialised agents, and hooks that force the logging.
