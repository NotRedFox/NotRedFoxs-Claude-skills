# Kick Start

Version 1.1.0. See [CHANGELOG.md](CHANGELOG.md).

A Claude skill that keeps your project's memory in files, so nothing depends on what Claude remembers. Turn it on once and it keeps four things up to date as you work:

| File | What's in it |
|---|---|
| `kickstart/<date>-<topic>.md` | Every problem in the conversation, every approach Claude took, whether it worked, and the proof |
| `BUGS.md` | Every bug found and fixed: symptom, cause, fix, the test that guards it, and the lesson. Claude rereads it before changing code so it doesn't repeat a mistake. |
| `README.md` | An Architecture section showing how the project is built right now, updated whenever the structure changes |
| Tests | Written from what you asked for, not copied from the code's output |

It also:

- **Checks that tests can fail.** Each test has to fail on the broken version before it counts. Bugs that aren't fixed yet stay as visible failing tests.
- **Writes comments for developers.** They explain why the code is the way it is. They never repeat your prompt or say "as requested".
- **Removes personal info** (names, emails, keys, home folder paths) from everything it writes.
- **Writes plainly.** It checks its writing for AI giveaways: em dashes, filler like "genuinely" or "robust", and stock phrases like "it's worth noting".

See a worked example in [examples/slugify](examples/slugify/): the [conversation log](examples/slugify/kickstart/2026-10-01-url-slugs.md), [BUGS.md](examples/slugify/BUGS.md), the [README with its Architecture section](examples/slugify/README.md), the [code](examples/slugify/slug.py) and the [tests](examples/slugify/test_slug.py).

## Install

### Claude app (claude.ai, desktop or phone)

1. Download [kick-start.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/kick-start.zip). Don't unzip it.
2. In Claude, open **Settings** and find **Skills**.
3. Upload the zip file.

### Claude Code

Paste this into your terminal (Mac or Linux):

```
mkdir -p ~/.claude/skills && curl -sL https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/kick-start.zip -o /tmp/kick-start.zip && unzip -oq /tmp/kick-start.zip -d ~/.claude/skills && rm /tmp/kick-start.zip
```

Then restart Claude Code. On Windows, download the zip and unzip it into `.claude\skills` in your user folder.

To update later, do the same steps again.

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
