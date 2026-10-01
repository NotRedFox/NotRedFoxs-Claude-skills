# Shadow and Teach

Version 1.0.1. See [CHANGELOG.md](CHANGELOG.md).

An Agent Skill (`SKILL.md`) that makes an AI coding agent teach you while it works, instead of changing your code in silence.

It does three things:

- **Map a repo.** Point it at any codebase and it writes `learn/map.html`: the repo split into areas on a clickable map, with request traces, code walkthroughs and practice for each area. Big repos get layered maps. Areas open into their own maps, and anything not mapped yet can be filled in later by asking "go deeper on <area>".
- **Replay agent work.** Give it a prompt to run, or point it at something already done (earlier in the chat, a commit, a PR, a Claude Code session log) and it writes a step-by-step replay page. You see each command, its real output and each diff, and you're asked to guess before the result is shown.
- **Shadow you while it works.** Before each action it says what it's about to do and why. It stops before anything hard to undo, then explains the result, keeping a running log in `learn/lessons.md`.

![A map of Flask's own source code](https://raw.githubusercontent.com/NotRedFox/NotRedFoxs-Claude-skills/main/shadow-and-teach/assets/example-map.png)

![A replay of the agent adding a username rule](https://raw.githubusercontent.com/NotRedFox/NotRedFoxs-Claude-skills/main/shadow-and-teach/assets/example-replay.png)

> Click a link in [Examples](#examples) to open a page in your browser.

The teaching choices come from learning-science research. `RESEARCH.md` has the short version and the end of `SKILL.md` has the sources.

## Examples

Click a name to open it in your browser. They're all made by the skill.

| Page | What it is |
|---|---|
| [flaskr-map](https://notredfox.github.io/NotRedFoxs-Claude-skills/shadow-and-teach/examples/flaskr-map.html) | Flask's small tutorial app, six areas |
| [flask-internals-map](https://notredfox.github.io/NotRedFoxs-Claude-skills/shadow-and-teach/examples/flask-internals-map.html) | Flask's own source code: 8 areas, two of them opening into their own maps, 17 areas in total. Behaviour claims were checked by running the 494-test suite and about 70 extra checks. |
| [username-rule-replay](https://notredfox.github.io/NotRedFoxs-Claude-skills/shadow-and-teach/examples/username-rule-replay.html) | A replay of the agent adding a username rule to Flaskr, including the test it broke and how it decided to fix it |

## Install

### Claude app (claude.ai, desktop or phone)

1. Download [shadow-and-teach.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/shadow-and-teach.zip). Don't unzip it.
2. In Claude, open **Settings** and find **Skills**.
3. Upload the zip file.

### Claude Code

Paste this into your terminal (Mac or Linux):

```
mkdir -p ~/.claude/skills && curl -sL https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/shadow-and-teach.zip -o /tmp/shadow-and-teach.zip && unzip -oq /tmp/shadow-and-teach.zip -d ~/.claude/skills && rm /tmp/shadow-and-teach.zip
```

Then restart Claude Code. On Windows, download the zip and unzip it into `.claude\skills` in your user folder.

To update later, do the same steps again.

## Use

- "Teach me this repo"
- "Go deeper on routing"
- "Replay what you just did", "Replay commit 3f2a1c9", "Explain this PR as a replay"
- Any task with "teach me as you go"

While it's working you can say `pause`, `hint`, `let me try`, `quiz me`, `recap`, `level up`, `level down` or `skip teaching`.

## Files

| Path | What it is |
|---|---|
| `SKILL.md` | The skill |
| `assets/learning-map.html` | The map page. The agent swaps in the `REPO` data between the marked comments. |
| `assets/session-replay.html` | The replay page. The agent swaps in the `SESSION` data. |
| `examples/` | The three pages above |
| `RESEARCH.md` | Which finding shaped which feature |
| `CHANGELOG.md` | Version history |

## Limits

- A page is only as accurate as what the agent read and ran. Each area lists which files were actually read, and the skill tells the agent to check behaviour claims by running them. Still, read it like notes from a colleague, not a textbook.
- Mapping a large repo takes a while and uses a fair amount of the agent's budget. The Flask internals example took about 20 minutes. That's why deeper levels are built on request.
- Progress on the pages is saved in your browser only.

## Ideas

- A Claude Code hook that records every tool call automatically, so replays don't depend on the agent's memory of what it did.
- Exporting page progress to a file the agent can read, so it knows what you've already learned.
