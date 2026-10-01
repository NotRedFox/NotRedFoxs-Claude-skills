# Claim Check

Version 1.0.0. See [CHANGELOG.md](CHANGELOG.md).

A Claude skill that checks whether your README and docs are true. Docs drift: a number was right once, a command got renamed, an example stopped running, a link moved. Claim Check lists every claim your docs make, checks each one with real evidence, and fixes the docs where they're wrong.

It checks:

| Kind of claim | How |
|---|---|
| Numbers ("15 tests", "17 areas") | Counts them, or re-runs what produced them |
| Commands and code examples | Runs them in a scratch copy and compares the output |
| Behaviour ("raises an error on empty input") | Writes the smallest script that shows it |
| File, function and option names | Checks they exist |
| Links and anchors | Fetches them |
| Comparisons and outside facts | Opens the source |
| Results from past runs | Checks them against the saved record |

Each claim gets a verdict: True, False, Partly true, Out of date, Can't check or Opinion. Nothing is marked True without evidence in the ledger.

When the docs are wrong, it changes the docs, not your code. When the docs look right and the code looks wrong, it changes neither and lists it as a possible code bug for you.

## Examples

**[This repo](examples/this-repo/2026-10-01.md).** Claim Check checked the READMEs and website of this collection: 171 claims. It found 1 false claim and 10 partly true ones, all fixed in the next update (a few with small wording changes), and listed 21 it couldn't check from where it ran, mostly paper links that were blocked. It also re-ran every recorded test result in the examples, and they all matched.

**[A test project with planted mistakes](examples/wordstat/ANSWER-KEY.md).** A small project whose README had 6 planted problems among 11 true claims. Claim Check found all 6, including a subtle one where the code was wrong and the docs were right, and marked no true claim as false. Compare [the original README](examples/wordstat/README.before.md) with [the fixed one](examples/wordstat/README.md).

## Install

### Claude app (claude.ai, desktop or phone)

1. Download [claim-check.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/claim-check.zip). Don't unzip it.
2. In Claude, open **Settings** and find **Skills**.
3. Upload the zip file.

### Claude Code

Paste this into your terminal (Mac or Linux):

```
mkdir -p ~/.claude/skills && curl -sL https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/claim-check.zip -o /tmp/claim-check.zip && unzip -oq /tmp/claim-check.zip -d ~/.claude/skills && rm /tmp/claim-check.zip
```

Then restart Claude Code. On Windows, download the zip and unzip it into `.claude\skills` in your user folder.

To update later, do the same steps again.

## Use

- "Claim check this repo"
- "Are the docs still true?"
- "Check the README before I publish"

The ledger goes in `claim-check/<date>.md` in your project.

## Limits

- It can only check what it can reach. Blocked sites and paywalled sources are marked Can't check, with what would check them.
- Measured figures (timings, token counts) can only be checked against a saved record of the run. Without one, they're marked Can't check.
- It asks before running anything that installs system packages, costs money, sends messages or changes data.

## Similar projects

- [docverity](https://glama.ai/mcp/servers/deveshagarwal/docverity): an MCP server that checks doc claims about flags, options and paths against source code.
- [doc-drift](https://dev.to/sunnydachs/your-readme-code-examples-are-silently-lying-i-built-a-cli-to-detect-documentation-drift-using-1blp): finds README code examples that no longer match the code's functions.
- [lychee](https://github.com/lycheeverse/lychee): a fast link checker.
- [pytest-markdown-docs](https://github.com/modal-labs/pytest-markdown-docs): runs the Python code blocks in your Markdown as tests.

Claim Check covers what these don't: numbers, behaviour, comparisons, outside facts and results from past runs. It also fixes the docs.
