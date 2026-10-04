# Token Meter

Version 0.2.0. See [CHANGELOG.md](CHANGELOG.md).

A Claude Code mod that shows how fast Claude is writing, live, in the status line:

```
~95 tok/s | 1.2k tok/min | 8.4k tok/hr
```

- **tok/s**: speed of the current reply, timed from when the request is sent. While Claude is still writing it starts with `~`, an estimate from the text so far. When the reply ends it switches to the exact number from the API.
- **tok/min**: tokens Claude wrote in the last 60 seconds.
- **tok/hr**: tokens Claude wrote in the last hour.

It counts output tokens only (what Claude writes, including thinking and tool calls), not what it reads.

## What's a mod?

A mod is a plugin with code that runs inside Claude Code, so it can draw in the interface and react to events like tool calls and replies. Skills are instructions Claude reads; mods change Claude Code itself. They need Claude Code v2.1.287 or later. See [Anthropic's mods overview](https://code.claude.com/docs/en/plugins/mods/overview).

## How the live estimate works

The API only reports the token count when a reply ends, so while Claude writes, the meter counts characters instead. It starts at 3 characters per token, measured on Claude's replies, then learns the real ratio from each finished reply in your session. When Claude's thinking is hidden it costs tokens but shows no text, so the meter skips the live figure for that reply and shows the exact one when it ends.

## Tested

Installed from this repo's marketplace and run in real sessions of three replies each (a story, a command, a story, a command, a story):

| | Result |
|---|---|
| Exact counts | Matched the API's own totals in every run (for example 1,462, 1,567 and 1,471 tokens) |
| Live `~` estimate against the exact speed | Within about 15%: 73 vs 83, 77 vs 90, 84 vs 93, 92 vs 86, 90 vs 80, 104 vs 94 tok/s |
| Before the 0.2.0 fixes | 2.5k tok/s on replies that thought first, and live estimates 30 to 40% low |

6 automated tests cover the exact speed, the live estimate, learning the ratio, hidden thinking, the per-minute window and clearing the status line. Run them with `claude plugin test mods/token-meter`.

The test sessions ran headless, where the meter writes to the debug log instead of a status line. I couldn't open an interactive terminal on the test machine, so I haven't seen it drawn on screen myself.

## Install

In your terminal:

```
claude plugin marketplace add NotRedFox/NotRedFoxs-Claude-skills
claude plugin install token-meter@notredfox
```

Or inside a Claude Code session, `/plugin marketplace add NotRedFox/NotRedFoxs-Claude-skills` then `/plugin install token-meter@notredfox`, then `/reload-plugins`.

To check what it does before installing, clone this repo and run `claude plugin validate mods/token-meter`. It only reads replies and the clock and writes to the status line.

## Where it shows

The terminal and the Code tab of the Claude Desktop app. It runs but shows nothing in the VS Code chat panel and `claude -p`.

To update it: `claude plugin update token-meter@notredfox`. To remove it: `claude plugin uninstall token-meter@notredfox`.
