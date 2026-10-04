# Token Meter

Version 0.1.0. A Claude Code mod that shows how fast Claude is writing, live, in the status line:

```
~95 tok/s | 1.2k tok/min | 8.4k tok/hr
```

- **tok/s**: speed of the current reply. While Claude is still writing it starts with `~`, an estimate from the text so far (about 4 characters per token). When the reply ends it switches to the exact number from the API.
- **tok/min**: tokens Claude wrote in the last 60 seconds.
- **tok/hr**: tokens Claude wrote in the last hour.

It counts output tokens only (what Claude writes, including thinking and tool calls), not what it reads.

## What's a mod?

A mod is a plugin with code that runs inside Claude Code, so it can draw in the interface and react to events like tool calls and replies. Skills are instructions Claude reads; mods change Claude Code itself. They need Claude Code v2.1.287 or later. See [Anthropic's mods overview](https://code.claude.com/docs/en/plugins/mods/overview).

## Tested

- In a real session, the exact count matched the API's own usage for the reply (328 output tokens).
- The live `~` estimate read 75 to 109 tok/s while the exact speed for that reply was 115 tok/s, so treat the live number as rough.
- 4 automated tests cover the exact speed, the live estimate, the per-minute window dropping old tokens, and clearing the status line when nothing has been counted. Run them with `claude plugin test mods/token-meter`.

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

To remove it: `claude plugin uninstall token-meter@notredfox`.
