# Kick Start

Version 1.1.2. See [CHANGELOG.md](CHANGELOG.md).

A Claude skill that keeps your project's memory in files, so nothing depends on what Claude remembers. Turn it on once and it keeps four things up to date as you work:

| File | What's in it |
|---|---|
| `kickstart/<date>-<topic>.md` | Every problem in the conversation, every approach Claude took, whether it worked, and the proof |
| `BUGS.md` | Every bug found and fixed: symptom, cause, fix, the test that guards it, and the lesson. Claude rereads it before changing code so it doesn't repeat a mistake. |
| `README.md` | An Architecture section showing how the project is built right now, updated whenever the structure changes |
| Tests | Written from what you asked for, not copied from the code's output |

It also:

- **Checks that tests can fail.** Each test is run against the broken version, and the log flags any test that was never seen to fail. Bugs that aren't fixed yet stay as visible failing tests.
- **Writes comments for developers.** They explain why the code is the way it is. They never repeat your prompt or say "as requested".
- **Removes personal info** (names, emails, keys, home folder paths) from everything it writes.
- **Writes plainly.** It checks its writing for AI giveaways: em dashes, filler like "genuinely" or "robust", and stock phrases like "it's worth noting".

## Only want the log?

If all you want is for Claude to keep track of what it tried, you don't need the skill. Add this to your project's `CLAUDE.md`:

```
After each approach you try, add a line to kickstart/log.md: what you tried, whether it worked, and the evidence (command and real output). Read it before starting work.
```

The skill adds what doesn't fit in a line: the `BUGS.md` format and the rule to reread it before touching a file, tests that must fail on the broken code before they count, the README architecture section, the personal info scrub and the writing checks. That's about 230 lines of instructions, which is why it's a skill and not part of `CLAUDE.md`: a skill loads only when used, while `CLAUDE.md` loads in every session.

## Example

[examples/invoice](examples/invoice/) is real output from two separate conversations on a small invoice project. The starting code is in [before/](examples/invoice/before/).

1. **"Customers are complaining about invoice totals, sort it out."** Claude fixed five bugs, logged each one in [BUGS.md](examples/invoice/BUGS.md), wrote the [Architecture section](examples/invoice/README.md) and [the log](examples/invoice/kickstart/2026-10-01-invoice-totals.md). 26 tests, 19 of which fail on the starting code.
2. **"Add CSV export"**, in a fresh conversation with no memory of the first. Claude read `BUGS.md` first and built the export around the money lessons from bugs B1 to B5. It found one more bug (B6), logged it as open with a test that flags when it's fixed, and updated the Architecture section. See [the log](examples/invoice/kickstart/2026-10-01-invoice-csv-export.md). 42 tests pass, plus 2 expected failures for B6.

`config.py` held a made-up payment key, email and home folder path to test the personal info scrub. None of them reached the logs, and they've been replaced with placeholders here.

## Install

### Claude app (claude.ai, desktop or phone)

1. Download [kick-start-claude-app.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/kick-start-claude-app.zip). Don't unzip it.
2. In Claude, open **Settings** and find **Skills**.
3. Upload the zip file.

### Claude Code

Paste this into your terminal (Mac or Linux):

```
mkdir -p ~/.claude/skills && curl -sL https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/kick-start.zip -o /tmp/kick-start.zip && unzip -oq /tmp/kick-start.zip -d ~/.claude/skills && rm /tmp/kick-start.zip
```

Then restart Claude Code. On Windows, download the zip and unzip it into `.claude\skills` in your user folder.

To update later, do the same steps again.

The two downloads hold the same skill. The Claude Code one also has Claude Code settings (an argument hint), which the Claude app doesn't accept.
Claude can start it on its own when your request matches, or you can type `/kick-start`.

## Use

- "Kick start"
- "Log this session"
- "What have we tried?"

Turn it on early. It stays on for the rest of the conversation. If you turn it on late, it goes back and fills in everything from the start. In a new conversation, it reads `BUGS.md`, the Architecture section and the last log before doing anything.

## Limits

- It only changes the part of your README between its markers, plus any line a change made wrong.
- It can only log what it can see in the conversation. Very long conversations get compacted, which is why it saves after every approach instead of at the end.
- The personal info check is a pattern search. It catches the common cases, so still read the file before sharing it.

## Similar skills

[handoff-skill](https://github.com/davidclarklee/handoff-skill) and the [handoff skill in claude-code-tips](https://github.com/ykdojo/claude-code-tips/blob/main/skills/handoff/SKILL.md) write a handoff file at the end of a session. Kick Start logs the whole conversation as it goes, including what worked, and adds the test rules, the personal info scrub and the checked versus believed split.
