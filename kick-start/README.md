# Kick Start

Version 1.0.0. See [CHANGELOG.md](CHANGELOG.md).

A Claude skill that keeps a running log of the whole conversation: every problem you worked on, every approach Claude took, what worked, what didn't and why. The next session can pick up exactly where this one stopped.

It keeps one file per conversation in `kickstart/`, and updates it as it goes:

- **Every approach, in order**, grouped by the problem it was for, marked Worked, Failed or Partly worked.
- **Proof for each result**: the command or test and its real output, not a summary from memory.
- **A summary at the top** that stays current: what works, what's still broken, and a table of problems and what fixed them.
- **What worked, what not to retry**, next steps and questions only you can answer.

It also adds tests, with rules that stop them from just agreeing with the AI:

- Expected answers come from what you asked for, never from copying what the code outputs.
- Every test is shown to fail on the broken version before it counts.
- Bugs that aren't fixed yet stay as visible failing tests, never deleted or weakened.

Before each save, it removes personal info (names, emails, keys, home folder paths) and checks the writing for AI giveaways like em dashes.

See a real example: [a full conversation's log](examples/slugify/kickstart/2026-10-01-url-slugs.md) and its [tests](examples/slugify/test_slug.py).

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

Turn it on early. It stays on for the rest of the conversation. If you turn it on late, it goes back and fills in everything from the start.

## Limits

- It can only log what it can see in the conversation. Very long conversations get compacted, which is why it saves after every approach instead of at the end.
- The personal info check is a pattern search. It catches the common cases, so still read the file before sharing it.

## Similar skills

[handoff-skill](https://github.com/davidclarklee/handoff-skill) and the [handoff skill in claude-code-tips](https://github.com/ykdojo/claude-code-tips/blob/main/skills/handoff/SKILL.md) write a handoff file at the end of a session. Kick Start logs the whole conversation as it goes, including what worked, and adds the test rules, the personal info scrub and the checked versus believed split.
